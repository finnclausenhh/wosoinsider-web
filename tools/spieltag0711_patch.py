#!/usr/bin/env python3
"""Spieltag-Feinschliff (Finn 07.11.2026), passt auf ticker/index.html und die Artifact-index.html.

1. Spielt sie? nach Tippschluss raus: keine Sammel-Karte im Feed, keine "Tippen ›"-Zeile unter Meldungen,
   im Artikel nur noch, wenn man selbst getippt hat (Auflösung). Fan-Wert in der Spielansicht nur bis zur offiziellen Aufstellung.
2. Live-Statistik unter den Wechseln (Torschüsse, aufs Tor, Ballbesitz, xG, Ecken ...) aus live.json "stats"
   (fbl-daten tools/live_ergebnis.py). Nach Abpfiff bleibt der letzte Stand stehen, bis die Statistik mit Noten da ist.

Aufruf: python3 tools/spieltag0711_patch.py <index.html> [...]
"""
import sys

ERS = [
    # 1a Sammel-Karte
    ("""    const r = tippRunde(); if (!r || !SS) return;
    const id = `tipp-runde-md${r.md}`; if (N.some(m => m.id === id)) return;""",
     """    const r = tippRunde(); if (!r || !SS) return;
    const id = `tipp-runde-md${r.md}`;
    if (Date.now() >= r.schluss) { const i = N.findIndex(m => m.id === id); if (i >= 0) N.splice(i, 1); return; }  // nach Tippschluss nicht mehr im Feed (Finn 07.11.2026)
    if (N.some(m => m.id === id)) return;"""),
    # 1b Zeile unter Meldungen
    ("""uT ? (tsFrageZu(m) ? `<div class="nkw">""",
     """uT ? (tsFrageZu(m) && Date.now() >= tsFrageZu(m).r.schluss ? newsKarte(m) : tsFrageZu(m) ? `<div class="nkw">"""),
    # 1c Artikel
    ("""    const zu = new Date() >= r.schluss, k = tsKarte(q, r, zu, TIPPS[r.md] || {}, TS.ok && TS.stand[r.md], true);""",
     """    const zu = new Date() >= r.schluss; if (zu && !Object.keys(TIPPS[r.md] || {}).length) return "";  // Spieltag: nur noch für Tippende (Finn 07.11.2026)
    const k = tsKarte(q, r, zu, TIPPS[r.md] || {}, TS.ok && TS.stand[r.md], true);"""),
    # 1d Fan-Wert
    ("""    gLaden(); const r = tippRunde(); if (!r) return "";
    const qs = r.fragen.filter(q => q.partie === p.id""",
     """    gLaden(); const r = tippRunde(); if (!r) return "";
    if ([p.heim_aufstellung, p.gast_aufstellung].some(a => a && a.typ === "offiziell")) return "";  // offizielle Aufstellung da: Fan-Wert unnötig (Finn 07.11.2026)
    const qs = r.fragen.filter(q => q.partie === p.id"""),
    # 2 Live-Statistik
    ("""    if (sp_ && (istLive(sp_) || aus_)) h += wechselBox(k, sp_, elf, bank);""",
     """    if (sp_ && (istLive(sp_) || aus_)) h += wechselBox(k, sp_, elf, bank) + (istLive(sp_) || k === sp_.gast_k ? liveStatBox(sp_) : "");"""),
    ("""  function wechselBox(k, p, elf, bank){""",
     """  // Live-Statistik unter den Wechseln (Finn 07.11.2026): live.json "stats", gleiche Schlüssel wie apifootball.json "w".
  // Nach Abpfiff bleibt der letzte Stand, bis die Statistik mit Noten (afStatBox) da ist.
  function liveStatBox(p){
    if (!p || !p.stats || (AF && AF.spiele && AF.spiele[p.id])) return "";
    const w = p.stats, Z = [["sch", "Torschüsse"], ["tor", "aufs Tor"], ["bes", "Ballbesitz", 0, " %"], ["xg", "Expected Goals (xG)", 2], ["eck", "Ecken"], ["par", "Paraden"], ["fou", "Fouls"], ["pq", "Passquote", 0, " %"]];
    const hf = "#6E9BFF", gf = "#A9B4C6";
    const z = Z.filter(x => w[x[0]] && w[x[0]][0] != null && w[x[0]][1] != null).map(([k, t, d, e]) => { const [a, b] = w[k], s = a + b || 1, f = x => (d ? dez(x, d) : Math.round(x)) + (e || "");
      return `<div class="af-bar"><span class="w">${f(a)}</span><div class="m"><span>${t}</span><span class="bb"><i style="width:${a / s * 100}%;background:${hf}"></i><i style="width:${b / s * 100}%;background:${gf}"></i></span></div><span class="w r">${f(b)}</span></div>`; }).join("");
    if (!z) return "";
    const live = istLive(p), mi = live && p.minute ? (/^\\d/.test(p.minute) ? p.minute + "'" : p.minute) : "";
    return `<div class="wb lst"><h4>${live ? "Live-Statistik" : "Statistik"}</h4><div class="lst-k">${logo(p.heim_k, 18)}<span>${live ? (mi ? "Stand " + esc(mi) : "live") : "Stand Abpfiff, Noten folgen"}</span>${logo(p.gast_k, 18)}</div>
      <div style="display:grid;gap:9px">${z}</div><p class="af-st" style="margin:0">Teamwerte: API-Football, alle 2 bis 5 Minuten neu.</p></div>`;
  }
  function wechselBox(k, p, elf, bank){"""),
    # CSS
    (""".wb h4{margin:0;font:800 16px var(--f-display);text-transform:uppercase;letter-spacing:.3px}""",
     """.wb h4{margin:0;font:800 16px var(--f-display);text-transform:uppercase;letter-spacing:.3px}
.wb.lst{margin-top:8px}
.lst-k{display:flex;align-items:center;justify-content:space-between;font-size:11.5px;color:var(--muted)}"""),
]


def patch(s, css=True):
    for a, b in ERS:
        if a.startswith(".wb h4") and not css:
            continue
        n = s.count(a)
        if n != 1:
            raise SystemExit(f"Stelle {n}x gefunden: {a[:80]!r}")
        s = s.replace(a, b)
    return s


if __name__ == "__main__":
    for f in sys.argv[1:]:
        s = open(f, encoding="utf-8").read()
        open(f, "w", encoding="utf-8").write(patch(s))
        print("gepatcht", f)
