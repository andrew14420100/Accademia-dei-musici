#!/usr/bin/env bash
# Pre-upscale the 1080p trailer clips for the 4K/60 composition.
#   ./scripts/upscale_clips.sh
# public/full/<id>.mp4   (1920x1080, 30 fps) -> public/full_up/<id>.mp4   (3840x2160)
# public/full60/<id>.mp4 (1920x1080, 60 fps) -> public/full60_up/<id>.mp4 (3840x2160)
# Lanczos 2x + light unsharp (luma only), so the browser only has to scale the remaining
# ~1.8x inside the 2160x3840 frame. This is interpolation: the result is NOT native 4K detail
# (ML super-resolution was evaluated in V3 and rejected: it altered HUD text and textures).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p public/full_up public/full60_up
ids=$(python3 -c "import json; print(' '.join(s['id'] for s in json.load(open('public/full_edl.json'))['shots'] if s['src'] == 'G'))")
for dir in full full60; do
  for id in $ids; do
    in="public/$dir/$id.mp4"
    [ -f "$in" ] || continue
    if [ "$dir" = full60 ] && ! python3 -c "import json,sys; sys.exit(0 if '$id' in json.load(open('public/full60/list.json'))['ids'] else 1)"; then continue; fi
    out="public/${dir}_up/$id.mp4"
    ffmpeg -loglevel error -y -i "$in" \
      -vf "scale=3840:2160:flags=lanczos+accurate_rnd+full_chroma_int,unsharp=5:5:0.45:5:5:0" \
      -c:v libx264 -preset fast -crf 15 -g 30 -pix_fmt yuv420p "$out.tmp.mp4"
    mv "$out.tmp.mp4" "$out"
    echo "up $dir/$id"
  done
done
