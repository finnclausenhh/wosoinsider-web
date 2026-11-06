#!/usr/bin/env python3
"""Live-Tempo (06.11.2026, während Spieltag 9 geprüft):
Auf den Stand nach tools/live6_patch.py (live.json über die GitHub-API).
2. Abruf während Spielen alle 30 statt 60 Sekunden.
3. Minute zählt im Gerät mit: aus uhr.a1 (Anpfiff) und uhr.a2 (Anpfiff 2. Halbzeit) in live.json, Anzeige alle 15 Sekunden
   frisch, ohne neu zu zeichnen. Ohne uhr bleibt die gemeldete Minute.
Aufruf: python3 tools/live_tempo_patch.py ticker/index.html
"""
import sys

ERSETZ = [
    ('setInterval(() => { if (!document.hidden && spielLaeuft()) loadLive(); }, 60000);',
     'setInterval(() => { if (!document.hidden && spielLaeuft()) loadLive(); }, 30000);\n'
     '  setInterval(() => { if (document.hidden || !SP) return; document.querySelectorAll("[data-lm]").forEach(el => {\n'
     '    const p = alleSpiele().find(x => x.id === el.dataset.lm); if (p && istLive(p)) { const t = liveText(p); if (el.textContent !== t) el.textContent = t; } }); }, 15000);'),
    ('const liveText = p => { const m = String(p.minute || "").trim(); return !m ? "LIVE" : /^[0-9+]+$/.test(m) ? m + "\'" : m; };',
     'const liveText = p => { const m = String(p.minute || "").trim(), u = p.uhr || {}, ab = x => Math.floor((Date.now() - new Date(x).getTime()) / 60000);\n'
     '    if (m !== "HZ" && p.status === "live") {\n'
     '      if (u.a2) { const n = 46 + ab(u.a2); if (n >= 46 && n <= 100) return n > 90 ? "90+" + (n - 90) + "\'" : n + "\'"; }\n'
     '      else if (u.a1) { const n = 1 + ab(u.a1); if (n >= 1 && n <= 52) return n > 45 ? "45+" + (n - 45) + "\'" : n + "\'"; } }\n'
     '    return !m ? "LIVE" : /^[0-9+]+$/.test(m) ? m + "\'" : m; };'),
    ('<small>${live ? esc(liveText(p)) : "Ende"}</small>',
     '<small${live ? ` data-lm="${esc(p.id)}"` : ""}>${live ? esc(liveText(p)) : "Ende"}</small>'),
]


def patch(s):
    for alt, neu in ERSETZ:
        if neu in s:
            continue
        assert s.count(alt) == 1, alt[:80]
        s = s.replace(alt, neu)
    return s


if __name__ == "__main__":
    p = sys.argv[1]
    neu = patch(open(p, encoding="utf-8").read())
    open(p, "w", encoding="utf-8").write(neu)
    print("ok", p)
