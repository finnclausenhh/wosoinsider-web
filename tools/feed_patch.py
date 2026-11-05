# Feed-Ordnung (Finn 05.11.2026): zwischen eigenen Meldungen und Modulen mindestens 5 echte News, "Spielt sie?" an 3 Tagen je Runde oben, solange nicht geöffnet
import sys
def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:80]); return s.replace(a, b)
def patch(s):
    s = rep(s, """    let seit = 99; const SONDER = [[gefragtZeile, 21]], MINAB = 2;
    rest.forEach((m, gi) => { if (A && dt(A.news_zeit) >= (dt(m.zeit) || 0) && seit >= MINAB) { h += anaTeaser(A); A = null; seit = 0; } const u""",
"""    // Eigene Meldungen (Datenmeldungen, Tippspiel) und Module brauchen 5 echte News Abstand (Finn 05.11.2026)
    const AFID = new Set([...(AF && AF.news || []), ...(TAW || [])].map(n => n.id)), eigen = m => m.typ === "tipprunde" || AFID.has(m.id);
    const MINAB = 5; let seit = 3, gi = 0; const warte = [], SONDER = [[gefragtZeile, 14]];
    const trTop = rest.find(m => m.typ === "tipprunde" && trHoch(m));
    if (trTop) { h += karteF(trTop); seit = 0; }
    const raus = nx => { if (seit < MINAB) return;
      if (A && dt(A.news_zeit) >= (nx ? dt(nx.zeit) || 0 : 0)) { h += anaTeaser(A); A = null; seit = 0; return; }
      if (warte.length) { h += karteF(warte.shift()); seit = 0; return; }
      if (SONDER.length && gi >= SONDER[0][1]) { const x = SONDER.shift()[0](); if (x) { h += x; seit = 0; } } };
    rest.forEach(m => { if (m === trTop) return; if (eigen(m)) { warte.push(m); return; } raus(m); h += karteF(m); seit++; gi++; });
    raus(null); while (warte.length) h += karteF(warte.shift());
    function karteF(m){ let h = ""; const u""")
    s = rep(s, """newsKarte(m); seit++;
      if (SONDER.length && gi + 1 >= SONDER[0][1] && seit >= MINAB) { const x = SONDER.shift()[0](); if (x) { h += x; seit = 0; } } });
    if (A) h += anaTeaser(A);""", """newsKarte(m); return h; }
    if (A) h += anaTeaser(A);""")
    # trHoch: an 3 Tagen je Runde (Erstellung, Vortag Tippschluss, Tippschluss) oben, solange weder geöffnet noch getippt
    s = rep(s, """  const trBild = (m, g) =>""", """  function trHoch(m){
    const r = tippRunde(); if (!r || !SS) return false;
    let off = {}; try { off = JSON.parse(localStorage.getItem("wi_tr_offen") || "{}"); } catch (e) {}
    if (off[r.md] || Object.keys(TIPPS[r.md] || {}).length) return false;
    const tg = d => { const x = new Date(d); return x.getFullYear() * 1e4 + x.getMonth() * 100 + x.getDate(); }, heute = tg(Date.now());
    if (Date.now() >= r.schluss) return false;
    return [tg(dt(SS.erstellt)), tg(r.schluss - 864e5), tg(r.schluss)].includes(heute);
  }
  const trBild = (m, g) =>""")
    s = rep(s, """    if (m.typ === "tipprunde") { tippschein(); return; }""",
"""    if (m.typ === "tipprunde") { try { const r = tippRunde(), o = JSON.parse(localStorage.getItem("wi_tr_offen") || "{}"); if (r) { o[r.md] = 1; localStorage.setItem("wi_tr_offen", JSON.stringify(o)); } } catch (e) {} tippschein(); return; }""")
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
