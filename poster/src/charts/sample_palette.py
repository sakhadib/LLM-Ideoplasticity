"""Sample exact colours from the paper's vector figures and the project logo.

Usage (reads downloaded material, so run isolated and pass paths as arguments):
    python -I poster/src/charts/sample_palette.py <arxiv_asset_dir> <logo_png> <out_json>
"""
import collections
import json
import sys

import pymupdf
from PIL import Image


def hexcol(rgb):
    return '#%02X%02X%02X' % tuple(int(round(v * 255)) for v in rgb[:3])


def blend(rgb, a):
    return tuple(v * a + (1 - a) for v in rgb[:3])


asset, logo_path, out = sys.argv[1:4]
res = {}

# 1) Compass quadrant fills from ow.pdf
doc = pymupdf.open(asset + '/ideoPlots/ow.pdf')
page = doc[0]
fills = collections.Counter()
detail = {}
for g in page.get_drawings():
    f = g.get('fill')
    if f is None:
        continue
    op = g.get('fill_opacity', 1) or 1
    r = g['rect']
    key = (hexcol(f), round(op, 3))
    fills[key] += r.width * r.height
    detail.setdefault(key, []).append(tuple(round(v, 1) for v in r))
print(fills.most_common(12))
# Pixel-sample the first axes panel corners, well away from hulls.
pix = page.get_pixmap(dpi=300, alpha=False)
img = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
scale = 300 / 72
for key, rects in detail.items():
    pass
# Find the first-panel big quadrants: rectangles of similar size at the top-left of the page.
big = sorted(((k, r) for k, rs in detail.items() for r in rs if (r[2] - r[0]) > 60 and (r[3] - r[1]) > 40 and (r[2] - r[0]) < 150),
             key=lambda kr: (round(kr[1][1] / 40), kr[1][0]))
print(big[:6])
quadrants = {}
for k, r in big[:4]:
    cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2
    quadrants[(round(cx), round(cy))] = {'pdf_fill': k[0], 'opacity': k[1]}
res['ow_big_rects'] = [{'fill': k[0], 'opacity': k[1], 'rect': r} for k, r in big[:4]]
# Sample rendered pixels near outer corners of the first panel's four quadrants.
xs = [r[0] for k, r in big[:4]] + [r[2] for k, r in big[:4]]
ys = [r[1] for k, r in big[:4]] + [r[3] for k, r in big[:4]]
x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
sample = {
    'auth_left': (x0 + 3, y0 + 3 + 14),
    'auth_right': (x1 - 3, y0 + 3 + 14),
    'lib_left': (x0 + 3, y1 - 3),
    'lib_right': (x1 - 3, y1 - 3),
}
res['quadrants_rendered'] = {}
for name, (x, y) in sample.items():
    px = img.getpixel((int(x * scale), int(y * scale)))
    res['quadrants_rendered'][name] = '#%02X%02X%02X' % px
print(res['quadrants_rendered'], (x0, y0, x1, y1))
doc.close()

# 2) MTMM colour ramp: the colourbar image, top (+1) to bottom (-1)
doc = pymupdf.open(asset + '/MTMM_3.pdf')
page = doc[0]
imgs = page.get_images(full=True)
base = doc.extract_image(imgs[0][0])
pm = pymupdf.Pixmap(doc, imgs[0][0])
if pm.alpha or pm.n > 3:
    pm = pymupdf.Pixmap(pymupdf.csRGB, pm)
w, h = pm.width, pm.height
stops = []
n = 41
for i in range(n):
    y = int(round(i / (n - 1) * (h - 1)))
    p = pm.pixel(w // 2, y)
    stops.append({'value': round(1 - 2 * i / (n - 1), 3), 'color': '#%02X%02X%02X' % tuple(p[:3])})
res['mtmm_ramp'] = stops
print(stops[0], stops[n // 2], stops[-1], (w, h))
# Heatmap cell fill as a cross-check: known cell values vs drawn fills.
cells = collections.Counter()
for g in page.get_drawings():
    f = g.get('fill')
    if f is not None and g['rect'].width > 20:
        cells[hexcol(f)] += 1
res['mtmm_cell_fills'] = list(cells.keys())[:60]
print(len(cells))
doc.close()

# 3) Logo: contour colours along a horizontal scan through the mark, plus ink
im = Image.open(logo_path).convert('RGBA')
W, H = im.size
print('logo', W, H)
counts = collections.Counter()
for y in range(0, H, 2):
    for x in range(0, W, 2):
        r, g, b, a = im.getpixel((x, y))
        if a > 250:
            counts[(r // 4 * 4, g // 4 * 4, b // 4 * 4)] += 1
res['logo_top_colors'] = ['#%02X%02X%02X' % c for c, _ in counts.most_common(24)]
# Scan row through the central dot; report run colours that are strongly saturated
row = int(H * 358 / 860)
runs = []
last = None
for x in range(W):
    r, g, b, a = im.getpixel((x, row))
    key = '#%02X%02X%02X' % (r, g, b) if a > 200 else None
    if key != last:
        runs.append((x, key))
        last = key
res['logo_scan_row'] = runs[:80]
for n_, c in zip(range(24), res['logo_top_colors']):
    pass
print(res['logo_top_colors'])

with open(out, 'w', encoding='utf-8', newline='\n') as f:
    json.dump(res, f, indent=1)
print('wrote', out)
