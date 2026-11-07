"""Finn 07.11.2026 (Leverkusen-HSV): Spielansicht und Spielbericht.

Aufruf: python3 tools/spielbericht_patch.py <eingabe.html> <ausgabe.html>
1  Spielansicht: Umschalter Heim/Gast immer, auch nach Abpfiff (Aufstellung mit Noten), nicht mehr beide Teams untereinander
2  Statistik (live und nach Abpfiff mit Noten) unter die Aufstellung, nicht mehr darüber bzw. im Team-Block unter den Wechseln
3  Spielbericht-Meldungen (endstand-*, Tag SPIELBERICHT, partie_id) zeigen Aufstellungen mit Umschalter, Noten und Statistik
Gilt für ticker/index.html und die index.html im Artifact.
"""
import sys

R = []
def r(alt, neu, n=1):
    R.append((alt, neu, n))

# 2: Live-Statistik nicht mehr im Team-Block
r('''if (sp_ && (istLive(sp_) || aus_)) h += wechselBox(k, sp_, elf, bank) + (istLive(sp_) || k === sp_.gast_k ? liveStatBox(sp_) : "");''',
  '''if (sp_ && (istLive(sp_) || aus_)) h += wechselBox(k, sp_, elf, bank);''')

# 1: Umschalter auch nach Abpfiff, merkt sich die Seite je Partie (Spielansicht und Artikel)
r('''    return `<div class="af-tw" role="tablist">${[["heim", p.heim, p.heim_k], ["gast", p.gast, p.gast_k]].map(([s, n, k]) => `<button role="tab" data-afseite="${s}" aria-pressed="${sel === s}"><span>${esc(KNAME[k] || n)}</span></button>`).join("")}</div>`
      + `<div class="af-swb">${sel === "heim" ? teamBlock(p.heim, p.heim_k, p.heim_aufstellung, "heim", false, p.anstoss) : teamBlock(p.gast, p.gast_k, p.gast_aufstellung, "gast", false, p.anstoss)}</div>`;
  }
  document.addEventListener("click", e => { const b = e.target.closest("[data-afseite]"); if (!b || !GAME) return; AFSEITE[GAME] = b.dataset.afseite; spiel(GAME, true); });''',
  '''    const vb = p.status === "beendet";
    return `<div class="af-tw" role="tablist">${[["heim", p.heim, p.heim_k], ["gast", p.gast, p.gast_k]].map(([s, n, k]) => `<button role="tab" data-afseite="${s}" data-afpid="${esc(p.id)}" aria-pressed="${sel === s}">${logo(k, 18)}<span>${esc(KNAME[k] || n)}</span></button>`).join("")}</div>`
      + `<div class="af-swb">${sel === "heim" ? teamBlock(p.heim, p.heim_k, p.heim_aufstellung, "heim", vb, p.anstoss) : teamBlock(p.gast, p.gast_k, p.gast_aufstellung, "gast", vb, p.anstoss)}</div>`;
  }
  document.addEventListener("click", e => { const b = e.target.closest("[data-afseite]"); if (!b) return; const pid = b.dataset.afpid || GAME; if (!pid) return; AFSEITE[pid] = b.dataset.afseite;
    if (GAME) spiel(GAME, true); else if (ARTIKEL) { const y = window.scrollY; article(ARTIKEL); window.scrollTo(0, y); } });''')

# 1+2: Spielansicht, Umschalter immer, Statistik darunter
r('''${sprung}${AS ? afBox : ""}${pv.length ?''', '''${sprung}${pv.length ?''')
r(''': `<span id="af-auf"></span>` + (p.status !== "beendet" ? teamSchalter(p) : teamBlock(p.heim, p.heim_k, p.heim_aufstellung, "heim", p.status === "beendet", p.anstoss) + teamBlock(p.gast, p.gast_k, p.gast_aufstellung, "gast", p.status === "beendet", p.anstoss))}''',
  ''': `<span id="af-auf"></span>` + teamSchalter(p) + liveStatBox(p)}''')
r('''      ${tsFanBlock(p)}
      ${!AS ? afBox : ""}''', '''      ${tsFanBlock(p)}
      ${afBox}''')

