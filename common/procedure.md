# Procedure: script → video → PR

1. User pastes the script. Ask the one question from `rules.md`. Wait for the answer.
2. Branch: create a new branch off the latest `main` (in cloud sessions, use the branch the
   session gives you, starting from `main`).
3. Create `videos/<topic>_<contenttype>_<datetime>/` and put in it:
   - `script.txt`: the pasted script, unchanged
   - `voice.mp3`: the MP3 moved from `audio/` (leave `audio/` empty afterwards)
4. Build the video with `common/skills/nex-reel-hyperframes/SKILL.md`, reusing
   `common/templates/` and `common/scripts/`. The HyperFrames project and all per-video assets
   (timing, sfx, frames) go inside the video's folder. Time scenes and captions to `voice.mp3`.
5. Render to `final.mp4` in the video folder. Check with ffprobe (h264, 1080x1920, aac, length).
6. Send `final.mp4` to the user.
7. Commit, push, open a PR to `main` titled `Video: <topic> (<contenttype>)`, and send the link.

## Per-video folder contents

```
videos/<topic>_<contenttype>_<datetime>/
  script.txt
  voice.mp3
  final.mp4
  project/        HyperFrames project (index.html, timing.json, assets/...)
```
