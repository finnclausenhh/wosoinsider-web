  // ---------------- TESTKOPIE: Gamification-Konzept (04.11.2026), nur in ticker-test/
  // Einsehbar, Prognose-Bilanz, Tippspiel "Spielt sie?" (Vorschau, Tipps nur auf dem Gerät), Gefragt diese Woche.
  const AUGE = '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>';
  const POKAL = '<path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0V4z"/><path d="M17 5h3v2a3 3 0 0 1-3 3M7 5H4v2a3 3 0 0 0 3 3"/>';
  const einsTag = nur => nur ? `<span class="eins" title="Aufstellung vor dem Kickbase-Schluss einsehbar" role="img" aria-label="Aufstellung einsehbar">${svg(AUGE)}</span>` : `<span class="eins">${svg(AUGE)}EINSEHBAR</span>`;
  const BILANZ_AB = 14, STUFEN_AB = 42, SCHLUSS_MIN = 90;
  let G_LADEN = null, TQ = null, KZ = null;
  let TIPPS = {}; try { TIPPS = JSON.parse(localStorage.getItem("woso-tipps") || "{}") || {}; } catch (e) {}
  const tippsSpeichern = () => { try { localStorage.setItem("woso-tipps", JSON.stringify(TIPPS)); } catch (e) {} };

  // Daten für die Bausteine einmal nachladen, danach die aktuelle Ansicht neu zeichnen
  function gLaden(){
    if (G_LADEN) return G_LADEN;
    G_LADEN = Promise.all([
      SP ? Promise.resolve(SP) : json("spielplan.json").then(d => { SP = d; if (MD == null) MD = d.aktuell; }).catch(() => {}),
      ladeSPN().catch(() => {}),
      json("tracking/trefferquote.json").then(d => { TQ = d; }).catch(() => { TQ = {}; }),
      json("klickzahlen.json").then(d => { KZ = d; }).catch(() => { KZ = {}; })
    ]).then(() => {
      if (BACK || ARTIKEL || GAME) return;
      const y = window.scrollY;
      if (VIEW === "meldungen" && document.querySelector("#main .liste")) list();
      else if (VIEW === "inside" && IN) inside();
      else if (VIEW === "tipp") tippschein();
      window.scrollTo(0, y);
    });
    return G_LADEN;
  }

  // Einsehbar: Spiele, die zum ersten Anpfiff ihres Spieltags beginnen. Kickbase schließt dann die Aufstellung,
  // nur ihre offizielle Aufstellung (ca. 60 Minuten vorher) ist vor dem Schluss bekannt.
  function ersteAnstoesse(){
    const s = new Set(); if (!SP) return s;
    (SP.spieltage || []).forEach(t => { const a = t.partien.filter(terminiert).map(p => p.anstoss).sort(); if (a.length) s.add(a[0]); });
    return s;
  }
  const einsehbar = p => !!(SP && p && terminiert(p) && ersteAnstoesse().has(p.anstoss) && (SP.spieltage || []).some(t => t.partien.some(x => x.id === p.id)));
  const einsehbarZeit = (z, wb) => (!wb || wb === "Liga") && ersteAnstoesse().has(String(z || "").slice(0, 16));

  // ---------------- Tippspiel "Spielt sie?"
  const wtUhr = d => `${WT[d.getDay()]} ${uhr(d)} Uhr`;
  const imWb = wb => wb === "Liga" ? "in der Liga" : wb === "Champions League" ? "in der Champions League" : "im " + wb;
  const sTore = s => (s.spiele || []).reduce((a, e) => a + ((e.tore || []).length), 0);
  const sVorl = s => (s.spiele || []).reduce((a, e) => a + (e.vorl || 0), 0);

  function tippTag(){ return SP && (SP.spieltage || []).find(t => t.nr === SP.aktuell) || null; }
  function tippRunde(){
    const t = tippTag(); if (!t || !SPN) return null;
    const ps = t.partien.filter(terminiert); if (!ps.length) return null;
    const erst = ps.map(p => p.anstoss).sort()[0], schluss = new Date(dt(erst).getTime() - SCHLUSS_MIN * 60000);
    const proV = {}, frei = k => (proV[k] || 0) < 2, nimm = k => { proV[k] = (proV[k] || 0) + 1; };
    const fragen = [], belegt = new Set();
    // 1. Bestehende Startelf-Umfragen des Spieltags (mit Infos und Einschätzung), höchstens 2
    (UM || []).filter(u => (u.art || "startelf") === "startelf" && u.partie && t.partien.some(p => p.id === u.partie)).slice(0, 2).forEach(u => {
      const p = t.partien.find(x => x.id === u.partie), e = u.einschaetzung, eo = e && (u.optionen || []).find(o => o.id === e.option);
      (u.optionen || []).forEach(o => o.nachname && belegt.add(normS(o.nachname)));
      nimm(u.verein);
      fragen.push({id: "u-" + u.id, art: u.position === "TW" ? "TOR" : "WER STARTET", p, ein: einsehbar(p), frage: u.frage, umfrage: u,
        warum: (u.position === "TW" ? "Torhüterinnen punkten bei Kickbase stark. " : "") + (u.optionen || []).filter(o => o.info).map(o => `${o.nachname || o.n}: ${o.info}`).join(" · "),
        prognose: eo ? `${STUFE[e.stufe] ? STUFE[e.stufe][2] : ""}: ${eo.nachname || eo.n}. ${e.text}` : "",
        optionen: (u.optionen || []).map(o => ({id: o.id, n: o.nachname || (o.id === "andere" ? "Andere" : o.n)}))});
    });
    // 2. Startelf-Fragen aus der Prognose: nur Kickbase-Gewicht, nur echte Unsicherheit, nur mit Anlass
    const kand = [];
    t.partien.forEach(p => {
      [[p.heim_k, p.heim_aufstellung], [p.gast_k, p.gast_aufstellung]].forEach(([k, a]) => {
        if (!a || a.typ !== "prognose") return;
        (a.startelf || []).concat(a.bank || []).forEach(x => {
          if (!["erwartet", "unsicher"].includes(x.st) || belegt.has(normS(x.n))) return;
          const s = findeSP(k, x.n); if (!s) return;
          const f = FOTOS[s.n] || {}; if (!f.portrait && !f.datei) return;
          const w = s.prognose && s.prognose.wert != null ? s.prognose.wert : Number((String(x.warum || "").match(/Einsatzwert (\d+)/) || [])[1] || 0);
          if (w >= 95 || w < 30) return;
          const tore = sTore(s), vorl = sVorl(s), tw = x.p === "TW", gewicht = tore * 2 + vorl + (tw ? 6 : 0);
          if (gewicht < 3) return;
          const ll = (s.spiele || []).slice(-1)[0], lp = (s.pokal || []).slice(-1)[0];
          const letzt = [ll && {d: ll.datum, wb: "Liga", g: ll.gegner, art: ll.art}, lp && {d: lp.datum, wb: lp.wb, g: lp.gegner, art: lp.art}].filter(Boolean).sort((a, b) => dt(b.d) - dt(a.d))[0];
          const einsch = (String(x.warum || "").split("Einschätzung WOSOINSIDER:")[1] || "").trim();
          const l3 = (s.spiele || []).slice(-3), s3 = l3.filter(e => e.art === "S").length;
          let anlass = "";
          if (letzt && letzt.art === "B") anlass = `Zuletzt ${imWb(letzt.wb)} gegen ${letzt.g} nur auf der Bank.`;
          else if (letzt && letzt.art === "E") anlass = `Zuletzt ${imWb(letzt.wb)} gegen ${letzt.g} nur eingewechselt.`;
          else if (einsch) anlass = einsch.replace(/\.?$/, ".");
          else if (l3.length === 3 && s3 < 3) anlass = `In den letzten 3 Ligaspielen ${s3}-mal in der Startelf.`;
          if (!anlass) return;
          const stz = (String(x.warum || "").match(/(\d)\/5 Startelf/) || [])[1];
          kand.push({id: "s-" + s.id, art: "STARTELF", p, k, s, ein: einsehbar(p), gewicht,
            frage: `Steht ${nachN(s.n)} in der Startelf?`,
            warum: `${anlass} ${tw ? "Torhüterinnen punkten bei Kickbase stark." : `Diese Saison ${tore} ${tore === 1 ? "Tor" : "Tore"}, ${vorl} ${vorl === 1 ? "Vorlage" : "Vorlagen"}.`}`,
            prognose: `${STUFE[x.st][2]}. ${stz ? stz + " von 5 zuletzt in der Startelf, " : ""}Einsatzwert ${w} %.`,
            optionen: [{id: "ja", n: "Ja"}, {id: "nein", n: "Nein"}]});
        });
      });
    });
    kand.sort((a, b) => b.gewicht - a.gewicht);
    // mindestens 2 Fragen zu nicht einsehbaren Spielen, höchstens 2 je Verein, insgesamt 5
    const pick = q => { if (fragen.length >= 5 || !frei(q.k) || fragen.some(f => f.id === q.id)) return; nimm(q.k); fragen.push(q); };
    kand.filter(q => !q.ein).slice(0, 2).forEach(pick);
    kand.forEach(pick);
    fragen.sort((a, b) => dt(a.p.anstoss) - dt(b.p.anstoss));
    return {md: t.nr, schluss, erst, fragen};
  }

  // Auflösung: Startelf aus der offiziellen Aufstellung, Umfragen über die bestehende Auflösung
  function tippErgebnis(q){
    if (q.umfrage) { const a = umfrageAufloesung(q.umfrage); return a && !a.offen ? a.richtig : null; }
    const a = q.p && (q.p.heim_k === q.k ? q.p.heim_aufstellung : q.p.gast_aufstellung);
    if (!a || a.typ !== "offiziell") return null;
    return (a.startelf || []).some(x => normS(x.n) === normS(nachN(q.s.n)) || normS(x.voll || "") === normS(q.s.n)) ? "ja" : "nein";
  }

  function tippZeile(){
    gLaden();
    const r = tippRunde(); if (!r || !r.fragen.length) return "";
    const zu = new Date() >= r.schluss, mein = TIPPS[r.md] || {}, n = r.fragen.filter(q => mein[q.id]).length;
    return `<button class="tz" data-tipp="1">
      <span class="tz-i">${svg(POKAL)}</span>
      <span class="tz-t"><span class="kap">TIPPSPIEL ${r.md}. SPIELTAG</span><b>Spielt sie?</b><small>${r.fragen.length} Fragen · ${zu ? "Tippen beendet" : "bis " + wtUhr(r.schluss)}</small></span>
      <span class="tz-b">${zu ? "Ansehen" : n === r.fragen.length ? "Ändern" : "Tippen"}</span></button>`;
  }

  function tippschein(){
    VIEW = "tipp"; ARTIKEL = null; GAME = null; BACK = null;
    gLaden();
    const r = tippRunde();
    if (!r) { $("#main").innerHTML = `<div class="det"><button class="back" data-tippzu="1">‹ Zurück</button><p class="leer">Tippspiel wird geladen …</p></div>`; return; }
    const zu = new Date() >= r.schluss, mein = TIPPS[r.md] || {};
    let punkte = 0, gewertet = 0;
    const karten = r.fragen.map(q => {
      const erg = tippErgebnis(q), t = mein[q.id];
      if (erg && t) { gewertet++; if (erg === t) punkte += 10; }
      const st = q.umfrage && UST[q.umfrage.id] ? UST[q.umfrage.id].stimmen || {} : null, ges = st ? Object.values(st).reduce((a, b) => a + (Number(b) || 0), 0) : 0;
      const opts = q.optionen.map(o => { const on = t === o.id, ok = erg && erg === o.id;
        return `<button class="ts-o${on ? " on" : ""}${ok ? " ok" : ""}" data-tv="${esc(r.md)}|${esc(q.id)}|${esc(o.id)}" ${zu ? "disabled" : ""} aria-pressed="${on}">${esc(o.n)}</button>`; }).join("");
      const foto = q.s ? pfFoto(q.s, 44, 44, 22) : "";
      return `<section class="ts-k">
        <div class="ts-h">${foto}<div class="ts-ht"><div class="ts-kz"><span class="kap">${esc(q.art)} · ${esc(q.p.heim_k)}-${esc(q.p.gast_k)} · ${esc(WT[dt(q.p.anstoss).getDay()])}</span>${q.ein ? einsTag() : ""}</div><h3>${esc(q.frage)}</h3></div></div>
        <div class="ts-i"><span class="l">WARUM</span><span>${esc(q.warum)}</span></div>
        ${q.prognose ? `<div class="ts-i"><span class="l p">PROGNOSE</span><span>${esc(q.prognose)}</span></div>` : ""}
        <div class="ts-os" style="--n:${q.optionen.length > 3 ? 2 : q.optionen.length}">${opts}</div>
        ${erg ? `<div class="ts-f ${t ? (erg === t ? "r" : "f") : ""}">${t ? (erg === t ? "Richtig · +10" : "Leider daneben") : "Nicht getippt"}</div>` : st ? `<div class="ts-f">${ges ? `Fans: ${q.optionen.map(o => `${esc(o.n)} ${Math.round((Number(st[o.id]) || 0) / ges * 100)} %`).join(" · ")} · ${zahlDE(ges)} ${ges === 1 ? "Tipp" : "Tipps"}` : "Noch keine Tipps"}</div>` : ""}
      </section>`;
    }).join("");
    $("#main").innerHTML = `<div class="det ts"><button class="back" data-tippzu="1">‹ Zurück</button>
      <div class="ts-kopf"><span class="kap">TIPPSPIEL ${r.md}. SPIELTAG</span><h1>Spielt sie?</h1></div>
      <div class="ts-hin">${svg(P.uhr)}<span>${zu ? `Tippen beendet. ${gewertet ? `${punkte} Punkte aus ${gewertet} gewerteten Fragen.` : "Die Wertung folgt mit den Aufstellungen."}` : `Tippen bis <b>${esc(wtUhr(r.schluss))}</b>, bevor die ersten Aufstellungen kommen.`}</span></div>
      ${karten}
      <div class="ts-fuss"><span>Jede richtige Antwort: 10 Punkte · max. ${r.fragen.length * 10}</span>
      <span class="ts-vs">Deine Tipps bleiben vorerst nur auf diesem Gerät. Rangliste und Fan-Werte kommen, sobald die Tipps gespeichert werden.</span></div></div>`;
    window.scrollTo(0, 0);
  }

  // ---------------- Gefragt diese Woche: 2 Spielerinnen aus den Klickzahlen, täglich wechselnd
  function gefragtZeile(){
    gLaden();
    const l = ((KZ && KZ.spielerinnen) || []).filter(x => x.oeffnungen_7t > 0 && (FOTOS[x.n] || {}).datei).slice(0, 6);
    if (l.length < 2) return "";
    const tag = Math.floor(Date.now() / 864e5), o = (tag * 2) % l.length, z = [l[o % l.length], l[(o + 1) % l.length]];
    return `<section class="gfw"><div class="kap">${svg('<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>')}GEFRAGT DIESE WOCHE</div><div class="gfw-g">${z.map(x => {
      const s = SPN && (SPN.spielerinnen || []).find(y => y.n === x.n && y.k === x.k);
      return `<button class="gfw-c" data-profilname="${esc(x.k)}|${esc(x.n)}">${s ? pfFoto(s, 34, 34, 17) : ""}<span><b>${esc(nachN(x.n))}</b><small>${esc(kname(x.k))}</small></span></button>`; }).join("")}</div></section>`;
  }

  // ---------------- Prognose-Bilanz (Inside)
  function bilanzSektion(){
    gLaden();
    const g = TQ && TQ.gesamt; if (!g || !g.teams) return "";
    const n = g.teams, oeff = n >= BILANZ_AB, stufen = n >= STUFEN_AB;
    const pz = v => v == null ? "–" : Math.round(v * 100) + " %";
    const ST = [["sicher", "Sicher", "#6E9BFF"], ["erwartet", "Erwartet", "#22C55E"], ["unsicher", "Unsicher", "#F59E0B"], ["unwahrscheinlich", "Unwahrscheinlich", "#F87171"], ["ausgeschlossen", "Ausgeschlossen", "#8A95A8"]];
    return `<section class="sek bil">
      ${!oeff ? `<div class="bil-test">Testansicht: öffentlich erst ab ${BILANZ_AB} geprüften Aufstellungen, aktuell ${n}.</div>` : ""}
      <div class="kap" style="color:#14B8A6">PROGNOSE-BILANZ</div><h2>Wie gut sind unsere Aufstellungen?</h2>
      <p class="mu">${n} Aufstellungen geprüft · Stand ${esc(tagDatum(TQ.stand))} · jeden Dienstag neu</p>
      <div class="bil-k"><div><span>24 h vor Anpfiff</span><b class="mu">kommt</b><small>wird ab jetzt mitgeschrieben</small></div>
        <div><span>Letzte Prognose</span><b style="color:#6E9BFF">${pz(g.elf_quote)}</b><small>im Schnitt ${esc(String(g.elf_treffer_schnitt).replace(".", ","))} von 11 richtig</small></div></div>
      ${stufen || !oeff ? `<div class="bil-s">${!stufen ? `<div class="bil-test">Testansicht: je Status erst ab ${STUFEN_AB} Aufstellungen.</div>` : ""}<div class="kap">HÄLT DER STATUS, WAS ER VERSPRICHT?</div>${ST.map(([k, l, c]) => { const x = (g.je_stufe || {})[k]; if (!x || !x.n) return "";
        return `<div class="bil-z"><div><span><i style="background:${c}"></i>${l}</span><span><b>${pz(x.quote)}</b> <small>(${x.begonnen} von ${x.n})</small></span></div><div class="bil-b"><div style="width:${Math.round((x.quote || 0) * 100)}%;background:${c}"></div></div></div>`; }).join("")}</div>` : ""}
      <p class="bil-so">Wir vergleichen jede Prognose mit der offiziellen Startelf, einmal 24 Stunden vor Anpfiff und einmal die letzte Fassung. Späte Korrekturen schönen die Quote so nicht. Die Bilanz erscheint immer, auch wenn sie schlecht ist.</p>
    </section>`;
  }
