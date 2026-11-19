#!/usr/bin/env python3
"""Phoneme-based lip-sync for the NextUp avatar.

Old way: one mouth per frame from loudness only, swapped by frame number -> mouth flapped at random.
This way: every word from the Whisper transcript is split into phonemes (CMU dict), each phoneme gets
a mouth shape (viseme), and the phonemes are packed into the part of the word where the voice is
really sounding (from the per-frame RMS). Quiet frames close the mouth, short flickers are merged,
and the picture leads the sound by one frame, which is how real speech looks.

    from lipsync import visemes
    track = visemes("tools/transcript_en.json", "tools/rms_en.txt", fps=30, dur=46)
    # track[i] is the mouth file name for frame i: m_closed / m_small / m_round / m_open / m_teeth / m_smile

Needs: pip install cmudict
"""
import json, re

try:
    import cmudict
    _CMU = cmudict.dict()
except Exception:  # still works without it, just rougher
    _CMU = {}

# words Whisper writes that the dictionary can't read, spelled the way they are said
SAY = {
    "mcp": "em see pee", "ai": "ay eye", "api": "ay pee eye", "ui": "you eye", "cli": "see el eye",
    "vo": "vee oh", "veo": "vee oh", "cdance": "see dance", "seedance": "see dance", "cling": "kling",
    "nextup": "next up", "umm": "um", "hmm": "hm", "higgsfield": "higgs field", "claude": "claude",
    "chatgpt": "chat gee pee tee", "openai": "open ay eye",
}
ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def _num(n):
    n = int(n)
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10] + ("" if n % 10 == 0 else " " + ONES[n % 10])
    if n < 1000: return ONES[n // 100] + " hundred" + ("" if n % 100 == 0 else " " + _num(n % 100))
    return " ".join(ONES[int(d)] for d in str(n))


def _spoken(word):
    w = word.lower().strip(".,!?;:\"'()[]…").replace("’", "'")
    if w in SAY: return SAY[w]
    w = re.sub(r"(\d+)\.(\d+)", lambda m: _num(m.group(1)) + " point " + " ".join(_num(c) for c in m.group(2)), w)
    w = re.sub(r"\d+", lambda m: " " + _num(m.group(0)) + " ", w)
    return w.replace("-", " ").replace("@", " at ")


# rough letter -> phoneme fallback for words not in the dictionary
_LET = [("tion", ["SH", "AH0", "N"]), ("ch", ["CH"]), ("sh", ["SH"]), ("th", ["TH"]), ("ph", ["F"]), ("ee", ["IY1"]),
        ("oo", ["UW1"]), ("ou", ["AW1"]), ("ow", ["OW1"]), ("ai", ["EY1"]), ("ay", ["EY1"]), ("ea", ["IY1"]),
        ("a", ["AE1"]), ("e", ["EH1"]), ("i", ["IH1"]), ("o", ["AA1"]), ("u", ["AH1"]), ("y", ["IY0"]),
        ("b", ["B"]), ("c", ["K"]), ("d", ["D"]), ("f", ["F"]), ("g", ["G"]), ("h", ["HH"]), ("j", ["JH"]), ("k", ["K"]),
        ("l", ["L"]), ("m", ["M"]), ("n", ["N"]), ("p", ["P"]), ("q", ["K"]), ("r", ["R"]), ("s", ["S"]), ("t", ["T"]),
        ("v", ["V"]), ("w", ["W"]), ("x", ["K", "S"]), ("z", ["Z"])]


def _guess(w):
    out, i = [], 0
    while i < len(w):
        for k, ph in _LET:
            if w.startswith(k, i): out += ph; i += len(k); break
        else: i += 1
    return out


def phonemes(word):
    out = []
    for part in _spoken(word).split():
        part = re.sub(r"[^a-z']", "", part)
        if not part: continue
        out += _CMU[part][0] if part in _CMU else _guess(part)
    return out


# phoneme -> viseme. The overlays: m_closed (lips together), m_small (slightly apart),
# m_open (jaw dropped), m_round (lips pushed out), m_teeth (wide, teeth showing), m_smile
def viseme(ph):
    base = ph.rstrip("012"); stress = ph[-1] if ph[-1] in "012" else ""
    if base in ("P", "B", "M"): return "m_closed"
    if base in ("F", "V"): return "m_teeth"
    if base in ("OW", "UW", "UH", "AO", "OY", "W", "R"): return "m_round"
    if base in ("AA", "AE", "AW", "AY"): return "m_open" if stress == "1" else "m_small"
    if base in ("IY", "EY", "IH", "EH"): return "m_teeth" if stress == "1" else "m_small"
    if base in ("S", "Z", "CH", "JH", "SH", "ZH", "T", "D"): return "m_teeth"
    return "m_small"  # AH ER L N K G NG TH DH HH Y


def _weight(ph):
    base = ph.rstrip("012")
    if ph[-1] in "012": return 2.6 if ph[-1] == "1" else 1.6  # vowels hold the longest
    if base in ("P", "B", "T", "D", "K", "G"): return .8          # stops are quick
    return 1.1


OPENNESS = {"m_closed": 0, "m_small": 1, "m_teeth": 2, "m_smile": 2, "m_round": 2, "m_open": 3}


def read_rms(path):
    txt = open(path).read()
    return [float(v) if "inf" not in v else -90.0 for v in re.findall(r"RMS_level=(-?[\d.]+|-?inf)", txt)]


def visemes(transcript, rms_path, fps=30, dur=45.0, lead=1, quiet=-42.0, min_frames=2):
    words = json.load(open(transcript))
    rms = read_rms(rms_path)
    n = int(round(dur * fps))
    loud = lambda i: rms[i] if 0 <= i < len(rms) else -90.0
    track = ["m_closed"] * n

    for w in words:
        a, b = int(w["start"] * fps), max(int(w["start"] * fps) + 1, int(round(w["end"] * fps)))
        # Whisper ends are often late: keep only the frames where the voice is really sounding
        voiced = [i for i in range(a, min(b, n)) if loud(i) > quiet]
        if not voiced: continue
        a, b = voiced[0], voiced[-1] + 1
        phs = phonemes(w["text"]) or ["AH0"]
        tot = sum(_weight(p) for p in phs)
        t = float(a)
        for p in phs:
            span = (b - a) * _weight(p) / tot
            for i in range(int(round(t)), int(round(t + span))):
                if 0 <= i < n: track[i] = viseme(p)
            t += span

    # quiet frames close; soft frames can't show the widest mouth
    for i in range(n):
        db = loud(i)
        if db < quiet: track[i] = "m_closed"
        elif db < -30 and track[i] == "m_open": track[i] = "m_small"

    # merge one-frame flickers into the neighbour that is more open (reads as a smoother mouth)
    for _ in range(2):
        i = 0
        while i < n:
            j = i
            while j + 1 < n and track[j + 1] == track[i]: j += 1
            if j - i + 1 < min_frames and 0 < i and j + 1 < n:
                prev, nxt = track[i - 1], track[j + 1]
                fill = prev if OPENNESS[prev] >= OPENNESS[nxt] else nxt
                for k in range(i, j + 1): track[k] = fill
            i = j + 1

    # the picture leads the sound slightly
    return track[lead:] + ["m_closed"] * lead


if __name__ == "__main__":
    import sys
    tr = visemes(sys.argv[1], sys.argv[2], dur=float(sys.argv[3]) if len(sys.argv) > 3 else 45)
    from collections import Counter
    print(Counter(tr).most_common(), "changes:", sum(1 for i in range(1, len(tr)) if tr[i] != tr[i - 1]))
