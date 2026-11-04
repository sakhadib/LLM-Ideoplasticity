"""Extract the IUT lockup, OIC emblem and QR images from the ACL 2023 reference poster, keeping alpha.

Usage: python -I extract_ref_logos.py <ref2.pdf> <hasper_poster3.pdf> <outdir>
"""
import io
import os
import sys

import pymupdf
from PIL import Image

ref2, hasper, out = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(out, exist_ok=True)


def rgba(doc, xref, smask):
    base = doc.extract_image(xref)
    im = Image.open(io.BytesIO(base['image'])).convert('RGB')
    if smask:
        mask = Image.open(io.BytesIO(doc.extract_image(smask)['image'])).convert('L')
        if mask.size != im.size:
            mask = mask.resize(im.size, Image.LANCZOS)
        im.putalpha(mask)
    return im


doc = pymupdf.open(ref2)
for name, xref, smask in (('ref2_iut_lockup', 9, 15), ('ref2_acl_logo', 10, 16), ('ref2_qr', 11, 17), ('ref2_oic', 12, 18)):
    im = rgba(doc, xref, smask)
    path = os.path.join(out, name + '.png')
    im.save(path)
    print(name, im.size, im.mode, os.path.getsize(path))

# The HaSPeR lockup and OIC are the same source images; check quickly.
doc2 = pymupdf.open(hasper)
page2 = doc2[0]
W, H = page2.rect.width, page2.rect.height
print('hasper page', W, H)
for name, xref in (('hasper_lockup_rgb', 23399), ('hasper_oic_rgb', 23405)):
    base = doc2.extract_image(xref)
    print(name, base['width'], base['height'], base['ext'], len(base['image']))
# Render the top-right corner (ICCV logo + QR, drawn as vector) at high dpi for QR decoding.
clip = pymupdf.Rect(W * 0.84, 0, W, H * 0.10)
pix = page2.get_pixmap(dpi=200, clip=clip, alpha=False)
pix.save(os.path.join(out, 'hasper_topright.png'))
print('hasper_topright', pix.width, pix.height)
