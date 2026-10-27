// Ereignisse im Ticker: geöffnete Meldungen (plus Spielerin und Verein), Reiter, Spiele, Analyse.
// Braucht zaehler.js davor. Liest news.json über die base-Adresse (fbl-daten), nur für Überschrift, Spielerin, Verein.
(function () {
  var NEWS = null;
  function slug(s) {
    return String(s).toLowerCase().replace(/ä/g, "ae").replace(/ö/g, "oe").replace(/ü/g, "ue").replace(/ß/g, "ss")
      .normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  }
  function laden() {
    if (!NEWS) NEWS = fetch("news.json").then(function (r) { return r.json(); })
      .then(function (d) { var m = {}; (d.meldungen || []).forEach(function (x) { m[x.id] = x; }); return m; })
      .catch(function () { NEWS = null; return {}; });
    return NEWS;
  }
  function meldung(id) {
    laden().then(function (m) {
      var x = m[id];
      if (!x) { wiZaehl("meldung/" + id, null, true); return; }
      wiZaehl("meldung/" + id, x.headline, true);
      if (x.spielerin) wiZaehl("spielerin/" + slug(x.spielerin), x.spielerin + (x.verein ? " (" + x.verein + ")" : ""), true);
      if (x.verein) wiZaehl("verein/" + slug(x.verein), x.verein, true);
    });
  }
  document.addEventListener("click", function (e) {
    var x = e.target.closest && e.target.closest("[data-id],[data-punkt],[data-tab],[data-tabgo],[data-game],[data-ana]");
    if (!x) return;
    var d = x.dataset;
    if (d.tab || d.tabgo) wiZaehl("reiter/" + (d.tab || d.tabgo), null, true);
    else if (d.game) wiZaehl("spiel/" + d.game, null, true);
    else if (d.ana !== undefined) wiZaehl("inside/analyse", "Analyse", true);
    else meldung(d.id || d.punkt);
  }, true);
  // Direktlink auf eine Meldung (wosoinsider.de/ticker/#id), z. B. aus Instagram
  var h = decodeURIComponent(location.hash.slice(1));
  if (h && !/^(spielplan|inside|analyse|impressum|datenschutz|kontakt|so-entsteht)$/.test(h)) meldung(h);
  else if (h) wiZaehl("reiter/" + h, null, true);
})();