# 3: Spielbericht im Artikel mit Aufstellungen
r('''${spielAufstellung(m.spiel_aufstellung, m.verein)}`;''', '''${spielAufstellung(m.spiel_aufstellung, m.verein)}${berichtAuf(m)}`;''')
r('''  function punktArtikel(m){''', '''  // Spielbericht (Endstand, Bericht mit Noten): Aufstellungen mit Umschalter, Noten und Statistik wie in der Spielansicht (Finn 07.11.2026)
  function berichtPartie(m){
    if (!m || !m.partie_id || m.platzhalter || m.aufstellung || (m.spiel_aufstellung || []).length) return null;
    if (!/^endstand-|^bericht-|^spielbericht-/.test(m.id || "") && !(m.tags || []).includes("SPIELBERICHT")) return null;
    return m.partie_id;
  }
  function berichtAuf(m){
    const pid = berichtPartie(m); if (!pid || !SP) return "";
    const p = alleSpiele().find(x => x.id === pid); if (!p || !(p.heim_aufstellung || p.gast_aufstellung)) return "";
    const vorS = SPIELP; liveMarken(p); SPIELP = p;
    const AS = AF && AF.spiele && AF.spiele[p.id];
    AFNOTEN = AS ? AS.no : null; AFBEST = null;
    if (AS && SPN) AFBEST = new Set(besteJeTeam(p, AS).map(x => x[0]));
    try { return `<div class="ber-auf">${kap(p.status === "beendet" ? "Aufstellungen und Noten" : "Aufstellungen")}${teamSchalter(p)}${liveStatBox(p)}${AS ? afStatBox(p, AS) : ""}<button class="btn-prog" data-game="${esc(p.id)}" data-tabspiel="1">Zum Spiel ›</button></div>`; }
    finally { AFNOTEN = null; AFBEST = null; SPIELP = vorS; }
  }
  function punktArtikel(m){''')
r('''    if (stdA && !IN) loadIN()''', '''    if (berichtPartie(m) && (!SP || !AF || !SPN)) Promise.all([SP ? 0 : loadSP(), ladeAF(), ladeSPN().catch(() => {})]).then(() => { if (ARTIKEL === id && VIEW === "meldungen") { const y = window.scrollY; article(id); window.scrollTo(0, y); } }).catch(() => {});
    if (stdA && !IN) loadIN()''')

# 4: Nach Abpfiff fehlende Wechsel, Tore, Vorlagen und Karten aus dem Liveticker ergänzen, wenn die offizielle Aufstellung schon Wechsel hat,
#    aber nicht alle (Leverkusen-HSV: Brandau 90+4 eingewechselt stand unter "Ohne Einsatz", Loonens 2:0 in der 90+6 fehlte). Rücknahme beim nächsten Rendern über _bk, _tz, _vz, _kg.
r('''        if (s._bk) { ["ein", "ein_min", "aus"].forEach(f => { if (s._bk[f] === undefined) delete s[f]; else s[f] = s._bk[f]; }); delete s._bk; } });''',
  '''        if (s._bk) { ["ein", "ein_min", "aus"].forEach(f => { if (s._bk[f] === undefined) delete s[f]; else s[f] = s._bk[f]; }); delete s._bk; }
        if (s._tz) { s.tore = (s.tore || 0) - s._tz; if (!(s.tore > 0)) delete s.tore; delete s._tz; }
        if (s._vz) { s.vorl = (s.vorl || 0) - s._vz; if (!(s.vorl > 0)) delete s.vorl; delete s._vz; }
        if (s._kg) { s._kg.forEach(f => delete s[f]); delete s._kg; } });
      if (p.status === "beendet" && alle.some(s => s.ein === true || s.aus)) {
        const n3 = x => nNorm(x || "").replace(/[^a-z0-9 -]/g, ""), f3 = n => { const x = n3(n); return x ? (alle.find(s => n3(s.n) === x) || alle.find(s => n3(s.n).endsWith(" " + x) || x.endsWith(" " + n3(s.n)))) : null; };
        (p.wechsel || []).filter(w => w.seite === seite).forEach(w => { const e = f3(w.ein), r = f3(w.aus); if (!e || e.ein === true) return;
          [e, r].forEach(s => { if (s && !s._bk) s._bk = {ein: s.ein, ein_min: s.ein_min, aus: s.aus}; }); e.ein = true; e.ein_min = w.min; if (r && !r.aus) r.aus = w.min; });
        const zaehl = (L, f) => { const c = new Map(); L.forEach(n => { const s = f3(n); if (s) c.set(s, (c.get(s) || 0) + 1); }); return c; };
        zaehl((p.tore || []).filter(t => t.seite === seite && t.art !== "Eigentor" && !t.et).map(t => t.n), "tore").forEach((n, s) => { const d = n - (s.tore || 0); if (d > 0) { s.tore = (s.tore || 0) + d; s._tz = d; } });
        if (alle.some(s => s.vorl > 0)) zaehl((p.tore || []).filter(t => t.seite === seite && t.vorlage).map(t => t.vorlage)).forEach((n, s) => { const d = n - (s.vorl || 0); if (d > 0) { s.vorl = (s.vorl || 0) + d; s._vz = d; } });
        (p.karten || []).filter(c => c.seite === seite).forEach(c => { const s = f3(c.n); if (!s) return; const f = c.art === "gelb" ? "gelb" : "rot"; if (s[f]) return; s[f] = true; s._kg = (s._kg || []).concat(f);
          if (c.art === "gelbrot" && !s.gr) { s.gr = true; s._kg.push("gr"); } });
      }''')

