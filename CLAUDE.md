# Nex @nextup reel workflow

The user starts a session by pasting a reel script. That script is the whole brief.

## Rule: ask exactly one question

After the script is pasted, ask **only** this, in Tamil, and nothing else:

> MP3 add பண்ணிட்டீங்களா?

- Do not ask about topic, style, length, voice, colours or anything else. Use the defaults below.
- Do not start rendering until the user confirms the MP3 is in place.
- If the user says yes, check that an `.mp3` exists in `audio/`. If none is there, say so in one line and wait.
- If the user says no MP3 this time, go ahead and use the AI voice from the skill instead.

## After the answer: make the reel

1. Use the `nex-reel-hyperframes` skill (light dotted reference style, big captions, no avatar).
2. The newest `.mp3` in `audio/` is the voice track. Time the scenes and captions to it; the caption text comes from the pasted script, word for word.
3. Output: 1080x1920 vertical MP4, saved to `output/<short-topic-slug>.mp4`.
4. Send the finished MP4 to the user, then commit and push it on the session's branch.

## Defaults (never ask about these)

- Language of captions: same as the script.
- Length: as long as the MP3 (or about 20 s with the AI voice).
- Branding: @nextup handle on screen.
