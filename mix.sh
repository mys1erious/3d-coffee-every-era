#!/bin/sh
# Adds the sound to a silent ?play recording: code-made SFX (sfx.py) + the narrator lines in vo/l0..l8.mp3,
# holds the end card for PAD seconds, and normalises to -14 LUFS.
# usage: sh mix.sh <silent.mp4> <out.mp4> [pad_seconds]
set -e
IN=$1; OUT=$2; PAD=${3:-0}
mkdir -p tmp
python3 sfx.py tmp/sfx.wav
# narrator: era i says its "Lost" line at 2.6i+0.5 s; the zero-g era at 19.35 s, the end card line at 20.05 s
DELAYS="500 3100 5700 8300 10900 13500 16100 19350 20050"
INPUTS=""; CHAIN=""; MIXIN="[s]"; k=0
for d in $DELAYS; do
  INPUTS="$INPUTS -i vo/l$k.mp3"
  CHAIN="$CHAIN[$((k + 2)):a]aresample=48000,aformat=channel_layouts=mono,adelay=$d,volume=1.15[v$k];"
  MIXIN="$MIXIN[v$k]"; k=$((k + 1))
done
LEN=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
TOTAL=$(python3 -c "print(round($LEN + $PAD, 3))")
ffmpeg -y -loglevel error -i "$IN" -i tmp/sfx.wav $INPUTS -filter_complex \
  "[1:a]volume=0.62,apad[s];$CHAIN${MIXIN}amix=inputs=$((k + 1)):normalize=0:duration=first,atrim=0:$TOTAL,acompressor=threshold=-20dB:ratio=3:attack=4:release=90:makeup=2,alimiter=limit=0.5:level=false[m]" \
  -map "[m]" -ar 48000 tmp/mix.wav
M=$(ffmpeg -i tmp/mix.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
P=$(echo "$M" | python3 -c "import json,sys; d=json.load(sys.stdin); print(f\"measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}:measured_thresh={d['input_thresh']}:offset={d['target_offset']}\")")
ffmpeg -y -loglevel error -i "$IN" -i tmp/mix.wav -filter_complex \
  "[0:v]tpad=stop_mode=clone:stop_duration=$PAD[v];[1:a]loudnorm=I=-14:TP=-1.5:LRA=11:$P:linear=true,aresample=48000[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -profile:v high -c:a aac -b:a 192k -ac 2 -movflags +faststart "$OUT"
ffmpeg -i "$OUT" -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1
