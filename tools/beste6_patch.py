import sys
# Finn 05.11.2026 22:27: Erklärung unter Platz 10, Reiter Alle nach Sturm
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    s = rep(s, '''pos = Object.keys(BTAB).filter(t => Object.values(T).some(x => tabVon(x.g) === t)); if (!pos.length) return "";''',
               '''pos = Object.keys(BTAB).filter(t => Object.values(T).some(x => tabVon(x.g) === t)); if (!pos.length) return ""; pos.push("ALLE");''')
    s = rep(s, '''const L = Object.entries(T).filter(([, x]) => tabVon(x.g) === BESTE).sort(''', '''const L = Object.entries(T).filter(([, x]) => BESTE === "ALLE" || tabVon(x.g) === BESTE).sort(''')
    a = '''<div class="stk-k"><h2>Die Besten</h2><small>Gesamtwert: 40 % Statistik pro 90 Minuten und 40 % Note von API-Football, jeweils im Vergleich mit der eigenen Rolle, dazu 20 % Spielzeit. Spielzeit zählt nur Spiele, in denen sie im Kader stand: Wer verletzt fehlt, verliert nichts, wer geschont wird, schon. Ab 270 Minuten.</small></div>'''
    s = rep(s, a, '''<div class="stk-k"><h2>Die Besten</h2></div>''')
    s = rep(s, '''BTAB[f][0] === "Torhüterinnen" ? "Tor" : BTAB[f][0]}</button>`).join("")}</div>''', '''f === "ALLE" ? "Alle" : BTAB[f][0] === "Torhüterinnen" ? "Tor" : BTAB[f][0]}</button>`).join("")}</div>''')
    s = rep(s, '''${x.ein} % Spielzeit</i>` : ""}</span></button>`; }).join("")}</section>`;''',
               '''${x.ein} % Spielzeit</i>` : ""}</span></button>`; }).join("")}<p class="bst-erkl">Gesamtwert: 40 % Statistik pro 90 Minuten und 40 % Note von API-Football, jeweils im Vergleich mit der eigenen Rolle, dazu 20 % Spielzeit. Spielzeit zählt nur Spiele, in denen sie im Kader stand: Wer verletzt fehlt, verliert nichts, wer geschont wird, schon. Ab 270 Minuten.${BESTE === "ALLE" ? " Unter Alle stehen alle Positionen zusammen, jede mit ihrem Wert aus der eigenen Rolle." : ""}</p></section>`;''')
    s = rep(s, '''.bst .bein{''', '''.bst-erkl{margin:10px 0 0;font-size:11.5px;line-height:1.45;color:var(--muted)}.bst .bein{''')
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
