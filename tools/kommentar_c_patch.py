"""Artikel-Ende Variante C (Finn 08.11.2026, Canvas 2vHpbqEeKCvoPHT5Hx7JrZ):
Kommentare als eine Karte "Fans sagen" (Fäden mit Trennlinien, Redaktion farbig hinterlegt,
Melden/Stumm/Moderation hinter "•••", Eingabe unten in der Karte mit "Posten"),
Quellen, KI-Hinweis und Foto als eine kleine zentrierte Zeile ganz unten.
Aufruf: python3 tools/kommentar_c_patch.py <kommentare.js ein> <kommentare.js aus> [<index.html ein> <index.html aus> [<script-src alt> <script-src neu>]]"""
import sys

def js(s):
    def r(a, b):
        nonlocal s
        assert s.count(a) == 1, a[:70]
        s = s.replace(a, b)
    # 1) Aktionen: Like und Antworten sichtbar, Rest hinter •••
    r("""    if (!geloescht) {
      h += '<div class="wk-akt">';
      if (k.status === "sichtbar") {
        h += '<button data-kaktion="like" data-kid="' + k.id + '" aria-pressed="' + (S.likes[k.id] ? "true" : "false") + '"' +
             (eigen ? " disabled" : "") + ">" + (S.likes[k.id] ? "♥" : "♡") + " " + (k.likes || 0) + "</button>";
        if (!istAntwort) h += '<button data-kaktion="antworten" data-kid="' + k.id + '">Antworten</button>';
        if (!eigen) h += '<button data-kaktion="melden" data-kid="' + k.id + '">Melden</button>';""",
      """    if (!geloescht) {
      h += '<div class="wk-akt">';
      var h0 = h; h = "";
      if (k.status === "sichtbar") {
        h0 += '<button data-kaktion="like" data-kid="' + k.id + '" aria-pressed="' + (S.likes[k.id] ? "true" : "false") + '"' +
             (eigen ? " disabled" : "") + ">" + (S.likes[k.id] ? "♥" : "♡") + " " + (k.likes || 0) + "</button>";
        if (!istAntwort) h0 += '<button data-kaktion="antworten" data-kid="' + k.id + '">Antworten</button>';
        if (!eigen) h += '<button data-kaktion="melden" data-kid="' + k.id + '">Melden</button>';""")
    r("""        h += '<button class="wk-mod" data-kaktion="sperren" data-kid="' + k.id + '">Sperren 7 T.</button>';
      }
      h += "</div>";
    }""",
      """        h += '<button class="wk-mod" data-kaktion="sperren" data-kid="' + k.id + '">Sperren 7 T.</button>';
      }
      var mehr = h;
      h = h0 + (mehr ? '<button class="wk-dots" data-kaktion="menu" data-kid="' + k.id + '" aria-expanded="' + (S.menu === k.id) + '" aria-label="Weitere Aktionen">•••</button>' : "") + "</div>" +
        (mehr && S.menu === k.id ? '<div class="wk-menu">' + mehr + "</div>" : "");
    }""")
    # Team-Kommentare hinterlegen
    r("""var h = '<div class="wk-k' + (istAntwort ? " wk-sub" : "")""",
      """var team = k.profil && (k.profil.rolle === "admin" || k.profil.rolle === "moderator");
    var h = '<div class="wk-k' + (istAntwort ? " wk-sub" : "") + (team ? " wk-team" : "")""")
    # 2) Eingabe zugeklappt als Pille mit "Posten"
    r("""return '<button type="button" class="wk-zu" data-kaktion="schreiben">Kommentar schreiben …</button>';""",
      """return '<button type="button" class="wk-zu" data-kaktion="schreiben"><span>Deine Meinung …</span><b>Posten</b></button>';""")
    # 3) Aufbau: eine Karte
    r("""    var h = '<section class="wk" aria-labelledby="wk-h"><div class="wk-top"><h2 id="wk-h" class="kap">Kommentare' +
      (sichtbar ? " · " + sichtbar : "") + "</h2>" +""",
      """    var h = '<section class="wk wk-c" aria-labelledby="wk-h"><div class="wk-karte"><div class="wk-top"><h2 id="wk-h"><span class="wk-ks">Fans sagen</span>' +
      '<span class="wk-anz">' + (sichtbar ? (sichtbar === 1 ? "1 Kommentar" : sichtbar + " Kommentare") : "Noch keine Kommentare") + "</span></h2>" +""")
    r("""    h += namensZeile() + formular(null);
    h += '<p class="wk-mu" style="font-size:11.5px;margin:0">Mit dem Absenden gelten unsere <button class="wk-rl" data-legal="so-entsteht">Kommentarregeln</button>.</p>';
""", "")
    r("""    if (haupt.length > S.zeige) h += '<button class="wk-mehr" data-kaktion="mehr">Weitere ' + Math.min(SEITE, haupt.length - S.zeige) + " Kommentare</button>";
    h += "</section>";""",
      """    if (haupt.length > S.zeige) h += '<button class="wk-mehr" data-kaktion="mehr">Weitere ' + Math.min(SEITE, haupt.length - S.zeige) + " Kommentare</button>";
    h += '<div class="wk-eingabe">' + namensZeile() + formular(null) + "</div></div>";
    h += '<p class="wk-mu wk-regelz">Mit dem Absenden gelten unsere <button class="wk-rl" data-legal="so-entsteht">Kommentarregeln</button>.</p>';
    h += "</section>";""")
    # 4) Menü-Klick
    r("""    if (a === "melden") { S.melden = S.melden === id ? null : id; zeichnen(); return; }""",
      """    if (a === "menu") { S.menu = S.menu === id ? null : id; S.melden = null; zeichnen(); return; }
    if (a === "melden") { S.melden = S.melden === id ? null : id; S.menu = null; zeichnen(); return; }""")
    # 5) CSS
    r(""".wk-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}";""",
      """.wk-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}" +
    ".wk-c{border-top:0;padding-top:0;gap:8px}.wk-karte{background:var(--card);border-radius:16px;overflow:hidden}" +
    ".wk-c .wk-top{padding:12px 16px;border-bottom:1px solid var(--line);gap:10px}.wk-c .wk-top h2{display:flex;align-items:baseline;gap:8px;font-size:inherit}" +
    ".wk-ks{font:700 12px var(--f-mono);letter-spacing:.9px;text-transform:uppercase;color:var(--hell)}.wk-anz{font-size:12.5px;font-weight:400;color:var(--muted)}" +
    ".wk-c .wk-sort{background:var(--bg)}" +
    ".wk-c .wk-faden{background:none;border-radius:0;padding:12px 16px;border-bottom:1px solid var(--line)}" +
    ".wk-c .wk-sub{margin-left:0;padding:10px 12px;border-left:0;border-radius:12px;background:rgba(255,255,255,.04)}" +
    ".wk-c .wk-sub.wk-team,.wk-c .wk-team{background:rgba(47,91,255,.13);border-radius:12px;padding:10px 12px}" +
    ".wk-c .wk-red{background:none;padding:0}" +
    ".wk-dots{margin-left:auto!important;letter-spacing:1px}" +
    ".wk-menu{display:flex;flex-wrap:wrap;gap:6px}.wk-menu button{font-size:12.5px;color:var(--muted);background:var(--bg);border:1px solid var(--line);border-radius:99px;padding:6px 12px;min-height:36px}.wk-menu .wk-mod{color:var(--frag)}" +
    ".wk-eingabe{padding:10px 12px 12px;display:grid;gap:8px}" +
    ".wk-c .wk-zu{display:flex;align-items:center;justify-content:space-between;background:var(--bg);border:0;border-radius:22px;padding:0 16px;min-height:44px}" +
    ".wk-c .wk-zu b{color:var(--hell);font-weight:600;font-size:14px}" +
    ".wk-c .wk-form textarea{background:var(--bg);border:0}" +
    ".wk-regelz{font-size:11.5px;margin:0;text-align:center}" +
    ".wk-c .wk-mehr{padding:12px}";""")
    return s

