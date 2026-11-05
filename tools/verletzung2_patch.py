"""Verletzungstag aus dem Spiel (Finn 05.11.2026): Steht in Status oder Meldung, in welchem Spiel es passiert ist,
und hat sie in den 7 Tagen vor der Meldung genau dieses Spiel gespielt, zählt der Spieltag statt des Meldedatums."""
import sys
def rep(s, old, new):
    n = s.count(old); assert n == 1, (old[:90], n); return s.replace(old, new)
ALT = 'const v = (s.verlauf || []).slice().reverse().find(x => x.status === "raus"), seit = (v && v.stand) || st.stand; if (!seit) return null;'
NEU = '''const v = (s.verlauf || []).slice().reverse().find(x => x.status === "raus"); let seit = (v && v.stand) || st.stand; if (!seit) return null;
    { const dm = new Date(seit + "T12:00"), txt = normS([st.grund, v && v.grund].concat(N.filter(m => m.spielerin === s.n).flatMap(m => [m.headline].concat(m.text || []))).join(" "));
      const GEN = new Set(["fc", "sv", "vfl", "vfb", "tsg", "rb", "sc", "fsv", "bayer", "1899", "04", "05"]);
      const treffer = e => String(e.gegner || "").split(/[\\s.]+/).map(normS).filter(w => w.length >= 4 && !GEN.has(w)).some(w => txt.includes(w));
      const sp = (s.spiele || []).concat(s.pokal || []).map(e => ({...e, d: String(e.datum || "").slice(0, 10)}))
        .filter(e => e.d && (e.art === "S" || e.art === "E") && (dm - new Date(e.d + "T12:00")) / 864e5 >= 0 && (dm - new Date(e.d + "T12:00")) / 864e5 <= 7 && treffer(e))
        .sort((a, b) => b.d.localeCompare(a.d));
      if (sp.length && /spiel|partie|gegen/.test(txt)) seit = sp[0].d; }'''
def patch(s): return rep(s, ALT, NEU)
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read()
    if "Verletzungstag aus dem Spiel" in s or "const GEN = new Set" in s: print("schon drin", f); continue
    t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
