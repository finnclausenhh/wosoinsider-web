#!/usr/bin/env python3
"""Live, Runde 7 (Finn 06.11.2026, 20:54), auf den Stand nach tools/live6_patch.py und live_tempo_patch.py:
- Spielansicht: Tore einzeln je Treffer (Name, Minute), Vorlage nur als Name in dünner Schrift darunter, ohne das Wort
  "Vorlage". So ist klar, welches Tor eine Vorlage hatte (Peddemors 70' war ein direkter Freistoß, ohne Vorlage).
- (FS) für direkte Freistöße in Liste und Spielansicht, wie (E) und (ET).
- Bank: Namen mit Abstand statt Mittelpunkt (der Punkt landete beim Umbruch am Zeilenanfang).
- Wechsel-Feld auch nach Abpfiff (aus live.json oder, nach dem Spieltage-Lauf, aus den Einwechselminuten der
  Aufstellung). Nach Abpfiff entfällt "Änderungen zum letzten Ligaspiel".
- Zwischen Abpfiff und Spieltage-Lauf setzt liveMarken Tore, Karten und Wechsel weiter aus live.json, damit
  Eingewechselte nicht unter "Ohne Einsatz" stehen.
Jede Ersetzung muss genau einmal passen. Aufruf: python3 tools/live7_patch.py <index.html>
"""
import sys

ZUSATZ = """t.art === "Elfmeter" ? " (E)" : t.art === "Eigentor" ? " (ET)" : t.art === "Freistoß" ? " (FS)" : \"\""""

ERS = [
    # Wechsel aus live.json auch nach Abpfiff behalten (Paare bei gleicher Minute sind nur dort eindeutig)
    ("""const x = L[p.id]; if (x && p.status !== "beendet") Object.assign(p, x); })); };""",
     """const x = L[p.id]; if (x && p.status !== "beendet") Object.assign(p, x); else if (x && !(p.wechsel || []).length && (x.wechsel || []).length) p.wechsel = x.wechsel; })); };"""),
    ("""  loadSP().then(() => { if (spielLaeuft()) loadLive(); });""",
     """  loadSP().then(() => loadLive());"""),
    ("""    .map(t => `<span class="tz-t"><b>${esc(t.n)}</b> ${esc(t.min)}'${t.art === "Elfmeter" ? " (E)" : t.art === "Eigentor" ? " (ET)" : ""}</span>`).join("");""",
     """    .map(t => `<span class="tz-t"><b>${esc(t.n)}</b> ${esc(t.min)}'${""" + ZUSATZ + """}</span>`).join("");"""),
    ("""    const r = [], mins = {};
    tore.filter(t => zaehlt(t) === seite).forEach(t => { const n = t.n || ""; if (!mins[n]) { r.push(n); mins[n] = []; }
      mins[n].push(`${t.min || ""}'${t.art === "Elfmeter" ? " (E)" : ""}${t.et ? " (ET)" : ""}`); if (t.vorlage) (mins[n].v = mins[n].v || []).push(t.vorlage); });
    return r.map(n => `<span><b>${esc(n)}</b> <span class="mu">${esc(mins[n].join(", "))}</span>${mins[n].v ? `<small class="tvl">Vorlage ${esc([...new Set(mins[n].v)].join(", "))}</small>` : ""}</span>`).join("");""",
     """    return tore.filter(t => zaehlt(t) === seite).map(t => `<span><b>${esc(t.n || "")}</b> <span class="mu">${esc(t.min || "")}'${t.art === "Elfmeter" ? " (E)" : t.art === "Freistoß" ? " (FS)" : ""}${t.et || t.art === "Eigentor" ? " (ET)" : ""}</span>${t.vorlage ? `<small class="tvl">${esc(t.vorlage)}</small>` : ""}</span>`).join("");"""),
    # Bank ohne Mittelpunkt
    (""".bk .ns b:not(:first-child)::before{content:"·";color:var(--muted);font-weight:400;margin:0 7px}""",
     """.bk .ns{gap:3px 14px}"""),
    # Spiel merken
    ("""    liveMarken(p); LIVEP = istLive(p) ? p : null;""",
     """    liveMarken(p); LIVEP = istLive(p) ? p : null; SPIELP = p;"""),
    ("""  let LIVEP = null;""",
     """  let LIVEP = null, SPIELP = null;"""),
    # Nach Abpfiff: Änderungen weg, Wechsel dazu
    ("""    h += aenderungen(k, elf.filter(s => neuSet.has(s.n)), raus);
    if (LIVEP && (LIVEP.heim_k === k || LIVEP.gast_k === k)) h += wechselBox(k, LIVEP, elf, bank);""",
     """    const sp_ = SPIELP && (SPIELP.heim_k === k || SPIELP.gast_k === k) ? SPIELP : null, aus_ = sp_ && sp_.status === "beendet";
    if (!aus_) h += aenderungen(k, elf.filter(s => neuSet.has(s.n)), raus);
    if (sp_ && (istLive(sp_) || aus_)) h += wechselBox(k, sp_, elf, bank);"""),
    # Wechsel nach Abpfiff aus der Aufstellung
    ("""    const w = (p.wechsel || []).filter(x => x.seite === seite);
    if (!w.length) return `<div class="wb"><h4>Wechsel</h4><p class="dat" style="margin:0">Bisher keine Wechsel.</p></div>`;""",
     """    let w = (p.wechsel || []).filter(x => x.seite === seite);
    if (!w.length && p.status === "beendet") {  // nach dem Spieltage-Lauf: Einwechselminuten aus der Aufstellung
      const rein = bank.filter(s => s.ein === true).sort((a, b) => (parseInt(a.ein_min, 10) || 99) - (parseInt(b.ein_min, 10) || 99));
      const raus = elf.concat(bank).filter(s => s.aus), frei = raus.slice();
      w = rein.map(s => { let i = frei.findIndex(r => String(r.aus) === String(s.ein_min)); if (i < 0) i = frei.length ? 0 : -1;
        const r = i >= 0 ? frei.splice(i, 1)[0] : null; return {ein: s.n, aus: r ? r.n : "", min: s.ein_min || (r && r.aus) || ""}; });
    }
    if (!w.length) return `<div class="wb"><h4>Wechsel</h4><p class="dat" style="margin:0">${p.status === "beendet" ? "Keine Wechsel." : "Bisher keine Wechsel."}</p></div>`;"""),
    # liveMarken auch zwischen Abpfiff und Spieltage-Lauf
    ("""      if (!live) return;
      const nn = x => nNorm(x).replace(/[^a-z0-9 -]/g, "");""",
     """      const luecke = p.status === "beendet" && (p.wechsel || []).length && !alle.some(s => s.ein === true || s.aus);
      if (!live && !luecke) return;
      const nn = x => nNorm(x).replace(/[^a-z0-9 -]/g, "");"""),
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
