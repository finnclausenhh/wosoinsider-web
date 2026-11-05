"""Verletzungen und Einsehbar (Finn 05.11.2026).
1. Kreuzbandriss: Ausfallzeit aus der UEFA-Studie (Median 292 Tage), Etappen und Rückkehr als Monat statt Datum
2. Verletzungs-Meldung zeigt den Status-Verlauf wie im Profil (Grafik und Einschätzung)
3. Einsehbar: neue Erklärung, Legende im Profil weg, Symbol auf Höhe des Gegners
"""
import sys
def rep(s, old, new):
    n = s.count(old); assert n == 1, (old[:90], n); return s.replace(old, new)

VT_ALT = '[/kreuzband/i, "Kreuzbandriss", 180, 300]'
VT_NEU = '[/kreuzband/i, "Kreuzbandriss", 246, 334, 292]'

LANG = r'''    if (t[2] >= 150) {  // lange Ausfälle (Finn 05.11.2026): Etappen und Rückkehr als Monat, kein Tagesdatum
      const MON = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"];
      const mk = d => MON[d.getMonth()].slice(0, 3) + (d.getFullYear() !== d0.getFullYear() ? " " + String(d.getFullYear()).slice(2) : "");
      const med = t[4] || Math.round((t[2] + t[3]) / 2), r = plus(med), saison = r.getMonth() >= 5 && r.getMonth() <= 8;
      const ET = [[90, "Lauftraining", "reha"], [150, "Training mit Ball", "reha"], [220, "Mannschaftstraining", "kader"]];
      return {seit, typisch: [t[2], t[3]], stand: st.stand,
        satz: `Ein ${t[1]} kostet Spielerinnen im europäischen Spitzenfußball im Mittel ${med} Tage, ${med / 30 % 1 > .5 ? "knapp " + Math.ceil(med / 30) : "gut " + Math.floor(med / 30)} Monate. Damit wäre sie etwa im ${MON[r.getMonth()]} ${r.getFullYear()} zurück${saison ? ", also zur neuen Saison" : ""}.${st.rueckkehr ? " Laut Bericht: " + st.rueckkehr + "." : ""}`,
        phasen: [{d: kd(d0), iso: seit, t: t[1], typ: "verletzung"}].concat(ET.map(([n, l, ty]) => ({d: mk(plus(n)), iso: iso(plus(n)), t: l, typ: ty, prog: true})), [{d: mk(r), iso: iso(r), t: "zurück im Spiel", typ: "startelf", prog: true}]),
        vergleich: t[4] ? `UEFA Women's Elite Club Injury Study (Hallén u. a., 2024): Kreuzbandriss im Mittel ${t[4]} Tage Ausfall, die meisten ${t[2]} bis ${t[3]} Tage. Die Zwischenschritte sind übliche Reha-Etappen, keine Meldungen zu ihr.`
          : "Erfahrungswerte aus typischen Verläufen dieser Verletzung, keine ärztliche Prognose. Die Zwischenschritte sind übliche Reha-Etappen, keine Meldungen zu ihr."};
    }
'''
LANG_ANKER = '''    const lang = n => n >= 150 ?'''

ART = r'''  // Status-Verlauf in der Verletzungs-Meldung (Finn 05.11.2026), wie im Profil: Grafik und Einschätzung
  function artVerlauf(m){
    if (!SPN || !istSpielerin(m) || !m.spielerin) return "";
    let s = findeSP(KURZ[m.verein], m.spielerin) || (SPN.spielerinnen || []).find(x => x.n === m.spielerin && x.k === KURZ[m.verein]); if (!s) return "";
    if (!(s.status && ["raus", "gesperrt"].includes(s.status.s))) return "";
    if (!s.einschaetzung) { const ve = verletzungEinsch(s); if (ve) s = Object.assign({}, s, {einschaetzung: ve}); }
    const g = verlaufGrafik(s), e = s.einschaetzung; if (!g) return "";
    return `<section class="pf-box art-sv">${kap("Status-Verlauf")}${g}${e && e.satz ? `<div class="pf-einsch"><b class="k">UNSERE EINSCHÄTZUNG</b>${esc(e.satz)}${e.vergleich ? `<p class="pf-vgl">${esc(e.vergleich)}</p>` : ""}</div>` : ""}</section>`;
  }
'''

def patch(s):
    s = rep(s, VT_ALT, VT_NEU)
    s = rep(s, LANG_ANKER, LANG + LANG_ANKER)
    s = rep(s, '  function article(id){', ART + '  function article(id){')
    # Grafik nach dem Text, vor der Kickbase-Box; nachladen, wenn die Profile noch fehlen
    s = rep(s, '''${kbBox(m.kickbase)}<div id="pf-karte">''', '''<div id="art-sv">${auf || sc ? "" : artVerlauf(m)}</div>${kbBox(m.kickbase)}<div id="pf-karte">''')
    s = rep(s, '''ladeSPN().then(() => { const el = $("#pf-karte"); if (el && ARTIKEL === id) el.innerHTML = profilKarte(m); }).catch(() => {});''',
               '''ladeSPN().then(() => { const el = $("#pf-karte"); if (el && ARTIKEL === id) el.innerHTML = profilKarte(m); const sv = $("#art-sv"); if (sv && ARTIKEL === id) sv.innerHTML = artVerlauf(m); }).catch(() => {});''')
    # Einsehbar: Erklärung neu, Legende unter den nächsten Spielen weg
    s = rep(s, 'title="Offizielle Startelf steht fest, bevor Kickbase die Aufstellung sperrt"', 'title="Die offizielle Aufstellung erscheint, solange du deine Kickbase-Aufstellung noch ändern kannst"')
    s = rep(s, '<span>Startelf steht fest, bevor Kickbase sperrt</span>', '<span>Offizielle Aufstellung kommt, bevor Kickbase schließt</span>')
    s = rep(s, '''${komH.includes('class="eins"') ? `<div class="pf-eins-leg">${einsTag(true)}<span>Startelf steht fest, bevor Kickbase sperrt (erstes Spiel des Spieltags)</span></div>` : ""}''', '')
    s = rep(s, '.pf-km .eins{margin-left:6px;vertical-align:-1px}', '.pf-km .gg{display:flex;align-items:center;gap:4px;min-width:0}.pf-km .eins{margin-left:4px;flex:none}')
    s = rep(s, '.pf-km .eins svg{width:15px;height:15px}', '.pf-km .eins svg{width:14px;height:14px}.art-sv{margin-top:4px}')
    s = rep(s, "ende = Math.max(tag(new Date(ph[ph.length - 1].iso + \"T12:00\")), tag(heute) + 4, 1);", "ende = Math.max(tag(new Date(ph[ph.length - 1].iso + \"T12:00\")), tag(heute) + 4, e.typisch ? e.typisch[1] : 0, 1);")
    s = rep(s, ".vg-band i{position:absolute;bottom:24px;left:0;", ".vg-band i{position:absolute;bottom:24px;right:0;")
    assert "—" not in s
    return s

if __name__ == "__main__":
    for f in sys.argv[1:]:
        s = open(f, encoding="utf-8").read()
        if "function artVerlauf" in s: print("schon drin", f); continue
        t = patch(s); open(f, "w", encoding="utf-8").write(t); print("ok", f)
