"""Finn 07.11.2026 16:38: Prognose-Ring nur ab 90 % erwarteter Trefferquote, dann mit der PROGNOSE-Plakette im selben Kasten
(Kopfzeile mit Plakette entfällt). Darunter kein Ring, Plakette wie bisher. Aufruf: python3 tools/ring90_patch.py <ein> <aus>"""
import sys
R = [
 ('''    const C = 2 * Math.PI * 27;
    return `<div class="pr-ring">''', '''    if (pz < 90) return "";
    const C = 2 * Math.PI * 27;
    return `<div class="pr-ring">'''),
 ('''<div class="t"><b>So sicher sind wir</b><span>''', '''<div class="t"><span class="t1"><b>So sicher sind wir</b><span class="badge ein">PROGNOSE</span></span><span>'''),
 ('''    return `<div class="kartebox"><div class="tb-k"><button class="kd-btn" data-kader="${esc(k)}" aria-label="Kader ${esc(name)}">${logo(k, 22)}<span class="n">${esc(name)}</span></button>${badge}</div>${progRing(a)}${inh}''',
  '''    const rg = progRing(a);
    return `<div class="kartebox">${rg ? "" : `<div class="tb-k"><button class="kd-btn" data-kader="${esc(k)}" aria-label="Kader ${esc(name)}">${logo(k, 22)}<span class="n">${esc(name)}</span></button>${badge}</div>`}${rg}${inh}'''),
]
CSS = ".pr-ring .t1{display:flex;justify-content:space-between;align-items:center;gap:8px}.pr-ring .t1 .badge{flex:none}\n"
s = open(sys.argv[1], encoding="utf-8").read()
for a, b in R:
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)
i = s.rindex("</style>"); s = s[:i] + CSS + s[i:]
open(sys.argv[2], "w", encoding="utf-8").write(s); print("ok")
