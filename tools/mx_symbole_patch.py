# Analyse-Matrix (Inside "Analyse der Woche", z. B. "FC Bayern in Wolfsburg"): Symbole statt Punkte (Finn 13.11.2026)
#  - Sperre statt "verletzt": fehlt sie wegen Rot-, Gelb-Rot- oder Gelbsperre, steht eine große Karte im Feld (neutral grau, nicht rot wie Verletzung).
#    Erkannt an der Notiz ("Rotsperre", "Gelbsperre", "Sperre ...") oder an der Karte im Spiel davor (spielerinnen.json).
#  - Gespielte Felder: Tor = Ball oben rechts (statt gelbem Punkt), Vorlage = V unten rechts, Karte im Spiel = kleine Karte oben links.
#    Vorlagen und Karten kommen aus spielerinnen.json (spiele[md]), Tore aus der Matrix (sonst aus spielerinnen.json).
#  - Legende: Tor (Ball), Vorlage, Gelb, Rot, Sperre. Analyse als News-Artikel lädt spielerinnen.json nach.
# Aufruf: python3 tools/mx_symbole_patch.py ticker/index.html   (derselbe Patch gilt für index.html im Artifact)
import sys


def rep(s, a, b, n=1):
    assert s.count(a) == n, (s.count(a), a[:90])
    return s.replace(a, b)


