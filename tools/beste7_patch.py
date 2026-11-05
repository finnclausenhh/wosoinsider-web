import sys
# Finn 05.11.2026 22:35: Start mit Alle, echte Spielzeit (auch Ausfälle), Torhüterinnen auch nach Haltequote
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    s = rep(s, '''    par: ["Paraden", x => {''', '''    hq: ["Haltequote", x => { const a = afSp(x.id) || {}, st = (x.spiele || []).filter(e => e.art === "S" && String(e.erg || "").includes(":")); if (!a.parsp || !st.length) return null;
      const ga = st.reduce((n, e) => { const [h, g] = String(e.erg).split(":").map(Number); return n + ((e.ha === "H" ? g : h) || 0); }, 0) / st.length, sv = a.par / a.parsp; return sv + ga ? sv / (sv + ga) : null; }],
    par: ["Paraden", x => {''')
    s = rep(s, '''TSET = {TW: ["par", "zn", "pass", "bk"],''', '''TSET = {TW: ["par", "hq", "zn", "pass", "bk"],''')
    s = rep(s, '''const l = (x.spiele || []).filter(e => e.erg && String(e.erg).includes(":") && e.art !== "X");''', '''const l = (x.spiele || []).filter(e => e.erg && String(e.erg).includes(":"));''')
    s = rep(s, '''let BESTE = "MF";''', '''let BESTE = "ALLE";''')
    s = rep(s, '''if (!pos.includes(BESTE)) BESTE =''', '''pos.unshift(pos.pop()); if (!pos.includes(BESTE)) BESTE =''')
    s = rep(s, '''dazu 20 % Spielzeit. Spielzeit zählt nur Spiele, in denen sie im Kader stand: Wer verletzt fehlt, verliert nichts, wer geschont wird, schon. Ab 270 Minuten.''',
               '''dazu 20 % Spielzeit, also der Anteil aller Ligaminuten ihres Teams. Ausfälle zählen mit, denn nur wer spielt, holt Punkte. Torhüterinnen zählen Paraden und Haltequote, damit eine Torhüterin mit wenig Arbeit nicht nur verliert. Ab 270 Minuten.''')
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
