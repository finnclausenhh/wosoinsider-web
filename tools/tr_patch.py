# Spielt sie? als normale Kachel mit Foto-Collage (Entwurf C, Finn 05.11.2026): höchstens 2 Fotos je Verein, "5 FRAGEN" mittig wie das VS,
# am ersten Tag einmalig als größeres Banner mit kleinem Knopf
import sys
def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:90]); return s.replace(a, b)
def patch(s):
    s = rep(s, """      kurz: `Spielt sie? ${r.fragen.length} Fragen zum ${r.md}. Spieltag`,""",
"""      kurz: `${r.fragen[0].frage} Und ${r.fragen.length - 1} weitere Fragen`,""")
    s = rep(s, """  const trBild = (m, g) => `<div class="bild fd-b" style="width:${g}px;height:${g}px;border-radius:${g > 70 ? 11 : 8}px" aria-hidden="true"><b>${m.n_fragen}</b><small>FRAGEN</small></div>`;""",
"""  // Fotos der Runde: je Frage die erste Spielerin mit echtem Foto, höchstens 2 je Verein
  function trFotos(n){
    const r = tippRunde(); if (!r) return [];
    const echt = nm => { const f = FOTOS[nm]; return f && !f.platzhalter && (f.portrait || f.datei) ? (f.portrait || f.datei) : ""; };
    const kand = r.fragen.map(q => { const l = [];
      if (q.s) l.push({src: echt(q.s.n), k: q.s.k || q.k});
      q.optionen.forEach(o => { if (o.sid) { const s = spById(o.sid); if (s) l.push({src: echt(s.n), k: s.k}); return; }
        const u = q.umfrage ? (q.umfrage.optionen || []).find(x => x.id === o.id) : null; if (u && u.nachname && !u.logo) l.push({src: echt(u.n), k: q.k}); });
      return l.filter(x => x.src); });
    const out = [], je = {};
    for (let runde = 0; runde < 4 && out.length < n; runde++) kand.forEach(l => { const x = l[runde]; if (!x || out.length >= n || out.some(y => y.src === x.src) || (je[x.k] || 0) >= 2) return; je[x.k] = (je[x.k] || 0) + 1; out.push(x); });
    return out;
  }
  const trBild = (m, g) => { const f = trFotos(4), r = g > 70 ? 11 : 8;
    if (f.length < 4) return `<div class="bild fd-b" style="width:${g}px;height:${g}px;border-radius:${r}px" aria-hidden="true"><b>${m.n_fragen}</b><small>FRAGEN</small></div>`;
    return `<div class="bild trc" style="width:${g}px;height:${g}px;border-radius:${r}px" aria-hidden="true">${f.map(x => `<img src="${esc(x.src)}" alt="" loading="lazy">`).join("")}<span class="trc-m" style="--d:${Math.round(g * .5)}px"><b>${m.n_fragen}</b><small>FRAGEN</small></span></div>`; };
  // Am ersten Tag, an dem jemand die Runde sieht, einmal als Banner
  function trGross(m){
    const r = tippRunde(); if (!r) return false;
    let g = {}; try { g = JSON.parse(localStorage.getItem("wi_tr_gross") || "{}"); } catch (e) {}
    const heute = new Date().toDateString();
    if (!g[r.md]) { g[r.md] = heute; try { localStorage.setItem("wi_tr_gross", JSON.stringify(g)); } catch (e) {} }
    return g[r.md] === heute;
  }
  function trBanner(m){
    const r = tippRunde(), f = trFotos(5), rest = r ? r.schluss - Date.now() : 0, tg = Math.floor(rest / 864e5), st = Math.floor(rest % 864e5 / 36e5);
    const mein = r ? Object.keys(TIPPS[r.md] || {}).length : 0;
    return `<button class="trb" data-id="${esc(m.id)}"><span class="trb-k"><span>SPIELT SIE? · ${r ? r.md : ""}. SPIELTAG</span>${rest > 0 ? `<i>noch ${tg ? tg + " T " : ""}${st} Std</i>` : ""}</span>
      <span class="trb-m"><span class="trb-f">${f.map(x => `<img src="${esc(x.src)}" alt="">`).join("")}</span><b>${m.n_fragen} Fragen.<br>Wie gut kennst du die Liga?</b></span>
      <span class="trb-p">${Array.from({length: m.n_fragen}, (_, i) => `<i${i < mein ? ' class="an"' : ""}></i>`).join("")}</span>
      <span class="trb-u"><small>${mein} von ${m.n_fragen} getippt · 10 Punkte je Treffer</small><em>Tippen ›</em></span></button>`;
  }""")
    s = rep(s, """    if (trTop) { h += karteF(trTop); seit = 0; }""", """    if (trTop) { h += trGross(trTop) ? trBanner(trTop) : karteF(trTop); seit = 0; }""")
    s = rep(s, """.fd-b{display:grid!important;""", """.trc{display:grid!important;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:2px;background:var(--bg,#0E1726);overflow:hidden;position:relative;flex:none}
.trc img{width:100%;height:100%;object-fit:cover;object-position:50% 8%;display:block;background:#2A3B5E}
.trc-m{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);width:var(--d);height:var(--d);border-radius:50%;background:var(--bg,#0E1726);border:2px solid var(--line,rgba(255,255,255,.14));display:grid;place-content:center;justify-items:center;line-height:1}
.trc-m b{font-family:var(--f-display);font-weight:800;font-size:calc(var(--d) * .42);color:#fff}
.trc-m small{font-size:calc(var(--d) * .14);font-weight:800;letter-spacing:.4px;color:#8FB0FF;margin-top:1px}
.trb{display:grid;gap:12px;width:100%;text-align:left;margin:0 0 10px;border-radius:16px;padding:16px;background:linear-gradient(135deg,#1B2B57,#13203C 60%);border:1px solid rgba(110,155,255,.35);color:#fff;font:inherit;box-sizing:border-box}
.trb-k{display:flex;justify-content:space-between;align-items:center;font-size:10px;letter-spacing:1.2px;font-weight:800;color:#8FB0FF}
.trb-k i{font-style:normal;letter-spacing:0;font-size:11px;font-weight:700;color:#F5C518;background:rgba(245,197,24,.12);padding:3px 8px;border-radius:20px}
.trb-m{display:flex;align-items:center;gap:12px}.trb-m b{font-family:var(--f-display);font-weight:800;font-size:23px;line-height:1.02}
.trb-f{display:flex;flex:none}.trb-f img{width:40px;height:40px;border-radius:50%;object-fit:cover;object-position:50% 8%;border:2px solid #14213F;background:#2A3B5E}.trb-f img+img{margin-left:-12px}
.trb-p{display:flex;gap:4px}.trb-p i{flex:1;height:5px;border-radius:3px;background:rgba(255,255,255,.14)}.trb-p i.an{background:#2F5BFF}
.trb-u{display:flex;justify-content:space-between;align-items:center;gap:10px}.trb-u small{font-size:12px;color:#A9B4C6}
.trb-u em{font-style:normal;font-size:13px;font-weight:700;color:#fff;background:#2F5BFF;border-radius:8px;padding:6px 11px;white-space:nowrap}
.fd-b{display:grid!important;""")
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
