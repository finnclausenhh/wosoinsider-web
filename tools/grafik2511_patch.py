#!/usr/bin/env python3
"""Grafiken vom 25.11.2026 (Finn): xG-Check als Pech-Glück-Skala (grafik typ "xgskala"), Nationalteams nach Ländern
(grafik typ "nationalteams"), Rückkehr-Block mit Fortschritt, Ausfalltagen (ab 50 Tagen Zeitstrahl), Bestform aus
bestform.json und Hinweis "kaum Kickbase-Relevanz". "Wie wichtig" zählt bei Rückkehr nur Spiele vor der Verletzung.

Aufruf: python3 tools/grafik2511_patch.py ticker-test/index.html  (passt auch auf ticker/index.html und die Artifact-index.html)
"""
import sys

CSS = r""".xgs{background:var(--card);border-radius:14px;padding:14px 12px;display:grid;gap:10px;margin-top:4px}
.xgs-k{display:flex;justify-content:space-between;font-size:11px;font-weight:700;letter-spacing:.5px}.xgs-k .u{color:#FFB27A}.xgs-k .o{color:#9DB0FF}
.xgs-r{display:grid;grid-template-columns:28px minmax(0,1fr) minmax(0,1fr);align-items:center}
.xgs-l{display:flex;justify-content:flex-end;align-items:center;min-height:24px;border-right:2px solid #3A4766}.xgs-rr{display:flex;align-items:center;min-height:24px}
.xgs-r small{font-size:11.5px;color:var(--muted);white-space:nowrap}.xgs-l small{padding-right:8px}.xgs-rr small{padding-left:8px}
.xgs-l i,.xgs-rr i{display:flex;align-items:center;height:22px;min-width:40px;font-style:normal;font-size:12px;font-weight:700;box-sizing:border-box}
.xgs-l i{background:#D9773A;color:#1A0E05;border-radius:4px 0 0 4px;padding-left:6px}.xgs-r.h .xgs-l i{background:#FF8A3D}
.xgs-rr i{background:#4A64FF;color:#fff;border-radius:0 4px 4px 0;justify-content:flex-end;padding-right:6px}
.xgs-kz{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:8px}.xgs-kz>div{border-radius:12px;padding:10px 12px;display:grid;gap:2px}
.xgs-kz .u{background:#2A1D17}.xgs-kz .o{background:#18244A}.xgs-kz b{font-size:22px;line-height:1.1}.xgs-kz .u b{color:#FFB27A}.xgs-kz .o b{color:#9DB0FF}.xgs-kz span{font-size:12.5px;line-height:1.35;color:#D8DEEA}
.ntg{display:grid;gap:8px;margin-top:4px}.ntg-l{background:var(--card);border-radius:12px;padding:12px 14px;display:grid;gap:6px}
.ntg-k{display:flex;align-items:center;gap:10px}.ntg-k i{width:30px;height:20px;border-radius:3px;flex:none;box-shadow:0 0 0 1px rgba(255,255,255,.12)}.ntg-k b{font-size:20px}
.ntg-k small{margin-left:auto;font-size:12px;color:var(--muted);text-align:right}.ntg-s{display:grid;gap:3px;padding-left:40px}
.ntg-n{all:unset;cursor:pointer;font-size:14px;line-height:1.45}.ntg-n em{font-style:normal;font-size:12px;color:var(--muted);margin-left:4px}
.rk{background:var(--card);border-radius:14px;padding:14px;display:grid;gap:12px;margin-top:10px}.rk.kaum{background:#141B2C;border:1px solid #232C42}
.rk-t{margin:0;font-size:13px;color:var(--muted)}.rk p{margin:0;font-size:13.5px;line-height:1.45;color:#C5CCE0}
.rk-st{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:4px;text-align:center;font-size:11px}.rk-st>div{display:grid;gap:5px}
.rk-st i{height:6px;border-radius:3px;background:#2A3757}.rk-st span{color:var(--muted)}.rk-st .an i{background:#2EB872}.rk-st .an span{color:#fff;font-weight:600}
.rk-tl{display:grid;gap:6px}.rk-tl b{font-size:24px;line-height:1.05}.rk-bar{height:10px;border-radius:5px;background:linear-gradient(90deg,#E24A4A 0 90%,#2EB872 90%)}
.rk-tl .d{display:flex;justify-content:space-between;font-size:11px;color:var(--muted)}
.rk-b{display:grid;gap:10px;border-top:1px solid rgba(255,255,255,.08);padding-top:12px}.rk-bk{display:flex;justify-content:space-between;align-items:baseline;gap:8px}
.rk-bk b{font-size:11px;letter-spacing:.6px;color:#8FB0FF}.rk-bk span{font-size:12px;color:var(--muted);text-align:right}
.rk-kz{display:grid;grid-template-columns:repeat(auto-fit,minmax(90px,1fr));gap:8px}.rk-kz>div{background:rgba(255,255,255,.05);border-radius:10px;padding:10px;display:grid;gap:2px}
.rk-kz b{font-size:22px;line-height:1.05}.rk-kz small{font-size:11px;color:var(--muted);line-height:1.25}
.rk-bal{display:grid;gap:4px}.rk-bal .z{display:flex;justify-content:space-between;font-size:12px}.rk-bal .s{height:8px;background:#2A3757;border-radius:4px;overflow:hidden}.rk-bal .s i{display:block;height:100%;border-radius:4px}
.rk-q{font-size:11px;color:var(--muted)}
"""

