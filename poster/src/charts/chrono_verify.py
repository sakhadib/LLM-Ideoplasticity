"""Render each chrono panel before and after cleaning, side by side, and measure where the pixels differ.

    python poster/src/charts/chrono_verify.py <output_dir>

Differences must lie only where the removed glyphs stood (each <use data-text> position, padded by one glyph);
anything else means the cleaning touched the drawing.
"""
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / 'poster' / 'assets' / 'figures'
OUT = ROOT / 'poster' / 'charts'
PX = 900  # rendered panel side, in pixels


def glyph_boxes(svg_text, vb):
    """Pixel boxes around every removed glyph, generous enough for its full extent."""
    boxes = []
    for m in re.finditer(r'<use data-text="[^"]*" xlink:href="#font_[^"]+" transform="matrix\(([^)]*)\)"', svg_text):
        a, b, c, d, e, f = [float(v) for v in m.group(1).split(',')]
        size = max(abs(a), abs(b), abs(c), abs(d))
        x0, y0 = (e - vb[0]) / vb[2] * PX, (f - vb[1]) / vb[3] * PX
        r = size * 1.2 / vb[2] * PX
        boxes.append((x0 - r, y0 - r, x0 + r, y0 + r))
    return boxes


def main(dst):
    dst.mkdir(parents=True, exist_ok=True)
    report = []
    with sync_playwright() as p:
        b = p.chromium.launch(channel='chrome')
        pg = b.new_page(viewport={'width': 2 * PX + 60, 'height': PX + 40})
        for year in (2009, 2014, 2019):
            before, after = SRC / f'polytope_chrono_2d_{year}.svg', OUT / f'chrono_2d_{year}.svg'
            html = ('<!doctype html><body style="margin:0;background:#fff">'
                    f'<img id="a" src="{before.as_uri()}" style="width:{PX}px;height:{PX}px;position:absolute;left:0;top:0">'
                    f'<img id="b" src="{after.as_uri()}" style="width:{PX}px;height:{PX}px;position:absolute;left:{PX + 60}px;top:0">'
                    '</body>')
            page = dst / f'chrono_{year}_compare.html'
            page.write_text(html, encoding='utf-8')
            pg.goto(page.as_uri())  # a file page may load file images; about:blank may not
            pg.wait_for_function('() => [...document.images].every(i => i.complete)')
            widths = pg.evaluate('() => [...document.images].map(i => i.naturalWidth)')
            if min(widths) == 0:
                raise RuntimeError(f'{year}: a panel failed to load ({widths})')
            pg.wait_for_timeout(300)
            shot = dst / f'chrono_{year}_before_after.png'
            pg.screenshot(path=str(shot), clip={'x': 0, 'y': 0, 'width': 2 * PX + 60, 'height': PX})
            im = np.asarray(Image.open(shot).convert('RGB')).astype(int)
            A, B = im[:, :PX], im[:, PX + 60:2 * PX + 60]
            diff = np.abs(A - B).max(axis=2) > 24
            src_text = before.read_text(encoding='utf-8')
            vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', src_text).group(1).split()]
            allowed = np.zeros_like(diff)
            for x0, y0, x1, y1 in glyph_boxes(src_text, vb):
                allowed[max(0, int(y0)):min(PX, int(y1) + 1), max(0, int(x0)):min(PX, int(x1) + 1)] = True
            stray = diff & ~allowed
            report.append((year, int(diff.sum()), int(stray.sum())))
            # Mark stray pixels in red on the "after" half for inspection
            vis = Image.open(shot).convert('RGB')
            dr = ImageDraw.Draw(vis)
            ys, xs = np.nonzero(stray)
            for y, x in zip(ys[:4000], xs[:4000]):
                dr.point((x + PX + 60, y), fill=(255, 0, 0))
            vis.save(shot)
        b.close()
    for year, n, stray in report:
        print(f'{year}: {n} differing pixels, {stray} outside the removed glyphs')
    return report


if __name__ == '__main__':
    main(Path(sys.argv[1]))
