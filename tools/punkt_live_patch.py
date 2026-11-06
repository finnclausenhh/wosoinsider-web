#!/usr/bin/env python3
"""Auf den Punkt lebt bis zum letzten Anpfiff (Finn 06.11.2026). Daten aus fbl-daten/tools/punkt_update.py:
updates [{zeit, k, text}], wackel [{k, p, a, b, anstoss}], update an Einträgen, headline mit "· Update HH:MM".
- Karte im Feed: neuestes Update als Zeile, "Angeheftet bis zum letzten Anpfiff".
- Artikel: Block "Letzte Änderungen" oben (Uhrzeit, Wappen, Text), Abschnitt "Wackelkandidaten" (A oder B, Position,
  Anstoß), Hinweis an überholten Einträgen.
Jede Ersetzung muss genau einmal passen. Aufruf: python3 tools/punkt_live_patch.py <index.html>
"""
import sys

ERS = [
    ("""      <div class="pk-b">${tag("AUF DEN PUNKT")}<h2>${esc(m.headline)}</h2><div class="z">${fest ? "Angeheftet bis zum Anpfiff" : esc(relativ(m.zeit))}</div></div></button>`;""",
     """      <div class="pk-b">${tag("AUF DEN PUNKT")}<h2>${esc(m.headline)}</h2>${(m.updates || []).length ? `<div class="pk-u">${logo(m.updates[0].k, 16)}<span>${esc(m.updates[0].text)}</span></div>` : ""}<div class="z">${fest ? "Angeheftet bis zum letzten Anpfiff" : esc(relativ(m.zeit))}</div></div></button>`;"""),
    ("""    const sek = (t, xs, farbe) => { const l = sicht(xs); return l.length ? `<div class="psec" style="--pc:${farbe}">${kap(t, farbe)}${l.map(x =>
      `<div class="prow">${logo(x.k, 28)}<div><b>${esc(x.n)}</b><small>${esc(kname(x.k))}</small><p>${esc(x.warum)}</p></div></div>`).join("")}</div>` : ""; };""",
     """    const sek = (t, xs, farbe) => { const l = sicht(xs); return l.length ? `<div class="psec" style="--pc:${farbe}">${kap(t, farbe)}${l.map(x =>
      `<div class="prow">${logo(x.k, 28)}<div><b>${esc(x.n)}</b><small>${esc(kname(x.k))}</small><p>${esc(x.warum)}</p>${x.update ? `<p class="pupd">Update ${esc(x.update.zeit.slice(11, 16))}: ${esc(x.update.text)}</p>` : ""}</div></div>`).join("")}</div>` : ""; };
    const ups = sicht(m.updates), wk = sicht(m.wackel);
    const updBlock = ups.length ? `<div class="psec" style="--pc:#F5C518">${kap("Letzte Änderungen", "#F5C518")}${ups.map(u =>
      `<div class="pup"><span class="pz">${esc(u.zeit.slice(11, 16))}${u.zeit.slice(0, 10) !== (m.aktualisiert || u.zeit).slice(0, 10) ? `<small>${esc(wtLang(u.zeit).split(",")[0])}</small>` : ""}</span>${logo(u.k, 20)}<span>${esc(u.text)}</span></div>`).join("")}</div>` : "";
    const wkBlock = wk.length ? `<div class="psec" style="--pc:#A78BFA">${kap("Wackelkandidaten", "#A78BFA")}${wk.map(w =>
      `<div class="prow">${logo(w.k, 28)}<div><b>${esc(w.a)} oder ${esc(w.b)}</b><small>${esc(w.p)} · ${esc(kname(w.k))} · ${esc(wtLang(w.anstoss).split(",")[0])} ${esc(uhr(dt(w.anstoss)))}</small></div></div>`).join("")}</div>` : "";""",
     ),
    ("""      ${(m.text || []).map(p => `<p style="font-size:16.5px">${esc(p)}</p>`).join("")}
      ${sek("Sicher aufstellen", m.sicher, "#2EB872")}${sek("Finger weg", m.finger_weg, "#E24A4A")}${sek("Günstiger Tipp", m.tipp, "#2F5BFF")}${sek("Achtung", m.achtung, "#E0962B")}""",
     """      ${updBlock}
      ${(m.text || []).map(p => `<p style="font-size:16.5px">${esc(p)}</p>`).join("")}
      ${sek("Sicher aufstellen", m.sicher, "#2EB872")}${sek("Finger weg", m.finger_weg, "#E24A4A")}${wkBlock}${sek("Günstiger Tipp", m.tipp, "#2F5BFF")}${sek("Achtung", m.achtung, "#E0962B")}"""),
    ("""      <div class="dat">${esc(lang(m.zeit))}${SEL.size ? " · gefiltert auf deine Vereine" : ""}</div>""",
     """      <div class="dat">${esc(lang(m.zeit))}${m.aktualisiert ? ` · zuletzt aktualisiert ${esc(wtLang(m.aktualisiert).split(",")[0])} ${esc(m.aktualisiert.slice(11, 16))} Uhr` : ""}${SEL.size ? " · gefiltert auf deine Vereine" : ""}</div>"""),
    (""".psec::before{""",
     """.pk-u{display:flex;align-items:center;gap:6px;font-size:13px;color:var(--muted);line-height:1.3}
.pk-u span{overflow:hidden;text-overflow:ellipsis;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.pup{display:grid;grid-template-columns:44px 20px 1fr;gap:8px;align-items:start;font-size:14.5px;line-height:1.35}
.pup .pz{font:700 13px var(--f-mono);color:#F5C518;padding-top:1px;display:grid}
.pup .pz small{font:500 10px var(--f-body);color:var(--muted);text-transform:uppercase}
.pupd{color:#F5C518 !important;font-size:13px !important}
.psec::before{"""),
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
