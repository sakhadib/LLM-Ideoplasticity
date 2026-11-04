"""Second font test: mid optical size for big numbers and subtitles, plus a Bangla zoom."""
import os
import pathlib
import sys

import pymupdf

sys.path.insert(0, os.path.dirname(__file__))
from chrome import html_to_pdf  # noqa: E402

fonts_css, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
css_url = pathlib.Path(fonts_css).resolve().as_uri()
BN = 'সোশ্যাল ওয়েলফেয়ার স্টেটের মূল ধারণা'
html = f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="{css_url}">
<style>
@page {{ size: 500mm 300mm; margin: 0 }}
html,body {{ margin:0; background:#fff; color:#111827; }}
.band {{ background:#5445B5; color:#fff; padding:6mm 10mm; }}
.lab {{ font:400 14pt 'JetBrains Mono Poster'; opacity:.8; }}
.n {{ font-size:96pt; line-height:1.05; font-weight:600; }}
.s {{ font-size:54pt; line-height:1.1; font-weight:500; }}
.bn {{ font:400 60pt/1.5 'Bangla Poster'; padding:0 10mm; }}
</style></head><body>
<div class="band">
<div class="lab">subtitle 54 pt medium: opsz 144 / 72 / 36</div>
<div class="s" style="font-family:'Fraunces Poster'">Measuring Ideological Plasticity in LLMs</div>
<div class="s" style="font-family:'Fraunces Poster Mid'">Measuring Ideological Plasticity in LLMs</div>
<div class="s" style="font-family:'Fraunces Poster Text'">Measuring Ideological Plasticity in LLMs</div>
</div>
<div style="padding:4mm 10mm">
<div class="lab">big stat 96 pt semibold: opsz 144 / 72 / 36</div>
<div class="n" style="font-family:'Fraunces Poster'">0.57 0.52 17/27 2.56% ≈0.29</div>
<div class="n" style="font-family:'Fraunces Poster Mid'">0.57 0.52 17/27 2.56% ≈0.29</div>
<div class="n" style="font-family:'Fraunces Poster Text'">0.57 0.52 17/27 2.56% ≈0.29</div>
</div>
<div class="bn">{BN}</div>
</body></html>"""
hp = os.path.join(out, 'fonts_test2.html')
open(hp, 'w', encoding='utf-8', newline='\n').write(html)
pdf = os.path.join(out, 'fonts_test2.pdf')
print(html_to_pdf(hp, pdf, 500, 300))
d = pymupdf.open(pdf)
print('pages', len(d))
for f in d[0].get_fonts(full=True):
    print(' ', f[1], f[2], f[3])
d[0].get_pixmap(dpi=64, alpha=False).save(os.path.join(out, 'fonts_test2.png'))
