"""Design-Auswahl Finn 07.11.2026 (Canvas 1gQBj5kLA6gSvtSRDn1deT Variante B, Tor/Vorlage AUHGn8HnMUgRbsi8kgu2Kd Variante C).

Aufruf: python3 tools/design0711_patch.py <eingabe.html> <ausgabe.html>  (ticker/index.html und Artifact index.html)
1B Standards: drei Kacheln (Ecken, Freistoß, Elfmeter) unter Spielfeld und Bank statt gelber Hinweise über dem Feld
2B Spielerin antippen: schlanke Schnellinfo-Zeile (Foto, Status, Einsatzwert, kurzer Grund, führt ins Profil), kein Begründungs-Kasten mehr
3B Prognose: Ring mit erwarteter Trefferquote dieser Elf (Quoten je Status aus tracking/trefferquote.json) über dem Feld
4B Platzhalter ohne Foto: Status als farbiger Ring statt Symbol auf der Rückennummer; Direkte Duelle als große Zahlen
2C Tor und Vorlage: runde Marken rechts am Foto (weiß Tor, blau V, Zähler), Karte links oben, Leuchtring für Scorerinnen
"""
import sys

R = []
def r(alt, neu, n=1):
    R.append((alt, neu, n))

# 1B + 3B im Team-Block
r('''${!vorbei && a && !(anstoss && dt(anstoss) && dt(anstoss).getTime() <= Date.now()) ? stdHinweis(k, a) : ""}${inh}</div>`;''',
  '''${progRing(a)}${inh}${!vorbei && a && !(anstoss && dt(anstoss) && dt(anstoss).getTime() <= Date.now()) ? stdKacheln(k, a) : ""}</div>`;''')

# 2B
r('''    h += `<div class="begr">${kap("Begründung")}${g ? begrAnalyse(k, g) : '<span class="mu">Spielerin antippen, dann steht hier, warum wir sie so einschätzen.</span>'}</div>`;''',
  '''    if (g) h += quickInfo(k, g);''')

# 4B + 2C im Spielfeld
r('''        const badge = o.modus === "p" && STUFE[s.st] ? `<span class="sb">${stufeSym(s.st, 16)}</span>` : "";''',
  '''        const ph = istPlatzhalter(src), badge = o.modus === "p" && STUFE[s.st] && !ph ? `<span class="sb">${stufeSym(s.st, 16)}</span>` : "";
        let foKl = o.modus === "p" && STUFE[s.st] && ph ? " ph-r" : "", foSt = foKl ? `--rc:${STUFE[s.st][1]};` : "";''')
r('''        if (o.modus === "o") { if (s.tore > 0) ex += `<span class="tg" aria-label="${s.tore} ${s.tore > 1 ? "Tore" : "Tor"}">${s.tore <= 3 ? BALL.repeat(s.tore) : BALL + "<b>×" + s.tore + "</b>"}</span>`; if (s.vorl > 0) ex += `<span class="as" aria-label="${s.vorl} ${s.vorl > 1 ? "Vorlagen" : "Vorlage"}">${VORL}${s.vorl > 1 ? `<b>${s.vorl}</b>` : ""}</span>`;''',
  '''        if (o.modus === "o") { if (s.tore > 0) ex += `<span class="ob o1" aria-label="${s.tore} ${s.tore > 1 ? "Tore" : "Tor"}">${BALL}${s.tore > 1 ? `<b>${s.tore}</b>` : ""}</span>`; if (s.vorl > 0) ex += `<span class="ob ov ${s.tore > 0 ? "o2" : "o1"}" aria-label="${s.vorl} ${s.vorl > 1 ? "Vorlagen" : "Vorlage"}">V${s.vorl > 1 ? `<b>${s.vorl}</b>` : ""}</span>`;
          if (s.tore > 0) foKl = " sc-t"; else if (s.vorl > 0) foKl = " sc-v";''')
r('''if (s.rot) ex += `<span class="kt">${karte(true)}</span>`; else if (s.gelb) ex += `<span class="kt">${karte(false)}</span>`; }
        const unten''', '''if (s.rot) ex += `<span class="ob o3">${karte(true)}</span>`; else if (s.gelb) ex += `<span class="ob o3">${karte(false)}</span>`; }
        const unten''')
r('''<span class="fo" style="width:${F}px;height:${F}px">''', '''<span class="fo${foKl}" style="${foSt}width:${F}px;height:${F}px">''')

