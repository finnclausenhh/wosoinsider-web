"""Spielplan (Finn 07.11.2026): am Spieltag nur "AUFSTELLUNG AB CA. hh:mm", ohne VORSCHAU."""
import sys
p = sys.argv[1]; s = open(p, encoding="utf-8").read()
a = '''return `<div class="af-hin"><span class="v">VORSCHAU</span>${heute ? `<span class="a">AUFSTELLUNG AB CA. ${uhr(new Date(d.getTime() - 3600000))}</span>` : ""}</div>`;'''
b = '''return `<div class="af-hin">${heute ? `<span class="a">AUFSTELLUNG AB CA. ${uhr(new Date(d.getTime() - 3600000))}</span>` : '<span class="v">VORSCHAU</span>'}</div>`;'''
assert s.count(a) == 1; s = s.replace(a, b); open(p, "w", encoding="utf-8").write(s); print("ok", p)
