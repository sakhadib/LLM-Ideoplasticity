"""Place every asset at its intended size on an A0 page, print it, and report weight, page size, fonts and images.
Also compares the AACL SVG with the v2 PNG.
"""
import json
import os
import pathlib
import sys

import numpy as np
import pymupdf
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from chrome import html_to_pdf, html_to_png  # noqa: E402

assets, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)


def u(*p):
    return pathlib.Path(assets, *p).resolve().as_uri()


meta = json.load(open(os.path.join(assets, 'icons', 'model_icons.json'), encoding='utf-8'))
icons = ''.join(f'<img src="{u("icons", f)}" style="height:9mm;margin:2mm">' * 3 for f in meta['files'].values())
figs = [('fig1a_parties', 257), ('fig1b_llms', 257), ('polytope_3d', 200), ('polytope_chrono_2d_2009', 110), ('polytope_chrono_2d_2014', 110), ('polytope_chrono_2d_2019', 110),
        ('polytope_chrono_3d_2009', 110), ('polytope_chrono_3d_2014', 110), ('polytope_chrono_3d_2019', 110), ('pipeline', 170)]
imgs = ''.join(f'<img src="{u("figures", n + ".svg")}" style="width:{w}mm;margin:3mm;vertical-align:top">' for n, w in figs)
ui = ''.join(f'<img src="{u("icons", "ui", n + ".svg")}" style="height:8mm;margin:2mm">' for n in ('twitter_white', 'envelope_white', 'github_white', 'globe_white', 'arxiv_white', 'heart_red'))
html = f'''<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{u("fonts", "fonts.css")}"><style>
@page {{ size: 841mm 1189mm; margin:0 }} html,body {{ margin:0; background:#fff; color:#111827 }}
.band {{ background:#5445B5; color:#fff; height:130mm; padding:8mm 20mm; box-sizing:border-box }}
.t {{ font:600 115pt 'Fraunces Poster' }} .s {{ font:500 54pt 'Fraunces Poster Mid' }} .b {{ font:400 27pt/36pt 'Pagella Poster'; padding:0 20mm }} .m {{ font:500 20pt 'JetBrains Mono Poster'; padding:0 20mm }}
.h {{ font:600 50pt 'Fraunces Poster Text'; padding:0 20mm }} .bn {{ font:400 27pt 'Bangla Poster'; padding:0 20mm }} .bi {{ font-style:italic }}
</style></head><body>
<div class="band"><img src="{u("logos", "iut_lockup_white.svg")}" style="width:190mm"> <img src="{u("logos", "project_logo_band.png")}" style="height:30mm"> <img src="{u("qr", "qr_card_white.svg")}" style="width:95mm;float:right"> {ui}
<div style="background:#fff;border-radius:4mm;padding:4mm;width:190mm;margin-top:4mm"><img src="{u("logos", "aacl_2026_logo.svg")}" style="width:180mm"></div></div>
<div class="t">LLM-Ideoplasticity</div><div class="s">Measuring Ideological Plasticity <i>as a shape</i></div><div class="h">3 Local Plasticity</div>
<div class="b">Body text in Pagella <i>italic</i> <b>bold</b> <b class="bi">both</b>.</div><div class="m">0.1829 0.2813</div><div class="bn">সোশ্যাল ওয়েলফেয়ার</div>
<div style="padding:0 17mm">{imgs}</div><div style="padding:0 17mm">{icons}</div>
</body></html>'''
hp = os.path.join(out, 'weight.html')
open(hp, 'w', encoding='utf-8', newline='\n').write(html)
pdf = os.path.join(out, 'weight.pdf')
print('console', html_to_pdf(hp, pdf, 841, 1189))
d = pymupdf.open(pdf)
p = d[0]
print('pages', len(d), 'page size pt', round(p.rect.width, 2), round(p.rect.height, 2), '| mm', round(p.rect.width * 0.35278, 2), round(p.rect.height * 0.35278, 2))
print('PDF size', round(os.path.getsize(pdf) / 1048576, 2), 'MB')
print('fonts', sorted(set((f[3].split('+')[-1], f[2]) for f in p.get_fonts(full=True))))
big = sorted(((i[2], i[3], i[8]) for i in p.get_images(full=True)), key=lambda x: -x[0] * x[1])[:8]
print('images', len(p.get_images()), 'largest', big)
p.get_pixmap(dpi=24, alpha=False).save(os.path.join(out, 'weight.png'))

# AACL SVG vs v2 PNG, at the PNG's size
svg_uri = u('logos', 'aacl_2026_logo.svg')
hp2 = os.path.join(out, 'aacl.html')
open(hp2, 'w', encoding='utf-8', newline='\n').write(f'<!doctype html><html><body style="margin:0;background:#fff"><img src="{svg_uri}" style="width:1200px;display:block"></body></html>')
html_to_png(hp2, os.path.join(out, 'aacl_svg_1200.png'), 1200, 291)
a = np.asarray(Image.open(os.path.join(out, 'aacl_svg_1200.png')).convert('RGB')).astype(int)
png = Image.open(os.path.join(assets, 'logos', 'aacl_2026_logo_v2.png')).convert('RGBA')
bg = Image.new('RGBA', png.size, (255, 255, 255, 255))
bg.alpha_composite(png)
b = np.asarray(bg.convert('RGB')).astype(int)
hh, ww = min(a.shape[0], b.shape[0]), min(a.shape[1], b.shape[1])
diff = np.abs(a[:hh, :ww] - b[:hh, :ww]).sum(axis=2)
print('AACL svg vs v2 png: shapes', a.shape, b.shape, 'mean diff', round(float(diff.mean()), 2), 'frac>150', round(float((diff > 150).mean()), 4))
