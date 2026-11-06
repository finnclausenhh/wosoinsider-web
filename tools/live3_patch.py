#!/usr/bin/env python3
"""News live (Finn 06.11.2026): Meldungen "Offizielle Aufstellung" verschwinden aus dem Feed, sobald ihr Spiel läuft
(und danach). Der Artikel bleibt per Link erreichbar, die Aufstellung steht in der Spielansicht. Der Feed zeichnet sich
neu, wenn live.json einen Statuswechsel bringt. Auf den Stand nach tools/live2_patch.py. Jede Ersetzung genau einmal.
Aufruf: python3 tools/live3_patch.py <index.html>
"""
import sys

ERS = [
    ("""    const alle = N.filter(m => !fest.includes(m)).sort((a, b) => (dt(b.zeit) || 0) - (dt(a.zeit) || 0));""",
     """    const alle = N.filter(m => !fest.includes(m) && !aufAngepfiffen(m)).sort((a, b) => (dt(b.zeit) || 0) - (dt(a.zeit) || 0));"""),
    ("""  function list(){""",
     """  function aufAngepfiffen(m){
    if (!SP || !(m.aufstellung || /^aufstellung-/.test(m.id || ""))) return false;
    const ma = ((m.quellen || [])[0] || {}).url || "", id = m.partie_id || (ma.match(/\\/ma(\\d+)\\//) || [])[1];
    const p = id && (SP.spieltage || []).flatMap(t => t.partien.concat(t.nachholspiele || [])).find(x => x.id === id);
    return !!p && (p.status === "live" || p.status === "läuft" || p.status === "beendet");
  }
  function list(){"""),
    ("""      if (neu && SP) { mischLive(SP); if (!BACK && VIEW === "spielplan") GAME ? spiel(GAME, true) : spielplan(); } }).catch(() => {});""",
     """      if (neu && SP) { mischLive(SP); if (!BACK && VIEW === "spielplan") GAME ? spiel(GAME, true) : spielplan();
        else if (!BACK && VIEW === "meldungen" && document.querySelector("#main .liste")) { const y = window.scrollY; list(); window.scrollTo(0, y); } } }).catch(() => {});"""),
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
