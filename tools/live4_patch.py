#!/usr/bin/env python3
"""Live, Runde 4 (Finn 06.11.2026), auf den Stand nach tools/live3_patch.py:
- News: Live-Leiste oben im Feed mit allen laufenden Spielen (Stand, Minute, Torschützinnen mit Vorlage sichtbar).
- Spielansicht live: Tore, Vorlagen und Karten aus live.json als Symbole an den Spielerinnen der offiziellen
  Aufstellung (Feld und Bank). Vorlage als Schuh-Symbol statt "1V" (auch nach Abpfiff).
- Ab Anpfiff weg: Standard-Hinweis "X nicht in der Startelf" und die Box Englische Woche.
Jede Ersetzung muss genau einmal passen. Aufruf: python3 tools/live4_patch.py <index.html>
"""
import sys

VORL = ("""  const VORL = '<svg class="vorl" viewBox="0 0 24 24" aria-label="Vorlage"><path d="M3 15.5h7.2l2.6-3.4 2.4.9c.9.4 1.5 1.2 1.6 2.2l.1 1.3H21v2.8H3z" fill="currentColor"/>'
    + '<path d="M9.6 12.2l1.4 1.1M11 10.6l1.3 1" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/><path d="M5.2 15.5V9.2h3.9l1.6 3" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>';
""")

ERS = [
    # Schuh-Symbol definieren
    ("""  const BALL = '<svg class="ball" viewBox="0 0 24 24" aria-label="Tor">""",
     VORL + """  const BALL = '<svg class="ball" viewBox="0 0 24 24" aria-label="Tor">"""),
    # Feld: Vorlage als Symbol
    ("""if (s.vorl > 0) ex += `<span class="as">${s.vorl}V</span>`;""",
     """if (s.vorl > 0) ex += `<span class="as" aria-label="${s.vorl} ${s.vorl > 1 ? "Vorlagen" : "Vorlage"}">${VORL}${s.vorl > 1 ? `<b>${s.vorl}</b>` : ""}</span>`;"""),
    ("""<span><i class="as">Vorl.</i> Vorlage</span>""",
     """<span><i class="as">${VORL}</i> Vorlage</span>"""),
    # Bank: Symbole hinter dem Namen
    ("""`<b${s.dim ? ' class="dim"' : ""}>${esc(s.n)}${s.em ? `<span class="em">${esc(s.em)}</span>` : ""}""",
     """`<b${s.dim ? ' class="dim"' : ""}>${esc(s.n)}${s.em ? `<span class="em">${esc(s.em)}</span>` : ""}${s.tore > 0 ? `<span class="bsy">${BALL.repeat(Math.min(s.tore, 3))}</span>` : ""}${s.vorl > 0 ? `<span class="bsy v">${VORL.repeat(Math.min(s.vorl, 3))}</span>` : ""}${s.rot ? `<span class="bsy">${karte(true)}</span>` : s.gelb ? `<span class="bsy">${karte(false)}</span>` : ""}"""),
    # Standard-Hinweis nur vor Anpfiff
    ("""${!vorbei && a ? stdHinweis(k, a) : ""}""",
     """${!vorbei && a && !(anstoss && dt(anstoss) && dt(anstoss).getTime() <= Date.now()) ? stdHinweis(k, a) : ""}"""),
    # Englische Woche in der Spielansicht nur vor Anpfiff
    ("""      ${bs.length ? `<div class="kartebox" style="gap:8px">${kap("Englische Woche")}""",
     """      ${bs.length && !istLive(p) ? `<div class="kartebox" style="gap:8px">${kap("Englische Woche")}"""),
    # Spielansicht: Live-Marken setzen
    ("""    const AS = AF && AF.spiele && AF.spiele[p.id];
    AFNOTEN = AS ? AS.no : null; AFBEST = null;""",
     """    liveMarken(p);
    const AS = AF && AF.spiele && AF.spiele[p.id];
    AFNOTEN = AS ? AS.no : null; AFBEST = null;"""),
    ("""  function aufAngepfiffen(m){""",
     """  // Tore, Vorlagen, Karten aus live.json an die Spielerinnen der offiziellen Aufstellung (nur live, jedes Mal neu)
  function liveMarken(p){
    const live = p.status === "live" || p.status === "läuft";
    [["heim", p.heim_aufstellung], ["gast", p.gast_aufstellung]].forEach(([seite, a]) => {
      if (!a || a.typ !== "offiziell") return;
      const alle = [...(a.startelf || []), ...(a.bank || [])];
      alle.forEach(s => { if (s._lt) { ["tore", "vorl", "gelb", "rot", "gr", "_lt"].forEach(f => delete s[f]); } });
      if (!live) return;
      const nn = x => nNorm(x).replace(/[^a-z0-9 -]/g, "");
      const finde = n => { const x = nn(n); if (!x) return null;
        return alle.find(s => nn(s.n) === x) || alle.find(s => nn(s.n).endsWith(" " + x) || x.endsWith(" " + nn(s.n)) || nn(s.n).endsWith(x)); };
      const setz = (n, f, v) => { const s = finde(n); if (!s) return; s._lt = true; s[f] = v === true ? true : (s[f] || 0) + 1; };
      (p.tore || []).filter(t => t.seite === seite && t.art !== "Eigentor").forEach(t => { setz(t.n, "tore"); if (t.vorlage) setz(t.vorlage, "vorl"); });
      (p.karten || []).filter(c => c.seite === seite).forEach(c => { if (c.art === "gelb") setz(c.n, "gelb", true); else { setz(c.n, "rot", true); if (c.art === "gelbrot") setz(c.n, "gr", true); } });
    });
  }
  function liveLeiste(){
    if (!SP) return "";
    const l = (SP.spieltage || []).flatMap(t => t.partien.concat(t.nachholspiele || [])).filter(p => p.status === "live" || p.status === "läuft")
      .sort((a, b) => (dt(a.anstoss) || 0) - (dt(b.anstoss) || 0));
    return l.length ? `<div class="live-l"><div class="live-k"><i></i>LIVE</div>${l.map(p => partieZeile(p).replace('<button class="pr', '<button data-tabspiel="1" class="pr')).join("")}</div>` : "";
  }
  function aufAngepfiffen(m){"""),
    # Feed: Live-Leiste ganz oben
    ("""    let h = fest.map(punktKarte).join("");""",
     """    let h = liveLeiste() + fest.map(punktKarte).join("");"""),
    # CSS
    (""".pr-tore{display:grid;""",
     """.live-l{display:grid;gap:8px}
.live-k{display:flex;align-items:center;gap:6px;font:800 11px var(--f-mono);letter-spacing:.08em;color:var(--inj)}
.live-k i{width:7px;height:7px;border-radius:50%;background:var(--inj);animation:lvp 1.6s infinite}
@keyframes lvp{0%,100%{opacity:1}50%{opacity:.3}}
.spl .as{display:flex;align-items:center;gap:1px;padding:2px 4px}
.spl .as .vorl{width:14px;height:14px;display:block}
.spl .as b{font:800 11px var(--f-body)}
.fleg .as{display:inline-flex;align-items:center;background:#8FB0FF;color:#0B1220;border-radius:6px;padding:1px 4px}
.fleg .as .vorl{width:12px;height:12px}
.bsy{display:inline-flex;gap:1px;align-items:center;margin-left:4px;vertical-align:-2px}
.bsy .ball,.bsy .vorl{width:13px;height:13px}
.bsy.v{color:#8FB0FF}
.bsy .krt{width:9px;height:12px;border-radius:2px}
.pr-tore{display:grid;"""),
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
