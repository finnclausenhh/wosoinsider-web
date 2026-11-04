# wosoinsider.de

Webseite zur App WOSOINSIDER (GitHub Pages, eigene Domain wosoinsider.de).

- Start, Support, Impressum, Datenschutz, KI-Hinweis. Kopfzeile nur mit Logo, alle Links stehen im Fuß.
- Startseite: sechs Karten verlinken in den Ticker (News, #spielplan, #inside, Spielbericht #bayern-pokal-0111, #analyse, #statistik) und zeigen Screenshots aus bilder/. Neue Beispiel-Partie oder Analyse: Hash in tools/screens.py und tools/bau.py anpassen. Erneuern mit `python3 tools/screens.py bilder`.
- Rechtstexte kommen aus derselben Quelle wie `legal.json` der App (`tools/legal_bau.py`).
- Neu bauen: `python3 tools/legal_bau.py <altes legal.json> <neues legal.json> <legal_html.json>`, dann `python3 tools/bau.py <legal.json> .`
- /ticker/: Webversion des Newstickers. Gebaut mit `python3 tools/ticker_bau.py <index.html aus dem Artifact> ticker/index.html`; Daten kommen live aus fbl-daten. Nach jeder Änderung an der index.html im Artifact neu bauen. Bis zum Launch noindex und nicht verlinkt.
- Keine Cookies, keine externen Schriften oder Skripte. Reichweite: GoatCounter-Zählpixel (tools/zaehler.js, im Ticker zusätzlich tools/zaehler_ticker.js), zählt nur auf wosoinsider.de. Auswertung: https://wosoinsider.goatcounter.com
- Ticker mit aktuellen Rechtstexten bauen: `python3 tools/ticker_bau.py <index.html> ticker/index.html <legal_html.json>` (legal_html.json = dritte Ausgabe von legal_bau.py).
- Gamification (Spielt sie?, Einsehbar, Prognose-Bilanz, Gefragt diese Woche) und Standard-Check mit Messlatte: live seit 04.11.2026. Quellen in tools/gami/, eingebaut mit `python3 tools/gami_einbau.py <index.html> <ausgabe>` (für Artifact und Ticker gleich; `--test` setzt den Testseiten-Hinweis). Nach einem Neubau aus dem Artifact ist der Einbau schon enthalten, wenn er dort gemacht wurde.
