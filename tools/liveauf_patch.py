"""Spielansicht (Finn 07.11.2026, Leverkusen-HSV): offizielle Aufstellung aus den Live-Meldungen (news.json) übernehmen,
solange spielplan.json noch die Prognose hat. spielplan.json bekommt die offizielle Fassung erst mit dem nächsten Lauf."""
import sys
p = sys.argv[1]; s = open(p, encoding="utf-8").read()
R = [
 ('  let N = [], SP = null, IN = null, FOTOS = {}, PATCH = null;\n',
  '''  let N = [], SP = null, IN = null, FOTOS = {}, PATCH = null;
  function liveAufMisch(){
    if (!SP || !N || !N.length) return;
    (SP.spieltage || []).forEach(t => t.partien.concat(t.nachholspiele || []).forEach(p => {
      if (p.status === "beendet" || !p.anstoss) return;
      const d = dt(p.anstoss); if (!d) return;
      const tt = String(d.getDate()).padStart(2, "0") + String(d.getMonth() + 1).padStart(2, "0");
      ["heim", "gast"].forEach(sd => { const a = p[sd + "_aufstellung"], k = p[sd + "_k"]; if (!k || (a && a.typ === "offiziell" && !a._live)) return;
        const m = N.find(x => x.id === "aufstellung-" + String(k).toLowerCase() + "-" + tt && !x.platzhalter && x.aufstellung && (x.aufstellung.startelf || []).length === 11);
        if (!m) return;
        const au = m.aufstellung;
        p[sd + "_aufstellung"] = {typ: "offiziell", _live: true, formation: au.formation, geschaetzt: au.geschaetzt, hinweis: au.hinweis,
          startelf: au.startelf.map(c => ({...c, voll: c.voll || c.n})), bank: (au.bank || []).map(c => ({n: c.n, voll: c.voll || c.n, p: c.p, pid: c.pid})),
          quelle: ((m.quellen || [])[0] || {}).url || ""}; });
    }));
  }
'''),
 ('SP ? Promise.resolve(SP) : json("spielplan.json").then(d => { SP = d; if (MD == null) MD = d.aktuell; })',
  'SP ? Promise.resolve(SP) : json("spielplan.json").then(d => { SP = d; liveAufMisch(); if (MD == null) MD = d.aktuell; })'),
 ('return frisch("spielplan.json").then(d => { mischLive(d); SP = d; if (MD == null) MD = d.aktuell;',
  'return frisch("spielplan.json").then(d => { mischLive(d); SP = d; liveAufMisch(); if (MD == null) MD = d.aktuell;'),
 ('    N = d.meldungen.concat(N.filter(m => eigen.has(m.id) && !neuIds.has(m.id)));\n',
  '    N = d.meldungen.concat(N.filter(m => eigen.has(m.id) && !neuIds.has(m.id))); liveAufMisch();\n'),
 ('    N = d.meldungen || []; NSTAND = d.stand;', '    N = d.meldungen || []; NSTAND = d.stand; liveAufMisch();'),
]
for a, b in R:
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s); print("ok", p)
