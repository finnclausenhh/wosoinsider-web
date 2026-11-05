import sys
# Finn 05.11.2026 21:32: Box Für Kickbase als Fahrplan (D: drei Spieltage mit Pfeilen, E: Jetzt und danach), je nach Lage
def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90]); return s.replace(a, b)
CSS = (".fp-tl{display:grid;grid-template-columns:1fr 20px 1fr 20px 1fr;align-items:stretch;margin-top:8px}"
       ".fp-st{position:relative;border-radius:12px;padding:10px 5px 9px;display:grid;justify-items:center;align-content:start;gap:3px;text-align:center;border:1.5px solid var(--c);background:color-mix(in srgb,var(--c) 13%,transparent)}"
       ".fp-st b{font-size:14px;color:var(--c);line-height:1.15}.fp-st .d{font-size:11px;color:var(--muted)}.fp-st .s{font-size:10.5px;color:#C9D1DE;line-height:1.25}"
       ".fp-j{position:absolute;top:-9px;left:50%;transform:translateX(-50%);font:700 9.5px ui-monospace,monospace;letter-spacing:1px;background:#F4F5F7;color:#0E1726;border-radius:99px;padding:2px 7px}"
       ".fp-eye{position:absolute;top:6px;right:6px;width:18px;height:18px;border-radius:50%;background:rgba(74,222,128,.18);display:grid;place-items:center}"
       ".fp-ar{display:grid;place-items:center}.fp-rows{display:grid;gap:6px}"
       ".fp-r{position:relative;display:flex;align-items:center;gap:10px;border-radius:12px;padding:11px 44px 11px 12px;border:1.5px solid var(--c);background:color-mix(in srgb,var(--c) 13%,transparent)}"
       ".fp-r .t{display:grid;gap:2px}.fp-r .t span{font:700 10.5px ui-monospace,monospace;letter-spacing:1.1px;color:var(--c)}.fp-r b{font-size:17px;color:var(--c)}"
       ".fp-r .fp-eye{top:50%;transform:translateY(-50%);right:12px;width:24px;height:24px}"
       ".fp-wer{display:grid;gap:7px}.fp-wer>span{font:700 10.5px ui-monospace,monospace;letter-spacing:1.2px;color:#A9B4C6}"
       ".fp-z{display:flex;align-items:center;gap:9px;font-size:13px;background:none;border:0;color:inherit;padding:0;text-align:left;cursor:pointer}.fp-z small{color:var(--muted);font-size:12px;margin-left:auto}"
       ".eo-txt{margin:0;font-size:13.5px;line-height:1.5}")
