#!/usr/bin/env python3
"""Moment-Analysen im Ticker (Finn 26.11.2026): grafik.typ "analyse" mit Abschnitten und vier Grafiken
(perzentil, streu, verlauf, strahl). Daten baut fbl-daten/tools/moment_analyse.py.

- Headline bei Analysen 24 px (höchstens zweizeilig).
- Absätze ab dem zweiten, Abschnitte (Zwischenüberschrift, Grafik, Text) und Fazit kommen aus anGrafik.

Aufruf: python3 tools/moment_patch.py ticker/index.html [weitere Dateien, z. B. die index.html des Artifacts]
Passt auf Ticker und Artifact (Anker: ".ntg{", "const zgGrafik = m =>", h1 im Artikel).
"""
import sys

CSS = r"""
.an{display:grid;gap:14px;margin-top:6px}.an h2{margin:8px 0 0;font:800 21px/1.15 Inter,system-ui,sans-serif}
.an p{margin:0;font-size:16px;line-height:1.55;color:#DFE3EE}.an .an-daten{font-size:12px;color:var(--muted);font-style:italic}
.an-k{background:var(--card);border-radius:14px;padding:14px;display:grid;gap:11px}
.an-t{font:italic 800 21px/1.05 var(--f-display);letter-spacing:.02em}
.an-chips{display:flex;gap:6px;flex-wrap:wrap}.an-chips span{font-size:10px;font-weight:700;border:1px solid #3A4A72;border-radius:4px;padding:2px 6px}
.an-fuss{display:flex;justify-content:space-between;align-items:center}.an-fuss b{font-size:15px;letter-spacing:.08em}.an-fuss b i{font-style:normal;color:#5D7BFF}.an-fuss small{font-size:10px;color:var(--muted)}
.an-ini{display:inline-flex;align-items:center;justify-content:center;background:#2A3757;color:var(--muted);font-size:10px;font-weight:700}
.an-kopf{display:flex;gap:10px;align-items:center}.an-kopf .f{width:52px;height:52px;border-radius:50%;object-fit:cover;background:#2A3757;flex:none}
.an-kopf div{display:grid;gap:2px;flex:1;min-width:0}.an-kopf b{font:italic 800 22px/1 var(--f-display)}.an-kopf small{font-size:11px;color:var(--muted)}
.an-bl{background:#1B2747;border-radius:10px;padding:10px 12px;display:grid;gap:7px}.an-bl>b{font:italic 800 14px var(--f-display);letter-spacing:.06em;color:#C9D2E8}
.an-z{display:grid;grid-template-columns:minmax(0,1fr) 46px 64px 26px;gap:8px;align-items:center;font-size:12px}.an-z em{font-style:normal;text-align:right;color:#C9D2E8}
.an-bar{height:6px;background:#2A3757;border-radius:3px}.an-bar i{display:block;height:6px;border-radius:3px}.an-z strong{text-align:right}
.an-leg{display:flex;flex-wrap:wrap;gap:8px;font-size:10px;color:var(--muted);justify-content:center}.an-leg span{display:flex;gap:4px;align-items:center}.an-leg i{width:8px;height:8px;border-radius:2px}
.an-mini{font-size:10px;color:var(--muted);text-align:center}
.an-plot{position:relative;height:300px;margin:6px 4px 22px 34px;border-left:1px solid #3A4A72;border-bottom:1px solid #3A4A72}
.an-plot .pt{position:absolute;width:8px;height:8px;margin:-4px 0 0 -4px;border-radius:50%;background:#55617F}
.an-plot .lb{position:absolute;display:flex;align-items:center;gap:5px;transform:translate(-14px,-14px);font-size:11px;font-weight:700;color:#C9D2E8;white-space:nowrap}
.an-plot .lb.r{flex-direction:row-reverse;transform:translate(calc(-100% + 14px),-14px)}.an-plot .lb img,.an-plot .lb .an-ini{width:28px;height:28px;border-radius:50%;object-fit:cover;border:2px solid #C9D2E8;background:#2A3757}
.an-plot .lb.ich{color:#fff}.an-plot .lb.ich img,.an-plot .lb.ich .an-ini{border-color:#5D7BFF}
.an-plot .mx{position:absolute;top:0;bottom:0;border-left:1px solid #3A4A72}.an-plot .my{position:absolute;left:0;right:0;border-top:1px solid #3A4A72}
.an-plot .ec{position:absolute;right:4px;top:4px;font-size:9px;font-weight:700;color:#7B93FF;letter-spacing:.05em}
.an-plot .ty{position:absolute;left:-32px;width:26px;text-align:right;font-size:10px;color:var(--muted);transform:translateY(-50%)}.an-plot .tx{position:absolute;bottom:-18px;font-size:10px;color:var(--muted);transform:translateX(-50%)}
.an-ya{writing-mode:vertical-rl;transform:rotate(180deg);font-size:10px;color:var(--muted);position:absolute;left:-2px;top:0;height:300px;text-align:center}
.an-vl{position:relative;padding-top:22px}.an-vl .bs{display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:5px;align-items:end;height:126px;border-bottom:1px solid #3A4A72}
.an-vl .bs div{display:flex;flex-direction:column;justify-content:flex-end;align-items:center;gap:3px;height:100%}.an-vl .bs small{font-size:10px;font-weight:700;color:#C9D2E8}
.an-vl .bs i{width:100%;display:block;border-radius:4px 4px 0 0}.an-vl .ts{display:grid;grid-template-columns:repeat(var(--n),minmax(0,1fr));gap:5px;text-align:center;font-size:10px;color:var(--muted);margin-top:4px}
.an-vl .af{position:absolute;top:0;border-top:2px solid #F08A3C;text-align:center;font-size:10px;font-weight:700;color:#FFB27A;padding-top:2px;white-space:nowrap}
.an-kz{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px;text-align:center}.an-kz div{background:#1F2C4F;border-radius:10px;padding:8px 4px;display:grid}.an-kz b{font:800 22px var(--f-display)}.an-kz span{font-size:10px;color:var(--muted)}
.an-sr{display:grid;gap:4px}.an-sr .kp{display:flex;justify-content:space-between;font-size:12px}.an-sr .kp b{font-weight:600}.an-sr .kp em{font-style:normal;font-weight:700}
.an-sr .ln{position:relative;height:28px;margin:0 13px}.an-sr .ln:before{content:"";position:absolute;left:-13px;right:-13px;top:13px;border-top:2px solid #26324F}
.an-sr .ln i{position:absolute;top:9px;width:10px;height:10px;margin-left:-5px;border-radius:50%;background:#55617F}.an-sr .ln .me{position:absolute;top:1px;width:26px;height:26px;margin-left:-13px;display:block}
.an-sr .ln .me img,.an-sr .ln .me .an-ini{display:block;width:26px;height:26px;max-width:none;box-sizing:border-box;border-radius:50%;object-fit:cover;border:2px solid #5D7BFF;background:#2A3757}
.an-sr .mm{display:flex;justify-content:space-between;font-size:9px;color:var(--muted)}
"""

