"""Track the running player in shot S2 so its callout stays attached to him.

usage: python3 track_runner.py public/s2_combat.mp4 public/s2_track.json
"""
import json
import sys

import cv2
import numpy as np

src, out = sys.argv[1], sys.argv[2]
cap = cv2.VideoCapture(src)
ok, frame = cap.read()
tracker = cv2.TrackerMIL_create()
tracker.init(frame, (868, 590, 90, 180))  # player on the road, first frame
pts = [[913.0, 680.0]]
while True:
    ok, frame = cap.read()
    if not ok:
        break
    found, (x, y, w, h) = tracker.update(frame)
    pts.append([x + w / 2, y + h / 2] if found else pts[-1])

# Centred 5-frame average removes tracker jitter without lag.
p = np.array(pts, float)
k = 5
padded = np.pad(p, ((k // 2, k // 2), (0, 0)), mode="edge")
smooth = np.array([padded[i:i + k].mean(0) for i in range(len(p))])
with open(out, "w") as fh:
    json.dump({"fps": 30, "source": [1920, 1080], "runner": smooth.round(1).tolist()}, fh)
print(len(smooth), "frames tracked")
