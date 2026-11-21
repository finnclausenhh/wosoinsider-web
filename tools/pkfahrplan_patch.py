"""PK-Fahrplan als Design statt Fließtext (Finn 21.11.2026, Variante B aus dem Canvas).

Die Meldung pk-mdNN trägt das Feld "fahrplan" (fbl-daten tools/pk_fahrplan.py): je Verein Vorbericht oder
"erwartet bis" aus dem Verlauf, Vereinsseite, PK, dazu pin_bis = erster Anpfiff des Spieltags.
  - Feed: eigene Karte mit Zähler in der Überschrift und 14 Wappen mit Statusstrich, angeheftet bis pin_bis.
  - Artikel: ein Kasten je Verein, sortiert nach Dringlichkeit (überfällig, heute, morgen, ..., schon da), jeder
    Kasten ist ein Link (Vorbericht oder Vereinsseite). Der Status wird im Browser aus der Uhrzeit berechnet.
Meldungen ohne "fahrplan" bleiben unverändert (alter Fließtext).
Aufruf: python3 tools/pkfahrplan_patch.py <index.html> <ausgabe.html> [--test]
  --test: Testseiten-Hinweis und Testdaten aus pk-test.json neben der Seite (heute, mit ?pkdemo=1 der Stand Fr 08:05).
"""
import pathlib
import sys


def ersetze(s, alt, neu):
    n = s.count(alt)
    if n != 1:
        sys.exit(f"Anker {alt[:60]!r} {n}-mal gefunden")
    return s.replace(alt, neu)


CSS = r"""
/* PK-Fahrplan (Finn 21.11.2026) */
.fp{display:grid;gap:20px}
.fp-kopf{display:grid;gap:14px}
.fp-ic{fill:none;stroke:currentColor;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round;flex:none}
.fp-pin{display:inline-flex;align-items:center;gap:6px;justify-self:start;background:var(--soft);border-radius:99px;padding:5px 11px;font:700 11px var(--f-body);letter-spacing:.6px;text-transform:uppercase;color:var(--hell);white-space:nowrap}
.fp-k{display:flex;align-items:center;gap:12px}
.fp-kz{font:700 11px var(--f-body);letter-spacing:.8px;text-transform:uppercase;color:var(--hell);white-space:nowrap}
.fp-n{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.fp-n > div{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 12px;display:grid;gap:2px}
.fp-n b{display:flex;align-items:center;gap:6px;font:700 30px/1 var(--f-display)}
.fp-n span{font-size:11px;font-weight:600;letter-spacing:.6px;text-transform:uppercase;color:var(--muted);white-space:nowrap}
.fp-n .fpx-da b{color:var(--gruen)}.fp-n .fpx-offen b{color:var(--gelb)}.fp-n .fpx-spaet b{color:var(--rot)}
.fp-ls{display:flex;gap:4px;width:100%}
.fp-lz{flex:1;min-width:0;display:grid;justify-items:center;gap:5px}
.fp-lz img{max-width:100%}
.fp-lz i{width:100%;height:5px;border-radius:3px;background:#3F5075}
.fp-lz.fpx-da i{background:var(--gruen)}.fp-lz.fpx-spaet i{background:var(--rot)}.fp-lz.fpx-ohne i{background:var(--line)}.fp-lz.fpx-ohne img{opacity:.45}
.fp-g{display:grid;gap:8px}
.fp-gh{display:flex;justify-content:space-between;align-items:baseline;font:700 12px var(--f-body);letter-spacing:.7px;text-transform:uppercase;white-space:nowrap;color:var(--muted)}
.fp-gh span{font-weight:400;letter-spacing:0;text-transform:none;color:var(--muted)}
.fp-g.fpx-spaet .fp-gh{color:var(--rot)}.fp-g.fpx-offen .fp-gh{color:var(--gelb)}.fp-g.fpx-da .fp-gh{color:var(--gruen)}
.fp-z{display:block;background:var(--card);border:1.5px solid var(--gelb);border-radius:14px;overflow:hidden;color:var(--ink);text-decoration:none}
.fp-z.fpx-spaet{border-color:var(--rot)}.fp-z.fpx-pkz{border-color:var(--line)}
.fp-zh{display:flex;align-items:center;gap:12px;padding:12px 10px 12px 12px}
.fp-zh > .fp-ic{color:var(--muted)}
.fp-zn{flex:1;min-width:0;display:grid;gap:4px}
.fp-zn b{font:700 19px/1 var(--f-display);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.fp-zn small{font-size:12px;line-height:1;color:var(--muted);white-space:nowrap}
.fp-zr{display:grid;justify-items:end;gap:3px;flex:none}
.fp-zr em{display:flex;align-items:center;gap:4px;font:700 10.5px var(--f-body);font-style:normal;letter-spacing:.5px;text-transform:uppercase;white-space:nowrap;color:var(--gelb)}
.fp-z.fpx-spaet .fp-zr em{color:var(--rot)}.fp-z.fpx-pkz .fp-zr em{color:var(--hell)}
.fp-zr strong{font:700 22px/1 var(--f-display);white-space:nowrap}
.fp-pk{display:flex;align-items:center;gap:8px;padding:9px 12px;border-top:1px solid var(--line);background:var(--soft);font-size:12px;white-space:nowrap}
.fp-pk .fp-ic{color:var(--gelb)}.fp-pk b{font-weight:600}.fp-pk span{margin-left:auto;color:var(--muted)}
.fp-cs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.fp-c{display:flex;align-items:center;gap:9px;min-height:48px;padding:8px 10px;background:var(--card);border:1px solid var(--line);border-radius:12px;color:var(--ink);text-decoration:none;min-width:0}
.fp-c > span{flex:1;min-width:0;display:grid;gap:3px}
.fp-c b{font:700 17px/1 var(--f-display);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.fp-c small{font-size:11.5px;line-height:1;color:var(--muted);white-space:nowrap}
.fp-c .fp-ic{color:var(--gruen)}.fp-c.fpx-ohne .fp-ic{color:var(--muted)}.fp-c.fpx-ohne img{opacity:.55}
.fp-info summary{display:flex;align-items:center;gap:8px;min-height:44px;font-size:12px;color:var(--muted);cursor:pointer;list-style:none}
.fp-info summary::-webkit-details-marker{display:none}
.fp-info p{margin:0;font-size:12px;line-height:1.5;color:var(--muted)}
.fpk{display:grid;gap:12px;width:100%;text-align:left;background:var(--card);border:1px solid transparent;border-radius:14px;padding:12px;color:var(--ink)}
.fpk.fest{border:1.5px solid var(--accent)}
.fpk .fp-pin{background:none;padding:0;border-radius:0}
.fpk-k{display:flex;align-items:center;gap:12px}
.fpk-t{display:grid;gap:4px;min-width:0}
.fpk-t small{font-size:11px;color:var(--muted);white-space:nowrap}
.fpk-t b{font:700 20px/1.08 var(--f-display)}
.fpk-pk{display:flex;align-items:center;gap:5px;font-size:12px;white-space:nowrap}
.fpk-pk .fp-ic{color:var(--gelb)}
.fpk-z{font-size:11px;font-weight:500;letter-spacing:.4px;text-transform:uppercase;color:var(--muted)}
"""

