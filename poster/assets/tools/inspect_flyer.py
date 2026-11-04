"""Check whether the conference's printing flyer holds a better AACL logo than the 1200 px PNG."""
import io
import os
import sys

import pymupdf
from PIL import Image

flyer, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
d = pymupdf.open(flyer)
p = d[0]
print(p.rect, 'drawings', len(p.get_drawings()), 'fonts', len(p.get_fonts()))
for im in p.get_images(full=True):
    xref, smask, w, h = im[0], im[1], im[2], im[3]
    rects = p.get_image_rects(xref)
    print('img', xref, 'smask', smask, (w, h), im[5], im[8], [tuple(round(v) for v in r) for r in rects][:2])
    if rects and rects[0].y0 < 120:
        base = d.extract_image(xref)
        img = Image.open(io.BytesIO(base['image'])).convert('RGB')
        if smask:
            m = Image.open(io.BytesIO(d.extract_image(smask)['image'])).convert('L').resize(img.size)
            img.putalpha(m)
        img.save(os.path.join(out, f'flyer_logo_{xref}.png'))
        print('  saved', img.size)
top = [dr for dr in p.get_drawings() if dr['rect'].y1 < 130]
print('top drawings', len(top))
pix = p.get_pixmap(dpi=300, clip=pymupdf.Rect(150, 20, 450, 120), alpha=False)
pix.save(os.path.join(out, 'flyer_top_300dpi.png'))
