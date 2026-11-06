"""Feedback Finn 07.11.2026 (Teil "direkt umsetzen"), Patch für ticker/index.html bzw. Artifact index.html.

Aufruf: python3 tools/fb0711_patch.py <eingabe.html> <ausgabe.html>
1  Spielstile: ein Satz ohne Umbruch-Wirrwarr ("Tore: Bestwert aller 173 Feldspielerinnen")
2  Ihre Position: Plätze aus anderen Systemen nur auf passende Linie abbilden, nicht doppelt nennen
   (Memeti stand als "Linksverteidigerin 3x" und "Flügel links 3x")
3  Netz: lange Werte (z. B. "166 angekommen · 21/90") zweizeilig, nichts ragt aus dem Bild
4  Größenvergleich: Legende darf umbrechen (überlappte die Grafik)
5  Profil: News ganz unten, nur noch "Mehr aus dem Kader" danach
6  Lange Erklärtexte, Foto- und Datennachweise hinter "i Hinweise und Quellen"
7  Tabelle: Meister, Pokalsieger, Aufsteiger als Kürzel mit Legende
8  Inside "Wer schießt die Standards?" und "Alle Standards ›" springen direkt zu den Standards des Vereins
9  Für Kickbase: Note wie unten (Saisonschnitt -> Schnitt letzte 3)
"""
import sys

R = []
def r(alt, neu, n=1):
    R.append((alt, neu, n))

# 1 Spielstile
r('''<small>${esc(x.info)}${x.was && !/Elfmetern|schießt/.test(x.info) ? "<br>" + esc(x.was) : ""}</small>''',
  '''<small>${x.was && !/Elfmetern|schießt/.test(x.info) ? `<b class="stl-w">${esc(x.was.charAt(0).toUpperCase() + x.was.slice(1))}</b>: ` : ""}${esc(x.info)}</small>''')
r('''data-stl="${esc(x.t + (x.plus ? "+" : "") + ": " + x.info + (x.was && !/Elfmetern|schießt/.test(x.info) ? ", " + x.was : ""))}"''',
  '''data-stl="${esc(x.t + (x.plus ? "+" : "") + ": " + (x.was && !/Elfmetern|schießt/.test(x.info) ? x.was + ", " : "") + x.info)}"''')

# 2 Ihre Position
r('''      s.slots.forEach(t => { const u = naechster(t); meine[key(u)] = (meine[key(u)] || 0) + t[3]; });''',
  '''      // Finn 07.11.: fremde Plätze nur auf dieselbe Linie abbilden (Flügel = Mittelfeld oder Sturm), sonst nur als Text
      const linie = t => /Flügel/.test(t[2]) ? "FL" : /Schiene/.test(t[2]) ? "SCH" : t[0] === "ABW" || t[0] === "TW" ? t[0] : t[0] === "ST" ? "ST" : "MF";
      const passt = (u, t) => { const a = linie(u), b = linie(t); return a === b || (b === "FL" && (a === "MF" || a === "ST")) || (a === "FL" && (b === "MF" || b === "ST")) || (b === "SCH" && (a === "ABW" || a === "MF")) || (a === "SCH" && (b === "ABW" || b === "MF")); };
      const naechst2 = t => sys.slots.find(u => key(u) === key(t)) || sys.slots.filter(u => passt(u, t) && Math.abs(u[1] - t[1]) <= .3).sort((a, b) => Math.abs(a[1] - t[1]) - Math.abs(b[1] - t[1]))[0];
      s.slots.forEach(t => { const u = naechst2(t); if (u) meine[key(u)] = (meine[key(u)] || 0) + t[3]; });
      if (!Object.keys(meine).length) s.slots.forEach(t => { const u = naechster(t); meine[key(u)] = (meine[key(u)] || 0) + t[3]; });
      const eigen = {}; s.slots.forEach(t => { if (sys.slots.some(u => key(u) === key(t))) eigen[key(t)] = (eigen[key(t)] || 0) + t[3]; });''')
r('''const weitere = sys.slots.filter(u => u !== hauptSlot && meine[key(u)]).sort((x, y) => meine[key(y)] - meine[key(x)]);''',
  '''const weitere = sys.slots.filter(u => u !== hauptSlot && eigen[key(u)]).sort((x, y) => eigen[key(y)] - eigen[key(x)]);''')
