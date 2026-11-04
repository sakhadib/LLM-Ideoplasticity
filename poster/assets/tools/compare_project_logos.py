"""Contact sheet of the project-logo variants on the band colour and on white."""
import glob
import os
import sys

from PIL import Image, ImageDraw, ImageFont

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
files = sorted(glob.glob(os.path.join(src, 'llm_ideoplasticity_logo_1*.png')))
font = ImageFont.truetype(r'C:\Windows\Fonts\arial.ttf', 15)
cell = 300
sheet = Image.new('RGB', (cell * len(files) // 2 + 20, cell * 4 + 40), (255, 255, 255))
cols = len(files) // 2
for i, f in enumerate(files):
    im = Image.open(f)
    a = im.convert('RGBA').split()[3]
    corner = im.convert('RGBA').getpixel((2, 2))
    print(os.path.basename(f), im.size, im.mode, 'alpha', a.getextrema(), 'corner', corner, 'alpha-bbox', a.getbbox(), os.path.getsize(f))
    r = im.convert('RGBA').resize((cell - 40, cell - 40), Image.LANCZOS)
    c, row = i % cols, i // cols
    x, y = c * cell + 10, row * 2 * cell + 10
    d = ImageDraw.Draw(sheet)
    d.rectangle((x, y, x + cell - 20, y + cell - 20), fill=(0x54, 0x45, 0xB5))
    sheet.paste(r, (x + 10, y + 10), r)
    d.rectangle((x, y + cell, x + cell - 20, y + 2 * cell - 20), fill=(255, 255, 255), outline=(200, 200, 200))
    sheet.paste(r, (x + 10, y + cell + 10), r)
    d.text((x + 5, y + 2 * cell - 40), os.path.basename(f).replace('llm_ideoplasticity_logo_1', ''), fill=(0, 0, 0), font=font)
sheet.save(os.path.join(out, 'project_logos.png'))