EDITS = [
    # 1) Zelle: Sperre erkennen, Symbole aus spielerinnen.json
    ("""    reihen.forEach(([name, md]) => { mx += `<span class="nm">${esc(name)}</span>` + sp.map((o, i) => { const m = md[String(i + 1)], art = m ? m[0] : "N", mi = m ? m[1] : 0, to = m ? Number(m[2]) || 0 : 0, no = m && m[3] ? String(m[3]) : "";
      let t = `${name} · ${i + 1}. Spieltag gegen ${o}: ` + (art === "S" ? `Startelf, ${mi} Minuten` : art === "E" ? `eingewechselt, ${mi} Minuten` : art === "V" ? `fehlte (${no})` : "nicht eingesetzt");
      if (to > 0) t += `, ${to} Tor${to > 1 ? "e" : ""}`; if (no && art !== "V") t += `, ${no}`;
      return `<button class="c ${art}" data-mx="${esc(t)}" aria-label="${esc(t)}" aria-pressed="${MXINFO === t}">${art === "V" ? svg(P.plus) : art === "N" ? "·" : esc(mi)}${to > 0 ? '<i class="t"></i>' : ""}${no === "Rote Karte" ? '<i class="r"></i>' : ""}</button>`; }).join(""); });""",
     """    const mxKarte = (f, gross) => `<span class="mk-k${gross ? " gr" : ""}" style="background:${f === "gr" ? "linear-gradient(135deg,#F5C518 50%,#E24A4A 50%)" : f === "rot" ? "#E24A4A" : "#F5C518"}" role="img" aria-label="${f === "gr" ? "Gelb-Rote Karte" : f === "rot" ? "Rote Karte" : "Gelbe Karte"}"></span>`;
    reihen.forEach(([name, md]) => { const sx = SPN && A.verein ? findeSP(A.verein, name) : null, spMd = n => sx && (sx.spiele || []).find(z => z.md === n);
      mx += `<span class="nm">${esc(name)}</span>` + sp.map((o, i) => { const m = md[String(i + 1)], z = spMd(i + 1) || {}, vz = spMd(i) || {};
      let art = m ? m[0] : "N"; const mi = m ? m[1] : 0, no = m && m[3] ? String(m[3]) : "", to = m ? Number(m[2]) || 0 : (z.tore || []).length, vo = art === "S" || art === "E" ? Number(z.vorl) || 0 : 0;
      // Sperre: Notiz nennt sie, oder Rot / Gelb-Rot im Spiel davor
      let sperre = null; if (art === "V") { const nl = no.toLowerCase();
        if (/gelb.?rot/.test(nl) && /sperre|gesperrt/.test(nl)) sperre = "gr"; else if (/rot/.test(nl) && /sperre|gesperrt/.test(nl)) sperre = "rot"; else if (/gelb/.test(nl) && /sperre|gesperrt/.test(nl)) sperre = "gelb";
        else if (/sperre|gesperrt/.test(nl)) sperre = vz.gr ? "gr" : vz.rot ? "rot" : "gelb";
        else if (!no && (vz.rot || vz.gr)) sperre = vz.gr ? "gr" : "rot"; }
      const ka = art === "S" || art === "E" ? (z.gr ? "gr" : z.rot || no === "Rote Karte" ? "rot" : z.gelb || /gelbe karte/i.test(no) ? "gelb" : null) : null;
      const kn = {gr: "Gelb-Rote Karte", rot: "Rote Karte", gelb: "Gelbe Karte"};
      let t = `${name} · ${i + 1}. Spieltag gegen ${o}: ` + (art === "S" ? `Startelf, ${mi} Minuten` : art === "E" ? `eingewechselt, ${mi} Minuten` : sperre ? `gesperrt (${no || (sperre === "gelb" ? "Gelbsperre" : sperre === "gr" ? "Gelb-Rot-Sperre" : "Rotsperre")})` : art === "V" ? `fehlte (${no})` : "nicht eingesetzt");
      if (to > 0) t += `, ${to} Tor${to > 1 ? "e" : ""}`; if (vo > 0) t += `, ${vo} ${vo > 1 ? "Vorlagen" : "Vorlage"}`; if (ka && !(no && no.toLowerCase().includes(kn[ka].toLowerCase()))) t += `, ${kn[ka]}${z[ka === "gr" ? "rot" : ka] && z[ka === "gr" ? "rot" : ka] !== true ? " (" + z[ka === "gr" ? "rot" : ka] + ".)" : ""}`; if (no && art !== "V") t += `, ${no}`;
      return `<button class="c ${sperre ? "Sp" : art}" data-mx="${esc(t)}" aria-label="${esc(t)}" aria-pressed="${MXINFO === t}">${sperre ? mxKarte(sperre, true) : art === "V" ? svg(P.plus) : art === "N" ? "·" : esc(mi)}${to > 0 ? `<span class="mxt">${BALL}${to > 1 ? `<b>${to}</b>` : ""}</span>` : ""}${vo > 0 ? `<span class="mxv">${VORL}</span>` : ""}${ka ? `<span class="mkk">${mxKarte(ka)}</span>` : ""}</button>`; }).join(""); });
    if (!SPN) ladeSPN().then(() => { const w = document.querySelector(".mxw"); if (w && VIEW === "inside") { const y = window.scrollY; inside(); window.scrollTo(0, y); } else if (w) { const y = window.scrollY; anaArticle(); window.scrollTo(0, y); } }).catch(() => {});"""),
    # 2) Legende
    ("""<span><i style="background:rgba(226,74,74,.3)"></i>verletzt / Reha</span><span><i style="background:var(--pokal);border-radius:50%"></i>Tor</span>""",
     """<span><i style="background:rgba(226,74,74,.3)"></i>verletzt / Reha</span><span class="mxl">${BALL}Tor</span><span class="mxl">${VORL}Vorlage</span><span class="mxl"><span class="mk-k" style="background:#F5C518"></span><span class="mk-k" style="background:#E24A4A"></span>Karte</span><span class="mxl"><span class="mk-k gr" style="background:#E24A4A"></span>gesperrt</span>"""),
    # 3) CSS: alte Punkte raus, Symbole rein
    (""".mx .c .t{position:absolute;right:2px;top:2px;width:7px;height:7px;border-radius:50%;background:var(--pokal)}
.mx .c .r{position:absolute;right:2px;top:2px;width:5px;height:7px;background:var(--inj)}""",
     """.mx .c.Sp{background:color-mix(in srgb,var(--soft) 80%,transparent)}
.mx .c .mxt{position:absolute;right:1px;top:1px;display:flex;align-items:center;gap:1px;line-height:1}
.mx .c .mxt .ball{width:9px;height:9px}
.mx .c .mxt b{font:800 8px/1 var(--f-body);color:#fff;text-shadow:0 0 2px #000}
.mx .c .mxv{position:absolute;right:1px;bottom:1px;line-height:1}
.mx .c .mxv .vorl.vt{background:#8FB0FF;color:#0B1220;border-radius:2px;padding:0 2px;min-width:7px;font-size:7.5px;height:9px!important}
.mx .c .mkk{position:absolute;left:2px;top:2px;line-height:0}
.mk-k{display:inline-block;width:5px;height:7px;border-radius:1px;box-shadow:0 0 0 1px rgba(11,18,32,.6)}
.mk-k.gr{width:9px;height:13px;border-radius:2px;transform:rotate(-8deg);box-shadow:0 0 0 1.5px #1C2333}
.leg .mxl{gap:3px}
.leg .mxl .ball{width:11px;height:11px}
.leg .mxl .vorl.vt{background:#8FB0FF;color:#0B1220;border-radius:3px;padding:1px 3px;font-size:9px}
.leg .mxl .mk-k.gr{width:7px;height:10px}"""),
]


def main(p):
    s = open(p, encoding="utf-8").read()
    for a, b in EDITS:
        s = rep(s, a, b)
    open(p, "w", encoding="utf-8").write(s)
    print("ok", p)


if __name__ == "__main__":
    main(sys.argv[1])
