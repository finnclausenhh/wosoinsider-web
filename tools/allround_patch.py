import sys
# Finn 05.11.2026 22:56: Typ "komplette Innenverteidigerin" heißt jetzt Allrounderin
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    s = rep(s, '''["komplette Innenverteidigerin", "stark im Aufbau und im Zweikampf"]''', '''["Allrounderin", "stark im Aufbau und im Zweikampf"]''')
    s = rep(s, '''"komplette Innenverteidigerin": "Aufbau und Zweikampf", ''', '')
    s = rep(s, '''"komplette Innenverteidigerin": ["eine komplette Innenverteidigerin", "einer kompletten Innenverteidigerin"]''', '''"Allrounderin": ["eine Allrounderin", "einer Allrounderin"]''')
    s = rep(s, '''"komplette Innenverteidigerin": "Im Aufbau''', '''"Allrounderin": "Im Aufbau''')
    assert "komplette Innenverteidigerin" not in s
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
