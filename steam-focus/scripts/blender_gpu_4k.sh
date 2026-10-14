#!/usr/bin/env bash
# Native 4K render of the Blender bridge shot on a GPU workstation.
# (On the cloud runner, CPU Cycles needs ~98 s/frame at 4K, so the master uses
# the 1080p render with motion interpolation for the CG camera move.)
#
#   WORK=/path/to/work DEVICE=OPTIX ./scripts/blender_gpu_4k.sh
# then:  ffmpeg -framerate 30 -i $WORK/render_s3_4k/s3_%04d.png -vf "minterpolate=fps=60:mi_mode=mci" \
#          -c:v libx264 -crf 10 -pix_fmt yuv420p public/s3_blender_60.mp4
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${WORK:?set WORK}"
BLENDER="${BLENDER:-$WORK/blender-4.2.23-linux-x64/blender}"
mkdir -p "$WORK/render_s3_4k"
"$BLENDER" -b --factory-startup --python "$HERE/blender/redline_steam_page.py" -- \
  --assets "$WORK/assets" --plate "$WORK/plate" --out "$WORK/render_s3_4k" \
  --anchors "$WORK/render_s3_4k/anchors.json" --samples "${SAMPLES:-64}" --scale 200 \
  --frames 1-292 --device "${DEVICE:-OPTIX}"
