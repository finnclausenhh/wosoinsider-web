"""Baut die Webseite wosoinsider.de (GitHub Pages) aus legal.json.

Aufruf: python3 bau.py <legal.json> <zielordner>
Rechtstexte kommen aus derselben legal.json wie in der App. Bei Änderungen erst
legal_bau.py anpassen, dann diese Seite neu bauen.
"""
import json, sys, os, shutil, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from legal_bau import to_html

ZAEHLER = "<script>\n" + open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "zaehler.js"), encoding="utf8").read() + "</script>"

MAIL = "redaktion@wosoinsider.de"

FONTS = """@font-face{font-family:'Barlow Condensed';font-weight:500;font-display:swap;src:url(/fonts/barlow-condensed-500-latin-ext.woff2) format('woff2');unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C4,U+2113,U+2C60-2C7F,U+A720-A7FF}
@font-face{font-family:'Barlow Condensed';font-weight:500;font-display:swap;src:url(/fonts/barlow-condensed-500-latin.woff2) format('woff2');unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}
@font-face{font-family:'Barlow Condensed';font-weight:700;font-display:swap;src:url(/fonts/barlow-condensed-latin-ext-2.woff2) format('woff2');unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C4,U+2113,U+2C60-2C7F,U+A720-A7FF}
@font-face{font-family:'Barlow Condensed';font-weight:700;font-display:swap;src:url(/fonts/barlow-condensed-latin-3.woff2) format('woff2');unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}
@font-face{font-family:'Barlow Condensed';font-weight:800;font-display:swap;src:url(/fonts/barlow-condensed-latin-ext-4.woff2) format('woff2');unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C4,U+2113,U+2C60-2C7F,U+A720-A7FF}
@font-face{font-family:'Barlow Condensed';font-weight:800;font-display:swap;src:url(/fonts/barlow-condensed-latin-5.woff2) format('woff2');unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}
@font-face{font-family:'Inter';font-weight:400 700;font-display:swap;src:url(/fonts/inter-latin-ext.woff2) format('woff2');unicode-range:U+0100-02BA,U+02BD-02C5,U+02C7-02CC,U+02CE-02D7,U+02DD-02FF,U+0304,U+0308,U+0329,U+1D00-1DBF,U+1E00-1E9F,U+1EF2-1EFF,U+2020,U+20A0-20AB,U+20AD-20C4,U+2113,U+2C60-2C7F,U+A720-A7FF}
@font-face{font-family:'Inter';font-weight:400 700;font-display:swap;src:url(/fonts/inter-latin.woff2) format('woff2');unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}"""

CSS = """:root{--bg:#F4F5F7;--card:#fff;--ink:#0E1726;--muted:#596476;--line:#DCE1EA;--soft:#EEF1F6;--accent:#2F5BFF;--brand:#2F5BFF;
--d:"Barlow Condensed","Arial Narrow",Arial,sans-serif;--b:"Inter",system-ui,-apple-system,"Segoe UI",sans-serif;color-scheme:light}
@media (prefers-color-scheme:dark){:root{--bg:#0E1726;--card:#16223A;--ink:#F4F5F7;--muted:#A9B4C6;--line:#2A3954;--soft:#1C2A45;--accent:#6E9BFF;color-scheme:dark}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 var(--b)}
a{color:var(--accent)}
.wrap{max-width:760px;margin:0 auto;padding:0 16px}
header{background:var(--card);border-bottom:1px solid var(--line)}
header .wrap{display:flex;align-items:center;justify-content:space-between;gap:12px;padding-block:12px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:10px;text-decoration:none;color:var(--ink);font-family:var(--d);text-transform:uppercase;line-height:.82}
.tile{width:38px;height:38px;border-radius:9px;background:var(--brand);color:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;flex:none}
.tile b{font-weight:800;font-size:15px;letter-spacing:.5px}.tile i{font-style:normal;font-weight:500;font-size:9px;letter-spacing:.5px}
.word{font-size:28px;letter-spacing:1.5px}.word b{font-weight:800}.word i{font-style:normal;font-weight:500;color:var(--accent)}
nav.top{display:flex;gap:16px;font-size:14px}nav.top a{color:var(--muted);text-decoration:none}nav.top a:hover,nav.top a[aria-current]{color:var(--ink)}
main.wrap{padding-block:28px 40px}
.hero{display:grid;gap:14px;padding:8px 0 20px}
.kicker{font:600 12px var(--b);letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.hero h1{font-family:var(--d);font-weight:800;font-size:clamp(40px,9vw,64px);line-height:.95;margin:0;text-transform:uppercase;text-wrap:balance}
.hero h1 span{color:var(--accent)}
.lead{font-size:18px;max-width:58ch;margin:0}
.store{display:inline-flex;align-items:center;gap:10px;justify-self:start;background:var(--ink);color:var(--bg);border-radius:12px;padding:10px 16px;text-decoration:none;font-weight:600}
.store small{display:block;font-weight:400;font-size:12px;opacity:.75}
.store.soon{background:transparent;color:var(--ink);border:1.5px dashed var(--line)}
.feat{display:grid;gap:12px;margin:8px 0 24px}
@media (min-width:640px){.feat{grid-template-columns:repeat(3,1fr)}}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px;display:grid;gap:6px;align-content:start}
.card h2{font-family:var(--d);font-weight:700;font-size:22px;text-transform:uppercase;letter-spacing:.02em;margin:0}
.card p{margin:0;font-size:15px;color:var(--muted)}
.note{font-size:14px;color:var(--muted);max-width:65ch}
.doc{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;display:grid;gap:14px}
.doc h1{font-family:var(--d);font-weight:800;font-size:40px;line-height:1;margin:0;text-transform:uppercase}
.doc h2{font-family:var(--d);font-weight:700;font-size:20px;letter-spacing:.02em;text-transform:uppercase;margin:8px 0 -6px}
.doc p,.doc ul{margin:0;max-width:68ch}.doc ul{padding-left:20px;display:grid;gap:4px}
.doc address{font-style:normal}
.mailbox{display:flex;flex-wrap:wrap;align-items:center;gap:10px 16px;background:var(--soft);border-radius:12px;padding:14px 16px}
.mailbox a{font-weight:600;font-size:18px;overflow-wrap:anywhere}
details{border-top:1px solid var(--line);padding:10px 0}details:last-of-type{border-bottom:1px solid var(--line)}
summary{cursor:pointer;font-weight:600}details p{margin:8px 0 0}
footer{border-top:1px solid var(--line);color:var(--muted);font-size:13px}
footer .wrap{display:grid;gap:8px;padding-block:18px 32px}
footer nav{display:flex;flex-wrap:wrap;gap:4px 18px}footer nav a{color:var(--muted)}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px}"""

