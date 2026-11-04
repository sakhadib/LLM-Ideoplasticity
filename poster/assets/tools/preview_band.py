"""Assets-in-context check: lockup, AACL plate, project logo, QR cards, UI glyphs on the #5445B5 band at real print size."""
import os
import pathlib
import sys

import pymupdf

sys.path.insert(0, os.path.dirname(__file__))
from chrome import html_to_pdf  # noqa: E402

assets, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)


def u(*p):
    return pathlib.Path(assets, *p).resolve().as_uri()


html = f'''<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{u('fonts', 'fonts.css')}"><style>
@page {{ size: 841mm 260mm; margin:0 }}
html,body {{ margin:0; background:#fff; }}
.band {{ background:#5445B5; color:#fff; height:132mm; position:relative; }}
.lock {{ position:absolute; left:18mm; top:12mm; width:190mm; }}
.plate {{ position:absolute; left:18mm; top:62mm; width:190mm; height:56mm; background:#fff; border-radius:4mm; display:flex; align-items:center; justify-content:center; }}
.plate img {{ width:174mm; }}
.t {{ position:absolute; left:225mm; right:125mm; top:12mm; text-align:center; font:600 88pt/1.05 'Fraunces Poster'; }}
.t img {{ height:26mm; vertical-align:-3mm; margin-right:3mm; }}
.s {{ font:500 46pt/1.12 'Fraunces Poster Mid'; margin-top:2mm; }}
.icons {{ font:400 26pt/1 'Pagella Poster'; margin-top:6mm; }}
.icons img {{ height:7mm; vertical-align:-1mm; margin:0 1.5mm 0 6mm; }}
.qr {{ position:absolute; right:20mm; top:10mm; width:96mm; }}
.foot {{ background:#5445B5; color:#fff; height:24mm; margin-top:6mm; display:flex; align-items:center; justify-content:space-between; padding:0 18mm; font:400 27pt 'Pagella Poster'; }}
.foot img {{ height:7mm; vertical-align:-1mm; margin:0 1.5mm; }}
.alt {{ display:flex; gap:12mm; padding:8mm 18mm; align-items:flex-start; }}
.alt img {{ height:70mm; }}
</style></head><body>
<div class="band">
  <img class="lock" src="{u('logos', 'iut_lockup_white.svg')}">
  <div class="plate"><img src="{u('logos', 'aacl_2026_logo.svg')}"></div>
  <div class="t"><img src="{u('logos', 'project_logo_band.png')}">LLM-Ideoplasticity:
    <div class="s">Measuring Ideological Plasticity in the Political Behavior of LLMs as a Context-Conditioned Distribution</div>
    <div class="icons"><img src="{u('icons', 'ui', 'github_white.svg')}">sakhadib/LLM-Ideoplasticity <img src="{u('icons', 'ui', 'globe_white.svg')}">sakhadib.github.io/LLM-Ideoplasticity <img src="{u('icons', 'ui', 'arxiv_white.svg')}" style="height:9mm;vertical-align:-1.5mm">2606.28335</div>
  </div>
  <img class="qr" src="{u('qr', 'qr_card_white.svg')}">
</div>
<div class="foot"><div>Made with <img src="{u('icons', 'ui', 'heart_red.svg')}"> by Sakhawat, Raiyan <i>et al.</i></div><div>The conference name goes here</div><div><img src="{u('icons', 'ui', 'twitter_white.svg')}">@realRifatRaiyan <img src="{u('icons', 'ui', 'envelope_white.svg')}">rifatraiyan@iut-dhaka.edu</div></div>
<div class="alt"><img src="{u('qr', 'qr_card.svg')}"><img src="{u('logos', 'iut_emblem.svg')}"><img src="{u('logos', 'oic_emblem.svg')}"><img src="{u('icons', 'ui', 'arxiv_colour.svg')}" style="height:30mm"></div>
</body></html>'''
hp = os.path.join(out, 'band.html')
open(hp, 'w', encoding='utf-8', newline='\n').write(html)
pdf = os.path.join(out, 'band.pdf')
print(html_to_pdf(hp, pdf, 841, 260))
d = pymupdf.open(pdf)
p = d[0]
print('pages', len(d), 'KB', os.path.getsize(pdf) // 1024, 'images', [(i[2], i[3]) for i in p.get_images(full=True)], 'fonts', [f[3] for f in p.get_fonts()])
p.get_pixmap(dpi=62, alpha=False).save(os.path.join(out, 'band.png'))
r = p.rect
p.get_pixmap(dpi=120, alpha=False, clip=pymupdf.Rect(0, 0, r.width * 0.3, r.height * 0.52)).save(os.path.join(out, 'band_left_120dpi.png'))
p.get_pixmap(dpi=120, alpha=False, clip=pymupdf.Rect(r.width * 0.8, 0, r.width, r.height * 0.52)).save(os.path.join(out, 'band_right_120dpi.png'))
