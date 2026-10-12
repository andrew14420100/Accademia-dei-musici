"""Track one subject through a clip so its callout stays attached to it.

usage: python3 track_point.py <clip.mp4> <x> <y> <w> <h> <frames> <out.json>
(x, y, w, h: first-frame box in source pixels; frames: how many to track —
stop before any cut, where tracking is no longer reliable)
"""
import json
import sys

import cv2
import numpy as np

src, x, y, w, h, frames, out = sys.argv[1], *map(int, sys.argv[2:7]), sys.argv[7]
cap = cv2.VideoCapture(src)
ok, frame = cap.read()
tracker = cv2.TrackerMIL_create()
tracker.init(frame, (x, y, w, h))
pts = [[x + w / 2, y + h / 2]]
while len(pts) < frames:
    ok, frame = cap.read()
    if not ok:
        break
    found, (bx, by, bw, bh) = tracker.update(frame)
    pts.append([bx + bw / 2, by + bh / 2] if found else pts[-1])

# Centred 5-frame average removes tracker jitter without lag.
p = np.array(pts, float)
k = 5
padded = np.pad(p, ((k // 2, k // 2), (0, 0)), mode="edge")
smooth = np.array([padded[i:i + k].mean(0) for i in range(len(p))])
with open(out, "w") as fh:
    json.dump({"fps": 30, "source": [1920, 1080], "points": smooth.round(1).tolist()}, fh)
print(len(smooth), "frames tracked", smooth[[0, -1]].round(0).tolist())
