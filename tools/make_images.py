"""Draw the small images: the phone home-screen icon and the link-preview card.

  python3 tools/make_images.py
"""
from __future__ import annotations

import base64
import pathlib

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "docs" / "portfolio" / "assets" / "img"

ICON = """<html><body style="margin:0;background:#0b0b0b;width:180px;height:180px;display:grid;place-items:center;
font:700 72px system-ui,-apple-system,Helvetica,Arial,sans-serif;color:#f9f9f7;letter-spacing:-1px">MC</body></html>"""

CARD = """<html><body style="margin:0;width:1200px;height:630px;background:#f9f9f7;font-family:system-ui,-apple-system,Helvetica,Arial,sans-serif;color:#0b0b0b;position:relative;overflow:hidden">
<div style="position:absolute;inset:0;background:radial-gradient(40% 50% at 82% 20%,rgba(42,120,214,.20),transparent 70%),radial-gradient(30% 40% at 96% 75%,rgba(224,138,18,.16),transparent 70%),radial-gradient(34% 44% at 64% 92%,rgba(19,163,143,.16),transparent 70%)"></div>
<div style="position:relative;padding:68px 80px;display:flex;flex-direction:column;height:100%;box-sizing:border-box">
  <div style="display:flex;align-items:center;gap:16px;font-size:26px;font-weight:600;color:#52514e">
    <span style="width:56px;height:56px;border-radius:14px;background:#0b0b0b;color:#f9f9f7;display:grid;place-items:center;font-size:22px;font-weight:700">MC</span>Portfolio</div>
  <img src="__HEADSHOT__" style="position:absolute;right:80px;top:68px;width:200px;height:200px;border-radius:50%;border:6px solid #fff;box-shadow:0 0 0 1px rgba(11,11,11,.1),0 20px 50px -20px rgba(11,11,11,.35)">
  <div style="font-size:88px;font-weight:800;letter-spacing:-3px;margin-top:44px">Malachi Collins</div>
  <div style="font-size:36px;line-height:1.3;margin-top:16px;max-width:860px;font-weight:600;letter-spacing:-.5px">Looking for part-time, registered apprentice hours toward a Connecticut low-voltage, electrical or plumbing license.</div>
  <div style="margin-top:auto;display:flex;gap:14px;font-size:24px;color:#52514e">
    <span style="padding:8px 16px;border-radius:999px;background:#e6effa;color:#1c5cab;font-weight:800">C-6</span>
    <span style="padding:8px 16px;border-radius:999px;background:#fcefd9;color:#9a5200;font-weight:800">E-2</span>
    <span style="padding:8px 16px;border-radius:999px;background:#dcf3ee;color:#0b6e61;font-weight:800">P-2</span>
    <span style="padding:8px 16px;border-radius:999px;background:rgba(11,11,11,.05)">Hartford, CT</span>
    <span style="padding:8px 16px;border-radius:999px;background:rgba(11,11,11,.05)">CCSU, class of 2027</span>
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
        headshot = "data:image/webp;base64," + base64.b64encode((IMG / "headshot.webp").read_bytes()).decode()
        page.set_content(CARD.replace("__HEADSHOT__", headshot))
        page.screenshot(path=str(IMG / "og-card.png"))
        b.close()
    print("apple-touch-icon.png, og-card.png")


if __name__ == "__main__":
    main()
