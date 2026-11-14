# Symbole für die Gelbsperren-Sammelartikel (Finn 14.11.2026), Ergänzung zu tools/symbol_patch.py
#  - gelb_droht: "Gelbsperre droht" vor dem Spieltag (Gelbe Karte mit 4, die fünfte gestrichelt dahinter)
#  - gelbsperre: "Neue Gelbsperren" nach dem Spieltag (Gelbe Karte mit 5 und blauem Sperr-Badge)
# Rückfall: Meldungen ohne Spielerin mit Tag GELBSPERRE bekommen das Symbol auch ohne Feld "symbol".
# Aufruf: python3 tools/gelb_symbol_patch.py ticker/index.html   (derselbe Patch gilt für index.html im Artifact)
import sys

F = 'font-family="ui-monospace,Menlo,monospace" font-weight="800"'
BASIS = '<path d="M8 53h48" stroke="#8FB0FF" stroke-width="2.4" stroke-linecap="round" opacity=".55"/>'
GELB_DROHT = ('<svg class="sym" viewBox="0 -3 64 64" role="img" aria-label="Gelbsperre droht">' + BASIS +
  '<g transform="rotate(13 41 30)"><rect x="30" y="14" width="22" height="31" rx="3" fill="none" stroke="#F5B041" stroke-width="2.2" stroke-dasharray="3.6 3"/>'
  f'<text x="41" y="35" text-anchor="middle" {F} font-size="13" fill="#F5B041">5</text></g>'
  '<g transform="rotate(-9 24 30)"><rect x="12" y="13" width="24" height="33" rx="3" fill="#F5B041"/><path d="M15 16.5h9" stroke="#F4F5F7" stroke-width="1.6" stroke-linecap="round" opacity=".55"/>'
  f'<text x="24" y="37" text-anchor="middle" {F} font-size="17" fill="#2A3B5E">4</text></g></svg>')
GELBSPERRE = ('<svg class="sym" viewBox="0 -3 64 64" role="img" aria-label="Gelbsperre">' + BASIS +
  '<g transform="rotate(-8 28 29)"><rect x="16" y="11" width="24" height="33" rx="3" fill="#F5B041"/><path d="M19 14.5h9" stroke="#F4F5F7" stroke-width="1.6" stroke-linecap="round" opacity=".55"/>'
  f'<text x="28" y="35" text-anchor="middle" {F} font-size="17" fill="#2A3B5E">5</text></g>'
  '<circle cx="44.5" cy="40.5" r="10.5" fill="#2F5BFF" stroke="#2A3B5E" stroke-width="2.6"/>'
  '<circle cx="44.5" cy="40.5" r="5.6" fill="none" stroke="#F4F5F7" stroke-width="2.2"/><path d="M40.6 44.4l7.8-7.8" stroke="#F4F5F7" stroke-width="2.2" stroke-linecap="round"/></svg>')

EDITS = [
    ("  const SYMBOLE = {pk: '",
     "  const SYMBOLE = {gelb_droht: '" + GELB_DROHT + "', gelbsperre: '" + GELBSPERRE + "', pk: '"),
    ("    if (m.symbol && SYMBOLE[m.symbol]) { const hs = hh || g;",
     "    const symK = m.symbol || (!m.spielerin && (m.tags || []).includes(\"GELBSPERRE\") ? ((m.tags || []).includes(\"VORBERICHT\") ? \"gelb_droht\" : \"gelbsperre\") : null);\n"
     "    if (symK && SYMBOLE[symK]) { const hs = hh || g;"),
    ("aria-hidden=\"true\">${SYMBOLE[m.symbol]}</div>`; }", "aria-hidden=\"true\">${SYMBOLE[symK]}</div>`; }"),
]


def main(p):
    s = open(p, encoding="utf-8").read()
    if "gelb_droht:" in s:
        print("schon drin", p); return
    for a, b in EDITS:
        assert s.count(a) == 1, (s.count(a), a[:80])
        s = s.replace(a, b)
    open(p, "w", encoding="utf-8").write(s)
    print("ok", p)


if __name__ == "__main__":
    for p in sys.argv[1:]: main(p)