JS = r"""  // ---------------- PK-Fahrplan (Finn 21.11.2026): ein Kasten je Verein, sortiert nach Dringlichkeit, angeheftet bis zum ersten Anpfiff
  const fpJetzt = () => window.FPJETZT || Date.now();
  const fpOk = m => !!(m && m.fahrplan && (m.fahrplan.vereine || []).length);
  const fpFest = m => fpOk(m) && !!m.fahrplan.pin_bis && dt(m.fahrplan.pin_bis) > fpJetzt();
  const FP_IC = {da: '<path d="M5 12.5l4.5 4.5L19 7.5"/>', offen: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>', spaet: '<path d="M12 4L21 19.5H3z"/><path d="M12 10v4.5M12 17v.2"/>',
    ohne: '<path d="M6 12h12"/>', mic: '<rect x="9" y="3.5" width="6" height="11" rx="3"/><path d="M5.5 11.5a6.5 6.5 0 0 0 13 0M12 18v3"/>', pin: '<path d="M9 3.5h6l-1 6 3.5 3.5h-11L10 9.5zM12 13v7.5"/>',
    pfeil: '<path d="M9 5.5l6.5 6.5L9 18.5"/>', info: '<circle cx="12" cy="12" r="8.5"/><path d="M12 11v5M12 7.6v.2"/>'};
  const fpIc = (k, g = 14) => `<svg class="fp-ic" width="${g}" height="${g}" viewBox="0 0 24 24" aria-hidden="true">${FP_IC[k]}</svg>`;
  // Grenze von "erwartet bis": mit Uhrzeit dieser Zeitpunkt, ohne Uhrzeit das Ende des Tages
  const fpGrenze = v => { const e = v.erwartet; if (!e || !e.bis) return null; const d = dt(e.bis); return e.uhr ? d : new Date(d.getTime() + 864e5); };
  function fpSt(v){ const j = fpJetzt(); if (v.vb) return "da"; if (dt(v.anstoss) <= j) return "ohne"; const g = fpGrenze(v); return g && g <= j ? "spaet" : "offen"; }
  const fpZeit = (z, mitUhr) => { const d = dt(z); return mitUhr ? `${WT[d.getDay()]} ${uhr(d)}` : WTL[d.getDay()]; };
  const FP_LAB = {da: "da", offen: "erwartet", spaet: "überfällig", ohne: "kein Vorbericht"};
  function fpZahl(m){ const z = {da: 0, offen: 0, spaet: 0, ohne: 0}; m.fahrplan.vereine.forEach(v => z[fpSt(v)]++); return z; }
  function fpLeiste(m, g){ const r = {da: 0, spaet: 1, offen: 2, ohne: 3};
    const vs = m.fahrplan.vereine.map((v, i) => [v, i, fpSt(v)]).sort((a, b) => r[a[2]] - r[b[2]] || a[1] - b[1]);
    return `<span class="fp-ls" role="img" aria-label="${esc(vs.map(x => `${x[0].name} ${FP_LAB[x[2]]}`).join(", "))}">${vs.map(x => `<span class="fp-lz fpx-${x[2]}">${logo(x[0].k, g)}<i></i></span>`).join("")}</span>`; }
  const fpTitel = m => { const z = fpZahl(m), n = m.fahrplan.vereine.length; return `${z.da} von ${n} Vorberichten da${z.spaet ? `, ${z.spaet} überfällig` : ""}`; };
  const fpPin = m => { const d = dt(m.fahrplan.pin_bis); return `<span class="fp-pin">${fpIc("pin", 13)}Angeheftet bis Anpfiff · ${WT[d.getDay()]} ${uhr(d)}</span>`; };
  const fpPkText = p => p.kurz || `${String(p.tag || "").split(" ")[0]}, ${p.bestaetigt ? "bestätigt" : "Uhrzeit offen"}`;
  function fpKarte(m){
    const fest = fpFest(m), fp = m.fahrplan, pks = fp.vereine.filter(v => v.pk && dt(v.anstoss) > fpJetzt());
    const pk = pks.length === 1 ? `PK: ${pks[0].name} am ${String(pks[0].pk.tag || "").split(" ")[0]} ${pks[0].pk.bestaetigt ? "bestätigt" : "erwartet"}` : pks.length ? `PK: ${pks.map(v => v.name).join(", ")}` : "";
    return `<button class="fpk${fest ? " fest" : ""}" data-id="${esc(m.id)}">${fest ? fpPin(m) : ""}
      <span class="fpk-k">${bild(m, 56, 56)}<span class="fpk-t"><small>Pressekonferenzen · ${esc(String(fp.md))}. Spieltag</small><b>${esc(fpTitel(m))}</b></span></span>
      ${fpLeiste(m, 18)}${pk ? `<span class="fpk-pk">${fpIc("mic", 13)}${esc(pk)}</span>` : ""}${fest ? "" : `<span class="fpk-z">${esc(relativ(m.zeit))}</span>`}</button>`;
  }
  function fpZeile(v){
    const st = fpSt(v), e = v.erwartet, an = dt(v.anstoss), lab = st === "spaet" ? "Überfällig seit" : e ? "Erwartet bis" : "Erwartet", zt = e ? fpZeit(e.bis, e.uhr) : "offen";
    return `<a class="fp-z fpx-${st}" href="${esc(v.seite || "#")}" target="_blank" rel="noopener" aria-label="${esc(`${v.name}: ${lab} ${zt}, zur Vereinsseite`)}">
      <span class="fp-zh">${logo(v.k, 40)}<span class="fp-zn"><b>${esc(v.name)}</b><small>Anpfiff ${WT[an.getDay()]} ${uhr(an)}</small></span>
      <span class="fp-zr"><em>${fpIc(st, 12)}${lab}</em><strong>${esc(zt)}</strong></span>${fpIc("pfeil")}</span>
      ${v.pk ? `<span class="fp-pk">${fpIc("mic")}<b>Pressekonferenz</b><span>${esc(fpPkText(v.pk))}</span></span>` : ""}</a>`;
  }
  function fpPkZeile(v){ const an = dt(v.anstoss);
    return `<a class="fp-z fpx-pkz" href="${esc(v.seite || "#")}" target="_blank" rel="noopener" aria-label="${esc(`${v.name}: Pressekonferenz ${fpPkText(v.pk)}`)}">
      <span class="fp-zh">${logo(v.k, 40)}<span class="fp-zn"><b>${esc(v.name)}</b><small>Anpfiff ${WT[an.getDay()]} ${uhr(an)}</small></span>
      <span class="fp-zr"><em>${fpIc("mic", 12)}${v.pk.bestaetigt ? "Bestätigt" : "Üblich am"}</em><strong>${esc(String(v.pk.tag || "").split(" ")[0])}</strong></span>${fpIc("pfeil")}</span></a>`; }
  function fpChip(v){ const da = !!v.vb, z = !da ? "kein Vorbericht" : v.vb.zeit ? "seit " + fpZeit(v.vb.zeit, !v.vb.zeit.endsWith("T00:00")) : "online";
    return `<a class="fp-c${da ? "" : " fpx-ohne"}" href="${esc(da ? v.vb.url : v.seite || "#")}" target="_blank" rel="noopener" aria-label="${esc(da ? `${v.name}: Vorbericht lesen, ${z}` : `${v.name}: kein Vorbericht, zur Vereinsseite`)}">${logo(v.k, 28)}<span><b>${esc(kname(v.k))}</b><small>${esc(z)}</small></span>${fpIc(da ? "da" : "ohne", 15)}</a>`; }
  function fpArtikel(m){
    const fp = m.fahrplan, vs = fp.vereine, j = fpJetzt(), z = fpZahl(m), mt = d => new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();
    const von = st => vs.filter(v => fpSt(v) === st), gz = v => { const g = fpGrenze(v); return g ? g.getTime() : Infinity; };
    const gruppe = (kl, t, rechts, inhalt) => `<section class="fp-g fpx-${kl}"><div class="fp-gh">${esc(t)}${rechts ? `<span>${esc(rechts)}</span>` : ""}</div>${inhalt}</section>`;
    const spaet = von("spaet").sort((a, b) => gz(a) - gz(b)), offen = von("offen").sort((a, b) => gz(a) - gz(b)), da = von("da").sort((a, b) => String(b.vb.zeit || "").localeCompare(String(a.vb.zeit || ""))), ohne = von("ohne");
    let h = spaet.length ? gruppe("spaet", `Überfällig · ${spaet.length}`, "", spaet.map(fpZeile).join("")) : "";
    const tage = new Map();
    offen.forEach(v => { const k = v.erwartet ? mt(dt(v.erwartet.bis)) : Infinity; if (!tage.has(k)) tage.set(k, []); tage.get(k).push(v); });
    [...tage.keys()].sort((a, b) => a - b).forEach(k => { const l = tage.get(k), d = new Date(k), n = Math.round((k - mt(new Date(j))) / 864e5);
      h += gruppe("offen", `${k === Infinity ? "Noch offen" : n === 0 ? "Heute" : n === 1 ? "Morgen" : WTL[d.getDay()]} · ${l.length}`, k === Infinity ? "noch kein Rhythmus bekannt" : `${WT[d.getDay()]} ${kurz(d)}`, l.map(fpZeile).join("")); });
    const pkDa = vs.filter(v => v.pk && v.vb && dt(v.anstoss) > j);
    if (pkDa.length) h += gruppe("pkz", `Pressekonferenz · ${pkDa.length}`, "", pkDa.map(fpPkZeile).join(""));
    if (da.length) h += gruppe("da", `Schon da · ${da.length}`, "antippen zum Lesen", `<div class="fp-cs">${da.map(fpChip).join("")}</div>`);
    if (ohne.length) h += gruppe("ohne", `Kein Vorbericht · ${ohne.length}`, "Spiel läuft oder ist vorbei", `<div class="fp-cs">${ohne.map(fpChip).join("")}</div>`);
    const st = fp.stand ? dt(fp.stand) : null;
    return `<div class="fp"><div class="fp-kopf">${fpFest(m) ? fpPin(m) : ""}
      <div class="fp-k">${bild(m, 44, 44)}<div><div class="fp-kz">Pressekonferenzen · ${esc(String(fp.md))}. Spieltag</div><h1 class="disp" style="font-size:28px">Wann kommt was?</h1></div></div>
      <div class="fp-n"><div class="fpx-da"><b>${fpIc("da", 16)}${z.da}</b><span>Schon da</span></div><div class="fpx-offen"><b>${fpIc("offen", 16)}${z.offen}</b><span>Erwartet</span></div><div class="fpx-spaet"><b>${fpIc("spaet", 16)}${z.spaet}</b><span>Überfällig</span></div></div>
      ${fpLeiste(m, 20)}${st ? `<div class="dat">Stand ${WT[st.getDay()]} ${kurz(st)}, ${uhr(st)} Uhr</div>` : ""}</div>
      ${h}
      <details class="fp-info"><summary>${fpIc("info", 18)}Zeiten aus den letzten Spieltagen gelernt</summary><p>„Erwartet bis“ ist der späteste Zeitpunkt, zu dem der Verein seinen Vorbericht zuletzt gebracht hat, kein offizieller Termin. Die offiziellen Aufstellungen melden wir rund eine Stunde vor Anpfiff.</p></details>
      ${kbBox(m.kickbase)}</div>`;
  }
"""

