#!/usr/bin/env python3
"""Erzeugt die Rechtstexte für WOSOINSIDER aus einer Quelle:
- legal.json für die iOS-App (Format: {key: {titel, bloecke:[{typ:h2|p|li, text}]}})
- HTML-Bausteine für die Webversion (index.html, Objekt LEGAL)
Stand: 27.10.2026 (Datenschutzerklärung nach Teil A des Claude Docs, ergänzt um GoatCounter)."""
import json, re, sys

MAIL = "redaktion@wosoinsider.de"
ML = f"[{MAIL}](mailto:{MAIL})"
ANSCHRIFT = "Finn Clausen\nWOSOINSIDER\nWiesenweg 14\n83083 Riedering\nDeutschland"

def h2(t): return {"typ": "h2", "text": t}
def p(t): return {"typ": "p", "text": t}
def li(t): return {"typ": "li", "text": t}

IMPRESSUM = [
    h2("Angaben gemäß § 5 DDG"), p(ANSCHRIFT),
    h2("Kontakt"),
    p(f"E-Mail: {ML}"),
    p("Über diese Adresse erreichen Sie uns für alle Anliegen, auch für Hinweise, Korrekturen und Datenschutz."),
    h2("Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV"),
    p("Finn Clausen, Anschrift wie oben."),
    h2("Einsatz von KI"),
    p("Meldungen und mögliche Aufstellungen werden automatisiert mit einem KI-System erstellt und als solche gekennzeichnet. Die redaktionelle Verantwortung trägt Finn Clausen. Einzelheiten stehen unter KI-Hinweis & Methodik."),
    h2("Unabhängigkeit"),
    p("WOSOINSIDER ist ein unabhängiges Angebot. Es besteht keine Verbindung zu Kickbase, zum DFB, zur Google Pixel Frauen-Bundesliga oder zu den Vereinen. Genannte Marken und Namen gehören ihren jeweiligen Inhabern."),
    h2("Bild- und Datennachweise"),
    li("Spielerinnenfotos: Wikimedia Commons unter freien Lizenzen (CC BY, CC BY-SA, CC0). Urheberin oder Urheber und Lizenz stehen im jeweiligen Artikel."),
    li("Vereinslogos: mit Genehmigung der jeweiligen Vereine."),
    li("Spielplan, Ergebnisse, Tore und offizielle Aufstellungen: Sportschau (ARD), verlinkt an der jeweiligen Partie."),
    li("Meldungen: zusammengefasst aus den im Artikel verlinkten Quellen."),
    h2("Haftung für Inhalte"),
    p("Die Inhalte werden mit Sorgfalt erstellt, aber automatisiert und ohne Prüfung jeder einzelnen Meldung vor der Veröffentlichung. Für Richtigkeit, Vollständigkeit und Aktualität, insbesondere von Prognosen, wird keine Gewähr übernommen. Nach §§ 8 bis 10 DDG sind wir nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen. Sobald uns eine Rechtsverletzung bekannt wird, entfernen wir den Inhalt umgehend."),
    h2("Haftung für Links"),
    p("Für die Inhalte verlinkter fremder Seiten sind ausschließlich deren Betreiber verantwortlich. Zum Zeitpunkt der Verlinkung waren keine Rechtsverstöße erkennbar. Bei Bekanntwerden entfernen wir solche Links umgehend."),
    h2("Verbraucherstreitbeilegung"),
    p("Wir sind nicht bereit und nicht verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen."),
]

