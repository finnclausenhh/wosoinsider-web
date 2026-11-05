# Klickbare Logos und Fotos, Kader-Leiste im Profil zum Durchblättern (Finn 05.11.2026)
import sys
def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    s = rep(s, '''<img class="lg" src="logos/${esc(k)}.png" alt=""''', '''<img class="lg" data-lk="${esc(k)}" src="logos/${esc(k)}.png" alt=""''')
    s = rep(s, '''      : `<div class="fkomp"><div class="pic${''', '''      : `<div class="fkomp"><div data-profilname="${esc(f.k + "|" + f.n)}" style="cursor:pointer;display:contents"><div class="pic${''')
    s = rep(s, ''' : logo(f.k, 70)}</div>
          <div class="tx">''', ''' : logo(f.k, 70)}</div></div>
          <div class="tx">''')
    s = rep(s, '''return `<span class="mf"${src ? "" : ` style="background:${KFARBE[k] || "var(--soft)"}"`}>''', '''return `<span class="mf" data-profilname="${esc(k + "|" + (s.voll || s.n))}" style="cursor:pointer;${src ? "" : `background:${KFARBE[k] || "var(--soft)"}`}">''')
    # Kader-Leiste am Profilende
    s = rep(s, '''    $("#main").innerHTML = `<div class="det pf">${pfZurueck()}<button class="pf-teilen" data-teilen="${esc(s.id)}" aria-label="Profil teilen">${svg('<path d="M12 15V4M8 8l4-4 4 4"/><path d="M6 12v7h12v-7"/>')}</button>${h}</div>`;''',
'''    h += pfWeiter(s);
    $("#main").innerHTML = `<div class="det pf">${pfZurueck()}<button class="pf-teilen" data-teilen="${esc(s.id)}" aria-label="Profil teilen">${svg('<path d="M12 15V4M8 8l4-4 4 4"/><path d="M6 12v7h12v-7"/>')}</button>${h}</div>`;
    const ak = document.querySelector(".pfw-r .an"); if (ak) ak.parentElement.scrollLeft = ak.offsetLeft - ak.parentElement.clientWidth / 2 + ak.offsetWidth / 2;''')
    s = rep(s, '''  function profilSeite(s){''', '''  // Mehr aus dem Kader: Leiste mit allen Spielerinnen des Vereins, vor und zurück (Finn 05.11.2026)
  function pfWeiter(s){
    const R = {TW: 0, ABW: 1, MF: 2, ST: 3};
    const l = ((SPN && SPN.spielerinnen) || []).filter(x => x.k === s.k && !x.trainer).sort((a, b) => ((R[a.pos] ?? 9) - (R[b.pos] ?? 9)) || (Number(a.nr) || 99) - (Number(b.nr) || 99));
    if (l.length < 3) return "";
    const i = l.findIndex(x => x.id === s.id), vor = l[(i - 1 + l.length) % l.length], nach = l[(i + 1) % l.length];
    const kn = (x, r) => `<button class="pfw-n${r ? " r" : ""}" data-profil="${esc(x.id)}">${r ? "" : "‹ "}<span>${esc(nachN(x.n))}</span>${r ? " ›" : ""}</button>`;
    return `<section class="pf-box pfw">${kap("Mehr aus dem Kader")}<div class="pfw-r">${l.map(x => `<button class="pfw-c${x.id === s.id ? " an" : ""}" data-profil="${esc(x.id)}">${pfFoto(x, 54, 66, 10)}<small>${esc(nachN(x.n))}</small></button>`).join("")}</div>
      <div class="pfw-nv">${kn(vor)}<button class="pfw-k" data-kader="${esc(s.k)}">${logo(s.k, 18)} Ganzer Kader</button>${kn(nach, 1)}</div></section>`;
  }
  // Bare Logos öffnen die Vereinsseite (Finn 05.11.2026)
  document.addEventListener("click", e => {
    const lg = e.target.closest && e.target.closest("#main img.lg[data-lk]"); if (!lg) return;
    if (lg.parentElement.closest("button,a,summary,label,[data-profil],[data-profilname],[data-kader],[data-game],[data-id],[data-statverein],[data-statview],[data-tab],.pf-vk")) return;
    const b = document.createElement("button"); b.dataset.kader = lg.dataset.lk; b.hidden = true; document.body.appendChild(b); b.click(); b.remove();
  });
  function profilSeite(s){''')
    s = rep(s, '''.pf-kopf{display:grid;grid-template-columns:132px minmax(0,1fr);gap:16px;align-items:end}''', '''.pf-kopf{display:grid;grid-template-columns:132px minmax(0,1fr);gap:16px;align-items:end}
#main img.lg[data-lk]{cursor:pointer}
.pfw-r{display:flex;gap:8px;overflow-x:auto;scroll-snap-type:x proximity;padding:2px 2px 6px;margin:0 -2px;scrollbar-width:none}.pfw-r::-webkit-scrollbar{display:none}
.pfw-c{flex:none;display:grid;gap:5px;justify-items:center;width:62px;background:none;border:0;color:inherit;padding:0;scroll-snap-align:center;opacity:.72;font:inherit}
.pfw-c small{font-size:11px;max-width:62px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:var(--mu,#A9B4C6)}
.pfw-c.an{opacity:1}.pfw-c.an small{color:#fff;font-weight:700}.pfw-c.an .bild,.pfw-c.an img{outline:2px solid #2F5BFF;outline-offset:1px}
.pfw-nv{display:grid;grid-template-columns:1fr auto 1fr;gap:8px;align-items:center;margin-top:8px}
.pfw-n,.pfw-k{background:rgba(255,255,255,.06);border:0;border-radius:10px;color:#fff;font:inherit;font-size:13px;font-weight:600;padding:9px 10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.pfw-n{text-align:left}.pfw-n.r{text-align:right}.pfw-k{display:flex;gap:6px;align-items:center;color:#8FB0FF}''')
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
