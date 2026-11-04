"""Compare the hero floor texture: direct render of the source PDF vs. the Chrome-printed SVG, plus the raw mask."""
import glob
import os
import sys

import numpy as np
import pymupdf
from PIL import Image

src, fid, figs_raw, out = sys.argv[1:5]
os.makedirs(out, exist_ok=True)
name, pdf = 'fig1b_llms', 'teaser12_panelB_smallpdf-pages-1.pdf'
s = pymupdf.open(os.path.join(src, pdf))[0]
c = pymupdf.open(os.path.join(fid, name + '.pdf'))[0]
# Region of the pink floor to the right of the second peak, in fractions of the page
fx0, fy0, fx1, fy1 = 0.55, 0.30, 0.80, 0.55
scale_c = 300 / 72
pc = c.get_pixmap(matrix=pymupdf.Matrix(scale_c, scale_c), clip=pymupdf.Rect(c.rect.width * fx0, c.rect.height * fy0, c.rect.width * fx1, c.rect.height * fy1), alpha=False)
pc.save(os.path.join(out, 'floor_chrome_300dpi.png'))
scale_s = scale_c * c.rect.width / s.rect.width
ps = s.get_pixmap(matrix=pymupdf.Matrix(scale_s, scale_s), clip=pymupdf.Rect(s.rect.width * fx0, s.rect.height * fy0, s.rect.width * fx1, s.rect.height * fy1), alpha=False)
ps.save(os.path.join(out, 'floor_source_300dpi.png'))
print('sizes', pc.width, pc.height, ps.width, ps.height)
# Raw mask statistics at native resolution: does it hold a checkerboard or dither?
mp = [p for p in glob.glob(os.path.join(figs_raw, 'teaser12_panelB_smallpdf-pages-1_x*')) if '.mask.' in p][0]
m = np.asarray(Image.open(mp).convert('L')).astype(int)
H, W = m.shape
crop = m[int(H * 0.3):int(H * 0.5), int(W * 0.6):int(W * 0.85)]
print('mask crop mean', crop.mean(), 'std', crop.std(), 'neighbour |diff| x', np.abs(np.diff(crop, axis=1)).mean(), 'y', np.abs(np.diff(crop, axis=0)).mean())
Image.fromarray(np.clip(crop * 8, 0, 255).astype(np.uint8)).resize((crop.shape[1] * 3, crop.shape[0] * 3), Image.NEAREST).save(os.path.join(out, 'mask_crop_x8.png'))
