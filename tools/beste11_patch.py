import sys
# Finn 05.11.2026 22:51: Knopf "Mehr" klappt auf Top 25 auf
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    s = rep(s, '''.sort((a, b) => b[1].wert - a[1].wert).slice(0, 10).map(([id, x]) => [spById(id), x]).filter(([s]) => s);
    return `<section class="stk" id="st-beste">''', '''.sort((a, b) => b[1].wert - a[1].wert).slice(0, BMEHR ? 25 : 10).map(([id, x]) => [spById(id), x]).filter(([s]) => s);
    return `<section class="stk" id="st-beste">''')
    s = rep(s, '''}).join("")}<p class="bst-erkl">''', '''}).join("")}<button class="bst-mehr" data-bmehr="1">${BMEHR ? "Weniger" : "Mehr"}</button><p class="bst-erkl">''')
    s = rep(s, '''  let BESTE = "ALLE";''', '''  let BESTE = "ALLE", BMEHR = false;
  document.addEventListener("click", e => { const b = e.target.closest && e.target.closest("[data-bmehr]"); if (!b) return; e.preventDefault(); e.stopPropagation();
    BMEHR = !BMEHR; const el = document.getElementById("st-beste"); if (!el) return; const y = window.scrollY; el.outerHTML = besteSektion(); window.scrollTo(0, y);
    if (!BMEHR) { const n = document.getElementById("st-beste"); if (n && n.getBoundingClientRect().top < 0) n.scrollIntoView({block: "start"}); } }, true);''')
    s = rep(s, '''    BESTE = b.dataset.beste;''', '''    BESTE = b.dataset.beste; BMEHR = false;''')
    s = rep(s, '''.bst-erkl{''', '''.bst-mehr{display:block;margin:8px auto 0;border:0;background:rgba(255,255,255,.07);color:#fff;font:inherit;font-size:12px;font-weight:600;border-radius:99px;padding:5px 14px;cursor:pointer}.bst-erkl{''')
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
