# wosoinsider.de

Webseite zur App WOSOINSIDER (GitHub Pages, eigene Domain wosoinsider.de).

- Start, Support, Impressum, Datenschutz, KI-Hinweis
- Rechtstexte kommen aus derselben Quelle wie `legal.json` der App (`tools/legal_bau.py`).
- Neu bauen: `python3 tools/legal_bau.py` für legal.json, dann `python3 tools/bau.py <legal.json> .`
- /ticker/: Webversion des Newstickers. Gebaut mit `python3 tools/ticker_bau.py <index.html aus dem Artifact> ticker/index.html`; Daten kommen live aus fbl-daten. Nach jeder Änderung an der index.html im Artifact neu bauen. Bis zum Launch noindex und nicht verlinkt.
- Keine Cookies, kein Tracking, keine externen Schriften.
