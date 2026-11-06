#!/usr/bin/env python3
"""Live, Runde 6 (Finn 06.11.2026): raw.githubusercontent.com liefert live.json trotz ?t= bis zu 5 Minuten alt aus.
live.json kommt jetzt zuerst über die GitHub-API (max-age 60, mit ETag; 304 zählt nicht gegen das Limit von 60/h je IP),
bei Fehler (z. B. Limit) weiter über raw. Auf den Stand nach tools/live5_patch.py. Jede Ersetzung genau einmal.
Aufruf: python3 tools/live6_patch.py <index.html>
"""
import sys

ERS = [
    ("""    return fetch(LIVE_URL + "?t=" + Date.now(), {cache: "no-store"}).then(r => r.ok ? r.json() : null).then(l => {""",
     """    return fetch(LIVE_API, {cache: "no-cache", headers: {Accept: "application/vnd.github.raw+json"}}).then(r => r.ok ? r.json() : Promise.reject(r.status))
      .catch(() => fetch(LIVE_URL + "?t=" + Date.now(), {cache: "no-store"}).then(r => r.ok ? r.json() : null)).then(l => {"""),
    ("""  let LIVE = null;""",
     """  const LIVE_API = "https://api.github.com/repos/finnclausenhh/fbl-daten/contents/live.json?ref=main";
  let LIVE = null;"""),
]


def main(pfad):
    s = open(pfad, encoding="utf-8").read()
    for alt, neu in ERS:
        n = s.count(alt)
        if n != 1:
            sys.exit(f"passt {n}-mal: {alt[:80]!r}")
        s = s.replace(alt, neu)
    open(pfad, "w", encoding="utf-8").write(s)
    print("ok", pfad)


if __name__ == "__main__":
    main(sys.argv[1])
