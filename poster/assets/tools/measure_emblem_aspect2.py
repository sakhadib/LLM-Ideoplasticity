"""Compare proportions of the emblem between sources: crescent, shield and whole-emblem bounding boxes."""
import sys

import numpy as np
import pymupdf
from PIL import Image

wiki_p, sup_p, ref_p = sys.argv[1:4]


def on_white(im):
    im = im.convert('RGBA')
    bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    return np.asarray(bg.convert('RGB')).astype(int)


def stats(name, a):
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    red = (R > 170) & (G < 110) & (B < 110)
    green = (G > 120) & (R < 110) & (B < 130)
    ys, xs = np.where(red)
    cres = (xs.max() - xs.min() + 1, ys.max() - ys.min() + 1)
    ys, xs = np.where(green)
    whole = (xs.max() - xs.min() + 1, ys.max() - ys.min() + 1)
    # Shield width: widest green extent in the row band at 45% of the green height (above the ribbon)
    y0 = ys.min()
    h = whole[1]
    shield_row = green[int(y0 + 0.55 * h)]
    sx = np.where(shield_row)[0]
    shield_w = sx.max() - sx.min() + 1
    print(f'{name:12s} crescent {cres} ratio {cres[0] / cres[1]:.3f} | green whole {whole} ratio {whole[0] / whole[1]:.3f} | shield width/total height {shield_w / h:.3f}')
    return cres[0] / cres[1], whole[0] / whole[1], shield_w / h


wiki = on_white(Image.open(wiki_p))
sup = on_white(Image.open(sup_p))
ref = on_white(Image.open(ref_p).crop((0, 0, 234, 324)))
doc = pymupdf.open(r'C:\Users\rifat\Desktop\IUT Stuff\IUTLetterHeadBackground.pdf')
pix = doc[0].get_pixmap(dpi=1200, clip=pymupdf.Rect(40, 24, 98, 120), alpha=False)
lh = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n).astype(int)[..., :3]
a = stats('wikipedia', wiki)
b = stats('supplied', sup)
c = stats('ref lockup', ref)
d = stats('letterhead', lh)
for lab, v in (('wikipedia', a), ('supplied', b), ('ref lockup', c)):
    print(lab, 'implied x-stretch for letterhead: crescent', round(v[0] / d[0], 3), 'whole', round(v[1] / d[1], 3), 'shield', round(v[2] / d[2], 3))
