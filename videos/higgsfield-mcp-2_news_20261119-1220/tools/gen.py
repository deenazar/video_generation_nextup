#!/usr/bin/env python3
"""NextUp reel: Higgsfield MCP 2.0 | News | Warning/Alert | ~45 s (English voice).
Run from this folder:  python3 tools/gen.py en   ->  index.html + tools/sfx_events_en.json
Full-screen real Higgsfield images with a bottom black gradient, real logos, the avatar low on the
left with phoneme lip-sync (tools/lipsync.py), and the NextUp outro."""
import html, json, math, sys
sys.path.insert(0, "tools")
from lipsync import visemes

LANG = sys.argv[1] if len(sys.argv) > 1 else "en"
FPS, DUR, OUTRO, RED = 30, 46.0, 43.4, "#ea333f"
VOICE_DUR = 44.0

# scene starts, from the Whisper word times (hook, lead, body 1, loop 1, body 2, loop 2, body 3, CTA)
STARTS = [0, 6.6, 9.45, 19.2, 21.9, 28.8, 31.6, 39.5]
IDS = [f"s{i + 1}" for i in range(len(STARTS))]
SC = {sid: (STARTS[i], (STARTS + [OUTRO])[i + 1]) for i, sid in enumerate(IDS)}

# full-screen backgrounds: real images from higgsfield.ai (file, object-position)
# Real Higgsfield image only where it fits the beat (with the bottom black gradient);
# everywhere else a designed background: blue grid, white grid, plain white, plain grey.
BG = {"s1": ("img", "default.jpg", "62% 50%"),            # hook: Higgsfield's own hero image
      "s2": ("bluegrid",), "s3": ("whitegrid",), "s4": ("grey",), "s5": ("bluegrid",),
      "s6": ("img", "genjutsu-intro-poster.webp", "50% 50%"),  # "matters to YOU": a creator
      "s7": ("whitegrid",), "s8": ("white",)}

SFX = []
def sfx(kind, t): SFX.append((kind, round(t, 3)))
def esc(s): return html.escape(s, quote=True)
def logo(name, cls="lg"): return f'<img class="{cls}" src="assets/logos/{name}.svg" alt="{name}">'
HF = logo("higgsfield_dark", "lg")

# ---------- building blocks ----------
def burst(bid, x, y, n=14):
    return f'<div class="burst" id="{bid}" style="left:{x}px;top:{y}px">' + "".join(f'<i id="{bid}_{k}"></i>' for k in range(n)) + '</div>'
def burst_js(bid, t, n=14, r=170):
    out = [f'tl.set("#{bid}",{{opacity:1}},{t:.2f});tl.to("#{bid}",{{opacity:0,duration:.25}},{t + .45:.2f});']
    for k in range(n):
        a = k / n * 6.2832
        out.append(f'tl.fromTo("#{bid}_{k}",{{x:0,y:0,scale:1}},{{x:{math.cos(a) * r:.0f},y:{math.sin(a) * r:.0f},scale:.2,duration:.6,ease:"power3.out"}},{t:.2f});')
    return "\n".join(out)
def sheen(sid): return f'<div class="sheen" id="{sid}"></div>'
def sheen_js(sid, t): return f'tl.fromTo("#{sid}",{{x:-300}},{{x:1300,duration:.9,ease:"power2.inOut"}},{t:.2f});'
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
CURSOR = '<svg class="cursor" id="{id}" viewBox="0 0 24 24"><path d="M4 2l15 10-7 1.5 4 7.5-3 1.5-4-7.5-5 4.5z"/></svg>'
def ripple(rid, x, y): return f'<div class="ripple" id="{rid}" style="left:{x}px;top:{y}px"></div>'
def ripple_js(rid, t): return f'tl.fromTo("#{rid}",{{scale:.2,opacity:.9}},{{scale:2.4,opacity:0,duration:.5,ease:"power2.out"}},{t:.2f});'
def typed(pid, text): return " ".join("".join(f'<span id="{pid}{k}">{esc(c)}</span>' for k, c in w) for w in _words(text))
def _words(text):
    out, cur = [], []
    for i, c in enumerate(text):
        if c == " ": out.append(cur); cur = []
        else: cur.append((i, c))
    return out + [cur]
def typed_js(pid, text, t, step=.03):
    out = []
    for i, c in enumerate(text):
        if c == " ": continue
        out.append(f'tl.fromTo("#{pid}{i}",{{opacity:0}},{{opacity:1,duration:.01}},{t + i * step:.3f});')
        if i % 2 == 0: sfx("tick", t + i * step)
    return "\n".join(out)
