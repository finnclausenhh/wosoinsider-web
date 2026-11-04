#!/usr/bin/env python3
"""Baut Gamification (Spielt sie?, Einsehbar, Prognose-Bilanz, Gefragt diese Woche) und den Standard-Check
mit Messlatte in eine Ticker-index.html ein (live seit 04.11.2026, Finn).

Aufruf: python3 tools/gami_einbau.py <index.html> <ausgabe.html> [--test]
Gilt für beide Fassungen: die index.html im Artifact und ticker/index.html. Jede Ersetzung muss genau
einmal passen, sonst bricht das Skript ab. Bereits eingebaut (Marker vorhanden): Abbruch ohne Änderung.
Quellen: tools/gami/gami.js, gami.css, standard.js, standard.css.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
G = ROOT / "tools" / "gami"
MARKER = "// ---------------- Standard-Check (Finn 04.11.2026)"


def ersetze(s, alt, neu):
    n = s.count(alt)
    if n != 1:
        sys.exit(f"Anker {alt[:60]!r} {n}-mal gefunden")
    return s.replace(alt, neu)


def einbau(s, test=False):
    if MARKER in s or "function tippZeile()" in s:
        sys.exit("schon eingebaut")
    js = (G / "gami.js").read_text(encoding="utf-8")
    css = (G / "gami.css").read_text(encoding="utf-8") + "\n" + (G / "standard.css").read_text(encoding="utf-8")
    sjs = (G / "standard.js").read_text(encoding="utf-8")
    i = s.find("</style>", s.find("--f-display"))
    if i < 0:
        sys.exit("Stilblock nicht gefunden")
    s = s[:i] + "\n" + css + s[i:]
    # Umfragen: Prozente ab der ersten Stimme, immer mit Anzahl
    s = ersetze(s, "const MIN_STIMMEN = 10;", "const MIN_STIMMEN = 1;")
    s = ersetze(s, "genug ? `${zahlDE(ges)} Stimmen`", "genug ? `${zahlDE(ges)} ${ges === 1 ? \"Stimme\" : \"Stimmen\"}`")
    s = ersetze(s, "function list(){", js + "\n  function list(){")
    s = ersetze(s, "rest.forEach(m => {", "rest.forEach((m, gi) => {")
    s = ersetze(s, ": newsKarte(m); });", ": newsKarte(m); if (gi === 0) h += tippZeile(); if (gi === 2) h += gefragtZeile(); });")
    s = ersetze(s, "${bs.length ? (klein ?",
                "${p.status !== \"beendet\" && einsehbar(p) ? `<div class=\"eins-z\">${einsTag()}<span>Aufstellung vor dem Kickbase-Schluss</span></div>` : \"\"}${bs.length ? (klein ?")
    s = ersetze(s, "</span><span class=\"r\">${esc(tagDatum(z.datum))}",
                "${einsehbarZeit(z.datum, z.wb) ? einsTag(true) : \"\"}</span><span class=\"r\">${esc(tagDatum(z.datum))}")
    s = ersetze(s, "${IN.ausgabe ? hero(IN.ausgabe) : \"\"}", "${IN.ausgabe ? hero(IN.ausgabe) : \"\"}${bilanzSektion()}")
    s = ersetze(s, "if ((x = q(\"[data-profilname]\")))",
                "if (q(\"[data-tipp]\")) { tippschein(); return; }\n"
                "    if (q(\"[data-tippzu]\")) { VIEW = \"meldungen\"; list(); window.scrollTo(0, 0); return; }\n"
                "    if ((x = q(\"[data-tv]\"))) { if (x.disabled) return; const [md, qid, oid] = x.dataset.tv.split(\"|\"); TIPPS[md] = TIPPS[md] || {};"
                " TIPPS[md][qid] = TIPPS[md][qid] === oid ? undefined : oid; tippsSpeichern(); const y = window.scrollY; tippschein(); window.scrollTo(0, y); return; }\n"
                "    if ((x = q(\"[data-profilname]\")))")
    # Standard-Check: Karte im Feed und Artikel mit Messlatte (Daten: grafik in der Meldung, apifootball.json)
    s = ersetze(s, "  const angeheftet = m => m.typ === \"punkt\"", sjs + "  const angeheftet = m => m.typ === \"punkt\"")
    # Feed: normale Meldungskarte (Foto der ersten Spielerin über das Feld spielerin), Finn 04.11.2026
    s = ersetze(s, "    const st = STATUS[String(meldungsStatus(m) || \"\").toLowerCase()];\n    const kopf = auf",
                "    const st = STATUS[String(meldungsStatus(m) || \"\").toLowerCase()];\n    const sc = m.grafik && m.grafik.typ === \"messlatte\" && scSp(m).length;\n    const kopf = sc ? scArtikel(m) : auf")
    s = ersetze(s, "    const fi = FOTOS[m.spielerin], fc = m.foto_credit;", "    const fi = FOTOS[sc ? scSp(m)[0].n : m.spielerin], fc = m.foto_credit;")
    s = ersetze(s, "<div id=\"pf-karte\">${auf ? \"\" : profilKarte(m)}</div>", "<div id=\"pf-karte\">${auf || sc ? \"\" : profilKarte(m)}</div>")
    s = ersetze(s, "    if (!auf && !SPN && istSpielerin(m)) ladeSPN()", "    if (!auf && !sc && !SPN && istSpielerin(m)) ladeSPN()")
    if test:
        s = ersetze(s, "<main id=\"main\">", "<div style=\"background:#F5B041;color:#2A1700;font:600 12px/1.3 Inter,sans-serif;text-align:center;padding:6px 10px\">Testseite</div>\n<main id=\"main\">")
    assert "—" not in s
    return s


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    s = einbau(pathlib.Path(a[0]).read_text(encoding="utf-8"), "--test" in sys.argv)
    pathlib.Path(a[1]).write_text(s, encoding="utf-8")
    print("geschrieben:", a[1], len(s))
