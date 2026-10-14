#!/usr/bin/env bash
# STEAM FOCUS — ECC: REDLINE vertical demo: assemble the final MP4.
#
#   WORK=/path/to/work ./scripts/build_demo.sh
#
# Expects in $WORK (see scripts/fetch_assets.sh and README.md):
#   render_s3/s3_0001..0292.png   Blender shot (blender/redline_steam_page.py)
#   audio_s1.wav audio_s2.wav audio_s3.wav   trailer audio for each shot
set -euo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${WORK:?set WORK to the working directory}"
CHROME="${CHROME:-/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell}"
OUT="$HERE/out"
mkdir -p "$OUT"

# 1. Blender frames -> near-lossless clip Remotion can seek frame-accurately.
ffmpeg -loglevel error -y -framerate 30 -i "$WORK/render_s3/s3_%04d.png" \
  -c:v libx264 -preset slow -crf 8 -pix_fmt yuv420p -g 1 \
  "$HERE/public/s3_blender.mp4"

# 2. Picture: Remotion composition (ProRes 4444 intermediate, no audio).
(cd "$HERE" && npx remotion render src/index.ts RedlineDemo "$OUT/redline_demo_picture.mov" \
  --codec=prores --prores-profile=4444 --browser-executable="$CHROME" --muted --log=error)

# 3. Sound design + trailer beds, frame-synced.
python3 "$HERE/audio/build_audio.py" "$WORK" "$WORK/mix.wav"

# 4. Master: fine grain, H.264 High for social, loudness -14 LUFS / -1 dBTP.
ffmpeg -loglevel error -y -i "$OUT/redline_demo_picture.mov" -i "$WORK/mix.wav" \
  -filter_complex "[0:v]noise=c0s=3:c0f=t,format=yuv420p[v];[1:a]loudnorm=I=-14:TP=-1.0:LRA=11[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 17 -profile:v high -level 4.2 \
  -x264-params "aq-mode=3" -movflags +faststart \
  -c:a aac -b:a 320k -ar 48000 -shortest \
  "$OUT/redline_demo_9x16.mp4"

ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,duration \
  -show_entries format=duration,size -of compact "$OUT/redline_demo_9x16.mp4"