r('''auch als ${weitere.map(u => esc(u[2]) + " " + meine[key(u)] + "x").join(", ")}''',
  '''auch als ${weitere.map(u => esc(u[2]) + " " + eigen[key(u)] + "x").join(", ")}''')

# 3 Netz zweizeilig
r('''return `<text x="${x.toFixed(0)}" y="${yy.toFixed(0)}" text-anchor="${an}" class="nl">${esc(w[4])}</text><text x="${x.toFixed(0)}" y="${(yy + 12).toFixed(0)}" text-anchor="${an}" class="nw">${esc(w[7])}</text><text x="${x.toFixed(0)}" y="${(yy + 24).toFixed(0)}" text-anchor="${an}" class="nv" fill="${rFarbe(w[3])}">''',
  '''const tl = String(w[7]).length > 15 && String(w[7]).includes(" · ") && an !== "middle" ? String(w[7]).split(" · ") : [String(w[7])], z2 = (tl.length - 1) * 12;
            return `<text x="${x.toFixed(0)}" y="${yy.toFixed(0)}" text-anchor="${an}" class="nl">${esc(w[4])}</text>${tl.map((t, j) => `<text x="${x.toFixed(0)}" y="${(yy + 12 + j * 12).toFixed(0)}" text-anchor="${an}" class="nw">${esc(t)}</text>`).join("")}<text x="${x.toFixed(0)}" y="${(yy + 24 + z2).toFixed(0)}" text-anchor="${an}" class="nv" fill="${rFarbe(w[3])}">''')

# 4 + 6 + 7 CSS
r('''.sb-gr .lg{font-size:11px;color:var(--muted);white-space:nowrap}''',
  '''.sb-gr .lg{font-size:11px;color:var(--muted);white-space:normal;line-height:1.3}
.ik{display:grid;justify-items:start;gap:6px;margin-top:6px}.ik-b{display:inline-flex;align-items:center;gap:6px;background:none;border:0;padding:4px 0;color:var(--muted);font:600 11px var(--f-mono,inherit);letter-spacing:.04em;cursor:pointer}.ik-b svg{width:14px;height:14px}.ik > :not(.ik-b){display:none!important}.ik.auf > :not(.ik-b){display:block!important}
.stl-w{color:var(--ink,#E8EEFF);font-weight:600}
.tb-ti{display:inline-flex;gap:3px;margin-left:6px;vertical-align:2px}.tb-ti i{font:700 9px var(--f-mono,monospace);font-style:normal;line-height:1;padding:3px 4px;border-radius:4px}.tb-ti .m{background:#F5C518;color:#1A1606}.tb-ti .p{background:#C9D3E6;color:#0B1220}.tb-ti .a{background:rgba(74,222,128,.18);color:#4ADE80}
.tb-leg2{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:12px;color:var(--muted);margin-top:8px}.tb-leg2 .tb-ti{margin:0 4px 0 0}''')

# 5 News nach unten
r('''    if (nw.length) h += `<section class="pf-box">${kap("News zu " + nach)}''',
  '''    const newsH = !nw.length ? "" : `<section class="pf-box">${kap("News zu " + nach)}''')
r('''    h += pfWeiter(s);
    h += `<div class="pf-fuss">''',
  '''    h += newsH;  // Finn 07.11.: News ganz unten, danach nur der Kader
    h += pfWeiter(s);
    h += `<div class="pf-fuss">''')

# 7 Tabelle
r('''<span class="tb-vn">${esc(kname(r.k))}</span><span class="tb-mu">${r.sp}</span>''',
  '''<span class="tb-vn">${esc(kname(r.k))}${TITEL[r.k] ? `<span class="tb-ti">${TITEL[r.k].map(t => `<i class="${t}">${{m: "M", p: "P", a: "NEU"}[t]}</i>`).join("")}</span>` : ""}</span><span class="tb-mu">${r.sp}</span>''')
r('''<span><i style="background:rgba(226,74,74,.45)"></i>Abstieg</span></div>''',
  '''<span><i style="background:rgba(226,74,74,.45)"></i>Abstieg</span></div><div class="tb-leg2"><span><span class="tb-ti"><i class="m">M</i></span>Meister 2025/26</span><span><span class="tb-ti"><i class="p">P</i></span>Pokalsieger 2025/26</span><span><span class="tb-ti"><i class="a">NEU</i></span>Aufsteiger</span></div>''')
