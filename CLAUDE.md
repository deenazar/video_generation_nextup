# NextUp video generation kit

This repo makes vertical reels (1080x1920) for **NextUp Learn** (Instagram @nextup, YouTube Shorts) with
[HyperFrames](https://hyperframes.heygen.com) (HTML + GSAP rendered to MP4, CLI pinned at `hyperframes@0.9.56`).

## Who you work for

- The owner goes by **Nex** (Chennai, frontend engineer). Address him as "Nex".
- Reply in short Tanglish (Tamil + English), sized for reading on a phone.
- End every reply with a short **"English correction (professor mode)"** note that fixes his English from his last message.
- When you refer to Nex, use they/them unless he states pronouns.

## Procedure (Nex's rules, 2026-11-19) — follow exactly

1. Wait until Nex pastes the **script**. Do nothing before that: no checks, no builds, no renders.
2. Your job is **video generation only**. Don't review, rewrite or fact-check the script unless he asks.
3. After the script, ask exactly ONE question: **"Tamil or English MP3 add பண்ணிட்டீங்களா?"**
   - Voiceovers go in `reels/<topic>/assets/audio/voice_ta.mp3` and `voice_en.mp3`.
4. Then build, check, render, and deliver the MP4s.

## Rules for every video

- **Real assets only.** Use real and original icons, logos and photos: official logo files and real photographs.
  - If an asset is missing or you can't get it, **ask Nex**. Never draw a stand-in.
  - Logos: `npx hyperframes media-use resolve --type logo --intent "<brand>"`, or GitHub org avatars (`--from https://github.com/<org>.png`).
  - Photos: the HeyGen asset search if signed in, otherwise Wikimedia Commons with a credit line.
- **Background:** a full-screen real image with a **black gradient fading in at the bottom** of the screen.
- **Icons** look the same as in past reels: real logo files in white rounded tiles or pills.
- **Make it engaging.** Every reel needs attractive animation, motion graphics, SFX and VFX:
  - card entrances
  - odometer counters
  - drawn charts
  - stamps
  - bursts and sheens
  - a cursor clicking things
  - whooshes on cuts
- **Patient pace.** Never rush. Every beat stays on screen long enough to read and understand.
- **Outro:** always the NextUp outro: a red (#ea333f) circle reveal, then the full-screen NextUp Learn logo
  (`assets/img/logo_h.png`, 1200x600 at left -60, top 630) with a white sheen. Show no "@nextup" text.
- **Red/green zones (Instagram UI):** keep all key content in the green safe area.
  - Avoid the top ~250 px and the bottom ~360 px.
  - Avoid the right ~130 px column between y 1080 and y 1560.

## Brand

- The name is "NextUp", with no space. The wordmark is NextUp in Bold plus Learn in Light.
- Red #ea333f, ink #0f172a, Poppins (in `template/assets/fonts`).

## Avatar (Nex's 3D film-style character)

- Lives in `template/assets/avatar/*.png`, cut out at 1024 px. Pose names:
  - shocked, point_right, thinking, surprised
  - thumbs_up, thumbs_up2, point_up, count
  - what, five_figures, laptop, wave
  - slice, slice2, slice3 (the neck-slice CTA)
- `m_closed.png` is the talking base. Lip-sync overlays `avatar/mouth/m_*.png` on it.
- **Lip-sync uses `tools/lipsync.py`** (phonemes, not loudness): each Whisper word is split into CMU-dict phonemes
  (`pip install cmudict`), each phoneme maps to a mouth shape, packed into the frames where the voice is really
  sounding. Quiet frames close the mouth, 1-frame flickers are merged, and the picture leads the sound by one frame.
  Add hard words (brand names, acronyms) to `SAY` in `lipsync.py`.
- **Talking poses** have the head exactly where the mouth overlays fit, so the mouth keeps moving during gestures:
  `m_closed` (neutral), count, five_figures, point_right, what, thumbs_up2, slice, slice3.
  The other poses (shocked, thinking, surprised, wave, point_up, thumbs_up, slice2, laptop) have a different head
  size or a hand on the face: use them only in pauses. `gen.py` swaps back to neutral if one lands on speech.
- Placement: left -120, **top 1140**, 780x780 (low, body touching the bottom edge). Switch poses on key words and hold
  each gesture for about 1 s or more.

## How to make a reel

Every video lives in its own folder `videos/<topic>_<contenttype>_<datetime>/` (datetime IST `YYYYMMDD-HHMM`,
e.g. `videos/higgsfield-mcp-2_news_20261119-1220/`), on its own branch, delivered as a new PR to `main`.
Keep the voice MP3 in that folder and the final MP4 as `final_<platform>.mp4` there too.
Anything reusable goes back into `template/` in the same PR.

```bash
cp -R template videos/<topic>_<contenttype>_<datetime>   # new project
cd videos/<topic>_<contenttype>_<datetime>
# add voice_ta.mp3 / voice_en.mp3 to assets/audio/
npx hyperframes transcribe assets/audio/voice_en.mp3 -d /tmp/tr_en      # word timings (Tamil: -m medium -l ta)
for L in ta en; do ffmpeg -v error -i assets/audio/voice_$L.mp3 -af "aresample=44100,asetnsamples=1470,astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level:file=tools/rms_$L.txt" -f null -; done
# write tools/gen.py for this script (start from tools/gen_example_ai_layoffs.py)
DUR=45 sh tools/build.sh ta   # writes index.html + assets/audio/sfx_ta.wav
npx --yes hyperframes@0.9.56 check
npx --yes hyperframes@0.9.56 snapshot --at 2,6,10,...   # look at the frames, fix, repeat
npx --yes hyperframes@0.9.56 render --fps 30 -o renders/nextup_<topic>_tamil_v1.mp4
sh tools/build.sh en && npx --yes hyperframes@0.9.56 render --fps 30 -o renders/nextup_<topic>_english_v1.mp4
```

How the generator (`gen.py`) is laid out:

- `STARTS` holds the scene start times for each language. Read them from the transcript word times.
- Every in-scene beat is `T(scene, fraction)`, so one design fits both voiceovers.
- `sfx(kind, t)` logs a sound event. `tools/sfx.py` then synthesizes the pop, tick, ding, thud, shine and whoosh sounds with ffmpeg.
- HyperFrames contract:
  - one paused GSAP timeline in `window.__timelines = {main: tl}`
  - every timed element is `class="clip"` with `data-start` and `data-duration`
  - no `Math.random()` and no network fetches
  - every `<audio>` has an `id`
- `examples/ai_layoffs/` is a full worked reel: photos plus credits, logos, charts, odometers and source chips.
  - Its background is the older white grid. New reels use the full-screen photo with the bottom black gradient (see Rules).

## Delivery

- Render both language versions when there are two MP3s. Verify each with `ffprobe`: h264, 1080x1920, 30 fps, AAC, 45 s or the script length. The peak must stay at or below -1 dB.
- Send the MP4 to Nex. Files over 30 MB also get a `_phone.mp4` copy (`-crf 25`) so they reach his phone.
- Final reply, in short Tanglish:
  - what's in the reel
  - any honest caveats (no music, a missing asset)
  - an Instagram caption, 3–5 hashtags and a YouTube title
  - the English correction note
- Commit the voice MP3 and the final MP4 inside the video's folder (renders/ scratch files stay ignored).
