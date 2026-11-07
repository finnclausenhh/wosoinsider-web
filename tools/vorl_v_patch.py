"""Vorlage als V (Finn 07.11.2026, vorerst bis zur Design-Auswahl) und liveMarken-Fix (_lv statt _lt), wie ticker-test 4aefc9b."""
import re, sys
p = sys.argv[1]; s = open(p, encoding="utf-8").read()
a1 = ".bsy.v{color:#8FB0FF}\n"
b1 = a1 + ".vorl.vt{display:inline-flex;align-items:center;justify-content:center;width:auto!important;height:auto!important;min-width:9px;font:800 11px/1 var(--f-body);font-style:normal}\n.bsy.v .vorl.vt{background:#8FB0FF;color:#0B1220;border-radius:4px;padding:2px 3px;font-size:9.5px}\n"
assert s.count(a1) >= 1 and ".vorl.vt{" not in s
s = s.replace(a1, b1, 1)
m = re.search(r"  const VORL = '<svg class=\"vorl\".*?</svg>';\n", s, re.S)
assert m
s = s[:m.start()] + "  // Finn 07.11.2026: Vorlage als \"V\" statt Schuh-Symbol\n  const VORL = '<i class=\"vorl vt\" aria-label=\"Vorlage\">V</i>';\n" + s[m.end():]
a3 = '''      alle.forEach(s => { if (s._lt) { ["tore", "vorl", "gelb", "rot", "gr", "_lt"].forEach(f => delete s[f]); }\n'''
b3 = a3 + '''        if (s._lv) { delete s.vorl; delete s._lv; }  // Finn 07.11.: nur die ergänzte Vorlage zurücknehmen, Tore und Karten aus der Aufstellung bleiben\n'''
assert s.count(a3) == 1; s = s.replace(a3, b3)
a4 = "if (s) { s._lt = true; s.vorl = (s.vorl || 0) + 1; } }); return; }"
assert s.count(a4) == 1; s = s.replace(a4, "if (s) { s._lv = true; s.vorl = (s.vorl || 0) + 1; } }); return; }")
open(p, "w", encoding="utf-8").write(s); print("ok", p)
