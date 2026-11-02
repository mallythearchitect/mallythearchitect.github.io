#!/usr/bin/env python3
"""Every saved change, logged and tagged: a release tag for each day of work, a tag for each decision note,
CHANGELOG.md, and (with --releases) a GitHub release with its what-changed for each day.

After a day's work:
    python3 scripts/changelog.py --log-only   rewrite CHANGELOG.md, then save it with the day's work
    python3 scripts/changelog.py --tags-only  tag every day and decision that has no tag yet
    git push --follow-tags                    send the tags to GitHub with the saved changes
    python3 scripts/changelog.py --releases   a GitHub release for every day tag that has none yet (needs gh)
Also: no flag = the tags, then the log; --dry-run = say what it would do and change nothing; --releases --refresh = write
the notes of the releases already on GitHub again.

Releases. Each day of work is one release: the tag vYYYY.MM.DD goes on that day's last saved change. If more changes land on a
day that is already tagged, they become vYYYY.MM.DD.2, and so on. Decisions. Each note docs/decisions/NNNN-*.md gets the tag
decision-NNNN on the saved change that wrote it. Tags are annotated, dated like the change they mark, and never moved: a run
only adds what is missing.

The log. CHANGELOG.md lists every release, newest first: the decisions written in it, then every saved change, newest first.
A change that a later one took back out (its message says "This reverts …") says so.

Standard library only, so the same file works in any project; the project's name is the first heading of its README.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from datetime import date
from pathlib import Path

RELEASE = re.compile(r"^v(\d{4})\.(\d\d)\.(\d\d)(?:\.(\d+))?$")
DECISION_FILE = re.compile(r"^(\d{4})-.+\.md$")
REVERTS = re.compile(r"[Tt]his reverts (?:commits? )?((?:[0-9a-f]{7,40}(?:,\s*|\s+and\s+|\s*))+)")
SEP, END = "\x1f", "\x1e"


def git(root: Path, *args: str, env: dict | None = None) -> str:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=env)
    if r.returncode:
        raise SystemExit(f"git {' '.join(args[:3])}: {r.stderr.strip()}")
    return r.stdout


def project_name(root: Path) -> str:
    readme = root / "README.md"
    if readme.exists():
        for line in readme.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    return root.name


def changes(root: Path) -> list[dict]:
    """The main line's saved changes, oldest first."""
    out = git(root, "log", "--first-parent", "--reverse", f"--format=%H{SEP}%h{SEP}%cs{SEP}%cI{SEP}%s{SEP}%b{END}")
    rows = []
    for rec in out.split(END):
        rec = rec.strip("\n")
        if rec:
            sha, short, day, when, subject, body = rec.split(SEP, 5)
            rows.append({"sha": sha, "short": short, "day": day, "when": when, "subject": subject, "body": body})
    return rows


def existing_tags(root: Path) -> dict[str, str]:
    """Tag name -> the saved change it marks."""
    out = git(root, "for-each-ref", "refs/tags", f"--format=%(refname:short){SEP}%(objectname){SEP}%(*objectname)")
    found = {}
    for line in out.splitlines():
        name, obj, peeled = line.split(SEP)
        found[name] = peeled or obj
    return found


def _free(day: str, taken: set[str]) -> str:
    base = "v" + day.replace("-", ".")
    if base not in taken:
        return base
    n = 2
    while f"{base}.{n}" in taken:
        n += 1
    return f"{base}.{n}"


def releases(rows: list[dict], tags: dict[str, str]) -> list[dict]:
    """The main line cut into releases, oldest first. A release ends at a change that already carries a release tag, or at a
    day's last change; a new one is named for its day."""
    marked: dict[str, list[str]] = {}
    for name, sha in tags.items():
        if RELEASE.match(name):
            marked.setdefault(sha, []).append(name)
    taken = set(tags)
    out, cur = [], []
    for i, c in enumerate(rows):
        cur.append(c)
        nxt = rows[i + 1] if i + 1 < len(rows) else None
        named = sorted(marked.get(c["sha"], []))
        if named or nxt is None or nxt["day"] != c["day"]:
            if named:
                name, new = named[0], False
            else:
                name, new = _free(c["day"], taken), True
                taken.add(name)
            out.append({"tag": name, "new": new, "day": c["day"], "head": c, "changes": cur})
            cur = []
    return out


