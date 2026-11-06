#!/usr/bin/env python3
"""Aufstellungsfeld (Finn 06.11.2026): Reihen weiter auseinander, damit Minute unter dem Namen (z. B. Prašnikar ↓61')
nicht mit dem Tor-Symbol der Reihe darunter (Peddemors) kollidiert. Gilt für alle Aufstellungen (offiziell, Prognose).
Höhe 470/520/570 -> 520/610/680 px, oberste Reihe etwas höher (9 statt 11 %), Reihen über 77 statt 75 %.
Aufruf: python3 tools/feld_abstand_patch.py <index.html>"""
import sys
ERS = [
    # Vorlagen nach Abpfiff: Der Spieltage-Lauf schreibt Tore an die Spielerinnen, aber keine Vorlagen. Dann aus p.tore ergänzen.
    ("""      if (!live && !luecke) return;""",
     """      const ohneV = p.status === "beendet" && (p.tore || []).some(t => t.vorlage && t.seite === seite) && !alle.some(s => s.vorl > 0);
      if (!live && !luecke && ohneV) { const nn2 = x => nNorm(x).replace(/[^a-z0-9 -]/g, "");
        (p.tore || []).filter(t => t.seite === seite && t.vorlage).forEach(t => { const x = nn2(t.vorlage), s = alle.find(s => nn2(s.n) === x) || alle.find(s => nn2(s.n).endsWith(x) || x.endsWith(nn2(s.n)));
          if (s) { s._lt = true; s.vorl = (s.vorl || 0) + 1; } }); return; }
      if (!live && !luecke) return;"""),
    ("const n = rows.length, H = n <= 4 ? 470 : n === 5 ? 520 : 570, F = n >= 6 ? 48 : 54;",
     "const n = rows.length, H = n <= 4 ? 520 : n === 5 ? 610 : 680, F = n >= 6 ? 48 : 54;"),
    ("const y = n === 1 ? 50 : 11 + ri * (75 / (n - 1));",
     "const y = n === 1 ? 50 : 9 + ri * (77 / (n - 1));"),
]
s = open(sys.argv[1], encoding="utf-8").read()
for a, b in ERS:
    if s.count(a) != 1:
        sys.exit(f"passt {s.count(a)}-mal: {a[:60]}")
    s = s.replace(a, b)
open(sys.argv[1], "w", encoding="utf-8").write(s)
print("ok")
