"""Scan the user's local PDFs and PNGs for higher-resolution IUT emblem sources."""
import io
import os
import sys

import pymupdf
from PIL import Image

desk = r'C:\Users\rifat\Desktop'
out = sys.argv[1]
os.makedirs(out, exist_ok=True)

pngs = [
    r'GitHub\Starscream-11813.github.io\images\iut.png',
    r'GitHub\Starscream-11813.github.io\images\iutcse.png',
    r'GitHub\Starscream-11813.github.io\images\iut_big.png',
    r'GitHub\Starscream-11813.github.io\images\iut_writing.png',
    r'GitHub\Starscream-11813.github.io\images\iut_writing_big.png',
]
for p in pngs:
    im = Image.open(os.path.join(desk, p))
    print('PNG', p.split('\\')[-1], im.size, im.mode)
    im.convert('RGBA').save(os.path.join(out, p.split('\\')[-1]))

pdfs = [
    r'IUT Stuff\IUTLetterHeadBackground.pdf',
    r'IUT Teaching\StudentGuideIUT.pdf',
    r'IUT Teaching\IUT GERR 24 Final Working Copy.pdf',
    r'IUT Teaching\iut_organogram.pdf',
    r'IUT Teaching\IUT_Convocation_Brochure_Message__Kaykobad__2026.pdf',
    r'PhD Application Documents\IUT CSE Course Catalog.pdf',
    r'PhD Application Documents\IUT Grading System.pdf',
    r'PhD Application Documents\IUT Medium of Instruction MOI.pdf',
]
for p in pdfs:
    path = os.path.join(desk, p)
    if not os.path.exists(path):
        print('missing', p)
        continue
    d = pymupdf.open(path)
    print('PDF', p.split('\\')[-1], 'pages', len(d), d[0].rect)
    seen = set()
    for i, page in enumerate(d):
        if i > 12:
            break
        for im in page.get_images(full=True):
            xref, smask, w, h = im[0], im[1], im[2], im[3]
            if xref in seen:
                continue
            seen.add(xref)
            ratio = w / max(h, 1)
            if w >= 150 and h >= 150 and 0.45 <= ratio <= 1.1:
                rects = page.get_image_rects(xref)
                print('  img', 'page', i, 'xref', xref, 'smask', smask, 'size', (w, h), im[5], im[8], [tuple(round(v) for v in r) for r in rects][:2])
                try:
                    base = d.extract_image(xref)
                    img = Image.open(io.BytesIO(base['image'])).convert('RGB')
                    if smask:
                        m = Image.open(io.BytesIO(d.extract_image(smask)['image'])).convert('L').resize(img.size)
                        img.putalpha(m)
                    nm = f"{p.split(chr(92))[-1][:24].replace(' ', '_')}_{i}_{xref}.png"
                    img.save(os.path.join(out, nm))
                except Exception as exc:
                    print('   extract failed', exc)
    # Vector check on the first page
    page = d[0]
    try:
        draws = page.get_drawings()
        print('  first page: drawings', len(draws), 'images', len(page.get_images()))
    except Exception as exc:
        print('  drawings err', exc)
    pix = page.get_pixmap(dpi=60, alpha=False)
    pix.save(os.path.join(out, 'page0_' + p.split('\\')[-1][:24].replace(' ', '_') + '.png'))
