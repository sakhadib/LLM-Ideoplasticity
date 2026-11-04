"""Re-set the IUT wordmark as crisp outlines (EB Garamond 400), glyph-aligned to the reference lockup,
then recompose the lockup SVG. The soft trace is kept as iut_wordmark_trace.svg.

Usage: python build_wordmark.py <EBGaramond.ttf> <fit_best.json> <ref_lockup.png> <pylibs> <logos_dir>
"""
import json
import os
import re
import statistics
import sys

import numpy as np
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from PIL import Image
from scipy import ndimage

font_path, fit_json, ref_png, pylibs, logos = sys.argv[1:6]
sys.path.append(pylibs)
import potrace  # noqa: E402


def fmt(v):
    s = f'{v:.2f}'.rstrip('0').rstrip('.')
    return s if s not in ('', '-0') else '0'


fit = json.load(open(fit_json, encoding='utf-8'))
vf = TTFont(font_path)
inst = instancer.instantiateVariableFont(vf, {'wght': 400})
gs = inst.getGlyphSet()
cmap = inst.getBestCmap()
upem = inst['head'].unitsPerEm

FLAT = set('ILAMNERTYFHK')
paths = []
for text, info in fit['placements'].items():
    size = info['size']
    scale = size / upem
    baseline = statistics.median(y + gh for ch, x, y, gw, gh in info['pos'] if ch in FLAT)
    print(text, 'size', round(size, 1), 'baseline', baseline)
    for ch, x, y, gw, gh in info['pos']:
        gn = cmap[ord(ch)]
        bp = BoundsPen(gs)
        gs[gn].draw(bp)
        xmin, ymin, xmax, ymax = bp.bounds
        # Centre the outline's ink on the matched ink box.
        tx = x + gw / 2 - (xmin + xmax) / 2 * scale
        pen = SVGPathPen(gs, ntos=fmt)
        gs[gn].draw(TransformPen(pen, (scale, 0, 0, -scale, tx, baseline)))
        paths.append(pen.getCommands())
word_d = ''.join(paths)

ref = Image.open(ref_png).convert('RGBA')
alpha = np.asarray(ref.split()[3]).astype(float) / 255
H, W = alpha.shape
SPLIT = 234


def write_svg(path, vb, body, comment):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{fmt(vb[0])} {fmt(vb[1])} {fmt(vb[2])} {fmt(vb[3])}">\n')
        f.write(f'<!-- {comment} -->\n')
        f.write(body)
        f.write('\n</svg>\n')
    print('wrote', path, os.path.getsize(path))


# Keep a smoothed trace as the strict-fidelity alternative.
UP = 6
word_alpha = alpha.copy()
word_alpha[:, :SPLIT] = 0
big = np.asarray(Image.fromarray((word_alpha * 255).astype(np.uint8)).resize((W * UP, H * UP), Image.BICUBIC)).astype(float) / 255
big = ndimage.gaussian_filter(big, sigma=1.2 * UP)
pl = potrace.Bitmap(~(big >= 0.5)).trace(turdsize=60, turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY, alphamax=1.0, opticurve=True, opttolerance=1.5)
parts = []


def P(p):
    return f'{fmt(p.x / UP)} {fmt(p.y / UP)}'


for c in pl:
    parts.append('M' + P(c.start_point))
    for s in c.segments:
        if s.is_corner:
            parts.append('L' + P(s.c) + 'L' + P(s.end_point))
        else:
            parts.append('C' + P(s.c1) + ' ' + P(s.c2) + ' ' + P(s.end_point))
    parts.append('Z')
trace_d = ''.join(parts)
write_svg(os.path.join(logos, 'iut_wordmark_trace.svg'), (SPLIT, 0, W - SPLIT, H),
          f'<path fill="#ffffff" fill-rule="evenodd" d="{trace_d}"/>',
          'Wordmark traced directly from the lockup raster on the earlier posters: exact letterforms, softer edges. Alternative only.')
write_svg(os.path.join(logos, 'iut_wordmark_white.svg'), (SPLIT, 0, W - SPLIT, H),
          f'<path fill="#ffffff" d="{word_d}"/>',
          'ISLAMIC UNIVERSITY OF TECHNOLOGY outlines: EB Garamond 400, glyph positions matched to the lockup on the earlier posters.')

# Recompose the lockup: reuse the emblem group from the first build.
old = open(os.path.join(logos, 'iut_lockup_white.svg'), encoding='utf-8').read()
m = re.search(r'<g transform=.*?</g>', old, re.S)
emblem_group = m.group(0)
write_svg(os.path.join(logos, 'iut_lockup_white.svg'), (0, 0, W, H),
          emblem_group + f'\n<path fill="#ffffff" d="{word_d}"/>',
          'IUT lockup for coloured grounds. Emblem: official vector paths from the IUT letterhead over a white backing. Wordmark: EB Garamond 400 outlines placed to match the lockup on the earlier posters.')
