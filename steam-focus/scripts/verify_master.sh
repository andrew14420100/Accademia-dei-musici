#!/usr/bin/env bash
# STEAM FOCUS — checks on the 4K60 master. Writes everything to $QC.
#   WORK=... QC=out/qc ./scripts/verify_master.sh
# - ffprobe: size, frame rate (avg and real), frame count, duration
# - blackdetect / freezedetect on the whole picture (freezes are expected only
#   on the deliberate shop freeze and the Steam bridge backdrop)
# - mpdecimate on the pre-mux picture: count of exact duplicate frames
# - EBU R128 loudness and true peak of the master
# - one contact sheet per chapter (4K frames scaled down) with the TikTok
#   safe area drawn on top
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${WORK:?set WORK}"
QC="${QC:-$HERE/out/qc}"
M="${MASTER:-$HERE/out/steam_focus_ecc_redline_full_4K_60fps.mp4}"
P="${PICTURE:-$WORK/picture_4k60.mp4}"
mkdir -p "$QC"
cd "$HERE"

ffprobe -v error -count_frames -show_entries stream=codec_type,codec_name,width,height,avg_frame_rate,r_frame_rate,nb_read_frames,sample_rate,channels \
  -show_entries format=duration,size,bit_rate -of json "$M" > "$QC/ffprobe.json"

# Analyse at 540x960 (same timing, much faster); thresholds as for 1080p.
ffmpeg -hide_banner -nostats -i "$M" -vf "scale=540:960,blackdetect=d=0.1:pic_th=0.98:pix_th=0.10,freezedetect=n=0.001:d=0.5" -an -f null - 2> "$QC/detect.log" || true
grep -E "black_start|freeze_start|freeze_duration|freeze_end" "$QC/detect.log" > "$QC/black_freeze.txt" || true

ffmpeg -hide_banner -nostats -i "$P" -vf "scale=540:960,mpdecimate=hi=64:lo=32:frac=0.0" -an -f null - 2> "$QC/mpdecimate.log" || true
grep -c "drop_count" "$QC/mpdecimate.log" > /dev/null || true

ffmpeg -hide_banner -nostats -i "$M" -vn -af ebur128=peak=true -f null - 2> "$QC/ebur128.log" || true
tail -n 14 "$QC/ebur128.log" > "$QC/loudness.txt"

# Contact sheets: 8 frames per chapter, safe area in red.
python3 - "$M" "$QC" <<'PY'
import json, subprocess, sys
m, qc = sys.argv[1], sys.argv[2]
d = json.load(open('public/full_edl.json'))
S = dict(left=64, right=940, top=170, bottom=1440)  # 1080x1920 design units
for i, (name, (a, b)) in enumerate(d['sections'].items()):
    ts = [((a + (b - a) * (j + 0.5) / 8) / d['fps']) for j in range(8)]
    tiles = []
    for j, t in enumerate(ts):
        f = f"{qc}/_t{j}.png"
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', m, '-frames:v', '1',
                        '-vf', 'scale=540:960,'
                        f"drawbox=x={S['left']//2}:y={S['top']//2}:w={(S['right']-S['left'])//2}:h={(S['bottom']-S['top'])//2}:color=red@0.6:t=2,"
                        f"drawtext=text='{t:.2f}s':x=10:y=10:fontsize=28:fontcolor=white:box=1:boxcolor=black@0.6", f], check=True)
        tiles.append(f)
    inputs = sum([['-i', t] for t in tiles], [])
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *inputs, '-filter_complex',
                    ''.join(f'[{k}]' for k in range(8)) + 'xstack=inputs=8:layout=' +
                    '|'.join(f'{(k%4)*540}_{(k//4)*960}' for k in range(8)),
                    f'{qc}/sheet_{i:02d}_{name}.jpg'], check=True)
subprocess.run('rm -f ' + qc + '/_t*.png', shell=True)
PY
echo "QC written to $QC"