def num(n, sid): return f'<div class="numchip" id="{sid}num"><b>{n}</b></div>'
WARN = '<svg viewBox="0 0 24 24"><path d="M12 3L2 21h20L12 3z" fill="#fff"/><path d="M12 10v5M12 17.6v.4" stroke="#ea333f" stroke-width="2.4" stroke-linecap="round"/></svg>'
LOCK = ('<svg viewBox="0 0 48 48"><path id="s5shackle" d="M15 22v-7a9 9 0 0118 0v7" fill="none" stroke="#0f172a" stroke-width="4.5" stroke-linecap="round"/>'
        '<rect x="9" y="22" width="30" height="21" rx="5" fill="#0f172a"/><circle cx="24" cy="31" r="3.2" fill="#fff"/><path d="M24 33v4" stroke="#fff" stroke-width="3" stroke-linecap="round"/></svg>')
COIN = '<div class="hcoin"><img src="assets/logos/higgsfield.svg" alt=""></div>'
def tile(name, tid, cls="tile"): return f'<div class="{cls}" id="{tid}"><img src="assets/logos/{name}.svg" alt="{name}"></div>'
def logo_in(sel, t, frm="scale:0,rotation:-200,opacity:0", d=.55, snd="pop"):
    if snd: sfx(snd, t)
    return f'tl.fromTo("{sel}",{{{frm}}},{{scale:1,rotation:0,opacity:1,x:0,y:0,duration:{d},ease:"back.out(2.2)"}},{t:.2f});'
def wobble(sel, t, deg=10, n=3): return f'tl.fromTo("{sel}",{{rotation:0}},{{rotation:{deg},duration:.12,yoyo:true,repeat:{n},ease:"sine.inOut",immediateRender:false}},{t:.2f});'
def pulse(sel, t, s=1.18): return f'tl.fromTo("{sel}",{{scale:1}},{{scale:{s},duration:.14,yoyo:true,repeat:1,ease:"power2.out",immediateRender:false}},{t:.2f});'
PLAY = '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="11" fill="rgba(15,23,42,.6)"/><path d="M10 7.5l7 4.5-7 4.5z" fill="#fff"/></svg>'