def _title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            t = re.sub(r"^\d+\s*[.·:]\s*", "", line[2:].strip())
            return re.sub(r"\s*\(\d{4}-\d\d-\d\d\)$", "", t)
    return fallback


def decisions(root: Path) -> list[dict]:
    """Every saved decision note with the change that wrote it (renames followed back to the first write)."""
    folder = root / "docs" / "decisions"
    if not folder.is_dir():
        return []
    out = []
    for f in sorted(folder.iterdir()):
        m = DECISION_FILE.match(f.name)
        if not m:
            continue
        rel = f.relative_to(root).as_posix()
        added = git(root, "log", "--follow", "--diff-filter=A", "--format=%H", "--", rel).split()
        if added:
            out.append({"tag": f"decision-{m.group(1)}", "number": m.group(1), "path": rel, "sha": added[0],
                        "title": _title(f.read_text(encoding="utf-8"), f.stem)})
    return out


def reverted_by(rows: list[dict]) -> dict[str, str]:
    """Full sha of a change taken back out -> the short sha of the change that took it out."""
    out = {}
    for c in rows:
        for m in REVERTS.finditer(c["body"]):
            for ref in re.findall(r"[0-9a-f]{7,40}", m.group(1)):
                for r in rows:
                    if r["sha"].startswith(ref):
                        out[r["sha"]] = c["short"]
    return out


def say_day(day: str) -> str:
    d = date.fromisoformat(day)
    return f"{d:%A} {d.day} {d:%B %Y}"


def short_day(day: str) -> str:
    d = date.fromisoformat(day)
    return f"{d.day} {d:%b %Y}"


def plural(n: int, word: str) -> str:
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


def what_changed(rel: dict, decs: list[dict], gone: dict[str, str], base: str = "") -> str:
    """One release's what-changed, in Markdown: the decisions written in it, then its saved changes, newest first. `base` goes
    in front of a decision's path: nothing in CHANGELOG.md, the project's address on GitHub in a release's notes."""
    shas = {c["sha"] for c in rel["changes"]}
    lines = []
    mine = [d for d in decs if d["sha"] in shas]
    if mine:
        lines += ["**Decisions written:** " + " · ".join(f"[{d['number']} {d['title']}]({base}{d['path']})" for d in mine), ""]
    for c in reversed(rel["changes"]):
        note = f" *Taken back out in `{gone[c['sha']]}`.*" if c["sha"] in gone else ""
        lines.append(f"- `{c['short']}` {c['subject']}{note}")
    return "\n".join(lines)


def make_tags(root: Path, name: str, rels: list[dict], decs: list[dict], tags: dict[str, str], dry: bool) -> list[str]:
    made = []
    when = {c["sha"]: c["when"] for r in rels for c in r["changes"]}
    plan = [(r["tag"], r["head"]["sha"], f"{name}, {say_day(r['day'])}: {plural(len(r['changes']), 'saved change')}\n\n"
             + "\n".join(f"- {c['subject']}" for c in reversed(r["changes"]))) for r in rels if r["new"]]
    plan += [(d["tag"], d["sha"], f"Decision {d['number']}: {d['title']}\n\n{d['path']}") for d in decs if d["tag"] not in tags]
    for tag, sha, msg in plan:
        made.append(f"{tag} -> {sha[:7]}")
        if not dry:
            env = {**os.environ, "GIT_COMMITTER_DATE": when.get(sha, "")} if when.get(sha) else None
            git(root, "tag", "-a", "--cleanup=verbatim", "-m", msg, tag, sha, env=env)
    return made


