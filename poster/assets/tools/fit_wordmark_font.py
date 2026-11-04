"""Fit candidate fonts to the reference wordmark glyph by glyph and report overlap (IoU).

For each glyph: render it at the reference's cap height, then slide it to the x position of best overlap.
Usage: python fit_wordmark_font.py <ref_lockup.png> <out_dir> <font[:wght]> ...
"""
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ref_png, out, cands = sys.argv[1], sys.argv[2], sys.argv[3:]
os.makedirs(out, exist_ok=True)
alpha = np.asarray(Image.open(ref_png).convert('RGBA').split()[3]) > 127
SPLIT = 234
word = alpha.copy()
word[:, :SPLIT] = False
LINES = [('ISLAMIC UNIVERSITY', 0, 150), ('OF TECHNOLOGY', 150, alpha.shape[0])]


def font_for(path, wght, size):
    f = ImageFont.truetype(path, size)
    if wght:
        f.set_variation_by_axes([wght])
    return f


def glyph_mask(path, wght, size, ch):
    f = font_for(path, wght, size)
    img = Image.new('L', (int(size * 2.2), int(size * 2.2)), 0)
    d = ImageDraw.Draw(img)
    d.text((int(size * 0.4), int(size * 0.2)), ch, font=f, fill=255, anchor='ls' if False else None)
    arr = np.asarray(img) > 127
    ys, xs = np.where(arr)
    return arr[ys.min():ys.max() + 1, xs.min():xs.max() + 1], (xs.min(), ys.min())


results = []
for spec in cands:
    path, _, w = spec.partition('::')
    wght = float(w) if w else None
    fit_total_i = 0
    fit_total_u = 0
    placements = {}
    canvas = np.zeros_like(word)
    for text, y0, y1 in LINES:
        band = word[y0:y1]
        rows = np.where(band.any(axis=1))[0]
        top, bot = rows.min(), rows.max() + 1
        # Measure cap height with a flat glyph on the reference: first letter column run for the top line, 'F' etc.
        # Search size so that the rendered 'T' matches: use line ink height minus overshoot.
        ink_h = bot - top
        best = None
        for size_factor in np.linspace(0.9, 1.1, 11):
            # Size from the font's H height
            base = 400
            hm, _ = glyph_mask(path, wght, base, 'H')
            size = base * (ink_h * 0.94 * size_factor) / hm.shape[0]
            x_cursor = 0
            inter = 0
            union_mask = np.zeros_like(band)
            ok = True
            pos = []
            cols = np.where(band.any(axis=0))[0]
            xstart, xend = cols.min(), cols.max() + 1
            f = font_for(path, wght, size)
            total_adv = sum(f.getlength(c) for c in text)
            xscale = (xend - xstart) / total_adv
            x_exp = xstart
            for ch in text:
                adv = f.getlength(ch)
                if ch == ' ':
                    x_exp += adv * xscale
                    continue
                gm, (gx, gy) = glyph_mask(path, wght, size, ch)
                gh, gw = gm.shape
                bestx = None
                # vertical placement: flat letters sit on the baseline; search a few rows
                for dy in range(-3, 4):
                    yy = bot - gh + dy
                    if ch in 'SCGOU':
                        yy = bot - gh + dy
                    if ch in 'QJ':
                        yy = top + dy
                    if yy < 0 or yy + gh > band.shape[0]:
                        continue
                    for xx in range(int(x_exp) - 45, int(x_exp) + 45):
                        if xx < 0 or xx + gw > band.shape[1]:
                            continue
                        win = band[yy:yy + gh, xx:xx + gw]
                        score = (win & gm).sum() - 0.6 * ((~win) & gm).sum()
                        if bestx is None or score > bestx[0]:
                            bestx = (score, xx, yy)
                if bestx is None:
                    ok = False
                    break
                _, xx, yy = bestx
                union_mask[yy:yy + gh, xx:xx + gw] |= gm
                pos.append((ch, int(xx), int(yy + y0), int(gw), int(gh)))
                x_exp = xx + adv * xscale * 0.98
            if not ok:
                continue
            i = (union_mask & band).sum()
            u = (union_mask | band).sum()
            iou = i / max(u, 1)
            if best is None or iou > best[0]:
                best = (iou, size, pos, union_mask.copy(), i, u)
        fit_total_i += best[4]
        fit_total_u += best[5]
        placements[text] = {'size': float(best[1]), 'iou': float(best[0]), 'pos': best[2]}
        canvas[y0:y1] |= best[3]
    iou = fit_total_i / fit_total_u
    print(f'{iou:.3f}  {os.path.basename(path)} wght={wght}  ' + '  '.join(f'{k[:8]}={v["iou"]:.3f}@{v["size"]:.0f}' for k, v in placements.items()))
    results.append((iou, spec, placements))
    # overlay image: red = reference only, blue = font only, white = both
    H, W = word.shape
    rgb = np.zeros((H, W, 3), dtype=np.uint8)
    rgb[word & canvas] = (255, 255, 255)
    rgb[word & ~canvas] = (255, 60, 60)
    rgb[~word & canvas] = (60, 160, 255)
    name = os.path.basename(path).split('.')[0] + (f'_{int(wght)}' if wght else '')
    Image.fromarray(rgb).crop((SPLIT, 0, W, H)).save(os.path.join(out, f'fit_{name}.png'))

results.sort(key=lambda r: -r[0])
print('best', results[0][0], results[0][1])
with open(os.path.join(out, 'fit_best.json'), 'w', encoding='utf-8', newline='\n') as f:
    json.dump({'spec': results[0][1], 'iou': results[0][0], 'placements': results[0][2]}, f, indent=1)
