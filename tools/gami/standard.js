  // ---------------- Standard-Check (Finn 04.11.2026): Messlatte mit Größe und Kopfbällen nach Standards
  // Leerer Kreis = Kopfball nach Standard ohne Tor, gelber Kreis = Kopfball nach Standard mit Tor.
  const SC_FAHNE = `<svg class="sc-deko" viewBox="0 0 390 300" preserveAspectRatio="xMinYMin slice" aria-hidden="true"><circle cx="250" cy="330" r="190" fill="none" stroke="#1C2A47" stroke-width="1.5"/><line x1="22" y1="22" x2="22" y2="66" stroke="#F4F5F7" stroke-width="2.5"/><path d="M22 22 L46 30 L22 38 Z" fill="#2F5BFF"/><path d="M28 62 Q 150 -12 232 70" fill="none" stroke="#6E9BFF" stroke-width="2.5" stroke-dasharray="1.5 8" stroke-linecap="round"/><circle cx="236" cy="76" r="8" fill="#F4F5F7"/></svg>`;
  const scSp = m => ((m.grafik && m.grafik.sp) || []);
  const scFoto = (x, cls) => { const f = FOTOS[x.n] || {}, src = f.portrait || f.datei; return `<span class="${cls}" style="--vc:${ring(x.k)}">${src ? `<img src="${esc(src)}" alt="" loading="lazy" onerror="this.remove()">` : `<b>${esc(nachN(x.n).slice(0, 1))}</b>`}</span>`; };
  const scBaelle = (x, kl) => Array.from({length: x.kopf}, (_, i) => `<i class="${i < x.tore ? "t" : ""}${kl ? " " + kl : ""}"></i>`).join("");
  const scZahl = (n, eins, mehr) => `${n} ${n === 1 ? eins : mehr}`;
  function scHero(m, gross){
    const l = scSp(m)[0]; if (!l) return "";
    const f = FOTOS[l.n] || {}, src = f.datei || f.portrait, k = l.k;
    return `<div class="sc-hero${gross ? " gr" : ""}">${SC_FAHNE}
      <span class="sc-wm">${wm(k)}</span>${src ? `<img class="sc-f" src="${esc(src)}" alt="" onerror="this.remove()">` : ""}
      <span class="sc-zahl"><b>${l.kopf}</b><span>${l.kopf === 1 ? "KOPFBALL" : "KOPFBÄLLE"}</span><span class="h">NACH STANDARD</span></span>
      ${gross ? `<span class="sc-name"><small>${esc(l.n.split(" ").slice(0, -1).join(" ").toUpperCase())}</small>${esc(nachN(l.n).toUpperCase())}</span>` : ""}
      <span class="sc-lg">${logo(k, gross ? 28 : 24)}</span>
      ${f.autor ? `<span class="sc-cr">Foto: ${esc(f.autor)}</span>` : ""}</div>`;
  }
  function scKarte(m){
    const sp = scSp(m), rest = sp.slice(1);
    return `<button class="nk sc" data-id="${esc(m.id)}">${scHero(m)}
      <div class="sc-b"><div class="tags">${(m.tags || []).map(tag).join("")}</div>
      <h2>${esc(m.kurz || m.headline)}</h2>
      <div class="sc-mehr"><span class="sc-av">${rest.map(x => scFoto(x, "a")).join("")}</span><span class="mu">+ ${rest.length} Spielerinnen</span><span class="sc-los">Ansehen ›</span></div>
      <div class="meta">${esc(relativ(m.zeit))}</div></div></button>`;
  }
  function scMesslatte(m){
    const sp = scSp(m); if (!sp.length) return "";
    const cms = sp.map(x => x.cm).filter(Boolean), lo = 150, hi = Math.max(185, Math.max(...cms, 0) + 8), H = 300, B = 290;
    const y = c => B - (c - lo) / (hi - lo) * (B - 10);
    const linien = [150, 160, 170, 180].filter(c => c < hi).map(c => `<span class="sc-gl" style="top:${y(c).toFixed(1)}px"><em>${c}</em></span>`).join("");
    const w = 100 / sp.length;
    const spalten = sp.map((x, i) => { const cm = x.cm || lo + 15, t = y(cm);
      return `<div class="sc-sp${i === 0 ? " eins" : ""}" style="left:${(i * w).toFixed(2)}%;width:${w.toFixed(2)}%">
        <span class="sc-bar${x.cm ? "" : " offen"}" style="top:${t.toFixed(1)}px;height:${(B - t).toFixed(1)}px"></span>
        ${scFoto(x, "sc-kopf").replace('class="sc-kopf"', `class="sc-kopf" style="top:${(t - 20).toFixed(1)}px;--vc:${ring(x.k)}"`).replace(/ style="--vc:[^"]*"(?=>)/, "")}
        <span class="sc-baelle" style="bottom:${(H + 66 - t + 24).toFixed(1)}px">${x.tore ? '<em class="t">TOR</em>' : ""}${scBaelle(x)}</span>
        <span class="sc-fuss"><b>${esc(nachN(x.n).toUpperCase())}</b><small>${x.cm ? x.cm + " cm" : "Größe offen"}</small>${logo(x.k, 18)}</span></div>`; }).join("");
    return `<section class="sc-ml"><div class="sc-mlk"><h3 class="disp">Messlatte</h3><span class="mu">Größe und Kopfbälle</span></div>
      <div class="sc-leg"><span><i></i>Kopfball, kein Tor</span><span><i class="t"></i>Kopfball, Tor</span><span><i class="b"></i>Körpergröße</span></div>
      <div class="sc-feld" style="height:${H + 66}px">${linien}<div class="sc-spalten">${spalten}</div></div></section>`;
  }
  function scListe(m){
    const l = (m.grafik && m.grafik.liste) || scSp(m);
    return `${m.grafik.liste_titel ? `<h3 class="disp sc-lt">${esc(m.grafik.liste_titel)}</h3>` : ""}<section class="sc-li">${l.map(x => `<button class="sc-z" data-profilname="${esc(x.k + "|" + nachN(x.n))}">${scFoto(x, "sc-p")}
      <span class="sc-zn"><b>${esc(x.n)}</b><small>${esc(kname(x.k))}${x.pos ? " · " + esc(x.pos) : ""}${x.cm ? " · " + x.cm + " cm" : ""}</small></span>
      <span class="sc-zr"><span class="sc-zb">${scBaelle(x, "k")}</span><small class="${x.tore ? "t" : ""}">${scZahl(x.kopf, "Kopfball", "Kopfbälle")} · ${scZahl(x.tore, "Tor", "Tore")}</small></span></button>`).join("")}</section>`;
  }
  function scArtikel(m){
    const t = m.text || [];
    return `<div style="display:grid;gap:12px">${scHero(m, true)}<div class="tags">${(m.tags || []).map(tag).join("")}</div>
      <h1 class="disp" style="font-size:30px">${esc(m.grafik.titel || m.headline)}</h1><div class="dat">${esc(lang(m.zeit))}</div>
      ${t[0] ? `<p class="sc-lead">${esc(t[0])}</p>` : ""}</div>${scMesslatte(m)}${scListe(m)}
      ${t.length > 1 ? `<p class="sc-hw">${esc(t[t.length - 1])}</p>` : ""}`;
  }
