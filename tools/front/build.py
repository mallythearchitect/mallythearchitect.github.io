#!/usr/bin/env python3
"""Draws malachicollins.org's front page: the welcome (four looks), the looks themselves, and one timeline to scroll.

    python3 build.py --out ../../docs/index.html                 the public page
    python3 build.py --review --inline --out review.html         the review copy: waiting entries and questions shown,
                                                                 pictures inside the file so it opens anywhere
    --content FILE    the content (default content.py beside this file; the working copy is data.py)
    --portfolio URL   where the trades portfolio lives ("portfolio/" today; its own address once it moves)
    --site DIR        the website's docs/ folder (icons and pictures are read from it)
"""
from __future__ import annotations

import argparse
import base64
import html
import importlib.util
import re
from datetime import date
from pathlib import Path

E = html.escape
HERE = Path(__file__).resolve().parent

EXTRA_ICONS = {
    "focus": '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="3"/><path d="M12 1.5v4M12 18.5v4M1.5 12h4M18.5 12h4"/>',
    "eye": '<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="2.8"/>',
    "x": '<path d="M6 6l12 12M18 6 6 18"/>',
    "image": '<rect x="3" y="4.5" width="18" height="15" rx="2"/><circle cx="8.5" cy="10" r="1.6"/><path d="m4 17 5-4.5 3.5 3 3-2.5 4.5 4"/>',
    "swap": '<path d="M7 4v16M7 20l-3.5-3.5M7 20l3.5-3.5M17 20V4M17 4l-3.500 3.500M17 4l3.500 3.500"/>',
}


def load_icons(sprite: Path) -> dict:
    icons = dict(EXTRA_ICONS)
    for m in re.finditer(r'<symbol id="i-([a-z0-9-]+)"[^>]*>(.*?)</symbol>', sprite.read_text(encoding="utf-8"), re.S):
        icons.setdefault(m.group(1), re.sub(r"\s+", " ", m.group(2)).strip())
    return icons