JS = r"""  // Grafiken vom 25.11.2026 (Finn): xG-Skala, Nationalteams nach Ländern, Rückkehr-Block (tools/grafik2511_patch.py)
  let BEST = null;
  const ladeBest = () => BEST ? Promise.resolve(BEST) : frisch("bestform.json").then(d => (BEST = d || {})).catch(() => (BEST = {}));
  function xgSkala(g){
    const z = (g && g.z) || []; if (!z.length) return "";
    const mx = Math.max(1.5, ...z.map(r => Math.abs(r.d))), w = r => Math.max(18, Math.abs(r.d) / mx * 100).toFixed(1), D = v => (v > 0 ? "+" : "−") + dez(Math.abs(v));
    const tx = r => `<small>${r.t} ${r.t === 1 ? "Tor" : "Tore"}, ${dez(r.xg)} xG</small>`, u = z.filter(r => r.d < 0).length, o = z.length - u;
    return `<section class="xgs"><div class="xgs-k"><span class="u">‹ UNTER DEN CHANCEN</span><span class="o">DRÜBER ›</span></div>${z.map(r => `<div class="xgs-r${r.hervor ? " h" : ""}">${logo(r.k, 22)}<span class="xgs-l">${r.d < 0 ? `<i style="width:${w(r)}%">${D(r.d)}</i>` : tx(r)}</span><span class="xgs-rr">${r.d >= 0 ? `<i style="width:${w(r)}%">${D(r.d)}</i>` : tx(r)}</span></div>`).join("")}
      <div class="xgs-kz">${u ? `<div class="u"><b class="disp">${u} ${u === 1 ? "Team" : "Teams"}</b><span>${u === 1 ? "traf" : "trafen"} weniger als ${u === 1 ? "seine" : "ihre"} Chancen. Nächstes Mal eher mehr Tore.</span></div>` : ""}${o ? `<div class="o"><b class="disp">${o} ${o === 1 ? "Team" : "Teams"}</b><span>${o === 1 ? "traf" : "trafen"} mehr als erwartet. Das hält selten lange.</span></div>` : ""}</div></section>`;
  }
  const FLAG = {Deutschland: "linear-gradient(#000 0 33%,#DD0000 33% 66%,#FFCE00 66%)", "Österreich": "linear-gradient(#C8102E 0 33%,#fff 33% 66%,#C8102E 66%)", Schweiz: "#D52B1E",
    Ungarn: "linear-gradient(#CE2939 0 33%,#fff 33% 66%,#477050 66%)", Marokko: "#C1272D", Niederlande: "linear-gradient(#AE1C28 0 33%,#fff 33% 66%,#21468B 66%)",
    Frankreich: "linear-gradient(90deg,#0055A4 0 33%,#fff 33% 66%,#EF4135 66%)", Italien: "linear-gradient(90deg,#009246 0 33%,#fff 33% 66%,#CE2B37 66%)", Belgien: "linear-gradient(90deg,#000 0 33%,#FDDA24 33% 66%,#EF3340 66%)",
    Irland: "linear-gradient(90deg,#169B62 0 33%,#fff 33% 66%,#FF883E 66%)", Polen: "linear-gradient(#fff 0 50%,#DC143C 50%)", Tschechien: "linear-gradient(#fff 0 50%,#D7141A 50%)",
    Dänemark: "#C8102E", Schweden: "#006AA7", Norwegen: "#BA0C2F", Finnland: "#fff", Island: "#02529C", Spanien: "linear-gradient(#AA151B 0 25%,#F1BF00 25% 75%,#AA151B 75%)",
    Portugal: "linear-gradient(90deg,#046A38 0 40%,#DA291C 40%)", England: "#fff", Schottland: "#005EB8", Wales: "linear-gradient(#fff 0 50%,#00B140 50%)", Kroatien: "linear-gradient(#FF0000 0 33%,#fff 33% 66%,#171796 66%)",
    Serbien: "linear-gradient(#C6363C 0 33%,#0C4076 33% 66%,#fff 66%)", Slowenien: "linear-gradient(#fff 0 33%,#0000FF 33% 66%,#FF0000 66%)", Rumänien: "linear-gradient(90deg,#002B7F 0 33%,#FCD116 33% 66%,#CE1126 66%)",
    Ukraine: "linear-gradient(#0057B7 0 50%,#FFD700 50%)", Luxemburg: "linear-gradient(#EF3340 0 33%,#fff 33% 66%,#00A3E0 66%)", USA: "#3C3B6E", Kanada: "linear-gradient(90deg,#D80621 0 25%,#fff 25% 75%,#D80621 75%)",
    Japan: "#fff", Australien: "#012169", Neuseeland: "#012169", Brasilien: "#009C3B", Mexiko: "linear-gradient(90deg,#006847 0 33%,#fff 33% 66%,#CE1126 66%)", Nigeria: "linear-gradient(90deg,#008751 0 33%,#fff 33% 66%,#008751 66%)",
    Ghana: "linear-gradient(#CE1126 0 33%,#FCD116 33% 66%,#006B3F 66%)", Kamerun: "linear-gradient(90deg,#007A5E 0 33%,#CE1126 33% 66%,#FCD116 66%)", Südafrika: "#007749", Türkei: "#E30A17", Griechenland: "#0D5EAF",
    Israel: "#fff", Südkorea: "#fff", China: "#DE2910", Kolumbien: "linear-gradient(#FCD116 0 50%,#003893 50% 75%,#CE1126 75%)", Venezuela: "linear-gradient(#FFCC00 0 33%,#00247D 33% 66%,#CF142B 66%)",
    Jamaika: "#009B3A", Haiti: "linear-gradient(#00209F 0 50%,#D21034 50%)", Paraguay: "linear-gradient(#D52B1E 0 33%,#fff 33% 66%,#0038A8 66%)", Argentinien: "linear-gradient(#74ACDF 0 33%,#fff 33% 66%,#74ACDF 66%)"};
  function ntGrafik(g){
    const L = (g && g.laender) || []; if (!L.length) return "";
    return `<section class="ntg">${L.map(l => `<div class="ntg-l"><div class="ntg-k"><i style="background:${FLAG[l.land] || "#3A4766"}"></i><b class="disp">${esc(String(l.land).toUpperCase())}</b>${l.gegner ? `<small>${esc(l.gegner)}</small>` : ""}</div><div class="ntg-s">${(l.sp || []).map(x => `<button class="ntg-n" data-profilname="${esc((g.k || "") + "|" + x.n)}">${esc(x.n)}${x.team ? `<em>${esc(x.team)}</em>` : ""}</button>`).join("")}</div></div>`).join("")}</section>`;
  }
  const zgGrafik = m => !m.grafik ? "" : m.grafik.typ === "xgskala" ? xgSkala(m.grafik) : m.grafik.typ === "nationalteams" ? ntGrafik(m.grafik) : "";
  // Rückkehr: Beginn des letzten Ausfalls aus dem Status-Verlauf (Datum aus der Quelle "…, TT.MM.", sonst Stand)
  function rkAb(s){
    const v = s.verlauf || []; let i = v.length - 1;
    while (i >= 0 && v[i].status === "zurueck") i--;
    if (i < 0 || !["raus", "fraglich", "gesperrt"].includes(v[i].status)) return null;
    while (i > 0 && ["raus", "fraglich", "gesperrt"].includes(v[i - 1].status)) i--;
    const e = v[i], q = String(e.quelle || "").match(/(\d{1,2})\.(\d{1,2})\.(\d{4})?/), st = String(e.stand || "").slice(0, 10);
    if (q && st) { let y = +(q[3] || st.slice(0, 4)); const d = new Date(y, +q[2] - 1, +q[1], 12); if (!q[3] && d - dt(st + "T12:00") > 30 * 864e5) d.setFullYear(y - 1); return d; }
    return st ? dt(st + "T12:00") : null;
  }
  const rkDat = e => dt(String(e.datum).slice(0, 10) + "T12:00");
  function rkBlock(m){
    if (!SPN || !istSpielerin(m) || !m.spielerin || !(m.tags || []).includes("RÜCKKEHR")) return "";
    const k = KURZ[m.verein], s = findeSP(k, m.spielerin) || (SPN.spielerinnen || []).find(x => x.n === m.spielerin && x.k === k); if (!s) return "";
    const ab = rkAb(s); if (!ab) return "";
    const nach = (s.spiele || []).concat(s.pokal || []).filter(e => e.datum && rkDat(e) > ab && e.art !== "X").sort((a, b) => rkDat(a) - rkDat(b));
    if (!nach.length) return "";
    const sp = nach.filter(e => e.art === "S" || e.art === "E"), erst = nach[0], lz = sp.slice(-1)[0], start = sp.some(e => e.art === "S");
    const tage = Math.round((rkDat(erst) - ab) / 864e5), mn = lz ? (lz.min || 0) : 0, TT = d => `${String(d.getDate()).padStart(2, "0")}.${String(d.getMonth() + 1).padStart(2, "0")}.`;
    const b = BEST && BEST[s.id], vor = (s.spiele || []).filter(e => e.datum && rkDat(e) < ab && e.art !== "X"), stV = vor.filter(e => e.art === "S").length;
    const kaum = !b && vor.length >= 3 && stV / vor.length < .25;
    const schritt = [["Training", 1], ["Kader", 1], [sp.length ? `${mn} Min.` : "Einsatz", sp.length], ["Startelf", start]];
    const stH = `<div class="rk-st">${schritt.map(([t, an]) => `<div class="${an ? "an" : ""}"><i></i><span>${esc(t)}</span></div>`).join("")}</div>`;
    const lng = tage >= 50 ? `<div class="rk-tl"><b class="disp">Nach ${tage} Tagen ${sp.length ? "zurück auf dem Platz" : "zurück im Kader"}</b><div class="rk-bar"></div><div class="d"><span>Ausfall ab ${TT(ab)}</span><span style="color:#2EB872">${sp.length ? "Einsatz" : "Kader"} ${TT(rkDat(erst))}</span></div></div>
      <p>Nach so langer Pause kommen meist erst Joker-Einsätze, bevor die Startelf folgt.</p>` : `<p class="rk-t">${tage} Tage raus, seit ${TT(ab)}</p>`;
    const FIT = mn >= 75 ? ["voll belastbar", 90, "#2EB872"] : mn >= 45 ? ["fast da", 65, "#4ADE80"] : mn >= 20 ? ["im Aufbau", 40, "#F59E0B"] : sp.length ? ["erste Minuten", 18, "#FF8A3D"] : ["noch ohne Einsatz", 6, "#FF8A3D"];
    const KL = {Weltklasse: 95, Topspielerin: 85, Nationalspielerin: 80, Stammspielerin: 65}, kw = b ? (b.klasse_wert || KL[b.klasse] || 70) : 0;
    const bal = (t, w, c, p) => `<div class="rk-bal"><div class="z"><span>${esc(t)}</span><b style="color:${c}">${esc(w)}</b></div><div class="s"><i style="width:${p}%;background:${c}"></i></div></div>`;
    const best = b ? `<div class="rk-b"><div class="rk-bk"><b>IHRE BESTFORM</b><span>${esc([b.saison && "Saison " + b.saison, b.verein].filter(Boolean).join(", "))}</span></div>
      ${(b.werte || []).length ? `<div class="rk-kz">${b.werte.map(w => `<div><b class="disp">${esc(w.w)}</b><small>${esc(w.l)}</small></div>`).join("")}</div>` : ""}
      ${b.klasse ? bal("Klasse", b.klasse, "#2EB872", kw) : ""}${bal("Fitness jetzt", FIT[0], FIT[2], FIT[1])}
      ${b.satz ? `<p>${esc(b.satz)}</p>` : ""}${(b.quellen || []).length ? `<span class="rk-q">Quelle: ${b.quellen.map(q => q.url ? `<a href="${esc(q.url)}" target="_blank" rel="noopener">${esc(q.name)}</a>` : esc(q.name)).join(", ")}</span>` : ""}</div>` : "";
    const kh = kaum ? `<p>Für Kickbase vermutlich ohne Bedeutung: Auch vor dem Ausfall stand sie nur in ${stV} von ${vor.length} Ligaspielen in der Startelf.</p>` : "";
    return `<section class="rk${kaum ? " kaum" : ""}">${kap(kaum ? "Rückkehr · kaum Kickbase-Relevanz" : "Rückkehr")}${lng}${stH}${best}${kh}</section>`;
  }
"""


