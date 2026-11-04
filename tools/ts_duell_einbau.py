#!/usr/bin/env python3
"""Tippkarte im Duell-Stil (Finn 04.11.2026, Variante B für alle Fragetypen) einbauen.

Aufruf: python3 tools/ts_duell_einbau.py <datei> [<datei> ...]
Gilt für ticker/index.html, die index.html im Artifact und die Quellen tools/gami/gami.js und gami.css.
Jede Ersetzung wird nur angewandt, wenn ihr Anker genau einmal vorkommt. In einer Ticker-Fassung
(enthält "function article(") müssen alle Ersetzungen passen, sonst Abbruch.
Quellen: tools/gami/ts_duell.js, ts_duell.css.
"""
import pathlib
import sys

G = pathlib.Path(__file__).resolve().parent / "gami"
JS = (G / "ts_duell.js").read_text(encoding="utf-8")
CSS = (G / "ts_duell.css").read_text(encoding="utf-8")
MARK = "function tsKarte("

ERS = [
    # Auflösung aller Tippfragen aus tipp_loesung.json (spielt_sie.py)
    ('json("spielt_sie.json").then(d => { SS = d; }).catch(() => { SS = null; })', 'json("spielt_sie.json").then(d => { SS = d; }).catch(() => { SS = null; }),\n      json("tipp_loesung.json").then(d => { TL = d; }).catch(() => { TL = null; })'),
    # Umfragen im Duell-Stil, alte Liste nur noch als Rückfall
    ('<div class="um-o${kurz ? " kurz" : ""}" style="--n:${O.length}">${opts}</div>',
     '${umKarten(u, feed, {meine, zeigt, zp, pz, auf}) || `<div class="um-o${kurz ? " kurz" : ""}" style="--n:${O.length}">${opts}</div>`}'),
    # Artikel: Tippkarte statt Umfrage, wenn die Frage zur Meldung gehört
    ("ARTIKEL = id; const um = umfrageZu(m.id);", "ARTIKEL = id; const um = umfrageZu(m.id), tsA = tsArtikel(m);"),
    ('${zurueck()}${kopf}${um ? umfrageBlock(um) : ""}', '${zurueck()}${kopf}${tsA ? tsA : um ? umfrageBlock(um) : ""}'),
    # Feed: Meldungen bleiben einheitlich (Finn 04.11.2026). Tippfrage und Umfrage nur als schmale Zeile, Grafiken erst im Artikel
    ('uT ? `<div class="nkw">${newsKarte(m)}${umfrageBlock(uT, true)}</div>`',
     'uT ? (tsFrageZu(m) ? `<div class="nkw">${newsKarte(m)}<button class="um-h" data-id="${esc(m.id)}"><span class="tag" style="background:rgba(47,91,255,.18);color:#8FB0FF">SPIELT SIE?</span><span class="t">${esc(uT.frage)}</span><b>Tippen ›</b></button></div>` : `<div class="nkw">${newsKarte(m)}<button class="um-h" data-id="${esc(m.id)}">${tag("UMFRAGE")}<span class="t">${esc(uT.frage)}</span><b>${STIMMEN[uT.id] ? "abgestimmt" : "Abstimmen ›"}</b></button></div>`)'),
    # Tippen im Artikel zeichnet den Artikel neu
    ("tsSetzen(md, qid, TIPPS[md][qid]); const y = window.scrollY; tippschein(); window.scrollTo(0, y); return; }",
     "tsSetzen(md, qid, TIPPS[md][qid]); const y = window.scrollY; if (VIEW === \"tipp\") tippschein(); else if (ARTIKEL) article(ARTIKEL); window.scrollTo(0, y); return; }"),
    ('const tsNeu = () => { if (VIEW === "tipp") {',
     'const tsNeu = () => { if (VIEW !== "tipp" && ARTIKEL && document.querySelector(".tsd-art")) { const y = window.scrollY; article(ARTIKEL); window.scrollTo(0, y); return; } if (VIEW === "tipp") {'),
    ("    ]).then(() => {\n      if (BACK || ARTIKEL || GAME) return;",
     "    ]).then(() => {\n      if (ARTIKEL && !BACK && !GAME && VIEW === \"meldungen\" && SS) { const y = window.scrollY; article(ARTIKEL); window.scrollTo(0, y); return; }\n      if (BACK || ARTIKEL || GAME) return;"),
]


def einbau(s, name):
    if MARK in s:
        sys.exit(f"{name}: schon eingebaut")
    ticker = "function article(" in s
    a, b = s.find("  function tippschein(){"), s.find("  function gefragtZeile(){")
    if a >= 0:
        if b < a:
            sys.exit(f"{name}: Ende von tippschein nicht gefunden")
        s = s[:a] + JS + s[b:]
    elif ticker:
        sys.exit(f"{name}: tippschein fehlt")
    if ".ts-vs{font-size:11px}" in s:
        if s.count(".ts-vs{font-size:11px}") != 1:
            sys.exit(f"{name}: CSS-Anker mehrfach")
        s = s.replace(".ts-vs{font-size:11px}", ".ts-vs{font-size:11px}\n" + CSS.rstrip())
    elif ticker:
        sys.exit(f"{name}: CSS-Anker fehlt")
    for alt, neu in ERS:
        n = s.count(alt)
        if n == 1:
            s = s.replace(alt, neu)
        elif ticker or n > 1:
            sys.exit(f"{name}: Anker {alt[:50]!r} {n}-mal")
    assert "—" not in s
    return s


if __name__ == "__main__":
    for f in sys.argv[1:]:
        p = pathlib.Path(f)
        p.write_text(einbau(p.read_text(encoding="utf-8"), f), encoding="utf-8")
        print("ok", f)
