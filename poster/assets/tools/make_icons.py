"""Convert the paper's model-logo PDFs to tightly cropped SVGs and write the model-to-logo map.

Usage: python -I make_icons.py <asset/orgs dir> <out dir>
"""
import json
import os
import re
import sys

import numpy as np
import pymupdf

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
MODELS = {
    'DeepSeek-V4-Flash': 'deepseek',
    'Gemini-2.5-Flash-Lite': 'gemini',
    'Gemma-4-26B': 'gemma',
    'Granite-3.3-8B': 'ibm',
    'Llama-3-70B': 'meta',
    'Llama-4-Scout': 'meta',
    'GPT-5-mini': 'gpt',
    'Qwen-Turbo': 'qwen',
    'Grok-4.1-Fast': 'grok',
}
info = {}
for name in sorted(set(MODELS.values())):
    d = pymupdf.open(os.path.join(src, name + '.pdf'))
    p = d[0]
    imgs = [(i[2], i[3], i[8], i[1]) for i in p.get_images(full=True)]
    r = p.rect
    scale = 800 / max(r.width, r.height)
    pix = p.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=True)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    alpha = a[..., -1]
    rgb = a[..., :3].astype(int)
    ink = (alpha > 8) & (rgb.sum(axis=2) < 750)
    if not ink.any():
        ink = alpha > 8
    ys, xs = np.where(ink)
    k = 1 / scale
    pad = 0.5 * k
    x0, x1 = xs.min() * k + r.x0 - pad, (xs.max() + 1) * k + r.x0 + pad
    y0, y1 = ys.min() * k + r.y0 - pad, (ys.max() + 1) * k + r.y0 + pad
    svg = p.get_svg_image(text_as_path=True)

    def repl(m):
        tag = re.sub(r'\s(width|height|viewBox)="[^"]*"', '', m.group(0))
        return tag[:-1] + f' viewBox="{x0:.3f} {y0:.3f} {x1 - x0:.3f} {y1 - y0:.3f}">'
    svg = re.sub(r'<svg\b[^>]*>', repl, svg, count=1)
    path = os.path.join(out, name + '.svg')
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(svg)
    info[name] = {'page_pt': [round(r.width, 2), round(r.height, 2)], 'crop_pt': [round(x1 - x0, 2), round(y1 - y0, 2)],
                  'aspect': round((x1 - x0) / (y1 - y0), 3), 'embedded_images': imgs, 'svg_kb': os.path.getsize(path) // 1024,
                  'drawings': len(p.get_drawings())}
    print(name, info[name])
with open(os.path.join(out, 'model_icons.json'), 'w', encoding='utf-8', newline='\n') as f:
    json.dump({'models': MODELS, 'icons': info}, f, indent=1)
