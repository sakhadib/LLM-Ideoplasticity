"""Measure anisotropy in the letterhead emblem using shapes that should be round (nucleus and electron dots)
and compare with the same dots in the Wikipedia PNG."""
import sys

import numpy as np
import pymupdf
from PIL import Image
from scipy import ndimage

doc = pymupdf.open(r'C:\Users\rifat\Desktop\IUT Stuff\IUTLetterHeadBackground.pdf')
page = doc[0]
draws = [d for d in page.get_drawings() if d['rect'].x1 < 150 and d['rect'].y1 < 150]
print('filled small shapes (w, h, w/h):')
for d in draws:
    r = d['rect']
    if d['type'] == 'f' and r.width < 5 and r.height < 5 and r.width > 0.8:
        # Use actual on-curve extents via control points of a four-Bezier ellipse
        n = len(d['items'])
        print(f'  rect {r.x0:.2f},{r.y0:.2f} w={r.width:.3f} h={r.height:.3f} ratio={r.width / r.height:.3f} items={n}')

# The large ellipse extents of the gear hub: use outer green shield symmetric width vs. crescent
for d in draws:
    r = d['rect']
    if d.get('fill') is not None and tuple(round(v, 2) for v in d['fill'][:3]) in ((0.93, 0.11, 0.14),):
        print('crescent rect', [round(v, 2) for v in r], 'ratio', round(r.width / r.height, 3))

# Wikipedia PNG: measure the nucleus blob
wiki = Image.open(sys.argv[1]).convert('RGBA')
arr = np.asarray(wiki).astype(int)
dark = (arr[..., 3] > 128) & (arr[..., :3].sum(axis=2) < 200)
H, W = dark.shape
lab, n = ndimage.label(dark)
objs = ndimage.find_objects(lab)
print('wiki size', W, H)
for i, s in enumerate(objs):
    h = s[0].stop - s[0].start
    w = s[1].stop - s[1].start
    area = (lab[s] == i + 1).sum()
    cy, cx = (s[0].start + s[0].stop) / 2, (s[1].start + s[1].stop) / 2
    if 6 <= w <= 30 and 6 <= h <= 30 and area / (w * h) > 0.6 and H * 0.45 < cy < H * 0.8:
        print(f'  wiki blob at ({cx:.0f},{cy:.0f}) w={w} h={h} ratio={w / h:.3f} fill={area / (w * h):.2f}')
