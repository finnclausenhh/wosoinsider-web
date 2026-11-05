# Nachbesserung Profil Runde 3: Netz zeigt die gezählten Werte pro 90, "wenig Spielzeit" nach Minuten, gleichauf als eigene Zeile, Elfmeter-Text bei Torhüterinnen
import sys
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    s = rep(s, """"Zweikämpfe", pc, "gewonnen", `${st.zk_w} von ${st.zk_ges} · ${Math.round(st.zk_w / st.zk_ges * 100)} %`]);""",
              """"Zweikämpfe", pc, "gewonnen", `${dez(st.zk_w / Math.max(1, M(s)) * 90, 1)} gewonnen pro 90`]);""")
    s = rep(s, """"Passquote", pc, "angekommen", `${st.p_ok} von ${st.p_ges} · ${Math.round(st.p_ok / st.p_ges * 100)} %`]);""",
              """"Pässe", pc, "angekommen", `${dez(st.p_ok / Math.max(1, M(s)) * 90, 0)} angekommen pro 90`]);""")
    s = rep(s, """"Dribblings", pc, "erfolgreich", `${af.drib[0]} von ${af.drib[1]} · ${Math.round(af.drib[0] / af.drib[1] * 100)} %`]);""",
              """"Dribblings", pc, "erfolgreich", `${dez(af.drib[0] / Math.max(1, M(s)) * 90, 1)} erfolgreich pro 90`]);""")
    i = s.index("        const NETZ = {"); j = s.index("}[GR];", i)
    s = s[:i] + s[i:j].replace('"Passquote"', '"Pässe"') + s[j:]
    # wenig Spielzeit nach eigenen Minuten
    s = rep(s, """    let w = f(s), wenig = 0; if (w == null) {""", """    let w = f(s), wenig = (s.spiele || []).reduce((a, e) => a + (e.min || 0), 0) < 270 ? 1 : 0; if (w == null) {""")
    # gleichauf als eigene Zeile in den Kacheln
    s = rep(s, """<span class="ps">${esc(rText(r))}${r.wenig ?""", """<span class="ps">${esc(rText(r).replace(/ \\(wie \\d+ andere\\)$/, ""))}${r.eq > 1 ? `<br><i class="wenig">gleichauf mit ${r.eq - 1} ${r.eq === 2 ? "anderen" : "anderen"}</i>` : ""}${r.wenig ?""")
    # Elfmeter Torhüterin: verständlicher Text, Rang ab 1 Elfmeter
    s = rep(s, """"Elfmeter gehalten", `${e[1]} von ${e[0]} nicht verwandelt · seit""", """"Elfmeter gehalten", `${e[0]} gegen sie, ${e[0] - e[1]} verwandelt · seit""")
    s = rep(s, """if (!e || e[0] < 4) return null; const v = Object.values(AF.elf_tw).filter(q => q[0] >= 4).map(q => q[2] || 0);""",
              """if (!e || e[0] < 1) return null; const v = Object.values(AF.elf_tw).filter(q => q[0] >= 1).map(q => q[2] || 0);""")
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
