"""Take the portfolio's screenshots, with private details hidden before each one is taken.

Runs against copies of the apps (never the live ones), started like this:
  Mally's:  cd <copy>/route-map && MHS_PORT=8799 python3 src/serve.py
  FOCUS:    cd <copy>/mindscape-app && MINDSCAPE_DEMO=1 MINDSCAPE_PORT=8780 .venv/bin/python -m engine

  python3 tools/shots.py --mhs-data <copy>/route-map/data [--raw <folder for full-size PNGs>]

What each shot hides is written next to it below. With --mhs-data, every Mally's shot is also
checked against the names, phone numbers and street addresses in the Mally's data (its database and
its follow-ups list, read at run time, never written anywhere): if any of them is on screen, the
shot is not saved and the run fails.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sqlite3
import sys
import urllib.request

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "assets" / "img"
MHS = "http://127.0.0.1:8799"
FOCUS = "http://127.0.0.1:8780"

SKIP_TOUR = """() => { const b = [...document.querySelectorAll('button')].find(x => x.textContent.trim() === 'Skip');
  if (b) b.click(); }"""

SHOTS = [
    {
        "name": "mhs-console",
        "url": MHS + "/",
        # Hidden: the goals strip (money targets), the business numbers, Right now (customer names).
        "js": """() => { const gh = [...document.querySelectorAll('main.ps > .goals-h')];
          gh.forEach(h => h.style.display = 'none');
          if (gh[0] && gh[0].nextElementSibling) gh[0].nextElementSibling.style.display = 'none';
          document.querySelectorAll('#hero .cards, #now').forEach(e => e.style.display = 'none'); }""",
        "clip": "viewport",
        "height": 660,
    },
    {
        "name": "mhs-decide",
        "url": MHS + "/decision.html",
        # Hidden: the "Yours" column (customers per town).
        "js": """() => { document.querySelectorAll('table').forEach(t => {
            const hs = [...t.querySelectorAll('th')]; const i = hs.findIndex(h => /yours/i.test(h.textContent));
            if (i < 0) return;
            t.querySelectorAll('tr').forEach(r => { const c = r.children[i]; if (c) c.style.display = 'none'; }); }); }""",
        "clip": "viewport",
    },
    {
        "name": "mhs-sop",
        "url": MHS + "/service.html#bins",
        # Only the kit and the job steps: the stock photo (someone else's, CC BY-SA) and the sales pitch are left out.
        "js": """() => { document.querySelectorAll('#sop figure').forEach(f => f.style.display = 'none');
          const h = [...document.querySelectorAll('#sop h2')].find(x => /selling it/i.test(x.textContent));
          if (h) { h.style.display = 'none'; if (h.nextElementSibling) h.nextElementSibling.style.display = 'none'; } }""",
        "clip": "#sop",
    },
    {
        "name": "focus-home",
        "url": FOCUS + "/",
        "js": SKIP_TOUR,
        "clip": "viewport",
        "height": 560,
    },
    {
        "name": "focus-money",
        "url": FOCUS + "/apps/money/web/",
        "js": SKIP_TOUR,
        "clip": '#fc .card:has-text("Money, day by day")',
    },
    {
        "name": "focus-browse",
        "url": FOCUS + "/apps/system/web/browse.html",
        "js": SKIP_TOUR,
        "click": "text=Priya Natarajan",
        "wait_for": "text=Details",
        "clip": "viewport",
    },
]


def private_strings(data: pathlib.Path) -> list[str]:
    """Names, phones and street addresses from the Mally's data, to make sure none is on screen."""
    found: set[str] = set()
    db = sqlite3.connect(f"file:{data / 'knocks.db'}?mode=ro", uri=True)
    for table, cols in {"visits": ("name", "phone", "address"), "leads": ("who", "name", "phone"),
                        "crm_contacts": ("name", "phone", "address"), "knocks": ("address",),
                        "portal_customers": ("name", "phone", "email", "address")}.items():
        for row in db.execute(f"select {', '.join(cols)} from {table}"):
            found.update(str(v).strip() for v in row if v)
    # The people being followed up (realtors and prospects) are named from other lists; ask the app.
    with urllib.request.urlopen(MHS + "/api/followups", timeout=20) as r:
        for item in json.load(r).get("items", []):
            found.update(str(item.get(k) or "").strip() for k in ("name", "phone"))
    found.discard("")
    keep = set()
    for s in found:
        digits = re.sub(r"\D", "", s)
        if len(digits) >= 7 and len(digits) == len(re.sub(r"[\s()+.-]", "", s)):
            keep.add(digits[-7:])          # phone: match the last 7 digits
        elif len(s) >= 5 and s.lower() not in {"(name needed)", "unknown"}:
            keep.add(s.lower().split(",")[0])  # a name, or the street part of an address
    return sorted(keep)


def leaks(text: str, secrets: list[str]) -> list[str]:
    low, digits = text.lower(), re.sub(r"\D", "", text)
    return [s for s in secrets if (s.isdigit() and s in digits) or (not s.isdigit() and s in low)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mhs-data", type=pathlib.Path)
    ap.add_argument("--raw", type=pathlib.Path)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args()
    secrets = private_strings(a.mhs_data) if a.mhs_data else []
    OUT.mkdir(parents=True, exist_ok=True)
    if a.raw:
        a.raw.mkdir(parents=True, exist_ok=True)
    failed = False
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 800}, device_scale_factor=2)
        page.add_init_script("localStorage.setItem('mhs-decals', 'off')")  # Mally's background icons off
        for shot in SHOTS:
            if a.only and shot["name"] not in a.only:
                continue
            page.goto(shot["url"], wait_until="networkidle")
            page.wait_for_timeout(1500)
            page.evaluate(shot["js"])
            if shot.get("click"):
                page.click(shot["click"])
            if shot.get("wait_for"):
                page.wait_for_selector(shot["wait_for"], timeout=15000)
            page.wait_for_timeout(800)
            target = page if shot["clip"] == "viewport" else page.locator(shot["clip"])
            text = page.evaluate("document.body.innerText") if shot["clip"] == "viewport" else target.inner_text()
            bad = leaks(text, secrets) if shot["url"].startswith(MHS) else []
            if bad:
                print(f"{shot['name']}: NOT SAVED, {len(bad)} private item(s) still on screen")
                failed = True
                continue
            png = (a.raw or OUT) / f"{shot['name']}.png"
            if shot.get("height"):
                page.screenshot(path=str(png), clip={"x": 0, "y": 0, "width": 1280, "height": shot["height"]})
            else:
                target.screenshot(path=str(png))
            img = Image.open(png).convert("RGB")
            if img.width > 1600:
                img = img.resize((1600, round(img.height * 1600 / img.width)), Image.LANCZOS)
            img.save(OUT / f"{shot['name']}.webp", "WEBP", quality=82, method=6)
            if not a.raw:
                png.unlink()
            print(f"{shot['name']}: {img.width}x{img.height}, checked against {len(secrets)} private items")
        browser.close()
    print(json.dumps({"ok": not failed}))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
