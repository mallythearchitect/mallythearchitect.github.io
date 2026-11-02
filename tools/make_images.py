"""Draw the small images: the phone home-screen icon and the link-preview card.

  python3 tools/make_images.py
"""
from __future__ import annotations

import pathlib

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "docs" / "assets" / "img"

ICON = """<html><body style="margin:0;background:#0b0b0b;width:180px;height:180px;display:grid;place-items:center;
font:700 72px system-ui,-apple-system,Helvetica,Arial,sans-serif;color:#f9f9f7;letter-spacing:-1px">MC</body></html>"""

CARD = """<html><body style="margin:0;width:1200px;height:630px;background:#f9f9f7;font-family:system-ui,-apple-system,Helvetica,Arial,sans-serif;color:#0b0b0b">
<div style="padding:72px 80px;display:flex;flex-direction:column;height:100%;box-sizing:border-box">
  <div style="display:flex;align-items:center;gap:16px;font-size:26px;font-weight:600;color:#52514e">
    <span style="width:56px;height:56px;border-radius:14px;background:#0b0b0b;color:#f9f9f7;display:grid;place-items:center;font-size:22px;font-weight:700">MC</span>Portfolio</div>
  <div style="font-size:84px;font-weight:750;letter-spacing:-2px;margin-top:44px">Malachi Collins</div>
  <div style="font-size:36px;line-height:1.3;margin-top:18px;max-width:900px">Looking for part-time, registered apprentice hours toward a Connecticut C-6 low-voltage license.</div>
  <div style="margin-top:auto;display:flex;gap:14px;font-size:24px;color:#52514e">
    <span style="padding:8px 16px;border-radius:999px;background:#e6effa;color:#1c5cab;font-weight:700">C-6</span>
    <span style="padding:8px 16px;border-radius:999px;background:rgba(11,11,11,.05)">Hartford, CT</span>
    <span style="padding:8px 16px;border-radius:999px;background:rgba(11,11,11,.05)">CCSU, class of 2027</span>
    <span style="padding:8px 16px;border-radius:999px;background:rgba(11,11,11,.05)">AWS Certified Cloud Practitioner</span>
  </div>
</div></body></html>"""


def main() -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 180, "height": 180})
        page.set_content(ICON)
        page.screenshot(path=str(IMG / "apple-touch-icon.png"))
        page.set_viewport_size({"width": 1200, "height": 630})
        page.set_content(CARD)
        page.screenshot(path=str(IMG / "og-card.png"))
        b.close()
    print("apple-touch-icon.png, og-card.png")


if __name__ == "__main__":
    main()
