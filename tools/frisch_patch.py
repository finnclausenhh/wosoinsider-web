#!/usr/bin/env python3
"""News und Spielplan frisch (Finn 06.11.2026). GitHub Pages lieferte am 06.11. von 18:05 bis 19:29 keinen einzigen
Deploy aus, die Webapp sah so lange keine neuen Meldungen. Jetzt:
- news.json und spielplan.json zuerst über die GitHub-Contents-API (Stand des Repos, ETag; 304 zählt nicht gegen das
  Limit von 60/h je Gerät), bei Fehler über Pages wie bisher.
- News alle 90 Sekunden nachladen (nur sichtbar, nur bei neuem "stand"); eigene Meldungen aus apifootball.json und
  tipp_auswertung.json bleiben erhalten, Liste und Scroll-Position auch.
Jede Ersetzung muss genau einmal passen. Aufruf: python3 tools/frisch_patch.py <index.html>
"""
import sys

ERS = [
    ("""  const json = f => fetch(f, {cache: "no-store"}).then(""",
     """  const API_DATEN = "https://api.github.com/repos/finnclausenhh/fbl-daten/contents/";
  const frisch = f => fetch(API_DATEN + f + "?ref=main", {cache: "no-cache", headers: {Accept: "application/vnd.github.raw+json"}})
    .then(r => r.ok ? r.json() : Promise.reject(r.status)).catch(() => json(f));
  const json = f => fetch(f, {cache: "no-store"}).then("""),
    ("""    return json("spielplan.json").then(d => { mischLive(d);""",
     """    return frisch("spielplan.json").then(d => { mischLive(d);"""),
    ("""  json("news.json").then(d => {
    N = d.meldungen || [];""",
     """  let NSTAND = null;
  setInterval(() => { if (document.hidden || !N.length) return; frisch("news.json").then(d => {
    if (!d || !d.meldungen || d.stand === NSTAND) return; NSTAND = d.stand;
    const eigen = new Set([...(AF && AF.news || []), ...(TAW || [])].map(n => n.id)), neuIds = new Set(d.meldungen.map(m => m.id));
    N = d.meldungen.concat(N.filter(m => eigen.has(m.id) && !neuIds.has(m.id)));
    if (VIEW === "meldungen" && !ARTIKEL && !BACK && document.querySelector("#main .liste")) { const y = window.scrollY; list(); window.scrollTo(0, y); }
  }).catch(() => {}); }, 90000);
  frisch("news.json").then(d => {
    N = d.meldungen || []; NSTAND = d.stand;"""),
]


def main(pfad):
    s = open(pfad, encoding="utf-8").read()
    for alt, neu in ERS:
        n = s.count(alt)
        if n != 1:
            sys.exit(f"passt {n}-mal: {alt[:80]!r}")
        s = s.replace(alt, neu)
    open(pfad, "w", encoding="utf-8").write(s)
    print("ok", pfad)


if __name__ == "__main__":
    main(sys.argv[1])
