"""Profil Runde 12 (Finn 05.11.2026): Spielstile unter Weitere Werte (höchstens 2, ohne Erklärung),
strengere Vergabe (nicht jede braucht einen Titel), achte Kachel (Torbeteiligungen, bei Torhüterinnen Spiele zu null),
Größe im Vergleich zur eigenen Einzelposition (Außen- gegen Innenverteidigerin, Sechserin gegen Zehnerin), wenn mindestens 8 Werte da sind."""
import sys
def rep(s, old, new):
    n = s.count(old); assert n == 1, (old[:90], n); return s.replace(old, new)

def patch(s):
    # Spielstile: nach Weitere Werte, vor dem Steckbrief
    s = rep(s, '    h += stilBox(s);\n', '')
    s = rep(s, '      if (af.fuss || af.alter || af.gr) h += `<section class="pf-box">${kap("Steckbrief")}', '      h += stilBox(s);\n      if (af.fuss || af.alter || af.gr) h += `<section class="pf-box">${kap("Steckbrief")}')
    # höchstens 2, keine Erklärung im Profil (steht unter Regeln)
    s = rep(s, '''    const l = stileAlle()[s.id] || []; if (!l.length) return "";''', '''    const l = (stileAlle()[s.id] || []).slice(0, 2); if (!l.length) return "";''')
    s = rep(s, '''</div><p class="af-st">Titel aus den echten Liga-Werten. Mit Plus nur die Beste der Liga. Vergeben je nach Vergleichsfeld: an die besten 10 (ab 100 Spielerinnen), die besten 10 % (ab 30), die besten 3 (ab 10), sonst nur Platz 1. Gezählt wird ab 270 Minuten.</p></section>`;''',
               '''</div></section>`;''')
    # strengere Vergabe: ab 100 die besten 5, ab 30 die besten 3, ab 10 die besten 2, sonst nur Platz 1
    s = rep(s, "const stCut = n => n >= 100 ? 10 : n >= 30 ? Math.max(3, Math.round(n * .1)) : n >= 10 ? 3 : 1;",
               "const stCut = n => n >= 100 ? 5 : n >= 30 ? 3 : n >= 10 ? 2 : 1;")
    # Reihenfolge: Plus zuerst, dann der bessere Platz
    s = rep(s, "Object.values(out).forEach(l => l.sort((a, b) => b.plus - a.plus));",
               "Object.values(out).forEach(l => l.sort((a, b) => b.plus - a.plus || (a.platz || 99) - (b.platz || 99)));")
    s = rep(s, "add(x.id, {t: name, plus: platz === 1 && eq === 1, info:", "add(x.id, {t: name, platz, plus: platz === 1 && eq === 1, info:")
    # achte Kachel
    s = rep(s, '      const gelb = sp.filter(e => e.gelb && !e.gr).length; if (gelb || st.fouls != null) {',
               '''      { const TB = x => (x.spiele || []).reduce((a, e) => a + (e.tore || []).length + (e.vorl || 0), 0), tv = TB(s), mi = M(s);
        const GG = e => { const [a, b] = String(e.erg || "").split(":").map(Number); return isNaN(a) ? null : (e.ha === "H" ? b : a); }, ZN = x => (x.spiele || []).filter(e => e.art === "S" && GG(e) === 0).length;
        if (s.pos !== "TW" && mi) ww.push([tv, tv === 1 ? "Torbeteiligung" : "Torbeteiligungen", (() => { const t = sp.reduce((a, e) => a + (e.tore || []).length, 0), v = sp.reduce((a, e) => a + (e.vorl || 0), 0); return `${t} ${t === 1 ? "Tor" : "Tore"} · ${v} ${v === 1 ? "Vorlage" : "Vorlagen"} · ${dez(tv / mi * 90, 2)} pro 90 Min.`; })(), ligaRang(s, x => M(x) >= 270 ? TB(x) / M(x) * 90 : null), "Torbeteiligungen", v => dez(v, 2), "pro 90 Min.", `${tv} · ${dez(tv / mi * 90, 2)} pro 90`]);
        if (s.pos === "TW" && sp.some(e => e.art === "S")) { const st11 = sp.filter(e => e.art === "S"), gt = st11.reduce((a, e) => a + (GG(e) || 0), 0);
          ww.push([ZN(s), "Spiele zu null", `${gt} Gegentore in ${st11.length} Spielen`, ligaRang(s, x => M(x) >= 270 ? ZN(x) : null), "Zu null", v => String(v), "Spiele", `${ZN(s)} von ${st11.length}`]); } }
      const gelb = sp.filter(e => e.gelb && !e.gr).length; if (gelb || st.fouls != null) {''')
    # gerade Zahl an Kacheln: sonst Spielminuten dazu
    s = rep(s, '      const pfarbe0 = p =>', '''      if (ww.length % 2 === 1 && M(s)) { const mi = M(s), ns = sp.filter(e => e.art === "S").length; ww.push([`${mi.toLocaleString("de-DE")}'`, "Spielminuten", `${ns} von ${sp.length} Spielen in der Startelf`, ligaRang(s, x => M(x) >= 270 ? M(x) : null)]); }
      const pfarbe0 = p =>''')
    # Größe: Vergleich mit der eigenen Einzelposition
    s = rep(s, '      const grP = ((SPN && SPN.spielerinnen) || []).filter(x => x.pos === s.pos).map(x => (afSp(x.id) || {}).gr).filter(Boolean);',
               '''      const EPOS = x => { const t = String(((x.slots || [])[0] || [])[2] || "").replace(/ (links|rechts)$/, "");
        return /^(Rechts|Links)verteidigerin|Schienenspielerin/.test(t) ? "Außenverteidigerinnen" : /^Innenverteidigerin/.test(t) ? "Innenverteidigerinnen" : /^Sechserin/.test(t) ? "Sechserinnen"
          : /^(Zehnerin|Offensives Mittelfeld)/.test(t) ? "Zehnerinnen" : /^(Zentrales Mittelfeld|Mittelfeld)$/.test(t) ? "zentrale Mittelfeldspielerinnen" : /^Flügel/.test(t) ? "Flügelspielerinnen" : /^(Sturm|Mittelstürmerin)/.test(t) ? "Stürmerinnen" : null; };
      const eg = EPOS(s), grE = eg ? ((SPN && SPN.spielerinnen) || []).filter(x => EPOS(x) === eg).map(x => (afSp(x.id) || {}).gr).filter(Boolean) : [];
      const grP = grE.length >= 8 ? grE : ((SPN && SPN.spielerinnen) || []).filter(x => x.pos === s.pos).map(x => (afSp(x.id) || {}).gr).filter(Boolean);''')
    s = rep(s, '''refT = grPm ? ({TW: "Ø Torhüterinnen", ABW: "Ø Abwehr", MF: "Ø Mittelfeld", ST: "Ø Sturm"}[s.pos] || "Ø Position") : "Liga-Ø";''',
               '''refT = grPm ? (grE.length >= 8 ? "Ø " + eg : ({TW: "Ø Torhüterinnen", ABW: "Ø Abwehr", MF: "Ø Mittelfeld", ST: "Ø Sturm"}[s.pos] || "Ø Position")) : "Liga-Ø";''')
    return s

if __name__ == "__main__":
    for f in sys.argv[1:]:
        s = open(f, encoding="utf-8").read()
        if "const EPOS = x =>" in s: print("schon drin", f); continue
        t = patch(s); open(f, "w", encoding="utf-8").write(t); print("profil2 ok", f)