HOOK = [("Free,", 1.71), ("unlimited", 2.25), ("video", 2.82), ("inside", 3.2)]
SCENE_HTML = {
"s1": f"""<div class="alert" id="s1al">{WARN}<span>HEADS UP</span></div>
<div class="card claim" id="s1card">{sheen("s1sh")}
 <div class="who">{HF}<b>Higgsfield</b><small>says</small></div>
 <div class="qm">“</div>
 <div class="hook">""" + "".join(f'<span id="s1w{i}">{w}</span>' for i, (w, _) in enumerate(HOOK)) +
 f"""<span class="cl" id="s1cl">{logo("claude", "cll")}Claude</span></div>
</div>
<div class="plug" id="s1plug">{tile("higgsfield_dark", "s1hf", "tile big")}<svg class="wire" viewBox="0 0 360 40"><path id="s1wire" d="M5 20 C 90 -10, 270 50, 355 20"/></svg>{tile("claude", "s1ct", "tile big")}</div>
<div class="stamp" id="s1st">NOT THE WHOLE STORY</div>{burst("s1bu", 480, 640)}{burst("s1bu2", 480, 780, 12)}""",

"s2": f"""<div class="card lead" id="s2card">
 <div class="three">""" + "".join(f'<div class="dot" id="s2d{i}">{i + 1}</div>' for i in range(3)) + f"""</div>
 <h2 id="s2h"><span class="red">3 things</span> to know</h2>
 <p id="s2p">before you connect it</p>
</div>
<div class="connect" id="s2btn">{logo("higgsfield", "lgw")}Connect to Claude</div>
<div class="wait" id="s2wait">✋ Wait</div>
{CURSOR.format(id="s2cur")}{ripple("s2rip", 540, 615)}""",

"s3": f"""{num(1, "s3")}<div class="kicker" id="s3k">What happened</div>
<div class="card ann" id="s3ann"><img class="annimg" src="assets/photos/mcp-og-chatgpt-claude-20260925.webp" alt="">
 <div class="annbar"><span class="pill dark" id="s3mcp">{logo("higgsfield", "lgw")}Higgsfield MCP <b class="v2" id="s3v2">2.0</b></span>
 <span class="pill white" id="s3in">inside {logo("claude", "lgi")}Claude</span></div></div>
<div class="duo" id="s3duo">{tile("higgsfield_dark", "s3hf", "tile big")}<div class="plus" id="s3plus">+</div>{tile("claude", "s3ct", "tile big")}<div class="mcpb" id="s3mcpb">MCP 2.0</div></div>{burst("s3bu", 480, 760, 16)}
<div class="card chat" id="s3chat">
 <div class="chead">{logo("claude", "lgc")}<b>Claude</b><span class="hfc">{logo("higgsfield_dark", "lgs")}Higgsfield connected</span></div>
 <div class="ub" id="s3ub">{typed("s3t", "Make a 15s launch video for my sneakers")}</div>
 <div class="cb" id="s3cb"><span class="spin" id="s3spin"></span>Running video models for you…</div>
 <div class="models">
  <div class="model" id="s3m0">{logo("deepmind", "lgm")}<b>Veo</b><i><u id="s3p0"></u></i></div>
  <div class="model" id="s3m1">{logo("kling", "lgm")}<b>Kling</b><i><u id="s3p1"></u></i></div>
  <div class="model" id="s3m2">{logo("bytedance", "lgm")}<b>Seedance</b><i><u id="s3p2"></u></i></div>
 </div>
</div>""" + "".join(burst(f"s3mb{i}", 70, 470 + i * 92, 10) for i in range(3)),

"s4": f"""<div class="card loop" id="s4card">
 <div class="free"><span class="q">“</span><span id="s4free">FREE</span><span class="q">”</span>
 <svg class="strike" viewBox="0 0 600 60"><path id="s4line" d="M10 40 C 160 10, 380 60, 590 18"/></svg></div>
 <div class="qbig" id="s4q">?</div>
 <div class="ptag" id="s4tag"><img src="assets/logos/higgsfield_dark.svg" alt=""><span>$0?</span></div>
 <div class="next" id="s4next">That's point two →</div>
</div>{burst("s4bu", 760, 380, 12)}""",

"s5": f"""{num(2, "s5")}<div class="kicker" id="s5k">The catch</div>
<div class="card catch" id="s5a"><div class="ic cal"><div class="days">""" + "".join(f'<span id="s5day{i}">{i + 1}</span>' for i in range(3)) + """</div></div>
 <div><b>3-day trial</b><small>then it ends</small></div><span class="pill red tagr" id="s5end">ends</span></div>
<div class="card catch" id="s5b"><div class="ic">""" + LOCK + """</div>
 <div><b>Paid plan to connect</b><small>says Higgsfield's own docs</small></div></div>
<div class="card catch" id="s5c"><div class="ic">""" + COIN + """</div>
 <div class="cw"><b>Every video uses credits</b><div class="meter"><u id="s5meter"></u></div></div></div>
""" + "".join(f'<div class="coin" id="s5coin{i}">{COIN}</div>' for i in range(5)),

"s6": """<div class="card why" id="s6card"><div class="p3" id="s6p3">Point three</div>
 <h2>is why this matters to <span class="you" id="s6you">YOU</span></h2></div>
<div class="arrow" id="s6arr"><svg viewBox="0 0 120 200"><path d="M60 10 C 90 70, 20 110, 60 180 M30 150 L60 185 L92 150"/></svg></div>""",

"s7": f"""{num(3, "s7")}<div class="kicker" id="s7k">What's next</div>
<div class="card stat" id="s7card">{sheen("s7sh")}
 <div class="sh">{HF}<b>Higgsfield says</b></div>
 <div class="lbl">agent-tool usage</div>
 <div class="row"><div class="n42" id="s7big">{odo("s7n", "42", 220)}<span class="x">×</span></div><span class="pill red" id="s7m">in 3 months</span></div>
 <div class="rider" id="s7ride">{tile("higgsfield", "s7rt", "tile dark")}</div><svg class="curve" viewBox="0 0 860 200"><path class="base" d="M10 190 H850"/><path id="s7c" d="M10 186 C 300 184, 520 170, 640 120 S 800 20, 850 8"/></svg>
</div>
<div class="card vchat" id="s7v"><div class="vb"><img src="assets/photos/robot-pop-cover-web-poster.webp" alt=""><div class="play">{PLAY}</div></div>
 {tile("claude", "s7cl", "tile sm")}<div class="vt">Video is moving <span class="hl" id="s7hl">into chat</span></div></div>{burst("s7bu", 300, 470, 14)}""",

"s8": f"""<div class="card poll" id="s8poll"><div class="igh">{logo("instagram", "iglogo")}<b>Would you pay for it?</b></div>
 <div class="opt" id="s8o0"><i id="s8f0"></i><span>Yes, worth it</span></div>
 <div class="opt" id="s8o1"><i id="s8f1"></i><span>No, I'll wait</span></div>
 <div class="cmt" id="s8cmt">Let me know below ↓</div>
 <div class="frow"><div class="follow" id="s8fol">Follow</div>{tile("claude", "s8a", "tile sm")}{tile("higgsfield_dark", "s8b", "tile sm")}<div class="heart" id="s8heart">❤</div></div>
 {CURSOR.format(id="s8cur")}{ripple("s8rip", 190, 650)}</div>""",
}
SOURCES = {"s3": "Higgsfield MCP announcement", "s5": "Higgsfield docs & pricing", "s7": "Higgsfield"}


