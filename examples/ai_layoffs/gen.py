#!/usr/bin/env python3
"""Builds index.html for the NextUp 'AI layoffs or AI-washing?' reel (light grid look, real photos + logos).
Run from the project folder:  python3 tools/gen.py ta   (or: en)
Writes index.html for that language plus tools/sfx_events_<lang>.json (read by tools/sfx.py).
Every in-scene beat is a fraction of the scene, so both voiceovers share one design."""
import re, html, os, sys, math, json

LANG = sys.argv[1] if len(sys.argv) > 1 else "ta"
FPS, DUR, OUTRO, RED = 30, 45.0, 42.4, "#ea333f"

# scene starts from the word timings of each voiceover (whisper + RMS check)
STARTS = {"en": [0, 6.45, 11.0, 16.45, 19.85, 21.4, 26.05, 30.1, 34.95],
          "ta": [0, 6.15, 11.85, 17.0, 19.7, 20.75, 26.05, 30.8, 35.9]}[LANG]
# CTA beats: pinned comment drops, follow click
BEAT = {"en": {"pin": 36.3, "follow": 37.9}, "ta": {"pin": 38.6, "follow": 40.7}}[LANG]
VOICE_DUR = {"en": 39.6, "ta": 42.71}[LANG]
COLS = ["#3b82f6", "#ef4444", "#f6821f", "#8b5cf6", "#ffd60a", "#0ea5e9", "#22c55e", "#f59e0b", RED]
IDS = [f"s{i+1}" for i in range(9)]
ENDS = STARTS[1:] + [OUTRO]
SC = {sid: (STARTS[i], ENDS[i]) for i, sid in enumerate(IDS)}
def T(sid, u):
    a, b = SC[sid]; return round(a + u * (b - a), 3)

CREDITS = json.load(open("assets/photos/credits.json"))
SFX = []
def sfx(kind, t): SFX.append((kind, round(t, 3)))
def esc(s): return html.escape(s, quote=True)

# ---------- small building blocks ----------
def photo(sid, pid, inner=""):
    return (f'<div class="phc" id="{pid}"><img class="ph" id="{pid}i" src="assets/photos/{sid}.jpg" alt="">'
            f'<div class="fade"></div>{inner}<div class="cr">{esc(CREDITS[sid])}</div></div>')
def sheen(sid): return f'<div class="sheen" id="{sid}"></div>'
def sheen_js(sid, t): return f'tl.fromTo("#{sid}",{{x:-300}},{{x:1300,duration:.9,ease:"power2.inOut"}},{t:.2f});'
def burst(bid, x, y, n=14):
    return f'<div class="burst" id="{bid}" style="left:{x}px;top:{y}px">' + "".join(f'<i id="{bid}_{k}"></i>' for k in range(n)) + '</div>'
def burst_js(bid, t, n=14, r=170):
    out = [f'tl.set("#{bid}",{{opacity:1}},{t:.2f});tl.to("#{bid}",{{opacity:0,duration:.25}},{t+.45:.2f});']
    for k in range(n):
        a = k / n * 6.2832
        out.append(f'tl.fromTo("#{bid}_{k}",{{x:0,y:0,scale:1}},{{x:{math.cos(a)*r:.0f},y:{math.sin(a)*r:.0f},scale:.2,duration:.6,ease:"power3.out"}},{t:.2f});')
    return "\n".join(out)
def odo(oid, text, h):
    out, j = [], 0
    for ch in text:
        if ch.isdigit():
            strip = "".join(f'<span style="height:{h}px">{d % 10}</span>' for d in range(20))
            out.append(f'<span class="col" style="height:{h}px"><span class="strip" id="{oid}_{j}">{strip}</span></span>'); j += 1
        else:
            out.append(f'<span class="sep">{esc(ch)}</span>')
    return f'<span class="odo" data-layout-ignore id="{oid}" style="height:{h}px">' + "".join(out) + "</span>"
