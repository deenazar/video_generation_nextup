#!/usr/bin/env python3
"""Synthesises small UI sound effects with ffmpeg and places them on the reel's visible actions.
Run from the project folder after gen.py: python3 tools/sfx.py ta  ->  assets/audio/sfx_ta.wav"""
import subprocess, os, sys, json
LANG = sys.argv[1] if len(sys.argv) > 1 else "ta"
DUR = 45.0
T = "tools/sfx_parts"; os.makedirs(T, exist_ok=True)
SR = 44100
PARTS = {
 "pop":   ("aevalsrc='0.6*sin(2*PI*(500+900*exp(-t*30))*t)*exp(-t*26)':d=0.14", ""),
 "tick":  ("aevalsrc='0.35*sin(2*PI*2600*t)*exp(-t*95)':d=0.05", ""),
 "ding":  ("aevalsrc='0.35*(sin(2*PI*1318*t)+0.5*sin(2*PI*2637*t)+0.25*sin(2*PI*3951*t))*exp(-t*4)':d=1.1", ""),
 "thud":  ("aevalsrc='0.9*sin(2*PI*(95-45*t)*t)*exp(-t*11)':d=0.45", ""),
 "shine": ("aevalsrc='0.18*(sin(2*PI*1760*t)+sin(2*PI*2349*t)+sin(2*PI*2960*t))*(0.5+0.5*sin(2*PI*18*t))*exp(-t*2.5)':d=0.9", ""),
 "whoosh":("anoisesrc=d=0.5:c=pink:a=0.6", ",bandpass=f=1400:w=1800,afade=t=in:d=0.22,afade=t=out:st=0.24:d=0.26"),
}
for k, (src, post) in PARTS.items():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", src, "-af", f"aresample={SR}{post}", "-ac", "1", f"{T}/{k}.wav"], check=True)

EV = [tuple(e) for e in json.load(open(f"tools/sfx_events_{LANG}.json"))]

args = ["ffmpeg", "-v", "error", "-y"]
for k in PARTS: args += ["-i", f"{T}/{k}.wav"]
keys = list(PARTS)
fc, labs = [], []
for i, (k, t) in enumerate(EV):
    ms = int(max(0, t) * 1000)
    fc.append(f"[{keys.index(k)}]adelay={ms}|{ms}[e{i}]")
    labs.append(f"[e{i}]")
# each input can only be consumed once -> split them first
splits = []
for j, k in enumerate(keys):
    n = sum(1 for e in EV if e[0] == k)
    if n: splits.append(f"[{j}]asplit={n}" + "".join(f"[{k}{m}]" for m in range(n)))
cnt = {k: 0 for k in keys}
fc = []
for i, (k, t) in enumerate(EV):
    ms = int(max(0, t) * 1000)
    fc.append(f"[{k}{cnt[k]}]adelay={ms}|{ms}[e{i}]"); cnt[k] += 1
graph = ";".join(splits + fc) + ";" + "".join(labs) + f"amix=inputs={len(EV)}:normalize=0,apad=whole_len={int(DUR*SR)},atrim=0:{DUR},volume=0.9[out]"
args += ["-filter_complex", graph, "-map", "[out]", "-ar", str(SR), "-ac", "2", f"assets/audio/sfx_{LANG}.wav"]
subprocess.run(args, check=True)
print(f"sfx_{LANG}.wav:", len(EV), "events")
