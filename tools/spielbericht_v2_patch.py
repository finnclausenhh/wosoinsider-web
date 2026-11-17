#!/usr/bin/env python3
"""Spielbericht Version 2 (Finn 17.11.2026): Endstand, Spielerin des Spiels, Key Highlights,
Das zählt, Statistik, Beste Noten im Vergleich, Aufstellungen. Keine Headline, kein Fließtext.
Aufruf: python3 spielbericht_v2_patch.py ein.html aus.html (jede Ersetzung muss genau einmal passen)."""
import sys

JS = r'''
  // Spielbericht Version 2 (Finn 17.11.2026): Endstand, Spielerin des Spiels, Key Highlights, Das zählt, Statistik, Noten im Vergleich, Aufstellungen
  function sbV2(m){
    const pid = berichtPartie(m); if (!pid || !SP) return "";
    const p = alleSpiele().find(x => x.id === pid); if (!p || p.status !== "beendet" || !(p.ergebnis || []).length) return "";
    const vorS = SPIELP; liveMarken(p); SPIELP = p;
    const AS = AF && AF.spiele && AF.spiele[p.id];
    AFNOTEN = AS ? AS.no : null; AFBEST = null;
    if (AS && SPN) AFBEST = new Set(besteJeTeam(p, AS).map(x => x[0]));
    try {
      const mn = v => { const t = String(v || "").split("+"); return (parseInt(t[0], 10) || 0) + (parseInt(t[1], 10) || 0) / 100; };
      const halb = v => (parseInt(String(v || ""), 10) || 0) <= 45;
      const nk = x => nNorm(nachN(x || ""));
      const sk = s => s === "heim" ? p.heim_k : p.gast_k;
      const tore = (p.tore || []).slice().sort((a, b) => mn(a.min) - mn(b.min));
      const hz = [0, 0]; tore.filter(t => halb(t.min)).forEach(t => hz[t.seite === "heim" ? 0 : 1]++);
      const karten = (p.karten || []).length ? p.karten : (p.platzverweise || []).map(x => ({...x, art: x.art || "rot"}));
      const rot = karten.filter(c => c.art !== "gelb");
      // Verschossene Elfmeter: live_ergebnis.py schreibt "verschossen"; fehlt das Feld, aus dem Text des Spielberichts ("Elfmeter verschossen: Bremer (90+4.).")
      let vs = p.verschossen || p.elf_vs || [];
      if (!vs.length) (m.text || []).forEach(t => { const r = /Elfmeter verschossen: ([^(]+?) \((\d+(?:\+\d+)?)\.?\)/.exec(t); if (!r) return;
        const seite = ["heim", "gast"].find(s => { const a = p[s + "_aufstellung"] || {}; return [...(a.startelf || []), ...(a.bank || [])].some(x => nk(x.n) === nk(r[1])); }); if (seite) vs = vs.concat({seite, n: r[1].trim(), min: r[2]}); });
      const chip = (s, n) => [...(s.startelf || []), ...(s.bank || [])].find(x => nk(x.n) === nk(n));
      const gelbVon = seite => { const L = karten.filter(c => c.art === "gelb" && c.seite === seite).map(c => nachN(c.n));
        if (L.length || (p.karten || []).length) return L; const a = p[seite + "_aufstellung"] || {};
        return [...(a.startelf || []), ...(a.bank || [])].filter(x => x.gelb && !x.rot).map(x => nachN(x.n)); };
      const POS = {TW: "Tor", ABW: "Abwehr", DM: "Mittelfeld", MF: "Mittelfeld", OM: "Mittelfeld", ST: "Sturm"};
      const d = String(p.anstoss || "").slice(0, 10).split("-").reverse().join(".");
      let h = `<div class="sbv2"><div class="sbv2-kz"><span>SPIELBERICHT${p.md ? " · " + esc(p.md) + ". SPIELTAG" : ""}</span><span>${esc(d)}</span></div>`;
      // Endstand
      h += `<div class="sbv2-end">${[[p.heim, p.heim_k], null, [p.gast, p.gast_k]].map(t => t ? `<button class="sbv2-tm kd-btn" data-kader="${esc(t[1])}" aria-label="Kader ${esc(t[0])}"><span class="sbv2-wp">${logo(t[1], 40)}</span><span>${esc(KNAME[t[1]] || t[0])}</span></button>`
        : `<div class="sbv2-st"><b>${esc(p.ergebnis[0])}:${esc(p.ergebnis[1])}</b><span>Ende · Halbzeit ${hz[0]}:${hz[1]}</span></div>`).join("")}</div>`;
      // Spielerin des Spiels: beste Note (ab 46 Min.), ohne Noten die Torschützin mit den meisten Toren
      let sds = null;
      if (AS && SPN) { const b = besteJeTeam(p, AS).sort((a, c) => c[1] - a[1])[0]; const x = b && spById(b[0]); if (x) sds = {n: x.n, k: x.k, id: x.id, note: b[1]}; }
      if (!sds && tore.length) { const c = new Map(); tore.filter(t => t.art !== "Eigentor").forEach(t => c.set(t.seite + "|" + t.n, (c.get(t.seite + "|" + t.n) || 0) + 1));
        const top = [...c.entries()].sort((a, b) => b[1] - a[1])[0]; if (top) { const [s, n] = top[0].split("|"); sds = {n, k: sk(s), tore: top[1]}; } }
      if (sds) { const seite = sds.k === p.heim_k ? "heim" : "gast", a = p[seite + "_aufstellung"] || {}, ch = chip(a, sds.n) || {};
        const tz = tore.filter(t => t.seite === seite && t.art !== "Eigentor" && nk(t.n) === nk(sds.n)), vz = tore.filter(t => t.seite === seite && t.vorlage && nk(t.vorlage) === nk(sds.n));
        const kz = karten.filter(c => c.seite === seite && nk(c.n) === nk(sds.n));
        const chips = tz.map(t => `<span>Tor ${esc(t.min)}'${t.art === "Elfmeter" ? " (FE)" : ""}</span>`).join("") + vz.map(t => `<span>Vorlage ${esc(t.min)}'</span>`).join("")
          + (kz.length ? kz : ch.gelb ? [{art: "gelb"}] : []).map(c => `<span><i class="sbv2-k ${c.art === "gelb" ? "g" : "r"}"></i>${c.art === "gelb" ? "Gelb" : c.art === "gelbrot" ? "Gelb-Rot" : "Rot"}</span>`).join("");
        const nm = sds.id ? `<button class="sbv2-nm" data-profil="${esc(sds.id)}">${esc(sds.n)}</button>` : `<b class="sbv2-nm">${esc(sds.n)}</b>`;
        h += `<div class="sbv2-sds"><b class="sbv2-big">${sds.note != null ? dez(sds.note) : sds.tore}</b><div><div class="sbv2-l">SPIELERIN DES SPIELS${sds.note == null ? " · NOTEN FOLGEN" : ""}</div>${nm}<div class="sbv2-v">${esc(kname(sds.k))}${POS[ch.p] ? " · " + POS[ch.p] : ""}</div>${chips ? `<div class="sbv2-ch">${chips}</div>` : ""}</div></div>`; }
      // Key Highlights
      const ev = [];
      let st = [0, 0]; tore.forEach(t => { st[t.seite === "heim" ? 0 : 1]++; ev.push({seite: t.seite, min: t.min, n: nachN(t.n), was: (t.art === "Eigentor" ? "Eigentor zum " : t.art === "Elfmeter" ? "Elfmeter zum " : "Tor zum ") + st[0] + ":" + st[1] + (t.vorlage ? ", Vorlage " + nachN(t.vorlage) : ""), tor: true}); });
      rot.forEach(c => ev.push({seite: c.seite, min: c.min, n: nachN(c.n), was: c.art === "gelbrot" ? "Gelb-Rote Karte" : "Rote Karte", k: c.art === "gelbrot" ? "gr" : "r"}));
      vs.forEach(c => ev.push({seite: c.seite, min: c.min, n: nachN(c.n), was: "Elfmeter verschossen"}));
      ev.sort((a, b) => mn(a.min) - mn(b.min));
      const zeile = e => { const txt = `<div class="sbv2-tx"><b>${esc(e.n)}</b><small>${esc(e.was)}</small></div>`;
        const mi = `<span class="sbv2-mi${e.tor ? " t" : ""}">${e.k ? `<i class="sbv2-k ${e.k}"></i>` : ""}${esc(e.min)}'</span>`;
        return `<div class="sbv2-ev">${e.seite === "heim" ? txt.replace('sbv2-tx"', 'sbv2-tx r"') : "<div></div>"}${mi}${e.seite === "gast" ? txt : "<div></div>"}</div>`; };
      const g1 = gelbVon("heim"), g2 = gelbVon("gast");
      if (ev.length || g1.length || g2.length) {
        const vor = ev.filter(e => halb(e.min)), nach = ev.filter(e => !halb(e.min));
        h += `<section class="sbv2-sec">${kap("Key Highlights")}<div class="sbv2-box">${vor.map(zeile).join("")}<div class="sbv2-hz"><i></i><span>HALBZEIT ${hz[0]}:${hz[1]}</span><i></i></div>${nach.map(zeile).join("")}`
          + (g1.length || g2.length ? `<div class="sbv2-ln"></div><div class="sbv2-ev sbv2-ge"><div class="sbv2-tx r">${esc(g1.join(", ")) || "–"}</div><span class="sbv2-gl"><i class="sbv2-k g"></i>Gelb</span><div class="sbv2-tx">${esc(g2.join(", ")) || "–"}</div></div>` : "") + `</div></section>`; }
      // Das zählt für dein Team
      const no = (AS && AS.no) || {}, kz = kurzEinsatz(p), mitNote = Object.entries(no).map(([id, n]) => [spById(id), n]).filter(([x]) => x && (x.k === p.heim_k || x.k === p.gast_k) && !kz.has(nk(x.n)));
      const schw = mitNote.slice().sort((a, b) => a[1] - b[1])[0];
      const zl = [];
      rot.forEach(c => { const s = schw && nk(schw[0].n) === nk(c.n) && sk(c.seite) === schw[0].k;
        zl.push(["r", `${nachN(c.n)} fehlt wohl im nächsten Spiel`, `${c.art === "gelbrot" ? "Gelb-Rot" : "Rot"} in der ${c.min}. Minute, Sperre wahrscheinlich.${s ? ` Dazu die schwächste Startelf-Note (${dez(schw[1])}).` : ""}`]); });
      vs.forEach(c => zl.push(["fe", `${nachN(c.n)} vergibt vom Punkt`, `Elfmeter verschossen in der ${c.min}. Minute.`]));
      const w = (AS && AS.w) || p.stats || {};
      if (w.xg) [[p.heim, 0], [p.gast, 1]].forEach(([n, i]) => { const t = Number(p.ergebnis[i]), dd = t - w.xg[i];
        if (dd >= 1.5) zl.push(["xg", `${KNAME[i ? p.gast_k : p.heim_k] || n} traf über den Erwartungen`, `${t} Tore bei ${dez(w.xg[i], 2)} xG. So effizient bleibt kaum ein Team, daraus folgt für das nächste Spiel nicht automatisch so viel Offensive.`]);
        if (dd <= -1.5) zl.push(["xg", `${KNAME[i ? p.gast_k : p.heim_k] || n} ließ Chancen liegen`, `${dez(w.xg[i], 2)} xG, aber nur ${t} ${t === 1 ? "Tor" : "Tore"}. Das spricht eher für mehr Tore im nächsten Spiel.`]); });
      if (m.kickbase) zl.push(["kb", "Für Kickbase", m.kickbase]);
      const ico = t => t === "r" ? `<i class="sbv2-k r gr2"></i>` : t === "fe" ? `<svg aria-hidden="true" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="8"></circle><path d="M6 6l12 12"></path></svg>`
        : t === "xg" ? `<svg aria-hidden="true" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 19h16M7 16V9M12 16V5M17 16v-4"></path></svg>`
        : `<svg aria-hidden="true" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 3l2.6 5.6 6 .7-4.5 4.1 1.2 6L12 16.4 6.7 19.4l1.2-6L3.4 9.3l6-.7z"></path></svg>`;
      if (zl.length) h += `<section class="sbv2-sec">${kap("Das zählt für dein Team")}${zl.map(([t, a, b]) => `<div class="sbv2-z"><span class="sbv2-zi">${ico(t)}</span><div><b>${esc(a)}</b><p>${esc(b)}</p></div></div>`).join("")}</section>`;
      // Statistik
      const Z = [["xg", "Expected Goals", 2], ["sch", "Torschüsse"], ["tor", "Schüsse aufs Tor"], ["bes", "Ballbesitz", 0, " %"], ["eck", "Ecken"]];
      const zs = Z.filter(z => w[z[0]] && w[z[0]][0] != null && w[z[0]][1] != null).map(([k, t, dz, e]) => { const [a, b] = w[k], s = a + b || 1, f = x => (dz ? dez(x, dz) : Math.round(x)) + (e || "");
        return `<div class="sbv2-sb"><div><span${a > b ? ' class="v"' : ""}>${f(a)}</span><small>${t}</small><span${b > a ? ' class="v"' : ""}>${f(b)}</span></div><p><i style="width:${a / s * 100}%"></i><i></i></p></div>`; }).join("");
      if (zs) h += `<section class="sbv2-sec">${kap("Statistik")}<div class="sbv2-sbk"><span>${logo(p.heim_k, 16)}${esc(KNAME[p.heim_k] || p.heim)}</span><span>${esc(KNAME[p.gast_k] || p.gast)}${logo(p.gast_k, 16)}</span></div>${zs}${AS ? "" : '<p class="af-st" style="margin:0">Stand Abpfiff, Noten folgen.</p>'}</section>`;
      // Beste Noten im Vergleich: Top 3 je Team, dazu die schwächste Note
      if (mitNote.length) {
        const top = [p.heim_k, p.gast_k].flatMap(k => mitNote.filter(([x]) => x.k === k).sort((a, b) => b[1] - a[1]).slice(0, 3)).sort((a, b) => b[1] - a[1]);
        const L = top.concat(schw && !top.includes(schw) ? [schw] : []), best = top[0];
        h += `<section class="sbv2-sec">${kap("Beste Noten im Vergleich")}<div class="sbv2-nv">${L.map(r => { const [x, n] = r, f = r === best ? "#F5B041" : r === schw && !top.includes(schw) ? "#5C6B86" : "#8FB0FF";
          return `<button class="sbv2-nr" data-profil="${esc(x.id)}"><span class="n">${esc(nachN(x.n))}</span><span class="k">${esc(x.k)}</span><span class="b"><i style="width:${Math.max(0, Math.min(10, n)) * 10}%;background:${f}"></i></span><b>${dez(n)}</b></button>`; }).join("")}</div><p class="sbv2-fn">Top 3 je Team${schw && !top.includes(schw) ? " und die schwächste Note" : ""}. Nur Einsätze ab 46 Minuten.</p></section>`; }
      // Aufstellungen
      h += `<section class="sbv2-sec ber-auf">${kap("Aufstellungen und Noten")}${teamSchalter(p)}<button class="btn-prog" data-game="${esc(p.id)}" data-tabspiel="1">Zum Spiel ›</button></section>`;
      return h + `</div>`;
    } finally { AFNOTEN = null; AFBEST = null; SPIELP = vorS; }
  }
'''

