# Netz: absolute Zahl vorne, pro 90 dahinter (Finn 05.11.2026: "oben steht 3 und unten 4/7")
import sys
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    s = rep(s, '`${dez(st.zk_w / Math.max(1, M(s)) * 90, 1)} gewonnen pro 90`', '`${st.zk_w} gewonnen · ${dez(st.zk_w / Math.max(1, M(s)) * 90, 1)}/90`')
    s = rep(s, '`${dez(st.p_ok / Math.max(1, M(s)) * 90, 0)} angekommen pro 90`', '`${st.p_ok} angekommen · ${dez(st.p_ok / Math.max(1, M(s)) * 90, 0)}/90`')
    s = rep(s, '`${dez(af.drib[0] / Math.max(1, M(s)) * 90, 1)} erfolgreich pro 90`', '`${af.drib[0]} erfolgreich · ${dez(af.drib[0] / Math.max(1, M(s)) * 90, 1)}/90`')
    s = rep(s, 'dez(w, 1) + " pro 90 Min."]); }', 'sum + " · " + dez(w, 1) + "/90"]); }')
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