CSS = r"""
:root{color-scheme:light;--page:#f9f9f7;--surface:#fcfcfb;--raised:#fff;--ink:#0b0b0b;--ink-2:#52514e;--muted:#6f6e69;
--grid:#e1e0d9;--axis:#c3c2b7;--ring:rgba(11,11,11,.10);--wash:rgba(11,11,11,.045);--shadow:0 1px 2px rgba(11,11,11,.05),0 8px 28px rgba(11,11,11,.07);
--s-trade:#eb6834;--s-sports:#e87ba4;--s-career:#2a78d6;--s-focus:#eda100;--radius:18px;
--font:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;--raised:#1f1f1e;
--ink:#f0efec;--ink-2:#c3c2b7;--muted:#a3a29b;--grid:#2c2c2a;--axis:#383835;--ring:rgba(255,255,255,.10);--wash:rgba(255,255,255,.055);
--shadow:0 1px 2px rgba(0,0,0,.4),0 8px 28px rgba(0,0,0,.45);--s-trade:#d95926;--s-sports:#d55181;--s-career:#3987e5;--s-focus:#c98500}}
:root[data-theme="dark"]{color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;--raised:#1f1f1e;
--ink:#f0efec;--ink-2:#c3c2b7;--muted:#a3a29b;--grid:#2c2c2a;--axis:#383835;--ring:rgba(255,255,255,.10);--wash:rgba(255,255,255,.055);
--shadow:0 1px 2px rgba(0,0,0,.4),0 8px 28px rgba(0,0,0,.45);--s-trade:#d95926;--s-sports:#d55181;--s-career:#3987e5;--s-focus:#c98500}
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;scroll-behavior:smooth;scroll-padding-top:124px}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}*{transition:none!important;animation:none!important}}
body{margin:0;background:var(--page);color:var(--ink);font:17px/1.55 var(--font);overflow-x:hidden}
a{color:inherit;text-underline-offset:3px}
img{max-width:100%;height:auto;display:block}
h1,h2,h3,h4,p,ul,ol,figure{margin:0}
ul,ol{padding:0;list-style:none}
[hidden]{display:none!important}
.icon{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round;flex:none}
.wrap{width:min(1120px,100% - 32px);margin-inline:auto}
:focus-visible{outline:2px solid var(--ink);outline-offset:3px;border-radius:8px}
.skip{position:absolute;left:-999px}.skip:focus{left:16px;top:12px;z-index:50;background:var(--raised);padding:8px 12px;border-radius:8px}

.top{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--page) 88%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--ring)}
.top .wrap{display:flex;align-items:center;gap:14px;min-height:60px}
.brand{display:flex;align-items:center;gap:10px;font-weight:750;text-decoration:none;letter-spacing:-.01em}
.mono{display:grid;place-items:center;width:34px;height:34px;border-radius:10px;background:var(--ink);color:var(--page);font-size:13px;font-weight:800;letter-spacing:.02em}
.top nav{margin-left:auto;display:flex;gap:2px;align-items:center}
.top nav a{font-size:15px;font-weight:600;text-decoration:none;padding:8px 10px;border-radius:10px;color:var(--ink-2)}
.top nav a:hover{background:var(--wash);color:var(--ink)}
@media (max-width:720px){.top nav a.hide-s{display:none}}
.review{background:var(--ink);color:var(--page);font-size:14px;font-weight:600;text-align:center;padding:8px 16px}

.hero{padding:40px 0 22px;display:grid;gap:22px;align-items:center}
@media (min-width:860px){.hero{grid-template-columns:1fr 280px;padding:64px 0 30px;gap:48px}}
.hero h1{font-size:clamp(44px,10.5vw,96px);line-height:.95;letter-spacing:-.045em;font-weight:820;margin:0 0 16px}
.lead{font-size:clamp(19px,2.6vw,24px);line-height:1.35;color:var(--ink-2);max-width:34ch}
.meta{display:flex;flex-wrap:wrap;gap:8px 18px;margin-top:16px;color:var(--ink-2);font-size:15.5px}
.meta span{display:inline-flex;gap:7px;align-items:center}
.meta .icon{width:18px;height:18px;color:var(--muted)}
.shot{width:min(280px,60vw);aspect-ratio:1;border-radius:28px;overflow:hidden;box-shadow:var(--shadow);background:var(--wash)}
.shot img{width:100%;height:100%;object-fit:cover}
@media (max-width:859px){.shot{order:-1;width:124px;border-radius:22px}}
.btn{display:inline-flex;align-items:center;gap:8px;min-height:46px;padding:0 16px;border-radius:12px;border:1px solid var(--ring);background:var(--raised);
font:650 15.5px var(--font);color:var(--ink);text-decoration:none;cursor:pointer}
.btn:hover{border-color:var(--axis)}
.btn.primary{background:var(--ink);color:var(--page);border-color:var(--ink)}
.btn .icon{width:18px;height:18px}

/* the four looks */
.doors{display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:6px 0 0}
@media (min-width:900px){.doors{grid-template-columns:repeat(4,1fr);gap:14px}}
.door{position:relative;display:grid;align-content:end;gap:2px;min-height:150px;padding:16px;border-radius:var(--radius);border:1px solid var(--ring);
background:linear-gradient(160deg,color-mix(in srgb,var(--c) 26%,var(--surface)),color-mix(in srgb,var(--c) 7%,var(--surface)) 70%);
text-decoration:none;overflow:hidden;transition:translate .15s,box-shadow .15s}
@media (min-width:900px){.door{min-height:210px;padding:20px}}
.door:hover{translate:0 -3px;box-shadow:var(--shadow)}
.door .big{position:absolute;right:4px;top:4px;width:60px;height:60px;color:var(--c);opacity:.5;stroke-width:1.3}
@media (min-width:900px){.door .big{width:140px;height:140px;right:-8px;top:-8px;stroke-width:1.2}}
.door b{font-size:clamp(20px,3.4vw,26px);letter-spacing:-.025em;line-height:1.1;font-weight:800}
.door span{font-size:14.5px;color:var(--ink-2);line-height:1.3}
.door .go{position:absolute;left:16px;top:16px;width:22px;height:22px}
.door[aria-current="true"]{box-shadow:0 0 0 2px var(--ink)}

/* a look, opened */
.panel{margin-top:22px;border-radius:24px;border:1px solid var(--ring);background:var(--surface);padding:22px 18px;display:grid;gap:18px;scroll-margin-top:76px;position:relative;overflow:hidden}
.panel::before{content:"";position:absolute;left:0;top:0;bottom:0;width:6px;background:var(--c)}
@media (min-width:860px){.panel{padding:30px 34px;grid-template-columns:1fr 1fr;align-items:center;gap:30px}.panel.solo{grid-template-columns:1fr}}
.kicker{display:flex;align-items:center;gap:8px;font-size:13px;font-weight:750;letter-spacing:.08em;text-transform:uppercase;color:var(--ink-2)}
.kicker .icon{width:18px;height:18px;color:var(--c)}
.panel h2{font-size:clamp(28px,5vw,42px);letter-spacing:-.035em;line-height:1.03;font-weight:800;margin:8px 0 10px}
.panel p.line{font-size:17.5px;color:var(--ink-2);line-height:1.45;max-width:52ch}
.nums{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:16px}
.num{background:var(--page);border:1px solid var(--ring);border-radius:14px;padding:12px 12px 10px}
.num b{display:block;font-size:clamp(20px,3.6vw,30px);letter-spacing:-.03em;line-height:1.05;font-weight:820}
.num span{display:block;font-size:13.5px;font-weight:650;line-height:1.25;margin-top:5px}
.num small{display:block;font-size:12.5px;color:var(--muted);line-height:1.25;margin-top:2px}
.tags{display:flex;flex-wrap:wrap;gap:6px;margin-top:14px}
.tags span{font-size:13.5px;font-weight:600;padding:5px 10px;border-radius:999px;background:var(--wash)}
.steps{display:flex;flex-wrap:wrap;gap:6px 4px;align-items:center;margin-top:14px;font-weight:700;font-size:15px}
.steps i{font-style:normal;display:inline-grid;place-items:center;width:22px;height:22px;border-radius:50%;background:var(--ink);color:var(--page);font-size:12px;margin-right:6px}
.steps span{display:inline-flex;align-items:center;margin-right:10px}
.acts{display:flex;flex-wrap:wrap;gap:10px;margin-top:18px}
.panel figure{border-radius:16px;overflow:hidden;border:1px solid var(--ring);box-shadow:var(--shadow)}
.panel figcaption{font-size:12.5px;color:var(--muted);padding:8px 10px;background:var(--page)}

/* the timeline */
section.block{padding:46px 0 0}
.head{display:flex;flex-wrap:wrap;align-items:end;justify-content:space-between;gap:10px 24px;margin-bottom:12px}
.head h2{font-size:clamp(28px,5vw,44px);letter-spacing:-.035em;line-height:1.02;font-weight:800}
.head p{color:var(--ink-2);font-size:16.5px}
.bar{position:sticky;top:60px;z-index:15;margin:0 -16px;padding:8px 16px;background:color-mix(in srgb,var(--page) 90%,transparent);backdrop-filter:blur(10px);
display:flex;gap:6px;align-items:center;overflow-x:auto;scrollbar-width:none;border-bottom:1px solid var(--ring)}
.bar::-webkit-scrollbar{display:none}
.pill{flex:none;display:inline-flex;align-items:center;gap:7px;min-height:36px;padding:0 12px;border-radius:999px;border:1px solid var(--ring);background:var(--raised);
font:650 14px var(--font);color:var(--ink);text-decoration:none;cursor:pointer;white-space:nowrap}
.pill i{width:9px;height:9px;border-radius:3px;background:var(--c)}
.pill[aria-current="true"],.pill[aria-pressed="true"]{background:var(--ink);color:var(--page);border-color:var(--ink)}
.pill.yr{font-variant-numeric:tabular-nums;border-color:transparent;background:transparent;color:var(--ink-2);padding:0 9px}
.pill.yr.on{background:var(--wash);color:var(--ink)}
.bar .sep{flex:none;width:1px;height:22px;background:var(--grid);margin:0 4px}
.pill .icon{width:16px;height:16px}
.tl{position:relative;margin-top:8px;display:flex;flex-direction:column}
.tl.rev,.tl.rev .items{flex-direction:column-reverse}
.year{display:grid;grid-template-columns:1fr;scroll-margin-top:120px}
.ylab{font-size:clamp(44px,9vw,72px);font-weight:820;letter-spacing:-.05em;line-height:1;color:var(--ink);opacity:.14;padding:26px 0 6px}
@media (min-width:860px){.year{grid-template-columns:150px 1fr;gap:0 18px}.ylab{position:sticky;top:124px;align-self:start;padding:18px 0 0;font-size:54px;opacity:.2}}
.items{display:flex;flex-direction:column;border-left:2px solid var(--grid);margin-left:7px;padding:6px 0 10px}
.ev{position:relative;padding:8px 0 8px 22px}
.ev::before{content:"";position:absolute;left:-8px;top:30px;width:14px;height:14px;border-radius:50%;background:var(--c);box-shadow:0 0 0 4px var(--page)}
.ev.going::before{background:var(--page);border:3.5px solid var(--c)}
.cont{padding:6px 0 6px 22px;font-size:14.5px;color:var(--muted)}
.tcard{display:grid;background:var(--surface);border:1px solid var(--ring);border-radius:var(--radius);overflow:hidden;scroll-margin-top:130px}
.tcard:target{box-shadow:0 0 0 2px var(--ink)}
@media (min-width:700px){.tcard{grid-template-columns:230px 1fr}}
.cover{position:relative;min-height:128px;background:linear-gradient(150deg,color-mix(in srgb,var(--c) 30%,var(--surface)),color-mix(in srgb,var(--c) 8%,var(--surface)));display:grid;place-items:center;overflow:hidden}
.cover img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:top left}
.cover .icon{width:54px;height:54px;color:var(--c);stroke-width:1.3;opacity:.9}
.cover small{position:absolute;left:10px;bottom:8px;font-size:12px;font-weight:650;color:var(--ink-2);display:flex;gap:5px;align-items:center}
.cover small .icon{width:14px;height:14px;opacity:1;color:currentColor;stroke-width:1.7}
.tb{padding:16px 18px 15px}
.when{font-size:13.5px;font-weight:650;color:var(--muted);font-variant-numeric:tabular-nums;display:flex;flex-wrap:wrap;gap:4px 8px;align-items:center}
.now{font-size:11.5px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--page);background:var(--ink);border-radius:6px;padding:2px 6px}
.tcard h4{font-size:21px;line-height:1.15;letter-spacing:-.02em;font-weight:780;margin:5px 0 2px}
.role{color:var(--ink-2);font-size:15.5px;font-weight:600}
.fact{margin-top:9px;font-size:16.5px;line-height:1.35;font-weight:600}
details{margin-top:6px}
summary{cursor:pointer;font-size:14.5px;font-weight:650;color:var(--ink-2);width:max-content;padding:4px 0;list-style:none;display:flex;align-items:center;gap:6px}
summary::-webkit-details-marker{display:none}
summary::after{content:"+";font-weight:700}
details[open] summary::after{content:"–"}
.pts{margin-top:4px;display:grid;gap:5px;font-size:15.5px;line-height:1.35}
.pts li{padding-left:16px;position:relative}
.pts li::before{content:"";position:absolute;left:2px;top:.6em;width:5px;height:5px;border-radius:50%;background:var(--axis)}
.foot{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;margin-top:12px}
.lz{display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:700;color:var(--ink-2)}
.lz i{width:9px;height:9px;border-radius:3px;background:var(--c)}
.more-link{font-size:14.5px;font-weight:700;display:inline-flex;gap:5px;align-items:center}
.more-link .icon{width:16px;height:16px}
.q{margin-top:12px;background:var(--wash);border-radius:10px;padding:9px 11px;font-size:14px;font-weight:600;line-height:1.35}
.q b{display:inline-grid;place-items:center;min-width:24px;height:21px;padding:0 6px;border-radius:7px;background:var(--ink);color:var(--page);font-size:12.5px;font-weight:800;margin-right:6px}
.wait .tcard{border-style:dashed}

footer{padding:44px 0 48px;color:var(--muted);font-size:14.5px}
footer .wrap{display:flex;flex-wrap:wrap;gap:10px 22px;align-items:center;justify-content:space-between;border-top:1px solid var(--ring);padding-top:22px}
footer nav{display:flex;flex-wrap:wrap;gap:6px 18px}
footer a{color:var(--ink-2)}

/* the welcome */
dialog#ask{border:0;padding:0;background:transparent;color:var(--ink);width:min(560px,100% - 20px);max-height:calc(100dvh - 20px);overflow:visible}
dialog#ask::backdrop{background:rgba(8,8,8,.66);backdrop-filter:blur(5px)}
.ask{background:var(--raised);border-radius:26px;box-shadow:var(--shadow);padding:22px 16px 16px;position:relative}
@media (min-width:560px){.ask{padding:28px 24px 20px}}
.ask .kicker{color:var(--muted)}
.ask h2{font-size:clamp(26px,6.4vw,34px);letter-spacing:-.03em;line-height:1.05;font-weight:800;margin:6px 0 14px;padding-right:40px}
.ask h2:focus{outline:none}
.ask .close{position:absolute;right:12px;top:12px;width:40px;height:40px;border-radius:12px;border:0;background:var(--wash);color:var(--ink);display:grid;place-items:center;cursor:pointer}
.ask .doors{padding:0;grid-template-columns:1fr 1fr;gap:9px}
.ask .door{min-height:128px;padding:14px}
.ask .door .big{width:54px;height:54px;right:4px;top:4px;stroke-width:1.3}
.ask .door b{font-size:19px}
.ask .door span{font-size:13.5px}
.stay{margin-top:10px;width:100%;display:flex;align-items:center;justify-content:center;gap:8px;min-height:48px;border-radius:14px;border:1.5px dashed var(--axis);
background:transparent;color:var(--ink);font:650 15.5px var(--font);cursor:pointer}
.stay .icon{width:18px;height:18px}
"""

