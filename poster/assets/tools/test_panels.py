"""Contact sheet of per-panel crops, printed via Chrome, to check crops and clipping."""
import os
import pathlib
import sys

import pymupdf

sys.path.insert(0, os.path.dirname(__file__))
from chrome import html_to_pdf  # noqa: E402

figs, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
names = [f'polytope_chrono_2d_{y}' for y in (2009, 2014, 2019)] + [f'polytope_chrono_3d_{y}' for y in (2009, 2014, 2019)]
imgs = ''.join(f'<img src="{pathlib.Path(figs, n + ".svg").resolve().as_uri()}" style="width:105mm;margin:4mm;outline:0.2mm dashed #bbb;vertical-align:top">' for n in names)
html = f'<!doctype html><html><head><style>@page {{ size:360mm 240mm; margin:0 }} html,body {{ margin:0;background:#fff }}</style></head><body>{imgs}</body></html>'
hp = os.path.join(out, 'panels.html')
open(hp, 'w', encoding='utf-8', newline='\n').write(html)
pdf = os.path.join(out, 'panels.pdf')
print(html_to_pdf(hp, pdf, 360, 240))
d = pymupdf.open(pdf)
print('pages', len(d), 'KB', os.path.getsize(pdf) // 1024, 'images', len(d[0].get_images()))
d[0].get_pixmap(dpi=75, alpha=False).save(os.path.join(out, 'panels.png'))
