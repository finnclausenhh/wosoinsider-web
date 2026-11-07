import sys
p=sys.argv[1]; s=open(p,encoding="utf-8").read()
alt='''${p.status !== "beendet" && !istLive(p) ? (() => { const v = AF && (AF.vorschau || []).some(x => x.id === p.id), a = [p.heim_aufstellung, p.gast_aufstellung].filter(Boolean), off = a.some(x => x.typ === "offiziell");
        return v || a.length ? `<div class="af-hin"><span class="${off ? "o" : "v"}">${off ? "OFFIZIELLE AUFSTELLUNG" : "VORSCHAU"}</span></div>` : ""; })() : ""}'''
neu='''${p.status !== "beendet" && !istLive(p) ? afHin(p) : ""}'''
assert s.count(alt)==1; s=s.replace(alt,neu)
anker='  function partieZeile(p, mitTag){'
fn='''  // Hinweis unter der Partie (Finn 07.11.2026): offizielle Aufstellung auch aus den Live-Meldungen (news.json), sonst Vorschau;
  // am Spieltag zusätzlich, ab wann die Aufstellung erwartet wird (rund 60 Minuten vor Anpfiff).
  function afHin(p){
    const v = AF && (AF.vorschau || []).some(x => x.id === p.id), a = [p.heim_aufstellung, p.gast_aufstellung].filter(Boolean);
    const d = dt(p.anstoss), tt = d ? String(d.getDate()).padStart(2, "0") + String(d.getMonth() + 1).padStart(2, "0") : "";
    const live = [p.heim_k, p.gast_k].filter(k => k && tt && (N || []).some(m => m.id === "aufstellung-" + String(k).toLowerCase() + "-" + tt && !m.platzhalter)).length;
    const off = Math.max(live, a.filter(x => x.typ === "offiziell").length);
    if (off) return `<div class="af-hin"><span class="o">${off >= 2 ? "AUFSTELLUNGEN SIND DA" : "ERSTE AUFSTELLUNG IST DA"}</span></div>`;
    if (!v && !a.length) return "";
    const heute = d && d.toDateString() === new Date().toDateString() && terminiert(p);
    return `<div class="af-hin"><span class="v">VORSCHAU</span>${heute ? `<span class="a">AUFSTELLUNG AB CA. ${uhr(new Date(d.getTime() - 3600000))}</span>` : ""}</div>`;
  }
'''
assert s.count(anker)==1; s=s.replace(anker,fn+anker)
open(p,"w",encoding="utf-8").write(s)
