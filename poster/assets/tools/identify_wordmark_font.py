"""Identify the wordmark's typeface by rendering each line in every candidate font and scoring overlap (IoU)."""
import glob
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ref_png, out, extra = sys.argv[1], sys.argv[2], sys.argv[3:]
os.makedirs(out, exist_ok=True)
alpha = np.asarray(Image.open(ref_png).convert('RGBA').split()[3]) > 127
SPLIT = 234
word = alpha.copy()
word[:, :SPLIT] = False
rows = word.any(axis=1)
idx = np.where(rows)[0]
runs = np.split(idx, np.where(np.diff(idx) > 3)[0] + 1)
print('rows', [(r[0], r[-1]) for r in runs])
lines = []
for r, text in zip(runs, ('ISLAMIC UNIVERSITY', 'OF TECHNOLOGY')):
    sub = word[r[0]:r[-1] + 1]
    cols = np.where(sub.any(axis=0))[0]
    crop = sub[:, cols[0]:cols[-1] + 1]
    lines.append((text, crop, (cols[0], r[0], cols[-1] + 1, r[-1] + 1)))
    print(text, 'bbox', lines[-1][2], crop.shape)


def score(path):
    total = 0.0
    for text, crop, _ in lines:
        h, w = crop.shape
        try:
            font = ImageFont.truetype(path, 400)
        except Exception:
            return None
        # Render large, crop to ink, and fit the reference bbox.
        img = Image.new('L', (9000, 800), 0)
        d = ImageDraw.Draw(img)
        try:
            d.text((100, 100), text, font=font, fill=255)
        except OSError:
            return None
        box = img.getbbox()
        if not box:
            return None
        ink = img.crop(box)
        aspect_ref = w / h
        aspect = ink.width / ink.height
        fitted = np.asarray(ink.resize((w, h), Image.BICUBIC)) > 127
        iou = (fitted & crop).sum() / max((fitted | crop).sum(), 1)
        # Penalise strongly different aspect ratio (it means tracking would have to change a lot).
        total += iou - 0.15 * abs(np.log(aspect / aspect_ref))
    return total / len(lines)


cands = sorted(set(glob.glob(r'C:\Windows\Fonts\*.ttf') + glob.glob(r'C:\Windows\Fonts\*.TTF') + glob.glob(r'C:\Windows\Fonts\*.otf') + extra))
res = []
for p in cands:
    s = score(p)
    if s is not None:
        res.append((s, os.path.basename(p), p))
res.sort(reverse=True)
for s, n, _ in res[:15]:
    print(f'{s:.3f} {n}')

# Contact sheet of the top 6 against the reference
top = res[:6]
rowh = 150
sheet = Image.new('L', (1600, rowh * (len(top) + 1)), 255)
crop = lines[1][1]
ref_img = Image.fromarray((~crop * 255).astype(np.uint8)).resize((1000, 120))
sheet.paste(ref_img, (0, 10))
for i, (s, n, p) in enumerate(top):
    f = ImageFont.truetype(p, 400)
    img = Image.new('L', (9000, 800), 255)
    ImageDraw.Draw(img).text((100, 100), lines[1][0], font=f, fill=0)
    box = Image.eval(img, lambda v: 255 - v).getbbox()
    ink = img.crop(box).resize((1000, 120), Image.LANCZOS)
    sheet.paste(ink, (0, rowh * (i + 1) + 10))
    ImageDraw.Draw(sheet).text((1020, rowh * (i + 1) + 50), f'{n} {s:.3f}', fill=0, font=ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 26))
sheet.save(os.path.join(out, 'font_candidates.png'))
