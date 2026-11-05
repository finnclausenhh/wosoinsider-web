# Profil Runde 3 (Finn 05.11.2026 nachmittags): Strahl immer (bei wenig Spielzeit mit Hinweis), Rang nach absoluten Werten pro 90 (Kickbase zählt Aktionen),
# Vergleich nach Einzelposition (IV, AV, Sechserin, zentrales Mittelfeld, Flügel, Sturm, Tor) mit eigenen Netzwerten, Paraden rot bis grün,
# Elfmeter gehalten bei Torhüterinnen, "gleichauf" als "(wie N andere)", Formkurve mit Gegnerlogos, "Um diesen Platz kämpft sie", Fotonachweis ganz unten
import sys
def rep(s, a, b, n=1, nur1=False):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b, 1) if nur1 else s.replace(a, b)
def patch(s):
    # ligaRang: Gruppe nach Einzelposition und Rohwert bei wenig Spielzeit
    s = rep(s, """  function ligaRang(s, f, filt){
    const peers = ((SPN && SPN.spielerinnen) || []).filter(x => x.pos === s.pos && (x.spiele || []).reduce((a, e) => a + (e.min || 0), 0) >= 270 && (!filt || filt(x)));
    const w = f(s); if (w == null || peers.length < 8) return null;""", """  // Einzelposition aus dem Hauptplatz (Finn 05.11.2026)
  const PGRP = x => { const t = String(((x.slots || [])[0] || [])[2] || ""); return t === "Tor" ? "TW" : /^Innenverteidigerin/.test(t) ? "IV" : /verteidigerin|Schienenspielerin/.test(t) ? "AV" : /^Sechserin/.test(t) ? "DM"
    : /^(Flügel|Mittelfeld (links|rechts))/.test(t) ? "FL" : /Zehnerin|Offensives Mittelfeld|Zentrales Mittelfeld|^Mittelfeld$/.test(t) ? "ZM" : /^Sturm|Mittelstürmerin/.test(t) ? "ST" : null; };
  const GLAB = {TW: "Torhüterinnen", IV: "Innenverteidigerinnen", AV: "Außenverteidigerinnen", DM: "Sechserinnen", ZM: "zentralen Mittelfeldspielerinnen", FL: "Flügelspielerinnen", ST: "Stürmerinnen"};
  let ROH = 0; const ab = n => ROH ? 0 : n;
  function ligaRang(s, f, filt, grp){
    const peers = ((SPN && SPN.spielerinnen) || []).filter(x => (grp ? PGRP(x) === grp : x.pos === s.pos) && (x.spiele || []).reduce((a, e) => a + (e.min || 0), 0) >= 270 && (!filt || filt(x)));
    let w = f(s), wenig = 0; if (w == null) { ROH = 1; try { w = f(s); } finally { ROH = 0; } wenig = 1; }
    if (w == null || peers.length < 8) return null;""")
    s = rep(s, """    const vals = peers.map(f).filter(v => v != null); if (vals.length < 8) return null;
    const eq = vals.filter(v => Math.abs(v - w) < 1e-9).length, p = Math.round((vals.filter(v => v < w - 1e-9).length + (eq - 1) / 2) / (vals.length - 1) * 100);
    const pl = 1 + vals.filter(v => v > w + 1e-9).length, mn = Math.min(...vals), mx = Math.max(...vals), mw = vals.reduce((a, b) => a + b, 0) / vals.length;
    return {p: Math.max(0, Math.min(100, p)), n: vals.length, platz: pl, min: mn, max: mx, mw, w, eq};""",
"""    const vals0 = peers.filter(x => x.id !== s.id).map(f).filter(v => v != null); if (vals0.length < 7) return null;
    const vals = vals0.concat([w]);
    const eq = vals.filter(v => Math.abs(v - w) < 1e-9).length, p = Math.round((vals.filter(v => v < w - 1e-9).length + (eq - 1) / 2) / (vals.length - 1) * 100);
    const pl = 1 + vals.filter(v => v > w + 1e-9).length, mn = Math.min(...vals), mx = Math.max(...vals), mw = vals.reduce((a, b) => a + b, 0) / vals.length;
    return {p: Math.max(0, Math.min(100, p)), n: vals.length, platz: pl, min: mn, max: mx, mw, w, eq, wenig};""")
    # Gruppe im Block Weitere Werte
    s = rep(s, """      const P = PLURAL[s.pos] || "Spielerinnen", d1 = v => dez(v, 1), pc = v => Math.round(v * 100) + " %";""",
"""      const GR = PGRP(s), GRok = GR && ((SPN && SPN.spielerinnen) || []).filter(x => PGRP(x) === GR && M(x) >= 270).length >= 8;
      const P = GRok ? GLAB[GR] : (PLURAL[s.pos] || "Spielerinnen"), d1 = v => dez(v, 1), pc = v => Math.round(v * 100) + " %";
      const LR = (s, f) => ligaRang(s, f, null, GRok ? GR : null);""")
    a = s.index("      if (st.sch && s.pos !== \"TW\") ww.push(")
    b = s.index("      const pfarbe0 = p =>", a)
    blk = s[a:b]
    blk = blk.replace("ligaRang(s, ", "LR(s, ")
    blk = blk.replace("LR(s, x => Sx(x).zk_ges >= 10 ? Sx(x).zk_w / Sx(x).zk_ges : null)", "LR(s, x => Sx(x).zk_ges >= ab(10) && M(x) ? Sx(x).zk_w / M(x) * 90 : null)")
    blk = blk.replace("LR(s, x => Sx(x).p_ges >= 50 ? Sx(x).p_ok / Sx(x).p_ges : null)", "LR(s, x => Sx(x).p_ges >= ab(50) && M(x) ? Sx(x).p_ok / M(x) * 90 : null)")
    blk = blk.replace("af.drib[1] >= 5 ? LR(s, x => { const d = (afSp(x.id) || {}).drib; return d && d[1] >= 5 ? d[0] / d[1] : null; }) : null", "LR(s, x => { const d = (afSp(x.id) || {}).drib; return d && d[1] >= ab(5) && M(x) ? d[0] / M(x) * 90 : null; })")
    blk = blk.replace("(r => r ? Object.assign({}, r, {neutral: 1}) : null)(LR(s, x => (afSp(x.id) || {}).parsp >= 3 ? afSp(x.id).par / afSp(x.id).parsp : null))", "LR(s, x => (afSp(x.id) || {}).parsp >= ab(3) ? afSp(x.id).par / afSp(x.id).parsp : null)")
    blk = blk.replace("return q && q[3] >= 270 ?", "return q && q[3] >= ab(270) ?")
    blk = blk.replace("M(x) >= 270 ?", "M(x) >= ab(270) ?")
    for k in ["Sx(x).zk_ges >= ab(10)", "Sx(x).p_ges >= ab(50)", "d[1] >= ab(5) && M(x)", "parsp >= ab(3)", "q[3] >= ab(270)"]:
        assert k in blk, k
    # Elfmeter bei Torhüterinnen: gehalten statt nicht verwandelt, Rang nach Anzahl gehaltener
    old = """        if (e && e[0]) ww.push([`${e[1]}/${e[0]}`, `Elfmeter nicht verwandelt (${Math.round(e[1] / e[0] * 100)} %)`, `${e[0]} gegen sie seit ${(li.saisons || [""])[0]}${e[2] ? `, ${e[2]} sicher gehalten` : ""}${lq != null ? ` · Liga trifft ${lq} %` : ""}`, er]); }"""
    assert old in blk
    blk = blk.replace(old, """        if (e && e[0]) ww.push([`${e[2] || 0}/${e[0]}`, "Elfmeter gehalten", `${e[1]} von ${e[0]} nicht verwandelt · seit ${(li.saisons || [""])[0]}${lq != null ? ` · Liga trifft ${lq} %` : ""}`, er]); }""")
    old2 = """const w = e[1] / e[0];"""
    assert old2 in blk
    blk = blk.replace("""const v = Object.values(AF.elf_tw).filter(q => q[0] >= 4).map(q => q[1] / q[0]);""", """const v = Object.values(AF.elf_tw).filter(q => q[0] >= 4).map(q => q[2] || 0);""")
    blk = blk.replace(old2, "const w = e[2] || 0;")
    s = s[:a] + blk + s[b:]
    # Texte: gleichauf, Paraden-Sonderfall raus, Hinweis bei wenig Spielzeit
    s = rep(s, """      const rText = r => { const mit = r.eq > 1 ? `, gleichauf mit ${r.eq - 1}` : "";""", """      const rText = r => { const mit = r.eq > 1 ? ` (wie ${r.eq - 1} ${r.eq === 2 ? "andere" : "andere"})` : "";""")
    s = rep(s, """${esc(rText(w[3]).replace(/, gleichauf mit \\d+$/, ""))}""", """${esc(rText(w[3]).replace(/ \\(wie \\d+ andere\\)$/, ""))}""")
    s = rep(s, """<span class="rg" style="color:${rFarbe(r)}">Platz ${r.platz} von ${r.n}</span><span class="ps">${esc(rText(r))}</span>""",
"""<span class="rg" style="color:${rFarbe(r)}">Platz ${r.platz} von ${r.n}</span><span class="ps">${esc(rText(r))}${r.wenig ? '<br><i class="wenig">wenig Spielzeit, Wert schwankt noch</i>' : ""}</span>""")
    s = rep(s, """Platz und Prozent: Vergleich mit allen ${esc(P)} der Liga ab 270 Minuten. Rot, gelb, grün zeigt, wo sie in der Liga steht.${ww.some(w => w[3] && w[3].neutral) ? " Paraden in Blau ohne Wertung: wenige Paraden heißen oft nur, dass die Abwehr wenig zulässt." : ""}""",
"""Platz und Prozent: Vergleich mit allen ${esc(P)} der Liga ab 270 Minuten, gezählt pro 90 Minuten, denn Kickbase wertet jede Aktion. Rot, gelb, grün zeigt, wo sie in der Liga steht.""")
    # Netz: Werte je Einzelposition
    s = rep(s, """        const nz = mitR.slice(0, 6);""", """        const NETZ = {IV: ["Zweikämpfe", "Abwehrarbeit", "Passquote", "Ballkontakte", "Torschüsse", "Torbeteiligungen"], AV: ["Abwehrarbeit", "Zweikämpfe", "Schlüsselpässe", "Dribblings", "Passquote", "Torbeteiligungen"],
          DM: ["Abwehrarbeit", "Passquote", "Ballkontakte", "Zweikämpfe", "Schlüsselpässe", "Torschüsse"], ZM: ["Schlüsselpässe", "Passquote", "Ballkontakte", "Torschüsse", "Torbeteiligungen", "Abwehrarbeit"],
          FL: ["Torschüsse", "Torbeteiligungen", "Dribblings", "Schlüsselpässe", "Zweikämpfe", "Ballkontakte"], ST: ["Torschüsse", "Torbeteiligungen", "Dribblings", "Schlüsselpässe", "Zweikämpfe", "Ballkontakte"]}[GR];
        const nzW = NETZ ? NETZ.map(t => mitR.find(w => w[4] === t)).filter(Boolean) : [];
        const nz = nzW.concat(mitR.filter(w => w[4] && !nzW.includes(w))).slice(0, 6);""")
    s = rep(s, """.ww-netz{width:100%;max-width:360px;justify-self:center;display:block;overflow:visible}""", """.ww-netz{width:100%;max-width:360px;justify-self:center;display:block;overflow:visible}
.af-ww .ps .wenig{font-style:normal;font-size:10.5px;color:var(--muted);opacity:.8}
.fk-lg{position:relative;height:18px;margin:-2px 0 2px}.fk-lg button{position:absolute;top:0;transform:translateX(-50%);background:none;border:0;padding:0;cursor:pointer;line-height:0}
.fk-lg button.an{outline:1.5px solid #8FB0FF;outline-offset:2px;border-radius:50%}.fk-info{font-size:12px;color:#C9D3E2;min-height:16px;margin:2px 0 0}""")
    # Formkurve: Gegnerlogos unter den Punkten, Antippen zeigt Gegner und Note
    s = rep(s, """      ${sp.map(e => `<text x="${X(e.md).toFixed(1)}" y="${H - 3}" fill="rgba(169,180,198,.8)" font-size="9" font-family="ui-monospace,monospace" text-anchor="middle">${e.md}.</text>`).join("")}
    </svg><div class="af-st" style="display:flex;justify-content:space-between"><span>Linie: Note je Spieltag ab 60 Minuten</span><span>gestrichelt: Ø ${dez(af.avg)}</span></div>`;""",
"""      ${sp.map(e => `<text x="${X(e.md).toFixed(1)}" y="${H - 3}" fill="rgba(169,180,198,.8)" font-size="9" font-family="ui-monospace,monospace" text-anchor="middle">${e.md}.</text>`).join("")}
    </svg><div class="fk-lg">${sp.map(e => { const k = KURZ[e.gegner], n = voll.find(x => x[0] === e.md);
      return k ? `<button style="left:${(X(e.md) / W * 100).toFixed(1)}%" data-fk="${esc(`${e.md}. Spieltag ${e.ha === "A" ? "in" : "gegen"} ${kname(k)}${n ? ": Note " + dez(n[1]) : e.art === "S" || e.art === "E" ? `: ${e.min} Minuten, keine Note` : ": nicht gespielt"}`)}" aria-label="${esc(kname(k))}">${logo(k, 14)}</button>` : ""; }).join("")}</div>
    <p class="fk-info"></p><div class="af-st" style="display:flex;justify-content:space-between"><span>Punkt = Note im Spiel, je grüner, desto besser</span><span>gestrichelt: Ø ${dez(af.avg)}</span></div>`;""")
    s = rep(s, """  function formkurve(s){""", """  document.addEventListener("click", e => { const b = e.target.closest && e.target.closest("[data-fk]"); if (!b) return; e.preventDefault(); e.stopPropagation();
    const box = b.closest(".fk-lg"), an = b.classList.contains("an"); box.querySelectorAll("button").forEach(x => x.classList.remove("an"));
    const t = box.nextElementSibling; if (an) { t.textContent = ""; return; } b.classList.add("an"); t.textContent = b.dataset.fk; }, true);
  function formkurve(s){""")
    # Wer sie ersetzt / Um diesen Platz kämpft sie
    s = rep(s, """      const ers = (s.ersatz || []).map(r => `<div class="pf-er"><b>${esc(r.n)}</b><span>${[r.s ? r.s + "x für sie in der Startelf" : "", r.w ? r.w + "x für sie eingewechselt" : ""].filter(Boolean).join(" · ")}</span></div>`).join("");""",
"""      const kaempft = rolleS[0] !== "STAMMPLATZ", ers = (s.ersatz || []).map(r => `<div class="pf-er"><b>${esc(r.n)}</b><span>${[r.s ? r.s + (kaempft ? "x statt ihr in der Startelf" : "x für sie in der Startelf") : "", r.w ? r.w + "x für sie eingewechselt" : ""].filter(Boolean).join(" · ")}</span></div>`).join("");""", 2, True)
    s = rep(s, """      const ers = (s.ersatz || []).map(r => `<div class="pf-er"><b>${esc(r.n)}</b><span>${[r.s ? r.s + "x für sie in der Startelf" : "", r.w ? r.w + "x für sie eingewechselt" : ""].filter(Boolean).join(" · ")}</span></div>`).join("");""",
"""      const kaempft = rolle[0] !== "STAMMPLATZ", ers = (s.ersatz || []).map(r => `<div class="pf-er"><b>${esc(r.n)}</b><span>${[r.s ? r.s + (kaempft ? "x statt ihr in der Startelf" : "x für sie in der Startelf") : "", r.w ? r.w + "x für sie eingewechselt" : ""].filter(Boolean).join(" · ")}</span></div>`).join("");""")
    s = rep(s, """        ${kap("Wer sie ersetzt")}${ers || '<div class="pf-er"><span>Bisher keine, sie hat immer selbst gespielt.</span></div>'}</section>`;""",
"""        ${kap(kaempft ? "Um diesen Platz kämpft sie" : "Wer sie ersetzt")}${ers || `<div class="pf-er"><span>${kaempft ? "Noch keine Konkurrenz erfasst." : "Bisher keine, sie hat immer selbst gespielt."}</span></div>`}</section>`;""", 2)
    # Fotonachweis nach "Mehr aus dem Kader"
    s = rep(s, """    h += `<div class="pf-fuss">${f && f.autor ? esc(nachweis(f).replace(/<[^>]+>/g, "")) + " · " : ""}Daten: Sportschau, Vereine, eigene Auswertung</div>`;
    h += pfWeiter(s);""", """    h += pfWeiter(s);
    h += `<div class="pf-fuss">${f && f.autor ? esc(nachweis(f).replace(/<[^>]+>/g, "")) + " · " : ""}Daten: Sportschau, Vereine, eigene Auswertung</div>`;""")
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
