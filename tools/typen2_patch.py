# Spielertyp im Kader und in der Einordnung (Finn 05.11.2026): "Wir rechnen mit Proost, einer Ballverteilerin", Alternative mit Typ,
# und wenn die Ausfallende einen anderen Typ hat: wer ihre Tore und Vorlagen auffangen muss
import sys
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    s = rep(s, """  function typZeile(s){""", """  const TYPFORM = {"defensive Sechserin": ["eine defensive Sechserin", "einer defensiven Sechserin"], "offensive Sechserin": ["eine offensive Sechserin", "einer offensiven Sechserin"],
    "Box-to-Box": ["eine Box-to-Box-Spielerin", "einer Box-to-Box-Spielerin"], "ausgewogene Außenverteidigerin": ["eine ausgewogene Außenverteidigerin", "einer ausgewogenen Außenverteidigerin"],
    "offensive Außenverteidigerin": ["eine offensive Außenverteidigerin", "einer offensiven Außenverteidigerin"], "defensive Außenverteidigerin": ["eine defensive Außenverteidigerin", "einer defensiven Außenverteidigerin"],
    "ausgewogene Innenverteidigerin": ["eine ausgewogene Innenverteidigerin", "einer ausgewogenen Innenverteidigerin"], "groß und zweikampfstark": ["groß und zweikampfstark", "einer großen, zweikampfstarken Innenverteidigerin"],
    "torgefährliche Mittelfeldspielerin": ["eine torgefährliche Mittelfeldspielerin", "einer torgefährlichen Mittelfeldspielerin"], "arbeitet nach hinten mit": ["eine defensiv starke Außenspielerin", "einer defensiv starken Außenspielerin"],
    "mitspielende Torhüterin": ["eine mitspielende Torhüterin", "einer mitspielenden Torhüterin"], "sicherer Rückhalt": ["ein sicherer Rückhalt", "einem sicheren Rückhalt"], "mitspielende Stürmerin": ["eine mitspielende Stürmerin", "einer mitspielenden Stürmerin"]};
  const typNom = t => (TYPFORM[t] || ["eine " + t])[0], typDat = t => (TYPFORM[t] || [null, "einer " + t])[1];
  const typVon = s => { const d = s && typDaten()[s.id]; return d && d.typ[0] ? d.typ[0] : null; };
  function typZeile(s){""")
    # Kader: Typ-Chip neben der Rolle
    s = rep(s, """class="kd-r" style="color:${r[1]}">${r[0]}</span></small>""", """class="kd-r" style="color:${r[1]}">${r[0]}</span></small>${typVon(s) ? `<small class="kd-ty">${esc(typVon(s)[0].toUpperCase() + typVon(s).slice(1))}</small>` : ""}""")
    s = rep(s, """.typ{display:grid;""", """.kd-ty{display:block;color:#C9D3E2;font-size:12px;margin-top:1px}
.typ{display:grid;""")
    # Einordnung: Typ der Ersatzspielerin, Alternative, Analyse bei anderem Typ
    s = rep(s, """        return i === 0 ? `Wir rechnen mit ${btn(x)}${r && r.s ? `, sie stand schon ${r.s === 1 ? "einmal" : r.s + "-mal"} für ${esc(nachN(s.n))} in der Startelf` : ""}${pr ? `. Unsere Prognose für sie: ${pr}` : ""}.`
          : `Auch ${btn(x)} ist möglich${pr ? `, Prognose ${pr}` : ""}.`; }).join(" "), 1]);""",
"""        const ty = typVon(x);
        return i === 0 ? `Wir rechnen mit ${btn(x)}${ty ? `, ${esc(typDat(ty))}` : ""}${r && r.s ? `. Sie stand schon ${r.s === 1 ? "einmal" : r.s + "-mal"} für ${esc(nachN(s.n))} in der Startelf` : ""}${pr ? `. Unsere Prognose für sie: ${pr}` : ""}.`
          : `Alternative wäre ${btn(x)}${ty ? `, ${esc(typNom(ty))}` : ""}${pr ? `, Prognose ${pr}` : ""}.`; }).join(" ") + typAnalyse(s, kon), 1]);""")
    s = rep(s, """  function einordnung(m){""", """  // Analyse (Finn 05.11.2026): spielt die Ersatzspielerin anders, wer fängt Tore und Vorlagen auf?
  function typAnalyse(s, kon){
    const tA = typVon(s), x = kon[0], tB = typVon(x); if (!tA || !x || !tB || tA === tB) return "";
    const d = typDaten()[s.id], off = d && ((d.p.tb ?? 0) >= 65 || (d.p.kp ?? 0) >= 65 || (d.p.sch ?? 0) >= 65);
    let t = ` ${esc(nachN(x.n))} spielt anders als ${esc(nachN(s.n))}: ${esc(nachN(s.n))} ist ${esc(typNom(tA))}, ${esc(nachN(x.n))} ${esc(typNom(tB))}.`;
    if (off) {
      const tb = y => (y.spiele || []).reduce((a, e) => a + (e.tore || []).length + (e.vorl || 0), 0);
      const L = (SPN.spielerinnen || []).filter(y => y.k === s.k && y.id !== s.id && y.id !== x.id && y.pos !== "TW" && !(y.status && ["raus", "gesperrt"].includes(y.status.s)) && ((y.spiele || []).slice(-1)[0] || {}).art === "S")
        .sort((a, b) => tb(b) - tb(a)).filter(y => tb(y) >= 2).slice(0, 2);
      const eig = tb(s);
      if (L.length) t += ` ${esc(nachN(s.n))}s ${eig} ${eig === 1 ? "Torbeteiligung muss" : "Torbeteiligungen müssen"} dann andere liefern, am ehesten ${L.map(y => `<button class="eo-n" data-profil="${esc(y.id)}">${esc(nachN(y.n))}</button> (${tb(y)})`).join(" und ")}.`;
    }
    return t;
  }
  function einordnung(m){""")
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