r('''  function statView(art, sanft){''',
  '''  // Finn 07.11.: Titel und Aufsteiger in der Tabelle (Meister und Pokal 2025/26 FC Bayern, Aufsteiger Stuttgart und Mainz)
  const TITEL = {FCB: ["m", "p"], VFB: ["a"], M05: ["a"]};
  function statView(art, sanft){''')

# 8 Standards direkt
r('''<button class="sf-v" data-kader="${esc(s.k)}">''', '''<button class="sf-v" data-kader="${esc(s.k)}" data-ziel="std">''')
r('''<button class="lk sf-hl" data-kader="${esc(k)}">Alle Standards ›</button>''', '''<button class="lk sf-hl" data-kader="${esc(k)}" data-ziel="std">Alle Standards ›</button>''')
r('''ladeSPN().then(() => { vereinsKader(x.dataset.kader, "zurueck"); window.scrollTo(0, 0); }).catch(() => {}); return; }''',
  '''const zielStd = x.dataset.ziel === "std"; ladeSPN().then(() => { vereinsKader(x.dataset.kader, "zurueck"); window.scrollTo(0, 0);
      if (zielStd) setTimeout(() => { const sf = document.querySelector("#main .sf"), kp = sf && sf.previousElementSibling; const el = kp && kp.classList.contains("kap") ? kp : sf; if (el) window.scrollTo(0, el.getBoundingClientRect().top + window.scrollY - 70); }, 60); }).catch(() => {}); return; }''')

# 9 Für Kickbase: Note wie unten
r('''<span>Note <span class="mu">${dez(vor)}</span> → <b style="color:${g[1]}">${dez(l3)}</b> in den letzten 3</span>''',
  '''<span>Note Ø Saison <span class="mu">${dez(a.avg != null ? a.avg : n.reduce((x, y) => x + y, 0) / n.length)}</span> → <b style="color:${g[1]}">${dez(l3)}</b> in den letzten 3</span>''')

# 6 Hinweise und Quellen einklappen (Profil, Spiel, Tabelle, Inside); läuft nach jedem Neuaufbau von #main
JS6 = '''
  // Finn 07.11.2026: lange Erklärtexte sowie Foto- und Datennachweise hinter "i Hinweise und Quellen"
  (function(){
    const SEL = ".af-st, .pf-fuss, .st-notiz";
    const klapp = () => { const m = document.getElementById("main"); if (!m) return;
      m.querySelectorAll(SEL).forEach(el => { if (el.dataset.ik || el.closest(".ik")) return;
        if (getComputedStyle(el).display === "flex") return;
        const t = el.textContent.trim(); if (!el.classList.contains("pf-fuss") && t.length < 90) return;
        el.dataset.ik = "1"; const w = document.createElement("div"); w.className = "ik";
        w.innerHTML = '<button type="button" class="ik-b" aria-expanded="false"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.5"/></svg>' + (el.classList.contains("pf-fuss") ? "Foto und Daten" : "Hinweise und Quellen") + '</button>';
        el.parentNode.insertBefore(w, el); w.appendChild(el); }); };
    document.addEventListener("click", e => { const b = e.target.closest(".ik-b"); if (!b) return; const w = b.parentElement; w.classList.toggle("auf"); b.setAttribute("aria-expanded", w.classList.contains("auf")); }, true);
    const go = () => { const m = document.getElementById("main"); if (!m) return setTimeout(go, 200); klapp(); new MutationObserver(klapp).observe(m, {childList: true, subtree: true}); };
    go();
  })();
'''

def main(a, b):
    s = open(a, encoding="utf-8").read()
    fehl = []
    for alt, neu, n in R:
        c = s.count(alt)
        if c != n: fehl.append((c, alt[:90])); continue
        s = s.replace(alt, neu)
    if fehl:
        for f in fehl: print("NICHT GEFUNDEN/MEHRFACH", f)
        sys.exit(1)
    i = s.index("</script>", s.index("loadSP().then(() => loadLive());"))
    s = s[:i] + JS6 + s[i:]
    open(b, "w", encoding="utf-8").write(s)
    print("ok", len(R), "Ersetzungen")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
