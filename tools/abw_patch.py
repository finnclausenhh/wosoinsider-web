# Abwehrarbeit in "Weitere Werte" für Abwehr und Mittelfeld (Finn 05.11.2026): Tacklings, abgefangene Bälle und Blocks pro 90 Minuten (API-Football)
import sys
def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    a = """      if (st.p_ges) ww.push([`${st.p_ok}/${st.p_ges}`, "Pässe angekommen","""
    s = rep(s, a, """      if (af.abw && af.abw[3] >= 90 && (s.pos === "ABW" || s.pos === "MF")) { const [tk, ic, bl, mn] = af.abw, sum = tk + ic + bl, w = sum / mn * 90;
        ww.push([sum, "Abwehraktionen", `${dez(w, 1)} pro 90 · ${tk} ${tk === 1 ? "Tackling" : "Tacklings"} · ${ic} abgefangen${bl ? ` · ${bl} ${bl === 1 ? "Block" : "Blocks"}` : ""}`, ligaRang(s, x => { const q = (afSp(x.id) || {}).abw; return q && q[3] >= 270 ? (q[0] + q[1] + q[2]) / q[3] * 90 : null; }), "Abwehrarbeit", d1, "pro 90 Min.", dez(w, 1) + " pro 90 Min."]); }
""" + a)
    s = rep(s, "Schlüsselpässe, Dribblings und Paraden: API-Football", "Schlüsselpässe, Dribblings, Abwehrarbeit und Paraden: API-Football")
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
