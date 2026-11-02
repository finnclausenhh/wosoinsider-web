"""Erneuert die Screenshots der Startseite (bilder/*.webp).

Aufruf: python3 tools/screens.py <zielordner, z. B. bilder>
Fotografiert den Live-Ticker auf wosoinsider.de im iPhone-Format (390 px breit, 2x),
schneidet auf 2:3 zu und speichert als WebP in 390 x 585. Aufrufe laufen über ?intern,
zählen also nicht in GoatCounter mit.

Reihe 1 zeigt die Reiter von oben. Reihe 2 springt auf den spannenden Teil:
Ausschnitt beginnt am angegebenen Text (minus Abstand). Partie und Analyse sind
fest gewählt; bei einer neuen Partie oder Analyse hier den Hash anpassen und in
tools/bau.py (START) Link und Text nachziehen.
"""
import io, os, sys
from PIL import Image
from playwright.sync_api import sync_playwright

# Name, Hash, Text, an dem der Ausschnitt beginnt (None = oben), Abstand nach oben in px
ANSICHTEN = [
    ("news", "", None, 0),
    ("spielplan", "#spielplan", None, 0),
    ("inside", "#inside", None, 0),
    ("partie", "#bayern-pokal-0111", "Aufstellung im Spiel", 16),
    ("analyse", "#analyse", "Top-Analyse", 26),
    ("statistik", "#statistik", "Nur Liga, nach dem", 60),
]

def main(ziel):
    os.makedirs(ziel, exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        p = b.new_context(viewport={"width": 390, "height": 780}, device_scale_factor=2).new_page()
        for name, hash_, text, abstand in ANSICHTEN:
            p.goto("about:blank")
            p.goto("https://wosoinsider.de/ticker/?intern" + hash_, wait_until="networkidle")
            p.wait_for_timeout(4000)
            y = 0
            if text:
                box = p.get_by_text(text).first.bounding_box()
                y = max(0, int(box["y"] + p.evaluate("window.scrollY")) - abstand)
            im = Image.open(io.BytesIO(p.screenshot(full_page=True))).convert("RGB")
            im = im.crop((0, 2 * y, 780, 2 * y + 1170)).resize((390, 585), Image.LANCZOS)
            im.save(os.path.join(ziel, name + ".webp"), "WEBP", quality=82, method=6)
            print("ok", name, y)
        b.close()

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "bilder")
