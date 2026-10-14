"""Cinematic grade for the V4 cover background, built from the source frame (not an upscale
of an older cover).

    python3 scripts/cover_grade.py FRAME.png public/cover_bg_v4.png [SCALE YSHIFT XBIAS]

FRAME is a 608x1080 vertical crop of the official trailer (picked for the sharpest katana/hand,
see EXPORT_REPORT). The frame is scaled with Lanczos straight to the 2160x3840 canvas (SCALE x
the fill size, shifted up by YSHIFT canvas px), then graded with restrained, global operations
only: local contrast (CLAHE on lightness), deeper shadows with a Steam-blue tint, slightly
cooler highlights, moderate unsharp mask and a soft vignette that keeps the katana in the light.
No content is painted, removed or generated.
"""
import sys

import cv2
import numpy as np

W, H = 2160, 3840
INK = np.array([38, 22, 11], np.float32) / 255  # #0B1626 in BGR
STEAM = np.array([244, 192, 102], np.float32) / 255  # #66C0F4 in BGR

src_path, out_path = sys.argv[1:3]
scale = float(sys.argv[3]) if len(sys.argv) > 3 else 1.15
yshift = int(sys.argv[4]) if len(sys.argv) > 4 else 660
xbias = float(sys.argv[5]) if len(sys.argv) > 5 else 0.5

src = cv2.imread(src_path)
k = H / src.shape[0] * scale
big = cv2.resize(src, (round(src.shape[1] * k), round(src.shape[0] * k)), interpolation=cv2.INTER_LANCZOS4)
x0 = int((big.shape[1] - W) * xbias)
canvas = np.empty((H, W, 3), np.uint8)
canvas[:] = (INK * 255).astype(np.uint8)
part = big[yshift:yshift + H, x0:x0 + W]
canvas[:part.shape[0]] = part

# local contrast on lightness only (colours untouched)
lab = cv2.cvtColor(canvas, cv2.COLOR_BGR2LAB)
l, a, b = cv2.split(lab)
l = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(6, 10)).apply(l)
img = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR).astype(np.float32) / 255

# tone: deeper shadows (toe), gentle highlight roll-off
lum = img @ np.array([0.114, 0.587, 0.299], np.float32)
img = np.clip(img, 0, 1) ** 1.12
img = img * 1.04 - 0.012
# split tone: shadows toward night blue / Steam blue, highlights a touch cooler
sh = np.clip(1 - lum / 0.45, 0, 1)[..., None]
hi = np.clip((lum - 0.6) / 0.4, 0, 1)[..., None]
img = img * (1 - 0.22 * sh) + (INK * 0.6 + STEAM * 0.12) * 0.22 * sh
img = img * (1 - 0.05 * hi) + STEAM * 0.05 * hi
# saturation +6% (keeps the leaves and glove natural)
hsv = cv2.cvtColor(np.clip(img, 0, 1), cv2.COLOR_BGR2HSV)
hsv[..., 1] = np.clip(hsv[..., 1] * 1.06, 0, 1)
img = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

# soft vignette, centred on the katana (canvas ~ 0.5 x 0.40)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
d = np.sqrt(((xx - W * 0.5) / (W * 0.85)) ** 2 + ((yy - H * 0.40) / (H * 0.62)) ** 2)
img *= (1 - 0.32 * np.clip(d - 0.35, 0, 1) ** 1.4)[..., None]

out = np.clip(img * 255, 0, 255).astype(np.uint8)
# moderate unsharp (radius matched to the ~3.5x upscale)
blur = cv2.GaussianBlur(out, (0, 0), 2.2)
out = cv2.addWeighted(out, 1.45, blur, -0.45, 0)
cv2.imwrite(out_path, out, [cv2.IMWRITE_PNG_COMPRESSION, 6])
print(out_path, out.shape)
