import sys
# Finn 05.11.2026 22:49: oben zwei Sätze, Details unten
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    s = rep(s, '''<div class="stk-k"><h2>Die Besten</h2></div>''', '''<div class="stk-k"><h2>Die Besten</h2><small>Gesamtwert aus Statistik, Note und Spielzeit, jeweils im Vergleich mit der eigenen Rolle. 100 heißt überall vorne.</small></div>''')
    s = rep(s, '''<p class="bst-erkl">Gesamtwert: 40 % Statistik''', '''<p class="bst-erkl">So rechnen wir: 40 % Statistik''')
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
