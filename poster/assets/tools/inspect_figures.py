"""Inspect the paper's figure PDFs: page size, images, vector drawings, fonts, transparency; extract embedded rasters."""
import io
import os
import sys

import pymupdf
from PIL import Image

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
names = ['teaser12_panelB_smallpdf-pages-2.pdf', 'teaser12_panelB_smallpdf-pages-1.pdf', 'extended_teaser.pdf',
         'extended_teaser_chrono.pdf', 'extended_teaser_chrono_2d.pdf', 'IdeoPlasticityLLM_pipeline2.pdf', 'IdeoPlasticityLLM_pipeline.pdf']
for n in names:
    d = pymupdf.open(os.path.join(src, n))
    p = d[0]
    r = p.rect
    print(f'== {n}: {r.width:.1f} x {r.height:.1f} pt ({r.width * 0.3528:.0f} x {r.height * 0.3528:.0f} mm) pages={len(d)} size={os.path.getsize(os.path.join(src, n)) // 1024} KB')
    print('   fonts:', [f[3] for f in p.get_fonts(full=True)][:6])
    draws = p.get_drawings()
    alphas = set()
    kinds = {}
    for dr in draws:
        kinds[dr['type']] = kinds.get(dr['type'], 0) + 1
        for key in ('fill_opacity', 'stroke_opacity'):
            v = dr.get(key)
            if v not in (None, 1, 1.0):
                alphas.add(round(v, 2))
    print('   drawings', len(draws), kinds, 'opacities', sorted(alphas)[:10])
    for im in p.get_images(full=True):
        xref, smask, w, h, cs, flt = im[0], im[1], im[2], im[3], im[5], im[8]
        rects = p.get_image_rects(xref)
        print(f'   image xref={xref} smask={smask} {w}x{h} {cs} {flt} rect={[tuple(round(v, 1) for v in x) for x in rects][:2]}')
        base = d.extract_image(xref)
        nm = n.replace('.pdf', '') + f'_x{xref}.{base["ext"]}'
        with open(os.path.join(out, nm), 'wb') as f:
            f.write(base['image'])
        if smask:
            mb = d.extract_image(smask)
            with open(os.path.join(out, nm + '.mask.' + mb['ext']), 'wb') as f:
                f.write(mb['image'])
            print('   smask', mb['width'], mb['height'], mb['ext'])
    # High-res crop for a look at line quality
    pix = p.get_pixmap(dpi=200, alpha=False)
    pix.save(os.path.join(out, n.replace('.pdf', '') + '_200dpi.png'))