# 4B Direkte Duelle
r('''${du ? (() => { const n = v.dus[0] + v.dus[1] + v.dus[2] || 1, pz = x => x / n * 100;
        return `<div class="dz-dl">${kap("Direkte Duelle seit 2023 · " + n + " Spiele")}<div class="dz-db">${v.dus[0] ? `<span style="width:${pz(v.dus[0])}%;background:#4ADE80">${v.dus[0]}</span>` : ""}${v.dus[1] ? `<span style="width:${pz(v.dus[1])}%;background:#A9B4C6">${v.dus[1]}</span>` : ""}${v.dus[2] ? `<span style="width:${pz(v.dus[2])}%;background:#FF8A8A">${v.dus[2]}</span>` : ""}</div><div class="dz-dk"><span><i style="background:#4ADE80"></i>${esc(kname(v.h))} ${v.dus[0]}</span><span><i style="background:#A9B4C6"></i>Remis ${v.dus[1]}</span><span><i style="background:#FF8A8A"></i>${esc(kname(v.g))} ${v.dus[2]}</span></div></div>`; })() : ""}''',
  '''${du ? (() => { const n = v.dus[0] + v.dus[1] + v.dus[2], L = (v.du || []).slice().sort((a, b) => String(b.d).localeCompare(String(a.d))), z = L[0];
        const tg = L.reduce((x, d) => [x[0] + (d.t[0] || 0), x[1] + (d.t[1] || 0)], [0, 0]), dat = d => /^\\d{4}-\\d\\d-\\d\\d/.test(d.d) ? ` (${d.d.slice(8, 10)}.${d.d.slice(5, 7)}.${d.d.slice(2, 4)})` : "";
        const fb = i => v.dus[i] > Math.max(...v.dus.filter((_, j) => j !== i)) ? (i === 1 ? "#F4F5F7" : "#8FB0FF") : "#A9B4C6";
        return `<div class="dz-dl dz-d4">${kap("Direkte Duelle seit 2023 · " + n + (n === 1 ? " Spiel" : " Spiele"))}<div class="d4"><div><b style="color:${fb(0)}">${v.dus[0]}</b><small>Siege ${esc(kname(v.h))}</small></div><div class="m"><b style="color:${fb(1)}">${v.dus[1]}</b><small>Remis</small></div><div><b style="color:${fb(2)}">${v.dus[2]}</b><small>Siege ${esc(kname(v.g))}</small></div></div>
          <p class="d4z">Tore ${tg[0]}:${tg[1]}${z ? ` · zuletzt ${esc(kname(v.h))} ${z.t[0]}:${z.t[1]} ${esc(kname(v.g))}${dat(z)}` : ""}</p></div>`; })() : ""}''')

