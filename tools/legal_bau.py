#!/usr/bin/env python3
"""Erzeugt die Rechtstexte für WOSOINSIDER aus einer Quelle:
- legal.json für die iOS-App (Format: {key: {titel, bloecke:[{typ:h2|p|li, text}]}})
- HTML-Bausteine für die Webversion (index.html, Objekt LEGAL)
Stand: 28.10.2026 (Datenschutzerklärung nach Teil A des Claude Docs, ergänzt um GoatCounter, Umfragen und Kommentare)."""
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
    li("Spielerinnenfotos: Wikimedia Commons unter freien Lizenzen (CC BY, CC BY-SA, CC0). Urheberin oder Urheber und Lizenz stehen im jeweiligen Artikel. Vereinsportraits der Spielerinnen und Funktionsteams mit Genehmigung der jeweiligen Vereine."),
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
    p("**Kurz gesagt:** WOSOINSIDER braucht kein Konto, setzt keine Cookies und zeigt keine Werbung. Die App enthält keine Analyse. Webseite und Webversion zählen Aufrufe anonym mit GoatCounter, ohne Cookies und ohne Speicherung von IP-Adressen. Stimmen Sie in einer Umfrage ab, wird nur die gewählte Antwort gezählt, in App und Web (Abschnitt 6). Wer kommentiert, bekommt ein Profil ohne E-Mail-Adresse (Abschnitt 7). Personenbezogene Daten fallen sonst nur dort an, wo Technik es zwingend verlangt (Abruf der Inhalte) oder wenn Sie uns schreiben."),
    h2("1. Geltungsbereich"),
    p("Diese Erklärung gilt für die iOS-App WOSOINSIDER, die Webseite wosoinsider.de, die Webversion des Newstickers und den E-Mail-Kontakt."),
    h2("2. Verantwortlicher"),
    p(ANSCHRIFT),
    p(f"E-Mail: {ML}"),
    p("Eine Datenschutzbeauftragte oder einen Datenschutzbeauftragten müssen wir nicht benennen."),
    h2("3. Die App"),
    p("Die App lädt ihre Inhalte (Meldungen, Spielplan, Inside, Fotos, Logos) als Dateien von einem Server bei GitHub und speichert sie für schnelleres Laden im Zwischenspeicher Ihres Geräts. Beim Abruf übermittelt Ihr Gerät technisch notwendig seine IP-Adresse, Datum und Uhrzeit sowie die abgerufene Datei. Was GitHub damit macht, steht in Abschnitt 5. Wir selbst erhalten diese Daten nicht."),
    p("Die App enthält keine Analyse-, Werbe- oder Tracking-Werkzeuge. Software von Drittanbietern nutzt sie nur für die Kommentare (Programmbibliothek von Supabase, Abschnitt 7). Stimmen Sie in einer Umfrage ab, sendet die App nur die gewählte Antwort zur Zählung an GoatCounter (Abschnitt 6). Sie fragt keine Berechtigungen ab, etwa für Standort, Kontakte, Fotos oder Kamera. Links zu Quellen, Lizenzen oder Instagram öffnet sie erst, wenn Sie darauf tippen (siehe Abschnitt 11). Rechtsgrundlage für den Abruf ist unser berechtigtes Interesse, Ihnen die Inhalte auszuliefern (Art. 6 Abs. 1 lit. f DSGVO)."),
    p("Push-Mitteilungen bietet die App derzeit nicht an. Kommen sie dazu, ergänzen wir diese Erklärung vorher."),
    h2("4. Speicherung auf Ihrem Gerät"),
    p("Ihre Vereinsauswahl und Ihre Stimmen in Umfragen speichern App und Webversion lokal auf Ihrem Gerät (App: Einstellungen der App, Webversion: localStorage des Browsers), damit Sie Ihre Auswahl behalten und jede Umfrage nur einmal beantworten. Die Vereinsauswahl wird nicht übertragen; wie eine Stimme gezählt wird, steht in Abschnitt 6. Diese Speicherung ist für die von Ihnen gewünschte Funktion unbedingt erforderlich und braucht daher keine Einwilligung (§ 25 Abs. 2 Nr. 2 TDDDG). Sie löschen sie, indem Sie die Auswahl zurücksetzen, die App löschen oder die Browserdaten entfernen. Kommentieren Sie, speichern App und Webversion zusätzlich einen Sitzungsschlüssel (App: Schlüsselbund des Geräts, Webversion: Eintrag „woso-konto“ im Browser), damit Ihr Kommentar-Profil erhalten bleibt, und gegebenenfalls die Liste der Personen, die Sie stummgeschaltet haben (Eintrag „woso-stumm“, wird nicht übertragen). Es werden keine Cookies gesetzt."),
    h2("5. Webseite und Datenabruf über GitHub Pages"),
    p("Die Webseite wosoinsider.de und die Dateien für die App liegen bei GitHub Pages, einem Dienst der GitHub, Inc., 88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, USA. Beim Aufruf verarbeitet GitHub technisch notwendige Verbindungsdaten: IP-Adresse, Datum und Uhrzeit, abgerufene Datei, Browser oder App-Kennung, Betriebssystem und gegebenenfalls die zuvor besuchte Seite. Das dient der sicheren und stabilen Auslieferung (Art. 6 Abs. 1 lit. f DSGVO). Wie lange GitHub diese Daten speichert, legt GitHub selbst fest. Wir erhalten keine Logfiles und können keine Nutzerinnen oder Nutzer identifizieren."),
    p("GitHub verarbeitet Daten auch in den USA. GitHub ist nach dem EU-U.S. Data Privacy Framework zertifiziert, für das ein Angemessenheitsbeschluss der EU-Kommission besteht (Art. 45 DSGVO). Weitere Informationen: [Datenschutzerklärung von GitHub](https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement)."),
    p("Die Schriften werden zusammen mit der Seite ausgeliefert. Es besteht keine Verbindung zu Google Fonts oder anderen Schriftanbietern."),
    h2("6. Reichweitenmessung und Umfragen (GoatCounter)"),
    p("Die Webseite wosoinsider.de und die Webversion des Newstickers zählen Seitenaufrufe und das Öffnen von Meldungen, Spielen und Reitern sowie Stimmen in Umfragen (nur die gewählte Antwort) mit GoatCounter. Die App überträgt an GoatCounter ausschließlich Stimmen in Umfragen, keine Aufrufe. Anbieter ist Martin Tournoij, Irland ([goatcounter.com](https://www.goatcounter.com)). Dabei überträgt Ihr Browser oder die App die aufgerufene Seite, das geöffnete Element oder die gewählte Antwort, gegebenenfalls die zuvor besuchte Seite und Kampagnen-Angaben aus der Adresse (etwa „utm_source=instagram“), die Browser- und Betriebssystemkennung sowie technisch bedingt Ihre IP-Adresse."),
    p("GoatCounter speichert die IP-Adresse nicht. Daraus wird nur das Land abgeleitet. Zusammen mit der Browserkennung dient sie höchstens 8 Stunden im Arbeitsspeicher dazu, wiederholte Aufrufe nicht doppelt zu zählen. Gespeichert werden nur zusammengefasste Zahlen, mit denen sich keine Person erkennen lässt. GoatCounter setzt keine Cookies, es wird kein Skript eines Drittanbieters geladen, und GoatCounter speichert oder liest keine Informationen auf Ihrem Gerät. Die Server betreibt die Hetzner Online GmbH in Deutschland und Finnland."),
    p("Zweck ist zu erfahren, wie viele Menschen das Angebot nutzen und welche Themen, Spielerinnen und Vereine gefragt sind, sowie die Ergebnisse von Umfragen anzuzeigen. Rechtsgrundlage ist unser berechtigtes Interesse an dieser Auswertung (Art. 6 Abs. 1 lit. f DSGVO). Sie können jederzeit widersprechen (Abschnitt 13), zum Beispiel per E-Mail; technisch verhindern Sie die Zählung mit einem Inhaltsblocker. Weitere Informationen: [Datenschutzerklärung von GoatCounter](https://www.goatcounter.com/help/privacy)."),
    h2("7. Kommentare (Supabase)"),
    p("In der App und in der Webversion des Newstickers können Sie Meldungen kommentieren sowie Kommentare liken und melden. Lesen ist ohne Anmeldung möglich. Wenn Sie zum ersten Mal schreiben, liken oder melden, wird für Ihr Gerät beziehungsweise Ihren Browser ein pseudonymes Profil angelegt: eine zufällige Kennung und ein Name, den Sie beim ersten Kommentar selbst wählen (ohne Wahl ein Platzhalter wie „WoSo-Fan 1704“). Eine E-Mail-Adresse oder ein Konto ist dafür nicht nötig."),
    p("Verarbeitet werden die pseudonyme Kennung, der Name, Ihre Kommentare mit Zeitpunkt, Ihre Likes, Ihre Meldungen mit Grund, Moderationsentscheidungen und gegebenenfalls eine Sperre mit Begründung. Beim Abruf verarbeitet der Dienstleister technisch Ihre IP-Adresse und Angaben zum Browser oder zur App (Server-Protokolle). Kommentare und Name sind für alle sichtbar. Schreiben Sie bitte keine persönlichen Daten in Kommentare."),
    p("Zweck und Rechtsgrundlage: Bereitstellung der Kommentarfunktion, die Sie selbst nutzen (Art. 6 Abs. 1 lit. b DSGVO), Schutz vor Missbrauch und Spam sowie die Bearbeitung von Meldungen nach dem Digital Services Act (Art. 6 Abs. 1 lit. c und f DSGVO). Ein Wortfilter prüft Kommentare und Namen automatisch; zurückgehaltene oder gemeldete Kommentare prüft die Redaktion."),
    p("Dienstleister und Auftragsverarbeiter (Art. 28 DSGVO) ist die Supabase Pte. Ltd., 65 Chulia Street #38-02/03, OCBC Centre, Singapur 049513. Die Daten liegen in einem Rechenzentrum in Frankfurt am Main. Der Auftragsverarbeitungsvertrag ist Teil der Nutzungsbedingungen von Supabase; für Zugriffe aus Ländern außerhalb der EU (etwa Support aus Singapur oder den USA) gelten die EU-Standardvertragsklauseln. Weitere Informationen: [Datenschutzerklärung von Supabase](https://supabase.com/privacy)."),
    p(f"Speicherdauer: Kommentare, bis Sie sie löschen oder wir sie entfernen. Profile ohne jede Aktivität löschen wir nach 30 Tagen automatisch. Erledigte Meldungen löschen wir nach 6 Monaten, das Moderationsprotokoll nach 12 Monaten. Eigene Kommentare können Sie jederzeit selbst löschen. Für die Löschung Ihres Profils oder Auskunft schreiben Sie an {ML} und nennen Ihren Namen in den Kommentaren. Die Kommentarregeln stehen unter dem Eingabefeld; rechtswidrige Inhalte melden Sie über „Melden“ oder per E-Mail."),
    h2("8. Keine Werbeprofile, keine automatisierten Entscheidungen"),
    p("Wir bilden keine Nutzerprofile zu Werbe- oder Analysezwecken und verkaufen oder teilen keine Daten. Das Kommentar-Profil (Abschnitt 7) dient nur der Kommentarfunktion. Eine automatisierte Entscheidungsfindung nach Art. 22 DSGVO findet nicht statt."),
    h2("9. App Store"),
    p("Die App laden Sie über den App Store von Apple. Dafür verarbeitet Apple Daten wie Ihre Apple-ID, Gerätekennung und Kaufhistorie in eigener Verantwortung. Wir haben darauf keinen Einfluss und erhalten keine personenbezogenen Daten von Apple. Haben Sie in den iOS-Einstellungen zugestimmt, Analysedaten mit App-Entwicklern zu teilen, stellt Apple uns anonymisierte Absturzberichte und Nutzungsstatistiken bereit. Einzelheiten stehen in der [Datenschutzrichtlinie von Apple](https://www.apple.com/de/legal/privacy/)."),
    h2("10. Kontakt per E-Mail"),
    p(f"Wenn Sie an {ML} schreiben, verarbeiten wir Ihre E-Mail-Adresse, Ihren Namen (falls angegeben) und Ihre Nachricht, um die Anfrage zu bearbeiten (Art. 6 Abs. 1 lit. b oder f DSGVO). Hinweise an die Redaktion nutzen wir für die Berichterstattung. Ihren Namen veröffentlichen wir nur mit Ihrer Zustimmung. Die Daten löschen wir, sobald die Anfrage erledigt ist und keine Aufbewahrungspflicht besteht."),
    p("Das Postfach läuft über Google Workspace. Vertragspartner und Auftragsverarbeiter (Art. 28 DSGVO) ist die Google Cloud EMEA Limited, 70 Sir John Rogerson's Quay, Dublin 2, Irland. Google kann Daten auch in den USA verarbeiten. Die Google LLC ist nach dem EU-U.S. Data Privacy Framework zertifiziert, für das ein Angemessenheitsbeschluss der EU-Kommission besteht (Art. 45 DSGVO)."),
    h2("11. Links zu anderen Seiten"),
    p("Quellen, die Sportschau und Instagram-Profile sind verlinkt. Daten werden erst übertragen, wenn Sie einen Link antippen. Dann gilt die Datenschutzerklärung der jeweiligen Seite."),
    h2("12. Berichterstattung über Spielerinnen"),
    p("Meldungen nennen Spielerinnen, Trainerinnen und Trainer im Rahmen der Sportberichterstattung (journalistische Zwecke, Art. 85 DSGVO in Verbindung mit § 23 MStV). Die redaktionelle Verantwortung trägt Finn Clausen."),
    p("Für Angaben zur Gesundheit gelten feste Regeln: Wir berichten nur, was Verein, Verband oder Medien bereits veröffentlicht haben, und nur so genau, wie es für die Frage nötig ist, ob und wann eine Spielerin spielen kann. Eigene Vermutungen zu Diagnosen veröffentlichen wir nicht. Meldungen werden nach 14 Tagen aus der App entfernt."),
    p(f"Fotos stammen von Wikimedia Commons unter freien Lizenzen oder werden mit Genehmigung genutzt. Betroffene können jederzeit unter {ML} eine Korrektur, die Entfernung eines Fotos oder einer Angabe verlangen. Berechtigte Anliegen setzen wir unverzüglich um."),
    h2("13. Ihre Rechte"),
    p(f"Sie haben das Recht auf Auskunft (Art. 15), Berichtigung (Art. 16), Löschung (Art. 17), Einschränkung der Verarbeitung (Art. 18) und Datenübertragbarkeit (Art. 20 DSGVO). Eine Nachricht an {ML} genügt."),
    p("**Widerspruchsrecht:** Verarbeiten wir Daten auf Grundlage berechtigter Interessen (Art. 6 Abs. 1 lit. f DSGVO), können Sie aus Gründen, die sich aus Ihrer besonderen Situation ergeben, jederzeit widersprechen (Art. 21 DSGVO). Wir verarbeiten die Daten dann nicht mehr, es sei denn, es liegen zwingende schutzwürdige Gründe vor."),
    h2("14. Beschwerderecht"),
    p("Sie können sich bei einer Datenschutz-Aufsichtsbehörde beschweren. Zuständig für uns ist das Bayerische Landesamt für Datenschutzaufsicht (BayLDA), Promenade 18, 91522 Ansbach."),
    h2("15. Stand"),
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
