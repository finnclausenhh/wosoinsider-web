# Spielertyp: Menge und Quote getrennt, Torhüterinnen fair bewertet (Finn 11.11.2026)
#  - Torhüterinnen: Paraden und Ballkontakte zählen nicht mehr in den Gesamtwert (wer fast nichts aufs Tor bekommt, hat wenige Paraden
#    und wenige Ballkontakte), dafür Haltequote, Spiele zu null und Passquote. Paraden, Pässe, Ballkontakte bleiben als Information.
#  - Spielertyp-Zeile: kein doppeltes "zu null" mehr beim sicheren Rückhalt, Quoten mit Prozentwert (Haltequote, Passquote, Zweikampfquote).
#  - "Wenige Paraden, aber sehr gute Haltequote", "wenige Zweikämpfe, aber mit hoher Quote" (oder schwacher Quote) als eigener Satz.
# Aufruf: python3 tools/tw_quote_patch.py ticker/index.html   (derselbe Patch gilt für index.html im Artifact)
import sys


def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90])
    return s.replace(a, b)


EDITS = [
    # 1) neue Kennzahlen: Passquote, Zweikampfquote, Zweikampfhäufigkeit
    ("""    bk: ["Ballkontakten", x => (x.stat || {}).bk && TMIN(x) ? x.stat.bk / TMIN(x) * 90 : null],
""", """    bk: ["Ballkontakten", x => (x.stat || {}).bk && TMIN(x) ? x.stat.bk / TMIN(x) * 90 : null],
    pq: ["Passquote", x => (x.stat || {}).p_ges >= 20 ? x.stat.p_ok / x.stat.p_ges * 100 : null],
    zkq: ["Zweikampfquote", x => (x.stat || {}).zk_ges >= 10 ? x.stat.zk_w / x.stat.zk_ges * 100 : null],
    zkv: ["Zweikämpfen", x => (x.stat || {}).zk_ges != null && TMIN(x) ? x.stat.zk_ges / TMIN(x) * 90 : null],
"""),
    # 2) Gesamtwert der Torhüterinnen ohne Paraden und Ballkontakte
    ("""const TSET = {TW: ["par", "hq", "zn", "pass", "bk"],""", """const TSET = {TW: ["hq", "zn", "pq"],"""),
    ("""  let TCACHE = null;
""", """  // nur zur Einordnung, nicht im Gesamtwert: Menge (Paraden, Pässe, Ballkontakte, Zweikämpfe) hängt vom Spiel der Mannschaft ab
  const TINFO = {TW: ["par", "pass", "bk"], IV: ["pq", "zkq", "zkv"], AV: ["pq", "zkq", "zkv"], DM: ["pq", "zkq", "zkv"], ZM: ["pq", "zkq", "zkv"], FL: ["pq", "zkq", "zkv"], ST: ["pq", "zkq", "zkv"]};
  let TCACHE = null;
"""),
    ("""const keys = TSET[g].concat(g === "IV" || g === "ST" ? ["gr"] : []), V = {}, NR = {};""",
     """const keys = TSET[g].concat(TINFO[g] || [], g === "IV" || g === "ST" ? ["gr"] : []), V = {}, NR = {};"""),
    # 3) Typ der Torhüterin
    ("""    if (g === "TW") { const par = m("par"), auf = m("pass", "bk"), zn = m("zn"); return zn >= 65 && zn >= par ? ["sicherer Rückhalt", "viele Spiele zu null"] : auf >= par && auf >= 55 ? ["mitspielende Torhüterin", "viel am Ball, spielt mit"] : ["Paraden-Torhüterin", "hat viel zu halten und hält viel"]; }""",
     """    if (g === "TW") { const par = m("par"), auf = m("pass", "bk", "pq"), zn = m("zn"), hq = m("hq");
      return (zn >= 65 || hq >= 70) && Math.max(zn, hq) >= par ? ["sicherer Rückhalt", "viele Spiele zu null"] : auf >= par && auf >= 55 ? ["mitspielende Torhüterin", "viel am Ball, spielt mit"]
        : par >= 55 ? ["Paraden-Torhüterin", "hat viel zu halten und hält viel"] : ["solide Torhüterin", "ohne klaren Schwerpunkt"]; }"""),
    ("""  const TYPERKL = {"sicherer Rückhalt": "Bleibt oft ohne Gegentor: viele Spiele zu null im Vergleich zu den anderen Torhüterinnen.",
    "mitspielende Torhüterin": "Viele Ballkontakte und angekommene Pässe, spielt mit wie eine Feldspielerin.",
    "Paraden-Torhüterin": "Bekommt viele Schüsse aufs Tor und hält viele. Bei Kickbase bringt jede Parade Punkte.",""",
     """  const TYPERKL = {"sicherer Rückhalt": "Bleibt oft ohne Gegentor und hält einen hohen Anteil der Schüsse aufs Tor (Haltequote). Wenige Paraden sind kein Makel, wenn die Abwehr wenig zulässt.",
    "mitspielende Torhüterin": "Viele Ballkontakte und angekommene Pässe, spielt mit wie eine Feldspielerin.",
    "Paraden-Torhüterin": "Bekommt viele Schüsse aufs Tor und hält viele. Bei Kickbase bringt jede Parade Punkte.",
    "solide Torhüterin": "Ohne klaren Ausschlag in den Werten: weder auffallend viele Paraden noch Spiele zu null.","""),
    # 4) Spielertyp-Zeile: Prozentwerte, keine Doppelung, Menge gegen Quote
    ("""  function typZeile(s){""", """  // Menge und Quote getrennt (Finn 11.11.2026): "wenige Zweikämpfe, aber mit hoher Quote", "wenige Paraden, aber sehr gute Haltequote"
  const PCT = (k, s) => { const v = TMET[k][1](s); return v == null ? "" : Math.round(k === "hq" ? v * 100 : v) + " %"; };
  const MIT = (k, s) => TMET[k][0] + (["hq", "pq", "zkq"].includes(k) && PCT(k, s) ? ` (${PCT(k, s)})` : "");
  function quoten(d, s){
    const p = d.p, o = {saetze: [], skip: []};
    if (d.g === "TW") {
      if (p.par != null && p.hq != null) {
        if (p.par < 40 && p.hq >= 65) { o.saetze.push(`Wenige Paraden, aber eine sehr gute Haltequote (${PCT("hq", s)}).`); o.skip.push("hq"); }
        else if (p.par >= 65 && p.hq < 35) { o.saetze.push(`Viele Paraden, aber eine schwache Haltequote (${PCT("hq", s)}).`); o.skip.push("hq"); }
      }
      return o;
    }
    if (p.zkv != null && p.zkq != null) {
      const q = PCT("zkq", s);
      if (p.zkv < 35) o.saetze.push(p.zkq >= 60 ? `Wenige Zweikämpfe, aber mit hoher Quote (${q} gewonnen).` : p.zkq < 35 ? `Wenige Zweikämpfe und mit schwacher Quote (${q} gewonnen).`
        : `Wenige Zweikämpfe, die Quote liegt im Schnitt (${q} gewonnen).`);
      else if (p.zkv >= 65) o.saetze.push(p.zkq >= 60 ? `Viele Zweikämpfe mit hoher Quote (${q} gewonnen).` : p.zkq < 35 ? `Viele Zweikämpfe, aber mit schwacher Quote (${q} gewonnen).`
        : `Viele Zweikämpfe, die Quote liegt im Schnitt (${q} gewonnen).`);
      if (o.saetze.length) o.skip.push("zk");
    }
    return o;
  }
  function typZeile(s){"""),
    ("""    const st = TSET[d.g].filter(k => d.p[k] != null).sort((a, b) => d.p[b] - d.p[a]), gut = st.filter(k => d.p[k] >= 60).slice(0, 2), sw = st.filter(k => d.p[k] < 35).slice(-1);""",
     """    const ex = quoten(d, s), ok = k => !ex.skip.includes(k) && !(d.typ[0] === "sicherer Rückhalt" && k === "zn");
    const st = TSET[d.g].filter(k => d.p[k] != null).sort((a, b) => d.p[b] - d.p[a]), gut = st.filter(k => d.p[k] >= 60 && ok(k)).slice(0, 2), sw = st.filter(k => d.p[k] < 35 && ok(k)).slice(-1);"""),
    ("""<span>${esc(d.typ[1])}${gut.length ? `. Stark in ${gut.map(k => TMET[k][0]).join(" und ")}` : ""}${sw.length ? `, weniger in ${TMET[sw[0]][0]}` : ""}.</span>""",
     """<span>${esc(d.typ[1])}${gut.length ? `. Stark in ${gut.map(k => MIT(k, s)).join(" und ")}` : ""}${sw.length ? `, weniger in ${MIT(sw[0], s)}` : ""}.${ex.saetze.length ? " " + esc(ex.saetze.join(" ")) : ""}</span>"""),
    # 5) Beugung und Kurzform für "solide Torhüterin"
    ("""    "mitspielende Torhüterin": ["eine mitspielende Torhüterin", "einer mitspielenden Torhüterin"], "sicherer Rückhalt": ["ein sicherer Rückhalt", "einem sicheren Rückhalt"],""",
     """    "mitspielende Torhüterin": ["eine mitspielende Torhüterin", "einer mitspielenden Torhüterin"], "solide Torhüterin": ["eine solide Torhüterin", "einer soliden Torhüterin"], "sicherer Rückhalt": ["ein sicherer Rückhalt", "einem sicheren Rückhalt"],"""),
    ("""    "arbeitet nach hinten mit": "defensiv stark", "mitspielende Torhüterin": "mitspielend",""",
     """    "arbeitet nach hinten mit": "defensiv stark", "mitspielende Torhüterin": "mitspielend", "solide Torhüterin": "solide","""),
]


def patch(s):
    for a, b in EDITS:
        s = rep(s, a, b)
    return s


if __name__ == "__main__":
    p = sys.argv[1]
    s = open(p, encoding="utf-8").read()
    open(p, "w", encoding="utf-8").write(patch(s))
    print("ok", p)
