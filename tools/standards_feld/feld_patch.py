import sys
import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from std_patch import rep, OLD_BLOCK_START, OLD_BLOCK_END, SCH

JS = r'''  // Standards als Spielfeld (Finn 04.11.2026, Route B): Vereinsseite und Hinweis in der Aufstellung
  const SF_STUFE = {3: "#6E9BFF", 2: "#22C55E", 1: "#F59E0B", 0: "#7F8BA0"};
  const sfGl = (a, b) => a && b && normS(nachN(a)) === normS(nachN(b));
  function sfDaten(k){
    const st = ((IN && IN.standards) || []).find(s => s.k === k) || {k}, d = (AF && AF.stdt && AF.stdt[k]) || {}, h = normS(st.hinweis || "");
    const raus = n => new RegExp(normS(nachN(n)) + "[^.]*(raus|verletzt|\\bop\\b)").test(h);
    const stand = (lst, af, sd, fd) => {
      const l = (lst || []).length ? lst.map(x => [x[0], Number(x[1]) || 1]) : ((af || []).length ? af : (fd || [])).slice(0, 2).map(x => [nachN(x[0]), 1]);
      if (!l.length) return null;
      return {n: l[0][0], b: Math.min(3, l[0][1]), alt: l.slice(1).map(x => x[0]), L: sd && sd.l ? nachN(sd.l[0]) : null, R: sd && sd.r ? nachN(sd.r[0]) : null};
    };
    const ecke = stand(st.ecken, d.ecke, d.seiten), fs = stand(st.fs, d.fs, d.fs_seiten, d.fs_direkt);
    if (fs) fs.direkt = (d.fs_direkt || []).some(x => sfGl(x[0], fs.n));
    const akt = ((AF && AF.elf) || []).filter(x => x.k === k), vs = ((AF && AF.elf_vorsaison && AF.elf_vorsaison[k]) || []);
    const il = (st.elfer || []).filter(x => !raus(x[0]));
    let elf = null;
    if (il.length) { const q = akt.find(a => sfGl(a.n, il[0][0])); elf = {n: il[0][0], b: Math.min(3, Number(il[0][1]) || 1), q: q ? [q.t, q.v] : null, alt: il.slice(1).map(x => x[0])}; }
    else {
      const a2 = akt.filter(a => !raus(a.n)).sort((a, b) => b.t - a.t || a.v - b.v), v2 = vs.filter(x => !x[3]);
      if (a2.length) elf = {n: nachN(a2[0].n), b: a2[0].t + a2[0].v >= 2 ? 2 : 1, q: [a2[0].t, a2[0].v], alt: a2.slice(1).map(a => nachN(a.n))};
      else if (v2.length) elf = {n: nachN(v2[0][0]), b: 0, vs: true, q: [v2[0][1], v2[0][2]], alt: v2.slice(1).map(x => nachN(x[0]))};
    }
    return {st, ecke, fs, elf, akt, vs};
  }
  function sfTag(k, x, pos, sub, neu){
    if (!x || !x.n) return `<div class="sf-t sf-off" style="${pos}"><span class="sf-q">?</span><small>offen</small></div>`;
    const s = SPN && findeSP(k, x.n), f = s ? pfFoto(s, 30, 30, 15) : `<span class="sf-q sf-i" style="background:${KFARBE[k] || "var(--soft)"}">${initialen(x.n)}</span>`;
    const inn = `${f}<b>${esc(x.n)}</b><small><i style="background:${SF_STUFE[x.vs ? 0 : x.b] || SF_STUFE[1]}"></i>${sub || ""}</small>`;
    if (neu) return `<div class="sf-t sf-neu" style="${pos}">${f}<b>${esc(x.n)}</b><small><span class="sf-nt">NEU</span>${sub || ""}</small></div>`;
    return s ? `<button class="sf-t" style="${pos}" data-profil="${esc(s.id)}">${inn}</button>` : `<div class="sf-t" style="${pos}">${inn}</div>`;
  }
  function stdFeld(k, g){  // g: Grafik einer Wechsel-Meldung {art, alt, neu}, markiert die geänderte Position
    if (!IN || !(IN.standards || []).some(s => s.k === k)) return "";
    const D = sfDaten(k), e = D.ecke, seiteBek = e && (e.L || e.R);
    let L = e && seiteBek ? {...e, n: e.L || e.n} : e, R = e && seiteBek ? {...e, n: e.R || e.n} : e;
    let lsub = e && !e.L ? "Seite offen" : "", rsub = e && !e.R ? "Seite offen" : "";
    let esub = D.elf && D.elf.q ? `${D.elf.q[0]}/${D.elf.q[0] + D.elf.q[1]}${D.elf.vs ? " · Vorsaison" : ""}` : "";
    const art = g ? normS(g.art) : "", vorher = g && g.alt ? `vorher ${esc(nachN(g.alt))}` : "", NEU = {};
    if (g && g.neu) {
      const neu = {n: nachN(g.neu), b: 2};
      if (art.startsWith("elf")) { const q = D.akt.find(a => sfGl(a.n, g.neu)); D.elf = neu; esub = q ? `${q.t}/${q.t + q.v}` : ""; NEU.elf = 1; }
      else if (art.startsWith("frei")) { D.fs = {...neu, direkt: false}; NEU.fs = 1; }
      else { const nurL = L && g.alt && sfGl(L.n, g.alt) && !(R && sfGl(R.n, g.alt)), nurR = R && g.alt && sfGl(R.n, g.alt) && !(L && sfGl(L.n, g.alt));
        if (!nurR) { L = neu; lsub = ""; NEU.L = 1; } if (!nurL) { R = neu; rsub = ""; NEU.R = 1; } }
    }
    const Lin = 'fill="none" stroke="rgba(255,255,255,.16)" stroke-width="1.5"';
    return `${g ? "" : kap("Standards")}<div class="sf${g ? " sf-art" : ""}"><svg viewBox="0 0 340 200" preserveAspectRatio="none" aria-hidden="true"><g ${Lin}><rect x="2" y="2" width="336" height="196"/><rect x="70" y="2" width="200" height="80"/><rect x="125" y="2" width="90" height="28"/><path d="M130 82 A45 45 0 0 0 210 82"/><path d="M2 14 A12 12 0 0 0 14 2"/><path d="M326 2 A12 12 0 0 0 338 14"/></g><circle cx="170" cy="58" r="2.5" fill="rgba(255,255,255,.45)"/><rect x="140" y="0" width="60" height="5" fill="rgba(255,255,255,.35)"/></svg>
      <span class="sf-lb" style="left:20px;top:6px">ECKE L</span><span class="sf-lb" style="right:20px;top:6px">ECKE R</span><span class="sf-lb sf-m" style="top:32px">ELFMETER</span><span class="sf-lb sf-m" style="top:124px">FREISTOSS</span>
      ${sfTag(k, L, "left:8px;top:22px", lsub, NEU.L)}${sfTag(k, R, "right:8px;top:22px;align-items:flex-end;text-align:right", rsub, NEU.R)}
      ${sfTag(k, D.elf, "left:50%;top:42px;transform:translateX(-50%);align-items:center;text-align:center", esub, NEU.elf)}
      ${sfTag(k, D.fs, "left:50%;top:136px;transform:translateX(-50%);align-items:center;text-align:center", NEU.fs ? "" : D.fs && D.fs.direkt ? "direkt" : "", NEU.fs)}</div>
      <div class="sf-leg"><span><i style="background:${SF_STUFE[3]}"></i>Sicher</span><span><i style="background:${SF_STUFE[2]}"></i>Wahrscheinlich</span><span><i style="background:${SF_STUFE[1]}"></i>Unsicher</span><span><i style="background:${SF_STUFE[0]}"></i>Vorsaison</span></div>
      ${g && g.alt ? `<p class="sf-cap"><span class="sf-nt">NEU</span> <b>${esc(nachN(g.neu))}</b> übernimmt ${esc(g.art || "die Standards")}, vorher <b>${esc(nachN(g.alt))}</b>.</p>` : ""}
      ${!g && (D.akt.length || D.vs.length) ? `<div class="sf-el"><span class="k">ELFMETER</span><span><small>Diese Saison</small>${D.akt.length ? D.akt.map(a => `<em><b>${esc(nachN(a.n))}</b> ${a.t}/${a.t + a.v}</em>`).join("") : "noch keiner"}</span><span><small>Letzte Saison</small>${D.vs.length ? D.vs.map(x => `<em><b>${esc(nachN(x[0]))}</b> ${x[1]}/${x[1] + x[2]}${x[3] ? ` <small>für ${esc(x[3])}</small>` : ""}</em>`).join("") : "keine Daten"}</span></div>` : ""}
      ${!g && D.st.hinweis ? `<p class="ki" style="color:#F5B041">${esc(D.st.hinweis)}</p>` : ""}`;
  }
  // Aufstellung: fehlt eine Schützin in der Startelf, nennen wir die nächste aus den Daten, die spielt
  function stdHinweis(k, a){
    const elf = (a && a.startelf) || []; if (elf.length < 11 || !IN) return "";
    const D = sfDaten(k), drin = n => elf.some(s => sfGl(s.voll || s.n, n));
    const fehlt = {};
    [["Ecken", D.ecke], ["Freistöße", D.fs], ["Elfmeter", D.elf]].forEach(([lbl, x]) => { if (!x || !x.n || drin(x.n)) return;
      const ers = (x.alt || []).find(drin), key = normS(nachN(x.n)); (fehlt[key] = fehlt[key] || {n: x.n, z: []}).z.push([lbl, ers]); });
    const zeilen = Object.values(fehlt).map(f => {
      const nachE = {}; f.z.forEach(([l, e]) => (nachE[e || ""] = nachE[e || ""] || []).push(l));
      const teile = Object.entries(nachE).map(([e, ls]) => `${ls.join(" und ")}: ${e ? `voraussichtlich <b>${esc(e)}</b>` : "Ersatz unklar"}`);
      return `<div class="sf-h">${svg(P.warn, "")}<span><b>${esc(f.n)}</b> nicht in der Startelf. ${teile.join(". ")}.</span><button class="lk" data-kader="${esc(k)}">Standards</button></div>`; });
    return zeilen.join("");
  }
'''

