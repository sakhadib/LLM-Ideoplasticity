"""Verify the QR cards: print via Chrome at 95 mm on the band colour, render at low dpi, decode under degradations."""
import os
import pathlib
import sys

import numpy as np
import pymupdf
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
from chrome import html_to_pdf  # noqa: E402

qr_dir, out, pylibs = sys.argv[1:4]
CARDS = sys.argv[4:] or ['qr_card.svg', 'qr_card_white.svg']  # optional: the card files to test
sys.path.append(pylibs)
import cv2  # noqa: E402
import zxingcpp  # noqa: E402

os.makedirs(out, exist_ok=True)
det = cv2.QRCodeDetector()


def decode(im):
    a = np.asarray(im.convert('L'))
    z = [r.text for r in zxingcpp.read_barcodes(a)]
    try:
        c, _, _ = det.detectAndDecode(a)
    except Exception:
        c = ''
    return (z[0] if z else None), (c or None)


for fname in CARDS:
    p = pathlib.Path(qr_dir, fname).resolve().as_uri()
    html = f'''<!doctype html><html><head><style>@page {{ size: 130mm 140mm; margin:0 }}
    html,body {{ margin:0; background:#5445B5 }} img {{ width:95mm; margin:10mm 17.5mm; display:block }}</style></head>
    <body><img src="{p}"></body></html>'''
    hp = os.path.join(out, fname + '.html')
    open(hp, 'w', encoding='utf-8', newline='\n').write(html)
    pdf = os.path.join(out, fname + '.pdf')
    print(fname, 'console', html_to_pdf(hp, pdf, 130, 140))
    d = pymupdf.open(pdf)
    print('  pages', len(d), 'images', [(i[2], i[3]) for i in d[0].get_images(full=True)], 'drawings', len(d[0].get_drawings()))
    for dpi in (72, 96, 150, 300):
        pix = d[0].get_pixmap(dpi=dpi, alpha=False)
        im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        if dpi == 150:
            im.save(os.path.join(out, fname + '_150dpi.png'))
        print(f'  {dpi} dpi ({im.width}x{im.height}):', decode(im))
        if dpi in (72, 96):
            for sig in (0.6, 1.0):
                print(f'    blur sigma={sig}:', decode(im.filter(ImageFilter.GaussianBlur(sig))))
            print('    rotate 8 deg + blur 0.6:', decode(im.rotate(8, resample=Image.BICUBIC, fillcolor=(84, 69, 181)).filter(ImageFilter.GaussianBlur(0.6))))
            # Washed-out print with a soft shadow gradient
            arr = np.asarray(im).astype(float)
            grad = np.linspace(0.75, 1.0, arr.shape[1])[None, :, None]
            print('    low contrast + gradient:', decode(Image.fromarray(np.clip(arr * 0.75 * grad + 45, 0, 255).astype(np.uint8))))
