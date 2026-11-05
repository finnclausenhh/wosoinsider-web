import sys
# Finn 05.11.2026 23:07: Duell-Balken mit Zahlen in der Legende, Erklärung unter Die Besten kürzer
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    a = '''<div class="dz-dk"><span>${esc(kname(v.h))} gewinnt</span><span>Remis</span><span>${esc(kname(v.g))} gewinnt</span></div></div>`; })() : ""}'''
    b = '''<div class="dz-dk"><span><i style="background:#4ADE80"></i>${esc(kname(v.h))} ${v.dus[0]}</span><span><i style="background:#A9B4C6"></i>Remis ${v.dus[1]}</span><span><i style="background:#FF8A8A"></i>${esc(kname(v.g))} ${v.dus[2]}</span></div></div>`; })() : ""}'''
    s = rep(s, a, b)
    s = rep(s, '''.dz-dk{display:flex;justify-content:space-between;font-size:11.5px;color:var(--muted)}''',
               '''.dz-dk{display:flex;justify-content:space-between;font-size:11.5px;color:var(--muted)}.dz-dk span{display:flex;align-items:center;gap:5px}.dz-dk i{width:9px;height:9px;border-radius:3px;display:inline-block}''')
    a = s[s.index('<p class="bst-erkl">So rechnen wir:'):]
    a = a[:a.index('</p>') + 4]
    s = rep(s, a, '''<p class="bst-erkl">40 % Statistik, 40 % Note, 20 % Spielzeit (Ausfälle zählen halb). Ab 270 Minuten.</p>''')
    s = rep(s, '''.bst-erkl{margin:10px 0 0;font-size:11.5px;''', '''.bst-erkl{margin:10px 0 0;font-size:10.5px;''')
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