def pop(sel, t, frm="scale:.6,opacity:0,y:60", ease="back.out(2)", d=.42, snd="pop"):
    if snd: sfx(snd, t)
    return f'tl.fromTo("{sel}",{{{frm}}},{{scale:1,opacity:1,y:0,x:0,rotation:0,duration:{d},ease:"{ease}"}},{t:.2f});'


def anim(sid):
    a, b = SC[sid]; J = []; add = J.append
    add(f'tl.fromTo("#{sid}w",{{opacity:0,y:120,rotationX:20,scale:.94,filter:"blur(12px)"}},{{opacity:1,y:0,rotationX:0,scale:1,filter:"blur(0px)",duration:.5,ease:"expo.out"}},{a + .02:.2f});')
    add(f'tl.to("#{sid}w",{{x:-520,opacity:0,filter:"blur(16px)",duration:.26,ease:"power3.in"}},{b - .28:.2f});')
    if BG[sid][0] == "img":
        add(f'tl.fromTo("#{sid}bgi",{{scale:1.16}},{{scale:1.02,duration:{b - a:.2f},ease:"power1.out"}},{a:.2f});')
    else:
        add(f'tl.fromTo("#{sid}bgi",{{x:0,y:0}},{{x:-72,y:-72,duration:{b - a:.2f},ease:"none"}},{a:.2f});')
    if a > 0: add(f'tl.fromTo("#{sid}bg",{{opacity:0}},{{opacity:1,duration:.3,ease:"power1.out"}},{a - .05:.2f});')
    if sid in SOURCES:
        add(f'tl.fromTo("#{sid}src",{{opacity:0,x:60}},{{opacity:1,x:0,duration:.35,ease:"expo.out"}},{a + .6:.2f});')
        add(f'tl.to("#{sid}src",{{opacity:0,duration:.2}},{b - .28:.2f});')
    if sid in ("s3", "s5", "s7"):
        add(pop(f"#{sid}num", a + .1, "scale:0,opacity:0,rotation:-90", "back.out(3)", .4, "thud"))
        add(pop(f"#{sid}k", a + .25, "x:-80,opacity:0", "expo.out", .4, None))

    if sid == "s1":
        add(pop("#s1al", .15, "scale:0,opacity:0", "back.out(3)", .35, "pop"))
        add(f'tl.fromTo("#s1al",{{opacity:1}},{{opacity:.55,duration:.3,yoyo:true,repeat:9,ease:"sine.inOut"}},.6);')
        add(pop("#s1card", .3, "y:200,opacity:0,scale:.95", "expo.out", .5, "whoosh"))
        for i, (_, t) in enumerate(HOOK):
            add(pop(f"#s1w{i}", t - .05, "y:40,opacity:0,scale:.7", "back.out(3)", .3, "pop"))
        add(logo_in("#s1card .who .lg", .35, d=.7))
        add(pop("#s1cl", 3.66, "scale:0,opacity:0,rotation:-12", "back.out(3)", .35, "ding"))
        add(logo_in("#s1cl .cll", 3.66, "scale:0,rotation:-360,opacity:0", .6, None))
        add(pop("#s1plug", 3.75, "y:60,opacity:0", "expo.out", .3, None))
        add(logo_in("#s1hf", 3.75, "x:-300,rotation:-360,opacity:0", .5, "whoosh"))
        add(logo_in("#s1ct", 3.95, "x:300,rotation:360,opacity:0", .5, None))
        add(f'tl.fromTo("#s1wire",{{strokeDashoffset:400}},{{strokeDashoffset:0,duration:.35,ease:"power2.out"}},4.15);'); sfx("shine", 4.15)
        add(burst_js("s1bu2", 4.45, 12, 140))
        add(sheen_js("s1sh", 3.9))
        add(f'tl.fromTo("#s1st",{{scale:2.6,opacity:0,rotation:-24}},{{scale:1,opacity:1,rotation:-8,duration:.24,ease:"power4.in"}},4.6);'); sfx("thud", 4.84)
        add(burst_js("s1bu", 4.84, 16, 260))
        add(f'tl.fromTo("#s1card",{{x:0}},{{x:-16,duration:.05,yoyo:true,repeat:5}},4.86);')
        add(f'tl.fromTo("#s1card .hook",{{opacity:1}},{{opacity:.35,duration:.4}},5.2);')

    if sid == "s2":
        add(pop("#s2card", a + .05, "y:160,opacity:0", "expo.out", .45, "whoosh"))
        for i in range(3): add(pop(f"#s2d{i}", 7.0 + i * .14, "scale:0,opacity:0", "back.out(3)", .3, "pop"))
        add(pop("#s2h", 7.04, "y:30,opacity:0", "expo.out", .35, None))
        add(pop("#s2p", 7.75, "y:30,opacity:0", "expo.out", .35, None))
        add(pop("#s2btn", 7.95, "y:80,opacity:0", "back.out(2)", .35, "pop"))
        add(logo_in("#s2btn .lgw", 8.0, d=.6, snd=None))
        add(pulse("#s2btn", 8.7, 1.08))
        add(f'tl.fromTo("#s2cur",{{x:900,y:900,opacity:0}},{{x:900,y:900,opacity:1,duration:.15}},8.2);tl.to("#s2cur",{{x:525,y:600,duration:.4,ease:"power3.inOut"}},8.3);')
        add(ripple_js("s2rip", 8.7)); sfx("pop", 8.7)
        add(pop("#s2wait", 8.75, "scale:2.2,opacity:0,rotation:-15", "power4.in", .22, "thud"))

    if sid == "s3":
        add(pop("#s3ann", 9.65, "y:160,opacity:0", "expo.out", .5, "whoosh"))
        add(pop("#s3mcp", 10.3, "x:-120,opacity:0", "back.out(2)", .4, "pop"))
        add(pop("#s3duo", 10.35, "opacity:0", "none", .1, None))
        add(logo_in("#s3hf", 10.35, "x:-420,rotation:-540,opacity:0", .7, "whoosh"))
        add(pulse("#s3hf", 11.2)); add(wobble("#s3hf", 11.5, 8, 3))
        add(pop("#s3v2", 12.33, "scale:0,opacity:0,rotation:-30", "back.out(4)", .35, "ding"))
        add(pop("#s3in", 13.1, "x:120,opacity:0", "back.out(2)", .4, "pop"))
        add(logo_in("#s3ct", 13.1, "x:420,rotation:540,opacity:0", .45, "whoosh"))
        add(pop("#s3plus", 13.4, "scale:0,opacity:0", "back.out(4)", .25, "thud")); add(burst_js("s3bu", 13.45, 16, 200))
        add(pop("#s3mcpb", 13.5, "scale:2,opacity:0", "power4.in", .2, None))
        add(f'tl.to("#s3duo",{{y:80,opacity:0,duration:.3,ease:"power3.in"}},13.85);')
        add(f'tl.to("#s3ann",{{y:-60,scale:.9,opacity:0,duration:.35,ease:"power3.in"}},13.85);')
        add(pop("#s3chat", 14.0, "y:200,opacity:0", "expo.out", .45, "whoosh"))
        add(typed_js("s3t", "Make a 15s launch video for my sneakers", 14.25, .022))
        add(pop("#s3cb", 15.3, "y:40,opacity:0", "back.out(2)", .35, "pop"))
        add(f'tl.fromTo("#s3spin",{{rotation:0}},{{rotation:1080,duration:3.6,ease:"none"}},15.3);')
        for i, t in enumerate([16.85, 17.33, 18.05]):
            add(pop(f"#s3m{i}", t, "x:120,opacity:0", "back.out(2)", .35, "pop"))
            add(logo_in(f"#s3m{i} .lgm", t + .05, "scale:0,rotation:-360,opacity:0", .5, None)); add(burst_js(f"s3mb{i}", t + .3, 10, 90))
            add(f'tl.fromTo("#s3p{i}",{{scaleX:0}},{{scaleX:1,duration:{1.9 - i * .4:.2f},ease:"power1.inOut"}},{t + .2:.2f});')

    if sid == "s4":
        add(pop("#s4card", a + .05, "scale:.7,opacity:0", "back.out(2)", .4, "whoosh"))
        add(pop("#s4free", 19.95, "scale:1.8,opacity:0", "power4.in", .2, "thud"))
        add(f'tl.fromTo("#s4line",{{strokeDashoffset:640}},{{strokeDashoffset:0,duration:.35,ease:"power2.in"}},20.4);'); sfx("whoosh", 20.4)
        add(pop("#s4q", 20.6, "scale:0,opacity:0,rotation:-40", "back.out(3)", .35, "ding")); add(burst_js("s4bu", 20.65, 12, 180))
        add(f'tl.fromTo("#s4q",{{rotation:0}},{{rotation:10,duration:.2,yoyo:true,repeat:3}},21.0);')
        add(logo_in("#s4tag", 19.6, "y:-400,rotation:-60,opacity:0", .7, "whoosh"))
        add(f'tl.fromTo("#s4tag",{{rotation:0}},{{rotation:-14,duration:.4,yoyo:true,repeat:3,ease:"sine.inOut",immediateRender:false}},20.3);')
        add(pop("#s4next", 20.75, "x:-100,opacity:0", "expo.out", .35, "pop"))

    if sid == "s5":
        add(pop("#s5a", 22.6, "x:300,opacity:0", "expo.out", .4, "whoosh"))
        for i in range(3): add(pop(f"#s5day{i}", 22.85 + i * .18, "y:-40,opacity:0", "bounce.out", .3, "tick"))
        add(f'tl.to("#s5day2",{{backgroundColor:"{RED}",color:"#fff",duration:.15}},23.6);')
        add(pop("#s5end", 23.62, "scale:2,opacity:0", "power4.in", .22, "thud"))
        add(pop("#s5b", 24.15, "x:300,opacity:0", "expo.out", .4, "whoosh"))
        add(f'tl.fromTo("#s5shackle",{{y:-7}},{{y:0,duration:.18,ease:"power4.in"}},25.4);'); sfx("thud", 25.55)
        add(f'tl.fromTo("#s5b .ic",{{x:0}},{{x:-8,duration:.05,yoyo:true,repeat:5}},25.6);')
        add(logo_in("#s5c .ic .hcoin", 26.7, "scale:0,rotation:-720,opacity:0", .7, "ding"))
        add(pop("#s5c", 26.6, "x:300,opacity:0", "expo.out", .4, "whoosh"))
        add(f'tl.fromTo("#s5meter",{{scaleX:1}},{{scaleX:.18,duration:1.6,ease:"power1.in"}},27.0);')
        for i in range(5):
            t = 27.0 + i * .3
            add(f'tl.fromTo("#s5coin{i}",{{x:0,y:0,opacity:0,scale:.6}},{{x:{40 + i * 60},y:-140,opacity:1,scale:1,duration:.45,ease:"power2.out"}},{t:.2f});'
                f'tl.to("#s5coin{i}",{{opacity:0,duration:.2}},{t + .45:.2f});'); sfx("tick", t)

    if sid == "s6":
        add(pop("#s6card", a + .05, "y:160,opacity:0", "expo.out", .45, "whoosh"))
        add(pop("#s6p3", 29.0, "scale:0,opacity:0", "back.out(3)", .35, "pop"))
        add(f'tl.fromTo("#s6you",{{backgroundSize:"0% 100%"}},{{backgroundSize:"100% 100%",duration:.35,ease:"power2.out"}},30.95);'); sfx("shine", 30.95)
        add(f'tl.fromTo("#s6you",{{scale:1}},{{scale:1.18,duration:.15,yoyo:true,repeat:1}},31.0);')
        add(f'tl.fromTo("#s6arr path",{{strokeDashoffset:420}},{{strokeDashoffset:0,duration:.5,ease:"power2.out"}},30.5);')
        add(f'tl.fromTo("#s6arr",{{y:0}},{{y:18,duration:.25,yoyo:true,repeat:1}},31.05);')

    if sid == "s7":
        add(pop("#s7card", 32.0, "y:160,opacity:0", "expo.out", .45, "whoosh"))
        add(f'tl.fromTo("#s7c",{{strokeDashoffset:1000}},{{strokeDashoffset:0,duration:2.6,ease:"power2.in"}},33.3);'); sfx("shine", 34.4)
        add(odo_js("s7n", "42", 220, 34.0, 1.0)); sfx("thud", 35.0)
        add(f'tl.fromTo("#s7big",{{scale:1}},{{scale:1.12,duration:.16,yoyo:true,repeat:1}},35.0);')
        add(burst_js("s7bu", 35.0, 14, 220)); add(sheen_js("s7sh", 35.2))
        add(logo_in("#s7card .sh .lg", 32.1, d=.6, snd=None))
        add(f'tl.fromTo("#s7ride",{{x:0,y:0,opacity:0}},{{x:470,y:-160,opacity:1,duration:2.6,ease:"power2.in"}},33.3);')
        add(f'tl.fromTo("#s7rt",{{rotation:0}},{{rotation:360,duration:2.6,ease:"power2.in"}},33.3);')
        add(pulse("#s7rt", 35.9, 1.3))
        add(pop("#s7m", 35.95, "scale:0,opacity:0,rotation:-20", "back.out(3)", .35, "ding"))
        add(pop("#s7v", 37.3, "y:200,opacity:0", "expo.out", .45, "whoosh"))
        add(logo_in("#s7cl", 37.45, d=.6, snd="pop")); add(wobble("#s7cl", 38.5, 12, 3))
        add(f'tl.fromTo("#s7hl",{{backgroundSize:"0% 100%"}},{{backgroundSize:"100% 100%",duration:.35,ease:"power2.out"}},38.5);'); sfx("shine", 38.5)

    if sid == "s8":
        add(pop("#s8poll", a + .05, "y:160,opacity:0", "expo.out", .45, "whoosh"))
        for i, w in enumerate([.62, .38]):
            add(pop(f"#s8o{i}", 39.9 + i * .15, "x:-80,opacity:0", "back.out(2)", .3, "pop"))
            add(f'tl.fromTo("#s8f{i}",{{scaleX:0}},{{scaleX:{w},duration:.8,ease:"power3.out"}},{40.25 + i * .1:.2f});')
        add(logo_in("#s8poll .iglogo", 39.6, d=.6, snd=None)); add(wobble("#s8poll .iglogo", 40.3, 12, 3))
        add(logo_in("#s8a", 42.2, d=.45)); add(logo_in("#s8b", 42.35, d=.45, snd=None))
        add(pop("#s8cmt", 40.75, "y:40,opacity:0", "back.out(2)", .35, "pop"))
        add(f'tl.fromTo("#s8cmt",{{y:0}},{{y:10,duration:.25,yoyo:true,repeat:3,ease:"sine.inOut",immediateRender:false}},41.1);')
        f = 41.95
        add(f'tl.fromTo("#s8cur",{{x:760,y:820,opacity:0}},{{x:760,y:820,opacity:1,duration:.15}},{f - .55:.2f});tl.to("#s8cur",{{x:175,y:640,duration:.4,ease:"power3.inOut"}},{f - .45:.2f});')
        add(ripple_js("s8rip", f)); sfx("pop", f)
        add(f'tl.fromTo("#s8fol",{{backgroundColor:"#0095f6"}},{{backgroundColor:"#22c55e",duration:.15}},{f:.2f});')
        add(f'tl.fromTo("#s8heart",{{scale:0,opacity:0}},{{scale:1.4,opacity:1,duration:.25,ease:"back.out(4)"}},{f + .15:.2f});tl.to("#s8heart",{{scale:1,duration:.2}},{f + .4:.2f});'); sfx("ding", f + .15)
    return "\n".join(J)


