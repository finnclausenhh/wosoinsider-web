  // ---------------- TESTKOPIE: Gamification-Konzept (04.11.2026), nur in ticker-test/
  // Einsehbar, Prognose-Bilanz, Tippspiel "Spielt sie?" (Vorschau, Tipps nur auf dem Gerät), Gefragt diese Woche.
  const AUGE = '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>';
  const POKAL = '<path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0V4z"/><path d="M17 5h3v2a3 3 0 0 1-3 3M7 5H4v2a3 3 0 0 0 3 3"/>';
  const einsTag = nur => nur ? `<span class="eins" title="Aufstellung vor dem Kickbase-Schluss einsehbar" role="img" aria-label="Aufstellung einsehbar">${svg(AUGE)}</span>` : `<span class="eins">${svg(AUGE)}EINSEHBAR</span>`;
  const BILANZ_AB = 14, STUFEN_AB = 42, SCHLUSS_MIN = 90;
  let G_LADEN = null, TQ = null, KZ = null, SS = null;
  let TIPPS = {}; try { TIPPS = JSON.parse(localStorage.getItem("woso-tipps") || "{}") || {}; } catch (e) {}
  const tippsSpeichern = () => { try { localStorage.setItem("woso-tipps", JSON.stringify(TIPPS)); } catch (e) {} };
  // Tipps in Supabase (supabase/tippspiel.sql, 04.11.2026): gleiche anonyme Sitzung wie die Kommentare.
  // Fehlt die Datenbank-Funktion oder das Netz, bleibt alles wie bisher auf dem Gerät.
  const TS = { sb: null, ok: null, stand: {}, geladen: {} };
  function tsClient(){
    if (TS.sb || TS.ok === false) return TS.sb;
    const c = window.WI_KOMMENTARE || {};
    if (!(c.url && c.key && window.supabase && window.supabase.createClient)) { TS.ok = false; return null; }
    TS.sb = window.supabase.createClient(c.url, c.key, { auth: { persistSession: true, autoRefreshToken: true } });
    return TS.sb;
  }
  const tsSitzung = (anlegen) => { const sb = tsClient(); if (!sb) return Promise.reject(new Error("aus"));
    return sb.auth.getSession().then(r => r.data && r.data.session ? r.data.session : anlegen ? sb.auth.signInAnonymously().then(x => { if (x.error) throw x.error; return x.data.session; }) : null); };
  const tsNeu = () => { if (VIEW === "spielplan" && GAME && document.querySelector(".det")) { spiel(GAME, true); return; } if (VIEW !== "tipp" && ARTIKEL && document.querySelector(".tsd-art")) { const y = window.scrollY; article(ARTIKEL); window.scrollTo(0, y); return; } if (VIEW === "tipp") { const y = window.scrollY; tippschein(); window.scrollTo(0, y); } };
  function tsLaden(md){
    if (TS.geladen[md]) return; TS.geladen[md] = true;
    tsSitzung(false).then(se => {
      const sb = TS.sb;
      return Promise.all([se ? sb.rpc("meine_tipps", { p_md: Number(md) }) : Promise.resolve({ data: null }), sb.rpc("tipp_stand", { p_md: Number(md) })]);
    }).then(([m, st]) => {
      if (st && st.error) { TS.ok = false; return; }
      TS.ok = true; TS.stand[md] = (st && st.data) || {};
      if (m && m.data) { TIPPS[md] = Object.assign({}, TIPPS[md] || {}, m.data); tippsSpeichern(); }
      tsNeu();
    }).catch(() => { TS.ok = TS.ok || false; });
  }
  function tsSetzen(md, qid, oid){
    tsSitzung(true).then(() => TS.sb.rpc("tipp_setzen", { p_md: Number(md), p_frage: qid, p_antwort: oid || null }))
      .then(r => { if (r.error) throw r.error; TS.ok = true; TS.stand[md] = r.data || {}; tsNeu(); })
      .catch(e => { if (/Tippschluss/.test(String(e && e.message))) { alert("Der Tippschluss ist vorbei."); } });
  }

  // Daten für die Bausteine einmal nachladen, danach die aktuelle Ansicht neu zeichnen
  function gLaden(){
    if (G_LADEN) return G_LADEN;
    G_LADEN = Promise.all([
      SP ? Promise.resolve(SP) : json("spielplan.json").then(d => { SP = d; if (MD == null) MD = d.aktuell; }).catch(() => {}),
      ladeSPN().catch(() => {}),
      json("tracking/trefferquote.json").then(d => { TQ = d; }).catch(() => { TQ = {}; }),
      json("klickzahlen.json").then(d => { KZ = d; }).catch(() => { KZ = {}; }),
      json("spielt_sie.json").then(d => { SS = d; }).catch(() => { SS = null; }),
      json("tipp_loesung.json").then(d => { TL = d; }).catch(() => { TL = null; })
    ]).then(() => {
      if (ARTIKEL && !BACK && !GAME && VIEW === "meldungen" && SS) { const y = window.scrollY; article(ARTIKEL); window.scrollTo(0, y); return; }
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
    // Fragen kommen fest aus spielt_sie.json (tools/spielt_sie.py in fbl-daten, Finn 04.11.2026), nicht mehr aus der Prognose im Browser
    const r = SS; if (!r || !(r.fragen || []).length || !SP || !SPN || r.md !== SP.aktuell) return null;
    const t = (SP.spieltage || []).find(x => x.nr === r.md); if (!t) return null;
    const fragen = r.fragen.map(q => { const p = t.partien.find(x => x.id === q.partie); if (!p) return null;
      const s = q.sid ? spById(q.sid) : null, u = q.umfrage ? (UM || []).find(x => x.id === q.umfrage) : null;
      if ((q.umfrage && !u) || (q.sid && !s)) return null;
      return Object.assign({}, q, {p, s, umfrage: u, ein: einsehbar(p)}); }).filter(Boolean);
    return {md: r.md, schluss: dt(r.schluss), erst: r.erst, fragen};
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
    return `<button class="tipz" data-tipp="1">
      <span class="tipz-i">${svg(POKAL)}</span>
      <span class="tipz-t"><span class="kap">TIPPSPIEL ${r.md}. SPIELTAG</span><b>Spielt sie?</b><small>${r.fragen.length} Fragen · ${zu ? "Tippen beendet" : "bis " + wtUhr(r.schluss)}</small></span>
      <span class="tipz-b">${zu ? "Ansehen" : n === r.fragen.length ? "Ändern" : "Tippen"}</span></button>`;
  }

  // Tippkarte im Duell-Stil (Finn 04.11.2026, Variante B für alle Fragetypen)
  // Ja/Nein: gleiches Foto, Nein abgedunkelt, ODER in der Mitte. Zwei Spielerinnen: Duell mit VS, übrige Antworten als Knöpfe darunter.
  // Sonst Karten nebeneinander: Foto, Vereinslogo, große Zahl oder Symbol. Infos nur bei zwei Spalten, höchstens zwei Zeilen.
  const TSI = {
    leute: '<circle cx="9" cy="8" r="3"/><circle cx="16.5" cy="9" r="2.5"/><path d="M3 19c0-3 3-5 6-5s6 2 6 5"/><path d="M15.5 14c3 0 5.5 1.5 5.5 4.5"/>',
    start: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 12h18"/><circle cx="12" cy="12" r="3"/>',
    bank: '<path d="M4 15h16"/><path d="M6 15v4M18 15v4"/><path d="M6 15V9a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v6"/>',
    raus: '<circle cx="12" cy="12" r="9"/><path d="m8.5 8.5 7 7M15.5 8.5l-7 7"/>'
  };
  const tsSym = n => { const s = normS(n); return /startelf|beginnt/.test(s) ? "start" : /bank|kader/.test(s) && !/nicht/.test(s) ? "bank" : /nicht|fehlt|keine/.test(s) ? "raus" : "leute"; };
  const tsSrc = n => { const f = FOTOS[n] || {}; return f.portrait || f.datei || ""; };
  let TL = null, TAW = null;   // tipp_loesung.json: Auflösung aller Fragen (spielt_sie.py), mehrere richtige mit Komma
  const tsOk = (erg, id) => !!erg && String(erg).split(",").includes(id);
  const TS_NEU = ["mvp", "weste", "flaute", "serie"];
  const tsErg = q => { const l = TL && TL.md === (SS && SS.md) && TL.loesung ? TL.loesung[q.id] : null;
    if (l != null) return l; return TS_NEU.includes(q.typ) ? null : tippErgebnis(q); };
  function tsBild(src, k, kurz, grau){
    const g = WMG[k], wmi = g ? `<img class="wm" src="logos/wm/${esc(k)}.png" alt="" style="width:${g[0]}%;height:${g[1]}%" onerror="this.remove()">` : "";
    if (src) return `<span class="tsd-b fg${grau ? " g" : ""}">${wmi}<img class="f" src="${esc(src)}" alt="" loading="lazy" onerror="this.remove()"></span>`;
    return `<span class="tsd-b tsd-ph${grau ? " g" : ""}" style="background:${KFARBE[k] || "var(--soft)"}"><b>${esc(kurz)}</b></span>`;
  }
  function tsOpts(q){
    return q.optionen.map(o => {
      if (o.sid) { const s = spById(o.sid); return {id: o.id, n: o.n, name: o.n, info: o.info || "", src: s ? tsSrc(s.n) : "", sp: true, k: o.k || (s && s.k), logo: null}; }
      const u = q.umfrage ? (q.umfrage.optionen || []).find(x => x.id === o.id) : null;
      const sp = u && u.nachname && !u.logo && u.bild !== false;
      return {id: o.id, n: o.n, name: (u && u.nachname) || o.n, info: o.info || (u && u.info) || "", src: sp ? tsSrc(u.n) : "", sp, k: q.k, logo: u && u.logo};
    });
  }
  function tsKarte(q, r, zu, mein, srv, imArtikel){
    const erg = tsErg(q), t = mein[q.id];
    const st = srv ? (t || zu ? srv[q.id] || {} : null) : q.umfrage && UST[q.umfrage.id] ? UST[q.umfrage.id].stimmen || {} : null, ges = st ? Object.values(st).reduce((a, b) => a + (Number(b) || 0), 0) : 0;
    const pz = id => ges ? Math.round((Number(st[id]) || 0) / ges * 100) : 0;
    const os = tsOpts(q), jn = q.s && os.length === 2 && os[0].id === "ja" && os[1].id === "nein";
    const zust = o => { const on = t === o.id, ok = tsOk(erg, o.id); return {on, cls: `${on ? " on" : ""}${ok ? " ok" : ""}`, attr: `data-tv="${esc(r.md)}|${esc(q.id)}|${esc(o.id)}" ${zu ? "disabled" : ""} aria-pressed="${on}"`}; };
    const haken = on => on ? `<span class="tsd-hk" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="m5 12 5 5 9-10"/></svg></span>` : "";
    const fz = o => st && ges ? `<span class="tsd-fz"><span class="fb"><i style="width:${pz(o.id)}%"></i></span><b>${pz(o.id)} %</b></span>` : "";
    const karte = (o, oben, name, info) => { const z = zust(o);
      return `<button class="tsd-k${z.cls}" ${z.attr}>${oben}${haken(z.on)}<span class="tsd-t">${name ? `<b>${esc(name)}</b>` : ""}${info ? `<small>${esc(info)}</small>` : ""}${fz(o)}</span></button>`; };
    const feld = inner => `<span class="tsd-fd">${inner}</span>`;
    const ohneFoto = o => o.logo ? feld(logo(o.logo, 44)) : /^[0-9]/.test(o.n) ? feld(`<span class="tsd-z">${esc(o.n)}</span>`) : feld(`<svg class="tsd-i" viewBox="0 0 24 24">${TSI[tsSym(o.n)]}</svg>`);
    const kurzSp = s => s ? s.n.split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase() : "";
    let felder = "", knoepfe = "", kopf = "";
    if (jn) {
      const src = tsSrc(q.s.n), nn = nachN(q.s.n);
      if (q.typ === "serie") { const L = (q.s.spiele || []).filter(e => e.md < r.md), mx = Math.max(1, ...L.map(e => (e.tore || []).length));
        kopf = `<div class="tsd-kopf">${tsBild(src, q.k, kurzSp(q.s))}<span><b>${esc(nn.toUpperCase())}</b><small>Tore je Spieltag</small><span class="tsd-bars" aria-label="Tore je Spieltag">${L.map(e => { const n = (e.tore || []).length; return `<span>${n ? `<i style="height:${Math.round(n / mx * 26) + 4}px"></i>` : `<i class="z"></i>`}${e.md}</span>`; }).join("")}</span></span></div>`; }
      felder = `<div class="tsd-g" style="--n:2">${karte(os[0], tsBild(src, q.k, kurzSp(q.s)), "JA", os[0].info || `${nn} beginnt`)}${karte(os[1], tsBild(src, q.k, kurzSp(q.s), true), "NEIN", os[1].info || "Bank oder nicht dabei")}<span class="tsd-vs w" aria-hidden="true">ODER</span></div>`;
    } else {
      const fo = os.filter(o => o.sp), duell = fo.length === 2 && os.length >= 3, vier = fo.length === 4,
        haupt0 = duell || vier ? fo : fo.length >= 2 && q.optionen.some(o => o.sid) ? fo : os, rest = os.filter(o => !haupt0.includes(o));
      if (q.s) kopf = `<div class="tsd-kopf">${tsBild(tsSrc(q.s.n), q.k, kurzSp(q.s))}<span><b>${esc(nachN(q.s.n).toUpperCase())}</b><small>${esc(q.s.n)}</small></span></div>`;
      const haupt = haupt0, n = haupt.length <= 3 ? haupt.length : 2, mitInfo = n === 2 || haupt.every(o => String(o.info || "").length <= 16);
      felder = `<div class="tsd-g" style="--n:${n}">${haupt.map(o => karte(o, o.sp ? tsBild(o.src, o.k || q.k, o.name.slice(0, 2).toUpperCase()) : ohneFoto(o), String(o.name).toUpperCase(), mitInfo ? o.info : "")).join("")}${vier ? `<span class="tsd-vs c" aria-hidden="true">VS</span>` : fo.length === 2 && haupt.length === 2 ? `<span class="tsd-vs" aria-hidden="true">VS</span>` : ""}</div>`;
      if (rest.length) knoepfe = `<div class="ts-os" style="--n:${rest.length}">${rest.map(o => { const z = zust(o); return `<button class="ts-o${z.cls}" ${z.attr}>${esc(o.n)}${st && ges ? ` · ${pz(o.id)} %` : ""}</button>`; }).join("")}</div>`;
    }
    const fans = erg ? `<div class="ts-f ${t ? (tsOk(erg, t) ? "r" : "f") : ""}">${t ? (tsOk(erg, t) ? "Richtig · +10" : "Leider daneben") : "Nicht getippt"}</div>`
      : st && ges ? `<div class="tsd-fans"><span>${t ? `Dein Tipp: <b>${esc((os.find(o => o.id === t) || {}).name || "")}</b>` : "Fans"}</span><span>${zahlDE(ges)} ${ges === 1 ? "Tipp" : "Tipps"}</span></div>`
      : st ? (ges && os.length === 2 ? `<div class="tsd-fans"><span><b>${pz(os[0].id)} %</b> ${esc(jn ? "Ja" : os[0].name)}</span><span>${zahlDE(ges)} ${ges === 1 ? "Tipp" : "Tipps"}</span><span>${esc(jn ? "Nein" : os[1].name)} <b>${pz(os[1].id)} %</b></span></div>`
        : `<div class="ts-f">${ges ? `Fans: ${os.map(o => `${esc(o.n)} ${pz(o.id)} %`).join(" · ")} · ${zahlDE(ges)} ${ges === 1 ? "Tipp" : "Tipps"}` : "Noch keine Tipps"}</div>`) : "";
    const html = `<section class="ts-k tsd">
        ${imArtikel ? "" : `<div class="ts-kz"><span class="kap">${esc(q.art)} · ${q.multi ? `${r.md}. SPIELTAG` : `${esc(q.p.heim_k)}-${esc(q.p.gast_k)} · ${esc(WT[dt(q.p.anstoss).getDay()])}`}</span>${(q.multi ? q.einsehbar : q.ein) ? einsTag() : ""}</div>`}
        <h3 class="tsd-q">${esc(q.frage)}</h3>
        ${kopf}${felder}${knoepfe}${fans}
        <div class="ts-i"><span class="l">WARUM</span><span>${esc(q.warum)}</span></div>
        ${q.prognose ? `<div class="ts-i"><span class="l p">PROGNOSE</span><span>${esc(q.prognose)}</span></div>` : ""}
      </section>`;
    return {html, erg, t};
  }
  // Frage zur Meldung: Umfrage mit dieser Meldung, sonst Startelf-Frage an der neuesten Meldung zur Spielerin (höchstens 21 Tage alt)
  function tsFrageZu(m){
    const r = tippRunde(); if (!r || !m) return null;
    const neueste = n => N.filter(x => x.spielerin && normS(x.spielerin) === normS(n) && x.typ !== "punkt").sort((a, b) => (dt(b.zeit) || 0) - (dt(a.zeit) || 0))[0];
    const q = r.fragen.find(x => x.umfrage ? x.umfrage.meldung === m.id
      : x.s && m.spielerin && normS(x.s.n) === normS(m.spielerin) && KURZ[m.verein] === x.k && (neueste(x.s.n) || {}).id === m.id && (Date.now() - (dt(m.zeit) || 0)) < 21 * 864e5);
    return q ? {r, q} : null;
  }
  function tsArtikel(m){
    gLaden(); const z = tsFrageZu(m); if (!z) return "";
    const {r, q} = z; tsLaden(r.md);
    const zu = new Date() >= r.schluss, k = tsKarte(q, r, zu, TIPPS[r.md] || {}, TS.ok && TS.stand[r.md], true);
    return `<div class="tsd-art"><div class="tsd-ak"><span class="kap">SPIELT SIE?</span><span class="tsd-bis">${svg(P.uhr)}${zu ? "Tippen beendet" : "Tippen bis " + esc(wtUhr(r.schluss))}</span></div>${k.html}
      <button class="tsd-mehr" data-tipp="1">${r.fragen.length > 1 ? `${r.fragen.length - 1} weitere ${r.fragen.length === 2 ? "Frage" : "Fragen"} im Tippschein` : "Zum Tippschein"} ›</button></div>`;
  }

  // Umfragen im Duell-Stil (Finn 04.11.2026): Spielerinnen als Fotokarten, zwei Spielerinnen mit VS, übrige Antworten als Knöpfe.
  // Umfrage zu einer Spielerin ohne Fotos an den Antworten (z. B. Tore): Kopfzeile mit Foto, Antworten als Zahlkarten. Sonst bleibt die alte Liste.
  function umKarten(u, feed, v){
    const O = u.optionen || [], spO = o => o.nachname && !o.logo && o.bild !== false && tsSrc(o.n);
    const fo = O.filter(spO), spN = u.spielerin ? Object.keys(FOTOS).find(n => normS(nachN(n)) === normS(u.spielerin) && KURZ[(FOTOS[n] || {}).verein] === u.verein) : null, sp = spN ? {n: spN} : null;
    const zahl = o => o.von == null ? "" : o.bis == null ? o.von + "+" : o.von === o.bis ? String(o.von) : o.von + "–" + o.bis;
    const zahlen = !fo.length && O.length <= 3 && O.every(o => zahl(o));
    if (!fo.length && !zahlen) return "";
    const zu = o => { const mein = v.meine && v.meine.o === o.id, richtig = v.auf && v.auf.richtig === o.id;
      return {mein, cls: `${mein ? " on" : ""}${richtig ? " ok" : ""}`, attr: `data-uvote="${esc(u.id)}|${esc(o.id)}" ${v.zeigt ? "disabled" : ""}`}; };
    const pzT = o => v.zp ? `<span class="tsd-pz">${v.pz(o)} %</span>` : "";
    const haken = on => on ? `<span class="tsd-hk" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="m5 12 5 5 9-10"/></svg></span>` : "";
    const ks = o => !feed && o.kader ? `<span class="ks" aria-label="Kader der letzten 5 Spieltage">${[...String(o.kader)].map(c => `<i class="${"bse".includes(c) ? c : ""}"></i>`).join("")}</span>` : "";
    const karte = (o, oben, name, info) => { const z = zu(o);
      return `<button class="tsd-k${z.cls}" ${z.attr}>${oben}${haken(z.mein)}<span class="tsd-t">${name ? `<b>${esc(name)}</b>` : ""}${info ? `<small>${esc(info)}</small>` : ""}${ks(o)}${pzT(o)}</span></button>`; };
    const knopf = o => { const z = zu(o); return `<button class="ts-o${z.cls}" ${z.attr}>${esc(o.n)}${v.zp ? ` · ${v.pz(o)} %` : ""}</button>`; };
    if (zahlen) {
      const kopf = sp ? `<div class="tsd-kopf">${tsBild(tsSrc(sp.n), u.verein, nachN(sp.n).slice(0, 2).toUpperCase())}<span><b>${esc(nachN(sp.n).toUpperCase())}</b><small>${esc((FOTOS[sp.n] || {}).verein || sp.n)}</small></span></div>` : "";
      return `<div class="tsd-um${feed ? " feed" : ""}">${kopf}<div class="tsd-g" style="--n:${O.length}">${O.map(o => karte(o, `<span class="tsd-fd"><span class="tsd-z">${esc(zahl(o))}</span></span>`, "", o.n)).join("")}</div></div>`;
    }
    const duell = fo.length === 2, haupt = duell ? fo : O, rest = duell ? O.filter(o => !fo.includes(o)) : [];
    const n = haupt.length <= 3 ? haupt.length : 2, mitInfo = n <= 2;
    const oben = o => spO(o) ? tsBild(tsSrc(o.n), u.verein, (o.nachname || o.n).slice(0, 2).toUpperCase()) : `<span class="tsd-fd">${o.logo ? logo(o.logo, 44) : `<svg class="tsd-i" viewBox="0 0 24 24">${TSI[tsSym(o.n)]}</svg>`}</span>`;
    return `<div class="tsd-um${feed ? " feed" : ""}"><div class="tsd-g" style="--n:${n}">${haupt.map(o => karte(o, oben(o), (o.nachname || o.n).toUpperCase(), mitInfo ? o.info : "")).join("")}${duell ? `<span class="tsd-vs" aria-hidden="true">VS</span>` : ""}</div>
      ${rest.length ? `<div class="ts-os" style="--n:${rest.length}">${rest.map(knopf).join("")}</div>` : ""}</div>`;
  }

  // Sammel-News (Finn 04.11.2026): hat mindestens eine Frage keinen passenden Artikel, steht eine normal große Meldung im Feed, die zum Tippschein führt
  function tsRundeNews(){
    const r = tippRunde(); if (!r || !SS) return;
    const id = `tipp-runde-md${r.md}`; if (N.some(m => m.id === id)) return;
    const ohne = r.fragen.filter(q => !N.some(m => m.typ !== "tipprunde" && (tsFrageZu(m) || {}).q === q));
    if (!ohne.length) return;
    N.push({id, typ: "tipprunde", zeit: SS.erstellt, tags: ["SPIELT SIE?"], headline: `Spielt sie? ${r.fragen.length} Fragen zum ${r.md}. Spieltag`,
      kurz: `Spielt sie? ${r.fragen.length} Fragen zum ${r.md}. Spieltag`, spielerin: `Tippen bis ${wtUhr(r.schluss)}`, pos: "Spielansetzung", n_fragen: r.fragen.length});
  }
  const trBild = (m, g) => `<div class="bild fd-b" style="width:${g}px;height:${g}px;border-radius:${g > 70 ? 11 : 8}px" aria-hidden="true"><b>${m.n_fragen}</b><small>FRAGEN</small></div>`;

  function tippschein(){
    VIEW = "tipp"; ARTIKEL = null; GAME = null; BACK = null;
    gLaden();
    const r = tippRunde();
    if (!r) { $("#main").innerHTML = `<div class="det"><button class="back" data-tippzu="1">‹ Zurück</button><p class="leer">Tippspiel wird geladen …</p></div>`; return; }
    tsLaden(r.md);
    const zu = new Date() >= r.schluss, mein = TIPPS[r.md] || {}, srv = TS.ok && TS.stand[r.md];
    let punkte = 0, gewertet = 0;
    const karten = r.fragen.map(q => { const k = tsKarte(q, r, zu, mein, srv);
      if (k.erg && k.t) { gewertet++; if (tsOk(k.erg, k.t)) punkte += 10; }
      return k.html; }).join("");
    $("#main").innerHTML = `<div class="det ts"><button class="back" data-tippzu="1">‹ Zurück</button>
      <div class="ts-kopf"><span class="kap">TIPPSPIEL ${r.md}. SPIELTAG</span><h1>Spielt sie?</h1></div>
      <div class="ts-hin">${svg(P.uhr)}<span>${zu ? `Tippen beendet. ${gewertet ? `${punkte} Punkte aus ${gewertet} gewerteten Fragen.` : "Die Wertung folgt mit den Aufstellungen."}` : `Tippen bis <b>${esc(wtUhr(r.schluss))}</b>, bevor die ersten Aufstellungen kommen.`}</span></div>
      ${karten}
      <div class="ts-fuss"><span>Jede richtige Antwort: 10 Punkte · max. ${r.fragen.length * 10}</span>
      <span class="ts-vs">${TS.ok ? "Ohne Konto gespeichert. Ändern geht bis zum Tippschluss, gewertet wird dein letzter Tipp. Die Fan-Werte siehst du, sobald du selbst getippt hast." : "Deine Tipps bleiben vorerst nur auf diesem Gerät."}</span></div></div>`;
    window.scrollTo(0, 0);
  }

  // Fans gegen Daten (Finn 04.11.2026): Auswertung als normale Meldung, Grafik im Artikel
  function fdGrafik(g){
    const z = (g.zeilen || []).map(r => `<div class="fd-z"><span><b>${esc(r.frage)}</b><small>Richtig: ${esc(r.richtig)}${r.fans_n ? ` · Fans: ${esc(r.fans_n)} (${r.fans_p} %)` : " · Fans: kein klarer Tipp"}</small></span>
      <span class="c ${r.fans ? "ok" : "no"}">${r.fans ? "✓" : "✗"}</span><span class="c ${r.daten ? "ok" : "no"}">${r.daten ? "✓" : "✗"}</span></div>`).join("");
    return `<div class="fd"><div class="fd-sb"><span class="s"><b>${g.fans}</b><small>FANS</small></span><span class="tsd-vs" style="position:static;transform:none">VS</span><span class="s"><b>${g.daten}</b><small>DATEN</small></span></div>
      <div class="fd-z fd-k"><span>FRAGE</span><span class="c">FANS</span><span class="c">DATEN</span></div>${z}
      <p class="fd-h">Fans = Antwort mit den meisten Tipps, Daten = unsere Prognose. Bis zu ${g.tipps} ${g.tipps === 1 ? "Tipp" : "Tipps"} je Frage.</p></div>`;
  }
  const fdBild = (m, g) => `<div class="bild fd-b" style="width:${g}px;height:${g}px;border-radius:${g > 70 ? 11 : 8}px" aria-hidden="true"><b>${m.grafik.fans}:${m.grafik.daten}</b><small>FANS : DATEN</small></div>`;
  // Fan-Wert an der Prognose: Spielansicht, nur Einsatzfragen dieser Partie, ab 10 Tipps, immer mit Anzahl
  function tsFanBlock(p){
    gLaden(); const r = tippRunde(); if (!r) return "";
    const qs = r.fragen.filter(q => q.partie === p.id && (q.typ === "einsatz" || !q.typ)); if (!qs.length) return "";
    tsLaden(r.md); const srv = TS.ok && TS.stand[r.md]; if (!srv) return "";
    const rows = qs.map(q => { const st = srv[q.id] || {}, ges = Object.values(st).reduce((a, b) => a + (Number(b) || 0), 0); if (ges < 10) return "";
      const pz = id => Math.round((Number(st[id]) || 0) / ges * 100);
      const os = tsOpts(q).filter(o => o.sp || q.s), jn = q.s && q.optionen.length === 2 && q.optionen[0].id === "ja";
      const stufe = n => { const a = [p.heim_aufstellung, p.gast_aufstellung].find(a => a && a.typ === "prognose" && [...(a.startelf || []), ...(a.bank || [])].some(x => normS(x.n) === normS(n)));
        const x = a && [...(a.startelf || []), ...(a.bank || [])].find(x => normS(x.n) === normS(n)), S = x && STUFE[x.st];
        return S ? `<span class="fw-s">${stufeSym(x.st, 12)} ${esc(S[2])}</span>` : ""; };
      const zeile = (n, src, k, w) => `<div class="fw-r">${tsBild(src, k, n.slice(0, 2).toUpperCase())}<span class="tx"><b>${esc(n)}</b>${stufe(n)}<span class="fb"><i style="width:${w}%"></i></span><small>Fans: ${w} % erwarten sie in der Startelf</small></span></div>`;
      const inner = jn ? zeile(nachN(q.s.n), tsSrc(q.s.n), q.k, pz("ja")) : os.filter(o => o.sp).map(o => zeile(o.name, o.src, o.k || q.k, Math.min(100, pz(o.id) + (st.beide ? pz("beide") : 0)))).join("");
      return inner ? `<div class="fw-q"><span class="fw-f">${esc(q.frage)}</span>${inner}<span class="fw-n">${zahlDE(ges)} Tipps</span></div>` : ""; }).join("");
    return rows ? `<div class="kartebox fw">${kap("Spielt sie? Das tippen die Fans")}${rows}</div>` : "";
  }
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
      <div class="bil-k">${TQ.gesamt_24h && TQ.gesamt_24h.teams ? `<div><span>24 h vor Anpfiff</span><b style="color:#6E9BFF">${pz(TQ.gesamt_24h.elf_quote)}</b><small>im Schnitt ${esc(String(TQ.gesamt_24h.elf_treffer_schnitt).replace(".", ","))} von 11 richtig</small></div>` : `<div><span>24 h vor Anpfiff</span><b class="mu">kommt</b><small>ab dem nächsten Spieltag</small></div>`}
        <div><span>Letzte Prognose</span><b style="color:#6E9BFF">${pz(g.elf_quote)}</b><small>im Schnitt ${esc(String(g.elf_treffer_schnitt).replace(".", ","))} von 11 richtig</small></div></div>
      ${stufen || !oeff ? `<div class="bil-s">${!stufen ? `<div class="bil-test">Testansicht: je Status erst ab ${STUFEN_AB} Aufstellungen.</div>` : ""}<div class="kap">HÄLT DER STATUS, WAS ER VERSPRICHT?</div>${ST.map(([k, l, c]) => { const x = (g.je_stufe || {})[k]; if (!x || !x.n) return "";
        return `<div class="bil-z"><div><span><i style="background:${c}"></i>${l}</span><span><b>${pz(x.quote)}</b> <small>(${x.begonnen} von ${x.n})</small></span></div><div class="bil-b"><div style="width:${Math.round((x.quote || 0) * 100)}%;background:${c}"></div></div></div>`; }).join("")}</div>` : ""}
      <p class="bil-so">Wir vergleichen jede Prognose mit der offiziellen Startelf, einmal 24 Stunden vor Anpfiff und einmal die letzte Fassung. Späte Korrekturen schönen die Quote so nicht. Die Bilanz erscheint immer, auch wenn sie schlecht ist.</p>
    </section>`;
  }
