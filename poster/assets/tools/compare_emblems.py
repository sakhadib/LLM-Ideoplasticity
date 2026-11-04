"""Side-by-side of every IUT emblem source at equal height, on white, to confirm the design matches."""
import os
import sys

import pymupdf
from PIL import Image

sp, logos, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
H = 900
srcs = []
for name, p in (('supplied png', os.path.join(sp, 'refs', 'iut_logo.png')),
                ('wikipedia png', os.path.join(sp, 'refs', 'web_iut', 'Islamic_University_of_Technology_%28coat_of_arms%29.png')),
                ('ref lockup', os.path.join(sp, 'refs', 'extracted', 'ref2_iut_lockup.png'))):
    im = Image.open(p).convert('RGBA')
    if name == 'ref lockup':
        im = im.crop((0, 0, 234, 324))
    bb = im.getchannel('A').point(lambda v: 255 if v > 30 else 0).getbbox()
    im = im.crop(bb)
    srcs.append((name, im))
# Letterhead vector
doc = pymupdf.open(r'C:\Users\rifat\Desktop\IUT Stuff\IUTLetterHeadBackground.pdf')
pix = doc[0].get_pixmap(dpi=900, clip=pymupdf.Rect(40, 24, 98, 120), alpha=False)
im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('RGBA')
bb = im.convert('L').point(lambda v: 255 if v < 245 else 0).getbbox()
srcs.append(('letterhead vector', im.crop(bb)))
# Student guide cover vector (on green)
doc = pymupdf.open(r'C:\Users\rifat\Desktop\IUT Teaching\StudentGuideIUT.pdf')
pix = doc[0].get_pixmap(dpi=900, clip=pymupdf.Rect(145, 70, 200, 130), alpha=False)
srcs.append(('student guide', Image.frombytes('RGB', (pix.width, pix.height), pix.samples).convert('RGBA')))
W = sum(int(i.width * H / i.height) + 30 for _, i in srcs)
sheet = Image.new('RGBA', (W, H + 20), (0x54, 0x45, 0xB5, 255))
x = 10
for name, im in srcs:
    w = int(im.width * H / im.height)
    r = im.resize((w, H), Image.LANCZOS)
    sheet.alpha_composite(r, (x, 10))
    print(name, im.size, 'aspect', round(im.width / im.height, 3))
    x += w + 30
sheet.convert('RGB').save(os.path.join(out, 'emblem_sources.png'))
