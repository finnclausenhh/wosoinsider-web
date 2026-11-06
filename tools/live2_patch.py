#!/usr/bin/env python3
"""Spielplan live (Finn 06.11.2026): Sobald ein Spiel läuft, verschwinden die Hinweise unter der Partie
(Aufstellung, Einsehbar, Englische Woche). Torschützinnen mit Minute und Vorlage stehen direkt unter dem
Vereinsnamen in der Spielplan-Liste und in der Spielansicht (Vorlage dort jetzt direkt unter der Schützin) (nur live; nach Abpfiff zeigt sie die Spielansicht wie bisher).
In der Spielansicht verschwindet "Daten zum Spiel", sobald das Spiel läuft; die Tore stehen dort schon unter den Vereinen. Auf den Stand nach tools/live_patch.py. Jede Ersetzung muss genau einmal passen.
Aufruf: python3 tools/live2_patch.py <index.html>
"""
import sys

ERS = [
    # Hinweise ausblenden, solange das Spiel läuft
    ("""      ${p.status !== "beendet" ? (() => { const v = AF && (AF.vorschau || []).some(x => x.id === p.id), a = [p.heim_aufstellung, p.gast_aufstellung].filter(Boolean), off = a.some(x => x.typ === "offiziell");""",
     """      ${p.status !== "beendet" && !istLive(p) ? (() => { const v = AF && (AF.vorschau || []).some(x => x.id === p.id), a = [p.heim_aufstellung, p.gast_aufstellung].filter(Boolean), off = a.some(x => x.typ === "offiziell");"""),
    ("""      ${p.status !== "beendet" && einsehbar(p) ? `<div class="eins-z">""",
     """      ${p.status !== "beendet" && !istLive(p) && einsehbar(p) ? `<div class="eins-z">"""),
    ("""<span>Offizielle Aufstellung kommt, bevor Kickbase schließt</span></div>` : ""}${bs.length ? (klein""",
     """<span>Offizielle Aufstellung kommt, bevor Kickbase schließt</span></div>` : ""}${torZeile(p)}${bs.length && !istLive(p) ? (klein"""),
    # Torschützinnen unter den Vereinsnamen
    ("""  function partieZeile(p, mitTag){""",
     """  const torListe = (p, seite) => (p.tore || []).filter(t => t.seite === seite)
    .map(t => `<span class="tz-t"><b>${esc(t.n)}</b> ${esc(t.min)}'${t.vorlage ? `<small>Vorlage ${esc(t.vorlage)}</small>` : t.art ? `<small>${esc(t.art)}</small>` : ""}</span>`).join("");
  const torZeile = p => istLive(p) && (p.tore || []).length
    ? `<div class="pr-tore"><div class="h">${torListe(p, "heim")}</div><div></div><div>${torListe(p, "gast")}</div></div>` : "";
  function partieZeile(p, mitTag){"""),
    # Spielansicht: Vorlage direkt unter der Schützin (nicht erst im Detail)
    ("""      mins[n].push(`${t.min || ""}'${t.art === "Elfmeter" ? " (E)" : ""}${t.et ? " (ET)" : ""}`); });
    return r.map(n => `<span><b>${esc(n)}</b> <span class="mu">${esc(mins[n].join(", "))}</span></span>`).join("");""",
     """      mins[n].push(`${t.min || ""}'${t.art === "Elfmeter" ? " (E)" : ""}${t.et ? " (ET)" : ""}`); if (t.vorlage) (mins[n].v = mins[n].v || []).push(t.vorlage); });
    return r.map(n => `<span><b>${esc(n)}</b> <span class="mu">${esc(mins[n].join(", "))}</span>${mins[n].v ? `<small class="tvl">Vorlage ${esc([...new Set(mins[n].v)].join(", "))}</small>` : ""}</span>`).join("");"""),
    # Spielansicht: Daten zum Spiel weg, sobald live
    ("""    const hatV = p.status !== "beendet" && AF && (AF.vorschau || []).some(v => v.id === p.id),""",
     """    const hatV = p.status !== "beendet" && !istLive(p) && AF && (AF.vorschau || []).some(v => v.id === p.id),"""),
    # CSS
    (""".pr-t.h{justify-content:flex-end;text-align:right}""",
     """.pr-t.h{justify-content:flex-end;text-align:right}
.pr-tore{display:grid;grid-template-columns:minmax(0,1fr) 58px minmax(0,1fr);gap:8px;margin-top:-4px;font-size:12px;line-height:1.25}
.pr-tore>div{display:grid;gap:5px;align-content:start;min-width:0;padding-left:38px}
.pr-tore>.h{padding-left:0;padding-right:38px;text-align:right}
.tz-t{display:block;min-width:0}
.tz-t b{font-weight:600}
.tz-t small{display:block;font-size:11px;color:var(--muted);overflow-wrap:anywhere}
.tore .tvl{display:block;font-size:11px;color:var(--muted)}"""),
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