def odo_js(oid, text, h, t, dur=1.4):
    digits = [int(c) for c in text if c.isdigit()]
    for k in range(int(dur / .1)): sfx("tick", t + k * .1)
    return "\n".join(f'tl.fromTo("#{oid}_{j}",{{y:0}},{{y:{-(10 + d) * h},duration:{dur + j * .06:.2f},ease:"power3.out"}},{t:.2f});'
                     for j, d in enumerate(digits))
def src(sid, text): return f'<div class="src" id="{sid}src"><b>SOURCE</b>{esc(text)}</div>'
def logo(name, cls="", ext="svg"): return f'<img class="{cls}" src="assets/logos/{name}.{ext}" alt="{name}">'
CURSOR = '<svg class="cursor" id="{id}" viewBox="0 0 24 24"><path d="M4 2l15 10-7 1.5 4 7.5-3 1.5-4-7.5-5 4.5z"/></svg>'
def ripple(rid): return f'<div class="ripple" id="{rid}"></div>'
def ripple_js(rid, t): return f'tl.fromTo("#{rid}",{{scale:.2,opacity:.9}},{{scale:2.4,opacity:0,duration:.5,ease:"power2.out"}},{t:.2f});'
DOWN = '<svg viewBox="0 0 24 24"><path d="M12 4v15M5 12l7 7 7-7"/></svg>'

QUOTE = ["…there's", "some", "<em>AI", "washing</em>", "where", "people", "are", "blaming", "AI", "for", "layoffs…"]

