# Feinschliff (Finn 05.11.2026 20:45): Abwehrarbeit "12 Aktionen", Fotos in "Die Besten" größer mit Note, IV-Kurzform, kein "Ebenfalls" nach Platz 10 bei Note,
# Kurzeinsatz in der News senkt die Einplan-Ampel, Rückkehr mit Ausblick
import sys
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    s = rep(s, """sum + " · " + dez(w, 1) + "/90"]); }""", """sum + " Aktionen · " + dez(w, 1) + "/90"]); }""")
    s = rep(s, """gezählt pro 90 Minuten, denn Kickbase wertet jede Aktion.""", """gezählt pro 90 Minuten (/90), denn Kickbase wertet jede Aktion.""")
    s = rep(s, """${pfFoto(s, 34, 34, 17)}<span class="nm"><b>${esc(s.n)}</b>""", """${pfFoto(s, 46, 46, 23)}<span class="nm"><b>${esc(s.n)}</b>""")
    s = rep(s, """.bst{display:grid;grid-template-columns:18px 34px minmax(0,1fr) auto;""", """.bst{display:grid;grid-template-columns:18px 46px minmax(0,1fr) auto;""")
    s = rep(s, """<span class="sc" style="color:${x.wert >= 67 ? "#4ADE80" : x.wert >= 45 ? "#F5C26B" : "#FF8A8A"}">${x.wert}</span>""",
              """<span class="sc" style="color:${x.wert >= 67 ? "#4ADE80" : x.wert >= 45 ? "#F5C26B" : "#FF8A8A"}">${x.wert}${(afSp(s.id) || {}).avg ? `<small class="bnt">Note ${dez(afSp(s.id).avg)}</small>` : ""}</span>""")
    s = rep(s, """.bst .sc{font:800 20px var(--f-display)}""", """.bst .sc{font:800 20px var(--f-display);text-align:right;line-height:1}.bst .bnt{display:block;font:600 10.5px var(--f-body,inherit);color:#A9B4C6;margin-top:2px}""")
    s = rep(s, """ "komplette Innenverteidigerin": "komplett",""", """ "komplette Innenverteidigerin": "Aufbau und Zweikampf",""")
    s = rep(s, """${mehr.length ? `<div class="st-erkl">Ebenfalls ${stFmt(k, l[n - 1][k])}: ${stNamen(mehr)}</div>` : ""}""", """${mehr.length && k !== "note" ? `<div class="st-erkl">Ebenfalls ${stFmt(k, l[n - 1][k])}: ${stNamen(mehr)}</div>` : ""}""")
    # Einplan-Ampel: Kurzeinsatz laut News kappt auf "unwahrscheinlich"; Rückkehr bekommt einen Ausblick
    s = rep(s, """    const pst0 = (s.prognose || {}).st, PL = {""", """    const KZE = /(Kurzeinsatz|ein paar Minuten|einige Minuten|wenige Minuten|Minuten sammeln|von der Bank kommen|Einsatz von der Bank)/i.test([m.headline, m.kickbase].concat(m.text || []).join(" "));
    let pst0 = (s.prognose || {}).st; if (KZE && ["sicher", "erwartet", "unsicher"].includes(pst0)) pst0 = "unwahrscheinlich";
    const vorher = (s.spiele || []).filter(e => e.art !== "X"), stV = vorher.filter(e => e.art === "S").length;
    const ausblick = zurueck && (KZE || pst0 === "unwahrscheinlich" || pst0 === "unsicher") && vorher.length >= 3 && stV / vorher.length >= .5
      ? `Danach wieder Startelf-Kandidatin: Vor dem Ausfall stand sie in ${stV} von ${vorher.length} Ligaspielen in der Startelf.` : "";
    const PL = {""")
    s = rep(s, """unwahrscheinlich: ["Eher nicht einplanen", "#F59E0B"]""", """unwahrscheinlich: [KZE ? "Diesmal nur Kurzeinsatz" : "Eher nicht einplanen", "#F59E0B"]""")
    s = rep(s, """<b>${PL[0]}</b><span>${esc(WTL[dt(p.anstoss).getDay()])} gegen ${esc(kname(p.heim_k === k ? p.gast_k : p.heim_k))}</span></div>` : "";""",
              """<b>${PL[0]}</b><span>${esc(WTL[dt(p.anstoss).getDay()])} gegen ${esc(kname(p.heim_k === k ? p.gast_k : p.heim_k))}</span></div>${ausblick ? `<p class="eo-aus">${esc(ausblick)}</p>` : ""}` : "";""")
    s = rep(s, """.eo-plan b{font-size:15px;color:var(--c)}""", """.eo-plan b{font-size:15px;color:var(--c)}.eo-aus{margin:-4px 0 0;font-size:13px;color:#4ADE80;line-height:1.4}""")
    s = rep(s, '''const z = [], M = x => (x.spiele || []).reduce((a, e) => a + (e.min || 0), 0), l5 = (s.spiele || []).slice(-5), st5 = l5.filter(e => e.art === "S").length;''', '''const z = [], M = x => (x.spiele || []).reduce((a, e) => a + (e.min || 0), 0), l5 = (s.spiele || []).filter(e => e.art !== "X").slice(-5), st5 = l5.filter(e => e.art === "S").length;''')
    s = rep(s, '''${st5} der letzten ${l5.length} Ligaspiele in der Startelf''', '''${st5} der letzten ${l5.length} Ligaspiele in der Startelf${(s.spiele || []).slice(-5).some(e => e.art === "X") ? ", in denen sie im Kader stand" : ""}''')
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