JS = r"""
(() => {
  const LENSES = ['trade', 'sports', 'career', 'focus'];
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const dlg = $('#ask');
  const seen = () => { try { return sessionStorage.getItem('mc.asked'); } catch (e) { return null; } };
  const mark = () => { try { sessionStorage.setItem('mc.asked', '1'); } catch (e) {} };

  // one look at a time: its panel opens and the timeline shows only its entries
  const setLens = (lens, scroll) => {
    if (!LENSES.includes(lens)) lens = 'all';
    $$('.panel').forEach((p) => { p.hidden = p.id !== lens; });
    $$('.ev').forEach((e) => { e.hidden = lens !== 'all' && e.dataset.lens !== lens; });
    $$('.year').forEach((y) => {
      const any = $$('.ev', y).some((e) => !e.hidden);
      y.hidden = !any && lens !== 'all';
      const c = $('.cont', y); if (c) c.hidden = lens !== 'all';
    });
    $$('.pill.yr').forEach((a) => { const y = document.getElementById(a.getAttribute('href').slice(1)); a.hidden = !y || y.hidden; });
    $$('[data-lens-link]').forEach((a) => a.setAttribute('aria-current', String(a.dataset.lensLink === lens)));
    if (scroll) (lens === 'all' ? $('#timeline') : document.getElementById(lens)).scrollIntoView({ block: 'start' });
  };
  const fromHash = () => location.hash.slice(1);
  $$('[data-lens-link]').forEach((a) => a.addEventListener('click', (e) => {
    e.preventDefault();
    const lens = a.dataset.lensLink;
    if (dlg && dlg.open) dlg.close();
    history.pushState(null, '', lens === 'all' ? '#timeline' : '#' + lens);
    setLens(lens, true);
  }));
  window.addEventListener('popstate', () => setLens(fromHash(), LENSES.includes(fromHash())));
  setLens(fromHash(), LENSES.includes(fromHash()));

  // the welcome: on arrival, once per visit; a link to a part of the page (#...) or ?stay skips it
  if (dlg && dlg.showModal) {
    if (!seen() && !location.hash && !/[?&]stay\b/.test(location.search)) dlg.showModal();
    dlg.addEventListener('close', mark);
    dlg.addEventListener('click', (e) => { if (e.target === dlg) dlg.close(); });
    $$('a', dlg).forEach((a) => a.addEventListener('click', mark));
    $$('[data-ask]').forEach((b) => b.addEventListener('click', (e) => { e.preventDefault(); dlg.showModal(); }));
  }

  // newest first, or from the start
  const flip = $('#flip'), tl = $('.tl');
  if (flip) flip.addEventListener('click', () => {
    const rev = tl.classList.toggle('rev');
    flip.setAttribute('aria-pressed', String(rev));
    flip.lastChild.textContent = rev ? 'From the start' : 'Newest first';
    const bar = $('.bar'); $$('.pill.yr', bar).reverse().forEach((a) => bar.insertBefore(a, $('.sep', bar)));
  });

  // the year you're in lights up as you scroll
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((es) => es.forEach((e) => {
      if (!e.isIntersecting) return;
      $$('.pill.yr').forEach((a) => a.classList.toggle('on', a.getAttribute('href') === '#' + e.target.id));
    }), { rootMargin: '-130px 0px -70% 0px' });
    $$('.year').forEach((y) => io.observe(y));
  }
})();
"""


