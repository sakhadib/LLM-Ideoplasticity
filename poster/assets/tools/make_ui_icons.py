"""Make UI glyph SVGs from Font Awesome (the set the user's earlier posters use) and the official arXiv mark.

Usage: python -I make_ui_icons.py <site fonts dir> <arxiv.svg> <ui out dir>
"""
import os
import re
import sys

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

fonts, arxiv_svg, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)

GLYPHS = {
    'twitter': ('fa-brands-400.ttf', 0xF099),
    'github': ('fa-brands-400.ttf', 0xF09B),
    'envelope': ('fa-solid-900.ttf', 0xF0E0),
    'globe': ('fa-solid-900.ttf', 0xF0AC),
    'globe_asia': ('fa-solid-900.ttf', 0xF57E),  # \faGlobeAsia, for the project page
    'heart': ('fa-solid-900.ttf', 0xF004),
}
COLOURS = {'white': '#ffffff', 'ink': '#111827', 'purple': '#5445B5'}

for name, (fontfile, code) in GLYPHS.items():
    f = TTFont(os.path.join(fonts, fontfile))
    gs = f.getGlyphSet()
    gn = f.getBestCmap()[code]
    bp = BoundsPen(gs)
    gs[gn].draw(bp)
    x0, y0, x1, y1 = bp.bounds
    pen = SVGPathPen(gs, ntos=lambda v: f'{v:.1f}'.rstrip('0').rstrip('.'))
    gs[gn].draw(TransformPen(pen, (1, 0, 0, -1, -x0, y1)))
    d = pen.getCommands()
    w, h = x1 - x0, y1 - y0
    variants = {'red': '#E0202C'} if name == 'heart' else COLOURS
    for tag, col in variants.items():
        path = os.path.join(out, f'{name}_{tag}.svg')
        with open(path, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.1f} {h:.1f}"><!-- Font Awesome Free 5, CC BY 4.0, fontawesome.com --><path fill="{col}" d="{d}"/></svg>\n')
    print(name, 'aspect', round(w / h, 3))

# arXiv mark
s = open(arxiv_svg, encoding='utf-8').read()
assert '<script' not in s
print('arxiv fills', sorted(set(re.findall(r'fill[:=]"?\s*(#[0-9a-fA-F]{3,6})', s))), 'styles', re.findall(r'<style[^>]*>(.*?)</style>', s, re.S)[:1])
with open(os.path.join(out, 'arxiv_colour.svg'), 'w', encoding='utf-8', newline='\n') as fh:
    fh.write(s)
white = re.sub(r'#[0-9a-fA-F]{3,6}', '#ffffff', s)
if 'fill' not in white:
    white = white.replace('<path ', '<path fill="#ffffff" ')
with open(os.path.join(out, 'arxiv_white.svg'), 'w', encoding='utf-8', newline='\n') as fh:
    fh.write(white)