JS = r"""
  // ---------------- Moment-Analysen (Finn 26.11.2026): grafik.typ "analyse", Daten aus tools/moment_analyse.py
  const AN_F = p => p < 20 ? "#E5484D" : p < 40 ? "#F08A3C" : p < 60 ? "#E6C84A" : p < 80 ? "#9FD356" : p < 95 ? "#2FBF6B" : "#22D3C5";
  const anFoto = (n, cls = "") => { const f = FOTOS[n] || {}, s = f.portrait || f.datei; const ini = String(n || "").split(" ").map(w => w[0] || "").join("").slice(0, 2);
    return s ? `<img class="${cls}" src="${esc(s)}" alt="" loading="lazy">` : `<span class="${cls} an-ini">${esc(ini)}</span>`; };
  const anKurz = n => { const t = String(n || "").split(" "); return t.length > 1 ? t[0][0] + ". " + t.slice(1).join(" ") : n; };
  const anChips = c => `<div class="an-chips">${(c || []).map(x => `<span>${esc(x)}</span>`).join("")}</div>`;
  const anFuss = q => `<div class="an-fuss"><b class="disp">WOSO<i>INSIDER</i></b><small>${esc(q)}</small></div>`;
  function anPerz(g){
    const leg = [[0,"0–19"],[20,"20–39"],[40,"40–59"],[60,"60–79"],[80,"80–94"],[95,"95–100"]].map(([p, t]) => `<span><i style="background:${AN_F(p)}"></i>${t}</span>`).join("");
    return `<div class="an-k"><div class="an-kopf">${anFoto(g.n, "f")}<div><b>${esc(anKurz(g.n).toUpperCase())}</b><small>${esc([g.hinweis, (g.vgl - 1) + " Vergleichsspielerinnen"].filter(Boolean).join(" · "))}</small></div>${anChips([g.pos, g.min + " Min."])}</div>
      ${(g.bl || []).map(b => `<div class="an-bl"><b>// ${esc(b.t)}</b>${b.z.map(z => `<div class="an-z"><span>${esc(z.l)}${z.hb ? "" : " ▾"}</span><em>${esc(z.w)}</em><span class="an-bar"><i style="width:${Math.max(z.p, 3)}%;background:${AN_F(z.p)}"></i></span><strong style="color:${AN_F(z.p)}">${z.p}</strong></div>`).join("")}</div>`).join("")}
      <div class="an-leg">${leg}</div><div class="an-mini">Perzentil · Werte pro 90 Min. · ▾ weniger ist besser · Ballgewinne = Tacklings + Interceptions</div>${anFuss("Daten: API-Football")}</div>`;
  }
  function anStreu(g){
    const P = g.p || []; if (!P.length) return "";
    const rx = P.map(p => p.x), ry = P.map(p => p.y), pad = (a, b) => (b - a) * 0.08 || 1;
    const x0 = Math.min(...rx) - pad(Math.min(...rx), Math.max(...rx)), x1 = Math.max(...rx) + pad(Math.min(...rx), Math.max(...rx));
    const y0 = Math.min(...ry) - pad(Math.min(...ry), Math.max(...ry)), y1 = Math.max(...ry) + pad(Math.min(...ry), Math.max(...ry));
    const X = v => ((v - x0) / (x1 - x0) * 100).toFixed(1), Y = v => (100 - (v - y0) / (y1 - y0) * 100).toFixed(1);
    const tick = (a, b) => { const s = [0.1,0.2,0.5,1,2,5,10,20,50].find(s => (b - a) / s <= 5) || 100, o = []; for (let v = Math.ceil(a / s) * s; v <= b; v += s) o.push(+v.toFixed(2)); return o; };
    const pts = P.filter(p => !p.l).map(p => `<i class="pt" style="left:${X(p.x)}%;top:${Y(p.y)}%"></i>`).join("");
    // Beschriftungen, die sich überdecken würden, senkrecht auseinanderschieben
    const L = P.filter(p => p.l).map(p => ({p, x: +X(p.x), y: +Y(p.y)})).sort((a, b) => a.y - b.y);
    L.forEach((a, i) => L.slice(0, i).forEach(b => { if (Math.abs(a.x - b.x) < 40 && a.y - b.y < 11) a.y = b.y + 11; }));
    const lbs = L.sort((a, b) => a.p.ich - b.p.ich).map(({p, x, y}) => `<span class="lb${p.ich ? " ich" : ""}${x > 62 ? " r" : ""}" style="left:${x}%;top:${Math.min(y, 97)}%">${anFoto(p.n)}<span>${esc(anKurz(p.n))}</span></span>`).join("");
    return `<div class="an-k"><span class="an-t">// ${esc(g.titel)}</span>${anChips(g.chips)}
      <div style="position:relative"><span class="an-ya">${esc(g.y)}</span><div class="an-plot">
        ${tick(y0, y1).map(v => `<span class="ty" style="top:${Y(v)}%">${dez(v, v % 1 ? 1 : 0)}</span>`).join("")}${tick(x0, x1).map(v => `<span class="tx" style="left:${X(v)}%">${dez(v, v % 1 ? 1 : 0)}</span>`).join("")}
        <span class="mx" style="left:${X(g.mx)}%"></span><span class="my" style="top:${Y(g.my)}%"></span><span class="ec">${esc(g.ecke || "")}</span>${pts}${lbs}</div></div>
      <div class="an-mini">${esc(g.x)} · Linien = Median</div>${anFuss("Daten: API-Football")}</div>`;
  }
  function anVerlauf(g){
    const S = g.s || [], n = S.length; if (!n) return "";
    const F = {S: "#2FBF6B", E: "#E6C84A", B: "#55617F", X: "#2A3757"}, W = {S: "Startelf", E: "eingewechselt", B: "Bank", X: "nicht im Kader"};
    const af = g.ausfall && S.findIndex(s => s.md === g.ausfall[0]), bis = g.ausfall && S.findIndex(s => s.md === g.ausfall[1]);
    const ein = S.find((s, i) => i > bis && s.min > 0), start = S.find((s, i) => i > bis && s.art === "S"), letzt = S[n - 1];
    const kz = g.ausfall && ein ? [[ein.min, `Min. Comeback (${ein.md}.)`], start && start !== ein ? [start.min, `Min. Startelf (${start.md}.)`] : null, letzt !== ein && letzt !== start ? [letzt.min, `Min. ${W[letzt.art] || ""} (${letzt.md}.)`] : null].filter(Boolean) : [];
    return `<div class="an-k"><span class="an-t">// ${esc(g.titel || "EINSATZZEIT")}</span>${anChips(["Bundesliga", "Minuten je Spieltag"])}
      <div class="an-vl" style="--n:${n}">${af >= 0 && bis >= 0 ? `<span class="af" style="left:calc(${af} * 100% / ${n});width:calc(${bis - af + 1} * 100% / ${n})">${esc(g.ausfall[2] || "Ausfall")}</span>` : ""}
        <div class="bs">${S.map(s => `<div><small>${s.min || ""}</small><i style="height:${Math.max(Math.round(s.min / 90 * 100), 3)}%;background:${F[s.art] || F.X}"></i></div>`).join("")}</div>
        <div class="ts">${S.map(s => `<span>${s.md}<br>${esc(s.gk || "")}</span>`).join("")}</div></div>
      <div class="an-leg">${Object.keys(W).map(k => `<span><i style="background:${F[k]}"></i>${W[k]}</span>`).join("")}</div>
      ${kz.length ? `<div class="an-kz">${kz.map(([v, t]) => `<div><b>${v}</b><span>${esc(t)}</span></div>`).join("")}</div>` : ""}${anFuss("Daten: Spielberichte")}</div>`;
  }
  function anStrahl(g){
    const Z = g.z || [];
    const fm = (k, v) => k === "pq" || k === "zq" ? dez(v, 0) + " %" : k === "note" || k === "pass" ? dez(v, 1) : dez(v, 2);
    return `<div class="an-k"><span class="an-t">// ${esc(g.titel)}</span>${anChips(g.chips)}
      ${Z.map(z => { const a = z.alle.concat([z.ich]), lo = Math.min(...a), hi = Math.max(...a), P = v => hi > lo ? ((v - lo) / (hi - lo) * 100).toFixed(1) : 50;
        return `<div class="an-sr"><div class="kp"><b>${esc(z.l.replace(" %", "").replace(" Ø", ""))}</b><span><em>${esc(z.w)}</em><em style="color:${z.rang === 1 ? "#22D3C5" : "var(--muted)"}"> · Platz ${z.rang}/${z.von}</em></span></div>
          <div class="ln">${z.alle.map(v => `<i style="left:${P(v)}%"></i>`).join("")}<span class="me" style="left:${P(z.ich)}%">${anFoto(g.n)}</span></div>
          <div class="mm"><span>${fm(z.k, z.hb ? lo : hi)}</span><span>${fm(z.k, z.hb ? hi : lo)}</span></div></div>`; }).join("")}
      ${g.hinweis ? `<div class="an-mini" style="color:#FFB27A">${esc(g.hinweis)}</div>` : ""}${anFuss("Daten: API-Football, Spielberichte")}</div>`;
  }
  const AN_G = {perzentil: anPerz, streu: anStreu, verlauf: anVerlauf, strahl: anStrahl};
  function anGrafik(m){
    const g = m.grafik || {};
    return `<section class="an">${(m.text || []).slice(1).map(p => `<p>${esc(p)}</p>`).join("")}
      ${(g.abschnitte || []).map(a => `<h2>${esc(a.h)}</h2>${a.g && AN_G[a.g.typ] ? AN_G[a.g.typ](a.g) : ""}${(a.text || []).map(p => `<p>${esc(p)}</p>`).join("")}`).join("")}
      ${(g.fazit || []).length ? `<h2>Fazit</h2>${g.fazit.map(p => `<p>${esc(p)}</p>`).join("")}` : ""}${g.daten ? `<p class="an-daten">${esc(g.daten)}</p>` : ""}</section>`;
  }
"""

def patch(pfad):
    s = open(pfad, encoding="utf-8").read()
    if "function anGrafik(m)" in s: print(pfad, "schon gepatcht"); return
    i = s.find(".ntg{")
    assert i > 0, "CSS-Anker .ntg{ fehlt"
    s = s[:i] + CSS.strip() + "\n" + s[i:]
    a = "const zgGrafik = m => !m.grafik ? \"\" : "
    assert s.count(a) == 1, "Anker zgGrafik fehlt oder doppelt"
    s = s.replace(a, JS.strip("\n") + "\n  " + a + "m.grafik.typ === \"analyse\" ? anGrafik(m) : ")
    h = '<h1 class="disp" style="font-size:30px">${esc(m.headline)}</h1>'
    assert s.count(h) >= 1, "Anker h1 fehlt"
    s = s.replace(h, '<h1 class="disp" style="font-size:${m.grafik && m.grafik.typ === "analyse" ? 24 : 30}px">${esc(m.headline)}</h1>')
    open(pfad, "w", encoding="utf-8").write(s); print(pfad, "gepatcht")

for p in sys.argv[1:] or ["ticker/index.html"]:
    patch(p)
