# Spielstil-Chips im Kader antippbar (Finn 05.11.2026): Rahmen wie bei Aufstellungschips, darunter die Erklärung
import sys
def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    s = rep(s, """  const stChip = (x, klein) => `<span class="stl${x.plus ? " plus" : ""}${klein ? " k" : ""}">""",
"""  const stChip = (x, klein) => `<span class="stl${x.plus ? " plus" : ""}${klein ? " k" : ""}"${klein ? ` role="button" tabindex="0" data-stl="${esc(x.t + (x.plus ? "+" : "") + ": " + x.info + (x.was && !/Elfmetern|schießt/.test(x.info) ? ", " + x.was : ""))}"` : ""}>""")
    s = rep(s, """  const stilKader = s => {""", """  document.addEventListener("click", e => {
    const c = e.target.closest && e.target.closest("[data-stl]"); if (!c) return;
    e.preventDefault(); e.stopPropagation();
    const z = c.closest(".stl-z"), an = c.classList.contains("sel");
    document.querySelectorAll(".stl.sel").forEach(x => x.classList.remove("sel")); document.querySelectorAll(".stl-i").forEach(x => x.remove());
    if (an) return;
    c.classList.add("sel"); (c.closest(".pf-tr") || z).insertAdjacentHTML("afterend", `<span class="stl-i">${esc(c.dataset.stl)}</span>`);
  }, true);
  const stilKader = s => {""")
    s = rep(s, """.stl-z{display:flex;flex-wrap:wrap;gap:4px;margin-top:3px}""", """.stl-z{display:flex;flex-wrap:wrap;gap:4px;margin-top:3px}
.stl[data-stl]{cursor:pointer}.stl.sel{box-shadow:0 0 0 2px #0E1726,0 0 0 3.5px #8FB0FF}
.stl-i{display:block;margin:-2px 0 6px 56px;font-size:11.5px;line-height:1.35;color:#C9D3E2;background:rgba(143,176,255,.1);border-radius:8px;padding:6px 8px;white-space:normal}""")
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
