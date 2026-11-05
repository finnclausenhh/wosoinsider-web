import sys
def rep(s, old, new):
    n = s.count(old); assert n == 1, (old[:80], n); return s.replace(old, new)
OLD_BLOCK_START = '''      <div style="display:grid;gap:6px;padding-top:8px"><h3 class="disp" style="font-size:21px">Alle Schützinnen</h3>'''
OLD_BLOCK_END = '''</div>`).join("")}</div>${afStandards()}</section>`;'''
NEW_BLOCK = '''      <div style="display:grid;gap:4px;padding-top:8px"><h3 class="disp" style="font-size:21px">Wer schießt die Standards?</h3>
        <p class="af-st" style="font-size:12px">Je Verein die erste Schützin. Sicher: in den Spielberichten mehrfach belegt. Wahrscheinlich: 2 bis 3 Belege. Unsicher: erst ein Hinweis. Bei Ecken und Freistößen steht die Seite dabei, wenn sie belegt ist. Elfmeter: auch die Schützinnen der Vorsaison.</p></div>
      ${SEL.size ? `<button class="lk" style="font-size:12px;justify-self:start;text-decoration:none" data-stdalle="1">${STDALLE ? "Nur meine Vereine" : "Alle 14 Vereine"}</button>` : ""}
      <div class="sz-l">${r.map(s => `<div class="szk"><div class="sz-k">${logo(s.k, 20)}<b>${esc(kname(s.k))}</b></div>
        <div class="sz-g">${szSlot("ECKEN", s.ecken, s.k, AF && AF.stdt && AF.stdt[s.k] && AF.stdt[s.k].seiten)}${szSlot("FREISTÖSSE", (s.fs || []).length ? s.fs : ((AF && AF.stdt && AF.stdt[s.k] && AF.stdt[s.k].fs) || []).slice(0, 1).map(x => [nachN(x[0]), 1]), s.k, AF && AF.stdt && AF.stdt[s.k] && AF.stdt[s.k].fs_seiten, szFsExtra(s.k))}${szSlot("ELFMETER", (s.elfer || []).length ? s.elfer : ((AF && AF.elf) || []).filter(x => x.k === s.k).map(x => [nachN(x.n), 1]), s.k, null, szElfExtra(s.k, s.elfer))}</div>
        ${s.hinweis ? `<div class="hw">${svg(P.warn, "").replace("<svg", '<svg style="width:13px;height:13px;flex:none;stroke:currentColor;fill:none;stroke-width:2"')}<span>${esc(s.hinweis)}</span></div>` : ""}</div>`).join("")}</div>${afStandards()}</section>`;'''
