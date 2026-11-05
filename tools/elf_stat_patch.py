# Elfmeter in der Liga: von Inside in die Statistik (Finn 05.11.2026), Fuß als "Schussfuß" kennzeichnen
import sys
def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    a = s.index('      ${el.length ? `<h3 class="disp" style="font-size:21px;margin-top:8px">Elfmeter in der Liga</h3>')
    e = s.index('\n', s.index('${false && el.length', a)) + 1
    s = s[:a] + s[e:]
    s = rep(s, 'Ecken, Schüsse pro Spiel und Elfmeter: API-Football', 'Ecken und Schüsse pro Spiel: API-Football')
    s = rep(s, ' Fuß aus unseren Stammdaten.</p>', ' Elfmeter jetzt unter Statistik.</p>')
    s = rep(s, """        <div class="st-chips">${STKAT.map(([k, t]) => `<button data-stsprung="${k}">${t}</button>`).join("")}</div>`;""",
"""        <div class="st-chips">${STKAT.map(([k, t]) => `<button data-stsprung="${k}">${t}</button>`).join("")}${(AF && AF.elf || []).length ? `<button data-stsprung="elf">Elfmeter</button>` : ""}</div>`;""")
    s = rep(s, """      h += `<p class="st-notiz">Tore, Vorlagen, Karten und Minuten aus""", """      const EL = (AF && AF.elf) || [];
      if (EL.length) h += `<section class="stk" id="st-elf"><div class="stk-k"><h2>Elfmeter</h2><small>alle Schützinnen der Liga, Fuß = Schussfuß</small></div><div class="elf-l" style="--pkw:${Math.max(...EL.map(x => x.t + x.v)) * 16 + 8}px">${EL.map(x => `<button class="elf-r" data-profil="${esc(x.id)}">${logo(x.k, 22)}<span><b>${esc(x.n)}</b><small>${esc(kname(x.k))}${x.fuss ? " · Schussfuß " + esc(x.fuss) : ""}</small></span><span class="pk">${"<i class=t></i>".repeat(x.t)}${"<i class=v></i>".repeat(x.v)}</span><span class="q">${x.t}/${x.t + x.v}</span></button>`).join("")}</div><p class="st-notiz" style="margin:10px 0 0">Grün: verwandelt, roter Ring: verschossen oder gehalten. Quelle API-Football, Schussfuß aus unseren Stammdaten.</p></section>`;
      h += `<p class="st-notiz">Tore, Vorlagen, Karten und Minuten aus""")
    s = rep(s, ".elf-r{display:grid;grid-template-columns:22px minmax(0,1fr) auto 34px;", ".elf-r{display:grid;grid-template-columns:22px minmax(0,1fr) var(--pkw,auto) 34px;")
    s = rep(s, ".elf-r .pk{display:flex;gap:4px}", ".elf-r .pk{display:flex;gap:4px;justify-content:flex-end}")
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
