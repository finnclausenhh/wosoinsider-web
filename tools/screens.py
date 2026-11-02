"""Erneuert die Screenshots der Startseite (bilder/news.webp, spielplan.webp, inside.webp).

Aufruf: python3 tools/screens.py <zielordner, z. B. bilder>
Fotografiert den Live-Ticker auf wosoinsider.de im iPhone-Format (390 px breit, 2x),
schneidet auf 2:3 zu und speichert als WebP in 390 x 585. Aufrufe laufen über ?intern,
zählen also nicht in GoatCounter mit.
"""
import io, os, sys
from PIL import Image
from playwright.sync_api import sync_playwright

ANSICHTEN = [("news", ""), ("spielplan", "#spielplan"), ("inside", "#inside")]

def main(ziel):
    os.makedirs(ziel, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        p = b.new_context(viewport={"width": 390, "height": 780}, device_scale_factor=2).new_page()
        for name, hash_ in ANSICHTEN:
            p.goto("about:blank")
            p.goto("https://wosoinsider.de/ticker/?intern" + hash_, wait_until="networkidle")
            p.wait_for_timeout(3500)
            im = Image.open(io.BytesIO(p.screenshot())).convert("RGB")
            im = im.crop((0, 0, 780, 1170)).resize((390, 585), Image.LANCZOS)
            im.save(os.path.join(ziel, name + ".webp"), "WEBP", quality=82, method=6)
            print("ok", name)
        b.close()

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "bilder")