NAV = [("/", "Start"), ("/support/", "Support"), ("/impressum/", "Impressum"), ("/datenschutz/", "Datenschutz")]

def page(path, title, desc, body):
    nav = "".join(f'<a href="{h}"{" aria-current=\"page\"" if h == path else ""}>{t}</a>' for h, t in NAV[1:])
    foot = "".join(f'<a href="{h}">{t}</a>' for h, t in NAV + [("/ki-hinweis/", "KI-Hinweis &amp; Methodik")])
    full = "WOSOINSIDER" if path == "/" else f"{title} · WOSOINSIDER"
    return f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{full}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<style>
{FONTS}
{CSS}
</style>
{ZAEHLER}
</head>
<body>
<header><div class="wrap"><a class="brand" href="/" aria-label="WOSOINSIDER Startseite"><span class="tile" aria-hidden="true"><b>WOSO</b><i>INSIDER</i></span><span class="word" aria-hidden="true"><b>WOSO</b><i>INSIDER</i></span></a><nav class="top" aria-label="Hauptmenü">{nav}</nav></div></header>
<main class="wrap">
{body}
</main>
<footer><div class="wrap"><nav aria-label="Rechtliches">{foot}</nav>
<span>WOSOINSIDER ist ein unabhängiges Angebot und nicht mit Kickbase, dem DFB oder den Vereinen verbunden. Inhalte werden mit KI erstellt.</span></div></footer>
</body>
</html>
"""

START = f"""<section class="hero">
  <span class="kicker">Frauen-Bundesliga · Kickbase</span>
  <h1>Alles, was deine <span>Aufstellung</span> wissen muss.</h1>
  <p class="lead">WOSOINSIDER sammelt jeden Tag die Meldungen zur Google Pixel Frauen-Bundesliga: Verletzungen, Sperren, Rückkehrerinnen und mögliche Aufstellungen. Kurz zusammengefasst, mit Quelle und mit einer Einordnung für Kickbase.</p>
  <span class="store soon" aria-label="Die iOS-App erscheint bald im App Store">Bald im App Store<small>für iPhone, kostenlos</small></span>
</section>
<section class="feat" aria-label="Was die App bietet">
  <div class="card"><h2>News</h2><p>Mehrmals täglich, an Spieltagen stündlich. Jede Meldung nennt und verlinkt ihre Quelle.</p></div>
  <div class="card"><h2>Spielplan</h2><p>Ergebnisse, Tore und mögliche Aufstellungen mit Einstufung von Sicher bis Unsicher. Die offizielle Elf ersetzt die Prognose.</p></div>
  <div class="card"><h2>Inside</h2><p>Einmal pro Woche: Formkurven, Standardschützinnen, Belastung und die Spiele mit Ansage.</p></div>
