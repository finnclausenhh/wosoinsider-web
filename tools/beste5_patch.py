import sys
# Finn 05.11.2026 22:05: Schonung in englischen Wochen ist oft nicht vorher sichtbar. Spielzeit zählt mit 20 %, aber nur Spiele im Kader (Verletzung und Sperre bestrafen nicht)
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    s = rep(s, '''const l = (x.spiele || []).filter(e => e.erg && String(e.erg).includes(":"));''', '''const l = (x.spiele || []).filter(e => e.erg && String(e.erg).includes(":") && e.art !== "X");''')
    s = rep(s, '''wert: Math.round(pn != null ? (stat + pn) / 2 : stat), ein: EIN(x)''', '''wert: Math.round((pn != null ? (stat + pn) / 2 : stat) * (EIN(x) != null ? .8 : 1) + (EIN(x) != null ? Math.min(100, EIN(x)) * .2 : 0)), ein: EIN(x)''')
    s = rep(s, '''<small>Gesamtwert: halb Statistik pro 90 Minuten, halb Note von API-Football, jeweils im Vergleich mit der eigenen Rolle. 100 heißt überall vorne. Ab 270 Minuten. Rechts unten: Anteil der gespielten Ligaminuten.</small>''',
               '''<small>Gesamtwert: 40 % Statistik pro 90 Minuten und 40 % Note von API-Football, jeweils im Vergleich mit der eigenen Rolle, dazu 20 % Spielzeit. Spielzeit zählt nur Spiele, in denen sie im Kader stand: Wer verletzt fehlt, verliert nichts, wer geschont wird, schon. Ab 270 Minuten.</small>''')
    s = rep(s, '''${x.ein} % Einsatz</i>''', '''${x.ein} % Spielzeit</i>''')
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
