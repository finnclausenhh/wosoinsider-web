"""Spielstile (Finn 05.11.2026): Titel wie die PlayStyles in EA FC, aus echten Liga-Werten.
Vergabe nach Größe des Vergleichsfelds (nur ab 270 Minuten): ab 100 die besten 10, ab 30 die besten 10 %, bei 10 bis 29 die besten 3, darunter nur Platz 1.
Platz 1 allein bekommt das Plus (Spielstil+). Gleichstände, die mehr Spielerinnen teilen als Plätze vergeben werden, zählen nicht.
Dazu im Torhüterinnen-Profil die Elfmeter der letzten drei Saisons (apifootball.json elf_tw).
Nach tools/af_r11.py und af_r11b.py (fbl-daten) anwenden."""
import sys
def rep(s, old, new):
    n = s.count(old); assert n == 1, (old[:90], n); return s.replace(old, new)

JS = r'''  // Spielstile (Finn 05.11.2026): Titel aus Liga-Werten, Plus nur für Platz 1
  let STILE = null;
  const stCut = n => n >= 100 ? 10 : n >= 30 ? Math.max(3, Math.round(n * .1)) : n >= 10 ? 3 : 1;
  const stMin = x => (x.spiele || []).reduce((a, e) => a + (e.min || 0), 0);
  const stSum = (x, f) => (x.spiele || []).reduce((a, e) => a + f(e), 0);
  const stGegen = e => { const [a, b] = String(e.erg || "").split(":").map(Number); return isNaN(a) ? null : (e.ha === "H" ? b : a); };
  const stElf = x => { const t = ((AF && AF.elf) || []).filter(e => e.k === x.k && normS(nachN(e.n)) === normS(nachN(x.n))).reduce((a, e) => [a[0] + e.t, a[1] + e.v], [0, 0]);
    Object.values((AF && AF.elf_vorsaison) || {}).forEach(l => l.forEach(e => { if (normS(e[0]) === normS(x.n)) { t[0] += e[1]; t[1] += e[2]; } })); return t; };
  // [Name, Wert, Vergleichsfeld (pos | feld | tw), Mindestwert, Beschreibung]
  const STIL_DEF = [
    ["Torjägerin", x => stSum(x, e => (e.tore || []).length), "feld", 3, "Tore"],
    ["Vorlagengeberin", x => stSum(x, e => e.vorl || 0), "feld", 3, "Vorlagen"],
    ["Ideengeberin", x => { const a = afSp(x.id); return a && a.kp90 != null && stMin(x) >= 270 ? a.kp90 : null; }, "pos", .5, "Schlüsselpässe pro 90 Minuten"],
    ["Dauerfeuer", x => (x.stat || {}).sch != null && stMin(x) >= 270 ? x.stat.sch / stMin(x) * 90 : null, "pos", 1, "Torschüsse pro 90 Minuten"],
    ["Dribbelkünstlerin", x => { const d = (afSp(x.id) || {}).drib; return d && d[1] >= 10 ? d[0] / d[1] : null; }, "pos", 0, "erfolgreiche Dribblings"],
    ["Zweikampfmonster", x => (x.stat || {}).zk_ges >= 20 ? x.stat.zk_w / x.stat.zk_ges : null, "pos", 0, "gewonnene Zweikämpfe"],
    ["Passmaschine", x => (x.stat || {}).p_ges >= 100 ? x.stat.p_ok / x.stat.p_ges : null, "pos", 0, "angekommene Pässe"],
    ["Fair Play", x => (x.stat || {}).fouls != null && stMin(x) >= 540 ? -x.stat.fouls / stMin(x) * 90 : null, "pos", -99, "wenigste Fouls pro 90 Minuten"],
    ["Paradenkönigin", x => { const a = afSp(x.id); return a && a.parsp >= 3 ? a.par / a.parsp : null; }, "tw", 0, "Paraden pro Spiel"],
    ["Weiße Weste", x => stSum(x, e => e.art === "S" && stGegen(e) === 0 ? 1 : 0), "tw", 2, "Spiele zu null"],
    ["Elfmeterkillerin", x => { const e = AF && AF.elf_tw && AF.elf_tw[x.id]; return e && e[0] >= 4 ? e[1] / e[0] : null; }, "tw", .01, "nicht verwandelte Elfmeter seit " + (((AF && AF.elf_tw_info) || {}).saisons || [""])[0], {ohneMin: 1, mindestN: 5}]];
  function stileAlle(){
    if (STILE || !SPN) return STILE || {};
    const L = SPN.spielerinnen || [], out = {}, add = (id, x) => (out[id] = out[id] || []).push(x);
    STIL_DEF.forEach(([name, f, feld, minW, was, opt]) => { opt = opt || {};
      const gruppen = feld === "feld" ? {feld: L.filter(x => x.pos !== "TW")} : feld === "tw" ? {tw: L.filter(x => x.pos === "TW")} : L.reduce((g, x) => { if (x.pos !== "TW") (g[x.pos] = g[x.pos] || []).push(x); return g; }, {});
      Object.entries(gruppen).forEach(([gk, peers]) => {
        const v = peers.filter(x => opt.ohneMin || stMin(x) >= 270).map(x => [x, f(x)]).filter(p => p[1] != null); if (v.length < (opt.mindestN || 8)) return;
        const n = v.length, cut = stCut(n), P = feld === "feld" ? "Feldspielerinnen" : feld === "tw" ? "Torhüterinnen" : (PLURAL[gk] || "Spielerinnen");
        v.forEach(([x, w]) => { if (w < minW) return; const platz = 1 + v.filter(p => p[1] > w + 1e-9).length, eq = v.filter(p => Math.abs(p[1] - w) < 1e-9).length;
          if (platz > cut || eq > cut) return;
          add(x.id, {t: name, plus: platz === 1 && eq === 1, info: platz === 1 && eq === 1 ? `Bestwert aller ${n} ${P}` : `Platz ${platz} von ${n} ${P}`, was}); }); }); });
    L.forEach(x => { const [t, v] = stElf(x); if (t >= 3 && v === 0) add(x.id, {t: "Eiskalt vom Punkt", plus: t >= 8, info: `${t} von ${t} Elfmetern verwandelt (diese und letzte Saison)`, was: "Elfmeter"}); });
    ((IN && IN.standards) || []).forEach(st => [["ecken", "Ecken"], ["fs", "Freistöße"]].forEach(([key, lbl]) => { const e = (st[key] || [])[0]; if (!e || Number(e[1]) < 3) return;
      const x = L.find(y => y.k === st.k && normS(nachN(y.n)) === normS(nachN(e[0]))); if (x && !(out[x.id] || []).some(z => z.t === "Standardspezialistin")) add(x.id, {t: "Standardspezialistin", plus: false, info: `schießt bei ${kname(st.k)} die ${lbl}`, was: "Standards"}); }));
    Object.values(out).forEach(l => l.sort((a, b) => b.plus - a.plus));
    return STILE = out;
  }
  window.WI_STILE = () => stileAlle();
  const stChip = (x, klein) => `<span class="stl${x.plus ? " plus" : ""}${klein ? " k" : ""}">${esc(x.t)}${x.plus ? "<sup>+</sup>" : ""}</span>`;
  function stilBox(s){
    const l = stileAlle()[s.id] || []; if (!l.length) return "";
    return `<section class="pf-box">${kap("Spielstile")}<div class="stl-l">${l.map(x => `<div>${stChip(x)}<small>${esc(x.info)}${x.was && !/Elfmetern|schießt/.test(x.info) ? "<br>" + esc(x.was) : ""}</small></div>`).join("")}</div><p class="af-st">Titel aus den echten Liga-Werten. Mit Plus nur die Beste der Liga. Vergeben je nach Vergleichsfeld: an die besten 10 (ab 100 Spielerinnen), die besten 10 % (ab 30), die besten 3 (ab 10), sonst nur Platz 1. Gezählt wird ab 270 Minuten.</p></section>`;
  }
  const stilKader = s => { const l = (stileAlle()[s.id] || []).slice(0, 2); return l.length ? `<span class="stl-z">${l.map(x => stChip(x, true)).join("")}</span>` : ""; };
'''