def html(s, alt=None, neu=None):
    def r(a, b):
        nonlocal s
        assert s.count(a) == 1, a[:70]
        s = s.replace(a, b)
    # Quellen, KI-Hinweis und Foto als eine Zeile
    r("""${(m.quellen || []).length ? `<div class="nq-z"><b>QUELLEN</b>${m.quellen.map(""",
      """${(m.quellen || []).length ? `<div class="nq-z"><b>Quelle</b>${m.quellen.map(""")
    r(""".nq-z{display:flex;flex-wrap:wrap;gap:4px 8px;align-items:baseline;font-size:13.5px}.nq-z b{font:600 10.5px var(--f-mono);letter-spacing:.8px;color:var(--muted)}""",
      """.nq-z{display:inline;font-size:12px;color:var(--muted)}.nq-z b{font-weight:400;margin-right:4px}.nq-z .nq-p{margin:0 4px}""")
    r(""".nq-z a{color:var(--ink);text-decoration:none;border-bottom:1px solid var(--line)}""",
      """.nq-z a{color:var(--muted);text-decoration:none;border-bottom:1px solid var(--line)}.det .nachw{display:block;text-align:center;font-size:12px;color:var(--muted);line-height:1.6;border-top:1px solid var(--line);padding-top:14px;margin-top:6px}.det .nachw .nq-ki{display:inline;font-size:12px}.det .nachw .nq-z+.nq-ki:before{content:" · "}.det .nachw .nq-mehr{display:block}""")
    if alt: r(alt, neu)
    return s

if __name__ == "__main__":
    a = sys.argv[1:]
    t = js(open(a[0], encoding="utf-8").read()); open(a[1], "w", encoding="utf-8").write(t)
    if len(a) >= 4:
        t = html(open(a[2], encoding="utf-8").read(), *(a[4:6] if len(a) >= 6 else [])); open(a[3], "w", encoding="utf-8").write(t)
