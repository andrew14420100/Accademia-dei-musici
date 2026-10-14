#!/usr/bin/env bash
# 30 -> 60 fps motion-compensated interpolation, only for the shots listed in
# public/full60/list.json (smooth camera moves; shots with weapons close to the
# lens, explosions or fast pans ghost and stay at native 30, doubled in the 60 fps timeline).
#   ./scripts/interp_clips.sh            (after edit/extract_clips.py)
set -euo pipefail
cd "$(dirname "$0")/.."
for id in $(python3 -c "import json; print(' '.join(json.load(open('public/full60/list.json'))['ids']))"); do
  ffmpeg -loglevel error -y -i "public/full/$id.mp4" \
    -vf "minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" \
    -c:v libx264 -preset medium -crf 13 -g 30 -pix_fmt yuv420p "public/full60/$id.mp4"
  echo "interp $id $(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 "public/full60/$id.mp4") frames"
done
