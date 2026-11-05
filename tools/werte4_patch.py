# Weitere Werte Runde 4 (Finn 05.11.2026 20:34): "mehr als / weniger als" statt "besser / schlechter als" (gezählt wird Anzahl, wenig Schüsse aufs Tor heißt nicht schlecht gehalten);
# Torhüterinnen mit 6 Werten im Netz: Paraden, Zu null, Gegentore (weniger = besser), Pässe, Ballkontakte, Elfmeter gehalten
import sys
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    s = rep(s, """        if (r.platz === 1) return (r.fair ? "die wenigsten Fouls" : "Bestwert") + mit;
        if (r.w <= r.min + 1e-9) return (r.fair ? "die meisten Fouls" : "niedrigster Wert") + mit;
        if (r.fair) return r.p >= 50 ? "foult seltener als " + r.p + " %" : "foult häufiger als " + (100 - r.p) + " %";
        return r.p >= 50 ? "besser als " + r.p + " %" : "schlechter als " + (100 - r.p) + " %"; };""",
"""        if (r.gegen) return r.platz === 1 ? "die wenigsten Gegentore" + mit : r.w <= r.min + 1e-9 ? "die meisten Gegentore" + mit : r.p >= 50 ? "weniger Gegentore als " + r.p + " %" : "mehr Gegentore als " + (100 - r.p) + " %";
        if (r.platz === 1) return (r.fair ? "die wenigsten Fouls" : "Bestwert") + mit;
        if (r.w <= r.min + 1e-9) return (r.fair ? "die meisten Fouls" : "niedrigster Wert") + mit;
        if (r.fair) return r.p >= 50 ? "foult seltener als " + r.p + " %" : "foult häufiger als " + (100 - r.p) + " %";
        return r.p >= 50 ? "mehr als " + r.p + " %" : "weniger als " + (100 - r.p) + " %"; };""")
    s = rep(s, """r.p >= 50 ? "besser als " + r.p + " % der " + P : "schlechter als " + (100 - r.p) + " % der " + P;""", """r.p >= 50 ? "mehr als " + r.p + " % der " + P : "weniger als " + (100 - r.p) + " % der " + P;""")
    s = rep(s, """r.p >= 50 ? "besser als " + r.p + " %" : "schlechter als " + (100 - r.p) + " %";
        const kacheln""", """r.p >= 50 ? "mehr als " + r.p + " %" : "weniger als " + (100 - r.p) + " %";
        const kacheln""")
    # Gegentore pro Spiel für Torhüterinnen (weniger = besser)
    s = rep(s, """          ww.push([ZN(s), "Spiele zu null", `${gt} Gegentore in ${st11.length} Spielen`, LR(s, x => M(x) >= ab(270) ? ZN(x) : null), "Zu null", v => String(v), "Spiele", `${ZN(s)} von ${st11.length}`]); } }""",
"""          ww.push([ZN(s), "Spiele zu null", `${gt} Gegentore in ${st11.length} Spielen`, LR(s, x => M(x) >= ab(270) ? ZN(x) : null), "Zu null", v => String(v), "Spiele", `${ZN(s)} von ${st11.length}`]);
          const GA = x => { const l = (x.spiele || []).filter(e => e.art === "S"), g = l.reduce((a, e) => a + (GG(e) || 0), 0); return l.length ? g / l.length : null; };
          const rg = LR(s, x => M(x) >= ab(270) ? -GA(x) : null);
          ww.push([dez(gt / st11.length, 1), "Gegentore pro Spiel", `${gt} in ${st11.length} Spielen`, rg ? Object.assign({}, rg, {gegen: 1}) : null, "Gegentore", d1, "pro Spiel", dez(gt / st11.length, 1) + " pro Spiel"]); } }""")
    # Elfmeter gehalten ins Netz
    s = rep(s, """if (e && e[0]) ww.push([`${e[2] || 0}/${e[0]}`, "Elfmeter gehalten", `${e[0]} gegen sie, ${e[0] - e[1]} verwandelt · seit ${(li.saisons || [""])[0]}${lq != null ? ` · Liga trifft ${lq} %` : ""}`, er]); }""",
"""if (e && e[0]) ww.push([`${e[2] || 0}/${e[0]}`, "Elfmeter gehalten", `${e[0]} gegen sie, ${e[0] - e[1]} verwandelt${lq != null ? ` · Liga ${lq} %` : ""}`, er, "Elfmeter", v => String(v), "gehalten", `${e[2] || 0} von ${e[0]} gehalten`]); }""")
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