JS = r'''
    // Fahrplan der nächsten Spiele (Finn 05.11.2026): D mit drei Spieltagen, E mit Jetzt und danach, sonst die einfache Zeile
    const fahr = (() => {
      if (!zurueck || !p || !pst0 || pst0 === "ausgeschlossen") return null;
      const kom = alleSpiele().filter(q => (q.heim_k === k || q.gast_k === k) && q.status !== "beendet" && q.status !== "abgesagt" && terminiert(q)).sort((x, y) => dt(x.anstoss) - dt(y.anstoss)).slice(0, 3);
      if (kom.length < 2 || kom[0].id !== p.id) return null;
      const stamm = vorher.length >= 3 && stV / vorher.length >= .5, tab = (ligaStand() || {}).tab || [], plz = kk => tab.findIndex(r => r.k === kk);
      const top = q => { const a = plz(q.heim_k), b = plz(q.gast_k); return a >= 0 && b >= 0 && a < 4 && b < 4; }, geg = q => q.heim_k === k ? q.gast_k : q.heim_k;
      const R = ["ausgeschlossen", "unwahrscheinlich", "unsicher", "erwartet", "sicher"], ri = x => Math.max(0, R.indexOf(x));
      const eng = q => { const A = q.heim_k === k ? q.heim_aufstellung : q.gast_aufstellung, L = Array.isArray(A) ? A : A && typeof A === "object" ? Object.values(A).filter(Array.isArray).flat() : [];
        const e = L.filter(x => x && typeof x === "object").find(x => normS(x.voll || "") === normS(s.n) || normS(x.n) === normS(nachN(s.n))); return e && e.st; };
      const st = [pst0];
      kom.slice(1).forEach((q, i) => { let r = stamm ? Math.min(ri(st[i]) + (i ? 2 : 1), 3) : Math.min(ri(st[i]) + (i ? 1 : 0), 2);
        if (top(q)) r = Math.min(r, stamm ? 2 : 1);
        const e = eng(q); if (e && e !== "ausgeschlossen" && ri(e) < r) r = ri(e); st.push(R[r]); });
      const gleich = st.every(x => x === st[0]);
      const FB = (x, i) => x === "unwahrscheinlich" && i ? "#FF7A6B" : {unwahrscheinlich: "#F59E0B", unsicher: "#F5C26B", erwartet: "#4ADE80", sicher: "#4ADE80"}[x] || "#8A95A8";
      const lab = (x, i) => x === "unwahrscheinlich" ? (i === 0 ? (KZE ? ["Kurzeinsatz", "von der Bank"] : ["Bank", "Joker möglich"]) : ["Eher nicht", top(kom[i]) ? (stamm ? "Topspiel" : "Topspiel ohne Spielpraxis") : "noch ohne Rhythmus"])
        : x === "unsicher" ? (i && !stamm ? ["Chance", "wenn rotiert wird"] : ["Unsicher", i && top(kom[i]) ? "Topspiel" : "Startelf offen"])
        : x === "erwartet" ? ["Startelf", i ? "wieder Kandidatin" : "erwartet"] : x === "sicher" ? ["Gesetzt", ""] : ["Fällt aus", ""];
      const tag = q => { const d = dt(q.anstoss); return `${WT[d.getDay()]} ${String(d.getDate()).padStart(2, "0")}.${String(d.getMonth() + 1).padStart(2, "0")}.`; };
      const EYE = `<span class="fp-eye" title="Die Aufstellung kommt, bevor Kickbase schließt" aria-label="Aufstellung vor Kickbase-Schluss"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#4ADE80" stroke-width="2.6" stroke-linecap="round"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg></span>`;
      const eye = einsehbar(kom[0]) ? EYE : "";
      const PF = d => `<div class="fp-ar" aria-hidden="true"><svg width="${d ? 26 : 20}" height="${d ? 26 : 20}" viewBox="0 0 24 24"><path d="${d ? "M12 3v15M5 12l7 7 7-7" : "M4 12h13M12 5l7 7-7 7"}" fill="none" stroke="#8FB0FF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg></div>`;
      let html;
      const row = (q, t, w, c, e) => `<div class="fp-r" style="--c:${c}">${logo(geg(q), 30)}<div class="t"><span>${esc(t)}</span><b>${esc(w)}</b></div>${e || ""}</div>`;
      const jetztL = `JETZT · ${WT[dt(kom[0].anstoss).getDay()].toUpperCase()} GEGEN ${kname(geg(kom[0])).toUpperCase()}`;
      if (gleich) html = `<div class="fp-rows">${row(kom[0], "DIE NÄCHSTEN SPIELE", PL ? PL[0] : lab(st[0], 0)[0], FB(st[0], 0), eye)}</div>`;
      else if (st.length === 3 && st[1] !== st[2]) {
        html = `<div class="fp-tl">${kom.map((q, i) => { const [w, sub] = lab(st[i], i);
          return (i ? PF(0) : "") + `<div class="fp-st" style="--c:${FB(st[i], i)}">${i ? "" : `<span class="fp-j">JETZT</span>${eye}`}${logo(geg(q), 26)}<span class="d">${esc(tag(q))}</span><b>${esc(w)}</b>${sub ? `<span class="s">${esc(sub)}</span>` : ""}</div>`; }).join("")}</div>`;
      } else {
        const w0 = lab(st[0], 0), w1 = lab(st[1], 1), q1 = kom[1];
        html = `<div class="fp-rows">${row(kom[0], jetztL, st[0] === "unwahrscheinlich" && KZE ? "Nur Kurzeinsatz" : w0[0] + (w0[0] === "Bank" ? ", Joker möglich" : ""), FB(st[0], 0), eye)}${PF(1)}${row(q1, `DANACH · AB ${tag(q1)} GEGEN ${kname(geg(q1)).toUpperCase()}`, st[1] === "erwartet" ? "Startelf-Kandidatin" : st[1] === "unsicher" && !stamm ? "Chance bei Rotation" : w1[0], FB(st[1], 1))}</div>`;
      }
      // Wer vor ihr steht oder sie vertritt, Rotation auf der Position
      const GORT = {TW: "im Tor", IV: "in der Innenverteidigung", AV: "auf den Außenverteidigerpositionen", DM: "auf der Sechs", ZM: "im zentralen Mittelfeld", FL: "auf den Flügeln", ST: "im Sturm"};
      const mds = (s.spiele || []).slice(-5).map(e => e.md), gs = x => (x.spiele || []).filter(e => mds.includes(e.md) && e.art === "S").length;
      const grp = [s].concat(mates), dist = grp.filter(x => gs(x)).length, slots = Math.round(grp.reduce((a, x) => a + gs(x), 0) / Math.max(1, mds.length)), eig = gs(s);
      const wer = stamm ? mates.filter(fit).filter(x => ((x.spiele || []).slice(-1)[0] || {}).art === "S").sort((x, y) => q5(y) - q5(x)).slice(0, 1) : mates.filter(fit).filter(x => q5(x) > q5(s)).sort((x, y) => q5(y) - q5(x)).slice(0, 3);
      const werH = wer.length ? `<div class="fp-wer"><span>${stamm ? "VERTRITT SIE" : "VOR IHR " + (GORT[gr] || "").toUpperCase()}</span>${wer.map((x, i) => `<button class="fp-z" data-profil="${esc(x.id)}">${pfFoto(x, 30, 30, 15)}<b>${esc(nachN(x.n))}</b><small>${q5(x)} ${i ? "von 5" : "der letzten 5 in der Startelf"}</small></button>`).join("")}</div>` : "";
      let txt = "";
      if (stamm) txt = `<p class="eo-aus">Vor dem Ausfall stand sie in ${stV} von ${vorher.length} Ligaspielen in der Startelf. Wer jetzt kauft, kauft für die Wochen ${top(kom[1]) ? "nach dem Topspiel" : "danach"}.</p>`;
      else { const rot = gr && dist >= slots + 2 ? `${kname(k)} rotiert ${GORT[gr]}: ${dist} Spielerinnen in den letzten ${mds.length} Spielen, ${nachN(s.n)} stand ${eig === 0 ? "nicht" : eig === 1 ? "einmal" : eig + "-mal"} in der Startelf.` : "";
        const ch = st.length === 3 && top(kom[1]) && st[2] === "unsicher" ? ` Ihre Chance kommt eher gegen ${kname(geg(kom[2]))} als im Topspiel.` : "";
        txt = `<p class="eo-txt">Wieder fit, aber ohne Spielpraxis.${rot ? " " + rot : ""}${ch}</p>`; }
      return {html: html + txt + werH};
    })();
'''
def patch(s):
    s = rep(s, ".eo-plan b{font-size:15px;color:var(--c)}", ".eo-plan b{font-size:15px;color:var(--c)}" + CSS)
    a = '''    const plan = PL && p ? `<div class="eo-plan"'''
    s = rep(s, a, JS.lstrip("\n") + a)
    s = rep(s, '''    return `<section class="eo">${kap("Für Kickbase")}${plan}${m.kickbase ? `<p class="eo-kb">${esc(m.kickbase)}</p>` : ""}${z.map(''',
               '''    const zz = fahr ? z.filter(([t]) => t !== "Aufstellung" && t !== "Wen kann sie verdrängen?") : z;
    return `<section class="eo">${kap("Für Kickbase")}${fahr ? fahr.html : plan}${m.kickbase && !fahr ? `<p class="eo-kb">${esc(m.kickbase)}</p>` : ""}${zz.map(''')
    return s
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
