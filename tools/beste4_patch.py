import sys
# Finn 05.11.2026 22:01: Die Besten mit 4 Reitern, Gesamtwert halb Statistik halb Note, Einsatz getrennt sichtbar
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    # Gesamtwert: 50 % Statistik-Rang, 50 % Noten-Rang (Noten ab 46 Minuten, mindestens 3), beides innerhalb der eigenen Rolle
    s = rep(s, '''        const ks = TSET[g].filter(k => p[k] != null); if (ks.length < Math.min(4, TSET[g].length)) return;
        out[x.id] = {g, fg: FGRP(x), p, wert: Math.round(ks.reduce((a, k) => a + p[k], 0) / ks.length), typ: typBestimmen(g, p)}; }); });''',
'''        const ks = TSET[g].filter(k => p[k] != null); if (ks.length < Math.min(4, TSET[g].length)) return;
        const stat = ks.reduce((a, k) => a + p[k], 0) / ks.length, pn = NR[x.id];
        out[x.id] = {g, fg: FGRP(x), p, stat: Math.round(stat), pn, wert: Math.round(pn != null ? (stat + pn) / 2 : stat), ein: EIN(x), typ: typBestimmen(g, p)}; }); });''')
    s = rep(s, '''      const keys = TSET[g].concat(g === "IV" || g === "ST" ? ["gr"] : []), V = {};''',
'''      const keys = TSET[g].concat(g === "IV" || g === "ST" ? ["gr"] : []), V = {}, NR = {};
      const nv = P.map(x => [x.id, NOTE46(x)]).filter(e => e[1] != null);
      nv.forEach(([id, w]) => { const eq = nv.filter(e => Math.abs(e[1] - w) < 1e-9).length; NR[id] = Math.round((nv.filter(e => e[1] < w - 1e-9).length + (eq - 1) / 2) / Math.max(1, nv.length - 1) * 100); });''')
    s = rep(s, '''  let TCACHE = null;''', '''  let TCACHE = null;
  const NOTE46 = x => { const v = ((afSp(x.id) || {}).no || []).filter(n => n[2] >= 46); return v.length >= 3 ? v.reduce((a, n) => a + n[1], 0) / v.length : null; };
  const EIN = x => { const l = (x.spiele || []).filter(e => e.erg && String(e.erg).includes(":")); return l.length ? Math.round(TMIN(x) / (l.length * 90) * 100) : null; };
  const BTAB = {TW: ["Torhüterinnen", ["TW"]], ABW: ["Abwehr", ["IV", "AV"]], MF: ["Mittelfeld", ["DM", "ZM"]], ST: ["Sturm", ["FL", "ST"]]};
  const tabVon = g => Object.keys(BTAB).find(t => BTAB[t][1].includes(g));''')
    # Profil: Platz im Reiter
    s = rep(s, '''    const L = Object.entries(typDaten()).filter(([, x]) => x.fg === d.fg).sort((a, b) => b[1].wert - a[1].wert), pl = 1 + L.findIndex(([id]) => id === s.id);''',
'''    const tb = tabVon(d.g), L = Object.entries(typDaten()).filter(([, x]) => tabVon(x.g) === tb).sort((a, b) => b[1].wert - a[1].wert), pl = 1 + L.findIndex(([id]) => id === s.id);''')
    s = rep(s, '''<button class="typ-l" data-beste="${d.fg}">Platz ${pl} von ${L.length} ${esc(FLAB[d.fg][0])} · Gesamtwert ${d.wert} ›</button>''',
'''<button class="typ-l" data-beste="${tb}">Platz ${pl} von ${L.length} im Reiter ${esc(BTAB[tb][0])} · Gesamtwert ${d.wert} ›</button>''')
    s = rep(s, '''  let BESTE = "DM";''', '''  let BESTE = "MF";''')
    s = rep(s, '''    const T = typDaten(), pos = Object.keys(FLAB).filter(f => Object.values(T).some(x => x.fg === f)); if (!pos.length) return "";
    if (!pos.includes(BESTE)) BESTE = pos[0];
    const L = Object.entries(T).filter(([, x]) => x.fg === BESTE).sort((a, b) => b[1].wert - a[1].wert).slice(0, 10).map(([id, x]) => [spById(id), x]).filter(([s]) => s);
    const g = (L[0] || [])[1] ? L[0][1].g : "DM";
    return `<section class="stk" id="st-beste"><div class="stk-k"><h2>Die Besten</h2><small>Gesamtwert = Schnitt der Ränge pro 90 Minuten in ${TSET[g].map(k => TMET[k][0]).join(", ").replace(/, ([^,]*)$/, " und $1")}, ab 270 Minuten. 100 = überall Bestwert.</small></div>
      <div class="bst-t">${pos.map(f => `<button data-beste="${f}"${f === BESTE ? ' class="an"' : ""}>${FLAB[f][1]}</button>`).join("")}</div>''',
'''    const T = typDaten(), pos = Object.keys(BTAB).filter(t => Object.values(T).some(x => tabVon(x.g) === t)); if (!pos.length) return "";
    if (!pos.includes(BESTE)) BESTE = pos.includes(tabVon(BESTE)) ? tabVon(BESTE) : pos.includes(tabVon(PGRPfg(BESTE))) ? tabVon(PGRPfg(BESTE)) : pos[0];
    const L = Object.entries(T).filter(([, x]) => tabVon(x.g) === BESTE).sort((a, b) => b[1].wert - a[1].wert).slice(0, 10).map(([id, x]) => [spById(id), x]).filter(([s]) => s);
    return `<section class="stk" id="st-beste"><div class="stk-k"><h2>Die Besten</h2><small>Gesamtwert: halb Statistik pro 90 Minuten, halb Note von API-Football, jeweils im Vergleich mit der eigenen Rolle. 100 heißt überall vorne. Ab 270 Minuten. Rechts unten: Anteil der gespielten Ligaminuten.</small></div>
      <div class="bst-t">${pos.map(f => `<button data-beste="${f}"${f === BESTE ? ' class="an"' : ""}>${BTAB[f][0] === "Torhüterinnen" ? "Tor" : BTAB[f][0]}</button>`).join("")}</div>''')
    s = rep(s, '''<small>${esc(kname(s.k))} · <span data-typerk''', '''<small>${esc(kname(s.k))} · ${esc(FLAB[x.fg] ? FLAB[x.fg][1] : "")} · <span data-typerk''')
    s = rep(s, '''<span class="st">stark in ${st.map(k => TMET[k][0]).join(" und ")}</span></button>`; }).join("")}</section>`;''',
'''<span class="st">stark in ${st.map(k => TMET[k][0]).join(" und ")}${x.ein != null ? `<i class="bein" style="color:${x.ein >= 75 ? "#4ADE80" : x.ein >= 45 ? "#F5C26B" : "#FF8A8A"}">${x.ein} % Einsatz</i>` : ""}</span></button>`; }).join("")}</section>`;''')
    s = rep(s, '''.bst .st{grid-column:3/5;font-size:11px;color:#A9B4C6}''', '''.bst .st{grid-column:3/5;font-size:11px;color:#A9B4C6;display:flex;gap:8px}.bst .bein{margin-left:auto;font-style:normal;font-weight:700;white-space:nowrap}''')
    # alte Links mit Feingruppe (z. B. data-beste="ZM") auf den Reiter abbilden
    s = rep(s, '''  const tabVon = g => Object.keys(BTAB).find(t => BTAB[t][1].includes(g));''', '''  const tabVon = g => Object.keys(BTAB).find(t => BTAB[t][1].includes(g));
  const PGRPfg = f => ({RV: "AV", LV: "AV", OM: "ZM", LM: "FL", RM: "FL"})[f] || f;''')
    s = rep(s, '''${(afSp(s.id) || {}).avg ? `<small class="bnt">Note ${dez(afSp(s.id).avg)}</small>` : ""}''', '''${NOTE46(s) != null ? `<small class="bnt">Note ${dez(NOTE46(s))}</small>` : ""}''')
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
