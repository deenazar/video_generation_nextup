# Rules (always apply)

1. **One question only.** After a script is pasted, ask only: `MP3 add பண்ணிட்டீங்களா?`
   Never ask about topic, style, length, voice or colours; use the defaults below.
   - Yes → check `audio/` for an `.mp3`. None there → say so in one line and wait.
   - No → use the AI voice from the skill.
2. **Common vs per-video.** Anything reusable (rules, procedure, conditions, skills, templates,
   scripts, fonts, logos, branding, render settings) lives in `common/`. Anything for one video
   lives only in that video's folder. Something reusable built during a video → move it to
   `common/` in the same PR.
3. **Per-video folder:** `videos/<topic>_<contenttype>_<datetime>/`
   - `topic`: lowercase slug, words joined with `-` (e.g. `gpt-6-launch`)
   - `contenttype`: `reel` (default), `short`, `explainer`, `news`, ...
   - `datetime`: IST, `YYYYMMDD-HHMM`
   - e.g. `videos/gpt-6-launch_reel_20261119-1430/`
4. **Every piece of work is a new PR.** Each video, and each change to `common/`, goes on its own
   new branch off the latest `main` and is delivered as a new pull request to `main`.
   Never push straight to `main`. Send the user the PR link at the end.

# Defaults (never ask)

- Caption language: same as the script; caption text is the script word for word.
- Length: as long as the MP3 (about 20 s with the AI voice).
- Format: 1080x1920 vertical MP4, H.264 + AAC.
- Branding: @nextup handle on screen; light dotted style, big captions, no avatar.
