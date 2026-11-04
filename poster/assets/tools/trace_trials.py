"""Compare wordmark traces at different smoothing levels: render each at print-like zoom beside the source."""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

ref_png, pylibs, out = sys.argv[1:4]
sys.path.append(pylibs)
sys.path.insert(0, os.path.dirname(__file__))
import potrace  # noqa: E402
from chrome import html_to_png  # noqa: E402

os.makedirs(out, exist_ok=True)
alpha = np.asarray(Image.open(ref_png).convert('RGBA').split()[3]).astype(float) / 255
H, W = alpha.shape
SPLIT = 234
alpha = alpha.copy()
alpha[:, :SPLIT] = 0
UP = 6


def fmt(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.')


def run(sigma_src, alphamax, opttol):
    big = np.asarray(Image.fromarray((alpha * 255).astype(np.uint8)).resize((W * UP, H * UP), Image.BICUBIC)).astype(float) / 255
    big = ndimage.gaussian_filter(big, sigma=sigma_src * UP)
    pl = potrace.Bitmap(~(big >= 0.5)).trace(turdsize=60, turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY, alphamax=alphamax, opticurve=True, opttolerance=opttol)
    parts = []
    def P(p):
        return f'{fmt(p.x / UP)} {fmt(p.y / UP)}'
    nseg = 0
    for c in pl:
        parts.append('M' + P(c.start_point))
        for s in c.segments:
            nseg += 1
            if s.is_corner:
                parts.append('L' + P(s.c) + 'L' + P(s.end_point))
            else:
                parts.append('C' + P(s.c1) + ' ' + P(s.c2) + ' ' + P(s.end_point))
        parts.append('Z')
    return ''.join(parts), nseg


rows = []
for sig, am, ot in ((0.5, 1.0, 0.4), (0.9, 1.0, 1.0), (1.2, 1.0, 1.5), (1.2, 0.85, 1.5)):
    d, n = run(sig, am, ot)
    print('sigma', sig, 'alphamax', am, 'opttol', ot, 'segments', n, 'bytes', len(d))
    rows.append((sig, am, ot, d))

svgs = ''.join(
    f'<div style="margin:8px 0;color:#fff;font:14px sans-serif">sigma={s} alphamax={a} opttol={o}</div>'
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="234 0 760 324" style="width:1900px;height:810px;display:block"><path fill="#fff" fill-rule="evenodd" d="{d}"/></svg>'
    for s, a, o, d in rows)
html = f'<!doctype html><html><body style="margin:0;background:#5445B5">{svgs}</body></html>'
hp = os.path.join(out, 'trials.html')
open(hp, 'w', encoding='utf-8', newline='\n').write(html)
html_to_png(hp, os.path.join(out, 'trials.png'), 1900, 3400)
img = Image.open(os.path.join(out, 'trials.png'))
for i in range(4):
    img.crop((0, i * 842, 1900, (i + 1) * 842)).save(os.path.join(out, f'trial_{i}.png'))
