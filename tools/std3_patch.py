# Aufstellungs-Hinweis Standards (Finn 05.11.2026): bei Elfmeter ohne Ersatz aus den Daten nennen, wer in der Startelf seit 3 Saisons Ligaelfmeter geschossen hat;
# Link "Alle Standards" unter dem Text statt rechts daneben (kein schiefer Umbruch)
import sys
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    s = rep(s, """      const teile = Object.entries(nachE).map(([e, ls]) => `${ls.join(" und ")}: ${e ? `voraussichtlich <b>${esc(e)}</b>` : "Ersatz unklar"}`);
      return `<div class="sf-h">${svg(P.warn, "")}<span><b>${esc(f.n)}</b> nicht in der Startelf. ${teile.join(". ")}.</span><button class="lk" data-kader="${esc(k)}">Standards</button></div>`; });""",
"""      const e3 = ((AF && AF.elf3 && AF.elf3[k]) || []).filter(x => drin(x[0]) && !sfGl(x[0], f.n)), seit = (AF && AF.elf3_seit) || "";
      const teile = Object.entries(nachE).map(([e, ls]) => {
        if (e) return `${ls.join(" und ")}: voraussichtlich <b>${esc(e)}</b>`;
        const nurElf = ls.length === 1 && ls[0] === "Elfmeter", rest = ls.filter(l => l !== "Elfmeter");
        const elfT = e3.length ? `Elfmeter: zuletzt ${e3.slice(0, 2).map(x => `<b>${esc(nachN(x[0]))}</b> ${x[1]} von ${x[1] + x[2]} verwandelt`).join(", ")} seit ${seit}` : `Elfmeter: in der Startelf hat seit ${seit} keine einen Ligaelfmeter geschossen`;
        return ls.includes("Elfmeter") ? (nurElf ? elfT : `${rest.join(" und ")}: Ersatz unklar. ${elfT}`) : `${ls.join(" und ")}: Ersatz unklar`; });
      return `<div class="sf-h">${svg(P.warn, "")}<span><b>${esc(f.n)}</b> nicht in der Startelf. ${teile.join(". ")}.<button class="lk sf-hl" data-kader="${esc(k)}">Alle Standards ›</button></span></div>`; });""")
    s = rep(s, """.sf-h{display:grid;grid-template-columns:14px 1fr auto;""", """.sf-h .sf-hl{display:block;margin-top:4px;padding:0;background:none;border:0;font-weight:600}
.sf-h{display:grid;grid-template-columns:14px 1fr;""")
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