# ---------- avatar ----------
# Poses whose head sits exactly where the mouth overlays were cut can talk; the others are only used in pauses.
TALK = {"n", "count", "five_figures", "point_right", "what", "thumbs_up2", "slice", "slice3"}
POSES = [(0, "n"), (.9, "five_figures"), (2.2, "n"), (4.25, "what"), (5.6, "n"),
         (6.95, "count"), (8.3, "n"), (9.55, "point_right"), (11.0, "n"), (15.3, "point_right"), (16.6, "n"),
         (19.3, "what"), (20.5, "n"), (21.62, "thinking"), (22.03, "count"), (23.2, "n"), (24.2, "what"), (25.6, "n"),
         (26.7, "point_right"), (27.8, "n"), (28.58, "shocked"), (29.03, "point_right"), (30.4, "n"),
         (31.67, "count"), (32.7, "n"), (34.9, "five_figures"), (36.1, "n"), (37.3, "point_right"), (38.6, "n"),
         (39.4, "surprised"), (39.73, "what"), (40.6, "n"), (41.85, "thumbs_up2"), (42.95, "wave")]
POSE_FILES = sorted({p for _, p in POSES if p != "n"})
MOUTHS = ["m_closed", "m_small", "m_round", "m_open", "m_teeth"]
mouth = visemes(f"tools/transcript_{LANG}.json", f"tools/rms_{LANG}.txt", fps=FPS, dur=DUR)

