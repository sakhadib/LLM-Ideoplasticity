"""Composite the reference lockup raster on the band colour and crop for inspection."""
import os
import sys

from PIL import Image

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
im = Image.open(src).convert('RGBA')
bg = Image.new('RGBA', im.size, (0x54, 0x45, 0xB5, 255))
bg.alpha_composite(im)
bg.convert('RGB').save(os.path.join(out, 'ref_lockup_on_band.png'))
# zooms
bg.crop((0, 0, 240, 324)).resize((720, 972), Image.LANCZOS).convert('RGB').save(os.path.join(out, 'ref_lockup_emblem_zoom.png'))
bg.crop((240, 0, 900, 324)).resize((1320, 648), Image.LANCZOS).convert('RGB').save(os.path.join(out, 'ref_lockup_word_zoom.png'))
print(im.size)
a = im.split()[3]
print('alpha extrema', a.getextrema())
