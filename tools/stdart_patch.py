"""Standard-Meldungen (Finn 07.11.2026, Brengel): statt "Wer spielt für sie" die Standards-Grafik des Vereins zeigen."""
import sys
p = sys.argv[1]; s = open(p, encoding="utf-8").read()
R = [
 ('''    ARTIKEL = id; const um = umfrageZu(m.id), tsA = tsArtikel(m);''',
  '''    ARTIKEL = id; const um = umfrageZu(m.id), tsA = tsArtikel(m);
    const stdA = !auf && !sc && !m.grafik && (m.tags || []).includes("STANDARD"), stdHtml = () => (IN ? stdFeld(KURZ[m.verein]) : "") + kbBox(m.kickbase);'''),
 ('''<div id="art-eo">${(auf || sc ? "" : einordnung(m)) || kbBox(m.kickbase)}</div>''',
  '''<div id="art-eo">${stdA ? stdHtml() : (auf || sc ? "" : einordnung(m)) || kbBox(m.kickbase)}</div>'''),
 ('''const eo = $("#art-eo"); if (eo && ARTIKEL === id) eo.innerHTML = einordnung(m) || kbBox(m.kickbase);''',
  '''const eo = $("#art-eo"); if (eo && ARTIKEL === id && !stdA) eo.innerHTML = einordnung(m) || kbBox(m.kickbase);'''),
 ('''    // Kommentare: nur in der öffentlichen Webversion (Skripte setzt ticker_bau.py ein)
    if (window.WIKOM) window.WIKOM.mount(m.id);
    window.scrollTo(0, 0);''',
  '''    if (stdA && !IN) loadIN().then(() => { const eo = $("#art-eo"); if (eo && ARTIKEL === id) eo.innerHTML = stdHtml(); }).catch(() => {});
    // Kommentare: nur in der öffentlichen Webversion (Skripte setzt ticker_bau.py ein)
    if (window.WIKOM) window.WIKOM.mount(m.id);
    window.scrollTo(0, 0);'''),
]
for a, b in R:
    assert s.count(a) == 1, a[:60]
    s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok", p)
