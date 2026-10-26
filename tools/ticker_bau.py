"""Baut die öffentliche Webversion wosoinsider.de/ticker/ aus der index.html des Artifacts.

Aufruf: python3 tools/ticker_bau.py <index.html aus dem Artifact> ticker/index.html

Die Daten (news.json, spielplan.json, inside.json, fotos.json, fotos/, logos/) kommen live aus
dem Repo fbl-daten (GitHub Pages), das der Spiegel-Lauf aktuell hält. Die Seite selbst ändert
sich nur, wenn sich die index.html im Artifact ändert: dann dieses Skript erneut ausführen.
"""
import sys, re

DATEN = "https://finnclausenhh.github.io/fbl-daten/"

HEAD = f"""<base href="{DATEN}">
<meta name="robots" content="noindex">
<meta name="description" content="News, Spielplan und Inside zur Frauen-Bundesliga für Kickbase.">
<link rel="icon" href="https://wosoinsider.de/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="https://wosoinsider.de/apple-touch-icon.png">
<script>
// Daten liegen auf einer anderen Adresse (base). Adresszeile trotzdem auf dieser Seite halten.
(function(){{ var r = history.replaceState.bind(history);
  history.replaceState = function(s, t, u){{ return r(s, t, u == null ? u : new URL(u, location.href).href); }}; }})();
</script>
"""

def main(src, out):
    s = open(src, encoding="utf8").read()
    s = s.replace('<html>', '<html lang="de">', 1)
    s = s.replace("url(fonts/", "url(https://wosoinsider.de/fonts/")
    i = s.index("<head>") + len("<head>")
    s = s[:i] + HEAD + s[i:]
    # Basis-Prüfungen
    assert s.count("<base ") == 1
    assert "url(fonts/" not in s
    for f in ["news.json", "spielplan.json", "inside.json", "fotos.json"]:
        assert f'"{f}"' in s, f
    assert "—" not in s
    open(out, "w", encoding="utf8").write(s)
    print("ok", len(s))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
