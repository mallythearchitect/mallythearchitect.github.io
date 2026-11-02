"""Make the public resume PDF from the Word resume, with the phone number taken out.

  python3 tools/resume_pdf.py "$HOME/Desktop/Malachi Collins's Resume-2026.docx"

Reads the .docx with pandoc, removes every phone number, lays it out for Letter paper and prints
it to docs/assets/Malachi-Collins-Resume.pdf with Chromium (Playwright). The Word file is only read.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "assets" / "Malachi-Collins-Resume.pdf"
PHONE = re.compile(r"\(?\b\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b")

CSS = """
@page { size: Letter; margin: 0.42in 0.55in; }
* { box-sizing: border-box; }
body { margin: 0; font: 9.3pt/1.25 "Helvetica Neue", Helvetica, Arial, sans-serif; color: #111; }
h1 { font-size: 19pt; margin: 0 0 1pt; letter-spacing: -0.01em; }
.contact { margin: 0 0 5pt; color: #333; }
.contact a { color: #1c5cab; text-decoration: none; }
h2 { font-size: 10.5pt; letter-spacing: 0.06em; text-transform: uppercase; margin: 7pt 0 3pt; padding-bottom: 1.5pt;
     border-bottom: 1px solid #bbb; break-after: avoid; }
p { margin: 0 0 1pt; }
p.entry { margin-top: 4pt; break-after: avoid; }
.when { float: right; font-style: normal; font-weight: 600; color: #333; }
ul { margin: 0.5pt 0 2pt; padding-left: 13pt; }
li { margin: 0 0 0.8pt; }
li p { margin: 0; }
em { color: #333; }
"""


def build_html(docx: pathlib.Path) -> str:
    body = subprocess.run(["pandoc", "-t", "html", "--wrap=none", str(docx)],
                          check=True, capture_output=True, text=True).stdout
    # the phone number, and the separator after it
    body = re.sub(PHONE.pattern + r"\s*\|\s*", "", body)
    if PHONE.search(body):
        raise SystemExit("A phone number is still in the resume text; not writing the PDF.")
    # the LinkedIn address as a working link
    body = re.sub(r"<u>(www\.linkedin\.com/[^<]+)</u>", r'<a href="https://\1">\1</a>', body)
    # name, contact line, section headings, entry lines with their dates on the right
    body = re.sub(r"^<p><strong>([^<]+)</strong></p>", r"<h1>\1</h1>", body, count=1)
    body = re.sub(r"</h1>\s*<p>", '</h1>\n<p class="contact">', body, count=1)
    body = re.sub(r"<p><strong>([A-Z][A-Z &]+[A-Za-z &]*)</strong></p>",
                  lambda m: f"<h2>{m.group(1)}</h2>" if m.group(1).split()[0].isupper() else m.group(0), body)
    body = re.sub(r"<p>(<strong>.*?)<em><strong>([^<]+)</strong></em></p>",
                  r'<p class="entry"><span class="when">\2</span>\1</p>', body)
    return f"<!doctype html><html><head><meta charset='utf-8'><title>Malachi Collins · Resume</title><style>{CSS}</style></head><body>{body}</body></html>"


def main() -> int:
    docx = pathlib.Path(sys.argv[1]).expanduser()
    html = build_html(docx)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html, wait_until="load")
        page.emulate_media(media="print")
        page.pdf(path=str(OUT), format="Letter", print_background=True, prefer_css_page_size=True)
        if len(sys.argv) > 2:  # a preview picture of the layout, for checking
            page.set_viewport_size({"width": 816, "height": 1056})
            page.screenshot(path=sys.argv[2], full_page=True)
        browser.close()
    pages = len(re.findall(rb"/Type\s*/Page[^s]", OUT.read_bytes()))
    print(f"{OUT.relative_to(ROOT)}: {OUT.stat().st_size // 1024} KB, {pages} page(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
