# Malachi Collins: my website

This repo is my public website, malachicollins.org. It has two parts: **the front page** (https://malachicollins.org/, see
**The front page** below) and **the portfolio** (https://malachicollins.org/portfolio/), which came first and which the
front page's trades look leads to.

The portfolio is for the contractors, union training directors and employers who open the link in
my apprenticeship emails: **Home** (my goal: apprentice hours toward a C-6, E-2 or P-2 license; my availability from
Jan 1, 2027; what comes with me on top of learning the trade; my technical skill set and why the trades), **Work** (the
software behind the home-services business I ran over summer 2026, FOCUS as my personal ERP, and both internships shown
with drawn mock-ups), **Projects** (research that turns into leads, tools and models, the power-grid AI and how I
work) and **Resume** (a work timeline you can hover and click, the details, skills and the PDF). It lives in its own folder, `docs/portfolio/`.

Since Nov 10, 2026 the domain's front page is the site's own (see **The front page** below): a welcome with four looks
(the trades, sports, skills and career, FOCUS) and one timeline to scroll. The trades look leads to this portfolio.

**Live at:** https://malachicollins.org/ and https://malachicollins.org/portfolio/ (GitHub Pages, from the `docs/` folder of
this repo's `main` branch; the domain was registered at Squarespace on Nov 1, 2026 and pointed here on Nov 5, 2026). The old
address, https://mallythearchitect.github.io/portfolio/, forwards to it, so links already sent keep working.
Nothing goes live until a change is pushed, and a change is pushed only when I say yes.

The portfolio will also answer at an address of its own, https://portfolio.malachicollins.org, once my server is up: it
serves these same pages from this repo. That isn't live yet, and the addresses above keep working either way.

## What's here

| Path | What it is |
|---|---|
| `docs/` | Everything GitHub Pages publishes. `index.html` is the front page (built, don't edit it by hand); `404.html` is the not-found page |
| `tools/front/content.py` | The front page's content: the four looks and every entry on the timeline |
| `tools/front/build.py` | Draws `docs/index.html` from that content |
| `docs/assets/img/` | The front page's pictures |
| `docs/portfolio/` | The portfolio section, self-contained: `index.html`, `work.html`, `projects.html`, `resume.html` |
| `docs/portfolio/assets/site.css` | The one stylesheet: phone-first, light and dark follow the device, motion only when the device allows it |
| `docs/portfolio/assets/site.js` | Small touches of motion (fade-ins, count-ups, a pointer spotlight). Every page works without it |
| `docs/portfolio/assets/icons.svg` | The line icons the pages use |
| `docs/portfolio/assets/img/` | My headshot (`headshot.webp`, on Home), screenshots (`mhs-*` from Mally's, `focus-*` from the FOCUS demo), the phone icon and the link-preview card |
| `docs/portfolio/assets/Malachi-Collins-Resume.pdf` | The resume as I exported it from my Word file (Nov 5, 2026), phone number included |
| `tools/shots.py` | Retakes the screenshots, hiding private details first and refusing to save one that still shows any |
| `tools/resume_pdf.py` | Rebuilds the resume PDF from the Word file |
| `tools/make_images.py` | Redraws the phone icon and the link-preview card |
| `scripts/changelog.py` | Writes CHANGELOG.md and tags a release a day, the same as my other repos |

## The front page

What people see at https://malachicollins.org/: what I want shown, not everything about me.

- **The welcome.** On arrival it asks "Take a look into": The trades, Sports, Skills & career, FOCUS, or just looking
  around. The trades door goes straight to the portfolio, for the people my apprenticeship emails send here. It shows once
  per visit; a link to a part of the page (like `/#career`) skips it.
- **The four looks.** Picking one opens it (a line, a few numbers, where it leads) and narrows the timeline to it.
  `/#trade`, `/#sports`, `/#career` and `/#focus` open a look directly.
- **The timeline.** One scroll, newest first (or from the start), a year at a time, every entry with its picture.
- **What my engines publish.** The Sports and the Skills & career looks also show what I published from my private Sports
  and Career engines (feats and stats, clips, skill sets, projects): only what I switched on there and pressed Publish
  for. The page reads those two feeds when it opens; until one exists, or while the server isn't up, the look stays as
  it is. Everything from a feed is written as text, and a link is used only when it is an https address.
- **Sign in and Developer mode.** The page asks my private hub one thing: is this device signed in? Signed out, a small
  Sign in link shows in the footer; signed in, a Developer mode button shows in the top bar and opens the hub. The hub
  does the checking, not this page, and while the hub isn't up neither shows.

To change it: edit `tools/front/content.py`, then

```bash
python3 tools/front/build.py --out docs/index.html
```

A picture for an entry: save it in `docs/assets/img/` and name it in that entry's `"image"`. Without one, the entry shows
its icon. The same rules as below decide what goes on it; an entry goes in only on my yes.

**Still to come:** my own pictures on more of the entries, what I publish from Sports (feats, stats and clips) and from
Career (skill sets and projects) once my server is up, and a public version of FOCUS.

## How malachicollins.org was pointed here

The domain has pointed here since Nov 5, 2026 (steps 1 to 3). The steps are kept as the record of how it was done.

1. **At Squarespace** (account.squarespace.com → Domains → malachicollins.org → DNS): delete the **Squarespace Defaults**
   preset, then add these custom records. Leave the `v=spf1 -all` text record.

   | Type | Host | Data |
   |---|---|---|
   | A | @ | 185.199.108.153 |
   | A | @ | 185.199.109.153 |
   | A | @ | 185.199.110.153 |
   | A | @ | 185.199.111.153 |
   | CNAME | www | mallythearchitect.github.io |

2. **Check they're live:** `dig +short @nsd1.squarespacedns.com malachicollins.org A` lists the four 185.199.x.153
   addresses, and `dig +short @nsd1.squarespacedns.com www.malachicollins.org` says `mallythearchitect.github.io.`
3. **Tell GitHub:** `echo malachicollins.org > docs/CNAME`, save it, push (on my yes).
4. **HTTPS:** once GitHub has the certificate (Settings → Pages says so, usually within the hour):
   `gh api -X PUT repos/mallythearchitect/mallythearchitect.github.io/pages -F https_enforced=true`
5. **Optional, recommended:** verify the domain on GitHub (profile Settings → Pages → Add a domain) and add the TXT record
   it gives at Squarespace, so nobody else can ever claim it on GitHub.
6. **The emails:** put `https://malachicollins.org/portfolio/` in Trade Doors → Emails → Portfolio link.

## Look at it on this Mac

```bash
python3 -m http.server 8791 --bind 127.0.0.1 --directory docs
```

Then open http://127.0.0.1:8791/ (the front page) or http://127.0.0.1:8791/portfolio/. On this Mac the front page doesn't
ask the hub or read the feeds; it does that only at its real https address.

## What never goes on it

- My home address, my personal money, and anything about customers (names, addresses, what each one paid). By choice,
  since Nov 5, 2026: my phone number, and Mally's billed total ($3,345 over 24 jobs, Jul 9 to Sep 2, 2026, from the
  app's visits log).
- Company work from internships: words and drawn mock-ups only, with made-up names and numbers and a label saying so.
  No screenshots, no real data.
- Journal and Self content, and the personal areas of the research map (only work areas' session counts are shown).
- The Trade Door Finder's company details: only counts by county and trade.

The screenshots come from **copies** of the apps, never the live ones. Mally's shots hide the goals, the business
numbers, Right now, the customers-per-town column and the stock photo before each picture is taken, and
`tools/shots.py --mhs-data <copy>/route-map/data` checks every Mally's picture against the names, phone numbers and street
addresses in that data: if one is on screen, the picture isn't saved. FOCUS shots use its demo mode, where every
name and number is made up.

## Change something

1. Edit the page in `docs/` (or rerun a tool above).
2. Look at it on this Mac.
3. Save the change (`git commit`), then `python3 scripts/changelog.py --log-only` and save CHANGELOG.md with it.
4. Only on my yes: `python3 scripts/changelog.py --tags-only`, `git push --follow-tags`, then
   `python3 scripts/changelog.py --releases`. GitHub Pages publishes within a minute or two.

### Retake the screenshots

Copy the apps somewhere outside their repos, start the copies, then run the tool:

```bash
cd <copy>/route-map && MHS_PORT=8799 python3 src/serve.py
```

```bash
cd <copy>/mindscape-app && MINDSCAPE_DEMO=1 MINDSCAPE_PORT=8780 .venv/bin/python -m engine
```

```bash
python3 tools/shots.py --mhs-data <copy>/route-map/data
```

### Rebuild the resume PDF

The live PDF is my own export from Word: export it again and replace the file. The tool below is the older way;
it takes the phone number out and fixes a few typos.

```bash
python3 tools/resume_pdf.py "$HOME/Desktop/Malachi Collins's Resume-2026.docx"
```

## The hosting call (Alignment Law)

GitHub Pages, ruled **Adopt · Watch** on Nov 1, 2026.

- **Preserve:** free, on the GitHub account I already have; nothing private is in the repo or on the site.
- **Develop:** the portfolio is live before outreach starts and before the Nov 13–28 trip.
- **Fine line:** the free plan publishes only from a public repo, so these files are public too (they're the site
  anyway). Pages is for personal and project sites, not for running a business.
- **Exit:** plain files. Moving them to any other host takes about an hour. My own domain, malachicollins.org, has
  pointed here since Nov 5, 2026, so a move wouldn't change the address.
- **Watch:** GitHub's Pages terms or pricing changing.