# 5: Beste Note je Team nur ab 46 Minuten (wie überall), Kurzeinsätze zählen nicht (Karczewska 6,7 als Joker war "beste HSV-Note", im Text Stoldt 6,6)
r('''  function afStatBox(p, AS){''', '''  function kurzEinsatz(p){
    const k = new Set(), mn = v => parseInt(String(v || "").replace(/\\+.*/, ""), 10) || 0, nk = x => nNorm(nachN(x || ""));
    [p.heim_aufstellung, p.gast_aufstellung].forEach(a => { if (!a || a.typ !== "offiziell") return;
      (a.startelf || []).forEach(s => { if (s.aus && mn(s.aus) < 46) k.add(nk(s.n)); });
      (a.bank || []).forEach(s => { if (s.ein === true && s.ein_min && 90 - mn(s.ein_min) < 46) k.add(nk(s.n)); }); });
    return k;
  }
  function besteJeTeam(p, AS){
    const kz = kurzEinsatz(p);
    return [p.heim_k, p.gast_k].map(k => Object.entries((AS && AS.no) || {}).filter(([id]) => { const x = spById(id) || {}; return x.k === k && !kz.has(nNorm(nachN(x.n || ""))); }).sort((a, b) => b[1] - a[1])[0]).filter(Boolean);
  }
  function afStatBox(p, AS){''')
r('''    const best = [p.heim_k, p.gast_k].map(k => Object.entries(AS.no || {}).filter(([id]) => (spById(id) || {}).k === k).sort((a, b) => b[1] - a[1])[0]).filter(Boolean);''',
  '''    const best = besteJeTeam(p, AS);''')
r('''    if (AS && SPN) { AFBEST = new Set(); [p.heim_k, p.gast_k].forEach(k => { const l = Object.entries(AS.no).filter(([id]) => (spById(id) || {}).k === k).sort((a, b) => b[1] - a[1]); if (l[0]) AFBEST.add(l[0][0]); }); }''',
  '''    if (AS && SPN) AFBEST = new Set(besteJeTeam(p, AS).map(x => x[0]));''')

CSS = '''.ber-auf{display:grid;gap:10px;margin-top:6px}.ber-auf .btn-prog{justify-self:start}
'''

def main(a, b):
    s = open(a, encoding="utf-8").read()
    fehl = []
    for alt, neu, n in R:
        c = s.count(alt)
        if c != n: fehl.append((c, alt[:100])); continue
        s = s.replace(alt, neu)
    if fehl:
        for f in fehl: print("NICHT GEFUNDEN/MEHRFACH", f)
        sys.exit(1)
    # CSS in den letzten Style-Block (im Artifact der große, Regel 9)
    i = s.rindex("</style>")
    s = s[:i] + CSS + s[i:]
    open(b, "w", encoding="utf-8").write(s)
    print("ok", len(R), "Ersetzungen")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
