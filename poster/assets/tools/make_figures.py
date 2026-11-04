"""Convert the paper's vector figure PDFs to tightly cropped SVGs with text as paths.

Usage: python -I make_figures.py <arxiv asset dir> <out dir>
Writes one SVG per figure, plus per-panel crops of the three-year strips, and figures.json with true aspect ratios.
"""
import json
import os
import re
import sys

import numpy as np
import pymupdf
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)

FIGS = {
    'fig1a_parties': 'teaser12_panelB_smallpdf-pages-2.pdf',
    'fig1b_llms': 'teaser12_panelB_smallpdf-pages-1.pdf',
    'polytope_3d': 'extended_teaser.pdf',
    'polytope_chrono_3d': 'extended_teaser_chrono.pdf',
    'polytope_chrono_2d': 'extended_teaser_chrono_2d.pdf',
    'pipeline': 'IdeoPlasticityLLM_pipeline2.pdf',
}
meta = {}


def ink_map(page, dpi=144):
    pix = page.get_pixmap(dpi=dpi, alpha=False, colorspace=pymupdf.csGRAY)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    return a < 250, 72 / dpi


def tight(mask, k, r, pad=1.5):
    ys, xs = np.where(mask)
    x0 = max(r.x0, xs.min() * k + r.x0 - pad)
    x1 = min(r.x1, (xs.max() + 1) * k + r.x0 + pad)
    y0 = max(r.y0, ys.min() * k + r.y0 - pad)
    y1 = min(r.y1, (ys.max() + 1) * k + r.y0 + pad)
    return x0, y0, x1, y1


def with_viewbox(svg, box):
    x0, y0, x1, y1 = box
    # Make the root scalable: drop fixed width and height, set the crop as viewBox, keep overflow hidden.
    def repl(m):
        tag = m.group(0)
        tag = re.sub(r'\s(width|height)="[^"]*"', '', tag)
        tag = re.sub(r'\sviewBox="[^"]*"', '', tag)
        return tag[:-1] + f' viewBox="{x0:.2f} {y0:.2f} {x1 - x0:.2f} {y1 - y0:.2f}">'
    return re.sub(r'<svg\b[^>]*>', repl, svg, count=1)


def save(name, svg, box, source):
    path = os.path.join(out, name + '.svg')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(with_viewbox(svg, box))
    w, h = box[2] - box[0], box[3] - box[1]
    meta[name] = {'source': source, 'width_pt': round(w, 2), 'height_pt': round(h, 2), 'aspect_w_over_h': round(w / h, 4), 'svg_kb': os.path.getsize(path) // 1024}
    print(f'{name}: {w:.1f} x {h:.1f} pt, aspect {w / h:.3f}, {os.path.getsize(path) // 1024} KB')


for name, pdf in FIGS.items():
    d = pymupdf.open(os.path.join(src, pdf))
    page = d[0]
    svg = page.get_svg_image(text_as_path=True)
    mask, k = ink_map(page)
    box = tight(mask, k, page.rect)
    save(name, svg, box, pdf)
    if name in ('polytope_chrono_3d', 'polytope_chrono_2d'):
        # Split the strip at its two widest empty vertical gaps
        cols = mask.any(axis=0)
        idx = np.where(~cols)[0]
        runs = np.split(idx, np.where(np.diff(idx) > 1)[0] + 1)
        first, last = np.where(cols)[0][[0, -1]]
        inner = [r for r in runs if len(r) and r[0] > first and r[-1] < last]
        inner.sort(key=len, reverse=True)
        cuts = sorted((int(r[0]) + int(r[-1])) // 2 for r in inner[:2])
        print('  panel gaps (px):', [(int(r[0]), int(r[-1])) for r in inner[:3]], 'cuts', cuts)
        edges = [0] + cuts + [mask.shape[1]]
        for i, year in enumerate((2009, 2014, 2019)):
            sub = np.zeros_like(mask)
            sub[:, edges[i]:edges[i + 1]] = mask[:, edges[i]:edges[i + 1]]
            if name == 'polytope_chrono_3d':
                # The bold year titles sit in the top rows: find the first empty row gap and start below it.
                rows = np.where(sub.any(axis=1))[0]
                gaps = np.split(rows, np.where(np.diff(rows) > 2)[0] + 1)
                sub[: gaps[1][0], :] = False if len(gaps) > 1 else sub[: gaps[1][0], :]
            b = tight(sub, k, page.rect)
            save(f'{name}_{year}', svg, b, pdf + f' panel {i + 1}')

with open(os.path.join(out, 'figures.json'), 'w', encoding='utf-8', newline='\n') as f:
    json.dump(meta, f, indent=1)