CSS = r'''
/* Spielbericht Version 2 (Finn 17.11.2026) */
.sbv2{display:grid;gap:18px}
.sbv2-kz{display:flex;justify-content:space-between;font:600 11px var(--f-body);letter-spacing:1.4px;color:var(--muted)}
.sbv2-end{background:var(--card);border-radius:16px;padding:20px 12px 16px;display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:8px}
.sbv2-tm{display:flex;flex-direction:column;align-items:center;gap:8px;background:none;border:0;color:var(--ink);font:600 14px var(--f-body);padding:0;cursor:pointer;min-height:44px}
.sbv2-wp{width:52px;height:52px;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center}
.sbv2-st{display:flex;flex-direction:column;align-items:center;gap:2px}
.sbv2-st b{font:800 76px/1 var(--f-display);letter-spacing:1px}
.sbv2-st span{font-size:12px;color:var(--muted)}
.sbv2-sds{background:var(--accent);border-radius:16px;padding:16px;display:grid;grid-template-columns:auto minmax(0,1fr);align-items:center;gap:16px}
.sbv2-big{font:800 72px/.9 var(--f-display)}
.sbv2-sds > div{display:grid;gap:6px;justify-items:start}
.sbv2-l{font:600 11px var(--f-body);letter-spacing:1.4px}
.sbv2-nm{font:700 20px/1.15 var(--f-body);color:#fff;background:none;border:0;padding:0;text-align:left;cursor:pointer}
.sbv2-v{font-size:13px}
.sbv2-ch{display:flex;gap:6px;flex-wrap:wrap}
.sbv2-ch span{background:var(--bg);border-radius:999px;padding:4px 10px;font-size:12px;font-weight:600;display:inline-flex;align-items:center;gap:5px}
.sbv2-k{width:8px;height:11px;border-radius:2px;display:inline-block}
.sbv2-k.g{background:#F5B041}.sbv2-k.r{background:#E5484D}.sbv2-k.gr{background:linear-gradient(135deg,#F5B041 50%,#E5484D 50%)}
.sbv2-k.gr2{width:14px;height:20px;border-radius:3px}
.sbv2-sec{display:grid;gap:10px}
.sbv2-box{background:var(--card);border-radius:16px;padding:14px 12px;display:grid;gap:12px}
.sbv2-ev{display:grid;grid-template-columns:minmax(0,1fr) 58px minmax(0,1fr);align-items:center;gap:8px}
.sbv2-tx{display:grid;gap:2px}.sbv2-tx.r{text-align:right}
.sbv2-tx b{font-size:15px}.sbv2-tx small{font-size:12px;color:var(--muted)}
.sbv2-mi{background:var(--bg);border:1px solid var(--line);border-radius:999px;padding:4px 0;display:flex;align-items:center;justify-content:center;gap:5px;font-size:13px;font-weight:700}
.sbv2-mi.t{background:var(--accent);border-color:var(--accent)}
.sbv2-hz{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:10px}
.sbv2-hz i{height:1px;background:var(--line)}
.sbv2-hz span{font-size:11px;font-weight:600;letter-spacing:1.2px;color:var(--muted)}
.sbv2-ln{height:1px;background:var(--line)}
.sbv2-ge{align-items:start;font-size:13px;line-height:1.5}
.sbv2-gl{display:flex;align-items:center;justify-content:center;gap:5px;color:var(--muted);font-size:12px;font-weight:600}
.sbv2-z{background:var(--card);border-radius:14px;padding:12px;display:grid;grid-template-columns:44px minmax(0,1fr);gap:12px;align-items:center}
.sbv2-zi{width:44px;height:44px;border-radius:12px;background:var(--bg);display:flex;align-items:center;justify-content:center;color:var(--ink)}
.sbv2-z b{font-size:15px}.sbv2-z p{margin:3px 0 0;font-size:13px;color:var(--muted);line-height:1.4}
.sbv2-sbk{display:flex;justify-content:space-between;font-size:12px;color:var(--muted)}
.sbv2-sbk span{display:inline-flex;align-items:center;gap:6px}
.sbv2-sb{display:grid;gap:6px}
.sbv2-sb div{display:grid;grid-template-columns:52px 1fr 52px;font-size:14px;font-weight:600}
.sbv2-sb div span:last-child{text-align:right}.sbv2-sb .v{font-weight:800}
.sbv2-sb small{text-align:center;color:var(--muted);font-size:12px;font-weight:400}
.sbv2-sb p{margin:0;display:flex;gap:3px;height:6px}
.sbv2-sb p i{display:block;border-radius:3px;background:var(--ink)}.sbv2-sb p i:last-child{flex:1;background:var(--accent)}
.sbv2-nv{display:grid;gap:4px}
.sbv2-nr{display:grid;grid-template-columns:96px 36px minmax(0,1fr) 32px;align-items:center;gap:8px;background:none;border:0;color:var(--ink);font:14px var(--f-body);padding:4px 0;min-height:32px;cursor:pointer;text-align:left}
.sbv2-nr .n{font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.sbv2-nr .k{font-size:11px;color:var(--muted)}
.sbv2-nr .b{height:8px;background:var(--card);border-radius:4px;overflow:hidden}.sbv2-nr .b i{display:block;height:8px;border-radius:4px}
.sbv2-nr b{text-align:right}
.sbv2-fn{margin:0;font-size:12px;color:var(--muted)}
'''