SCENE_HTML = {
"s1": photo("s1", "s1ph", '<div class="lgpill">USA · Jan–Oct 2026</div>') + f"""
<div class="card big" id="s1card">{sheen("s1sh")}
 <div class="lbl">US job cuts where companies cited <span style="color:var(--red)">AI</span></div>
 <div class="num">{odo("s1n", "121,401", 160)}</div>
 <div class="bars"><div class="bar" id="s1b0"><i></i><span>2025 · full year · 54,836</span></div>
  <div class="bar" id="s1b1"><i></i><span>2026 · Jan–Oct · 121,401</span></div></div>
 <div class="x2" id="s1x2">2.2×</div>
</div>
<div class="rly" id="s1rly">Really, bro?</div>
{burst("s1bu", 800, 520)}""",
"s2": photo("s2", "s2ph", f'<div class="tag">Sam Altman<small>{logo("openai","ol")}CEO, OpenAI</small></div>') + """
<div class="card quote" id="s2q"><div class="qm">“</div><p>""" + "".join(f'<span id="s2w{i}">{w}</span>' for i, w in enumerate(QUOTE)) + """</p>
 <small>Sam Altman · Feb 2026</small></div>
<div class="card defn" id="s2d"><span class="pill red">AI-washing</span><p>= blaming layoffs on AI, even when the cuts may have little to do with it</p></div>""",
"s3": photo("s3", "s3ph", f'<div class="lgpill">{logo("cloudflare")}Cloudflare</div><div class="pill white datepill">May 7, 2026</div>') + f"""
<div class="card rev" id="s3rev"><div class="kick">REVENUE</div><b>Record quarter</b><div class="up">+34%</div>
 <svg viewBox="0 0 417 170"><path id="s3line" d="M10 150 L110 118 L200 128 L300 66 L405 18"/></svg></div>
<div class="card jobs" id="s3jobs"><div class="kick">JOBS CUT</div><div class="num">~{odo("s3n", "1,100", 126)}</div><small>about 20% of staff</small>
 <div class="dn" id="s3dn">{DOWN}</div></div>
<div class="pill red cited" id="s3cited">Company cited AI</div>""",
"s4": photo("s4", "s4ph", '<div class="tag">Wix HQ<small>one of three companies citing AI</small></div>') + f"""
<div class="co3">
 <div class="card coc" id="s4c0">{logo("wix")}<b>Wix</b><small>~1,000 jobs · May</small><span class="pill red ct" id="s4t0">cited AI</span></div>
 <div class="card coc" id="s4c1">{logo("snap")}<b>Snap</b><small>~1,000 jobs · Apr</small><span class="pill red ct" id="s4t1">cited AI</span></div>
 <div class="card coc" id="s4c2">{logo("block","","png")}<b>Block</b><small>~4,000 jobs · Feb</small><span class="pill red ct" id="s4t2">cited AI</span></div>
</div>""",
"s5": """<div class="tw"><div class="but" id="s5but">But here's the…</div>
 <svg viewBox="0 0 800 560"><path id="s5arc" d="M120 470 C 0 300, 160 40, 420 50 S 800 180, 740 360 S 520 540, 380 470"/></svg>
 <div class="word">""" + "".join(f'<span id="s5l{i}">{c}</span>' for i, c in enumerate("TWIST")) + "</div></div>" + burst("s5bu", 480, 330, 18),
"s6": photo("s6", "s6ph", '<div class="gt">Gartner</div><div class="pill white datepill">May 2026 study</div>') + f"""
<div class="card find" id="s6find"><div class="ne">≠</div><p>No link between AI-related job cuts and better returns</p></div>
<div class="card donut" id="s6don"><svg viewBox="0 0 180 180"><circle class="bgc" cx="90" cy="90" r="70"/><circle class="fg" id="s6arc" cx="90" cy="90" r="70"/></svg>
 <div><b>~20%</b><small>of all 617,189 US cuts cited AI</small></div></div>
<div class="card total" id="s6tot"><div class="kick">ALL US CUTS · JAN–OCT</div><div class="big2" id="s6pct">↓44%</div><small>vs the same months of 2025</small></div>""",
"s7": photo("s7", "s7ph", '<div class="tag">AI is changing<small>some jobs for real</small></div>') + """
<div class="card chart" id="s7ch"><div class="kick">AI'S SHARE OF US LAYOFF ANNOUNCEMENTS</div><h4>2026, by month</h4>
 <svg viewBox="0 0 510 330"><line class="gl" x1="0" y1="300" x2="510" y2="300"/><line class="gl" x1="0" y1="170" x2="510" y2="170"/><line class="gl" x1="0" y1="40" x2="510" y2="40"/>
  <path class="ln" id="s7ln" d="M30 254.5 L250 137.5 L360 131 L470 40"/>""" + "".join(
    f'<circle class="pt" id="s7p{i}" cx="{x}" cy="{y}" r="12"/><text class="v" id="s7v{i}" x="{x}" y="{y-26}" text-anchor="middle">{v}%</text><text x="{x}" y="330" text-anchor="middle">{m}</text>'
    for i, (x, y, v, m) in enumerate([(30, 254.5, 7, "Jan"), (250, 137.5, 25, "Mar"), (360, 131, 26, "Apr"), (470, 40, 40, "May")])) + """</svg>
 <span class="pill red may" id="s7may">May: 38,579 cuts</span></div>
<div class="card tech" id="s7tech"><div class="kick">US TECH JOB CUTS · H1 2026</div><div class="num">""" + odo("s7n", "139,156", 100) + """</div><span class="pill green" id="s7pct">↑83%</span></div>""",
"s8": """<div class="vs"><span>AI?</span><span class="v" id="s8v">VS</span><span>EXCUSE?</span></div>
<div class="card colA" id="s8a"><h3>AI is real</h3>
 <div class="pt8" id="s8a0">AI's share of cuts: <b>7% → 40%</b> (Jan → May)</div>
 <div class="pt8" id="s8a1">US tech cuts: <b>+83%</b> (H1 2026)</div>
 <div class="pt8" id="s8a2">Cloudflare, Snap, Block: <b>company says AI</b></div></div>
<div class="card colB" id="s8b"><h3>Could be an excuse</h3>
 <div class="pt8" id="s8b0">All US cuts: <b>↓44%</b> vs 2025</div>
 <div class="pt8" id="s8b1">Gartner: <b>no proven returns</b></div>
 <div class="pt8" id="s8b2">Altman, Andreessen: <b>"AI-washing" / over-hiring</b></div>
 <div class="pt8" id="s8b3">October: AI cited in only <b>1,265</b> cuts</div></div>""",
"s9": f"""<div class="card igc" id="s9cmt"><div class="igh">{logo("instagram","iglogo")}<b>Comments</b></div>
 <div class="cm"><div class="av"></div><div class="ct"><small>you · now</small><div class="typed">""" + "".join(f'<span id="s9ch{i}">{c}</span>' for i, c in enumerate("LAYOFF")) + """<span class="cur">|</span></div></div></div>
 <div class="cm pinned" id="s9pin"><div class="av nx">N</div><div class="ct"><small><svg viewBox="0 0 24 24"><path d="M16 3l5 5-3 1-4 4 1 5-2 2-4-4-5 5-1-1 5-5-4-4 2-2 5 1 4-4z"/></svg> Pinned · nextup</small><div class="rep">link + 5 prompts</div></div></div>
 <div class="frow"><div class="follow" id="s9fol">Follow</div><div class="heart" id="s9heart">❤</div></div>""" + CURSOR.format(id="s9curs") + ripple("s9rip") + "</div>",
}
SOURCES = {"s1": "Challenger, Gray & Christmas, Oct 2026 report", "s2": "Altman to CNBC-TV18, India AI Impact Summit",
           "s3": "Cloudflare Q1 2026 results & staff memo", "s4": "Company statements, 2026",
           "s6": "Gartner study, May 2026 · Challenger, Gray & Christmas", "s7": "Challenger, Gray & Christmas, 2026 reports"}
