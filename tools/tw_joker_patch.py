"""Torhüterinnen bekommen kein "Joker möglich" und keinen "Kurzeinsatz" (Finn 13.11.2026, Reimann).
Torhüterinnen werden fast nie eingewechselt: steht eine TW auf der Bank, heißt es "Bank, spielt nur bei Ausfall".
Die Nummer 1 im Tor bekommt vor Topspielen keine Rotationskappe.
Gleiche Ersetzungen im Artifact (index.html)."""
import sys
ERS = [
 ('    const KZE = /(Kurzeinsatz|ein paar Minuten|einige Minuten|wenige Minuten|Minuten sammeln|von der Bank kommen|Einsatz von der Bank)/i.test(',
  '    const TWP = s.pos === "TW", KZE = !TWP && /(Kurzeinsatz|ein paar Minuten|einige Minuten|wenige Minuten|Minuten sammeln|von der Bank kommen|Einsatz von der Bank)/i.test('),
 ('(KZE ? ["Kurzeinsatz", "von der Bank"] : ["Bank", "Joker möglich"])',
  '(KZE ? ["Kurzeinsatz", "von der Bank"] : TWP ? ["Bank", "nur bei Ausfall"] : ["Bank", "Joker möglich"])'),
 ('w0[0] + (w0[0] === "Bank" ? ", Joker möglich" : "")',
  'w0[0] + (w0[0] === "Bank" ? (TWP ? ", spielt nur bei Ausfall" : ", Joker möglich") : "")'),
 ('        if (top(q)) r = Math.min(r, stamm ? 2 : 1);',
  '        if (top(q) && !(TWP && stamm)) r = Math.min(r, stamm ? 2 : 1);  // Nummer 1 im Tor wird vor Topspielen nicht rotiert'),
]
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
for a, b in ERS:
    assert s.count(a) == 1, a[:50]
    s = s.replace(a, b)
open(p, "w", encoding="utf-8").write(s)
print("ok", p)
