# Malachi Collins: portfolio

The portfolio section of my website, for the contractors, union training directors and employers who open the link in
my apprenticeship emails: **Home** (who I am and the C-6 license I'm working toward), **Work** (Mally's Home Solutions
and FOCUS in depth, internships, hackathons), **Projects** (all 21 projects, the Trade Door Finder chart and a map of my
AI sessions) and **Resume** (a timeline, the details and the PDF). It lives in its own folder, `docs/portfolio/`, so the
bigger site can wrap around it later; until that site exists, the domain's front page forwards to it.

**Live at:** https://malachicollins.org/portfolio/ (GitHub Pages, from the `docs/` folder of this repo's `main` branch;
the domain was registered at Squarespace on Nov 1, 2026 and pointed here on Nov 5, 2026). The old address,
https://mallythearchitect.github.io/portfolio/, forwards to it, so links already sent keep working.
Nothing goes live until a change is pushed, and a change is pushed only when I say yes.

## What's here

| Path | What it is |
|---|---|
| `docs/` | Everything GitHub Pages publishes. `index.html` forwards to the portfolio for now; `404.html` is the not-found page |
| `docs/portfolio/` | The portfolio section, self-contained: `index.html`, `work.html`, `projects.html`, `resume.html` |
| `docs/portfolio/assets/site.css` | The one stylesheet: phone-first, light and dark follow the device |
| `docs/portfolio/assets/icons.svg` | The line icons the pages use |
| `docs/portfolio/assets/img/` | My headshot (`headshot.webp`, on Home), screenshots (`mhs-*` from Mally's, `focus-*` from the FOCUS demo), the phone icon and the link-preview card |
| `docs/portfolio/assets/Malachi-Collins-Resume.pdf` | The resume, made from the Word file with the phone number and typos fixed |
| `tools/shots.py` | Retakes the screenshots, hiding private details first and refusing to save one that still shows any |
| `tools/resume_pdf.py` | Rebuilds the resume PDF from the Word file |
| `tools/make_images.py` | Redraws the phone icon and the link-preview card |
| `scripts/changelog.py` | Writes CHANGELOG.md and tags a release a day, the same as my other repos |

## Move it to malachicollins.org

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

Then open http://127.0.0.1:8791/portfolio/.

## What never goes on it

- My home address, my phone number, money, and anything about customers (names, addresses, jobs, what they paid).
- Company work from internships: words only, no screenshots.
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

```bash
python3 tools/resume_pdf.py "$HOME/Desktop/Malachi Collins's Resume-2026.docx"
```

## The hosting call (Alignment Law)

GitHub Pages, ruled **Adopt · Watch** on Nov 1, 2026.

- **Preserve:** free, on the GitHub account I already have; nothing private is in the repo or on the site.
- **Develop:** the portfolio is live before outreach starts and before the Nov 13–28 trip.
- **Fine line:** the free plan publishes only from a public repo, so these files are public too (they're the site
  anyway). Pages is for personal and project sites, not for running a business.
- **Exit:** plain files. Moving them to AWS (S3 or the Lightsail box) or any other host takes about an hour. A domain
  of my own, malachicollins.org, points here once its DNS is set.
- **Watch:** GitHub's Pages terms or pricing changing.