# Hilfsfunktionen vor feld()
r('''  function feld(elf, k, o){''', '''  let PHS = null, PHS_N = -1, PR_LADEN = false;
  function istPlatzhalter(src){
    if (!src) return false; const n = Object.keys(FOTOS || {}).length;
    if (!PHS || PHS_N !== n) { PHS_N = n; PHS = new Set(Object.values(FOTOS || {}).filter(f => f && f.platzhalter).flatMap(f => [f.portrait, f.datei]).filter(Boolean)); }
    return PHS.has(src);
  }
  function progRing(a){
    if (!a || a.typ !== "prognose" || (a.startelf || []).length !== 11) return "";
    if (!TQ) { if (!PR_LADEN) { PR_LADEN = true; gLaden().then(() => { if (GAME && VIEW === "spielplan") spiel(GAME, true); }).catch(() => {}); } return ""; }
    const g = TQ.gesamt, js = g && g.je_stufe; if (!js || !g.teams) return "";
    const qs = a.startelf.map(s => js[s.st] && js[s.st].quote != null ? js[s.st].quote : null); if (qs.some(x => x == null)) return "";
    const erw = qs.reduce((x, y) => x + y, 0), pz = Math.round(erw / 11 * 100), lo = Math.floor(erw), hi = Math.ceil(erw);
    const cnt = {}; a.startelf.forEach(s => { cnt[s.st] = (cnt[s.st] || 0) + 1; });
    const tl = [["sicher", "sichere"], ["erwartet", "erwartete"], ["unsicher", "unsichere"], ["unwahrscheinlich", "unwahrscheinliche"]].filter(([k]) => cnt[k]).map(([k, w]) => cnt[k] + " " + w);
    const C = 2 * Math.PI * 27;
    return `<div class="pr-ring"><div class="r"><svg viewBox="0 0 64 64" aria-hidden="true"><circle cx="32" cy="32" r="27" fill="none" stroke="rgba(255,255,255,.12)" stroke-width="7"/><circle cx="32" cy="32" r="27" fill="none" stroke="#8FB0FF" stroke-width="7" stroke-dasharray="${(C * pz / 100).toFixed(1)} ${C.toFixed(1)}" transform="rotate(-90 32 32)" stroke-linecap="round"/></svg><b>${pz}%</b></div>
      <div class="t"><b>So sicher sind wir</b><span>${tl.length > 1 ? tl.slice(0, -1).join(", ") + " und " + tl[tl.length - 1] : tl[0]} Spielerinnen, also ${lo === hi ? lo : lo + " bis " + hi} von 11 richtig erwartet. Bisher lagen wir im Schnitt bei <b>${String(g.elf_treffer_schnitt).replace(".", ",")} von 11</b> (${g.teams} Aufstellungen geprüft).</span></div></div>`;
  }
  function quickInfo(k, g){
    const s = spAus(k, g), st = STUFE[g.st], w = String(g.warum || ""), wert = (w.match(/Einsatzwert (\\d+) ?%/) || [])[1], src = fotoSp(k, g);
    const txt = kurzWarum(w.replace(/,?\\s*Einsatzwert \\d+ ?%/, ""));
    return `<button class="qi"${s ? ` data-profil="${esc(s.id)}"` : ""}><span class="qf"${src ? "" : ` style="background:${KFARBE[k] || "var(--soft)"}"`}>${src ? `<img src="${esc(src)}" alt="" loading="lazy">` : `<b>${initialen(g.voll || g.n)}</b>`}</span>
      <span class="qm"><span class="q1"><b>${esc(g.n)}</b>${st ? `${stufeSym(g.st, 14)}<em style="color:${st[1]}">${esc(st[2])}${wert ? " · " + wert + " %" : ""}</em>` : ""}</span>${txt ? `<small>${esc(txt)}</small>` : ""}</span>${s ? '<span class="qa">›</span>' : ""}</button>`;
  }
  function stdKacheln(k, a){
    const elf = (a && a.startelf) || []; if (elf.length < 11 || !IN) return "";
    const D = sfDaten(k), drin = n => elf.some(s => sfGl(s.voll || s.n, n)), e3 = (AF && AF.elf3 && AF.elf3[k]) || [];
    const bil = n => { const x = e3.find(y => sfGl(y[0], n)); return x ? `${x[1]} von ${x[1] + x[2]}` : ""; };
    const t = [["Ecken", D.ecke], ["Freistoß", D.fs], ["Elfmeter", D.elf]].filter(([, x]) => x && x.n).map(([lbl, x]) => {
      let wer, sub, kl = "";
      if (drin(x.n)) { wer = nachN(x.n); sub = lbl === "Elfmeter" && bil(x.n) ? bil(x.n) + " verwandelt" : "wie immer"; }
      else { let e = (x.alt || []).find(drin); if (!e && lbl === "Elfmeter") { const z = e3.find(y => drin(y[0]) && !sfGl(y[0], x.n)); if (z) e = z[0]; }
        wer = e ? nachN(e) : "offen"; sub = "statt " + nachN(x.n) + (e && lbl === "Elfmeter" && bil(e) ? " · " + bil(e) : ""); kl = e ? " ers" : " off"; }
      return `<div class="sk3${kl}"><span class="l">${lbl}</span><b>${esc(wer)}</b><small>${esc(sub)}</small></div>`; });
    if (!t.length) return "";
    return `<div class="sk3w"><div class="sk3k"><span>Standards in diesem Spiel</span><button class="lk" data-kader="${esc(k)}" data-ziel="std">Alle Standards ›</button></div><div class="sk3r">${t.join("")}</div></div>`;
  }
  function feld(elf, k, o){''')

