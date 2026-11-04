"""Crop the chosen project-logo variants to their alpha bounding box.

Band: (4), 864 px with arrowed axes, the logo used in the README. QR centre: (7), 432 px with plain axes, cleaner at small size.
Usage: python make_project_logos.py <images_dir> <logos_dir>
"""
import os
import sys

from PIL import Image

src, out = sys.argv[1], sys.argv[2]
for name, dst in (('llm_ideoplasticity_logo_1 (4).png', 'project_logo_band.png'),
                  ('llm_ideoplasticity_logo_1 (7).png', 'project_logo_qr.png')):
    im = Image.open(os.path.join(src, name)).convert('RGBA')
    box = im.getchannel('A').getbbox()
    im = im.crop(box)
    w, h = im.size
    # Square the crop on a transparent canvas if needed
    side = max(w, h)
    c = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    c.paste(im, ((side - w) // 2, (side - h) // 2))
    c.save(os.path.join(out, dst), optimize=True)
    print(dst, c.size, os.path.getsize(os.path.join(out, dst)) // 1024, 'KB')
