#!/usr/bin/env bash
# STEAM FOCUS — ECC: REDLINE full vertical report (100–120 s), end to end.
#
#   WORK=/path/to/work ./scripts/build_full.sh
#
# Needs in $WORK: assets/ (scripts/fetch_assets.sh), render_s3/ (Blender shot),
# audio_s3.wav, and a Python 3.12 venv at $WORK/tts-venv with kokoro +
# faster-whisper (see README.md). Skips the voice if $WORK/vo already exists
# and SKIP_VOICE=1.
set -euo pipefail

HERE="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${WORK:?set WORK to the working directory}"
CHROME="${CHROME:-/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell}"
OUT="$HERE/out"
mkdir -p "$OUT" "$WORK/vo"
cd "$HERE"

# 1. Narration (Kokoro TTS) + ASR round-trip report and word timings.
if [ "${SKIP_VOICE:-0}" != 1 ]; then
  "$WORK/tts-venv/bin/python" narration/synth_voice.py narration/ecc_redline_it.json "$WORK/vo" public/vo_timing.json
fi

# 2. Edit decision list, subtitles (SRT), shot clips.
ffmpeg -hide_banner -i "$WORK/assets/gameplay.mp4" -an \
  -vf "scale=320:-1,select='gt(scene,0.28)',metadata=print:file=$WORK/scenes_gameplay.txt" -f null - >/dev/null 2>&1
grep -o "pts_time:[0-9.]*" "$WORK/scenes_gameplay.txt" | cut -d: -f2 > "$WORK/cuts_gameplay.txt"
python3 edit/plan_full.py public/vo_timing.json public/full_edl.json "$WORK/cuts_gameplay.txt"
python3 edit/extract_clips.py public/full_edl.json "$WORK"
python3 scripts/track_point.py public/full/r_revive.mp4 760 440 200 240 36 public/track_revive.json

# 3. Blender bridge shot as a seekable clip (rendered by blender/redline_steam_page.py).
ffmpeg -loglevel error -y -framerate 30 -i "$WORK/render_s3/s3_%04d.png" \
  -c:v libx264 -preset slow -crf 8 -pix_fmt yuv420p -g 1 public/s3_blender.mp4

# 4. Picture.
npx remotion render src/index.ts RedlineFull "$WORK/full_picture.mp4" --codec=h264 --crf=12 --muted \
  --concurrency=4 --browser-executable="$CHROME" --log=error

# 5. Sound: voice + ducked trailer audio + design.
python3 audio/build_full_audio.py public/full_edl.json "$WORK" "$WORK/full_mix.wav"

# 6. Master: fine grain, H.264 High 30 fps, AAC 48 kHz, -14 LUFS / -1 dBTP.
ffmpeg -loglevel error -y -i "$WORK/full_picture.mp4" -i "$WORK/full_mix.wav" \
  -filter_complex "[0:v]noise=c0s=3:c0f=t,format=yuv420p[v];[1:a]loudnorm=I=-14:TP=-1.0:LRA=11[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 17 -profile:v high -level 4.2 -r 30 \
  -x264-params "aq-mode=3" -movflags +faststart -c:a aac -b:a 256k -ar 48000 -shortest \
  "$OUT/steam_focus_ecc_redline_full.mp4"

# 7. Companions: SRT, cover, sources, narration script, mix.
cp public/steam_focus_ecc_redline.srt "$OUT/steam_focus_ecc_redline.srt"
cp narration/steam_focus_ecc_redline_sources.txt "$OUT/steam_focus_ecc_redline_sources.txt"
python3 -c "
import json
d = json.load(open('narration/ecc_redline_it.json'))
with open('$OUT/steam_focus_ecc_redline_narrazione.txt', 'w') as f:
    f.write(d['title'] + ' — testo della narrazione (voce: ' + d['voice'] + ', ' + d['engine'] + ')\n\n')
    sec = None
    for l in d['lines']:
        if l['section'] != sec:
            sec = l['section']; f.write('\n[' + sec.upper() + ']\n')
        f.write(l['text'] + '\n')
"
cp "$WORK/full_mix.wav" "$OUT/steam_focus_ecc_redline_mix.wav"
npx remotion still src/index.ts RedlineFull "$OUT/steam_focus_ecc_redline_cover.png" \
  --frame="${COVER_FRAME:-212}" --browser-executable="$CHROME" --log=error

ffprobe -v error -count_frames -show_entries stream=codec_name,width,height,r_frame_rate,nb_read_frames \
  -show_entries format=duration,size -of compact "$OUT/steam_focus_ecc_redline_full.mp4"
