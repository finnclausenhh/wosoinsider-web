# Lange Namen im Profilkopf (z. B. NASCHENWENG, DAMNJANOVIĆ) liefen unter das Mini-Spielfeld: Schrift verkleinern, bis jede Zeile passt
import sys
def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    a = '''    const ak = document.querySelector(".pfw-r .an"); if (ak) ak.parentElement.scrollLeft = ak.offsetLeft - ak.parentElement.clientWidth / 2 + ak.offsetWidth / 2;'''
    s = rep(s, a, a + '''
    const nh = document.querySelector(".pf-kt h1"); if (nh) { let fs = 34; nh.style.fontSize = ""; while (nh.scrollWidth > nh.clientWidth + 1 && fs > 22) { fs -= 2; nh.style.fontSize = fs + "px"; } }''')
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
