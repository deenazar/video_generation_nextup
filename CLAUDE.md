# Nex @nextup video workflow

The user starts a session by pasting a reel script. That script is the whole brief.

## Rule: ask exactly one question

After the script is pasted, ask **only** this, in Tamil, and nothing else:

> MP3 add பண்ணிட்டீங்களா?

- Do not ask about topic, style, length, voice, colours or anything else. Use the defaults below.
- Do not start rendering until the user confirms the MP3 is in place.
- If the user says yes, check that an `.mp3` exists in `audio/`. If none is there, say so in one line and wait.
- If the user says no MP3 this time, go ahead and use the AI voice from the skill instead.

## Folder layout

```
audio/        inbox: the user drops the new MP3 here
common/       shared across all videos: style, templates, fonts, logos, music, reusable
              components, helper scripts. Reuse from here before making anything new.
videos/       one folder per generated video, never shared
  <topic>_<contenttype>_<datetime>/
```

### Common vs per-video

- Anything general that the next video could reuse (brand colours, caption style, the @nextup
  handle, dotted background, intro/outro, fonts, logos, render settings, scripts) goes in
  `common/`. If you build something reusable while making a video, move it to `common/` and
  reference it from there.
- Everything specific to one video goes in that video's own folder only.

### Per-video folder

Name: `videos/<topic>_<contenttype>_<datetime>/`

- `topic`: short lowercase slug of the script's subject, words joined with `-` (e.g. `gpt-6-launch`).
- `contenttype`: what it is, e.g. `reel`, `short`, `explainer`, `news`. Default `reel`.
- `datetime`: creation time in IST, `YYYYMMDD-HHMM` (e.g. `20261119-1430`).
- Example: `videos/gpt-6-launch_reel_20261119-1430/`

Put in it:

- `script.txt` – the pasted script, unchanged
- `voice.mp3` – the MP3 moved from `audio/` (leave `audio/` empty after)
- the HyperFrames project / any per-video assets
- `final.mp4` – the rendered video

## Making the video

1. Create the per-video folder first, save `script.txt`, move the MP3 into it.
2. Use the `nex-reel-hyperframes` skill (light dotted reference style, big captions, no avatar),
   pulling shared pieces from `common/`.
3. `voice.mp3` is the voice track. Time scenes and captions to it; caption text comes from the
   script, word for word.
4. Render 1080x1920 vertical MP4 to `final.mp4` in that folder.
5. Send `final.mp4` to the user, then commit and push on the session's branch.

## Defaults (never ask about these)

- Caption language: same as the script.
- Length: as long as the MP3 (or about 20 s with the AI voice).
- Branding: @nextup handle on screen.
