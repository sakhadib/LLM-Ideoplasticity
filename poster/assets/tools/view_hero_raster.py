"""Composite the hero rasters over white, and render the vector layer alone, to see what is baked into the raster."""
import glob
import os
import sys

import pymupdf
from PIL import Image

figs, src, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
for tag, pdf in (('parties', 'teaser12_panelB_smallpdf-pages-2.pdf'), ('llms', 'teaser12_panelB_smallpdf-pages-1.pdf')):
    stem = pdf.replace('.pdf', '')
    rgb_path = [p for p in glob.glob(os.path.join(figs, stem + '_x*')) if '.mask.' not in p][0]
    mask_path = [p for p in glob.glob(os.path.join(figs, stem + '_x*')) if '.mask.' in p][0]
    rgb = Image.open(rgb_path).convert('RGB')
    mask = Image.open(mask_path).convert('L')
    print(tag, rgb.size, mask.size, os.path.getsize(rgb_path) // 1024, 'KB', mask.getextrema())
    im = rgb.copy()
    im.putalpha(mask)
    bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    bg.convert('RGB').save(os.path.join(out, f'raster_{tag}.png'))
    # Zoom crop of the raster around the peak
    w, h = bg.size
    box = (int(w * 0.18), 0, int(w * 0.48), int(h * 0.42)) if tag == 'parties' else (int(w * 0.3), 0, int(w * 0.6), int(h * 0.42))
    bg.crop(box).resize(((box[2] - box[0]) * 2, (box[3] - box[1]) * 2), Image.NEAREST).convert('RGB').save(os.path.join(out, f'raster_{tag}_zoom.png'))
    # Vector layer only: remove images
    d = pymupdf.open(os.path.join(src, pdf))
    p = d[0]
    for imginfo in p.get_images(full=True):
        p.delete_image(imginfo[0])
    pix = p.get_pixmap(dpi=120, alpha=False)
    pix.save(os.path.join(out, f'vector_only_{tag}.png'))