def pose_at(t):
    cur = POSES[0][1]
    for s, p in POSES:
        if t >= s: cur = p
    return cur

# ---------- assemble ----------
scene_divs, scene_js, cuts_js = [], [], []
for sid in IDS:
    a, b = SC[sid]
    kind = BG[sid][0]
    if kind == "img":
        bg = (f'<div class="bgph" id="{sid}bg"><img id="{sid}bgi" src="assets/photos/{BG[sid][1]}" alt="" style="object-position:{BG[sid][2]}">'
              f'<div class="bgfade"></div><div class="credit" data-layout-ignore>Image: Higgsfield</div></div>')
    else:
        bg = (f'<div class="bgph bgpl {kind}" id="{sid}bg"><div class="gridmv" id="{sid}bgi"></div>'
              f'<div class="glow g1"></div><div class="glow g2"></div></div>')
    srcchip = f'<div class="src" id="{sid}src"><b>SOURCE</b>{esc(SOURCES[sid])}</div>' if sid in SOURCES else ""
    scene_divs.append(f'<div id="{sid}" class="clip scene" data-start="{a}" data-duration="{b - a:.2f}" data-track-index="2" data-layout-allow-overflow>'
                      f'{bg}<div class="wrap" id="{sid}w">{SCENE_HTML[sid]}</div>{srcchip}</div>')
    scene_js.append(anim(sid))
    if a > 0:
        cuts_js.append(f'tl.fromTo("#flash",{{opacity:0,x:-1100}},{{opacity:.85,x:1100,duration:.32,ease:"power2.inOut"}},{a - .16:.2f});'); sfx("whoosh", a - .14)