DATENSCHUTZ = [
    p("**Kurz gesagt:** WOSOINSIDER braucht kein Konto, setzt keine Cookies und zeigt keine Werbung. Die App enthält keine Analyse. Webseite und Webversion zählen Aufrufe anonym mit GoatCounter, ohne Cookies und ohne Speicherung von IP-Adressen (Abschnitt 6). Personenbezogene Daten fallen sonst nur dort an, wo Technik es zwingend verlangt (Abruf der Inhalte) oder wenn Sie uns schreiben."),
    h2("1. Geltungsbereich"),
    p("Diese Erklärung gilt für die iOS-App WOSOINSIDER, die Webseite wosoinsider.de, die Webversion des Newstickers und den E-Mail-Kontakt."),
    h2("2. Verantwortlicher"),
    p(ANSCHRIFT),
    p(f"E-Mail: {ML}"),
    p("Eine Datenschutzbeauftragte oder einen Datenschutzbeauftragten müssen wir nicht benennen."),
    h2("3. Die App"),
    p("Die App lädt ihre Inhalte (Meldungen, Spielplan, Inside, Fotos, Logos) als Dateien von einem Server bei GitHub und speichert sie für schnelleres Laden im Zwischenspeicher Ihres Geräts. Beim Abruf übermittelt Ihr Gerät technisch notwendig seine IP-Adresse, Datum und Uhrzeit sowie die abgerufene Datei. Was GitHub damit macht, steht in Abschnitt 5. Wir selbst erhalten diese Daten nicht."),
    p("Die App enthält keine Analyse-, Werbe- oder Tracking-Werkzeuge und keine Software von Drittanbietern. Sie fragt keine Berechtigungen ab, etwa für Standort, Kontakte, Fotos oder Kamera. Links zu Quellen, Lizenzen oder Instagram öffnet sie erst, wenn Sie darauf tippen (siehe Abschnitt 10). Rechtsgrundlage für den Abruf ist unser berechtigtes Interesse, Ihnen die Inhalte auszuliefern (Art. 6 Abs. 1 lit. f DSGVO)."),
    p("Push-Mitteilungen bietet die App derzeit nicht an. Kommen sie dazu, ergänzen wir diese Erklärung vorher."),
    h2("4. Speicherung auf Ihrem Gerät"),
    p("Ihre Vereinsauswahl speichern App und Webversion nur lokal auf Ihrem Gerät (App: Einstellungen der App, Webversion: localStorage des Browsers). Sie wird nicht an uns übertragen. Diese Speicherung ist für die von Ihnen gewünschte Funktion unbedingt erforderlich und braucht daher keine Einwilligung (§ 25 Abs. 2 Nr. 2 TDDDG). Sie löschen sie, indem Sie die Auswahl zurücksetzen, die App löschen oder die Browserdaten entfernen. Es werden keine Cookies gesetzt."),
    h2("5. Webseite und Datenabruf über GitHub Pages"),
    p("Die Webseite wosoinsider.de und die Dateien für die App liegen bei GitHub Pages, einem Dienst der GitHub, Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, USA. Beim Aufruf verarbeitet GitHub technisch notwendige Verbindungsdaten: IP-Adresse, Datum und Uhrzeit, abgerufene Datei, Browser oder App-Kennung, Betriebssystem und gegebenenfalls die zuvor besuchte Seite. Das dient der sicheren und stabilen Auslieferung (Art. 6 Abs. 1 lit. f DSGVO). Wie lange GitHub diese Daten speichert, legt GitHub selbst fest. Wir erhalten keine Logfiles und können keine Nutzerinnen oder Nutzer identifizieren."),
    p("GitHub verarbeitet Daten auch in den USA. GitHub ist nach dem EU-U.S. Data Privacy Framework zertifiziert, für das ein Angemessenheitsbeschluss der EU-Kommission besteht (Art. 45 DSGVO). Weitere Informationen: [Datenschutzerklärung von GitHub](https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement)."),
    p("Die Schriften werden zusammen mit der Seite ausgeliefert. Es besteht keine Verbindung zu Google Fonts oder anderen Schriftanbietern."),
    h2("6. Reichweitenmessung auf der Webseite (GoatCounter)"),
    p("Die Webseite wosoinsider.de und die Webversion des Newstickers zählen Seitenaufrufe und das Öffnen von Meldungen, Spielen und Reitern mit GoatCounter. Anbieter ist Martin Tournoij, Irland ([goatcounter.com](https://www.goatcounter.com)). Dabei überträgt Ihr Browser die aufgerufene Seite oder das geöffnete Element, gegebenenfalls die zuvor besuchte Seite und Kampagnen-Angaben aus der Adresse (etwa „utm_source=instagram“), die Browser- und Betriebssystemkennung sowie technisch bedingt Ihre IP-Adresse."),
    p("GoatCounter speichert die IP-Adresse nicht. Daraus wird nur das Land abgeleitet. Zusammen mit der Browserkennung dient sie höchstens 8 Stunden im Arbeitsspeicher dazu, wiederholte Aufrufe nicht doppelt zu zählen. Gespeichert werden nur zusammengefasste Zahlen, mit denen sich keine Person erkennen lässt. Es werden keine Cookies gesetzt, kein Skript eines Drittanbieters geladen und keine Informationen auf Ihrem Gerät gespeichert oder ausgelesen. Die Server betreibt die Hetzner Online GmbH in Deutschland und Finnland."),
    p("Zweck ist zu erfahren, wie viele Menschen das Angebot nutzen und welche Themen, Spielerinnen und Vereine gefragt sind. Rechtsgrundlage ist unser berechtigtes Interesse an dieser Auswertung (Art. 6 Abs. 1 lit. f DSGVO). Sie können jederzeit widersprechen (Abschnitt 12), zum Beispiel per E-Mail; technisch verhindern Sie die Zählung mit einem Inhaltsblocker. Die App nutzt GoatCounter nicht. Weitere Informationen: [Datenschutzerklärung von GoatCounter](https://www.goatcounter.com/help/privacy)."),
    h2("7. Keine Profile, keine automatisierten Entscheidungen"),
    p("Wir bilden keine Nutzerprofile und verkaufen oder teilen keine Daten. Eine automatisierte Entscheidungsfindung nach Art. 22 DSGVO findet nicht statt."),
    h2("8. App Store"),
    p("Die App laden Sie über den App Store von Apple. Dafür verarbeitet Apple Daten wie Ihre Apple-ID, Gerätekennung und Kaufhistorie in eigener Verantwortung. Wir haben darauf keinen Einfluss und erhalten keine personenbezogenen Daten von Apple. Haben Sie in den iOS-Einstellungen zugestimmt, Analysedaten mit App-Entwicklern zu teilen, stellt Apple uns anonymisierte Absturzberichte und Nutzungsstatistiken bereit. Einzelheiten stehen in der [Datenschutzrichtlinie von Apple](https://www.apple.com/de/legal/privacy/)."),
    h2("9. Kontakt per E-Mail"),
    p(f"Wenn Sie an {ML} schreiben, verarbeiten wir Ihre E-Mail-Adresse, Ihren Namen (falls angegeben) und Ihre Nachricht, um die Anfrage zu bearbeiten (Art. 6 Abs. 1 lit. b oder f DSGVO). Hinweise an die Redaktion nutzen wir für die Berichterstattung. Ihren Namen veröffentlichen wir nur mit Ihrer Zustimmung. Die Daten löschen wir, sobald die Anfrage erledigt ist und keine Aufbewahrungspflicht besteht."),
    p("Das Postfach läuft über Google Workspace. Vertragspartner und Auftragsverarbeiter (Art. 28 DSGVO) ist die Google Cloud EMEA Limited, 70 Sir John Rogerson's Quay, Dublin 2, Irland. Google kann Daten auch in den USA verarbeiten. Die Google LLC ist nach dem EU-U.S. Data Privacy Framework zertifiziert, für das ein Angemessenheitsbeschluss der EU-Kommission besteht (Art. 45 DSGVO)."),
    h2("10. Links zu anderen Seiten"),
    p("Quellen, die Sportschau und Instagram-Profile sind verlinkt. Daten werden erst übertragen, wenn Sie einen Link antippen. Dann gilt die Datenschutzerklärung der jeweiligen Seite."),
    h2("11. Berichterstattung über Spielerinnen"),
    p("Meldungen nennen Spielerinnen, Trainerinnen und Trainer im Rahmen der Sportberichterstattung (journalistische Zwecke, Art. 85 DSGVO in Verbindung mit § 23 MStV). Die redaktionelle Verantwortung trägt Finn Clausen."),
    p("Für Angaben zur Gesundheit gelten feste Regeln: Wir berichten nur, was Verein, Verband oder Medien bereits veröffentlicht haben, und nur so genau, wie es für die Frage nötig ist, ob und wann eine Spielerin spielen kann. Eigene Vermutungen zu Diagnosen veröffentlichen wir nicht. Meldungen werden nach 14 Tagen aus der App entfernt."),
    p(f"Fotos stammen von Wikimedia Commons unter freien Lizenzen oder werden mit Genehmigung genutzt. Betroffene können jederzeit unter {ML} eine Korrektur, die Entfernung eines Fotos oder einer Angabe verlangen. Berechtigte Anliegen setzen wir unverzüglich um."),
    h2("12. Ihre Rechte"),
    p(f"Sie haben das Recht auf Auskunft (Art. 15), Berichtigung (Art. 16), Löschung (Art. 17), Einschränkung der Verarbeitung (Art. 18) und Datenübertragbarkeit (Art. 20 DSGVO). Eine Nachricht an {ML} genügt."),
    p("**Widerspruchsrecht:** Verarbeiten wir Daten auf Grundlage berechtigter Interessen (Art. 6 Abs. 1 lit. f DSGVO), können Sie aus Gründen, die sich aus Ihrer besonderen Situation ergeben, jederzeit widersprechen (Art. 21 DSGVO). Wir verarbeiten die Daten dann nicht mehr, es sei denn, es liegen zwingende schutzwürdige Gründe vor."),
    h2("13. Beschwerderecht"),
    p("Sie können sich bei einer Datenschutz-Aufsichtsbehörde beschweren. Zuständig für uns ist das Bayerische Landesamt für Datenschutzaufsicht (BayLDA), Promenade 18, 91522 Ansbach."),
    h2("14. Stand"),
    p("Oktober 2026. Ändert sich etwas an App oder Webseite, passen wir diese Erklärung an."),
]

