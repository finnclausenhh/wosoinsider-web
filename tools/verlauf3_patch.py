# Verlauf: Belastungssteuerung bei Stammspielerin endet mit "Startelf gegen ..."; unbekannte Verletzung (z. B. Knieprobleme) zeigt trotzdem einen Verlauf mit "Rückkehr offen" (Finn 05.11.2026)
import sys
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    s = rep(s, """    return {seit, stand: st.stand, satz: `Keine Verletzung gemeldet: ${kname(s.k)} schont sie gegen ${g(ps[0])}. Wir erwarten sie ab Montag wieder im Training und gegen ${g(ps[1])} zurück im Kader.`,""",
"""    const stamm = (s.spiele || []).slice(-5).filter(e => e.art === "S").length >= 4;
    return {seit, stand: st.stand, satz: `Keine Verletzung gemeldet: ${kname(s.k)} schont sie gegen ${g(ps[0])}. Wir erwarten sie ab Montag wieder im Training und gegen ${g(ps[1])} zurück ${stamm ? "in der Startelf" : "im Kader"}.`,""")
    s = rep(s, """        {d: kd(mo), iso: iso(mo), t: "Training", typ: "reha", prog: true}, {d: kd(dt(ps[1].anstoss)), iso: iso(dt(ps[1].anstoss)), t: "Kader gegen " + g(ps[1]), typ: "kader", prog: true}],""",
"""        {d: kd(mo), iso: iso(mo), t: "Training", typ: "reha", prog: true}, {d: kd(dt(ps[1].anstoss)), iso: iso(dt(ps[1].anstoss)), t: (stamm ? "Startelf gegen " : "Kader gegen ") + g(ps[1]), typ: stamm ? "startelf" : "kader", prog: true}],""")
    s = rep(s, """    const t = VERL_TYP.find(x => x[0].test(st.grund)); if (!t) return null;""", """    const t = VERL_TYP.find(x => x[0].test(st.grund)); if (!t) return offenEinsch(s);""")
    s = rep(s, """  function verletzungEinsch(s){""", """  function offenEinsch(s){
    const st = s.status || {}, seit = st.stand; if (!seit || !SP) return null;
    const ps = alleSpiele().filter(p => (p.heim_k === s.k || p.gast_k === s.k) && p.status !== "abgesagt" && terminiert(p) && String(p.anstoss).slice(0, 10) >= seit).sort((a, b) => dt(a.anstoss) - dt(b.anstoss));
    if (!ps.length) return null;
    const g = p => kname(p.heim_k === s.k ? p.gast_k : p.heim_k), iso = d => `${d.getFullYear()}-${p2(d.getMonth() + 1)}-${p2(d.getDate())}`, kd = d => `${d.getDate()}.${d.getMonth() + 1}.`;
    const d0 = new Date(seit + "T12:00"), d1 = dt(ps[0].anstoss), d2 = ps[1] ? dt(ps[1].anstoss) : new Date(d1.getTime() + 7 * 864e5);
    return {seit, stand: st.stand, satz: `Der Verein nennt keinen Rückkehrtermin. Gegen ${g(ps[0])} fehlt sie, danach entscheidet sich die Rückkehr von Woche zu Woche. Wir melden, sobald sie wieder trainiert.`,
      phasen: (d1 - d0 < 3 * 864e5 ? [] : [{d: kd(d0), iso: seit, t: String(st.grund || "Ausfall").split(",")[0], typ: "verletzung"}]).concat([{d: kd(d1), iso: iso(d1), t: "fehlt gegen " + g(ps[0]), typ: "verletzung"},
        {d: kd(d2), iso: iso(d2), t: "Rückkehr offen" + (ps[1] ? ", frühestens gegen " + g(ps[1]) : ""), typ: "kader", prog: true}]),
      vergleich: "Ohne Diagnose und Termin gibt es keinen typischen Verlauf. Die Punkte nach heute sind nur der Spielplan."};
  }
  function verletzungEinsch(s){""")
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