pose_imgs = "".join(f'<img id="p_{p}" class="pose" src="assets/avatar/{p}.png" alt="">' for p in POSE_FILES)
mouth_imgs = "".join(f'<img id="{m}" class="mouth" src="assets/avatar/mouth/{m}.png" alt="">' for m in MOUTHS)
av_js, prev_pose, prev_m = [], None, None
for f in range(int(OUTRO * FPS)):
    t = round(f / FPS, 3); p = pose_at(t)
    m = mouth[f]
    if p not in TALK and m != "m_closed": p = "n"      # never freeze the mouth while he is talking
    if p != prev_pose:
        for q in POSE_FILES + ["n"]:
            av_js.append(f'tl.set("{"#neutral" if q == "n" else "#p_" + q}",{{opacity:{1 if q == p else 0}}},{t});')
        av_js.append(f'tl.set("#mouths",{{opacity:{1 if p in TALK else 0}}},{t});')
        if t > 0: av_js.append(f'tl.fromTo("#avpop",{{scale:.95}},{{scale:1,duration:.18,ease:"back.out(3)",immediateRender:false}},{t});')
        prev_pose = p
    if m != prev_m:
        for q in MOUTHS: av_js.append(f'tl.set("#{q}",{{opacity:{1 if q == m else 0}}},{t});')
        prev_m = m
