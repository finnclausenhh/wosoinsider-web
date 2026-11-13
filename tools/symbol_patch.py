# Symbole für News-Kategorien ohne Spielerin und ohne Verein (Finn 13.11.2026)
# Regel: Jede neue News-Kategorie bekommt ein eigenes Symbol. Die Meldung trägt "symbol": "<schluessel>",
# das Symbol steht in SYMBOLE (SVG, viewBox 64x64, Farben: Weiß #F4F5F7, Akzent #2F5BFF, Gelb #F5B041, Hell #8FB0FF)
# und sitzt auf demselben Lichtkegel wie die Vereinslogos.
#  - pk: Pressekonferenz-Fahrplan vor dem Spieltag (Mikrofon mit Schallwellen auf einem PK-Pult)
# Aufruf: python3 tools/symbol_patch.py ticker/index.html   (derselbe Patch gilt für index.html im Artifact)
import sys

PK = '<svg class="sym" viewBox="0 -3 64 64" role="img" aria-label="Pressekonferenz"><path d="M8 49h48" stroke="#8FB0FF" stroke-width="2.4" stroke-linecap="round" opacity=".55"/><rect x="14" y="40" width="36" height="9" rx="2" fill="#2F5BFF"/><text x="32" y="47.2" text-anchor="middle" font-family="ui-monospace,Menlo,monospace" font-weight="800" font-size="7" fill="#F4F5F7" letter-spacing=".8">PK</text><path d="M32 40v-6" stroke="#F4F5F7" stroke-width="2.4" stroke-linecap="round"/><path d="M23.5 23a8.5 8.5 0 0 0 17 0" fill="none" stroke="#F4F5F7" stroke-width="2.4" stroke-linecap="round"/><rect x="26.5" y="9" width="11" height="20" rx="5.5" fill="#F4F5F7"/><path d="M28.5 15h7M28.5 19h7M28.5 23h7" stroke="#2A3B5E" stroke-width="1.4" stroke-linecap="round"/><path d="M45 13.5a10 10 0 0 1 0 13M49.5 10a15 15 0 0 1 0 20M19 13.5a10 10 0 0 0 0 13M14.5 10a15 15 0 0 0 0 20" fill="none" stroke="#F5B041" stroke-width="2.2" stroke-linecap="round"/></svg>'


def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90])
    return s.replace(a, b)


EDITS = [
    ("""  function bild(m, g, hh){
    if (m.grafik && m.grafik.typ === "fansdaten") return fdBild(m, g);""",
     """  // Symbole je News-Kategorie (Finn 13.11.2026): jede neue Kategorie ohne Spielerin/Verein bekommt hier ein eigenes Symbol
  const SYMBOLE = {pk: '@@PK@@'};
  function bild(m, g, hh){
    if (m.grafik && m.grafik.typ === "fansdaten") return fdBild(m, g);
    if (m.symbol && SYMBOLE[m.symbol]) { const hs = hh || g; return `<div class="bild fg sy" style="width:${g}px;height:${hs}px;border-radius:${g > 70 ? 11 : 8}px;background:radial-gradient(circle at 50% 45%,#3A4F78 0%,#2A3B5E 70%)" aria-hidden="true">${SYMBOLE[m.symbol]}</div>`; }"""),
    (""".mx .c.Sp{""", """.bild.sy{display:grid;place-items:center}
.bild.sy .sym{width:80%;height:80%}
.mx .c.Sp{"""),
]


def main(p):
    s = open(p, encoding="utf-8").read()
    for a, b in EDITS:
        s = rep(s, a, b.replace("@@PK@@", PK))
    open(p, "w", encoding="utf-8").write(s)
    print("ok", p)


if __name__ == "__main__":
    main(sys.argv[1])