EXTRA = {"s8": '<div class="qmark" id="s8q"><b>?</b><small>What do<br>you think?</small></div>'}

def pop(sel, t, frm="scale:.6,opacity:0,y:60", ease="back.out(2)", d=.42, snd="pop"):
    if snd: sfx(snd, t)
    return f'tl.fromTo("{sel}",{{{frm}}},{{scale:1,opacity:1,y:0,x:0,rotation:0,duration:{d},ease:"{ease}"}},{t:.2f});'

def anim(sid):
    a, b = SC[sid]; J = []; add = J.append; u = lambda f: T(sid, f)
    add(f'tl.fromTo("#{sid}w",{{opacity:0,y:120,rotationX:24,scale:.92,filter:"blur(12px)"}},{{opacity:1,y:0,rotationX:0,scale:1,filter:"blur(0px)",duration:{.32 if sid=="s5" else .5},ease:"expo.out"}},{a+.02:.2f});')
    if sid != "s9":
        add(f'tl.to("#{sid}w",{{x:-520,opacity:0,filter:"blur(16px)",duration:.26,ease:"power3.in"}},{b-.28:.2f});')
    add(f'tl.fromTo("#{sid}push",{{scale:1}},{{scale:1.04,duration:{b-a:.2f},ease:"none"}},{a:.2f});')
    if os.path.exists(f"assets/photos/{sid}.jpg"):
        add(f'tl.fromTo("#{sid}phi",{{scale:1.18}},{{scale:1,duration:{b-a:.2f},ease:"power1.out"}},{a:.2f});')
    if sid in SOURCES:
        add(f'tl.fromTo("#{sid}src",{{opacity:0,x:60}},{{opacity:1,x:0,duration:.35,ease:"expo.out"}},{a+.45:.2f});')
        add(f'tl.to("#{sid}src",{{opacity:0,duration:.2}},{b-.28:.2f});')
    if sid == "s1":
        add(pop("#s1card", u(.08), "y:200,opacity:0,scale:.95", "expo.out", .5, "whoosh"))
        add(odo_js("s1n", "121,401", 160, u(.14), 1.5)); sfx("thud", u(.14) + 1.5)
        add(sheen_js("s1sh", u(.4)))
        for i, f in enumerate([.5, .6]):
            add(f'tl.fromTo("#s1b{i} i",{{scaleX:0}},{{scaleX:1,duration:.5,ease:"power3.out"}},{u(f):.2f});'); sfx("pop", u(f))
        add(pop("#s1x2", u(.7), "scale:0,rotation:-40,opacity:0", "back.out(3)", .35, "ding")); add(burst_js("s1bu", u(.7)))
        add(pop("#s1rly", u(.84), "scale:.3,opacity:0,y:40", "back.out(3)", .3))
        add(f'tl.fromTo("#s1card",{{x:0}},{{x:-14,duration:.05,yoyo:true,repeat:5}},{u(.86):.2f});')
    if sid == "s2":
        add(f'tl.fromTo("#s2ph",{{x:-300,opacity:0}},{{x:0,opacity:1,duration:.5,ease:"expo.out"}},{a+.05:.2f});')
        add(pop("#s2q", u(.14), "x:300,opacity:0", "expo.out", .45, "whoosh"))
        for i in range(len(QUOTE)):
            add(f'tl.fromTo("#s2w{i}",{{opacity:0,y:20}},{{opacity:1,y:0,duration:.18}},{u(.22) + i*.12:.2f});'); sfx("tick", u(.22) + i * .12)
        add(pop("#s2d", u(.62), "y:120,opacity:0", "expo.out", .45, "thud"))
        add(f'tl.fromTo("#s2d .pill",{{scale:1}},{{scale:1.15,duration:.15,yoyo:true,repeat:1}},{u(.7):.2f});')
    if sid == "s3":
        add(pop("#s3ph .lgpill", u(.06), "scale:0,opacity:0"))
        add(pop("#s3ph .datepill", u(.14), "scale:0,opacity:0"))
        add(pop("#s3rev", u(.24), "y:160,opacity:0", "expo.out", .45, "whoosh"))
        add(f'tl.fromTo("#s3line",{{strokeDashoffset:600}},{{strokeDashoffset:0,duration:.8,ease:"power2.inOut"}},{u(.3):.2f});'); sfx("shine", u(.3))
        add(pop("#s3jobs", u(.42), "y:160,opacity:0", "expo.out", .45, "whoosh"))
        add(odo_js("s3n", "1,100", 126, u(.48), 1.0))
        add(f'tl.fromTo("#s3dn",{{y:-40,opacity:0}},{{y:0,opacity:1,duration:.35,ease:"bounce.out"}},{u(.66):.2f});'); sfx("thud", u(.66))
        add(pop("#s3cited", u(.78), "scale:2.2,opacity:0,rotation:-12", "power4.in", .26, "thud"))
    if sid == "s4":
        for i, f in enumerate([.05, .2, .35]):
            add(pop(f"#s4c{i}", u(f), "y:-260,opacity:0,rotation:-8", "back.out(1.6)", .4, "thud"))
        for i in range(3):
            add(pop(f"#s4t{i}", u(.55) + i * .1, "scale:2,opacity:0", "power4.in", .2))
    if sid == "s5":
        add(f'tl.fromTo("#s5but",{{opacity:0,y:30}},{{opacity:1,y:0,duration:.2}},{a+.05:.2f});')
        for i in range(5):
            add(pop(f"#s5l{i}", a + .2 + i * .06, "y:-260,opacity:0,rotation:-25,scale:1.4", "back.out(2.5)", .3, None))
        sfx("shine", a + .2); sfx("thud", a + .45)
        add(f'tl.fromTo("#s5arc",{{strokeDashoffset:1900}},{{strokeDashoffset:0,duration:.55,ease:"power2.inOut"}},{a+.25:.2f});')
        add(burst_js("s5bu", a + .45, 18, 260))
    if sid == "s6":
        add(pop("#s6ph .gt", u(.06), "scale:0,opacity:0"))
        add(pop("#s6ph .datepill", u(.12), "scale:0,opacity:0"))
        add(pop("#s6find", u(.2), "x:300,opacity:0", "expo.out", .45, "whoosh"))
        add(f'tl.fromTo("#s6find .ne",{{rotation:-90,scale:0}},{{rotation:0,scale:1,duration:.4,ease:"back.out(3)"}},{u(.26):.2f});')
        add(pop("#s6don", u(.48), "y:140,opacity:0", "expo.out", .4, "pop"))
        add(f'tl.fromTo("#s6arc",{{strokeDashoffset:440}},{{strokeDashoffset:352,duration:.7,ease:"power2.out"}},{u(.52):.2f});')
        add(pop("#s6tot", u(.6), "y:140,opacity:0", "expo.out", .4, "pop"))
        add(pop("#s6pct", u(.68), "scale:2,opacity:0", "power4.in", .25, "thud"))
    if sid == "s7":
        add(f'tl.fromTo("#s7ph",{{x:-300,opacity:0}},{{x:0,opacity:1,duration:.5,ease:"expo.out"}},{a+.05:.2f});')
        add(pop("#s7ch", u(.1), "x:300,opacity:0", "expo.out", .45, "whoosh"))
        add(f'tl.fromTo("#s7ln",{{strokeDashoffset:700}},{{strokeDashoffset:0,duration:1.3,ease:"power1.inOut"}},{u(.2):.2f});')
        for i, f in enumerate([0, .4, .62, 1.0]):
            t = u(.2) + f * 1.3
            add(f'tl.fromTo("#s7p{i}",{{scale:0,transformOrigin:"50% 50%"}},{{scale:1,duration:.25,ease:"back.out(3)"}},{t:.2f});')
            add(f'tl.fromTo("#s7v{i}",{{opacity:0}},{{opacity:1,duration:.2}},{t:.2f});'); sfx("pop", t)
        add(pop("#s7may", u(.2) + 1.45, "scale:0,opacity:0", "back.out(3)", .35, "ding"))
        add(pop("#s7tech", u(.6), "y:160,opacity:0", "expo.out", .45, "whoosh"))
        add(odo_js("s7n", "139,156", 100, u(.64), 1.1))
        add(pop("#s7pct", u(.82), "scale:0,opacity:0,rotation:-20", "back.out(3)", .3, "ding"))
    if sid == "s8":
        add(pop("#s8v", u(.04), "scale:0,opacity:0,rotation:-180", "back.out(2.5)", .4, "thud"))
        add(pop("#s8a", u(.1), "x:-300,opacity:0", "expo.out", .4, "whoosh"))
        add(pop("#s8b", u(.16), "x:300,opacity:0", "expo.out", .4, None))
        for i in range(3): add(pop(f"#s8a{i}", u(.24) + i * .22, "x:-60,opacity:0", "back.out(2)", .3))
        for i in range(4): add(pop(f"#s8b{i}", u(.42) + i * .2, "x:60,opacity:0", "back.out(2)", .3))
        add(f'tl.fromTo("#s8a",{{y:0}},{{y:16,duration:.5,ease:"sine.inOut",yoyo:true,repeat:3}},{u(.3):.2f});')
        add(f'tl.fromTo("#s8b",{{y:0}},{{y:-16,duration:.5,ease:"sine.inOut",yoyo:true,repeat:3}},{u(.3):.2f});')
        add(pop("#s8q", u(.76), "scale:0,opacity:0,rotation:-30", "back.out(2.5)", .4, "ding"))
        add(f'tl.fromTo("#s8q",{{rotation:0}},{{rotation:8,duration:.25,yoyo:true,repeat:3}},{u(.76)+.45:.2f});')
        add(f'tl.to("#s8q",{{opacity:0,duration:.2}},{b-.28:.2f});')
    if sid == "s9":
        for i in range(6):
            add(f'tl.fromTo("#s9ch{i}",{{opacity:0}},{{opacity:1,duration:.01}},{a+.3+i*.09:.2f});'); sfx("tick", a + .3 + i * .09)
        add(pop("#s9pin", BEAT["pin"], "y:-80,opacity:0", "bounce.out", .45))
        f = BEAT["follow"]
        add(f'tl.fromTo("#s9curs",{{x:760,y:760,opacity:0}},{{x:760,y:760,opacity:1,duration:.15}},{f-.5:.2f});tl.to("#s9curs",{{x:220,y:600,duration:.4,ease:"power3.inOut"}},{f-.4:.2f});')
        add(ripple_js("s9rip", f)); sfx("pop", f); add(f'tl.fromTo("#s9fol",{{backgroundColor:"#0095f6"}},{{backgroundColor:"#22c55e",duration:.15}},{f:.2f});')
        add(f'tl.fromTo("#s9heart",{{scale:0,opacity:0}},{{scale:1.4,opacity:1,duration:.25,ease:"back.out(4)"}},{f+.15:.2f});tl.to("#s9heart",{{scale:1,duration:.2}},{f+.4:.2f});'); sfx("ding", f + .15)
    return "\n".join(J)

