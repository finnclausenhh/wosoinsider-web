# Reihenfolge (Finn 05.11.2026): Vereinsseite zuerst Kader und Legende, Standards unten; Inside "Wer schießt die Standards" ganz ans Ende
import sys
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    a = s.index('</h1></div>${stdFeld(k)}${kap("Kader")}<div class="kd-leg">')
    b = s.index('</div>\n      ${["TW", "ABW", "MF", "ST"].map(p =>', a)
    leg = s[a + len('</h1></div>${stdFeld(k)}${kap("Kader")}'):b + len('</div>')]
    s = s[:a] + '</h1></div>${kap("Kader")}' + s[b + len('</div>'):]
    s = rep(s, """return l.length ? kap({TW:"Tor", ABW:"Abwehr", MF:"Mittelfeld", ST:"Sturm"}[p]) + `<div class="pf-liste">${l.map(zeile).join("")}</div>` : ""; }).join("")}<div id="kd-trainer"></div>${kaderExtras(k, L)}</div>`;""",
            """return l.length ? kap({TW:"Tor", ABW:"Abwehr", MF:"Mittelfeld", ST:"Sturm"}[p]) + `<div class="pf-liste">${l.map(zeile).join("")}</div>` : ""; }).join("")}""" + leg + """<div id="kd-trainer"></div>${kaderExtras(k, L)}${stdFeld(k)}</div>`;""")
    s = rep(s, """      <div style="display:grid;gap:4px;padding-top:8px"><h3 class="disp" style="font-size:21px">Wer schießt die Standards?</h3>
        <p class="af-st" style="font-size:12px">Je Verein als Spielfeld auf der Vereinsseite: Ecke links und rechts, Freistoß, Elfmeter mit Quote.</p></div>
      <div class="sf-vl">${(IN.standards || []).map(s => `<button class="sf-v" data-kader="${esc(s.k)}">${logo(s.k, 26)}<span>${esc(kname(s.k))}</span></button>`).join("")}</div>${afStandards()}</section>`;""",
            """      ${afStandards()}</section>`;""")
    s = rep(s, """${IN.kalender ? kalenderSektion(IN.kalender) : ""}""", """${IN.kalender ? kalenderSektion(IN.kalender) : ""}${schuetzenSektion()}""")
    s = rep(s, """  function afStandards(){""", """  function schuetzenSektion(){
    if (!(IN.standards || []).length) return "";
    return `<section class="sek"><div style="display:grid;gap:4px;padding-top:8px"><h3 class="disp" style="font-size:21px">Wer schießt die Standards?</h3>
        <p class="af-st" style="font-size:12px">Je Verein als Spielfeld auf der Vereinsseite: Ecke links und rechts, Freistoß, Elfmeter mit Quote.</p></div>
      <div class="sf-vl">${(IN.standards || []).map(s => `<button class="sf-v" data-kader="${esc(s.k)}">${logo(s.k, 26)}<span>${esc(kname(s.k))}</span></button>`).join("")}</div></section>`;
  }
  function afStandards(){""")
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
