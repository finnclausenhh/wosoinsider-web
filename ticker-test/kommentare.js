/* WOSOINSIDER Kommentare (Web-Ticker)
 * Braucht vorher: supabase.js (lokal gehostet) und kommentare-config.js (URL + Publishable Key).
 * Einbau: Der Ticker legt im Artikel <div id="kom" data-beitrag="ID"></div> an und ruft WIKOM.mount(ID).
 * Lesen ohne Anmeldung. Erst beim ersten Schreiben, Liken oder Melden entsteht eine anonyme Sitzung.
 * Alle Regeln (Tempo, Wortfilter, Sperren, Meldeschwelle) prüft die Datenbank, nicht diese Datei.
 */
(function () {
  "use strict";
  var CFG = window.WI_KOMMENTARE || {};
  var AKTIV = !!(CFG.url && CFG.key && window.supabase && window.supabase.createClient);
  var sb = AKTIV ? window.supabase.createClient(CFG.url, CFG.key, {
    auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: false, storageKey: "woso-konto" }
  }) : null;

  var MAX = 1000, SEITE = 20;
  var S = { beitrag: null, liste: [], likes: {}, ich: null, sort: "neu", zeige: SEITE, antwort: null,
            melden: null, fehler: "", fehlerAn: null, sendet: false, offenRegeln: false, laden: false, geladen: false };
  var ENTWURF = {};   // Entwürfe je Meldung und Antwort, überleben das Neuzeichnen des Artikels
  var TIMER = null;

  var FEHLER = {
    WI_TEMPO: "Kurz durchatmen: Zwischen zwei Kommentaren braucht es ein paar Sekunden.",
    WI_LIMIT: "Für den Moment hast du genug kommentiert. Später geht es weiter.",
    WI_DOPPELT: "Diesen Kommentar hast du schon geschrieben.",
    WI_WORT: "Der Kommentar verstößt gegen unsere Kommentarregeln und wurde nicht veröffentlicht.",
    WI_GESPERRT: "Dein Profil ist zurzeit für Kommentare gesperrt.",
    WI_AUS: "Kommentare sind gerade pausiert.",
    WI_KONTO: "Kommentieren geht gerade nur mit Konto.",
    WI_ANTWORT: "Auf diesen Kommentar kann man nicht mehr antworten.",
    WI_KURZ: "Der Kommentar ist zu kurz.",
    WI_EIGEN: "Eigene Kommentare kannst du nicht liken oder melden.",
    WI_WEG: "Den Kommentar gibt es nicht mehr.",
    WI_LOGIN: "Verbindung fehlgeschlagen. Bitte noch einmal versuchen.",
    WI_KEIN_MOD: "Dafür fehlen die Rechte."
  };
  var GRUENDE = [["beleidigung", "Beleidigung"], ["hass", "Hass oder Hetze"], ["spam", "Spam oder Werbung"],
                 ["falschinfo", "Falschinformation"], ["rechtswidrig", "Rechtswidriger Inhalt"], ["sonstiges", "Sonstiges"]];

  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function fehlertext(e) {
    var m = String((e && (e.message || e.error_description)) || e || "");
    var k = (m.match(/WI_[A-Z_]+/) || [])[0];
    if (k && FEHLER[k]) return FEHLER[k];
    if (/anonymous.*disabled|signups not allowed/i.test(m)) return "Kommentare sind noch nicht freigeschaltet.";
    if (/rate limit|too many/i.test(m)) return "Zu viele Anfragen. Bitte gleich noch einmal versuchen.";
    return "Das hat nicht geklappt. Bitte später noch einmal versuchen.";
  }
  function vor(z) {
    var d = (Date.now() - new Date(z).getTime()) / 1000;
    if (d < 60) return "gerade eben";
    if (d < 3600) return "vor " + Math.floor(d / 60) + " Min.";
    if (d < 86400) return "vor " + Math.floor(d / 3600) + " Std.";
    if (d < 7 * 86400) { var t = Math.floor(d / 86400); return "vor " + t + (t === 1 ? " Tag" : " Tagen"); }
    var x = new Date(z); return x.getDate() + "." + (x.getMonth() + 1) + "." + x.getFullYear();
  }
  function el() { return document.getElementById("kom"); }
  function istMod() { return !!(S.ich && (S.ich.rolle === "moderator" || S.ich.rolle === "admin")); }

  // ---------- Daten ----------
  function hatSitzung() {
    return sb.auth.getSession().then(function (r) { return !!(r.data && r.data.session); });
  }
  function sitzung() {
    return hatSitzung().then(function (ok) {
      if (ok) return;
      return sb.auth.signInAnonymously().then(function (r) { if (r.error) throw r.error; });
    }).then(function () { return profilLaden(); });
  }
  function profilLaden() {
    return sb.rpc("mein_profil").then(function (r) { if (!r.error) S.ich = r.data; });
  }
  function laden() {
    if (!S.beitrag) return Promise.resolve();
    var b = S.beitrag; S.laden = true;
    return sb.from("kommentar")
      .select("id,beitrag,eltern,autor,text,status,grund,likes,erstellt,profil(name,rolle)")
      .eq("beitrag", b).order("erstellt", { ascending: false }).limit(500)
      .then(function (r) {
        if (b !== S.beitrag) return;
        S.laden = false; S.geladen = true;
        if (r.error) { S.liste = []; S.fehler = "Kommentare konnten nicht geladen werden."; S.fehlerAn = null; return; }
        S.liste = r.data || [];
        return hatSitzung().then(function (ok) {
          if (!ok || !S.liste.length) return;
          return Promise.all([
            S.ich ? null : profilLaden(),
            sb.from("kommentar_like").select("kommentar").in("kommentar", S.liste.map(function (k) { return k.id; }))
              .then(function (l) { S.likes = {}; (l.data || []).forEach(function (x) { S.likes[x.kommentar] = true; }); })
          ]);
        });
      })
      .catch(function () { S.laden = false; S.geladen = true; S.fehler = "Kommentare konnten nicht geladen werden."; })
      .then(zeichnen);
  }

  // ---------- Darstellung ----------
  function badge(k) {
    var r = k.profil && k.profil.rolle;
    return r === "admin" || r === "moderator" ? '<span class="wk-red">Redaktion</span>' : "";
  }
  function formular(eltern) {
    var key = S.beitrag + "|" + (eltern || ""), wert = ENTWURF[key] || "";
    var fehlerHier = S.fehler && S.fehlerAn === (eltern || "haupt");
    return '<form class="wk-form' + (eltern ? " wk-antw" : "") + '" data-kform="' + esc(eltern || "") + '">' +
      '<label class="wk-sr" for="wk-t-' + esc(eltern || "h") + '">' + (eltern ? "Antwort schreiben" : "Kommentar schreiben") + "</label>" +
      '<textarea id="wk-t-' + esc(eltern || "h") + '" maxlength="' + MAX + '" rows="' + (eltern ? 2 : 3) + '" placeholder="' +
        (eltern ? "Antworten …" : "Was meinst du? Fair bleiben, Spielerinnen respektieren.") + '">' + esc(wert) + "</textarea>" +
      '<div class="wk-fz"><span class="wk-mu">' + (S.ich ? "Du schreibst als " + esc(S.ich.name) : "Ohne Anmeldung, mit zufälligem Fan-Namen") +
      ' · <span data-kzahl>' + wert.length + "</span>/" + MAX + "</span>" +
      (eltern ? '<button type="button" class="wk-link" data-kaktion="abbrechen">Abbrechen</button>' : "") +
      '<button type="submit" class="wk-senden"' + (S.sendet ? " disabled" : "") + ">" + (S.sendet ? "Sendet …" : "Senden") + "</button></div>" +
      (fehlerHier ? '<p class="wk-fehler" role="alert">' + esc(S.fehler) + "</p>" : "") +
      "</form>";
  }
  function kommentar(k, istAntwort) {
    var eigen = S.ich && k.autor === S.ich.id;
    var geloescht = k.status === "geloescht";
    var nichtOeffentlich = k.status === "pruefung" || k.status === "ausgeblendet";
    var h = '<div class="wk-k' + (istAntwort ? " wk-sub" : "") + (nichtOeffentlich ? " wk-verborgen" : "") + '">' +
      '<div class="wk-kopf"><b>' + esc(k.profil ? k.profil.name : "Fan") + "</b>" + badge(k) +
      '<span class="wk-mu">' + vor(k.erstellt) + "</span></div>";
    if (nichtOeffentlich) {
      h += '<p class="wk-hinweis">' + (eigen ? "Nur für dich sichtbar. " : "Nicht öffentlich. ") + esc(k.grund || "") + "</p>";
    }
    h += '<p class="wk-text' + (geloescht ? " wk-mu" : "") + '">' + esc(k.text) + "</p>";
    if (!geloescht) {
      h += '<div class="wk-akt">';
      if (k.status === "sichtbar") {
        h += '<button data-kaktion="like" data-kid="' + k.id + '" aria-pressed="' + (S.likes[k.id] ? "true" : "false") + '"' +
             (eigen ? " disabled" : "") + ">" + (S.likes[k.id] ? "♥" : "♡") + " " + (k.likes || 0) + "</button>";
        if (!istAntwort) h += '<button data-kaktion="antworten" data-kid="' + k.id + '">Antworten</button>';
        if (!eigen) h += '<button data-kaktion="melden" data-kid="' + k.id + '">Melden</button>';
      }
      if (eigen) h += '<button data-kaktion="loeschen" data-kid="' + k.id + '">Löschen</button>';
      if (istMod() && !eigen) {
        h += k.status === "sichtbar"
          ? '<button class="wk-mod" data-kaktion="ausblenden" data-kid="' + k.id + '">Ausblenden</button>'
          : '<button class="wk-mod" data-kaktion="freigeben" data-kid="' + k.id + '">Freigeben</button>';
        h += '<button class="wk-mod" data-kaktion="sperren" data-kid="' + k.id + '">Sperren 7 T.</button>';
      }
      h += "</div>";
    }
    if (S.melden === k.id) {
      h += '<div class="wk-melden"><span class="wk-mu">Warum meldest du den Kommentar?</span><div class="wk-gr">' +
        GRUENDE.map(function (g) { return '<button data-kaktion="meldegrund" data-kid="' + k.id + '" data-grund="' + g[0] + '">' + g[1] + "</button>"; }).join("") +
        '</div><button class="wk-link" data-kaktion="melden-zu">Abbrechen</button></div>';
    }
    return h + "</div>";
  }
  function zeichnen() {
    var box = el();
    if (!box || !AKTIV) return;
    var alle = S.liste;
    var haupt = alle.filter(function (k) { return !k.eltern; });
    var kinder = {};
    alle.forEach(function (k) { if (k.eltern) (kinder[k.eltern] = kinder[k.eltern] || []).push(k); });
    if (S.sort === "top") haupt.sort(function (a, b) { return (b.likes - a.likes) || (new Date(b.erstellt) - new Date(a.erstellt)); });
    var sichtbar = alle.filter(function (k) { return k.status === "sichtbar"; }).length;
    var h = '<section class="wk" aria-labelledby="wk-h"><div class="wk-top"><h2 id="wk-h" class="kap">Kommentare' +
      (sichtbar ? " · " + sichtbar : "") + "</h2>" +
      (haupt.length > 1 ? '<div class="wk-sort" role="group" aria-label="Sortierung">' +
        '<button data-kaktion="sort" data-sort="neu" aria-pressed="' + (S.sort === "neu") + '">Neu</button>' +
        '<button data-kaktion="sort" data-sort="top" aria-pressed="' + (S.sort === "top") + '">Top</button></div>' : "") +
      "</div>";
    h += formular(null);
    h += '<details class="wk-regeln"' + (S.offenRegeln ? " open" : "") + '><summary>Kommentarregeln</summary>' + REGELN + "</details>";
    if (S.fehler && S.fehlerAn === null) h += '<p class="wk-fehler" role="alert">' + esc(S.fehler) + "</p>";
    if (!S.geladen) h += '<p class="wk-mu">Kommentare werden geladen …</p>';
    else if (!haupt.length) h += '<p class="wk-mu">Noch keine Kommentare. Schreib den ersten.</p>';
    haupt.slice(0, S.zeige).forEach(function (k) {
      var subs = (kinder[k.id] || []).slice().sort(function (a, b) { return new Date(a.erstellt) - new Date(b.erstellt); });
      if (k.status !== "sichtbar" && k.status !== "geloescht" && !(S.ich && k.autor === S.ich.id) && !istMod()) return;
      h += '<div class="wk-faden">' + kommentar(k, false) + subs.map(function (s) { return kommentar(s, true); }).join("") +
        (S.antwort === k.id ? formular(k.id) : "") + "</div>";
    });
    if (haupt.length > S.zeige) h += '<button class="wk-mehr" data-kaktion="mehr">Weitere ' + Math.min(SEITE, haupt.length - S.zeige) + " Kommentare</button>";
    h += "</section>";
    var fokus = document.activeElement && box.contains(document.activeElement) && document.activeElement.id;
    var pos = fokus && document.activeElement.selectionStart;
    box.innerHTML = h;
    if (fokus) { var f = document.getElementById(fokus); if (f) { f.focus(); try { f.setSelectionRange(pos, pos); } catch (e) {} } }
  }

  // ---------- Aktionen ----------
  function aktion(fn, wo) {
    S.fehler = ""; S.fehlerAn = wo === undefined ? null : wo;
    return sitzung().then(fn).then(function (r) { if (r && r.error) throw r.error; })
      .catch(function (e) { S.fehler = fehlertext(e); S.fehlerAn = wo === undefined ? null : wo; })
      .then(laden);
  }
  document.addEventListener("input", function (e) {
    var t = e.target; if (!t.closest || !t.closest("#kom form[data-kform]")) return;
    var f = t.closest("form"), key = S.beitrag + "|" + f.dataset.kform;
    ENTWURF[key] = t.value;
    var z = f.querySelector("[data-kzahl]"); if (z) z.textContent = t.value.length;
  });
  document.addEventListener("submit", function (e) {
    var f = e.target; if (!f.closest || !f.closest("#kom") || !f.matches("form[data-kform]")) return;
    e.preventDefault();
    if (S.sendet) return;
    var eltern = f.dataset.kform || null, key = S.beitrag + "|" + (eltern || "");
    var text = (f.querySelector("textarea").value || "").trim();
    if (text.length < 2) { S.fehler = FEHLER.WI_KURZ; S.fehlerAn = eltern || "haupt"; zeichnen(); return; }
    S.sendet = true; zeichnen();
    S.fehler = ""; S.fehlerAn = null;
    sitzung()
      .then(function () { return sb.from("kommentar").insert({ beitrag: S.beitrag, text: text, eltern: eltern }); })
      .then(function (r) { if (r.error) throw r.error; ENTWURF[key] = ""; if (eltern) S.antwort = null; })
      .catch(function (err) { S.fehler = fehlertext(err); S.fehlerAn = eltern || "haupt"; })
      .then(function () { S.sendet = false; return laden(); });
  });
  document.addEventListener("click", function (e) {
    var b = e.target.closest && e.target.closest("#kom [data-kaktion]");
    if (!b || b.disabled) return;
    e.preventDefault(); e.stopPropagation();
    var a = b.dataset.kaktion, id = b.dataset.kid;
    if (a === "sort") { S.sort = b.dataset.sort; zeichnen(); return; }
    if (a === "mehr") { S.zeige += SEITE; zeichnen(); return; }
    if (a === "antworten") { S.antwort = S.antwort === id ? null : id; S.melden = null; zeichnen();
      var t = document.getElementById("wk-t-" + id); if (t) t.focus(); return; }
    if (a === "abbrechen") { S.antwort = null; zeichnen(); return; }
    if (a === "melden") { S.melden = S.melden === id ? null : id; zeichnen(); return; }
    if (a === "melden-zu") { S.melden = null; zeichnen(); return; }
    if (a === "meldegrund") {
      S.melden = null;
      aktion(function () { return sb.from("kommentar_meldung").insert({ kommentar: id, grund: b.dataset.grund }); })
        .then(function () { if (!S.fehler) { S.fehler = "Danke, die Meldung ist angekommen. Die Redaktion prüft sie."; S.fehlerAn = null; zeichnen(); } });
      return;
    }
    if (a === "like") {
      var an = !S.likes[id];
      S.likes[id] = an;
      S.liste.forEach(function (k) { if (k.id === id) k.likes = Math.max(0, (k.likes || 0) + (an ? 1 : -1)); });
      zeichnen();
      aktion(function () {
        return an ? sb.from("kommentar_like").insert({ kommentar: id })
                  : sb.from("kommentar_like").delete().eq("kommentar", id).eq("nutzer", S.ich && S.ich.id);
      });
      return;
    }
    if (a === "loeschen") {
      if (!window.confirm("Kommentar wirklich löschen?")) return;
      aktion(function () { return sb.rpc("kommentar_loeschen", { kid: id }); });
      return;
    }
    if (a === "ausblenden" || a === "freigeben") {
      var g = a === "ausblenden" ? window.prompt("Begründung (sieht die Person):", "Verstoß gegen die Kommentarregeln") : null;
      if (a === "ausblenden" && g === null) return;
      aktion(function () { return sb.rpc("moderieren", { kid: id, aktion: a, begruendung: g }); });
      return;
    }
    if (a === "sperren") {
      var k = S.liste.find(function (x) { return x.id === id; }); if (!k) return;
      var grund = window.prompt("7 Tage sperren. Begründung (sieht die Person):", "Wiederholter Verstoß gegen die Kommentarregeln");
      if (grund === null) return;
      aktion(function () { return sb.rpc("nutzer_sperren", { uid: k.autor, tage: 7, begruendung: grund }); });
    }
  }, true);
  document.addEventListener("toggle", function (e) {
    if (e.target && e.target.classList && e.target.classList.contains("wk-regeln")) S.offenRegeln = e.target.open;
  }, true);

  // ---------- Einbau ----------
  function mount(beitrag) {
    if (!AKTIV) return;
    var box = el(); if (!box) return;
    if (S.beitrag !== beitrag) {
      S.beitrag = beitrag; S.liste = []; S.likes = {}; S.zeige = SEITE; S.antwort = null; S.melden = null;
      S.fehler = ""; S.fehlerAn = null; S.geladen = false; S.offenRegeln = false;
    }
    zeichnen(); laden();
    if (TIMER) clearInterval(TIMER);
    TIMER = setInterval(function () {
      var b = el();
      if (!b || b.dataset.beitrag !== S.beitrag) { clearInterval(TIMER); TIMER = null; return; }
      if (document.visibilityState === "visible" && !S.sendet && !(document.activeElement && b.contains(document.activeElement))) laden();
    }, 60000);
  }

  var REGELN = '<div class="wk-rt">' +
    "<p>Hier geht es um Fußball. Diskutiere fair, auch wenn es hitzig wird.</p><ul>" +
    "<li>Keine Beleidigungen, keine Hetze, keine Drohungen. Das gilt besonders gegenüber Spielerinnen, Trainerinnen und Trainern, Schiedsrichterinnen und anderen Fans.</li>" +
    "<li>Keine Kommentare über Aussehen, Körper oder Privatleben von Spielerinnen.</li>" +
    "<li>Keine Werbung, kein Spam, keine Links zu fremden Angeboten.</li>" +
    "<li>Keine Gerüchte als Tatsache. Verletzungs- oder Aufstellungsinfos gern als Hinweis an redaktion@wosoinsider.de.</li>" +
    "<li>Nichts Rechtswidriges, keine persönlichen Daten anderer.</li></ul>" +
    "<p>Ein Wortfilter hält manche Kommentare zurück, bis die Redaktion sie prüft. Kommentare, die mehrfach gemeldet werden, werden automatisch ausgeblendet und geprüft. Bei Verstößen können wir Kommentare ausblenden oder löschen und Profile zeitweise oder dauerhaft sperren. Den Grund siehst du bei deinem Kommentar.</p>" +
    "<p>Rechtswidrige Inhalte bitte über „Melden“ oder an redaktion@wosoinsider.de. Für deine Kommentare bist du selbst verantwortlich. Mehr dazu in der Datenschutzerklärung.</p></div>";

  var css = document.createElement("style");
  css.textContent =
    ".wk{display:grid;gap:12px;border-top:1px solid var(--line);padding-top:14px;margin-top:4px}" +
    ".wk-top{display:flex;justify-content:space-between;align-items:center}.wk-top h2{margin:0}" +
    ".wk-sort{display:flex;gap:4px;background:var(--card);border-radius:9px;padding:3px}" +
    ".wk-sort button{font-size:12px;padding:5px 10px;border-radius:7px;color:var(--muted)}" +
    ".wk-sort button[aria-pressed=true]{background:var(--soft);color:var(--ink);font-weight:600}" +
    ".wk-form{display:grid;gap:6px}" +
    ".wk-form textarea{width:100%;box-sizing:border-box;resize:vertical;min-height:64px;background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:12px;padding:10px 12px;font:15px/1.4 var(--f-body)}" +
    ".wk-form textarea:focus{outline:2px solid var(--accent);outline-offset:1px;border-color:transparent}" +
    ".wk-antw textarea{min-height:48px}" +
    ".wk-fz{display:flex;gap:10px;align-items:center;justify-content:flex-end;flex-wrap:wrap}.wk-fz .wk-mu{margin-right:auto}" +
    ".wk-senden{background:var(--accent);color:#fff;font-weight:600;font-size:14px;border-radius:10px;padding:8px 16px;min-height:36px}" +
    ".wk-senden[disabled]{opacity:.6}" +
    ".wk-mu{color:var(--muted);font-size:12.5px}" +
    ".wk-link{color:var(--accent);font-size:13px;padding:6px 2px}" +
    ".wk-fehler{margin:0;font-size:13px;color:var(--ink);background:var(--soft);border-left:3px solid var(--frag);border-radius:8px;padding:8px 10px}" +
    ".wk-regeln{font-size:13px;color:var(--muted)}.wk-regeln summary{cursor:pointer;color:var(--muted);font-size:12.5px;padding:2px 0}" +
    ".wk-rt{display:grid;gap:6px;padding:8px 0 2px}.wk-rt p,.wk-rt ul{margin:0}.wk-rt ul{padding-left:18px;display:grid;gap:4px}" +
    ".wk-faden{display:grid;gap:8px;background:var(--card);border-radius:14px;padding:12px}" +
    ".wk-k{display:grid;gap:4px}.wk-sub{margin-left:14px;padding-left:10px;border-left:2px solid var(--line)}" +
    ".wk-verborgen{opacity:.75}" +
    ".wk-kopf{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap}.wk-kopf b{font-size:13.5px}" +
    ".wk-red{font:700 10px var(--f-mono);letter-spacing:.6px;text-transform:uppercase;background:var(--accent);color:#fff;border-radius:99px;padding:2px 7px}" +
    ".wk-text{margin:0;white-space:pre-wrap;overflow-wrap:anywhere;font-size:15px}" +
    ".wk-hinweis{margin:0;font-size:12.5px;color:var(--frag)}" +
    ".wk-akt{display:flex;gap:14px;flex-wrap:wrap}" +
    ".wk-akt button{font-size:12.5px;color:var(--muted);padding:6px 0;min-height:32px}" +
    ".wk-akt button[aria-pressed=true]{color:var(--rot)}.wk-akt button[disabled]{opacity:.5}" +
    ".wk-akt .wk-mod{color:var(--frag)}" +
    ".wk-melden{display:grid;gap:6px;background:var(--soft);border-radius:10px;padding:10px}" +
    ".wk-gr{display:flex;flex-wrap:wrap;gap:6px}.wk-gr button{font-size:12.5px;background:var(--card);border:1px solid var(--line);border-radius:99px;padding:6px 10px}" +
    ".wk-mehr{justify-self:center;color:var(--accent);font-size:13px;font-weight:600;padding:8px 12px}" +
    ".wk-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}";
  document.head.appendChild(css);

  window.WIKOM = { mount: mount, aktiv: AKTIV };
  // Falls der Artikel schon vor diesem Skript gezeichnet wurde (Direktlink)
  var vorhanden = el(); if (vorhanden && vorhanden.dataset.beitrag) mount(vorhanden.dataset.beitrag);
})();
