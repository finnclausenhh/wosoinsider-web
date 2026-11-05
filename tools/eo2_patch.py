# Einordnung Runde 3 (Finn 05.11.2026 20:24): Ersatz-Kandidatinnen als kleine Karten mit "oder", Einplan-Ampel oben in der Box,
# Spielertyp antippen erklärt den Typ (Kader, Bestenliste, Profil), Typ im Kader nicht mehr abschneiden
import sys
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
ERKL = r'''
  const TYPERKL = {"sicherer Rückhalt": "Bleibt oft ohne Gegentor: viele Spiele zu null im Vergleich zu den anderen Torhüterinnen.",
    "mitspielende Torhüterin": "Viele Ballkontakte und angekommene Pässe, spielt mit wie eine Feldspielerin.",
    "Paraden-Torhüterin": "Bekommt viele Schüsse aufs Tor und hält viele. Bei Kickbase bringt jede Parade Punkte.",
    "komplette Innenverteidigerin": "Im Aufbau (Pässe, Ballkontakte) und im Zweikampf (gewonnene Duelle, Abwehraktionen) beide stark.",
    "Aufbauspielerin": "Eröffnet das Spiel: deutlich stärker in Pässen und Ballkontakten als im Zweikampf.",
    "groß und zweikampfstark": "Gewinnt viele Duelle und ist größer als die meisten Innenverteidigerinnen.",
    "Zweikämpferin": "Stärker gegen den Ball (Zweikämpfe, Abwehraktionen) als im Aufbau.",
    "ausgewogene Innenverteidigerin": "Aufbau und Zweikampf etwa gleich stark, ohne klaren Ausschlag.",
    "offensive Außenverteidigerin": "Mehr Schlüsselpässe, Dribblings und Torbeteiligungen als Abwehraktionen und Zweikämpfe.",
    "defensive Außenverteidigerin": "Mehr Abwehraktionen und Zweikämpfe als Offensivaktionen.",
    "ausgewogene Außenverteidigerin": "Vorne und hinten etwa gleich stark.",
    "Box-to-Box": "Gegen den Ball und nach vorne beide über dem Schnitt: läuft von Strafraum zu Strafraum.",
    "Ballverteilerin": "Am Ball am stärksten: viele Ballkontakte und angekommene Pässe, weniger Zweikämpfe und Abschlüsse.",
    "defensive Sechserin": "Räumt vor der Abwehr ab: Abwehraktionen und Zweikämpfe sind ihr stärkster Bereich.",
    "offensive Sechserin": "Sucht den Weg nach vorne: Schlüsselpässe und Torschüsse sind ihr stärkster Bereich.",
    "Spielmacherin": "Bereitet Chancen vor: Schlüsselpässe sind ihr stärkster Wert.",
    "torgefährliche Mittelfeldspielerin": "Sucht selbst den Abschluss: Torschüsse und Torbeteiligungen vorne.",
    "Dribblerin": "Geht ins Eins-gegen-eins: viele erfolgreiche Dribblings pro 90 Minuten.",
    "Vorbereiterin": "Spielt die letzten Pässe: viele Schlüsselpässe.",
    "Torjägerin von außen": "Zieht selbst ab: viele Torschüsse und Torbeteiligungen von der Außenbahn.",
    "arbeitet nach hinten mit": "Viele gewonnene Zweikämpfe für eine Außenspielerin.",
    "Zielspielerin": "Groß, hält Bälle fest und verteilt: viele Zweikämpfe und Ballkontakte, wenig Dribblings.",
    "Vollstreckerin": "Lebt vom Abschluss: Torschüsse und Torbeteiligungen weit vorne.",
    "mitspielende Stürmerin": "Legt viel für andere auf: viele Schlüsselpässe für eine Stürmerin.",
    "Mittelstürmerin": "Ohne klaren Schwerpunkt in den Werten.", "Außenspielerin": "Ohne klaren Schwerpunkt in den Werten."};
  document.addEventListener("click", e => {
    const c = e.target.closest && e.target.closest("[data-typerk]"); if (!c) return; e.preventDefault(); e.stopPropagation();
    const row = c.closest(".pf-tr, .bst") || c, an = c.classList.contains("sel");
    document.querySelectorAll("[data-typerk].sel").forEach(x => x.classList.remove("sel")); document.querySelectorAll(".typ-i").forEach(x => x.remove());
    if (an) return; c.classList.add("sel");
    const t = c.dataset.typerk; row.insertAdjacentHTML("afterend", `<span class="typ-i"><b>${esc(t[0].toUpperCase() + t.slice(1))}:</b> ${esc(TYPERKL[t] || "")} Bestimmt aus den Werten pro 90 Minuten im Vergleich zur eigenen Position, ab 270 Minuten.</span>`);
  }, true);
'''
def patch(s):
    s = rep(s, """  function typZeile(s){""", ERKL + """  function typZeile(s){""")
    # Kader: ganze Zeile, antippbar
    s = rep(s, """${typVon(s) ? `<small class="kd-ty">${esc(typVon(s)[0].toUpperCase() + typVon(s).slice(1))}</small>` : ""}""",
              """${typVon(s) ? `<small class="kd-ty" data-typerk="${esc(typVon(s))}">${esc(typVon(s)[0].toUpperCase() + typVon(s).slice(1))}</small>` : ""}""")
    s = rep(s, """.kd-ty{display:block;color:#C9D3E2;font-size:12px;margin-top:1px}""", """.pf-tx small.kd-ty{display:block;color:#C9D3E2;font-size:12px;margin-top:1px;white-space:normal;overflow:visible;cursor:pointer;text-decoration:underline dotted rgba(255,255,255,.3);text-underline-offset:3px}
[data-typerk].sel{color:#fff;text-decoration-color:#8FB0FF}.typ-i{display:block;font-size:12px;line-height:1.4;color:#C9D3E2;background:rgba(143,176,255,.1);border-radius:8px;padding:7px 9px;margin:-2px 0 8px}
.eo-plan{display:flex;align-items:center;gap:8px;border-radius:10px;padding:9px 11px;background:color-mix(in srgb,var(--c) 16%,transparent);border:1px solid color-mix(in srgb,var(--c) 45%,transparent)}
.eo-plan b{font-size:15px;color:var(--c)}.eo-plan span{font-size:12.5px;color:#C9D3E2}
.eo-vs{display:flex;align-items:stretch;gap:6px;margin-top:8px}.eo-vs i{align-self:center;font-style:normal;font:700 10px var(--f-mono);color:#8A95A8}
.eo-k{flex:1;min-width:0;display:grid;justify-items:center;gap:3px;background:rgba(255,255,255,.05);border:0;border-radius:10px;padding:8px 4px;color:inherit;font:inherit;cursor:pointer;text-align:center}
.eo-z .eo-k b{font-size:12.5px;text-transform:none;letter-spacing:0;color:#fff;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.eo-k small{font-size:10.5px;color:#A9B4C6;line-height:1.25}.eo-k .pg{display:flex;gap:4px;align-items:center;font-size:10.5px}""")
    # Bestenliste: Typ antippbar
    s = rep(s, """<small>${esc(kname(s.k))} · ${esc(typKurz(x.typ[0]))}</small>""", """<small>${esc(kname(s.k))} · <span data-typerk="${esc(x.typ[0])}" style="text-decoration:underline dotted rgba(255,255,255,.3);text-underline-offset:3px">${esc(typKurz(x.typ[0]))}</span></small>""")
    # Profil: Typ-Name antippbar
    s = rep(s, """<span class="typ-k">SPIELERTYP</span><b>${esc(d.typ[0][0].toUpperCase() + d.typ[0].slice(1))}</b>""", """<span class="typ-k">SPIELERTYP</span><b data-typerk="${esc(d.typ[0])}" style="cursor:pointer">${esc(d.typ[0][0].toUpperCase() + d.typ[0].slice(1))} <small style="font:600 11px var(--f-body,inherit);color:#8FB0FF">ⓘ</small></b>""")
    # bis zu 3 Kandidatinnen, Text nennt die ersten zwei, darunter Karten mit "oder"
    s = rep(s, """q5(y) - q5(x))).slice(0, 2);""", """q5(y) - q5(x))).slice(0, 3);""")
    s = rep(s, """kon = (ers.length ? ers : mates.filter(fit).filter(x => q5(x) < 4 && ((x.spiele || []).slice(-1)[0] || {}).art !== "S").sort(""", """kon = ers.concat(mates.filter(fit).filter(x => !ers.includes(x) && q5(x) < 4 && ((x.spiele || []).slice(-1)[0] || {}).art !== "S").sort(""")
    s = rep(s, """      if (kon.length) z.push(["Wer spielt für sie?", kon.map((x, i) => {""", """      if (kon.length) z.push(["Wer spielt für sie?", kon.slice(0, 2).map((x, i) => {""")
    s = rep(s, """}).join(" ") + typAnalyse(s, kon), 1]);""", """}).join(" ") + typAnalyse(s, kon) + ersatzKarten(kon), 1]);""")
    s = rep(s, """  function typAnalyse(s, kon){""", """  function ersatzKarten(kon){
    if (kon.length < 2) return "";
    return `<div class="eo-vs">${kon.map(x => { const st = (x.prognose || {}).st, ty = typVon(x);
      return `<button class="eo-k" data-profil="${esc(x.id)}">${pfFoto(x, 40, 40, 20)}<b>${esc(nachN(x.n))}</b>${ty ? `<small>${esc(typKurz(ty))}</small>` : ""}${st && STUFE[st] ? `<span class="pg">${stufeSym(st, 12)}${esc(STUFE[st][2])}</span>` : ""}</button>`; }).join("<i>ODER</i>")}</div>`;
  }
  function typAnalyse(s, kon){""")
    # Einplan-Ampel oben in der Box
    s = rep(s, """    return `<section class="eo">${kap("Für Kickbase")}${m.kickbase ? `<p class="eo-kb">${esc(m.kickbase)}</p>` : ""}""",
"""    const pst0 = (s.prognose || {}).st, PL = {ausgeschlossen: ["Nicht einplanen", "#FF6B6B"], unwahrscheinlich: ["Eher nicht einplanen", "#F59E0B"], unsicher: ["Unsicher, Ersatz bereithalten", "#F5C26B"], erwartet: ["Einplanen", "#4ADE80"], sicher: ["Fest einplanen", "#4ADE80"]}[pst0];
    const plan = PL && p ? `<div class="eo-plan" style="--c:${PL[1]}">${stufeSym(pst0, 18)}<b>${PL[0]}</b><span>${esc(WTL[dt(p.anstoss).getDay()])} gegen ${esc(kname(p.heim_k === k ? p.gast_k : p.heim_k))}</span></div>` : "";
    return `<section class="eo">${kap("Für Kickbase")}${plan}${m.kickbase ? `<p class="eo-kb">${esc(m.kickbase)}</p>` : ""}""")
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