def ersetze(h, alt, neu, n=1):
    c = h.count(alt)
    if c != n:
        sys.exit(f"Anker {alt[:70]!r} {c}-mal statt {n}-mal gefunden")
    return h.replace(alt, neu)


def main(pfad):
    h = open(pfad, encoding="utf-8").read()
    if "grafik2511_patch" in h:
        print("schon gepatcht"); return
    h = ersetze(h, ".eo{background:var(--card,#16223A)", CSS + ".eo{background:var(--card,#16223A)")
    h = ersetze(h, "  function fvGrafik(g){", JS + "  function fvGrafik(g){")
    # Grafik unter dem Text (Artikel und Spielbericht-Kopf)
    alt = '</div>${m.grafik && m.grafik.typ === "formvergleich" ? fvGrafik(m.grafik)'
    h = ersetze(h, alt, '</div>${zgGrafik(m)}${m.grafik && m.grafik.typ === "formvergleich" ? fvGrafik(m.grafik)', h.count(alt) or 1)
    # Mit Grafik nur der erste Absatz als Text (die Grafik ersetzt die Aufzählung)
    h = ersetze(h, '<div class="body">${(m.text || []).map(p => `<p>${esc(p)}</p>`).join("")}</div>${zgGrafik(m)}',
        '<div class="body">${(zgGrafik(m) ? (m.text || []).slice(0, 1) : (m.text || [])).map(p => `<p>${esc(p)}</p>`).join("")}</div>${zgGrafik(m)}')
    # Rückkehr-Block vor "Für Kickbase"
    h = ersetze(h, '<div id="art-eo">${v2 ? "" : stdA', '<div id="art-rk">${auf || sc || v2 ? "" : rkBlock(m)}</div><div id="art-eo">${v2 ? "" : stdA')
    h = ersetze(h, 'const sv = $("#art-sv"); if (sv && ARTIKEL === id) sv.innerHTML = artVerlauf(m); }).catch(() => {});',
        'const sv = $("#art-sv"); if (sv && ARTIKEL === id) sv.innerHTML = artVerlauf(m); const rk = $("#art-rk"); if (rk && ARTIKEL === id) rk.innerHTML = rkBlock(m); }).catch(() => {});\n'
        '    if (!auf && !sc && !v2 && BEST === null && (m.tags || []).includes("RÜCKKEHR")) Promise.all([ladeBest(), ladeSPN()]).then(() => { const rk = $("#art-rk"); if (rk && ARTIKEL === id) rk.innerHTML = rkBlock(m); }).catch(() => {});')
    # Wie wichtig: bei Rückkehr nur Spiele vor dem Ausfall
    h = ersetze(h, 'const z = [], M = x => (x.spiele || []).reduce((a, e) => a + (e.min || 0), 0), l5 = (s.spiele || []).filter(e => e.art !== "X").slice(-5),',
        'const rab = zurueck ? rkAb(s) : null, z = [], M = x => (x.spiele || []).reduce((a, e) => a + (e.min || 0), 0), l5 = (s.spiele || []).filter(e => e.art !== "X" && (!rab || (e.datum && rkDat(e) < rab))).slice(-5),')
    h = ersetze(h, 'if (l5.length) z.push(["Wie wichtig", `${st5 >= 4 ? "Stammspielerin" : st5 >= 2 ? "Rotation" : "Ergänzung"}: ${st5} der letzten ${l5.length} Ligaspiele in der Startelf${(s.spiele || []).slice(-5).some(e => e.art === "X") ? ", in denen sie im Kader stand" : ""}',
        'if (l5.length) z.push(["Wie wichtig", `${rab ? "Vor dem Ausfall " + (st5 >= 4 ? "Stammspielerin" : st5 >= 2 ? "Rotation" : l5.every(e => e.art === "E") ? "Jokerin" : "Ergänzung") + `: ${st5} von ${l5.length} Ligaeinsätzen in der Startelf` : `${st5 >= 4 ? "Stammspielerin" : st5 >= 2 ? "Rotation" : "Ergänzung"}: ${st5} der letzten ${l5.length} Ligaspiele in der Startelf${(s.spiele || []).slice(-5).some(e => e.art === "X") ? ", in denen sie im Kader stand" : ""}`}')
    h = h.replace("// Grafiken vom 25.11.2026 (Finn)", "// Grafiken vom 25.11.2026 (Finn) grafik2511_patch", 1)
    open(pfad, "w", encoding="utf-8").write(h)
    print("ok", pfad)


if __name__ == "__main__":
    main(sys.argv[1])
