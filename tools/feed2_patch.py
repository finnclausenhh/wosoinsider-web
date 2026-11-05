# Reiter nicht markiert in Statistik/Tabelle; "Zuletzt angesehen" als Feed-Modul weiter unten (Finn 05.11.2026)
import sys
def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    s = rep(s, """    document.querySelectorAll("[data-statview]").forEach(b => b.setAttribute("aria-pressed", b.dataset.statview === art));""",
"""    document.querySelectorAll("[data-statview]").forEach(b => b.setAttribute("aria-pressed", b.dataset.statview === art));
    document.querySelectorAll(".seg[role=tablist] button").forEach(b => b.setAttribute("aria-selected", false));""")
    s = rep(s, "const warte = [], SONDER = [[gefragtZeile, 14]];", "const warte = [], SONDER = [[zuletztZeile, 10], [gefragtZeile, 16]];")
    s = rep(s, """  function gefragtZeile(){""", """  function zuletztZeile(){
    if (!SPN) return "";
    const l = zuletzt().map(id => spById(id)).filter(Boolean).slice(0, 4); if (l.length < 2) return "";
    return `<section class="gfw"><div class="kap">${svg('<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>')}ZULETZT ANGESEHEN</div><div class="gfw-g">${l.map(s =>
      `<button class="gfw-c" data-profil="${esc(s.id)}">${pfFoto(s, 34, 34, 17)}<span><b>${esc(nachN(s.n))}</b><small>${esc(kname(s.k))}</small></span></button>`).join("")}</div></section>`;
  }
  function gefragtZeile(){""")
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
