# Noten zählen ab 46 Minuten, also mehr als eine Halbzeit (Finn 05.11.2026, vorher 60)
import sys, re
def patch(s):
    n0 = s.count("[2] >= 60")
    s = s.replace("[2] >= 60", "[2] >= 46").replace("[2] < 60", "[2] < 46")
    s = s.replace("ab 4 Einsätzen über 60 Minuten", "ab 4 Einsätzen über 45 Minuten").replace("Noten ab 60 Minuten", "Noten ab 46 Minuten")
    s = s.replace("Ø Note der Spielerinnen ab 60 Minuten", "Ø Note der Spielerinnen ab 46 Minuten").replace("Blasse Noten: unter 60 Minuten, zählen nicht.", "Blasse Noten: bis 45 Minuten, zählen nicht.")
    s = s.replace("nur Einsätze ab 60 Minuten", "nur Einsätze ab 46 Minuten").replace("zählen nur Einsätze ab 60 Minuten", "zählen nur Einsätze ab 46 Minuten")
    assert n0 >= 10, n0
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
