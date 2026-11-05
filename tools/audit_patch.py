# Audit 05.11.2026: Netz-Beschriftung rechts lief über den Kartenrand
import sys
def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    s = rep(s, '<svg class="ww-netz" viewBox="-10 2 320 222"', '<svg class="ww-netz" viewBox="-28 2 356 222"')
    # Netz: Zusatz "gleichauf mit N" nur in den Kacheln, im Netz zu lang
    s = rep(s, 'class="nv" fill="${rFarbe(w[3])}">${esc(rText(w[3]))}</text>', 'class="nv" fill="${rFarbe(w[3])}">${esc(rText(w[3]).replace(/, gleichauf mit \\d+$/, ""))}</text>')
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
