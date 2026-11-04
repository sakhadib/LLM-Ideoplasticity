"""Replace the problem model logos with clean RGBA PNGs and update model_icons.json.

gemma, qwen: the paper's PDFs hold rasters with a soft mask; the SVG conversion shows stray edge lines (gemma).
meta, gemini: gradient meshes that convert to many tiny raster patches with faint seams at large sizes.
Usage: python -I make_raster_icons.py <asset/orgs dir> <icons dir>
"""
import io
import json
import os
import sys

import numpy as np
import pymupdf
from PIL import Image, ImageDraw

src, icons = sys.argv[1], sys.argv[2]
meta = json.load(open(os.path.join(icons, 'model_icons.json'), encoding='utf-8'))


def from_pdf_image(name, size=384):
    d = pymupdf.open(os.path.join(src, name + '.pdf'))
    p = d[0]
    im = p.get_images(full=True)[0]
    rgb = Image.open(io.BytesIO(d.extract_image(im[0])['image'])).convert('RGB')
    mask = Image.open(io.BytesIO(d.extract_image(im[1])['image'])).convert('L')
    if mask.size != rgb.size:
        mask = mask.resize(rgb.size, Image.LANCZOS)
    rgba = rgb.copy()
    rgba.putalpha(mask)
    arr = np.asarray(mask)
    # Ignore a thin frame of stray alpha along the image edges when finding the logo's box.
    inner = arr.copy()
    m = max(4, int(0.004 * max(arr.shape)))
    inner[:m] = 0
    inner[-m:] = 0
    inner[:, :m] = 0
    inner[:, -m:] = 0
    ys, xs = np.where(inner > 24)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    return rgba, box


def save_png(im, name, target=384):
    w, h = im.size
    k = target / max(w, h)
    im = im.resize((max(1, round(w * k)), max(1, round(h * k))), Image.LANCZOS)
    path = os.path.join(icons, name + '.png')
    im.save(path, optimize=True)
    print(name, 'png', im.size, os.path.getsize(path) // 1024, 'KB')
    return im.size


sizes = {}
# Gemma: a circle. Recompose alpha with an exact circle so no stray frame can survive.
rgba, box = from_pdf_image('gemma')
c = rgba.crop(box)
w, h = c.size
side = max(w, h)
sq = Image.new('RGBA', (side, side), (0, 0, 0, 0))
sq.paste(c, ((side - w) // 2, (side - h) // 2))
SS = 4
circle = Image.new('L', (side * SS, side * SS), 0)
ImageDraw.Draw(circle).ellipse((0, 0, side * SS - 1, side * SS - 1), fill=255)
circle = circle.resize((side, side), Image.LANCZOS)
sq.putalpha(Image.fromarray(np.minimum(np.asarray(sq.getchannel('A')), np.asarray(circle))))
sizes['gemma'] = save_png(sq, 'gemma')

# Qwen: the mask covers the whole page, so find the logo by colour and make its near-white surround transparent.
rgba, _ = from_pdf_image('qwen')
arr = np.asarray(rgba).astype(float)
whiteness = arr[..., :3].min(axis=2)
print('qwen mask range', arr[..., 3].min(), arr[..., 3].max(), 'near-white frac', round(float((whiteness > 245).mean()), 3))
ink = (arr[..., 3] > 24) & (whiteness < 235)
ys, xs = np.where(ink)
box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
alpha = np.clip((250 - whiteness) / 30, 0, 1) * arr[..., 3]
out_arr = arr.copy()
out_arr[..., 3] = alpha
sizes['qwen'] = save_png(Image.fromarray(out_arr.astype(np.uint8), 'RGBA').crop(box), 'qwen')

# Meta and Gemini: render the source PDF directly with alpha.
for name in ('meta', 'gemini'):
    d = pymupdf.open(os.path.join(src, name + '.pdf'))
    p = d[0]
    z = 1600 / max(p.rect.width, p.rect.height)
    pix = p.get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=True)
    im = Image.frombytes('RGBA', (pix.width, pix.height), pix.samples)
    a = np.asarray(im.getchannel('A'))
    ys, xs = np.where(a > 8)
    sizes[name] = save_png(im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)), name, target=512)

files = {}
for model, ic in meta['models'].items():
    files[model] = ic + ('.png' if ic in sizes else '.svg')
meta['files'] = files
for ic, s in sizes.items():
    meta['icons'][ic]['png_px'] = list(s)
    meta['icons'][ic]['aspect'] = round(s[0] / s[1], 3)
    svg = os.path.join(icons, ic + '.svg')
    if os.path.exists(svg):
        os.remove(svg)
with open(os.path.join(icons, 'model_icons.json'), 'w', encoding='utf-8', newline='\n') as f:
    json.dump(meta, f, indent=1)
print(files)