CSS = '''
/* Standards als Spielfeld (04.11.2026) */
.sf{position:relative;height:200px;border-radius:12px;background:linear-gradient(#1E3A2B,#17301F);overflow:hidden}
.sf svg{position:absolute;inset:0;width:100%;height:100%}
.sf-t{position:absolute;display:flex;flex-direction:column;gap:2px;align-items:flex-start;padding:0;background:none;border:0;color:inherit;text-align:left}
.sf-t b{font-size:12.5px;font-weight:700;text-shadow:0 1px 2px rgba(0,0,0,.5)}
.sf-t small{font-size:10px;color:#C9D3E2;display:flex;gap:4px;align-items:center;white-space:nowrap}
.sf-t small i{width:7px;height:7px;border-radius:50%;display:inline-block}
.sf-q{width:30px;height:30px;border-radius:50%;border:1.5px dashed rgba(255,255,255,.35);display:grid;place-items:center;color:#A9B4C6;font-size:12px;font-weight:700}
.sf-q.sf-i{border:0;color:#fff}
.sf-lb{position:absolute;font:700 8.5px var(--f-mono);letter-spacing:.8px;color:rgba(255,255,255,.45)}
.sf-m{left:50%;transform:translateX(-50%)}
.sf-leg{display:flex;flex-wrap:wrap;gap:10px;font-size:11px;color:var(--muted);margin-top:6px}.sf-leg span{display:flex;gap:4px;align-items:center}.sf-leg i{width:7px;height:7px;border-radius:50%;display:inline-block}
.sf-h{display:grid;grid-template-columns:14px 1fr auto;gap:8px;align-items:start;font-size:12.5px;line-height:1.4;color:#F5D08A;background:rgba(245,176,65,.1);border-radius:10px;padding:8px 10px;margin:8px 0 4px}
.sf-vl{display:grid;grid-template-columns:repeat(2,1fr);gap:6px}.sf-v{display:flex;gap:8px;align-items:center;background:var(--card);border-radius:10px;padding:8px 10px;font-size:13.5px;font-weight:600;color:inherit;text-align:left}
.bb.sch{position:relative}.bb.sch i{position:absolute;left:0;top:0;bottom:0;background:#2F5BFF}.bb.sch i.t{background:#C7D6FF}
.sf-el{display:grid;grid-template-columns:auto 1fr 1fr;gap:10px;align-items:start;background:var(--card);border-radius:10px;padding:9px 12px;margin-top:8px;font-size:12.5px}.sf-el .k{font:700 9.5px var(--f-mono);letter-spacing:.7px;color:#8FB0FF;padding-top:2px}.sf-el span{display:grid;gap:2px}.sf-el small{font-size:10.5px;color:var(--muted)}.sf-el b{font-weight:600}.sf-el em{font-style:normal;display:block}.sf-el em small{display:inline}
.sf-neu .ph,.sf-neu .bild,.sf-neu .sf-q{box-shadow:0 0 0 2.5px #6E9BFF}.sf-nt{font:700 9px var(--f-mono);background:#2F5BFF;color:#fff;border-radius:4px;padding:1px 4px}.sf-art{margin-top:14px}.sf-cap{font-size:13px;color:var(--muted);margin:8px 0 0}.sf-cap b{color:var(--ink)}
.sf-h svg{width:14px;height:14px;stroke:currentColor;fill:none;stroke-width:2;margin-top:2px}.sf-h b{color:#fff}.sf-h .lk{font-size:12px}
'''