def build(content, icons: dict, review: bool, portfolio: str, site: Path, inline: bool) -> str:
    def icon(name: str, cls: str = "icon") -> str:
        return f'<svg class="{cls}" viewBox="0 0 24 24" aria-hidden="true">{icons[name]}</svg>'

    def img(name: str) -> str:
        if inline:
            p = site / "assets" / "img" / name
            p = p if p.exists() else site / "portfolio" / "assets" / "img" / name
            return f"data:image/webp;base64,{base64.b64encode(p.read_bytes()).decode()}"
        return f"assets/img/{name}"

    def url(u: str) -> str:
        return E(u.replace("{portfolio}", portfolio))

    today = date.fromisoformat(content.TODAY)
    lenses = {k: (name, line, ic) for k, name, line, ic in content.LENSES}
    entries = [e for e in content.ENTRIES if review or e["status"] == "public"]
    count = {k: sum(1 for e in entries if e["lens"] == k and e["status"] == "public") for k in lenses}

    def door(k: str, href: str | None = None) -> str:
        name, line, ic = lenses[k]
        link = f'href="{E(href)}"' if href else f'href="#{k}" data-lens-link="{k}"'
        return (f'<a class="door" style="--c:var(--s-{k})" {link}>{icon(ic, "icon big")}{icon("arrow", "icon go")}'
                f'<b>{E(name)}</b><span>{E(line)}</span></a>')

    # the welcome: the trades door goes straight to the trades portfolio (the people his emails send here)
    ask = f"""<dialog id="ask" aria-labelledby="ask-h"><div class="ask">
<form method="dialog"><button class="close" aria-label="Close">{icon("x")}</button></form>
<div class="kicker">Welcome</div><h2 id="ask-h" tabindex="-1" autofocus>Take a look into</h2>
<div class="doors">{door("trade", portfolio)}{door("sports")}{door("career")}{door("focus")}</div>
<form method="dialog"><button class="stay">{icon("eye")}Just looking around</button></form>
</div></dialog>"""

    def panel(k: str) -> str:
        name, line, ic = lenses[k]
        p = content.PANELS[k]
        left = [f'<div class="kicker">{icon(ic)}A look into</div><h2>{E(name)}</h2><p class="line">{E(p["line"])}</p>']
        if p.get("stats"):
            left.append('<div class="nums">' + "".join(f'<div class="num"><b>{E(a)}</b><span>{E(b)}</span><small>{E(c)}</small></div>'
                                                       for a, b, c in p["stats"]) + "</div>")
        if p.get("steps"):
            left.append('<div class="steps">' + "".join(f"<span><i>{i}</i>{E(s)}</span>" for i, s in enumerate(p["steps"], 1)) + "</div>")
        if p.get("chips"):
            left.append('<div class="tags">' + "".join(f"<span>{E(c)}</span>" for c in p["chips"]) + "</div>")
        if p.get("links"):
            left.append('<div class="acts">' + "".join(
                f'<a class="btn{" primary" if i == 0 else ""}" href="{url(u)}"{" rel=noopener" if u.startswith("http") else ""}>'
                f'{icon(ic2) if ic2 != "arrow" else ""}{E(t)}{icon("arrow") if ic2 == "arrow" else ""}</a>'
                for i, (t, u, ic2) in enumerate(p["links"])) + "</div>")
        right = ""
        if p.get("image"):
            f, alt = p["image"]
            right = f'<figure><img src="{img(f)}" alt="{E(alt)}" loading="lazy" width="1600" height="1000"><figcaption>Demo data: every name and number in this picture is made up.</figcaption></figure>'
        return (f'<section class="panel{"" if right else " solo"}" id="{k}" style="--c:var(--s-{k})"><div>{"".join(left)}</div>{right}</section>')

    def card(e: dict, n: int) -> str:
        going = e["end"] == "now"
        when = " · ".join(x for x in (e["when"], e["place"]) if x)
        cover = (f'<img src="{img(e["image"])}" alt="{E(e.get("alt", ""))}" loading="lazy">' if e.get("image")
                 else icon(e["icon"]) + (f'<small>{icon("image")}your picture here</small>' if review else ""))
        b = [f'<div class="when">{E(when)}{"<span class=now>Now</span>" if going else ""}</div>' if when or going else "",
             f'<h4>{E(e["title"])}</h4><p class="role">{E(e["role"])}</p>']
        if e.get("fact"):
            b.append(f'<p class="fact">{E(e["fact"])}</p>')
        if e.get("more"):
            b.append(f'<details{" open" if review else ""}><summary>More</summary><ul class="pts">'
                     + "".join(f"<li>{E(x)}</li>" for x in e["more"]) + "</ul></details>")
        foot = f'<span class="lz"><i></i>{E(lenses[e["lens"]][0])}</span>'
        if e.get("link"):
            foot += f'<a class="more-link" href="{url(e["link"][1])}">{E(e["link"][0])}{icon("arrow")}</a>'
        b.append(f'<div class="foot">{foot}</div>')
        if review and (e.get("ask") or e["status"] == "ask"):
            b.append(f'<div class="q"><b>{n}</b>{E(e.get("ask") or "Show it?")}</div>')
        cls = "ev" + (" going" if going else "") + (" wait" if e["status"] == "ask" else "")
        return (f'<li class="{cls}" data-lens="{e["lens"]}" style="--c:var(--s-{e["lens"]})"><article class="tcard" id="e-{e["id"]}">'
                f'<div class="cover">{cover}</div><div class="tb">{"".join(b)}</div></article></li>')

    # the timeline: a year at a time, newest first; a year with nothing new says what was still going
    dated = [e for e in entries if e["start"]]
    years = sorted({int(e["start"][:4]) for e in dated}, reverse=True)
    numbers, n = {}, 0
    order = []
    for y in range(max(years), min(years) - 1, -1):
        here = sorted((e for e in dated if int(e["start"][:4]) == y), key=lambda e: (e["start"], e["end"] == "now"), reverse=True)
        order.append((y, here))
    undated = [e for e in entries if not e["start"]]
    for _, here in order:
        for e in here:
            n += 1
            numbers[e["id"]] = n
    for e in undated:
        n += 1
        numbers[e["id"]] = n

    def ends(e) -> int:
        return today.year if e["end"] == "now" else int(e["end"][:4])

    secs = []
    for y, here in order:
        going = [e["title"] for e in dated if int(e["start"][:4]) < y <= ends(e) and e["status"] == "public"]
        cont = (f'<li class="cont">Still going: {E(", ".join(going[:5]))}</li>' if going and not here else "")
        secs.append(f'<section class="year" id="y{y}"><div class="ylab" aria-hidden="true">{y}</div>'
                    f'<ol class="items" aria-label="{y}">{"".join(card(e, numbers[e["id"]]) for e in here)}{cont}</ol></section>')
    if undated:
        secs.append('<section class="year" id="yalso"><div class="ylab" aria-hidden="true">Also</div><ol class="items" aria-label="Also">'
                    + "".join(card(e, numbers[e["id"]]) for e in undated) + "</ol></section>")
    year_pills = "".join(f'<a class="pill yr" href="#y{y}">{y}</a>' for y, _ in order)
    lens_pills = '<a class="pill" href="#timeline" data-lens-link="all" aria-current="true">All</a>' + "".join(
        f'<a class="pill" href="#{k}" data-lens-link="{k}" style="--c:var(--s-{k})"><i></i>{E(lenses[k][0])}</a>' for k in lenses)

    waiting = sum(1 for e in entries if e["status"] == "ask")
    review_bar = (f'<div class="review">Review copy · the dashed cards ({waiting}) are not on the live site · numbered boxes are questions for you</div>'
                  if review else "")
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Malachi Collins</title>
<meta name="description" content="Malachi Collins: a look into the trades, sports, skills and career, and FOCUS, and one timeline from now back to 2021.">
<meta property="og:type" content="website">
<meta property="og:title" content="Malachi Collins">
<meta property="og:description" content="A look into the trades, sports, skills and career, and FOCUS.">
<meta property="og:url" content="https://malachicollins.org/">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
{'<meta name="robots" content="noindex">' if review else ''}
<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="top"><div class="wrap">
<a class="brand" href="#main"><span class="mono">MC</span><span>Malachi Collins</span></a>
<nav aria-label="Main">{"".join(f'<a class="hide-s" href="#{k}" data-lens-link="{k}">{E(lenses[k][0])}</a>' for k in lenses)}<a href="#timeline" data-lens-link="all">Timeline</a></nav>
</div></header>
{review_bar}
<main id="main">
<div class="wrap">
<section class="hero">
<div>
<h1>Malachi Collins</h1>
<p class="lead">Take a look into the trades, sports, my skills and career, or FOCUS. Or scroll the timeline.</p>
<div class="meta"><span>{icon("pin")}Hartford, CT</span><span>{icon("cap")}CCSU, class of 2027</span></div>
</div>
<div class="shot"><img src="{img("headshot.webp")}" width="480" height="480" alt="Malachi Collins"></div>
</section>
<nav class="doors" aria-label="Take a look into">{"".join(door(k) for k in lenses)}</nav>
{"".join(panel(k) for k in lenses)}

