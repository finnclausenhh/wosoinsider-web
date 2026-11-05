import sys
# Finn 05.11.2026 23:13: Fällt eine Innenverteidigerin aus, rückt eine Innenverteidigerin nach (nicht die Außenverteidigerin mit dem höchsten Einsatzwert)
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    s = rep(s, '''            d["y"].append(p.get("y", 0.5))
''', '''            d["y"].append(p.get("y", 0.5))
            d.setdefault("xs", []).append(abs(p.get("x", 0.5) - 0.5))  # Abstand zur Mitte: klein = zentral (IV), groß = außen (AV)
''')
    s = rep(s, '''    for p in POS:
        pool = sorted([k for k, d in verfuegbar.items() if d["pos"] == p and k not in elf], key=lambda k: score(spieler[k]), reverse=True)
        neu = pool[:formation[p]]''', '''    def mitte(d):  # True zentral, False außen, None unbekannt (aus den Startelf-Grafiken)
        xs = d.get("xs") or []
        return None if not xs else sorted(xs)[len(xs) // 2] < 0.22  # Median, ein Ausreißer ändert die Rolle nicht
    for p in POS:
        pool = sorted([k for k, d in verfuegbar.items() if d["pos"] == p and k not in elf], key=lambda k: score(spieler[k]), reverse=True)
        neu = pool[:formation[p]]
        if p == "ABW" and letzte and formation[p] == 4:  # nur Viererkette: zwei innen, zwei außen
            # Zentrale und äußere Plätze aus der letzten Startelf getrennt besetzen (Finn 05.11.2026: Naschenweng nie IV)
            vor = [q for q in letzte[0]["start"] if q.get("lp") == "ABW"] if letzte_formation else []
            n_c = sum(1 for q in vor if abs(q.get("x", 0.5) - 0.5) < 0.22) if len(vor) == formation[p] else 2
            neu = list(pool[:formation[p]]); rest = pool[formation[p]:]
            for zu_viel, fehlt in ((False, True), (True, False)):  # erst zu viele Außen, dann zu viele Innen
                soll = formation[p] - n_c if zu_viel is False else n_c
                while sum(1 for k in neu if mitte(spieler[k]) is zu_viel) > soll:
                    ers = next((k for k in rest if mitte(spieler[k]) is fehlt and (spieler[k]["stufe"] if spieler[k]["stufe"] is not None else 2) >= 2), None)
                    if not ers:
                        break
                    raus = [k for k in neu if mitte(spieler[k]) is zu_viel][-1]
                    neu[neu.index(raus)] = ers; rest.remove(ers)
                    spieler[ers]["regeln"].append(f"spielt {'innen' if fehlt else 'außen'} statt {spieler[raus]['n']}, wie in der letzten Startelf")
''')
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