# ---------- avatar: poses as scene fractions, lip-sync from voice RMS ----------
POSES_F = [("s1", 0, "shocked"), ("s1", .25, "n"), ("s1", .82, "what"),
           ("s2", 0, "point_right"), ("s2", .3, "n"),
           ("s3", 0, "thinking"), ("s3", .28, "n"),
           ("s4", 0, "count"), ("s4", .45, "n"),
           ("s5", 0, "surprised"),
           ("s6", 0, "point_up"), ("s6", .25, "n"),
           ("s7", 0, "point_right"), ("s7", .25, "n"), ("s7", .8, "thumbs_up"),
           ("s8", 0, "thinking"), ("s8", .3, "n"), ("s8", .78, "what"),
           ("s9", 0, "slice"), ("s9", .1, "slice2"), ("s9", .2, "slice3"), ("s9", .3, "n")]
POSES = sorted([(T(s, f), p) for s, f, p in POSES_F] + [(BEAT["follow"] - .1, "wave"), (BEAT["follow"] + 1.2, "n")])
POSE_FILES = sorted({p for _, p in POSES if p != "n"})
rms = [float(m) if "inf" not in m else -90.0 for m in re.findall(r"RMS_level=(-?[\d.]+|-?inf)", open(f"tools/rms_{LANG}.txt").read())]
def mouth_at(i):
    db = rms[i] if i < len(rms) else -90
    if db < -40: return "m_closed"
    if db < -31: return "m_small"
    if db < -24: return "m_round" if (i // 3) % 2 else "m_open"
    return "m_teeth" if (i // 4) % 3 == 0 else "m_open"
mouth = [mouth_at(i) for i in range(int(DUR * FPS))]
for i in range(1, len(mouth) - 1):
    if mouth[i] != mouth[i - 1] and mouth[i + 1] != mouth[i]: mouth[i] = mouth[i - 1]
MOUTHS = ["m_closed", "m_small", "m_round", "m_open", "m_teeth"]
def pose_at(t):
    cur = POSES[0][1]
    for s, p in POSES:
        if t >= s: cur = p
    return cur

# ---------- assemble ----------
scene_divs, scene_js, bg_js = [], [], []
for i, sid in enumerate(IDS):
    a, b = SC[sid]
    extra = (src(sid, SOURCES[sid]) if sid in SOURCES else "") + EXTRA.get(sid, "")
    scene_divs.append(f'<div id="{sid}" class="clip scene" data-start="{a}" data-duration="{b - a:.2f}" data-track-index="2" data-track-kind="graphics" data-layout-allow-overflow>'
                      f'<div class="push" id="{sid}push"><div class="wrap" id="{sid}w">{SCENE_HTML[sid]}</div></div>{extra}</div>')
    scene_js.append(anim(sid))
    bg_js.append(f'tl.to(".blob",{{backgroundColor:"{COLS[i]}",duration:.5,ease:"power1.inOut"}},{max(0, a - .1):.2f});')
    if a > 0:
        bg_js.append(f'tl.fromTo("#flash",{{opacity:0,x:-1100}},{{opacity:.9,x:1100,duration:.32,ease:"power2.inOut"}},{a - .16:.2f});'); sfx("whoosh", a - .14)

pose_imgs = "".join(f'<img id="p_{p}" class="pose" src="assets/avatar/{p}.png" alt="">' for p in POSE_FILES)
mouth_imgs = "".join(f'<img id="{m}" class="mouth" src="assets/avatar/mouth/{m}.png" alt="">' for m in MOUTHS)
av_js, prev_pose, prev_m = [], None, None
for f in range(int(OUTRO * FPS)):
    t = round(f / FPS, 3); p = pose_at(t)
    if p != prev_pose:
        for q in POSE_FILES + ["n"]:
            av_js.append(f'tl.set("{"#neutral" if q == "n" else "#p_" + q}",{{opacity:{1 if q == p else 0}}},{t});')
        if t > 0: av_js.append(f'tl.fromTo("#avpop",{{scale:.94}},{{scale:1,duration:.18,ease:"back.out(3)",immediateRender:false}},{t});')
        prev_pose = p
    m = mouth[f] if p == "n" else "m_closed"
    if m != prev_m:
        for q in MOUTHS: av_js.append(f'tl.set("#{q}",{{opacity:{1 if q == m else 0}}},{t});')
        prev_m = m
av_js.append(f'tl.fromTo("#avbreath",{{y:0}},{{y:-8,duration:1.6,ease:"sine.inOut",yoyo:true,repeat:{int(OUTRO/1.6)}}},0);')
av_js.append(f'tl.to("#avpop",{{y:500,opacity:0,duration:.35,ease:"power2.in",immediateRender:false}},{OUTRO-.3:.2f});')
sfx("whoosh", OUTRO - .1); sfx("shine", OUTRO + .7)

outro_js = f"""tl.fromTo("#outro",{{clipPath:"circle(0% at 30% 72%)"}},{{clipPath:"circle(150% at 30% 72%)",duration:.7,ease:"power3.inOut"}},{OUTRO:.2f});
tl.fromTo("#outlogo",{{scale:.7,opacity:0}},{{scale:1,opacity:1,duration:.6,ease:"expo.out"}},{OUTRO+.25:.2f});
tl.fromTo("#outsheen",{{x:-600}},{{x:1400,duration:.9,ease:"power2.inOut"}},{OUTRO+.7:.2f});"""

CSS = open("tools/style.css").read().replace("__RED__", RED)
page = f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8"/>
<meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script>
<style>
{CSS}
.mouth{{position:absolute;left:{428*780/1024:.1f}px;top:{362*780/1024:.1f}px;width:{200*780/1024:.1f}px;height:{170*780/1024:.1f}px;opacity:0}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
 <div id="bgclip" class="clip" data-start="0" data-duration="{DUR}" data-track-index="0" data-layout-ignore style="position:absolute;inset:0"><div id="bg"></div><div class="blob" id="b1"></div><div class="blob" id="b2"></div><div id="grid"></div><div id="flash"></div></div>
 {''.join(scene_divs)}
 <div id="avatar" class="clip" data-start="0" data-duration="{OUTRO:.2f}" data-track-index="4" data-layout-ignore><div id="avpop"><div id="avbreath">
  {pose_imgs}<div id="neutral"><img class="base" src="assets/avatar/m_closed.png" alt="">{mouth_imgs}</div></div></div></div>
 <div id="outroclip" class="clip" data-start="{OUTRO}" data-duration="{DUR-OUTRO:.2f}" data-track-index="6" data-layout-ignore style="position:absolute;inset:0"><div id="outro"><div id="outsheen"></div><div id="outlogo"><img src="assets/img/logo_h.png" alt="NextUp Learn"></div></div></div>
 <audio id="voice" src="assets/audio/voice_{LANG}.mp3" data-start="0" data-duration="{VOICE_DUR}" data-track-index="10"></audio>
 <audio id="sfx" src="assets/audio/sfx_{LANG}.wav" data-start="0" data-duration="{DUR}" data-track-index="11"></audio>
</div>
<script>
const tl=gsap.timeline({{paused:true}});
tl.fromTo("#b1",{{x:0,y:0}},{{x:160,y:120,duration:{DUR},ease:"sine.inOut"}},0);tl.fromTo("#b2",{{x:0,y:0}},{{x:-200,y:-160,duration:{DUR},ease:"sine.inOut"}},0);
{chr(10).join(bg_js)}
{chr(10).join(scene_js)}
{chr(10).join(av_js)}
{outro_js}
window.__timelines={{main:tl}};
</script>
</body></html>
"""
open("index.html", "w").write(page)
json.dump(sorted(SFX, key=lambda e: e[1]), open(f"tools/sfx_events_{LANG}.json", "w"))
print(f"index.html ({LANG}) written:", len(page) // 1024, "KB;", len(SFX), "sfx events")
