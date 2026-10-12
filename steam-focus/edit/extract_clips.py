"""Cut every trailer shot of the EDL into its own clip (frame-accurate).

video -> public/full/<id>.mp4 (for Remotion), audio -> <work>/full_audio/<id>.wav
usage: python3 extract_clips.py public/full_edl.json <work>
"""
import json
import os
import subprocess
import sys

edl = json.load(open(sys.argv[1]))
work = sys.argv[2]
here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.makedirs(f"{here}/public/full", exist_ok=True)
os.makedirs(f"{work}/full_audio", exist_ok=True)
src = {"G": f"{work}/assets/gameplay.mp4"}
fps = edl["fps"]

for s in edl["shots"]:
    if s["src"] not in src:
        continue
    n = s["frames"] + 2  # tiny margin for seeking/rounding
    dur = n / fps
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{s['sin']:.3f}", "-i", src[s["src"]],
                    "-frames:v", str(n), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "13",
                    "-g", "15", "-pix_fmt", "yuv420p", f"{here}/public/full/{s['id']}.mp4"], check=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{s['sin']:.3f}", "-t", f"{dur:.3f}",
                    "-i", src[s["src"]], "-vn", "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le",
                    f"{work}/full_audio/{s['id']}.wav"], check=True)
    print("clip", s["id"], s["frames"])