HELPER = '''  // Schützinnen je Verein (Finn 04.11.2026): Foto der ersten Schützin, Wahrscheinlichkeit als Wort, Ecken nach Seite
  const SZ_STUFE = {3: ["Sicher", "#6E9BFF"], 2: ["Wahrscheinlich", "#22C55E"], 1: ["Unsicher", "#F59E0B"]};
  // Freistöße: wer direkt aufs Tor schießt (aus dem Liveticker)
  function szFsExtra(k){
    const d = AF && AF.stdt && AF.stdt[k] && AF.stdt[k].fs_direkt;
    if (!(d && d.length)) return null;
    const erst = s0 => { const st = (IN.standards || []).find(q => q.k === k); return st && (st.fs || [])[0] && normS(st.fs[0][0]) === normS(s0); };
    const andere = d.filter(x => !erst(nachN(x[0])));
    return { zeile: andere.length === d.length ? `direkt aufs Tor <b>${d.map(x => esc(nachN(x[0]))).join(", ")}</b>` : `schießt auch direkt${andere.length ? `, außerdem <b>${andere.map(x => esc(nachN(x[0]))).join(", ")}</b>` : ""}` };
  }
  // Elfmeter: Vorsaison (API-Football), auch nach Vereinswechsel
  function szElfExtra(k, akt){
    const v = AF && AF.elf_vorsaison && AF.elf_vorsaison[k]; if (!v || !v.length) return null;
    const z = v.slice(0, 2).map(x => `<b>${esc(nachN(x[0]))}</b> ${x[1]}/${x[1] + x[2]}${x[3] ? ` (für ${esc(x[3])})` : ""}`).join(" · ");
    return { zeile: `Vorsaison ${z}`, ersatz: (akt || []).length ? null : [[nachN(v[0][0]), 1]] };
  }
  function szSlot(lbl, l, k, seiten, extra){
    if (!(l || []).length && extra && extra.ersatz) l = extra.ersatz;
    if (!(l || []).length) return `<div class="sz-s"><span class="sz-lb">${lbl}</span><span class="sz-n"><span class="sz-in sz-of">?</span><b class="sz-uk">Noch unklar</b></span><small>Bisher kein Beleg</small></div>`;
    const [n, b0] = l[0], b = Math.max(1, Math.min(3, l[0].length > 1 ? Number(b0) : 1)), s = SPN && findeSP(k, n), [wort, fa] = SZ_STUFE[b];
    const foto = s ? pfFoto(s, 26, 26, 13) : `<span class="sz-in">${esc(String(n).slice(0, 1))}</span>`;
    const sl = seiten && seiten.l ? nachN(seiten.l[0]) : null, sr = seiten && seiten.r ? nachN(seiten.r[0]) : null, gl = x => x && normS(x) === normS(n);
    const sd = !(sl || sr) ? "" : (gl(sl) || !sl) && (gl(sr) || !sr) ? `<small class="sz-sd">von ${sl && sr ? "links und rechts" : sl ? "links" : "rechts"}</small>`
      : `<small class="sz-sd">${sl ? `links <b>${esc(sl)}</b>` : ""}${sl && sr ? " · " : ""}${sr ? `rechts <b>${esc(sr)}</b>` : ""}</small>`;
    const rest = l.slice(1).map(x => x[0]).filter(x => !(sd && [sl, sr].some(y => y && normS(y) === normS(x)))).join(", ");
    return `<div class="sz-s"><span class="sz-lb">${lbl}</span>${s ? `<button class="sz-n" data-profil="${esc(s.id)}">` : '<span class="sz-n">'}${foto}<b>${esc(n)}</b>${s ? "</button>" : "</span>"}
      <span class="sz-w" style="--c:${fa}">${wort}</span>${sd}${extra && extra.zeile ? `<small class="sz-sd">${extra.zeile}</small>` : ""}${rest ? `<small>sonst ${esc(rest)}</small>` : ""}</div>`;
  }
'''
SCH = '''      ${AF.schuesse ? (() => { const f = Object.entries(AF.schuesse).filter(([k, x]) => (STDALLE || zeigen(k)) && x.f != null).sort((a, b) => b[1].f - a[1].f), m3 = Math.max(...Object.values(AF.schuesse).map(x => Math.max(x.f || 0, x.g || 0)), 1);
        return `<h3 class="disp" style="font-size:21px;margin-top:8px">Schüsse pro Spiel</h3><p class="af-st" style="font-size:12px">Viele eigene Schüsse = viele Chancen für die Offensive. Viele Schüsse gegen = viel Arbeit für die Torhüterin, Paraden bringen Kickbase-Punkte. Heller Teil = aufs Tor.</p>
        <div class="eck"><div class="eck-h"><span></span><span>EIGENE</span><span></span><span>GEGEN</span></div>${f.map(([k, x]) => `<div class="eck-r">${logo(k, 22)}<span class="f">${dez(x.f)}</span><span class="bw"><span class="bb sch"><i style="width:${x.f / m3 * 100}%"></i><i class="t" style="width:${(x.tf || 0) / m3 * 100}%"></i></span><small>aufs Tor ${dez(x.tf || 0)} · gegen aufs Tor ${dez(x.tg || 0)}</small></span><span class="g">${x.g != null ? dez(x.g) : "–"}</span></div>`).join("")}</div>`; })() : ""}
'''
CSS = '''
/* Schützinnen je Verein und Schüsse pro Spiel (04.11.2026) */
.sz-l{display:grid;gap:8px}
.szk{background:var(--card);border-radius:14px;padding:12px;display:grid;gap:10px}
.sz-k{display:flex;align-items:center;gap:8px}
.sz-k b{font:700 18px var(--f-display)}
.sz-g{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.sz-s{display:grid;gap:5px;align-content:start;min-width:0}
.sz-lb{font:600 10px var(--f-mono);letter-spacing:.6px;color:var(--muted)}
.sz-n{display:flex;align-items:center;gap:6px;min-width:0;text-align:left;padding:0;background:none;border:0}
.sz-n b{font-size:13px;font-weight:600;line-height:1.15;overflow-wrap:anywhere}
.sz-in{width:26px;height:26px;border-radius:50%;background:var(--soft);display:grid;place-items:center;font-size:11px;font-weight:700;flex:none}
.sz-w{justify-self:start;font-size:10.5px;font-weight:700;color:var(--c);border:1px solid var(--c);border-radius:999px;padding:1px 7px}
.sz-of{background:transparent;border:1.5px dashed #3A4B6E;color:#7F8BA0}
.sz-uk{color:#A9B4C6;font-weight:500}
.sz-sd b{color:#DCE3EF;font-weight:600}
.sz-s small{font-size:11px;color:var(--muted)}
.szk .hw{display:flex;gap:6px;align-items:flex-start;font-size:12px;line-height:1.4;color:#F5B041;border-top:1px solid var(--line);padding-top:8px}
.szk .hw svg{margin-top:2px}
.bb.sch{position:relative}
.bb.sch i{position:absolute;left:0;top:0;bottom:0;background:#2F5BFF}
.bb.sch i.t{background:#C7D6FF}
'''
def patch(s):
    a = s.index(OLD_BLOCK_START); b = s.index(OLD_BLOCK_END, a) + len(OLD_BLOCK_END)
    s = s[:a] + NEW_BLOCK + s[b:]
    s = rep(s, '  function zelle(l){', HELPER + '  function zelle(l){')
    s = rep(s, '''      ${AF.freist ? (() => {''', SCH + '''      ${AF.freist ? (() => {''')
    s = rep(s, '''Ecken pro Spiel und Elfmeter: API-Football''', '''Ecken, Schüsse pro Spiel und Elfmeter: API-Football''')
    i = s.find("</style>", s.find("--f-display")); s = s[:i] + CSS + s[i:]
    assert "—" not in s
    return s
if __name__ == "__main__":
    for f in sys.argv[1:]:
        s = open(f, encoding="utf-8").read()
        if "function szSlot" in s: print("schon drin", f); continue
        open(f, "w", encoding="utf-8").write(patch(s)); print("ok", f)
