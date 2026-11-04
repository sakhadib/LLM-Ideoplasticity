"""Confirm MathJax renders offline to vector paths in a Chrome-printed PDF. All network requests are blocked."""
import os
import pathlib
import sys

import pymupdf
from playwright.sync_api import sync_playwright

vendor, fonts_css, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
mj = pathlib.Path(vendor, 'tex-svg.js').resolve().as_uri()
css = pathlib.Path(fonts_css).resolve().as_uri()
html = rf'''<!doctype html><html><head><meta charset="utf-8"><link rel="stylesheet" href="{css}">
<script>window.MathJax = {{ tex: {{ inlineMath: [['\\(', '\\)']], displayMath: [['\\[', '\\]']] }}, svg: {{ fontCache: 'none' }}, startup: {{ typeset: true }} }};</script>
<script src="{mj}"></script>
<style>@page {{ size: 400mm 170mm; margin:0 }} html,body {{ margin:0; background:#fff; color:#111827; font:400 27pt/36pt 'Pagella Poster' }}
.w {{ padding:8mm 12mm }} .big {{ font-size:54pt; color:#5445B5; line-height:1.4 }} .box {{ background:#F5F5FE; border-left:1mm solid #8180DE; padding:3mm 6mm; margin:3mm 0 }}</style>
</head><body><div class="w">
<div class="big">\(\mathbb{{P}}(\text{{position}}\mid\text{{context}})\)</div>
<div class="big">\(p \sim \mathbb{{P}}(\cdot \mid \mathbf{{c}})\)</div>
<div class="box">Inline in Pagella: a bounded ideological space \(\mathcal{{I}} \subset \mathbb{{R}}^d\), with context \(\mathcal{{C}} = \mathcal{{C}}_1 \times \mathcal{{C}}_2 \times \cdots \times \mathcal{{C}}_k\), and \(\mathrm{{PSS}}(m,c,s) = d(p_{{m,c,s}},\, p_{{m,c_0,s}})\).</div>
</div></body></html>'''
hp = os.path.join(out, 'math.html')
open(hp, 'w', encoding='utf-8', newline='\n').write(html)
pdf = os.path.join(out, 'math.pdf')
blocked = []
with sync_playwright() as p:
    b = p.chromium.launch(channel='chrome')
    pg = b.new_page()
    def handler(route):
        if route.request.url.startswith('file:'):
            route.continue_()
        else:
            blocked.append(route.request.url)
            route.abort()
    pg.route('**/*', handler)
    msgs = []
    pg.on('console', lambda m: msgs.append(m.text))
    pg.on('pageerror', lambda e: msgs.append('ERR ' + str(e)))
    pg.goto(pathlib.Path(hp).resolve().as_uri(), wait_until='load')
    pg.wait_for_function('window.MathJax && MathJax.startup && MathJax.startup.promise')
    pg.evaluate('MathJax.startup.promise')
    pg.evaluate('document.fonts.ready')
    n = pg.evaluate("document.querySelectorAll('mjx-container svg').length")
    print('mjx svg count', n, '| errors', pg.evaluate("document.querySelectorAll('mjx-merror, [data-mjx-error]').length"))
    pg.pdf(path=pdf, print_background=True, prefer_css_page_size=True)
    b.close()
print('console', msgs, 'blocked requests', blocked)
d = pymupdf.open(pdf)
pg0 = d[0]
print('pages', len(d), 'images', len(pg0.get_images()), 'drawings', len(pg0.get_drawings()), 'fonts', [f[3] for f in pg0.get_fonts()], os.path.getsize(pdf) // 1024, 'KB')
pg0.get_pixmap(dpi=80, alpha=False).save(os.path.join(out, 'math.png'))