TEST_JS = r"""  // Testseite: PK-News aus pk-test.json neben der Seite (heute; mit ?pkdemo=1 der Stand Fr 20.11., 08:05 mit angehefteter Karte)
  let FPTEST = null;
  const fpTestLaden = () => fetch(new URL("pk-test.json", location.href.split("#")[0]), {cache: "no-cache"}).then(r => r.json()).then(t => {
    const demo = /[?&]pkdemo=1/.test(location.search); FPTEST = demo ? t.demo : t.heute; if (demo) window.FPJETZT = dt(t.demo_jetzt).getTime(); }).catch(() => {});
  const fpTestMisch = l => FPTEST ? [FPTEST].concat(l.filter(m => m.id !== FPTEST.id)) : l;
"""


def patch(s, test=False):
    s = ersetze(s, ".pk.fest .pk-b .z{font-weight:700;color:var(--accent)}\n", ".pk.fest .pk-b .z{font-weight:700;color:var(--accent)}\n" + CSS.lstrip("\n"))
    s = ersetze(s, '  const angeheftet = m => m.typ === "punkt" && m.pin_bis && dt(m.pin_bis) > Date.now();\n',
                '  const angeheftet = m => (m.typ === "punkt" && m.pin_bis && dt(m.pin_bis) > Date.now()) || fpFest(m);\n' + JS + (TEST_JS if test else ""))
    s = ersetze(s, "    const fest = N.filter(angeheftet).sort((a, b) => dt(a.pin_bis) - dt(b.pin_bis));",
                "    const pinBis = m => dt(m.pin_bis || (m.fahrplan || {}).pin_bis), fest = N.filter(angeheftet).sort((a, b) => pinBis(a) - pinBis(b));")
    s = ersetze(s, 'let h = liveLeiste() + fest.map(punktKarte).join("");', 'let h = liveLeiste() + fest.map(m => fpOk(m) ? fpKarte(m) : punktKarte(m)).join("");')
    s = ersetze(s, 'h += m.typ === "punkt" ? punktKarte(m) : uT ?', 'h += fpOk(m) ? fpKarte(m) : m.typ === "punkt" ? punktKarte(m) : uT ?')
    anker = '    if (m.typ === "punkt") { $("#main").innerHTML = `<div class="det">${zurueck()}${punktArtikel(m)}</div>`; if (window.WIKOM) window.WIKOM.mount(m.id); window.scrollTo(0, 0); return; }\n'
    s = ersetze(s, anker, anker +
                '    if (fpOk(m)) { ARTIKEL = id; $("#main").innerHTML = `<article class="det">${zurueck()}${fpArtikel(m)}<div id="kom" data-beitrag="${esc(m.id)}"></div>'
                '<div class="nachw">${kiHinweis("Automatisch aus den Vereinsseiten und dem Verlauf der letzten Spieltage erstellt.")}</div></article>`; if (window.WIKOM) window.WIKOM.mount(m.id); window.scrollTo(0, 0); return; }\n')
    if test:
        s = ersetze(s, "    N = d.meldungen.concat(N.filter(m => eigen.has(m.id) && !neuIds.has(m.id))); liveAufMisch();",
                    "    N = fpTestMisch(d.meldungen.concat(N.filter(m => eigen.has(m.id) && !neuIds.has(m.id)))); liveAufMisch();")
        s = ersetze(s, '  frisch("news.json").then(d => {\n    N = d.meldungen || []; NSTAND = d.stand; liveAufMisch();',
                    '  Promise.all([frisch("news.json"), fpTestLaden()]).then(([d]) => {\n    N = fpTestMisch(d.meldungen || []); NSTAND = d.stand; liveAufMisch();')
        s = ersetze(s, "<main id=\"main\">", "<div style=\"background:#F5B041;color:#2A1700;font:600 12px/1.3 Inter,sans-serif;text-align:center;padding:6px 10px\">Testseite</div>\n<main id=\"main\">")
    assert "—" not in s
    return s


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    pathlib.Path(a[1]).write_text(patch(pathlib.Path(a[0]).read_text(encoding="utf-8"), "--test" in sys.argv), encoding="utf-8")
    print("ok", a[1])
