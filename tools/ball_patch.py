#!/usr/bin/env python3
"""Tor-Symbol C (Finn 06.11.2026): echter Fußball (Fünfeck mittig, fünf angeschnittene Fünfecke, Nähte), kräftig für
13 bis 16 px. Ersetzt die Konstante BALL überall (Aufstellung, Bank, Spielansicht, Legende).
Aufruf: python3 tools/ball_patch.py <index.html>"""
import re, sys

NEU = ("""  const BALL = '<svg class="ball" viewBox="0 0 24 24" aria-label="Tor"><defs><clipPath id="wsball"><circle cx="12" cy="12" r="10.6"/></clipPath></defs>"""
       """<circle cx="12" cy="12" r="11" fill="#fff"/><g clip-path="url(#wsball)"><path fill="#111827" d="M12 7.6L16.18 10.64 14.59 15.56H9.41L7.82 10.64Z"""
       """M12 5.5L8.1 2.67 9.59-1.92H14.41L15.9 2.67ZM18.18 9.99L19.67 5.41H24.49L25.98 9.99 22.08 12.82ZM15.82 17.26H20.64L22.13 21.84 18.23 24.68 14.33 21.84Z"""
       """M8.18 17.26L9.67 21.84 5.77 24.68 1.87 21.84 3.36 17.26ZM5.82 9.99L1.92 12.82-1.98 9.99-.49 5.41H4.33Z"/>"""
       """<path fill="none" stroke="#111827" stroke-width="1.5" stroke-linecap="round" d="M12 7.6V5.5M16.18 10.64L18.18 9.99M14.59 15.56L15.82 17.26M9.41 15.56L8.18 17.26"""
       """M7.82 10.64L5.82 9.99M15.9 2.67L19.67 5.41M22.08 12.82L20.64 17.26M14.33 21.84H9.67M3.36 17.26L1.92 12.82M4.33 5.41L8.1 2.67"/></g>"""
       """<circle cx="12" cy="12" r="11" fill="none" stroke="#111827" stroke-width="1.4"/></svg>';""")


def main(pfad):
    s = open(pfad, encoding="utf-8").read()
    alt = re.findall(r"^  const BALL = '.*?';$", s, re.M)
    if len(alt) != 1:
        sys.exit(f"BALL passt {len(alt)}-mal")
    s = s.replace(alt[0], NEU)
    open(pfad, "w", encoding="utf-8").write(s)
    print("ok", pfad)
    return alt[0]


if __name__ == "__main__":
    print(main(sys.argv[1]))
