"""List images and page objects in the reference posters' top bands (no get_drawings on HaSPeR)."""
import sys
import os
import pymupdf

sp = sys.argv[1]
refs = os.path.join(sp, 'refs')

for name, band_frac in (('ref2.pdf', 0.115), ('hasper_poster3.pdf', 0.10)):
    path = os.path.join(refs, name)
    doc = pymupdf.open(path)
    page = doc[0]
    W, H = page.rect.width, page.rect.height
    print(f'=== {name}: {W:.1f} x {H:.1f} pt')
    imgs = page.get_images(full=True)
    print('n images:', len(imgs))
    rows = []
    for im in imgs:
        xref, smask, w, h, bpc, cs, alt, nm, flt = im[0], im[1], im[2], im[3], im[4], im[5], im[6], im[7], im[8]
        try:
            rects = page.get_image_rects(xref)
        except Exception as exc:
            rects = []
            print('rect err', xref, exc)
        for r in rects:
            if r.y0 < H * band_frac * 1.05:
                dpi = w / (r.width / 72) if r.width else 0
                rows.append((round(r.x0), round(r.y0), round(r.x1), round(r.y1), xref, smask, w, h, cs, flt, round(dpi)))
    rows.sort()
    print('x0 y0 x1 y1 xref smask w h cs filter dpi')
    for r in rows:
        print(r)
    fonts = page.get_fonts(full=True)
    print('fonts:', sorted(set(f[3] for f in fonts))[:30])
    # Text spans in band
    blocks = page.get_text('dict', clip=pymupdf.Rect(0, 0, W, H * band_frac))['blocks']
    for b in blocks:
        if b.get('type') == 0:
            for l in b.get('lines', []):
                for s in l.get('spans', []):
                    print('TEXT', round(s['bbox'][0]), round(s['bbox'][1]), s['font'], round(s['size'], 1), '#%06x' % s['color'], s['text'][:60])
        else:
            print('IMGBLOCK', [round(v) for v in b['bbox']], b.get('width'), b.get('height'), b.get('ext'))
    if name == 'ref2.pdf':
        draws = page.get_drawings()
        band = [d for d in draws if d['rect'].y1 < H * band_frac]
        print('band vector drawings:', len(band))
        for d in band[:30]:
            print(d['type'], [round(v) for v in d['rect']], d.get('fill'), d.get('color'), len(d['items']))
