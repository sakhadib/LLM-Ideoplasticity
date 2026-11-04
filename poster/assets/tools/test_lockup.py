"""Render the vector lockup on the band colour, compare it with the reference raster, and print a fidelity test."""
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from chrome import html_to_pdf, html_to_png  # noqa: E402

logos, ref_png, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)
svg = open(os.path.join(logos, 'iut_lockup_white.svg'), encoding='utf-8').read()

html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size: 210mm 60mm; margin: 0 }}
html,body {{ margin:0; background:#5445B5; }}
.w {{ width:190mm; margin:6mm 10mm; }}
svg {{ width:100%; height:auto; display:block; }}
</style></head><body><div class="w">{svg}</div></body></html>"""
hp = os.path.join(out, 'lockup_test.html')
open(hp, 'w', encoding='utf-8', newline='\n').write(html)
msgs = html_to_pdf(hp, os.path.join(out, 'lockup_test.pdf'), 210, 60)
print('console', msgs)

html2 = svg.replace('<svg ', '<svg style="position:absolute;left:0;top:0;width:1786px;height:324px" ', 1)
html2 = f'<!doctype html><html><body style="margin:0;background:#5445B5">{html2}</body></html>'
hp2 = os.path.join(out, 'lockup_cmp.html')
open(hp2, 'w', encoding='utf-8', newline='\n').write(html2)
html_to_png(hp2, os.path.join(out, 'lockup_vector_1x.png'), 1786, 324)
html_to_png(hp2, os.path.join(out, 'lockup_vector_3x.png'), 1786, 324, scale=3)

v = Image.open(os.path.join(out, 'lockup_vector_1x.png')).convert('RGB')
r = Image.open(ref_png).convert('RGBA')
bg = Image.new('RGBA', r.size, (0x54, 0x45, 0xB5, 255))
bg.alpha_composite(r)
bg = bg.convert('RGB')
diff = np.abs(np.asarray(v).astype(int) - np.asarray(bg).astype(int)).sum(axis=2)
print('mean abs diff (per px, sum RGB):', round(float(diff.mean()), 2), '  frac >200:', round(float((diff > 200).mean()), 4))
# Side-by-side stack: reference on top, vector below, difference at the bottom
d_img = Image.fromarray(np.clip(diff, 0, 255).astype(np.uint8)).convert('RGB')
stack = Image.new('RGB', (r.size[0], r.size[1] * 3 + 20), (255, 255, 255))
stack.paste(bg, (0, 0))
stack.paste(v, (0, r.size[1] + 10))
stack.paste(d_img, (0, 2 * r.size[1] + 20))
stack.save(os.path.join(out, 'lockup_compare.png'))
hi = Image.open(os.path.join(out, 'lockup_vector_3x.png')).convert('RGB')
hi.crop((0, 0, 750, 972)).save(os.path.join(out, 'lockup_vec_emblem_zoom.png'))
hi.crop((720, 0, 2700, 972)).resize((1320, 648), Image.LANCZOS).save(os.path.join(out, 'lockup_vec_word_zoom.png'))