ERS = [
  ("  function punktArtikel(m){", JS + "  function punktArtikel(m){"),
  ("    const kopf = sc ? scArtikel(m) : auf\n", "    const v2 = !sc && !auf ? sbV2(m) : \"\";\n    const kopf = v2 ? v2 : sc ? scArtikel(m) : auf\n"),
  ('<div id="art-sv">${auf || sc ? "" : artVerlauf(m)}</div><div id="art-eo">${stdA ? stdHtml() : (auf || sc ? "" : einordnung(m)) || kbBox(m.kickbase)}</div><div id="pf-karte">${auf || sc ? "" : profilKarte(m)}</div>',
   '<div id="art-sv">${auf || sc || v2 ? "" : artVerlauf(m)}</div><div id="art-eo">${v2 ? "" : stdA ? stdHtml() : (auf || sc ? "" : einordnung(m)) || kbBox(m.kickbase)}</div><div id="pf-karte">${auf || sc || v2 ? "" : profilKarte(m)}</div>'),
  ("/* Design wie die iOS-App (ab Version 0.7)", CSS + "\n/* Design wie die iOS-App (ab Version 0.7)"),
]

def main(a, b):
    s = open(a, encoding="utf-8").read()
    for alt, neu in ERS:
        n = s.count(alt)
        if n != 1: sys.exit(f"Ersetzung passt {n}-mal statt einmal: {alt[:60]!r}")
        s = s.replace(alt, neu)
    open(b, "w", encoding="utf-8").write(s)
    print("ok", len(ERS), "Ersetzungen")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
