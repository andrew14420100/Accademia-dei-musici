#!/usr/bin/env bash
# STEAM FOCUS — ECC: REDLINE master: 2160x3840, 60 fps CFR, rendered in
# resumable segments (each segment is checked with ffprobe; finished ones are
# skipped on re-run), then joined without re-encoding and muxed with the mix.
#
#   WORK=/path/to/work ./scripts/render_4k60.sh            # full master
#   WORK=... SMOKE=1 ./scripts/render_4k60.sh              # 8 s smoke test only
#
# Env: SEG (frames per segment, default 600 = 10 s), CONC (Remotion
# concurrency, default 2 — 4K tabs are memory-heavy), CRF (default 16),
# SEGDIR (segment cache, default $WORK/seg4k), MIX (pre-master wav), OUT (master path),
# PRESET (x264 preset of the segments, default medium).
# FINAL=1 (v4): segments are an intermediate (use CRF=10, PRESET=veryfast); the master is then
# encoded once by FFmpeg: H.264 High@5.2, CRF ${FINAL_CRF:-17}, preset slow, GOP 120, yuv420p,
# BT.709 primaries/transfer/matrix (limited range), AAC-LC 320k 48 kHz stereo, faststart.
set -euo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${WORK:?set WORK}"
CHROME="${CHROME:-/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell}"
SEG="${SEG:-600}"
CONC="${CONC:-2}"
CRF="${CRF:-16}"
OUTDIR="${SEGDIR:-$WORK/seg4k}"
MIX="${MIX:-$WORK/full_mix_v2.wav}"
OUT="${OUT:-$HERE/out/steam_focus_ecc_redline_full_4K_60fps.mp4}"
PIC="$OUTDIR/picture_4k60.mp4"
mkdir -p "$OUTDIR" "$HERE/out"
cd "$HERE"

TOTAL=$(python3 -c "import json; d=json.load(open('public/full_edl.json')); print(d['frames']*60//d['fps'])")
BUNDLE="$WORK/bundle4k"
npx remotion bundle src/index.ts --out-dir "$BUNDLE" --log=error >/dev/null

render() { # $1 first frame, $2 last frame, $3 out file
  npx remotion render "$BUNDLE" RedlineFull4K "$3.part.mp4" --frames="$1-$2" --codec=h264 --crf="$CRF" \
    --x264-preset="${PRESET:-medium}" --pixel-format=yuv420p --color-space=bt709 --muted --concurrency="$CONC" \
    --browser-executable="$CHROME" --log=error
  mv "$3.part.mp4" "$3"
}

final_encode() { # $1 picture, $2 mix wav, $3 out, [$4 audio offset s, $5 duration s]
  local aoff=() dur=()
  [ -n "${4:-}" ] && aoff=(-ss "$4")
  [ -n "${5:-}" ] && dur=(-t "$5")
  ffmpeg -loglevel error -y -i "$1" "${aoff[@]}" -i "$2" "${dur[@]}" \
    -filter_complex "[1:a]loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.80:attack=3:release=60:level=disabled,aresample=48000[a]" \
    -map 0:v -map "[a]" -c:v libx264 -preset slow -crf "${FINAL_CRF:-17}" -profile:v high -level:v 5.2 \
    -g 120 -keyint_min 60 -pix_fmt yuv420p -color_range tv -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
    -x264-params "colorprim=bt709:transfer=bt709:colormatrix=bt709" \
    -c:a aac -profile:a aac_low -b:a 320k -ar 48000 -ac 2 -movflags +faststart -shortest "$3"
}

frames_of() { ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 "$1" 2>/dev/null || echo 0; }

if [ "${SMOKE:-0}" = 1 ]; then
  # 8 s across a chapter change (swing, plate, overlays, subtitles).
  A=$(python3 -c "import json; d=json.load(open('public/full_edl.json')); print(d['sections']['movement'][0]*2-120)")
  B=$((A + 479))
  t0=$(date +%s)
  render "$A" "$B" "$WORK/smoke_4k60.mp4"
  if [ "${FINAL:-0}" = 1 ]; then  # same final encode + the matching slice of the mix
    final_encode "$WORK/smoke_4k60.mp4" "$MIX" "$WORK/smoke_4k60_final.mp4" "$(python3 -c "print($A/60)")" 8
    ffprobe -v error -show_entries stream=codec_name,profile,level,width,height,pix_fmt,avg_frame_rate,r_frame_rate,color_space,color_primaries,color_transfer,sample_rate,channels,bit_rate -of compact "$WORK/smoke_4k60_final.mp4"
  fi
  echo "smoke: $((B - A + 1)) frames in $(( $(date +%s) - t0 )) s"
  ffprobe -v error -select_streams v -show_entries stream=width,height,avg_frame_rate,r_frame_rate,nb_frames -of compact "$WORK/smoke_4k60.mp4"
  exit 0
fi

: > "$OUTDIR/list.txt"
i=0
for ((a = 0; a < TOTAL; a += SEG)); do
  b=$((a + SEG - 1)); ((b >= TOTAL)) && b=$((TOTAL - 1))
  f="$OUTDIR/seg_$(printf %03d $i).mp4"
  want=$((b - a + 1))
  if [ -f "$f" ] && [ "$(frames_of "$f")" = "$want" ]; then
    echo "skip $f ($want frames)"
  else
    t0=$(date +%s)
    render "$a" "$b" "$f"
    echo "seg $i: frames $a-$b in $(( $(date +%s) - t0 )) s"
  fi
  echo "file '$f'" >> "$OUTDIR/list.txt"
  i=$((i + 1))
done

# Join (stream copy: every segment starts on an IDR frame, same encoder settings).
ffmpeg -loglevel error -y -f concat -safe 0 -i "$OUTDIR/list.txt" -c copy "$PIC"

if [ "${FINAL:-0}" = 1 ]; then
  final_encode "$PIC" "$MIX" "$OUT"
  ffprobe -v error -count_frames -show_entries stream=codec_name,profile,level,width,height,pix_fmt,avg_frame_rate,r_frame_rate,nb_read_frames,color_space,color_primaries,color_transfer \
    -show_entries format=duration,size,bit_rate -of compact "$OUT"
  exit 0
fi

# Master: mix normalised to -14 LUFS with a true-peak safety limiter.
ffmpeg -loglevel error -y -i "$PIC" -i "$MIX" \
  -filter_complex "[1:a]loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.80:attack=3:release=60:level=disabled,aresample=48000[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 320k -ar 48000 -movflags +faststart -shortest \
  "$OUT"

ffprobe -v error -count_frames -show_entries stream=codec_name,width,height,avg_frame_rate,r_frame_rate,nb_read_frames \
  -show_entries format=duration,size -of compact "$OUT"
