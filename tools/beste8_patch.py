import sys
# Finn 05.11.2026 22:41: Torhüterinnen nach Kickbase-Punkten (Parade 15, Weiße Weste 50), Ausfälle zählen halb
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    s = rep(s, '''    hq: ["Haltequote",''', '''    kb: ["Paraden und Weißen Westen", x => { const a = afSp(x.id) || {}, st = (x.spiele || []).filter(e => e.art === "S" && String(e.erg || "").includes(":")); if (!a.parsp || !st.length) return null;
      const zn = st.filter(e => { const [h, g] = String(e.erg).split(":").map(Number); return (e.ha === "H" ? g : h) === 0; }).length / st.length; return a.par / a.parsp * 15 + zn * 50; }],
    hq: ["Haltequote",''')
    s = rep(s, '''TSET = {TW: ["par", "hq", "zn", "pass", "bk"],''', '''TSET = {TW: ["kb", "hq", "pass", "bk"],''')
    s = rep(s, '''const keys = TSET[g].concat(g === "IV" || g === "ST" ? ["gr"] : []), V = {}, NR = {};''', '''const keys = TSET[g].concat(g === "IV" || g === "ST" ? ["gr"] : [], g === "TW" ? ["par", "zn"] : []), V = {}, NR = {};''')
    s = rep(s, '''const stat = ks.reduce((a, k) => a + p[k], 0) / ks.length, pn = NR[x.id];''', '''const wt = k => g === "TW" && k === "kb" ? 2 : 1, stat = ks.reduce((a, k) => a + p[k] * wt(k), 0) / ks.reduce((a, k) => a + wt(k), 0), pn = NR[x.id];''')
    s = rep(s, '''const EIN = x => { const l = (x.spiele || []).filter(e => e.erg && String(e.erg).includes(":")); return l.length ? Math.round(TMIN(x) / (l.length * 90) * 100) : null; };''',
               '''const EIN = x => { const l = (x.spiele || []).filter(e => e.erg && String(e.erg).includes(":")), n = l.length - .5 * l.filter(e => e.art === "X").length; return n > 0 ? Math.min(100, Math.round(TMIN(x) / (n * 90) * 100)) : null; };''')
    s = rep(s, '''dazu 20 % Spielzeit, also der Anteil aller Ligaminuten ihres Teams. Ausfälle zählen mit, denn nur wer spielt, holt Punkte. Torhüterinnen zählen Paraden und Haltequote, damit eine Torhüterin mit wenig Arbeit nicht nur verliert. Ab 270 Minuten.''',
               '''dazu 20 % Spielzeit. Spiele, in denen sie nicht im Kader stand (Verletzung, Sperre, Rotation), zählen halb. Torhüterinnen zählen vor allem Kickbase-Punkte aus Paraden (15) und Weißer Weste (50), dazu Haltequote, Pässe und Ballkontakte. Ab 270 Minuten.''')
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
