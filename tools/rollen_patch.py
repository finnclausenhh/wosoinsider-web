"""Rollen im Kader (Finn 05.11.2026): Stammelf (genau 11: 1 Torhüterin, 10 Feldspielerinnen mit den meisten Startelf-Einsätzen,
mindestens 40 % der Spiele), Rotation, Joker, Ergänzung, ohne Einsatz, nicht im Kader. Dazu Talent (U20, bis 19 Jahre).
Status (verletzt, Babypause, gesperrt) bleibt wie bisher rechts."""
import sys
def rep(s, old, new):
    n = s.count(old); assert n == 1, (old[:90], n); return s.replace(old, new)

JS = r'''  // Rollen im Kader (Finn 05.11.2026)
  const ROLLE = {stamm: ["Stammelf", "#4ADE80"], rot: ["Rotation", "#8FB0FF"], joker: ["Joker", "#F5C26B"], erg: ["Ergänzung", "#A9B4C6"], ohne: ["ohne Einsatz", "#7F8BA0"], nie: ["nicht im Kader", "#7F8BA0"]};
  function kaderRollen(L, nMd){
    const z = s => { const sp = (s.spiele || []).filter(e => e.erg); return {S: sp.filter(e => e.art === "S").length, E: sp.filter(e => e.art === "E").length, B: sp.filter(e => e.art === "B").length, M: sp.reduce((a, e) => a + (e.min || 0), 0)}; };
    const Z = new Map(L.map(s => [s.id, z(s)])), R = {}, ok = s => Z.get(s.id).S >= Math.max(1, Math.ceil(nMd * .4));
    const sort = l => l.slice().sort((a, b) => Z.get(b.id).S - Z.get(a.id).S || Z.get(b.id).M - Z.get(a.id).M);
    const tw = sort(L.filter(s => s.pos === "TW")).filter(ok).slice(0, 1), feld = sort(L.filter(s => s.pos !== "TW")).filter(ok).slice(0, 10);
    tw.concat(feld).forEach(s => R[s.id] = "stamm");
    L.forEach(s => { if (R[s.id]) return; const x = Z.get(s.id);
      R[s.id] = x.S >= 2 ? "rot" : x.E >= 3 && x.E >= x.S ? "joker" : x.S + x.E > 0 ? "erg" : x.B > 0 ? "ohne" : "nie"; });
    return R;
  }
  const istTalent = s => { const a = (afSp(s.id) || {}).alter; return a != null && a <= 19; };
'''

CSS = '''
/* Rollen im Kader (05.11.2026) */
.kd-r{font-weight:600}.kd-t{font:700 9.5px var(--f-mono);letter-spacing:.04em;color:#C9A7FF;border:1px solid rgba(201,167,255,.5);border-radius:5px;padding:0 4px;justify-self:start;width:max-content;margin-top:3px}
.kd-leg{display:flex;flex-wrap:wrap;gap:4px 12px;font-size:11px;color:var(--muted);margin:2px 0 6px}.kd-leg span b{font-weight:600}
'''

def patch(s):
    s = rep(s, '  function vereinsKader(k, von){', JS + '  function vereinsKader(k, von){')
    s = rep(s, '''    const zeile = s => { const st = stArt(s.status); return `<button class="pf-tr kd" data-profil="${esc(s.id)}">${pfFoto(s, 44, 44, 8)}<span class="pf-tx"><b>${esc(s.n)}</b><small>${s.nr ? "Nr. " + esc(s.nr) : ""}</small>''',
               '''    const ROL = kaderRollen(L, kdMd);
    const zeile = s => { const st = stArt(s.status), r = ROLLE[ROL[s.id]]; return `<button class="pf-tr kd" data-profil="${esc(s.id)}">${pfFoto(s, 44, 44, 8)}<span class="pf-tx"><b>${esc(s.n)}</b><small>${s.nr ? "Nr. " + esc(s.nr) + " · " : ""}<span class="kd-r" style="color:${r[1]}">${r[0]}</span></small>${istTalent(s) ? '<span class="kd-t">TALENT</span>' : ""}''')
    s = rep(s, '''<h1 class="disp">${esc(Object.keys(KURZ).find(v => KURZ[v] === k) || kname(k))}</h1></div>${stdFeld(k)}''',
               '''<h1 class="disp">${esc(Object.keys(KURZ).find(v => KURZ[v] === k) || kname(k))}</h1></div>${stdFeld(k)}${kap("Kader")}<div class="kd-leg"><span><b style="color:#4ADE80">Stammelf</b> die 11 mit den meisten Startelf-Spielen</span><span><b style="color:#8FB0FF">Rotation</b> mehrfach in der Startelf</span><span><b style="color:#F5C26B">Joker</b> meist eingewechselt</span><span><b>Ergänzung</b> wenige Einsätze</span><span><b style="color:#C9A7FF">TALENT</b> bis 19 Jahre</span></div>''')
    i = s.find("</style>", s.find("--f-display")); s = s[:i] + CSS + s[i:]
    assert "—" not in s
    return s

if __name__ == "__main__":
    for f in sys.argv[1:]:
        s = open(f, encoding="utf-8").read()
        if "function kaderRollen" in s: print("schon drin", f); continue
        t = patch(s); open(f, "w", encoding="utf-8").write(t); print("rollen ok", f)