CSS = '''
/* Spielstile (05.11.2026) */
.stl{display:inline-flex;align-items:center;gap:1px;font:700 11px var(--f-mono);letter-spacing:.02em;color:#C9D3E2;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.16);border-radius:999px;padding:3px 9px;white-space:nowrap}
.stl.plus{color:#1A1405;background:linear-gradient(135deg,#F7D774,#E0A93B);border-color:transparent}
.stl sup{font-size:9px;margin-left:1px}
.stl.k{font-size:9.5px;padding:1px 6px}
.stl-l{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.stl-l > div{display:grid;gap:4px;justify-items:start;align-content:start}.stl-l small{font-size:11.5px;line-height:1.35;color:var(--muted)}
.stl-z{display:flex;flex-wrap:wrap;gap:4px;margin-top:3px}
'''

def patch(s):
    s = rep(s, '  function profilSeite(s){', JS + '  function profilSeite(s){')
    s = rep(s, '    h += `<section class="pf-box pf-kb">${kap("Für Kickbase")}', '    h += stilBox(s);\n    h += `<section class="pf-box pf-kb">${kap("Für Kickbase")}')
    s = rep(s, '''<span class="pf-tx"><b>${esc(s.n)}</b><small>${s.nr ? "Nr. " + esc(s.nr) : ""}</small></span>${einsatz(s,''',
               '''<span class="pf-tx"><b>${esc(s.n)}</b><small>${s.nr ? "Nr. " + esc(s.nr) : ""}</small>${stilKader(s)}</span>${einsatz(s,''')
    # Elfmeter gegen die Torhüterin als Kachel in Weitere Werte
    s = rep(s, '      const gelb = sp.filter(e => e.gelb && !e.gr).length; if (gelb || st.fouls != null) {',
               '''      { const e = s.pos === "TW" && AF && AF.elf_tw && AF.elf_tw[s.id], li = AF && AF.elf_tw_info, lq = li && li.liga && li.liga[0] ? Math.round((li.liga[0] - li.liga[1]) / li.liga[0] * 100) : null;
        const er = (() => { if (!e || e[0] < 4) return null; const v = Object.values(AF.elf_tw).filter(q => q[0] >= 4).map(q => q[1] / q[0]); if (v.length < 5) return null; const w = e[1] / e[0];
          const eq = v.filter(x => Math.abs(x - w) < 1e-9).length; return {p: Math.round((v.filter(x => x < w - 1e-9).length + (eq - 1) / 2) / Math.max(1, v.length - 1) * 100), n: v.length, platz: 1 + v.filter(x => x > w + 1e-9).length, eq, w, min: Math.min(...v)}; })();
        if (e && e[0]) ww.push([`${e[1]}/${e[0]}`, `Elfmeter nicht verwandelt (${Math.round(e[1] / e[0] * 100)} %)`, `${e[0]} gegen sie seit ${(li.saisons || [""])[0]}${e[2] ? `, ${e[2]} sicher gehalten` : ""}${lq != null ? ` · Liga trifft ${lq} %` : ""}`, er]); }
      const gelb = sp.filter(e => e.gelb && !e.gr).length; if (gelb || st.fouls != null) {''')
    i = s.find("</style>", s.find("--f-display")); s = s[:i] + CSS + s[i:]
    assert "—" not in s
    return s

if __name__ == "__main__":
    for f in sys.argv[1:]:
        s = open(f, encoding="utf-8").read()
        if "function stileAlle" in s: print("schon drin", f); continue
        t = patch(s); open(f, "w", encoding="utf-8").write(t); print("stile ok", f)