INSIDE = '''      <div style="display:grid;gap:4px;padding-top:8px"><h3 class="disp" style="font-size:21px">Wer schießt die Standards?</h3>
        <p class="af-st" style="font-size:12px">Je Verein als Spielfeld auf der Vereinsseite: Ecke links und rechts, Freistoß, Elfmeter mit Quote.</p></div>
      <div class="sf-vl">${(IN.standards || []).map(s => `<button class="sf-v" data-kader="${esc(s.k)}">${logo(s.k, 26)}<span>${esc(kname(s.k))}</span></button>`).join("")}</div>${afStandards()}</section>`;'''
def patch(s):
    s = rep(s, '''m.grafik && m.grafik.typ === "fansdaten" ? fdGrafik(m.grafik) : ""}''', '''m.grafik && m.grafik.typ === "fansdaten" ? fdGrafik(m.grafik) : m.grafik && m.grafik.typ === "stdfeld" ? stdFeld(m.grafik.k, m.grafik) : ""}''')
    a = s.index(OLD_BLOCK_START); b = s.index(OLD_BLOCK_END, a) + len(OLD_BLOCK_END)
    s = s[:a] + INSIDE + s[b:]
    s = rep(s, '''      ${AF.freist ? (() => {''', SCH + '''      ${AF.freist ? (() => {''')
    s = rep(s, '''Ecken pro Spiel und Elfmeter: API-Football''', '''Ecken, Schüsse pro Spiel und Elfmeter: API-Football''')
    s = rep(s, '  function vereinsKader(k, von){', JS + '  function vereinsKader(k, von){')
    s = rep(s, '''<h1 class="disp">${esc(Object.keys(KURZ).find(v => KURZ[v] === k) || kname(k))}</h1></div>''',
               '''<h1 class="disp">${esc(Object.keys(KURZ).find(v => KURZ[v] === k) || kname(k))}</h1></div>${stdFeld(k)}''')
    s = rep(s, '''    return `<div class="kartebox"><div class="tb-k"><button class="kd-btn" data-kader="${esc(k)}" aria-label="Kader ${esc(name)}">${logo(k, 22)}<span class="n">${esc(name)}</span></button>${badge}</div>${inh}</div>`;''',
               '''    return `<div class="kartebox"><div class="tb-k"><button class="kd-btn" data-kader="${esc(k)}" aria-label="Kader ${esc(name)}">${logo(k, 22)}<span class="n">${esc(name)}</span></button>${badge}</div>${!vorbei && a ? stdHinweis(k, a) : ""}${inh}</div>`;''')
    i = s.find("</style>", s.find("--f-display")); s = s[:i] + CSS + s[i:]
    assert "—" not in s
    return s

if __name__ == "__main__":
    for f in sys.argv[1:]:
        s = open(f, encoding="utf-8").read()
        if "function stdFeld" in s: print("schon drin", f); continue
        t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
