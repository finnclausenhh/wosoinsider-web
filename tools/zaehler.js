// Reichweitenmessung mit GoatCounter (ohne Cookies, ohne Skript von Dritten, ohne Gerätespeicher).
// Sendet nur Pfad, Titel, Referrer und Kampagnen-Parameter (z. B. ?utm_source=instagram) als Zählpixel.
// Zählt nur auf wosoinsider.de, nicht im Artifact, lokal oder in Vorschauen.
(function () {
  var GC = "https://wosoinsider.goatcounter.com/count";
  if (!/(^|\.)wosoinsider\.de$/.test(location.hostname)) { window.wiZaehl = function () {}; return; }
  // Eigene Aufrufe über ein Lesezeichen mit ?intern: werden getrennt unter intern/... gezählt.
  var INTERN = /[?&]intern(=|&|$)/.test(location.search);
  function z(p, t, ev) {
    if (INTERN) { p = "intern/" + String(p).replace(/^\//, ""); t = "[intern] " + (t || ""); ev = true; }
    var q = "p=" + encodeURIComponent(p);
    if (t) q += "&t=" + encodeURIComponent(t);
    if (ev) q += "&e=true";
    else {
      if (document.referrer) q += "&r=" + encodeURIComponent(document.referrer);
      if (location.search) q += "&q=" + encodeURIComponent(location.search);
    }
    q += "&rnd=" + Math.random().toString(36).slice(2);
    try { new Image().src = GC + "?" + q; } catch (e) {}
  }
  window.wiZaehl = z;
  function seite() { z(location.pathname, document.title, false); }
  document.readyState === "loading" ? document.addEventListener("DOMContentLoaded", seite) : seite();
})();
