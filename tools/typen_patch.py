# Spielertypen und "Die Besten" nach Position (Finn 05.11.2026 abends)
# Typ = Rolle in Worten (z. B. defensive Sechserin, Ballverteilerin, Box-to-Box), aus Rängen pro 90 gegen die eigene Positionsgruppe (ab 270 Minuten).
# Die Besten: Gesamtwert = Schnitt der Ränge in den Werten der Position, Statistik mit Reitern TW, IV, RV, LV, DM, ZM, OM, LM, RM, ST.
import sys
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
JS = r'''
  // ---------------- Spielertypen und Die Besten (Finn 05.11.2026)
  const FGRP = x => { const t = String(((x.slots || [])[0] || [])[2] || ""), g = PGRP(x); if (!g) return null;
    if (g === "AV") return /^Links|links$/.test(t) ? "LV" : "RV";
    if (g === "FL") return /links/.test(t) ? "LM" : "RM";
    if (g === "ZM") return /Zehnerin|Offensives/.test(t) ? "OM" : "ZM";
    return g; };
  const FLAB = {TW: ["Torhüterinnen", "Tor"], IV: ["Innenverteidigerinnen", "IV"], RV: ["Rechtsverteidigerinnen", "RV"], LV: ["Linksverteidigerinnen", "LV"], DM: ["Sechserinnen", "DM"],
    ZM: ["zentralen Mittelfeldspielerinnen", "ZM"], OM: ["Zehnerinnen", "OM"], LM: ["linken Außen", "LM"], RM: ["rechten Außen", "RM"], ST: ["Stürmerinnen", "ST"]};
  const TMIN = x => (x.spiele || []).reduce((a, e) => a + (e.min || 0), 0);
  const TMET = {
    abw: ["Abwehrarbeit", x => { const q = (afSp(x.id) || {}).abw; return q && q[3] ? (q[0] + q[1] + q[2]) / q[3] * 90 : null; }],
    zk: ["Zweikämpfen", x => (x.stat || {}).zk_ges && TMIN(x) ? x.stat.zk_w / TMIN(x) * 90 : null],
    pass: ["Pässen", x => (x.stat || {}).p_ges && TMIN(x) ? x.stat.p_ok / TMIN(x) * 90 : null],
    bk: ["Ballkontakten", x => (x.stat || {}).bk && TMIN(x) ? x.stat.bk / TMIN(x) * 90 : null],
    kp: ["Schlüsselpässen", x => (afSp(x.id) || {}).kp90 ?? null],
    sch: ["Torschüssen", x => (x.stat || {}).sch != null && TMIN(x) ? x.stat.sch / TMIN(x) * 90 : null],
    drib: ["Dribblings", x => { const d = (afSp(x.id) || {}).drib; return d && TMIN(x) ? d[0] / TMIN(x) * 90 : null; }],
    tb: ["Torbeteiligungen", x => TMIN(x) ? (x.spiele || []).reduce((a, e) => a + (e.tore || []).length + (e.vorl || 0), 0) / TMIN(x) * 90 : null],
    par: ["Paraden", x => { const a = afSp(x.id) || {}; return a.parsp ? a.par / a.parsp : null; }],
    zn: ["Spielen zu null", x => { const st = (x.spiele || []).filter(e => e.art === "S"); if (!st.length) return null;
      return st.filter(e => { const [a, b] = String(e.erg || "").split(":").map(Number); return !isNaN(a) && (e.ha === "H" ? b : a) === 0; }).length / st.length; }],
    gr: ["Größe", x => (afSp(x.id) || {}).gr || null]};
  const TSET = {TW: ["par", "zn", "pass", "bk"], IV: ["zk", "abw", "pass", "bk", "sch", "tb"], AV: ["abw", "zk", "kp", "drib", "pass", "tb"], DM: ["abw", "zk", "pass", "bk", "kp", "sch"],
    ZM: ["kp", "pass", "bk", "sch", "tb", "abw"], FL: ["sch", "tb", "drib", "kp", "zk", "bk"], ST: ["sch", "tb", "drib", "kp", "zk", "bk"]};
  let TCACHE = null;
  function typDaten(){
    if (TCACHE || !SPN) return TCACHE || {};
    const L = (SPN.spielerinnen || []).filter(x => PGRP(x) && TMIN(x) >= 270), out = {};
    const gruppen = {}; L.forEach(x => (gruppen[PGRP(x)] = gruppen[PGRP(x)] || []).push(x));
    Object.entries(gruppen).forEach(([g, P]) => { if (P.length < 8) return;
      const keys = TSET[g].concat(g === "IV" || g === "ST" ? ["gr"] : []), V = {};
      keys.forEach(k => V[k] = P.map(TMET[k][1]).filter(v => v != null));
      P.forEach(x => { const p = {};
        keys.forEach(k => { const w = TMET[k][1](x), v = V[k]; if (w == null || v.length < 8) return; const eq = v.filter(y => Math.abs(y - w) < 1e-9).length;
          p[k] = Math.round((v.filter(y => y < w - 1e-9).length + (eq - 1) / 2) / Math.max(1, v.length - 1) * 100); });
        const ks = TSET[g].filter(k => p[k] != null); if (ks.length < Math.min(4, TSET[g].length)) return;
        out[x.id] = {g, fg: FGRP(x), p, wert: Math.round(ks.reduce((a, k) => a + p[k], 0) / ks.length), typ: typBestimmen(g, p)}; }); });
    return TCACHE = out;
  }
  function typBestimmen(g, p){
    const m = (...k) => { const v = k.map(x => p[x]).filter(x => x != null); return v.length ? v.reduce((a, b) => a + b, 0) / v.length : 0; };
    if (g === "TW") { const par = m("par"), auf = m("pass", "bk"), zn = m("zn"); return zn >= 65 && zn >= par ? ["sicherer Rückhalt", "viele Spiele zu null"] : auf >= par && auf >= 55 ? ["mitspielende Torhüterin", "viel am Ball, spielt mit"] : ["Paraden-Torhüterin", "hat viel zu halten und hält viel"]; }
    if (g === "IV") { const bau = m("pass", "bk"), def = m("zk", "abw"), gr = p.gr;
      return bau >= def + 10 ? ["Aufbauspielerin", "eröffnet das Spiel von hinten"] : def >= 60 && gr != null && gr >= 60 ? ["groß und zweikampfstark", "gewinnt viele Duelle"] : def > bau ? ["Zweikämpferin", "stark gegen den Ball"] : ["ausgewogene Innenverteidigerin", "solide im Aufbau und im Zweikampf"]; }
    if (g === "AV") { const off = m("kp", "drib", "tb"), def = m("abw", "zk");
      return Math.abs(off - def) < 12 ? ["ausgewogene Außenverteidigerin", "vorne und hinten gefragt"] : off > def ? ["offensive Außenverteidigerin", "schaltet sich viel nach vorne ein"] : ["defensive Außenverteidigerin", "sichert hinten ab"]; }
    if (g === "DM") { const def = m("abw", "zk"), bau = m("pass", "bk"), off = m("kp", "sch");
      return def >= 55 && off >= 55 ? ["Box-to-Box", "hinten und vorne dabei"] : bau >= def && bau >= off ? ["Ballverteilerin", "viele Ballkontakte und Pässe"] : def >= off ? ["defensive Sechserin", "räumt vor der Abwehr ab"] : ["offensive Sechserin", "sucht den Weg nach vorne"]; }
    if (g === "ZM") { const kp = m("kp"), bau = m("pass", "bk"), tor = m("sch", "tb"), abw = m("abw");
      return abw >= 55 && tor >= 55 ? ["Box-to-Box", "hinten und vorne dabei"] : kp >= Math.max(bau, tor) ? ["Spielmacherin", "bereitet Chancen vor"] : tor >= bau ? ["torgefährliche Mittelfeldspielerin", "sucht selbst den Abschluss"] : ["Ballverteilerin", "viele Ballkontakte und Pässe"]; }
    if (g === "FL") { const dr = m("drib"), kp = m("kp"), tor = m("sch", "tb"), def = m("zk");
      return dr >= Math.max(kp, tor) && dr >= 55 ? ["Dribblerin", "geht ins Eins-gegen-eins"] : kp >= tor && kp >= 55 ? ["Vorbereiterin", "spielt die letzten Pässe"] : tor >= 55 ? ["Torjägerin von außen", "zieht selbst ab"] : def >= 55 ? ["arbeitet nach hinten mit", "viele Zweikämpfe auf der Außenbahn"] : ["Außenspielerin", "ohne klaren Schwerpunkt"]; }
    if (g === "ST") { const dr = m("drib"), kp = m("kp"), tor = m("sch", "tb"), gr = p.gr, wucht = m("zk", "bk");
      return gr != null && gr >= 65 && dr < 50 && wucht >= 45 ? ["Zielspielerin", "groß, hält Bälle fest und verteilt"] : dr >= 65 && dr >= tor ? ["Dribblerin", "kommt über das Eins-gegen-eins"] : tor >= 60 ? ["Vollstreckerin", "lebt vom Abschluss"] : kp >= 60 ? ["mitspielende Stürmerin", "legt viel für andere auf"] : ["Mittelstürmerin", "ohne klaren Schwerpunkt"]; }
    return ["", ""];
  }
  function typZeile(s){
    const d = typDaten()[s.id]; if (!d || !d.typ[0]) { const mi = TMIN(s); return PGRP(s) && s.pos && mi < 270 ? `<div class="typ"><span class="typ-k">SPIELERTYP</span><span>Den Typ bestimmen wir ab 270 Minuten, sie hat erst ${mi}.</span></div>` : ""; }
    const st = TSET[d.g].filter(k => d.p[k] != null).sort((a, b) => d.p[b] - d.p[a]), gut = st.filter(k => d.p[k] >= 60).slice(0, 2), sw = st.filter(k => d.p[k] < 35).slice(-1);
    const L = Object.entries(typDaten()).filter(([, x]) => x.fg === d.fg).sort((a, b) => b[1].wert - a[1].wert), pl = 1 + L.findIndex(([id]) => id === s.id);
    return `<div class="typ"><span class="typ-k">SPIELERTYP</span><b>${esc(d.typ[0][0].toUpperCase() + d.typ[0].slice(1))}</b><span>${esc(d.typ[1])}${gut.length ? `. Stark in ${gut.map(k => TMET[k][0]).join(" und ")}` : ""}${sw.length ? `, weniger in ${TMET[sw[0]][0]}` : ""}.</span>
      <button class="typ-l" data-beste="${d.fg}">Platz ${pl} von ${L.length} ${esc(FLAB[d.fg][0])} · Gesamtwert ${d.wert} ›</button></div>`;
  }
  let BESTE = "DM";
  function besteSektion(){
    const T = typDaten(), pos = Object.keys(FLAB).filter(f => Object.values(T).some(x => x.fg === f)); if (!pos.length) return "";
    if (!pos.includes(BESTE)) BESTE = pos[0];
    const L = Object.entries(T).filter(([, x]) => x.fg === BESTE).sort((a, b) => b[1].wert - a[1].wert).slice(0, 10).map(([id, x]) => [spById(id), x]).filter(([s]) => s);
    const g = (L[0] || [])[1] ? L[0][1].g : "DM";
    return `<section class="stk" id="st-beste"><div class="stk-k"><h2>Die Besten</h2><small>Gesamtwert = Schnitt der Ränge pro 90 Minuten in ${TSET[g].map(k => TMET[k][0]).join(", ").replace(/, ([^,]*)$/, " und $1")}, ab 270 Minuten. 100 = überall Bestwert.</small></div>
      <div class="bst-t">${pos.map(f => `<button data-beste="${f}"${f === BESTE ? ' class="an"' : ""}>${FLAB[f][1]}</button>`).join("")}</div>
      ${L.map(([s, x], i) => { const st = TSET[x.g].filter(k => x.p[k] != null).sort((a, b) => x.p[b] - x.p[a]).slice(0, 2);
        return `<button class="bst" data-profil="${esc(s.id)}"><span class="pl">${i + 1}</span>${pfFoto(s, 34, 34, 17)}<span class="nm"><b>${esc(s.n)}</b><small>${esc(kname(s.k))} · ${esc(x.typ[0])}</small></span><span class="sc" style="color:${x.wert >= 67 ? "#4ADE80" : x.wert >= 45 ? "#F5C26B" : "#FF8A8A"}">${x.wert}</span><span class="st">stark in ${st.map(k => TMET[k][0]).join(" und ")}</span></button>`; }).join("")}</section>`;
  }
  document.addEventListener("click", e => { const b = e.target.closest && e.target.closest("[data-beste]"); if (!b) return; e.preventDefault(); e.stopPropagation();
    BESTE = b.dataset.beste;
    if (VIEW_STAT === "statistik" && BACK === "stat") { const y = window.scrollY, el = document.getElementById("st-beste"); if (el) { el.outerHTML = besteSektion(); window.scrollTo(0, y); return; } }
    const z = document.createElement("button"); z.dataset.statview = "statistik"; z.hidden = true; document.body.appendChild(z); z.click(); z.remove();
    setTimeout(() => { const el = document.getElementById("st-beste"); if (el) el.scrollIntoView({block: "start"}); }, 50); }, true);
'''
CSS = """
.typ{display:grid;gap:3px;background:rgba(143,176,255,.08);border-radius:12px;padding:10px 12px;margin-bottom:4px}.typ-k{font:700 10px var(--f-mono);letter-spacing:1px;color:#8FB0FF}
.typ b{font-family:var(--f-display);font-size:21px;font-weight:800;line-height:1.05}.typ span{font-size:13px;line-height:1.4;color:#C9D3E2}.typ-l{justify-self:start;background:none;border:0;padding:2px 0 0;color:#8FB0FF;font:inherit;font-size:12.5px;font-weight:600;cursor:pointer}
.bst-t{display:flex;flex-wrap:wrap;gap:5px;margin:2px 0 6px}.bst-t button{border:0;background:rgba(255,255,255,.07);color:#fff;font:inherit;font-size:12.5px;font-weight:600;border-radius:99px;padding:5px 11px;cursor:pointer}.bst-t button.an{background:#2F5BFF}
.bst{display:grid;grid-template-columns:18px 34px minmax(0,1fr) auto;gap:2px 9px;align-items:center;width:100%;text-align:left;background:none;border:0;border-top:1px solid rgba(255,255,255,.06);padding:8px 0;color:inherit;font:inherit;cursor:pointer}
.bst .pl{font-weight:800;color:#8FB0FF}.bst .nm b{display:block;font-size:13.5px}.bst .nm small{font-size:11px;color:var(--muted)}.bst .sc{font:800 20px var(--f-display)}.bst .st{grid-column:3/5;font-size:11px;color:#A9B4C6}
"""
def patch(s):
    s = rep(s, """  let ROH = 0; const ab = n => ROH ? 0 : n;""", """  let ROH = 0; const ab = n => ROH ? 0 : n;""" + JS)
    s = rep(s, """.ww-netz{width:100%;max-width:360px;justify-self:center;display:block;overflow:visible}""", """.ww-netz{width:100%;max-width:360px;justify-self:center;display:block;overflow:visible}""" + CSS)
    s = rep(s, """        h += `<section class="pf-box">${kap("Weitere Werte")}${netz}${kacheln}""", """        h += `<section class="pf-box">${kap("Weitere Werte")}${typZeile(s)}${netz}${kacheln}""")
    s = rep(s, """        <div class="st-chips">${STKAT.map(([k, t]) => `<button data-stsprung="${k}">${t}</button>`).join("")}""", """        <div class="st-chips"><button data-stsprung="beste">Die Besten</button>${STKAT.map(([k, t]) => `<button data-stsprung="${k}">${t}</button>`).join("")}""")
    s = rep(s, """      for (const [k, t, e] of STKAT) {""", """      h += besteSektion();
      for (const [k, t, e] of STKAT) {""")
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