def write_log(root: Path, name: str, rows: list[dict], rels: list[dict], decs: list[dict], gone: dict[str, str]) -> Path:
    head = rows[-1]
    parts = [
        f"# Changelog: {name}",
        "",
        "Every saved change, newest first, in releases: one per day of work. Each release is a tag on GitHub "
        "(`vYYYY.MM.DD`, on the day's last change) and a GitHub release with the same list as its what-changed. "
        + ("Each decision note is tagged where it was written (`decision-NNNN`). " if decs else "")
        + "A change that a later one took back out says so.",
        "",
        f"Covers every saved change up to `{head['short']}` ({short_day(head['day'])}): "
        f"{plural(len(rows), 'saved change')} in {plural(len(rels), 'release')}"
        + (f", {plural(len(decs), 'decision')}" if decs else "")
        + f", from {short_day(rows[0]['day'])} to {short_day(head['day'])}. "
        "Rebuilt with `python3 scripts/changelog.py --log-only`; once it is saved, `--tags-only`, `git push --follow-tags` "
        "and `--releases` tag the day and publish it, so the change that saves this file is tagged too.",
    ]
    for r in reversed(rels):
        parts += ["", f"## {r['tag']} · {say_day(r['day'])}", "", plural(len(r["changes"]), "saved change"), "",
                  what_changed(r, decs, gone)]
    path = root / "CHANGELOG.md"
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")
    return path


def _gh(root: Path, *args: str) -> str:
    r = subprocess.run(["gh", *args], cwd=root, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(f"gh {' '.join(args[:2])}: {r.stderr.strip()}")
    return r.stdout


def make_releases(root: Path, rels: list[dict], decs: list[dict], gone: dict[str, str], dry: bool,
                  refresh: bool = False) -> list[str]:
    """A GitHub release for every release tag that has none yet, oldest first, the newest marked latest. With `refresh`, the
    releases already there get their notes written again too."""
    have = {x["tagName"] for x in json.loads(_gh(root, "release", "list", "--limit", "1000", "--json", "tagName") or "[]")}
    url = _gh(root, "repo", "view", "--json", "url", "-q", ".url").strip()
    made = []
    for i, rel in enumerate(rels):
        title = f"{short_day(rel['day'])} · {plural(len(rel['changes']), 'saved change')}"
        notes = what_changed(rel, decs, gone, f"{url}/blob/{rel['tag']}/")
        if rel["tag"] in have:
            if refresh:
                made.append(f"{rel['tag']}: notes written again")
                if not dry:
                    _gh(root, "release", "edit", rel["tag"], "--title", title, "--notes", notes)
            continue
        made.append(f"{rel['tag']}: {title}")
        if not dry:
            latest = "--latest" if i == len(rels) - 1 else "--latest=false"
            _gh(root, "release", "create", rel["tag"], "--verify-tag", latest, "--title", title, "--notes", notes)
    return made


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--repo", type=Path, default=Path(__file__).resolve().parent, help="any folder inside the project")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--tags-only", action="store_true")
    ap.add_argument("--log-only", action="store_true")
    ap.add_argument("--releases", action="store_true")
    ap.add_argument("--refresh", action="store_true", help="with --releases: write the notes of existing releases again")
    a = ap.parse_args()
    root = Path(git(a.repo, "rev-parse", "--show-toplevel").strip())
    name, rows = project_name(root), changes(root)
    if not rows:
        raise SystemExit("no saved changes yet")
    tags = existing_tags(root)
    rels, decs, gone = releases(rows, tags), decisions(root), reverted_by(rows)
    if a.releases:
        for line in make_releases(root, rels, decs, gone, a.dry_run, a.refresh):
            print(("would release " if a.dry_run else "released ") + line)
        return
    if not a.log_only:
        made = make_tags(root, name, rels, decs, tags, a.dry_run)
        print("\n".join(("would tag " if a.dry_run else "tagged ") + m for m in made) or "every tag is already there")
    if not (a.tags_only or a.dry_run):
        print(f"wrote {write_log(root, name, rows, rels, decs, gone).relative_to(root)}: "
              f"{plural(len(rows), 'saved change')} in {plural(len(rels), 'release')}")


if __name__ == "__main__":
    main()
