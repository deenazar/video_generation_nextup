---
name: "nex-reel-maker"
description: "Make Nex's @nextup IT tech news reels (1080x1920 MP4, AI voice, illustrated avatar, motion graphics) from a topic or a Nex Reel Studio render brief. Use for any 'render this reel' request."
---

# Nex Reel Maker

User: Nex (goes by "Nex"), Chennai, frontend engineer. Channel: @nextup, IT tech reels for Instagram Reels and YouTube Shorts. He writes Tanglish; reply in Tanglish unless he asks for English. Correct his English briefly when he writes English.

## Inputs
1. A **render brief** copied from the "Nex Reel Studio" artifact: a JSON object `{tool:'nex-reel-maker', brand, stories[], voice}`. Each story has `tag, head, srcIcon, srcLabel, srcSub, rIcon, rIcon2, narr, steps[3]{i,l,s}, links[2], row[4], tog`.
2. Or just a topic. Then research it first (WebSearch/WebFetch), write 3 stories from facts you actually found, and build the same structure.

## Content rules (always)
- Facts only from sources you checked. Never invent numbers, names or dates. If a story rests on aggregator sites only, say so in the final reply and tell Nex to check the primary source before posting.
- No real company logos. Use generic icons plus text labels. No copyrighted music or clips. No watermarks from other apps.
- One idea per story. Narration: 1-2 short sentences, max ~22 words, plain English (spell numbers as words for the voice, e.g. 'seventy countries').
- Target length 20-30 s for 3 stories (intro ~2 s, each story 5-6 s, outro ~2 s). Say the real length if it differs from what he asked.

## Platform rules (re-check by search if the task depends on them)
- 1080x1920, 9:16, 30 fps, H.264 yuv420p, AAC audio.
- Hook in the first 3 s. CTA in the last 3 s (follow / share to a dev friend). Shares matter more than likes.
- Keep key content out of the IG UI zones: top 250 px, bottom 360 px, right 130 px column (y 1080-1560).
- Captions large and word-timed. Hashtags: 3-5 specific, put them in the caption (give Nex caption + hashtags + a YouTube title with the final file).
- YouTube Shorts max 3 min. Monetization thresholds change; point him to YouTube Studio.

## Visual style (match exactly)
Step-card explainer look: lavender-to-sage gradient background with light noise; karaoke captions top (y~196, 68 px Inter 800, active word dark, others grey); big title (#0N + crimson gradient word, Inter 900, 122 px); white rounded card (x40,y470,1000x920, radius 64) with black '#0N / 0M' badge, source tile -> dashed crimson arrow -> dark tile row, big headline, mono breadcrumb, grey panel with 3 step tiles joined by dashed links with pill words, a white toggle row that flips (and swaps text), 6-dot progress line. Floating icon tiles right of the avatar. Avatar bottom-left (Nex: spiky black hair, tortoiseshell rectangular glasses, full black beard with grey flecks, black crew-neck over white collar) with blink, head bob and mouth driven by the voice. Fonts: Inter (600-900) and JetBrains Mono (get woff2 via `npm i @fontsource/inter @fontsource/jetbrains-mono`). Accent default #a3243f. Scene order: intro card (N updates today), one scene per story, outro (Follow @nextup, bell tile, follow toggle turns on).

## Pipeline (workspace)
1. **Voice (Kokoro, local):** `pip install --break-system-packages kokoro-onnx soundfile`; download `kokoro-v1.0.onnx` and `voices-v1.0.bin` from `https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/`. Voice `am_michael`, speed 1.12, lang en-us. One WAV per scene; trim leading/trailing silence (abs>0.01). Scene i starts at previous end + 0.08 s; lead 0.15 s; tail 0.55 s after the last line. Mix a soft filtered-noise whoosh (-16 dB) at each scene change. Save audio.wav.
2. **Timeline:** per word times = scene audio duration split by syllable weights (+1.1 unit pause after sentence ends). Mouth envelope = RMS of the narration at 30 fps, normalised to the 90th percentile, fast attack / slow decay. Write timeline.js (`window.TL`).
3. **Page:** one HTML page, 1080x1920, all motion as paused Web Animations (`el.animate(...); a.pause()`) driven by a global `tick(t)` that sets `currentTime` for every animation (fill 'both'); window-style opacity animations must use per-keyframe easing and a linear overall easing. Dashes, captions, avatar and progress are updated in `tick`. Scene reveal times are fractions of the scene duration D (tiles 0.1 s, arrow 0.35 s, heading 0.55 s, nodes 0.30D/0.47D/0.64D, links 0.36D/0.53D, toggle row 0.64D, toggle flips 0.74D and 0.87D). The Nex Reel Studio artifact contains this exact scene engine; copy its JS when you need it.
4. **Test frames first:** screenshot 4-5 moments (intro, mid story, last story, outro) with Playwright using `executable_path='/usr/bin/google-chrome'`, args `--no-sandbox --allow-file-access-from-files`; look at them once, fix, then render. Check heading fit (no overflow past x=1010), caption width, nothing clipped.
5. **Render:** two parallel Playwright processes (frame ranges 0..N/2 and N/2..N), each piping JPEG q92 screenshots into `ffmpeg -f image2pipe -framerate 30 -vcodec mjpeg -i - -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -r 30 part.tmp.mp4`, renamed only when ffmpeg exits 0. Join with the concat demuxer `-c copy`, then mux `audio.wav` with `-c:v copy -c:a aac -b:a 160k -ar 44100 -shortest`. Check duration and one mid frame.
6. **Deliver:** send the MP4 with SendUserFile. Final reply (Tanglish, short): length, what the three stories are, the source caveat, a suggested caption + 3-5 hashtags + YouTube title, and one next step.

## Limits to state honestly
- No access to the Instagram reel video itself (Instagram blocks fetching); work from screenshots or descriptions he gives.
- The workspace cannot reach arbitrary websites; GitHub and package registries work.
- Account skills only carry this SKILL.md; heavier community skills (Remotion, ghost-editor, ffmpeg-skill) run best in Claude Code on his laptop.