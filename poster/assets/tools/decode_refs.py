"""Decode the QR codes on the two reference posters."""
import sys

import numpy as np
from PIL import Image

ref2_qr, hasper_tr, pylibs = sys.argv[1:4]
sys.path.append(pylibs)
import zxingcpp  # noqa: E402

for name, path in (('ACL 2023 poster', ref2_qr), ('HaSPeR poster', hasper_tr)):
    im = Image.open(path).convert('RGBA')
    bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
    bg.alpha_composite(im)
    gray = bg.convert('L')
    arrs = [np.asarray(gray), 255 - np.asarray(gray)]
    if name.startswith('HaSPeR'):
        w, h = gray.size
        crop = gray.crop((int(w * 0.70), int(h * 0.13), int(w * 0.91), int(h * 0.67)))
        crop = crop.resize((crop.width * 2, crop.height * 2), Image.LANCZOS)
        crop.save(path.replace('.png', '_qrcrop.png'))
        arrs = [np.asarray(crop), 255 - np.asarray(crop)]
    found = []
    for a in arrs:
        for r in zxingcpp.read_barcodes(a):
            found.append((r.format.name if hasattr(r.format, 'name') else str(r.format), r.text))
    print(name, '->', found if found else 'NOT DECODED')