KONTAKT = [
    p(f"Eine Adresse für alles: {ML}"),
    li("Fragen zu WOSOINSIDER und Wünsche für neue Funktionen"),
    li("Fehler in einer Meldung oder Aufstellung, neue Informationen zu Verletzungen, Sperren oder Rückkehr, bitte mit Link zur Quelle"),
    li("Auskunft, Berichtigung oder Löschung personenbezogener Daten sowie Fragen zu Bild- und Markenrechten"),
    p("Die Postanschrift steht im Impressum."),
]

def md_to_html(t):
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    return t.replace("\n", "<br>")

def to_html(titel, bloecke):
    out, ul = [f"<h1>{titel}</h1>"], False
    for b in bloecke:
        if b["typ"] == "li":
            if not ul: out.append("<ul>"); ul = True
            out.append(f"<li>{md_to_html(b['text'])}</li>")
            continue
        if ul: out.append("</ul>"); ul = False
        tag = "h2" if b["typ"] == "h2" else "p"
        txt = md_to_html(b["text"])
        if b["typ"] == "p" and "\n" in b["text"] and "WOSOINSIDER" in b["text"].split("\n")[1:2]:
            out.append(f"<address>{txt}</address>"); continue
        out.append(f"<{tag}>{txt}</{tag}>")
    if ul: out.append("</ul>")
    return "\n      ".join(out)

def main(alt_json, out_json, out_html):
    legal = json.load(open(alt_json, encoding="utf-8"))
    legal["impressum"] = {"titel": "Impressum", "bloecke": IMPRESSUM}
    legal["datenschutz"] = {"titel": "Datenschutz", "bloecke": DATENSCHUTZ}
    legal["kontakt"] = {"titel": "Kontakt", "bloecke": KONTAKT}
    # so-entsteht bleibt unverändert
    json.dump(legal, open(out_json, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    html = {k: to_html(legal[k]["titel"], legal[k]["bloecke"]) for k in ("impressum", "datenschutz", "kontakt")}
    json.dump(html, open(out_html, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    text = json.dumps(legal, ensure_ascii=False)
    assert "–" not in text and "—" not in text, "Gedankenstrich gefunden"
    assert "kontakt@" not in text and "datenschutz@" not in text, "alte Adresse gefunden"
    print("ok", {k: len(v["bloecke"]) for k, v in legal.items()})

if __name__ == "__main__":
    main(*sys.argv[1:4])
