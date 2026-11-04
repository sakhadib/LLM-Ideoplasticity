"""Fidelity test: print each SVG figure via Chrome at its intended poster width, render the PDF, and compare with a
direct render of the source PDF at the same scale.

Usage: python test_figures.py <figures dir> <arxiv asset dir> <out dir>
"""
import json
import os
import pathlib
import sys

import numpy as np
import pymupdf
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
from chrome import html_to_pdf  # noqa: E402

figs, src, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
meta = json.load(open(os.path.join(figs, 'figures.json'), encoding='utf-8'))
# Intended print widths in mm, from the brief
WIDTHS = {'fig1a_parties': 257, 'fig1b_llms': 257, 'polytope_3d': 200, 'polytope_chrono_2d': 330, 'pipeline': 170, 'polytope_chrono_3d': 330}
DPI = 110
rows = []
for name, wmm in WIDTHS.items():
    m = meta[name]
    hmm = wmm / m['aspect_w_over_h']
    uri = pathlib.Path(figs, name + '.svg').resolve().as_uri()
    html = f'''<!doctype html><html><head><style>@page {{ size: {wmm}mm {hmm:.3f}mm; margin:0 }}
    html,body {{ margin:0; background:#fff }} img {{ width:{wmm}mm; height:{hmm:.3f}mm; display:block }}</style></head>
    <body><img src="{uri}"></body></html>'''
    hp = os.path.join(out, name + '.html')
    open(hp, 'w', encoding='utf-8', newline='\n').write(html)
    pdf = os.path.join(out, name + '.pdf')
    msgs = html_to_pdf(hp, pdf, wmm, round(hmm, 3))
    d = pymupdf.open(pdf)
    p = d[0]
    imgs = [(i[2], i[3], i[8]) for i in p.get_images(full=True)]
    ndraw = len(p.get_drawings())
    fonts = len(p.get_fonts())
    kb = os.path.getsize(pdf) // 1024
    pages = len(d)
    # Chrome render
    pix = p.get_pixmap(dpi=DPI, alpha=False)
    chrome = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    # Direct render of source, same crop and scale
    s = pymupdf.open(os.path.join(src, m['source']))
    sp = s[0]
    # Find crop from the svg's viewBox
    txt = open(os.path.join(figs, name + '.svg'), encoding='utf-8').read(4000)
    import re
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', txt).group(1).split()]
    clip = pymupdf.Rect(vb[0], vb[1], vb[0] + vb[2], vb[1] + vb[3])
    scale = (wmm / 25.4 * DPI) / vb[2]
    pix2 = sp.get_pixmap(matrix=pymupdf.Matrix(scale, scale), clip=clip, alpha=False)
    direct = Image.frombytes('RGB', (pix2.width, pix2.height), pix2.samples)
    W = min(chrome.width, direct.width)
    H = min(chrome.height, direct.height)
    a = np.asarray(chrome.crop((0, 0, W, H))).astype(int)
    b = np.asarray(direct.crop((0, 0, W, H))).astype(int)
    diff = np.abs(a - b).sum(axis=2)
    nonwhite = (b.sum(axis=2) < 740).mean()
    print(f'{name:22s} {wmm}x{hmm:.0f} mm  pages={pages} pdf={kb} KB images={imgs} drawings={ndraw} fonts={fonts} console={msgs}')
    print(f'    mean|diff|={diff.mean():.2f} p99={np.percentile(diff, 99):.0f} frac>120={(diff > 120).mean():.4f} (ink {nonwhite:.2f})')
    sheet = Image.new('RGB', (W * 2 + 20, H + 20), (255, 0, 255))
    sheet.paste(direct.crop((0, 0, W, H)), (0, 10))
    sheet.paste(chrome.crop((0, 0, W, H)), (W + 20, 10))
    if sheet.width > 2400:
        sheet = sheet.resize((2400, int(sheet.height * 2400 / sheet.width)), Image.LANCZOS)
    sheet.save(os.path.join(out, name + '_compare.png'))