av_js.append(f'tl.fromTo("#avbreath",{{y:0}},{{y:-8,duration:1.6,ease:"sine.inOut",yoyo:true,repeat:{int(OUTRO / 1.6)}}},0);')
av_js.append(f'tl.fromTo("#avpop",{{y:420,opacity:0}},{{y:0,opacity:1,duration:.5,ease:"expo.out"}},0);')
av_js.append(f'tl.to("#avpop",{{y:500,opacity:0,duration:.35,ease:"power2.in",immediateRender:false}},{OUTRO - .3:.2f});')
sfx("whoosh", OUTRO - .1); sfx("shine", OUTRO + .7)

outro_js = f"""tl.fromTo("#outro",{{clipPath:"circle(0% at 30% 72%)"}},{{clipPath:"circle(150% at 30% 72%)",duration:.7,ease:"power3.inOut"}},{OUTRO:.2f});
tl.fromTo("#outlogo",{{scale:.7,opacity:0}},{{scale:1,opacity:1,duration:.6,ease:"expo.out"}},{OUTRO + .25:.2f});
tl.fromTo("#outsheen",{{x:-600}},{{x:1400,duration:.9,ease:"power2.inOut"}},{OUTRO + .7:.2f});"""

CSS = open("tools/style.css").read().replace("__RED__", RED)
S = 780 / 1024
page = f"""<!doctype html>
<html lang="en"><head><meta charset="UTF-8"/>
<meta name="viewport" content="width=1080, height=1920"/>
<script src="assets/gsap.min.js"></script>
<style>
{CSS}
{open("tools/reel.css").read()}
.mouth{{position:absolute;left:{428 * S:.1f}px;top:{362 * S:.1f}px;width:{200 * S:.1f}px;height:{170 * S:.1f}px;opacity:0}}
#mouths{{position:absolute;inset:0}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
 <div id="bgclip" class="clip" data-start="0" data-duration="{DUR}" data-track-index="0" data-layout-ignore style="position:absolute;inset:0"><div id="bg"></div><div id="flash"></div></div>
 {''.join(scene_divs)}
 <div id="avatar" class="clip" data-start="0" data-duration="{OUTRO:.2f}" data-track-index="4" data-layout-ignore><div id="avpop"><div id="avbreath">
  {pose_imgs}<div id="neutral"><img class="base" src="assets/avatar/m_closed.png" alt=""></div><div id="mouths">{mouth_imgs}</div></div></div></div>
 <div id="outroclip" class="clip" data-start="{OUTRO}" data-duration="{DUR - OUTRO:.2f}" data-track-index="6" data-layout-ignore style="position:absolute;inset:0"><div id="outro"><div id="outsheen"></div><div id="outlogo"><img src="assets/img/logo_h.png" alt="NextUp Learn"></div></div></div>
 <audio id="voice" src="assets/audio/voice_{LANG}.mp3" data-start="0" data-duration="{VOICE_DUR}" data-track-index="10"></audio>
 <audio id="sfx" src="assets/audio/sfx_{LANG}.wav" data-start="0" data-duration="{DUR}" data-track-index="11"></audio>
</div>
<script>
const tl=gsap.timeline({{paused:true}});
{chr(10).join(cuts_js)}
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
