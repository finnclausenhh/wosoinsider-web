import sys
# Finn 05.11.2026 22:45: keine Kickbase-Punkte nur für Torhüterinnen (nichts Halbes und nichts Ganzes). TW wieder Paraden, Haltequote, zu null, Pässe, Ballkontakte. Ausfälle bleiben halb.
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    s = rep(s, '''TSET = {TW: ["kb", "hq", "pass", "bk"],''', '''TSET = {TW: ["par", "hq", "zn", "pass", "bk"],''')
    s = rep(s, '''const keys = TSET[g].concat(g === "IV" || g === "ST" ? ["gr"] : [], g === "TW" ? ["par", "zn"] : []), V = {}, NR = {};''', '''const keys = TSET[g].concat(g === "IV" || g === "ST" ? ["gr"] : []), V = {}, NR = {};''')
    s = rep(s, '''const wt = k => g === "TW" && k === "kb" ? 2 : 1, stat =''', '''const wt = k => 1, stat =''')
    s = rep(s, '''Torhüterinnen zählen vor allem Kickbase-Punkte aus Paraden (15) und Weißer Weste (50), dazu Haltequote, Pässe und Ballkontakte. Ab 270 Minuten.''',
               '''Torhüterinnen zählen Paraden und Haltequote, damit eine Torhüterin mit wenig Arbeit nicht nur verliert. Ab 270 Minuten.''')
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
