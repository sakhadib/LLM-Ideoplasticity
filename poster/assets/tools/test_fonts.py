"""Print a font test page to PDF via Chrome; report embedded font types; render for inspection."""
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
@page {{ size: 500mm 520mm; margin: 0 }}
html,body {{ margin:0; background:#fff; color:#111827; font-family:'Pagella Poster'; }}
.band {{ background:#5445B5; color:#fff; padding:8mm 12mm; }}
.t1 {{ font:600 115pt/1.05 'Fraunces Poster'; letter-spacing:-0.01em; }}
.t2 {{ font:500 56pt/1.15 'Fraunces Poster'; }}
.wrap {{ padding:8mm 12mm; }}
.lab {{ font:400 16pt 'JetBrains Mono Poster'; color:#4B5563; margin-top:5mm; }}
.sec144 {{ font:600 50pt/1.1 'Fraunces Poster'; color:#5445B5; }}
.sec36 {{ font:600 50pt/1.1 'Fraunces Poster Text'; color:#5445B5; }}
.card144 {{ font:600 36pt/1.1 'Fraunces Poster'; color:#5445B5; }}
.card36 {{ font:600 36pt/1.1 'Fraunces Poster Text'; color:#5445B5; }}
.it144 {{ font:italic 500 50pt/1.15 'Fraunces Poster'; color:#5445B5; }}
.it36 {{ font:italic 500 36pt/1.15 'Fraunces Poster Text'; color:#5445B5; }}
.body {{ font:400 27pt/36pt 'Pagella Poster'; }}
.sc {{ font-variant-caps: small-caps; font-weight:700; color:#fff; background:#6E65CE; padding:1.5mm 4mm; font-size:27pt; display:inline-block; }}
.num {{ font:600 96pt/1 'Fraunces Poster'; }}
.mono {{ font:500 20pt/1.3 'JetBrains Mono Poster'; font-feature-settings:'liga' 0,'calt' 0; }}
.bn {{ font:400 30pt/1.4 'Bangla Poster'; }}
.bn2 {{ font:400 30pt/1.4 'Nirmala UI'; }}
</style></head><body>
<div class="band"><div class="t1">LLM-Ideoplasticity:</div>
<div class="t2">Measuring Ideological Plasticity in the Political Behavior of LLMs</div></div>
<div class="wrap">
<div class="lab">Fraunces Poster (opsz 144) vs Fraunces Poster Text (opsz 36), section head 50 pt</div>
<div class="sec144">3 Local Plasticity: One Model, Many Positions</div>
<div class="sec36">3 Local Plasticity: One Model, Many Positions</div>
<div class="lab">Card names 36 pt: opsz 144, then opsz 36</div>
<div class="card144">PSS Prompt register 0.1234 RSS LDS</div>
<div class="card36">PSS Prompt register 0.1234 RSS LDS</div>
<div class="lab">Italic 50 pt opsz 144; italic 36 pt opsz 36</div>
<div class="it144">A single point cannot summarize LLM political behavior</div>
<div class="it36">it must be characterized as a shape</div>
<div class="lab">Big numbers: default figures, then lining via font-variant</div>
<div class="num">0.5721 17/27 2.56% ≈0.29</div>
<div class="num" style="font-variant-numeric:lining-nums">0.5721 17/27 2.56% ≈0.29</div>
<div class="lab">Pagella body 27/36 pt with fi ligature, italic, bold; small caps box title; digits</div>
<div class="sc">Our Thesis and Contributions</div>
<div class="body">The prevailing approach to evaluating the <i>political</i> behavior of large language models typically relies on <b>forced-choice</b> instruments, office fi fl. Digits: 0123456789; lining+tabular: <span style="font-variant-numeric:lining-nums tabular-nums">0123456789</span>; oldstyle: <span style="font-variant-numeric:oldstyle-nums">0123456789</span>. Symbols: → ≈ × ∼ ≤ ≥ ∈ ⟨lrgen⟩ † − – —</div>
<div class="lab">JetBrains Mono 20 pt table numbers</div>
<div class="mono">0.1829 0.1795 0.2813 +0.0577 -0.4230 15.9222 25.61 -> => !=</div>
<div class="lab">Bangla Poster (Noto Serif Bengali), then Nirmala UI</div>
<div class="bn">{BN}</div>
<div class="bn2">{BN}</div>
</div></body></html>"""
hp = os.path.join(out, 'fonts_test.html')
open(hp, 'w', encoding='utf-8', newline='\n').write(html)
pdf = os.path.join(out, 'fonts_test.pdf')
msgs = html_to_pdf(hp, pdf, 500, 520)
print('console:', msgs)
d = pymupdf.open(pdf)
print('pages', len(d), d[0].rect)
for f in d[0].get_fonts(full=True):
    print(' ', f[1], f[2], f[3], f[5])
for s in d[0].get_text('dict')['blocks'][:0]:
    pass
pix = d[0].get_pixmap(dpi=60, alpha=False)
pix.save(os.path.join(out, 'fonts_test.png'))
print(pix.width, pix.height)
txt = d[0].get_text()
sys.stdout.reconfigure(encoding='utf-8')
print('text extraction sample:', txt[:120].replace('\n', ' | '))
print('bangla text in PDF:', [l for l in txt.split('\n') if any('ঀ' <= c <= '৿' for c in l)][:2])
