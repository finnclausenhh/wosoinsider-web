#!/usr/bin/env python3
"""Live-Ergebnis im Spielplan (Finn 06.11.2026). Lädt live.json direkt von raw.githubusercontent.com (GitHub Pages
braucht für spielplan.json zu lange), mischt Status, Ergebnis und Minute in SP und lädt während Spielen jede Minute nach.
Schreibt fbl-daten/tools/live_ergebnis.py. Jede Ersetzung muss genau einmal passen.
Aufruf: python3 tools/live_patch.py <index.html>
"""
import sys

ERS = [
    ("""  function loadSP(){
    return json("spielplan.json").then(d => { SP = d; if (MD == null) MD = d.aktuell;""",
     """  const LIVE_URL = "https://raw.githubusercontent.com/finnclausenhh/fbl-daten/main/live.json";
  let LIVE = null;
  const mischLive = d => { const L = (LIVE && LIVE.spiele) || {}; if (!d) return;
    (d.spieltage || []).forEach(t => t.partien.concat(t.nachholspiele || []).forEach(p => { const x = L[p.id]; if (x && p.status !== "beendet") Object.assign(p, x); })); };
  const spielLaeuft = () => SP && alleSpiele().some(p => { if (p.status === "beendet" || !p.anstoss || /T00:00/.test(p.anstoss)) return false;
    const m = (Date.now() - dt(p.anstoss).getTime()) / 60000; return m > -5 && m < 150; });
  function loadLive(){
    return fetch(LIVE_URL + "?t=" + Date.now(), {cache: "no-store"}).then(r => r.ok ? r.json() : null).then(l => {
      if (!l) return; const neu = JSON.stringify(l.spiele) !== JSON.stringify(LIVE && LIVE.spiele); LIVE = l;
      if (neu && SP) { mischLive(SP); if (!BACK && VIEW === "spielplan") GAME ? spiel(GAME, true) : spielplan(); } }).catch(() => {});
  }
  function loadSP(){
    return json("spielplan.json").then(d => { mischLive(d); SP = d; if (MD == null) MD = d.aktuell;"""),
    ("""  loadSP();
  loadIN();""",
     """  loadSP().then(() => { if (spielLaeuft()) loadLive(); });
  setInterval(() => { if (!document.hidden && spielLaeuft()) loadLive(); }, 60000);
  loadIN();"""),
]


def main(pfad):
    s = open(pfad, encoding="utf-8").read()
    for alt, neu in ERS:
        n = s.count(alt)
        if n != 1:
            sys.exit(f"passt {n}-mal: {alt[:70]!r}")
        s = s.replace(alt, neu)
    open(pfad, "w", encoding="utf-8").write(s)
    print("ok", pfad)


if __name__ == "__main__":
    main(sys.argv[1])