CSS = '''.spl .ob{position:absolute;width:20px;height:20px;border-radius:50%;display:flex;align-items:center;justify-content:center;z-index:2;box-shadow:0 0 0 2px var(--card);font:800 10px/1 var(--f-mono)}
.spl .ob .ball{width:16px;height:16px;display:block}
.spl .ob.o1{top:-6px;right:-9px;background:#fff;color:#0B1220}
.spl .ob.o2{top:15px;right:-15px}
.spl .ob.ov{background:#8FB0FF;color:#0B1220}
.spl .ob.o3{top:-4px;left:-7px;width:auto;height:auto;border-radius:0;box-shadow:none;background:none;line-height:0}
.spl .ob.o3 .krt{display:block;width:12px;height:16px;border-radius:2px;transform:rotate(-10deg);box-shadow:0 0 0 1.5px var(--card)}
.spl .ob b{position:absolute;right:-6px;top:-6px;background:#2F5BFF;color:#fff;border-radius:7px;font:800 9px/1 var(--f-mono);padding:2px 3px}
.spl .fo.sc-t .cl{box-shadow:0 0 0 2px #fff,0 0 16px -2px rgba(255,255,255,.45)}
.spl .fo.sc-v .cl{box-shadow:0 0 0 2px #8FB0FF,0 0 16px -2px rgba(143,176,255,.4)}
.spl .fo.ph-r .cl{box-shadow:0 0 0 3px var(--rc)}
.pr-ring{display:flex;gap:14px;align-items:center;background:var(--soft);border-radius:14px;padding:12px 14px;margin-bottom:10px}
.pr-ring .r{position:relative;width:64px;height:64px;flex:none}.pr-ring .r svg{width:64px;height:64px;display:block}
.pr-ring .r b{position:absolute;inset:0;display:grid;place-items:center;font:800 20px var(--f-display)}
.pr-ring .t{display:grid;gap:3px}.pr-ring .t>b{font-weight:700;font-size:15px}.pr-ring .t span{font-size:12.5px;line-height:1.4;color:var(--muted)}.pr-ring .t span b{color:var(--ink)}
.qi{display:flex;gap:12px;align-items:center;width:100%;background:var(--soft);border:0;border-radius:14px;padding:10px 12px;color:var(--ink);font:inherit;text-align:left;cursor:pointer;margin-top:10px}
.qi .qf{width:40px;height:40px;border-radius:50%;overflow:hidden;flex:none;display:grid;place-items:center}.qi .qf img{width:100%;height:100%;object-fit:cover;object-position:50% 0}.qi .qf b{font:800 14px var(--f-display);color:#fff}
.qi .qm{flex:1;min-width:0;display:grid;gap:2px}.qi .q1{display:flex;gap:6px;align-items:center}.qi .q1 b{font-size:14.5px}.qi .q1 em{font-style:normal;font-size:12px;font-weight:600}
.qi small{font-size:12px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.qi .qa{font-size:18px;color:#8FB0FF}
.sk3w{display:grid;gap:8px;margin-top:12px}.sk3k{display:flex;justify-content:space-between;align-items:baseline}
.sk3k span{font:600 11px var(--f-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}.sk3k .lk{font-size:12.5px;font-weight:600;background:none;border:0;padding:0}
.sk3r{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.sk3{background:var(--soft);border-radius:12px;padding:10px;display:grid;gap:3px;min-width:0}
.sk3 .l{font:600 10.5px var(--f-mono);letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.sk3 b{font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.sk3.ers b{color:#8FB0FF}.sk3.off b{color:#F5B041}
.sk3 small{font-size:11.5px;color:var(--muted)}
.dz-d4 .d4{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;text-align:center;margin-top:4px}
.dz-d4 .d4 b{display:block;font:800 40px/1 var(--f-display)}.dz-d4 .d4 .m b{font-size:28px}.dz-d4 .d4 small{font-size:12px;color:var(--muted)}
.dz-d4 .d4z{margin:6px 0 0;text-align:center;font-size:12px;color:var(--muted)}
'''

def main(a, b):
    s = open(a, encoding="utf-8").read()
    fehl = []
    for alt, neu, n in R:
        c = s.count(alt)
        if c != n: fehl.append((c, alt[:100])); continue
        s = s.replace(alt, neu)
    if fehl:
        for f in fehl: print("NICHT GEFUNDEN/MEHRFACH", f)
        sys.exit(1)
    i = s.rindex("</style>")
    s = s[:i] + CSS + s[i:]
    open(b, "w", encoding="utf-8").write(s)
    print("ok", len(R), "Ersetzungen")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