<section class="block" id="timeline">
<div class="head"><div><h2>The timeline</h2><p>Scroll it: now, back to 2021.</p></div></div>
<div class="bar">{year_pills}<span class="sep"></span>{lens_pills}<span class="sep"></span>
<button class="pill" id="flip" aria-pressed="false">{icon("swap")}Newest first</button></div>
<div class="tl">{"".join(secs)}</div>
</section>
</div>
</main>
<footer><div class="wrap"><span>Malachi Collins · Hartford, CT</span>
<nav aria-label="Links"><a href="{E(portfolio)}">Trades portfolio</a><a href="https://www.linkedin.com/in/malachi-collins/" rel="noopener">LinkedIn</a><a href="mailto:malachibcollins@gmail.com">Email</a><a href="#" data-ask>Welcome</a></nav>
</div></footer>
{ask}
<script>{JS}</script>
</body>
</html>
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--review", action="store_true")
    ap.add_argument("--inline", action="store_true", help="put the pictures inside the page")
    ap.add_argument("--content", default=str(HERE / "content.py"))
    ap.add_argument("--portfolio", default="portfolio/")
    ap.add_argument("--site", default=str(HERE.parent.parent / "docs"))
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    spec = importlib.util.spec_from_file_location("content", a.content)
    content = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(content)
    site = Path(a.site)
    page = build(content, load_icons(site / "portfolio" / "assets" / "icons.svg"), a.review, a.portfolio, site, a.inline)
    Path(a.out).write_text(page, encoding="utf-8")
    print(f"wrote {a.out} ({len(page) // 1024} KB)")


if __name__ == "__main__":
    main()
