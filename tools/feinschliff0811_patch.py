"""Feinschliff 08.11.2026 (Finn): (1) Spielplan: VORSCHAU klein wie "Ende" in der Mitte statt eigener Zeile,
(2) Statistik und andere Seiten: nur ein "Hinweise und Quellen" je Seite, ganz unten,
(3) Inside: "Spieltag x in 60 Sekunden" verschwindet, sobald mehr als die Hälfte der Spiele dieses Spieltags beendet ist.
Aufruf: python3 tools/feinschliff0811_patch.py <index.html ein> <index.html aus>"""
import sys

def patch(s):
    def r(a, b):
        nonlocal s
        assert s.count(a) == 1, a[:80]
        s = s.replace(a, b)
    # (1)
    r("""  function mitte(p){
    const e = erg(p), live = istLive(p);""", """  function mitte(p, vs){
    const e = erg(p), live = istLive(p);""")
    r("""    return `<span class="mid"><span class="k">${uhr(dt(p.anstoss))}</span><small>Uhr</small></span>`;""",
      """    return `<span class="mid"><span class="k">${uhr(dt(p.anstoss))}</span>${vs ? '<small class="vs">Vorschau</small>' : "<small>Uhr</small>"}</span>`;""")
    r("""    const bs = belSeiten(p), mk = meinK(p), klein = SEL.size && !mk;""",
      """    const bs = belSeiten(p), mk = meinK(p), klein = SEL.size && !mk, ah = p.status !== "beendet" && !istLive(p) ? afHin(p) : "", vsNur = ah.includes('class="v"');""")
    r("""${mitte(p)}<span class="pr-t"><span class="kd-l" data-kader""", """${mitte(p, vsNur)}<span class="pr-t"><span class="kd-l" data-kader""")
    r("""      ${p.status !== "beendet" && !istLive(p) ? afHin(p) : ""}""", """      ${vsNur ? "" : ah}""")
    r(""".mid small{font-size:10px;font-weight:600;color:var(--muted);line-height:1.1}""",
      """.mid small{font-size:10px;font-weight:600;color:var(--muted);line-height:1.1}.mid small.vs{color:#C9AEF7}""")
    # (2)
    r("""        el.dataset.ik = "1"; const w = document.createElement("div"); w.className = "ik";""",
      """        el.dataset.ik = "1";
        if (!el.classList.contains("pf-fuss")) { const da = m.querySelector(".ik.ik-s"); if (da) { da.appendChild(el); m.appendChild(da); return; } }
        const w = document.createElement("div"); w.className = "ik" + (el.classList.contains("pf-fuss") ? "" : " ik-s");""")
    # (3)
    r("""    const ph = IN.punkt_hinweis, pm = ph && N.find(m => m.id === ph.id),""",
      """    const ph = IN.punkt_hinweis, pm0 = ph && N.find(m => m.id === ph.id), pt = pm0 && SP && (SP.spieltage || []).find(t => t.nr === pm0.md),
      pm = pt && pt.partien.filter(p => p.status === "beendet").length > pt.partien.length / 2 ? null : pm0,""")
    return s

if __name__ == "__main__":
    t = patch(open(sys.argv[1], encoding="utf-8").read())
    open(sys.argv[2], "w", encoding="utf-8").write(t)
