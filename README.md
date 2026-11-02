# Malachi Collins: portfolio

Three pages for the contractors, union training directors and employers who open the link in my apprenticeship
emails: **Home** (who I am and the C-6 license I'm working toward), **Work** (Mally's Home Solutions, FOCUS,
internships, hackathons) and **Resume** (a timeline, the details and the PDF).

**Live at:** https://mallythearchitect.github.io (GitHub Pages, from the `docs/` folder of this repo's `main` branch).
Nothing goes live until a change is pushed, and a change is pushed only when I say yes.

## What's here

| Path | What it is |
|---|---|
| `docs/` | The website, exactly as published: `index.html`, `work.html`, `resume.html`, `404.html` |
| `docs/assets/site.css` | The one stylesheet: phone-first, light and dark follow the device |
| `docs/assets/icons.svg` | The line icons the pages use |
| `docs/assets/img/` | Screenshots (`mhs-*` from Mally's, `focus-*` from the FOCUS demo), the phone icon and the link-preview card |
| `docs/assets/Malachi-Collins-Resume.pdf` | The resume, made from the Word file with the phone number taken out |
| `tools/shots.py` | Retakes the screenshots, hiding private details first and refusing to save one that still shows any |
| `tools/resume_pdf.py` | Rebuilds the resume PDF from the Word file |
| `tools/make_images.py` | Redraws the phone icon and the link-preview card |
| `scripts/changelog.py` | Writes CHANGELOG.md and tags a release a day, the same as my other repos |

## Look at it on this Mac

```bash
python3 -m http.server 8791 --bind 127.0.0.1 --directory docs
```

Then open http://127.0.0.1:8791.

## What never goes on it

- My home address, my phone number, money, and anything about customers (names, addresses, jobs, what they paid).
- Company work from internships: words only, no screenshots.
- Anything from the research map, the career system or the Trade Door Finder's research.

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
  of my own can point here later.
- **Watch:** GitHub's Pages terms or pricing changing.
