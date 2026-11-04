"""High-zoom crops of the Chrome-printed figure PDFs, to inspect gradients, masks and thin lines at print scale."""
import os
import sys

import pymupdf

fid, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
CROPS = {
    'pipeline': (0.0, 0.0, 0.62, 0.32),
    'fig1a_parties': (0.15, 0.05, 0.60, 0.55),
    'fig1b_llms': (0.20, 0.05, 0.65, 0.55),
    'polytope_3d': (0.05, 0.55, 0.50, 1.0),
}
for name, (a, b, c, e) in CROPS.items():
    d = pymupdf.open(os.path.join(fid, name + '.pdf'))
    p = d[0]
    r = p.rect
    clip = pymupdf.Rect(r.width * a, r.height * b, r.width * c, r.height * e)
    pix = p.get_pixmap(dpi=200 if name != 'pipeline' else 300, clip=clip, alpha=False)
    pix.save(os.path.join(out, name + '_zoom.png'))
    print(name, pix.width, pix.height)
