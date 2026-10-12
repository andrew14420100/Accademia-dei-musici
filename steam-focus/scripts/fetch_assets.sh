#!/usr/bin/env bash
# Download the authentic ECC: REDLINE material from its Steam store page
# (app 5268340) plus Blender, and prepare everything the demo needs.
#
#   WORK=/path/to/work ./scripts/fetch_assets.sh
set -euo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${WORK:?set WORK to the working directory}"
APP=5268340
CHROME="${CHROME:-/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell}"
mkdir -p "$WORK/assets" "$WORK/plate"
cd "$WORK"

# Blender 4.2 LTS (free, portable). Cycles CPU is used: EEVEE needs a GPU/EGL.
if [ ! -x blender-4.2.23-linux-x64/blender ]; then
  curl -sS -o blender.tar.xz https://download.blender.org/release/Blender4.2/blender-4.2.23-linux-x64.tar.xz
  tar xf blender.tar.xz && rm blender.tar.xz
fi

# Official store data and the "Gameplay Footage" trailer (1080p30).
curl -sS "https://store.steampowered.com/api/appdetails?appids=$APP&l=italian&cc=IT" > assets/appdetails.json
HLS=$(python3 -c "
import json;d=json.load(open('assets/appdetails.json'))['$APP']['data']
m=[x for x in d['movies'] if x['name']=='Gameplay Footage'][0]['hls_h264']
print(m.split('hls_264_master')[0])")
ffmpeg -loglevel error -y -i "${HLS}hls_264_0_video.m3u8" -i "${HLS}hls_264_4_audio.m3u8" \
  -map 0:v -map 1:a -c copy assets/gameplay.mp4
python3 -c "
import json,urllib.request;d=json.load(open('assets/appdetails.json'))['$APP']['data']
for i,s in enumerate(d['screenshots'],1): urllib.request.urlretrieve(s['path_full'].split('?')[0], f'assets/shot_{i:02d}.jpg')"

# The real store page, captured at 2x (3840 px wide) after selecting a screenshot.
(cd "$HERE" && node scripts/capture_steam_page.mjs "$WORK/assets" "$CHROME")
python3 - "$WORK/assets" <<'EOF'
import sys
from PIL import Image, ImageEnhance, ImageFilter
a = sys.argv[1]
Image.open(f'{a}/steam_page_full.png').convert('RGB').crop((0, 0, 3840, 4320)).save(f'{a}/page_tex.png')
bg = Image.open(f'{a}/shot_05.jpg').convert('RGB').resize((1280, 720)).filter(ImageFilter.GaussianBlur(28))
ImageEnhance.Brightness(bg).enhance(0.8).save(f'{a}/bg_blur.jpg', quality=92)
EOF

# Shots (source timecodes in the official Gameplay Footage trailer).
G=assets/gameplay.mp4
P="$HERE/public"
ffmpeg -loglevel error -y -ss 63.25 -i $G -frames:v 104 -c:v libx264 -crf 12 -preset slow -an "$P/s1_heli.mp4"
ffmpeg -loglevel error -y -ss 349.567 -i $G -frames:v 54 -c:v libx264 -crf 12 -preset slow -an "$P/s2_combat.mp4"
ffmpeg -loglevel error -y -ss 364.9 -i $G -frames:v 300 -q:v 2 plate/p_%04d.jpg
ffmpeg -loglevel error -y -ss 63.25 -t 3.4667 -i $G -vn -c:a pcm_s16le audio_s1.wav
ffmpeg -loglevel error -y -ss 349.567 -t 1.8 -i $G -vn -c:a pcm_s16le audio_s2.wav
ffmpeg -loglevel error -y -ss 364.9 -t 10 -i $G -vn -c:a pcm_s16le audio_s3.wav
# Steam "inverse" logo (white, with (R)) from Valve's brand guidelines PDF, page 7.
mkdir -p "$P/brand"
curl -sS -o assets/steam_brandGuidelines.pdf \
  https://shared.fastly.steamstatic.com/community_assets/images/steamworks_docs/english/steam_brandGuidelines.pdf
pdftocairo -png -r 1600 -f 7 -l 7 -x 10560 -y 9120 -W 5680 -H 1952 assets/steam_brandGuidelines.pdf assets/inv 2>/dev/null
python3 - "$WORK/assets/inv-07.png" "$P/brand/steam_logo_inverse.png" <<'EOF2'
import sys
import numpy as np
from PIL import Image
im = np.asarray(Image.open(sys.argv[1]).convert('L')).astype(float)
bg = np.median(im[:20, :20])
a = np.clip((im - bg) / (255 - bg), 0, 1)
ys, xs = np.where(a > 0.02)
a = a[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
out = np.zeros(a.shape + (4,), np.uint8)
out[..., :3] = 255
out[..., 3] = (a * 255).round()
Image.fromarray(out).save(sys.argv[2])
EOF2
echo "assets ready in $WORK"
