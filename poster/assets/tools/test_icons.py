"""Print the model logos beside their names at poster text size; report embedded images; render for inspection."""
import json
import os
import pathlib
import sys

import pymupdf

sys.path.insert(0, os.path.dirname(__file__))
from chrome import html_to_pdf  # noqa: E402

icons, fonts_css, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
meta = json.load(open(os.path.join(icons, 'model_icons.json'), encoding='utf-8'))
css = pathlib.Path(fonts_css).resolve().as_uri()
rows = ''
for model, fname in meta['files'].items():
    uri = pathlib.Path(icons, fname).resolve().as_uri()
    rows += f'<div class="r"><img src="{uri}" style="height:0.95em;vertical-align:-0.13em;margin-right:0.35em">{model}</div>'
    rows += f'<div class="big"><img src="{uri}" style="height:30mm"></div>'
html = f'''<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{css}"><style>
@page {{ size: 330mm 250mm; margin:0 }} html,body {{ margin:0;background:#fff;color:#111827 }}
.g {{ display:grid; grid-template-columns: 110mm 40mm 110mm 40mm; padding:8mm; align-items:center; row-gap:3mm }}
.r {{ font:400 27pt/1.2 'Pagella Poster' }}
</style></head><body><div class="g">{rows}</div></body></html>'''
hp = os.path.join(out, 'icons.html')
open(hp, 'w', encoding='utf-8', newline='\n').write(html)
pdf = os.path.join(out, 'icons.pdf')
print(html_to_pdf(hp, pdf, 330, 250))
d = pymupdf.open(pdf)
print('pages', len(d), 'KB', os.path.getsize(pdf) // 1024, 'images', [(i[2], i[3], i[8]) for i in d[0].get_images(full=True)])
d[0].get_pixmap(dpi=90, alpha=False).save(os.path.join(out, 'icons.png'))
