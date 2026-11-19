---
name: "nex-reel-hyperframes"
description: "Build Nex's @nextup 20s vertical tech reels (light dotted reference style, English AI voice, big captions, no avatar) with HyperFrames in the workspace. Use for any new reel topic."
---

# Nex reel (HyperFrames, light reference style)

User: Nex (Azarudeen J, Chennai, frontend engineer). Channel @nextup, IT/tech reels for Instagram Reels + YouTube Shorts. He writes Tanglish: reply in Tamil/Tanglish, address him as "Nex", keep replies short (mobile), and end with a short "English correction (professor mode)" note correcting his English.

## What he wants (learned from 3 rounds)
- v1 static avatar template: rejected ("just moving an image"). v2 dark theme with his avatar + Tanglish subs: rejected.
- Current standard (v3, accepted direction): NO avatar, English voice, English captions, light style like reference reel by itsv0id.ai: light grey dotted background, white pill chips with line icons, dark terminal card, phone mockup with chat bubbles, flow diagram, toggle/checkbox UI cards, big lowercase-style bottom captions with mixed weights (light + bold italic), yellow highlighter on the key phrase, outro "Follow @nextup" toggle.
- Do it inside Claude (cloud workspace), not his Mac Terminal (Claude Code weekly limit can run out).
- Copy the STYLE, never the reference's scenes 1:1. Generic icons only (orange spark tile for Claude, green chat-bubble tile for WhatsApp, etc). No real logos, no copyrighted music.
- Instagram cannot be fetched (WebFetch robots block, browser login wall). Ask him for screenshots of the reference.

## Content rules
- Research the topic first (WebSearch/WebFetch). Facts only from sources checked; never invent numbers. If a claim rests on aggregators, tell Nex to verify on the official doc before posting.
- Script: 5 short sentences, ~20 s total, English plain words. Hook in first 3 s, CTA (Follow) in last 3 s.
- Safe zones for IG: keep key content out of top ~250 px, bottom ~360 px, right ~130 px. Captions around y=1100 worked well.

## Pipeline (all in /home/claude/hf)
1. Stage his files if needed (device_stage_files). Project dir /home/claude/hf/nextup (hyperframes init done; skills in .agents/skills). Back up the old index.html before overwriting.
2. Voice: kokoro-onnx, voice `am_michael`, speed 1.12, lang en-us; models /tmp/kokoro-v1.0.onnx and /tmp/voices-v1.0.bin (download from github thewh1teagle/kokoro-onnx releases model-files-v1.0 if missing). Per-sentence audio, trim silence (abs>0.01), LEAD 0.2 s, GAP 0.3 s, mix into one 20 s wav at 24 kHz -> assets/audio/voice.wav. Check total fits 20 s (raise speed if not).
3. Caption timing: split each sentence into 2-4 word chunks, mark emphasis `*bold*` and highlight `=phrase=`; word time = sentence duration split by syllable weights (+1 unit after , or .). Save timing.json with scene bounds (midpoints between sentences).
4. SFX: numpy-synthesized whoosh at scene boundaries, tick per typed character, pop on element entrances, ding on success, click on checkbox/toggle -> assets/audio/sfx.wav (normalize 0.8).
5. Generator approach: a Python script (gen.py + template.html) builds index.html from timing.json so retiming is one command. Scenes = `.clip` divs with data-start/data-duration; scene fade-out on inner wrapper 0.2 s before boundary.
6. Check/snapshot: `npx hyperframes@0.9.56 check` (0 errors required; line_unread warnings OK), `snapshot --at t1,t2,...` then read contact-sheet jpgs and fix overlaps (e.g. chip over chat bubble).
7. Render DETACHED or it gets cancelled when the shell exits: `cd nextup && setsid nohup npx -y hyperframes@0.9.56 render -o /home/claude/hf/out/<name>.mp4 > /tmp/r.log 2>&1 < /dev/null & disown`, then sleep/poll (20 s video ~ 1.5-2 min). Use a NEW filename per reel; never overwrite earlier renders.
8. Verify with ffprobe (h264, 1080x1920, aac, 20 s) and grab 1-2 frames with ffmpeg.
9. Deliver: SendUserFile, then device_commit_files with {fileUuid, devicePath:"/Users/azarudeen/nextup-reels/<name>.mp4"} (field is devicePath, not destPath). Final reply: what's in it, honest caveats, caption + 3-5 hashtags + YouTube title, one next step.

## HyperFrames contract (lint rules that bit us)
- Root `data-composition-id="main" data-width=1080 data-height=1920 data-duration=20`. Timed elements need `class="clip"` + data-start/data-duration/data-track-index.
- One paused GSAP timeline at `window.__timelines["main"]=tl`; seek-driven, so: no repeat:-1, no network fetches, no onUpdate tricks, no CSS transform on elements GSAP animates (use x/y/scale in GSAP; position with left/top).
- Load GSAP from local assets/gsap.min.js (template's CDN link fails offline).
- Use `tl.fromTo` with explicit start values; for off-screen wipes use CSS baseline + immediateRender:false.
- Typing effect: per-character spans revealed with tl.set at start + i*0.028; cursor moved with tl.set.
- Audio elements need ids: `<audio id=voice src=assets/audio/voice.wav data-start data-duration data-track-index>`; same for sfx.
- Fonts Inter and JetBrains Mono are bundled; min text size 28 px; `data-layout-ignore` / `data-layout-allow-overflow` for intentional overflow.
- Software GL in the cloud, ~14 fps capture.

## Honest limits to state
- Voice is a stock English AI voice, not Nex's voice; no voice cloning or lip-sync here (offer ElevenLabs-cloned MP3 that can be dropped in as voice.wav).
- Cannot watch the reference reel video, only screenshots he sends.
- Workspace network is allowlisted (package registries, GitHub); other sites may be refused.