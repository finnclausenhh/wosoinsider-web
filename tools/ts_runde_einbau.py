#!/usr/bin/env python3
"""Sammel-News "Spielt sie? x Fragen zum y. Spieltag" (Finn 04.11.2026) in einen Ticker einbauen, der ts_duell schon hat.
Aufruf: python3 tools/ts_runde_einbau.py <datei> [...]  (ticker/index.html, Artifact index.html, tools/gami/gami.js)"""
import pathlib, sys
G = pathlib.Path(__file__).resolve().parent / "gami"
js = (G / "ts_duell.js").read_text(encoding="utf-8")
neu = js[js.index("  // Sammel-News (Finn 04.11.2026)"):]
ERS = [
    ('    if (m.grafik && m.grafik.typ === "fansdaten") return fdBild(m, g);\n',
     '    if (m.grafik && m.grafik.typ === "fansdaten") return fdBild(m, g);\n    if (m.typ === "tipprunde") return trBild(m, g);\n'),
    ('  function list(){\n    GAME = null; ARTIKEL = null;\n', '  function list(){\n    GAME = null; ARTIKEL = null;\n    tsRundeNews();\n'),
    ('    if (m.typ === "punkt") { $("#main").innerHTML = `<div class="det">${zurueck()}${punktArtikel(m)}</div>`;',
     '    if (m.typ === "tipprunde") { tippschein(); return; }\n    if (m.typ === "punkt") { $("#main").innerHTML = `<div class="det">${zurueck()}${punktArtikel(m)}</div>`;'),
]
for f in sys.argv[1:]:
    p = pathlib.Path(f); s = p.read_text(encoding="utf-8")
    if "function tsRundeNews(" in s: sys.exit(f"{f}: schon eingebaut")
    ticker = "function article(" in s
    a = s.index("  function tippschein(){")
    s = s[:a] + neu + "\n" + s[a:]
    for alt, n in ERS:
        c = s.count(alt)
        if c == 1: s = s.replace(alt, n)
        elif ticker or c > 1: sys.exit(f"{f}: Anker {alt[:50]!r} {c}-mal")
    p.write_text(s, encoding="utf-8"); print("ok", f)