</section>
<p class="note">Kein Konto, keine Cookies, kein Tracking, keine Werbung. Fragen, Hinweise oder Korrekturen an <a href="mailto:{MAIL}">{MAIL}</a>.</p>"""

FAQ = [
    ("Was kostet WOSOINSIDER?", "Nichts. Die App ist kostenlos, ohne Werbung und ohne Abo."),
    ("Brauche ich ein Konto?", "Nein. Die App funktioniert ohne Anmeldung. Ihre Vereinsauswahl bleibt nur auf Ihrem Gerät."),
    ("Wie aktuell sind die Meldungen?", "Neue Meldungen kommen mehrmals täglich, an Spieltagen stündlich. Offizielle Aufstellungen erscheinen etwa 60 Minuten vor Anpfiff."),
    ("Woher kommen die Inhalte?", "Aus öffentlich zugänglichen Quellen wie Vereinsseiten, DFB, Sportschau und regionalen Medien. Ein KI-System fasst sie zusammen, jede Meldung verlinkt ihre Quelle. Mehr dazu unter <a href=\"/ki-hinweis/\">KI-Hinweis &amp; Methodik</a>."),
    ("Ist WOSOINSIDER ein Angebot von Kickbase?", "Nein. WOSOINSIDER ist unabhängig und nicht mit Kickbase, dem DFB oder den Vereinen verbunden."),
    ("Die App zeigt keine neuen Inhalte. Was tun?", "Prüfen Sie die Internetverbindung und öffnen Sie die App neu. Hilft das nicht, schreiben Sie uns mit Gerät und iOS-Version."),
]

def support():
    faq = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in FAQ)
    return f"""<article class="doc">
  <h1>Support</h1>
  <p>Fragen zur App, ein Fehler in einer Meldung oder ein Wunsch für eine neue Funktion? Eine Adresse für alles:</p>
  <div class="mailbox"><a href="mailto:{MAIL}">{MAIL}</a></div>
  <ul>
    <li>Fragen zu WOSOINSIDER und Wünsche für neue Funktionen</li>
    <li>Fehler in einer Meldung oder Aufstellung, neue Informationen zu Verletzungen, Sperren oder Rückkehr, bitte mit Link zur Quelle</li>
    <li>Auskunft, Berichtigung oder Löschung personenbezogener Daten sowie Fragen zu Bild- und Markenrechten</li>
  </ul>
  <h2>Häufige Fragen</h2>
  <div>{faq}</div>
  <p class="note">Die Postanschrift steht im <a href="/impressum/">Impressum</a>.</p>
</article>"""

NOTFOUND = """<article class="doc"><h1>Seite nicht gefunden</h1><p>Diese Adresse gibt es nicht (mehr). Zurück zur <a href="/">Startseite</a> oder zum <a href="/support/">Support</a>.</p></article>"""

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#2F5BFF"/><text x="32" y="33" text-anchor="middle" font-family="'Barlow Condensed','Arial Narrow',Arial,sans-serif" font-weight="800" font-size="25" fill="#fff">WOSO</text><text x="32" y="47" text-anchor="middle" font-family="'Barlow Condensed','Arial Narrow',Arial,sans-serif" font-weight="600" font-size="11.5" letter-spacing=".5" fill="#fff">INSIDER</text></svg>"""

def main(legal_path, out):
    L = json.load(open(legal_path, encoding="utf8"))
    doc = lambda k: f'<article class="doc">\n      {to_html(L[k]["titel"], L[k]["bloecke"])}\n</article>'
    imp = doc("impressum").replace("KI-Hinweis &amp; Methodik", '<a href="/ki-hinweis/">KI-Hinweis &amp; Methodik</a>')
    ki = doc("so-entsteht")
    pages = {
        "index.html": page("/", "Start", "News, mögliche Aufstellungen und Analysen zur Frauen-Bundesliga für Kickbase.", START),
        "support/index.html": page("/support/", "Support", "Kontakt und Hilfe zur App WOSOINSIDER.", support()),
        "impressum/index.html": page("/impressum/", "Impressum", "Impressum von WOSOINSIDER.", imp),
        "datenschutz/index.html": page("/datenschutz/", "Datenschutz", "Datenschutzerklärung für App und Webseite WOSOINSIDER.", doc("datenschutz")),
        "ki-hinweis/index.html": page("/ki-hinweis/", "KI-Hinweis & Methodik", "Wie WOSOINSIDER mit KI entsteht.", ki),
        "kontakt/index.html": page("/support/", "Kontakt", "Kontakt zu WOSOINSIDER.", support()),
        "404.html": page("", "Nicht gefunden", "Seite nicht gefunden.", NOTFOUND),
    }
    for rel, html in pages.items():
        assert "–" not in html and "—" not in html, rel
        assert "kontakt@" not in html and "datenschutz@" not in html, rel
        f = os.path.join(out, rel); os.makedirs(os.path.dirname(f), exist_ok=True)
        open(f, "w", encoding="utf8").write(html)
    open(os.path.join(out, "favicon.svg"), "w").write(FAVICON)
    open(os.path.join(out, "CNAME"), "w").write("wosoinsider.de\n")
    open(os.path.join(out, ".nojekyll"), "w").write("")
    open(os.path.join(out, "robots.txt"), "w").write("User-agent: *\nAllow: /\n")
    print("ok", sorted(pages))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
