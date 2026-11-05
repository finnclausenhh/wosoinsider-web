# News Runde 2 (Finn 05.11.2026 abends): "Für Kickbase" und Einordnung in einer Box, "Wer spielt für sie" als Fließtext,
# Verlauf bei Belastungssteuerung/Schonung (fehlt im nächsten Spiel, Training ab Montag, Kader im Spiel danach)
import sys
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    s = rep(s, """<div id="art-sv">${auf || sc ? "" : artVerlauf(m)}</div>${kbBox(m.kickbase)}<div id="art-eo">${auf || sc ? "" : einordnung(m)}</div>""",
              """<div id="art-sv">${auf || sc ? "" : artVerlauf(m)}</div><div id="art-eo">${(auf || sc ? "" : einordnung(m)) || kbBox(m.kickbase)}</div>""")
    s = rep(s, """const eo = $("#art-eo"); if (eo && ARTIKEL === id) eo.innerHTML = einordnung(m);""", """const eo = $("#art-eo"); if (eo && ARTIKEL === id) eo.innerHTML = einordnung(m) || kbBox(m.kickbase);""")
    s = rep(s, """    if (z.length < 2) return "";
    return `<section class="eo">${kap("Unsere Einordnung für Kickbase")}${z.map(""", """    if (z.length < 2) return "";
    return `<section class="eo">${kap("Für Kickbase")}${m.kickbase ? `<p class="eo-kb">${esc(m.kickbase)}</p>` : ""}${z.map(""")
    s = rep(s, """      if (kon.length) z.push(["Wer spielt für sie?", kon.map(x => { const r = (s.ersatz || []).find(e => normS(nachN(e.n)) === normS(nachN(x.n)));
        return `Chance für ${btn(x)}${r && r.s ? `, stand schon ${r.s}x für sie in der Startelf` : ""}${pst(x) && STUFE[pst(x)] ? `, Prognose: ${STUFE[pst(x)][2]}` : ""}.`; }).join(" "), 1]);""",
"""      if (kon.length) z.push(["Wer spielt für sie?", kon.map((x, i) => { const r = (s.ersatz || []).find(e => normS(nachN(e.n)) === normS(nachN(x.n))), pr = pst(x) && STUFE[pst(x)] ? STUFE[pst(x)][2].toLowerCase() : "";
        return i === 0 ? `Wir rechnen mit ${btn(x)}${r && r.s ? `, sie stand schon ${r.s === 1 ? "einmal" : r.s + "-mal"} für ${esc(nachN(s.n))} in der Startelf` : ""}${pr ? `. Unsere Prognose für sie: ${pr}` : ""}.`
          : `Auch ${btn(x)} ist möglich${pr ? `, Prognose ${pr}` : ""}.`; }).join(" "), 1]);""")
    s = rep(s, """.eo-z{display:grid;gap:2px}""", """.eo-kb{margin:0;font-size:14.5px;line-height:1.5}
.eo-z{display:grid;gap:2px}""")
    # Belastungssteuerung: eigener Verlauf
    s = rep(s, """  function verletzungEinsch(s){
    const st = s.status || {}; if (st.s !== "raus" || !st.grund) return null;""", """  function belastungEinsch(s){
    const st = s.status || {}; if (st.s !== "raus" || !/belastung|schonung|geschont|pause/i.test(st.grund || "") || !SP) return null;
    const seit = st.stand; if (!seit) return null;
    const ps = alleSpiele().filter(p => (p.heim_k === s.k || p.gast_k === s.k) && p.status !== "abgesagt" && terminiert(p) && String(p.anstoss).slice(0, 10) >= seit).sort((a, b) => dt(a.anstoss) - dt(b.anstoss));
    if (ps.length < 2) return null;
    const g = p => kname(p.heim_k === s.k ? p.gast_k : p.heim_k), d1 = dt(ps[0].anstoss), mo = new Date(d1); mo.setDate(mo.getDate() + ((8 - mo.getDay()) % 7 || 7));
    const iso = d => `${d.getFullYear()}-${p2(d.getMonth() + 1)}-${p2(d.getDate())}`, kd = d => `${d.getDate()}.${d.getMonth() + 1}.`, d0 = new Date(seit + "T12:00");
    return {seit: iso(d1), stand: st.stand, satz: `Keine Verletzung gemeldet: ${kname(s.k)} schont sie gegen ${g(ps[0])}. Wir erwarten sie ab Montag wieder im Training und gegen ${g(ps[1])} zurück im Kader.`,
      phasen: [{d: kd(d1), iso: iso(d1), t: "fehlt gegen " + g(ps[0]), typ: "verletzung"},
        {d: kd(mo), iso: iso(mo), t: "Training", typ: "reha", prog: true}, {d: kd(dt(ps[1].anstoss)), iso: iso(dt(ps[1].anstoss)), t: "Kader gegen " + g(ps[1]), typ: "kader", prog: true}],
      vergleich: "Eigene Einschätzung nach dem Spielplan, keine Meldung des Vereins zur Rückkehr."};
  }
  function verletzungEinsch(s){
    const st = s.status || {}; if (st.s !== "raus" || !st.grund) return null;
    { const b = belastungEinsch(s); if (b) return b; }""")
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
