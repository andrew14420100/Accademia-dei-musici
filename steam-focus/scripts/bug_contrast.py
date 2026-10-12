"""Per-shot scrim strength behind the STEAM FOCUS badge (top-left).

    python3 scripts/bug_contrast.py public/full_edl.json public/bug_contrast.json

For each gameplay shot, samples 5 frames of public/full/<id>.mp4, maps the badge area
(design px x 64..340, y 160..270) back into the source through the shot's reframe, and
measures mean luma and local contrast. Bright or busy backgrounds get a stronger
night-blue scrim (max 0.85), dark ones a light one (min 0.3).
"""
import json
import sys

import cv2
import numpy as np

W, H, SRC_W, SRC_H = 1080, 1920, 1920, 1080
BOX = (64, 160, 340, 270)


def lerp_keys(keys, t):
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            return v0 + (v1 - v0) * (t - t0) / max(t1 - t0, 1e-6)
    return keys[-1][1]


def crop(s, f, fps):
    t = f / fps
    z = s['zoom'][0] + (s['zoom'][1] - s['zoom'][0]) * min(1, f / max(1, s['frames'])) if s.get('zoom') else 1.03
    scale = H / SRC_H * z
    hw, hh = W / 2 / scale, H / 2 / scale
    cx = lerp_keys(s['cx'], t) if s.get('cx') else SRC_W / 2
    cx = min(SRC_W - hw, max(hw, cx))
    cy = min(SRC_H - hh, max(hh, s.get('cy') or SRC_H / 2))
    return cx, cy, scale


def main():
    edl = json.load(open(sys.argv[1]))
    fps = edl['fps']
    out = {}
    for s in edl['shots']:
        if s['src'] == 'S3':
            continue
        cap = cv2.VideoCapture(f"public/full/{s['id']}.mp4")
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        vals = []
        for k in np.linspace(0, min(n, s['frames']) - 1, 5).astype(int):
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(k))
            ok, img = cap.read()
            if not ok:
                continue
            cx, cy, sc = crop(s, k, fps)
            x0 = int(cx + (BOX[0] - W / 2) / sc)
            x1 = int(cx + (BOX[2] - W / 2) / sc)
            y0 = int(cy + (BOX[1] - H / 2) / sc)
            y1 = int(cy + (BOX[3] - H / 2) / sc)
            g = cv2.cvtColor(img[max(0, y0):y1, max(0, x0):x1], cv2.COLOR_BGR2GRAY) / 255.0
            vals.append((g.mean(), g.std()))
        cap.release()
        luma = float(np.mean([v[0] for v in vals]))
        busy = float(np.mean([v[1] for v in vals]))
        out[s['id']] = round(float(np.clip(0.3 + 0.75 * luma + 0.6 * busy, 0.3, 0.85)), 2)
        print(f"{s['id']:12s} luma {luma:.2f} std {busy:.2f} -> {out[s['id']]}")
    json.dump(out, open(sys.argv[2], 'w'), indent=1)


if __name__ == '__main__':
    main()
