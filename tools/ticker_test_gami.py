#!/usr/bin/env python3
"""Baut ticker-test/index.html: Live-Ticker plus Gamification-Konzept (Stand 04.11.2026).

Aufruf aus dem Repo-Wurzelordner: python3 tools/ticker_test_gami.py
Jede Ersetzung muss genau einmal passen, sonst bricht das Skript ab.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
src = (ROOT / "ticker" / "index.html").read_text(encoding="utf-8")
js = (ROOT / "tools" / "gami" / "gami.js").read_text(encoding="utf-8")
css = (ROOT / "tools" / "gami" / "gami.css").read_text(encoding="utf-8")


def ersetze(s, alt, neu):
    n = s.count(alt)
    if n != 1:
        sys.exit(f"Anker {alt[:60]!r} {n}-mal gefunden")
    return s.replace(alt, neu)


s = src
# Stil: an das Ende des ersten großen Stilblocks
i = s.find("</style>", s.find("--f-display"))
if i < 0:
    sys.exit("Stilblock nicht gefunden")
s = s[:i] + "\n" + css + s[i:]
# Umfragen: Prozente ab der ersten Stimme, immer mit Anzahl
s = ersetze(s, "const MIN_STIMMEN = 10;", "const MIN_STIMMEN = 1;")
s = ersetze(s, "genug ? `${zahlDE(ges)} Stimmen`", "genug ? `${zahlDE(ges)} ${ges === 1 ? \"Stimme\" : \"Stimmen\"}`")
# Bausteine vor dem Feed einfügen
s = ersetze(s, "function list(){", js + "\n  function list(){")
# Feed: Tippspiel nach der ersten Meldung, Gefragt diese Woche nach der dritten
s = ersetze(s, "rest.forEach(m => {", "rest.forEach((m, gi) => {")
s = ersetze(s, ": newsKarte(m); });", ": newsKarte(m); if (gi === 0) h += tippZeile(); if (gi === 2) h += gefragtZeile(); });")
# Spielplan: Einsehbar an der Partie
s = ersetze(s, "${bs.length ? (klein ?",
            "${p.status !== \"beendet\" && einsehbar(p) ? `<div class=\"eins-z\">${einsTag()}<span>Aufstellung vor dem Kickbase-Schluss</span></div>` : \"\"}${bs.length ? (klein ?")
# Profil: Einsehbar an den nächsten Spielen
s = ersetze(s, "</span><span class=\"r\">${esc(tagDatum(z.datum))}",
            "${einsehbarZeit(z.datum, z.wb) ? einsTag(true) : \"\"}</span><span class=\"r\">${esc(tagDatum(z.datum))}")
# Inside: Prognose-Bilanz nach der Ausgabe
s = ersetze(s, "${IN.ausgabe ? hero(IN.ausgabe) : \"\"}", "${IN.ausgabe ? hero(IN.ausgabe) : \"\"}${bilanzSektion()}")
# Klicks
s = ersetze(s, "if ((x = q(\"[data-profilname]\")))",
            "if (q(\"[data-tipp]\")) { tippschein(); return; }\n"
            "    if (q(\"[data-tippzu]\")) { VIEW = \"meldungen\"; list(); window.scrollTo(0, 0); return; }\n"
            "    if ((x = q(\"[data-tv]\"))) { if (x.disabled) return; const [md, qid, oid] = x.dataset.tv.split(\"|\"); TIPPS[md] = TIPPS[md] || {};"
            " TIPPS[md][qid] = TIPPS[md][qid] === oid ? undefined : oid; tippsSpeichern(); const y = window.scrollY; tippschein(); window.scrollTo(0, y); return; }\n"
            "    if ((x = q(\"[data-profilname]\")))")
# Kennzeichnung als Testseite
s = ersetze(s, "<main id=\"main\">", "<div style=\"background:#F5B041;color:#2A1700;font:600 12px/1.3 Inter,sans-serif;text-align:center;padding:6px 10px\">Testseite: Gamification-Konzept (Spielt sie?, Einsehbar, Prognose-Bilanz)</div>\n<main id=\"main\">")

out = ROOT / "ticker-test" / "index.html"
out.parent.mkdir(exist_ok=True)
out.write_text(s, encoding="utf-8")
print("geschrieben:", out, len(s))
