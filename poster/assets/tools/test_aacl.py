"""Render the conference SVG beside the v2 PNG and report SVG contents (scripts, images, fonts)."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from chrome import html_to_png  # noqa: E402

svg_path, png_path, out = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
s = open(svg_path, encoding='utf-8', errors='replace').read()
print('bytes', len(s))
print('head:', s[:300].replace('\n', ' '))
for tag in ('script', 'image', 'text', 'style', 'foreignObject', 'use', 'path', 'polygon', 'rect', 'circle', 'linearGradient'):
    print(tag, len(re.findall('<' + tag + r'[\s>]', s)))
print('external refs:', re.findall(r'(?:href|src)="(http[^"]+)"', s)[:5])
print('viewBox:', re.findall(r'viewBox="([^"]+)"', s)[:2], 'w/h', re.findall(r'<svg[^>]*?(width="[^"]+"|height="[^"]+")', s)[:2])
html = f'''<!doctype html><html><body style="margin:0;background:#fff;font:16px sans-serif">
<div>SVG</div><img src="{os.path.abspath(svg_path)}" style="width:1600px;display:block">
<div>v2 PNG</div><img src="{os.path.abspath(png_path)}" style="width:1600px;display:block">
</body></html>'''
hp = os.path.join(out, 'aacl_compare.html')
open(hp, 'w', encoding='utf-8', newline='\n').write(html)
html_to_png(hp, os.path.join(out, 'aacl_compare.png'), 1600, 860)
