# News mit Mehrwert (Finn 05.11.2026): "Unsere Einordnung für Kickbase" bei Ausfall, Rotation, Rückkehr (wie wichtig, wer spielt für sie / wen kann sie verdrängen,
# Belastung der Konkurrenz, einsehbar); TOP automatisch, wenn eine Topspielerin ausfällt; Status-Verlauf auch ohne Prognose-Etappen; keine Klammern bei "fehlt"
import sys
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
EINORD = r'''
  // ---------------- Unsere Einordnung für Kickbase (Finn 05.11.2026)
  let TOPIDS = null;
  function topIds(){
    if (TOPIDS || !SPN || !AF || !AF.sp) return TOPIDS || new Set();
    const L = SPN.spielerinnen || [], no = L.map(s => [s.id, (AF.sp[s.id] || {})]).filter(([, a]) => a.avg && (a.no || []).filter(n => n[2] >= 60).length >= 4).sort((a, b) => b[1].avg - a[1].avg).slice(0, 20).map(x => x[0]);
    const tb = s => (s.spiele || []).reduce((a, e) => a + (e.tore || []).length + (e.vorl || 0), 0);
    const tbl = L.filter(s => s.pos !== "TW").sort((a, b) => tb(b) - tb(a)).slice(0, 10).filter(s => tb(s) >= 3).map(s => s.id);
    return TOPIDS = new Set(no.concat(tbl));
  }
  const ausfallNews = m => ["verletzt", "gesperrt"].includes(m.status) || (m.tags || []).some(t => ["VERLETZUNG", "SPERRE", "ROTATION"].includes(t)) && m.status !== "fit";
  function tagsVon(m){
    const t = (m.tags || []).slice(); if (t.includes("TOP") || !istSpielerin(m) || !m.spielerin || !SPN || !ausfallNews(m)) return t;
    const s = findeSP(KURZ[m.verein], m.spielerin) || (SPN.spielerinnen || []).find(x => x.n === m.spielerin); if (!s || !topIds().has(s.id)) return t;
    return ["TOP"].concat(t);
  }
  function einordnung(m){
    if (!SPN || !istSpielerin(m) || !m.spielerin) return "";
    const k = KURZ[m.verein], s = findeSP(k, m.spielerin) || (SPN.spielerinnen || []).find(x => x.n === m.spielerin && x.k === k); if (!s) return "";
    const sl = (s.verlauf || []).slice(-1)[0] || {}, zurueck = (m.tags || []).includes("RÜCKKEHR") || sl.status === "zurueck" || /zurück|wieder (fit|einsatzfähig|im Kader)/i.test(m.headline || "");
    const aus = !zurueck && (ausfallNews(m) || (s.status && ["raus", "gesperrt"].includes(s.status.s)));
    if (!aus && !zurueck) return "";
    const z = [], M = x => (x.spiele || []).reduce((a, e) => a + (e.min || 0), 0), l5 = (s.spiele || []).slice(-5), st5 = l5.filter(e => e.art === "S").length;
    // 1. Wie wichtig
    const a = (AF && AF.sp && AF.sp[s.id]) || {}, rangN = (() => { if (!a.avg || !AF.sp) return null; const v = Object.values(AF.sp).filter(x => x.avg && (x.no || []).filter(n => n[2] >= 60).length >= 4).map(x => x.avg); return v.length >= 30 && (a.no || []).filter(n => n[2] >= 60).length >= 4 ? 1 + v.filter(x => x > a.avg).length : null; })();
    const tb = (s.spiele || []).reduce((x, e) => x + (e.tore || []).length + (e.vorl || 0), 0);
    if (l5.length) z.push(["Wie wichtig", `${st5 >= 4 ? "Stammspielerin" : st5 >= 2 ? "Rotation" : "Ergänzung"}: ${st5} der letzten ${l5.length} Ligaspiele in der Startelf${a.avg ? `, Notenschnitt ${dez(a.avg)}${rangN && rangN <= 30 ? `, Platz ${rangN} der Liga` : ""}` : ""}${s.pos !== "TW" && tb ? `, ${tb} ${tb === 1 ? "Torbeteiligung" : "Torbeteiligungen"}` : ""}.`]);
    // 2. Wer spielt für sie / wen kann sie verdrängen
    const gr = PGRP(s), mates = (SPN.spielerinnen || []).filter(x => x.k === k && x.id !== s.id && !x.trainer && (gr ? PGRP(x) === gr : x.pos === s.pos));
    const fit = x => !(x.status && ["raus", "gesperrt"].includes(x.status.s)), q5 = x => (x.spiele || []).slice(-5).filter(e => e.art === "S").length;
    const RANG = {sicher: 4, erwartet: 3, unsicher: 2, unwahrscheinlich: 1, ausgeschlossen: 0}, pst = x => (x.prognose || {}).st;
    const nm = x => nachN(x.n), btn = x => `<button class="eo-n" data-profil="${esc(x.id)}">${esc(nm(x))}</button>`;
    let kon = [];
    if (aus) {
      const ers = (s.ersatz || []).map(r => mates.find(x => normS(nachN(x.n)) === normS(nachN(r.n)))).filter(Boolean).filter(fit);
      kon = (ers.length ? ers : mates.filter(fit).filter(x => q5(x) < 4 && ((x.spiele || []).slice(-1)[0] || {}).art !== "S").sort((x, y) => (RANG[pst(y)] ?? -1) - (RANG[pst(x)] ?? -1) || q5(y) - q5(x))).slice(0, 2);
      if (kon.length) z.push(["Wer spielt für sie?", kon.map(x => { const r = (s.ersatz || []).find(e => normS(nachN(e.n)) === normS(nachN(x.n)));
        return `Chance für ${btn(x)}${r && r.s ? `, stand schon ${r.s}x für sie in der Startelf` : ""}${pst(x) && STUFE[pst(x)] ? `, Prognose: ${STUFE[pst(x)][2]}` : ""}.`; }).join(" "), 1]);
    } else {
      kon = mates.filter(fit).filter(x => ((x.spiele || []).slice(-1)[0] || {}).art === "S").sort((x, y) => q5(y) - q5(x)).slice(0, 2);
      if (kon.length) z.push(["Wen kann sie verdrängen?", kon.map(x => `${btn(x)}: ${q5(x)} der letzten ${Math.min(5, (x.spiele || []).length)} Ligaspiele in der Startelf.`).join(" "), 1]);
    }
    // 3. Belastung der Konkurrenz: Pflichtspiele in den letzten 8 Tagen
    const jetzt = Date.now(), last = x => (x.spiele || []).map(e => [e.datum, e.min || 0, e.art]).map(e => e.concat([1])).concat((x.pokal || []).map(e => [e.datum, e.min || 0, e.art, e.min != null ? 1 : 0]))
      .filter(e => e[0] && (e[2] === "S" || e[2] === "E") && jetzt - dt(String(e[0]).slice(0, 10) + "T12:00") <= 8 * 864e5 && jetzt >= dt(String(e[0]).slice(0, 10) + "T12:00"));
    const bel = kon.map(x => [x, last(x)]).filter(([, l]) => l.length >= 2);
    if (bel.length) z.push(["Belastung", bel.map(([x, l]) => `${esc(nm(x))}: ${l.length} Pflichtspiele in 8 Tagen${l.every(e => e[3]) ? `, ${l.reduce((a, e) => a + e[1], 0)} Minuten` : ""}.`).join(" ") + (aus ? "" : " Eine Pause ist möglich."), 1]);
    // 4. Einsehbar
    const p = alleSpiele().filter(q => (q.heim_k === k || q.gast_k === k) && q.status !== "beendet" && q.status !== "abgesagt").sort((x, y) => (dt(x.anstoss) || Infinity) - (dt(y.anstoss) || Infinity))[0];
    if (p && terminiert(p)) z.push(["Aufstellung", einsehbar(p) ? "Die offizielle Aufstellung kommt, bevor Kickbase schließt. Wer unsicher ist, kann abwarten." : "Kickbase schließt vor der offiziellen Aufstellung. Hier zählt unsere Prognose."]);
    if (z.length < 2) return "";
    return `<section class="eo">${kap("Unsere Einordnung für Kickbase")}${z.map(([t, x, html]) => `<div class="eo-z"><b>${esc(t)}</b><span>${html ? x : esc(x)}</span></div>`).join("")}</section>`;
  }
'''
def patch(s):
    s = rep(s, """  function artVerlauf(m){""", EINORD + """  function artVerlauf(m){""")
    # Einordnung nach "Für Kickbase" im Artikel, auch nach Laden der Spielerinnen
    s = rep(s, """<div id="art-sv">${auf || sc ? "" : artVerlauf(m)}</div>${kbBox(m.kickbase)}""", """<div id="art-sv">${auf || sc ? "" : artVerlauf(m)}</div>${kbBox(m.kickbase)}<div id="art-eo">${auf || sc ? "" : einordnung(m)}</div>""")
    s = rep(s, """const sv = $("#art-sv"); if (sv && ARTIK""", """const eo = $("#art-eo"); if (eo && ARTIKEL === id) eo.innerHTML = einordnung(m); const sv = $("#art-sv"); if (sv && ARTIK""")
    # TOP automatisch
    s = rep(s, """      <div class="nk-top"><div class="tags">${(m.tags || []).map(tag).join("")}""", """      <div class="nk-top"><div class="tags">${tagsVon(m).map(tag).join("")}""")
    s = rep(s, """      : `<div style="display:grid;gap:12px"><div class="mk">""", """      : `<div style="display:grid;gap:12px"><div class="mk" data-tg="1">""")
    a = s.index('<div class="mk" data-tg="1">'); b = s.index('<div class="tags">${(m.tags || []).map(tag).join("")}</div>', a)
    s = s[:b] + '<div class="tags">${tagsVon(m).map(tag).join("")}</div>' + s[b + len('<div class="tags">${(m.tags || []).map(tag).join("")}</div>'):]
    s = s.replace('<div class="mk" data-tg="1">', '<div class="mk">')
    # Status-Verlauf auch ohne Etappen: Zeitleiste aus dem Verlauf
    s = rep(s, """    const g = verlaufGrafik(s), e = s.einschaetzung; if (!g) return "";""", """    const e = s.einschaetzung, g = verlaufGrafik(s) || (s.verlauf || []).length && `<div class="pf-tl">${s.verlauf.slice().reverse().slice(0, 4).map(v => `<div class="ev"><i style="background:${STFARBE[stArt({s: v.status, grund: v.grund})] || STFARBE[v.status] || "#8A95A8"}"></i><div><div class="dt">${esc(kurz(dt(v.stand)))}${v.quelle ? " · " + esc(String(v.quelle).split(",")[0]) : ""}</div><b style="display:block">${esc(v.grund || "")}</b>${v.rueckkehr && v.rueckkehr !== "offen" ? `<small style="display:block">${esc(v.rueckkehr)}</small>` : v.rueckkehr === "offen" ? '<small style="display:block">Rückkehr offen</small>' : ""}</div></div>`).join("")}</div>`; if (!g) return "";""")
    s = rep(s, """.pf-km .eins svg{width:14px;height:14px}.art-sv{margin-top:4px}""", """.pf-km .eins svg{width:14px;height:14px}.art-sv{margin-top:4px}
.eo{background:var(--card,#16223A);border:1px solid rgba(110,155,255,.22);border-radius:14px;padding:14px;display:grid;gap:10px;margin-top:10px}
.eo-z{display:grid;gap:2px}.eo-z b{font-size:11px;letter-spacing:.6px;text-transform:uppercase;color:#8FB0FF}.eo-z span{font-size:14px;line-height:1.45}
.eo-n{background:none;border:0;padding:0;color:inherit;font:inherit;font-weight:700;text-decoration:underline dashed rgba(255,255,255,.35);text-underline-offset:3px;cursor:pointer}""")
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
