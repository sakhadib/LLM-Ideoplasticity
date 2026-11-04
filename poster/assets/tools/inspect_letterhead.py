"""Inspect the vector IUT and OIC emblems in the official letterhead and catalogue PDFs."""
import os
import sys

import pymupdf

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
desk = r'C:\Users\rifat\Desktop'
for tag, p in (
    ('letterhead', r'IUT Stuff\IUTLetterHeadBackground.pdf'),
    ('catalog', r'PhD Application Documents\IUT CSE Course Catalog.pdf'),
    ('guide', r'IUT Teaching\StudentGuideIUT.pdf'),
):
    d = pymupdf.open(os.path.join(desk, p))
    page = d[0]
    draws = page.get_drawings()
    print('==', tag, 'drawings', len(draws), 'page', page.rect, 'images', len(page.get_images()), 'fonts', len(page.get_fonts()))
    W, H = page.rect.width, page.rect.height
    # Cluster bounding boxes in the upper part of the page
    top = [dr for dr in draws if dr['rect'].y1 < H * 0.25]
    print(' top drawings', len(top))
    if top:
        x0 = min(dr['rect'].x0 for dr in top)
        y0 = min(dr['rect'].y0 for dr in top)
        x1 = max(dr['rect'].x1 for dr in top)
        y1 = max(dr['rect'].y1 for dr in top)
        print(' bbox', round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1))
    import collections
    fills = collections.Counter()
    nitems = 0
    for dr in top:
        c = dr.get('fill')
        if c is not None:
            fills['#%02x%02x%02x' % tuple(int(round(v * 255)) for v in c[:3])] += 1
        nitems += len(dr['items'])
    print(' fills', fills.most_common(12), 'path items', nitems)
    for dr in top[:12]:
        print('   ', dr['type'], [round(v, 1) for v in dr['rect']], dr.get('fill'), dr.get('color'), dr.get('width'), len(dr['items']), dr.get('even_odd'))
    # High-res render of top quarter
    clip = pymupdf.Rect(0, 0, W, H * 0.16)
    pix = page.get_pixmap(dpi=300, clip=clip, alpha=False)
    pix.save(os.path.join(out, f'{tag}_top.png'))
    print(' render', pix.width, pix.height)
