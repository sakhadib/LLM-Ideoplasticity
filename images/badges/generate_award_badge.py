"""Generate the README's transparent, looping award badge.

Run: python images/badges/generate_award_badge.py [--font path/to/verdana.ttf]
Requires Pillow, numpy, and PyMuPDF. The SVG is the static alternative.
"""
from pathlib import Path
import argparse
import math
import tempfile

import numpy as np
import pymupdf
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

OUT = Path(__file__).resolve().parent
GOLD = (148, 107, 24)
LABEL = 'AACL-IJCNLP 2026'
AWARD = 'Best Paper Award'
S = 4  # render at 4x, then store the GIF at 2x for crisp README text
TROPHY = 'M8 3h8v4c0 5-2 8-4 8s-4-3-4-8V3ZM8 5H4v2c0 3 2 5 5 5M16 5h4v2c0 3-2 5-5 5M12 15v5M8 21h8'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--font', default='C:/Windows/Fonts/verdana.ttf')
    args = parser.parse_args()
    font = ImageFont.truetype(args.font, 11 * S)
    left = math.ceil(font.getlength(LABEL) / S) + 31
    right = math.ceil(font.getlength(AWARD) / S) + 12
    width, height = left + right, 20
    px, py = 12, 8
    cw, ch = width + px * 2, height + py * 2
    size = (cw * S, ch * S)
    yy, xx = np.mgrid[:size[1], :size[0]] / S
    clip = Image.new('L', size)
    ImageDraw.Draw(clip).rounded_rectangle((px*S, py*S, (px+width)*S-1, (py+20)*S-1), radius=3*S, fill=255)

    trophy_svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="{TROPHY}"/></svg>'
    with pymupdf.open('svg', trophy_svg.encode()) as source:
        with pymupdf.open('pdf', source.convert_to_pdf()) as pdf:
            pix = pdf[0].get_pixmap(matrix=pymupdf.Matrix(8, 8), alpha=True)
            icon = Image.frombytes('RGBA', (pix.width, pix.height), pix.samples).resize((14*S, 14*S), Image.Resampling.LANCZOS)

    # An always-on amber halo, composited inside the opaque badge so GIF's
    # binary transparency stays clean on both light and dark backgrounds.
    trophy_alpha = Image.new('L', size)
    trophy_alpha.paste(icon.getchannel('A'), ((px+5)*S, (py+3)*S))
    halo = trophy_alpha.filter(ImageFilter.MaxFilter(3*S+1)).filter(ImageFilter.GaussianBlur(1.8*S))
    glow = Image.new('RGBA', size, (255,197,65,0))
    glow.putalpha(ImageChops.multiply(halo.point(lambda a: round(a*.42)), clip))

    # Deterministic four-point glints: origin, outward drift, onset, lifetime, radius.
    sparks = [
        (px+left+21, py+1, -5, -5, .12, .76, 3.6),
        (px+width-18, py+1, 6, -5, .34, .84, 4.05),
        (px+width-1, py+10, 7, -2, .55, .72, 3.45),
        (px+left+60, py+19, 3, 5, .76, .72, 3.3),
    ]

    def frame(t=None):
        rgb = np.empty((*xx.shape, 3), dtype=np.float32)
        rgb[:] = (85, 85, 85)
        rgb[xx >= px+left] = GOLD
        # The familiar subtle vertical finish of a flat Shields badge.
        finish = np.clip(1.04 - .06*(yy-py)/20, .98, 1.04)
        rgb *= finish[..., None]
        if t is not None and .12 < t < 1.22:
            progress = (t-.12) / 1.10
            center = px + left - 25 + progress*(right+50)
            stripe = np.exp(-((xx-center+(yy-py-10)*.55)/8.5)**2)
            stripe *= np.sin(math.pi*progress)**.7 * .30
            stripe[xx < px+left] = 0
            rgb = rgb*(1-stripe[..., None]) + 255*stripe[..., None]
        image = Image.fromarray(np.clip(rgb, 0, 255).astype('uint8'), 'RGB').convert('RGBA')
        image.putalpha(clip)
        image.alpha_composite(glow)
        ink = Image.new('RGBA', size)
        draw = ImageDraw.Draw(ink)
        for label, x in ((LABEL, px+24), (AWARD, px+left+6)):
            draw.text((x*S, (py+15.25)*S), label, font=font, anchor='ls', fill=(0,0,0,70))
            draw.text((x*S, (py+14.5)*S), label, font=font, anchor='ls', fill=(255,255,255,255))
        ink.alpha_composite(icon, ((px+5)*S, (py+3)*S))
        image.alpha_composite(ink)
        draw = ImageDraw.Draw(image)
        if t is not None:
            for x, y, dx, dy, start, lifetime, radius in sparks:
                u = (t-start)/lifetime
                if not 0 < u < 1:
                    continue
                ease = 1-(1-u)**2
                r = radius * math.sin(math.pi*u)**1.1
                cx, cy = (x+dx*ease)*S, (y+dy*ease)*S
                r *= S
                # Scaling replaces alpha fades, preserving clean GIF transparency.
                points = [(cx,cy-r),(cx+r*.23,cy-r*.23),(cx+r,cy),
                          (cx+r*.23,cy+r*.23),(cx,cy+r),(cx-r*.23,cy+r*.23),
                          (cx-r,cy),(cx-r*.23,cy-r*.23)]
                draw.polygon(points, fill=(246,198,80,255))
                if r > 5:
                    core = min(2.6, max(1.6, r*.2))
                    draw.ellipse((cx-core,cy-core,cx+core,cy+core), fill=(255,245,211,255))
        return image.resize((cw*2, ch*2), Image.Resampling.LANCZOS)

    still = frame()
    frames = [still] + [frame(i*.05) for i in range(1, 33)] + [still.copy()]
    durations = [700] + [50]*32 + [2900]
    # One palette across the entire animation; index 0 is reserved for transparency.
    sample = Image.new('RGB', (cw*2, ch*2*len(frames)))
    for i, im in enumerate(frames):
        sample.paste(im.convert('RGB'), (0, i*ch*2))
    adaptive = sample.quantize(colors=254, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    palette = Image.new('P', (1,1))
    # Keep pure white available alongside the shared neutral text shades.
    palette.putpalette([0,0,0,255,255,255] + adaptive.getpalette()[:254*3])
    indexed = []
    for im in frames:
        q = im.convert('RGB').quantize(palette=palette, dither=Image.Dither.NONE)
        q.paste(0, mask=im.getchannel('A').point(lambda a: 255 if a < 128 else 0))
        q.info['transparency'] = 0
        indexed.append(q)
    target = OUT / 'aacl-2026-best-paper.gif'
    indexed[0].save(target, save_all=True, append_images=indexed[1:], duration=durations,
                    loop=0, transparency=0, background=0, disposal=2, optimize=False)

    static_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="20" role="img" aria-label="{LABEL}: {AWARD}">
<title>{LABEL}: {AWARD}</title>
<defs><clipPath id="clip"><rect width="{width}" height="20" rx="3"/></clipPath><linearGradient id="finish" x2="0" y2="100%"><stop stop-color="#fff" stop-opacity=".06"/><stop offset="1" stop-opacity=".04"/></linearGradient><filter id="trophy-glow" x="-80%" y="-80%" width="260%" height="260%" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="3.1"/></filter></defs>
<g clip-path="url(#clip)"><path fill="#555" d="M0 0h{left}v20H0z"/><path fill="#946b18" d="M{left} 0h{right}v20H{left}z"/><rect width="{width}" height="20" fill="url(#finish)"/></g>
<g clip-path="url(#clip)"><svg x="5" y="3" width="14" height="14" viewBox="0 0 24 24" overflow="visible" fill="none" stroke="#ffc541" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" opacity=".42"><path d="{TROPHY}" filter="url(#trophy-glow)"/></svg></g>
<svg x="5" y="3" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="{TROPHY}"/></svg>
<g fill="#fff" font-family="Verdana,DejaVu Sans,sans-serif" font-size="11"><text x="24" y="14.5">{LABEL}</text><text x="{left+6}" y="14.5">{AWARD}</text></g></svg>'''
    (OUT / 'aacl-2026-best-paper.svg').write_text(static_svg, encoding='utf-8')

    # A contact sheet is a local review aid, outside the repository.
    sheet = Image.new('RGB', (cw*2*2, ch*2*4), '#ffffff')
    for i, n in enumerate((0,7,14,21,0,7,14,21)):
        bg = Image.new('RGBA', frames[n].size, '#ffffff' if i<4 else '#0d1117')
        bg.alpha_composite(frames[n])
        sheet.paste(bg.convert('RGB'), ((i%2)*cw*2, (i//2)*ch*2))
    preview = Path(tempfile.gettempdir()) / 'llm-ideoplasticity-award-badge-preview.png'
    sheet.save(preview)
    print(f'{target}: {target.stat().st_size:,} bytes; display {cw}x{ch}px; loop {sum(durations)/1000:.1f}s')
    print('Review:', preview)


if __name__ == '__main__':
    main()
