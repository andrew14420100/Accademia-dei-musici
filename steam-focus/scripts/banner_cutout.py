"""Make the approved STEAM FOCUS / ECC: REDLINE banner transparent outside its rounded frame.

    python3 scripts/banner_cutout.py SRC.webp OUT.png

Only the black area outside the banner is removed: an anti-aliased rounded-rectangle mask is
placed just outside the glowing border line (measured on the 2000x667 source: line centre at
x 14 / 1986, y 13.5 / 652.5, corner radius ~48 px). Inside the mask every pixel is copied
unchanged (blue background, text, chips); the result is cropped to the frame. No resampling.
"""
import sys

import numpy as np
from PIL import Image

src, out = sys.argv[1:3]
im = Image.open(src).convert('RGB')
rgb = np.asarray(im)
H, W = rgb.shape[:2]

# outer edge of the border line (+1.5 px from its centre) and matching radius
X0, X1, Y0, Y1, R = 12.5, 1987.5, 12.0, 654.0, 49.5

ss = 4  # supersampling for the anti-aliased edge
ys = (np.arange(H * ss) + 0.5) / ss
xs = (np.arange(W * ss) + 0.5) / ss
X, Y = np.meshgrid(xs, ys)
cx = np.clip(X, X0 + R, X1 - R)
cy = np.clip(Y, Y0 + R, Y1 - R)
inside = ((X - cx) ** 2 + (Y - cy) ** 2 <= R * R) & (X >= X0) & (X <= X1) & (Y >= Y0) & (Y <= Y1)
alpha = inside.reshape(H, ss, W, ss).mean(axis=(1, 3))

rgba = np.dstack([rgb, np.round(alpha * 255).astype(np.uint8)])
rgba[rgba[..., 3] == 0, :3] = 0  # no stray colour under fully transparent pixels (no fringes in editors)
x0, x1, y0, y1 = int(np.floor(X0)), int(np.ceil(X1)), int(np.floor(Y0)), int(np.ceil(Y1))
Image.fromarray(rgba[y0:y1, x0:x1], 'RGBA').save(out, optimize=True)
print(out, x1 - x0, 'x', y1 - y0, 'transparent px', int((alpha[y0:y1, x0:x1] == 0).sum()))
