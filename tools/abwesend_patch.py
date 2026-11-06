#!/usr/bin/env python3
"""Status "abwesend" wie bei Kickbase (Finn 06.11.2026, Tomasiak Trainingsrückstand).

Ausfälle ohne Verletzung (Trainingsrückstand, Belastungssteuerung, Schonung, Krankheit, persönliche Gründe) zeigen
ein eigenes Symbol: heller Kreis mit dunklem Viertel (wie Kickbase "Abwesend") statt des roten Verletzt-Kreuzes.
Meldungen: Tag ABWESEND oder status "abwesend". Profile und Kader: Status raus mit passendem Grund.
Aufruf: python3 tools/abwesend_patch.py ticker/index.html
"""
import sys

ERSETZUNGEN = [
    ('gesperrt:["verbot","#9B6BE8","gesperrt"]};',
     'gesperrt:["verbot","#9B6BE8","gesperrt"], abwesend:["uhr","#E6E8EC","abwesend"]};'),
    ('return t.includes("SPERRE") ? "gesperrt"',
     'return t.includes("ABWESEND") ? "abwesend" : t.includes("SPERRE") ? "gesperrt"'),
    ('<span class="plak${x[0] === "frage" ? " fr" : ""}"',
     '<span class="plak${x[0] === "frage" ? " fr" : x[0] === "uhr" ? " ab" : ""}"'),
    ("plus:'<path d=\"M12 5v14M5 12h14\"/>', ",
     "plus:'<path d=\"M12 5v14M5 12h14\"/>', uhr:'<path d=\"M12 12V0a12 12 0 0 1 12 12z\"/>', "),
    ('.plak.fr svg{width:80%;height:80%;stroke-width:3}',
     '.plak.fr svg{width:80%;height:80%;stroke-width:3}.plak.ab svg{width:100%;height:100%;fill:#15181D;stroke:none}'),
    ('baby:"#E58FB5", abgestellt:"#6E9BFF"};',
     'baby:"#E58FB5", abgestellt:"#6E9BFF", abwesend:"#C9CED6"};'),
    ('|Länderspiel|abgestellt/i.test(g)) return "abgestellt";\n    return st; };',
     '|Länderspiel|abgestellt/i.test(g)) return "abgestellt";\n'
     '    if (st === "raus" && /trainingsr(ü|ue)ckstand|belastung|schonung|geschont|krank|infekt|erk(ä|ae)ltung|grippe|pers(ö|oe)nlich|privat|famili(ä|ae)r|trauerfall|abwesend/i.test(g)) return "abwesend";\n'
     '    return st; };'),
    ('const STWORT = {raus: "verletzt", baby: "Babypause", abgestellt: "abgestellt",',
     'const STWORT = {raus: "verletzt", baby: "Babypause", abgestellt: "abgestellt", abwesend: "abwesend",'),
    ("sa === \"abgestellt\" ? '<span class=\"pf-tag abg\">ABGESTELLT</span>' :",
     "sa === \"abgestellt\" ? '<span class=\"pf-tag abg\">ABGESTELLT</span>' : sa === \"abwesend\" ? '<span class=\"pf-tag abw\">ABWESEND</span>' :"),
    ('.pf-tag.abg{background:rgba(110,155,255,.2);color:#B5CBFF}',
     '.pf-tag.abg{background:rgba(110,155,255,.2);color:#B5CBFF}.pf-tag.abw{background:rgba(201,206,214,.18);color:#E6E8EC}'),
    ('sa === "abgestellt" ? ["Abgestellt", kurzZurueck(s.status), STFARBE.abgestellt] :',
     'sa === "abgestellt" ? ["Abgestellt", kurzZurueck(s.status), STFARBE.abgestellt] : sa === "abwesend" ? ["Abwesend", kurzZurueck(s.status), STFARBE.abwesend] :'),
    ('stArt({s: v.status, grund: v.grund}) === "abgestellt" ? "Abstellung" :',
     'stArt({s: v.status, grund: v.grund}) === "abgestellt" ? "Abstellung" : stArt({s: v.status, grund: v.grund}) === "abwesend" ? "Abwesend" :'),
    ('const ausfallNews = m => ["verletzt", "gesperrt"].includes(m.status)',
     'const ausfallNews = m => ["verletzt", "gesperrt", "abwesend"].includes(m.status)'),
]


def main():
    pfad = sys.argv[1]
    s = open(pfad, encoding="utf-8").read()
    if 'abwesend:["uhr"' in s:
        print("schon gepatcht")
        return
    for alt, neu in ERSETZUNGEN:
        n = s.count(alt)
        if n < 1:
            sys.exit(f"nicht gefunden: {alt[:80]}")
        s = s.replace(alt, neu)
    open(pfad, "w", encoding="utf-8").write(s)
    print(f"{len(ERSETZUNGEN)} Ersetzungen")


if __name__ == "__main__":
    main()
