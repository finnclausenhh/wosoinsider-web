#!/usr/bin/env python3
"""Live, Runde 5 (Finn 06.11.2026), auf den Stand nach tools/live4_patch.py:
- News-Leiste: nur Stand und Minute, ohne Torschützinnen und Vorlagen.
- Spielplan-Liste: Torschützinnen mit Minute, ohne Vorlagen (Elfmeter/Eigentor als (E)/(ET)).
- Spielansicht: Knopf "Tore im Detail" entfällt (Vorlage steht schon unter der Schützin).
- Spielansicht live: unter "Änderungen zum letzten Ligaspiel" ein Feld "Wechsel" (live.json "wechsel"),
  sonst "Bisher keine Wechsel". Wechsel markieren auch Feld (↓ Minute) und Bank (Eingewechselt).
Jede Ersetzung muss genau einmal passen. Aufruf: python3 tools/live5_patch.py <index.html>
"""
import sys

ERS = [
    # Spielplan-Liste ohne Vorlagen
    ("""    .map(t => `<span class="tz-t"><b>${esc(t.n)}</b> ${esc(t.min)}'${t.vorlage ? `<small>Vorlage ${esc(t.vorlage)}</small>` : t.art ? `<small>${esc(t.art)}</small>` : ""}</span>`).join("");""",
     """    .map(t => `<span class="tz-t"><b>${esc(t.n)}</b> ${esc(t.min)}'${t.art === "Elfmeter" ? " (E)" : t.art === "Eigentor" ? " (ET)" : ""}</span>`).join("");"""),
    # News-Leiste ohne Torschützinnen
    ("""  const torZeile = p => istLive(p) && (p.tore || []).length""",
     """  let TZ_AUS = false;
  const torZeile = p => !TZ_AUS && istLive(p) && (p.tore || []).length"""),
    ("""${l.map(p => partieZeile(p).replace('<button class="pr', '<button data-tabspiel="1" class="pr')).join("")}""",
     """${(() => { TZ_AUS = true; try { return l.map(p => partieZeile(p).replace('<button class="pr', '<button data-tabspiel="1" class="pr')).join(""); } finally { TZ_AUS = false; } })()}"""),
    # Spielansicht ohne "Tore im Detail"
    ("""
          <button class="tbtn" data-tore="1" aria-expanded="${TOREOFFEN}">${TOREOFFEN ? "Tore im Detail ausblenden" : "Tore im Detail mit Vorlage"}</button>${TOREOFFEN ? `<div class="tdet">${det}</div>` : ""}` : ""}""",
     """` : ""}"""),
    # Live-Spiel merken für die Wechsel-Box
    ("""    liveMarken(p);
    const AS = AF && AF.spiele && AF.spiele[p.id];""",
     """    liveMarken(p); LIVEP = istLive(p) ? p : null;
    const AS = AF && AF.spiele && AF.spiele[p.id];"""),
    ("""    h += aenderungen(k, elf.filter(s => neuSet.has(s.n)), raus);""",
     """    h += aenderungen(k, elf.filter(s => neuSet.has(s.n)), raus);
    if (LIVEP && (LIVEP.heim_k === k || LIVEP.gast_k === k)) h += wechselBox(k, LIVEP, elf, bank);"""),
    # liveMarken: Wechsel markieren, alte Werte sichern
    ("""      alle.forEach(s => { if (s._lt) { ["tore", "vorl", "gelb", "rot", "gr", "_lt"].forEach(f => delete s[f]); } });
      if (!live) return;""",
     """      alle.forEach(s => { if (s._lt) { ["tore", "vorl", "gelb", "rot", "gr", "_lt"].forEach(f => delete s[f]); }
        if (s._bk) { ["ein", "ein_min", "aus"].forEach(f => { if (s._bk[f] === undefined) delete s[f]; else s[f] = s._bk[f]; }); delete s._bk; } });
      if (!live) return;"""),
    ("""      (p.karten || []).filter(c => c.seite === seite).forEach(c => {""",
     """      (p.wechsel || []).filter(w => w.seite === seite).forEach(w => {
        const sich = s => { if (s && !s._bk) s._bk = {ein: s.ein, ein_min: s.ein_min, aus: s.aus}; return s; };
        const e = sich(finde(w.ein)), r = sich(finde(w.aus));
        if (e) { e.ein = true; e.ein_min = w.min; }
        if (r) r.aus = w.min;
        (a.bank || []).forEach(s => { if (s.ein == null) { sich(s); s.ein = false; } });
      });
      (p.karten || []).filter(c => c.seite === seite).forEach(c => {"""),
    ("""  function liveLeiste(){""",
     """  let LIVEP = null;
  function wechselBox(k, p, elf, bank){
    const seite = p.heim_k === k ? "heim" : "gast", nn = x => nNorm(x);
    const such = (l, n) => l.find(s => nn(s.n) === nn(n)) || l.find(s => nn(s.n).endsWith(nn(n)) || nn(n).endsWith(nn(s.n))) || (n ? {n} : null);
    const w = (p.wechsel || []).filter(x => x.seite === seite);
    if (!w.length) return `<div class="wb"><h4>Wechsel</h4><p class="dat" style="margin:0">Bisher keine Wechsel.</p></div>`;
    return `<div class="wb"><h4>Wechsel</h4>${w.map(x => wxZeile(k, such(bank, x.ein), such(elf.concat(bank), x.aus), ["n", "EIN"], ["r", "AUS"], esc(x.min) + "'")).join("")}</div>`;
  }
  function liveLeiste(){"""),
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
