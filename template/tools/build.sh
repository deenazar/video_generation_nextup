#!/bin/sh
# Build one language: sh tools/build.sh ta   (or en). Writes index.html + assets/audio/sfx_<lang>.wav
set -e
L=${1:-ta}
python3 tools/gen.py $L
python3 tools/sfx.py $L
ffmpeg -v error -y -i assets/audio/sfx_$L.wav -af apad -t ${DUR:-45} tools/sfx_full.wav && mv tools/sfx_full.wav assets/audio/sfx_$L.wav
