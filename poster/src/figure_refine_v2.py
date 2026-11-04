"""Create typography-only v2 figure variants, retaining source data geometry."""
from pathlib import Path
import collections
import copy
import hashlib
import json
import math
import re
import sys

from lxml import etree as ET
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
import pymupdf
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'assets' / 'figures'
OUT = SRC / 'v2'
NS = '{http://www.w3.org/2000/svg}'
XLINK = '{http://www.w3.org/1999/xlink}'
NAMES = ['fig1a_parties.svg', 'fig1b_llms.svg', 'polytope_3d.svg']

def matrix(el):
    return [float(x) for x in re.findall(r'[-+]?\d*\.?\d+(?:e[-+]?\d+)?', el.get('transform', ''))]

def text_runs(root):
    runs = []
    for parent in root.iter():
        run = []
        signature = None
        for el in parent:
            if el.get('data-text') is not None:
                mat = matrix(el)
                sig = (tuple(round(x, 3) for x in mat[:4]), el.get('fill'), el.get(XLINK+'href', '').rsplit('_',1)[0])
                jump = math.dist(mat[4:6], matrix(run[-1])[4:6]) if run else 0
                if run and (sig != signature or jump > math.hypot(*mat[:2])*1.3):
                    runs.append(run)
                    run = []
                run.append(el)
                signature = sig
            elif run:
                runs.append(run)
                run = []
                signature = None
        if run:
            runs.append(run)
    return runs

def inspect():
    for name in NAMES:
        root = ET.parse(str(SRC/name)).getroot()
        print(name)
        for run in text_runs(root):
            print(repr(''.join(x.get('data-text') for x in run)), matrix(run[0]), run[0].get('fill'), 'parent opacity', run[0].getparent().get('opacity'))

FONTS = {}
def font(style='Regular'):
    if style not in FONTS:
        f = TTFont(ROOT/'assets'/'fonts'/f'PagellaPoster-{style}.ttf')
        FONTS[style] = f, f.getGlyphSet(), f.getBestCmap(), f['head'].unitsPerEm
    return FONTS[style]

def outlined_text(text, affine, style='Regular', fill='#111827'):
    f, gs, cmap, em = font(style)
    pen = SVGPathPen(gs)
    cursor = 0
    a,b,c,d,x,y = affine
    for ch in text:
        gn = cmap.get(ord(ch))
        if not gn:
            raise ValueError(f'Font cannot represent {ch!r}')
        gs[gn].draw(TransformPen(pen, (a/em,b/em,c/em,d/em,x+a*cursor/em,y+b*cursor/em)))
        cursor += f['hmtx'].metrics[gn][0]
    el = ET.Element(NS+'path', d=pen.getCommands(), fill=fill)
    el.set('data-text', text)
    el.set('data-v2-typography', 'Pagella '+style)
    return el

def text_stream(root):
    return ''.join(e.get('data-text','') for e in root.iter())

def data_paths(root):
    return collections.Counter((e.get('d'),e.get('transform')) for e in root.iter(NS+'path')
        if not any(p.tag == NS+'defs' for p in e.iterancestors()) and not e.get('data-v2-typography')
        and not e.get('data-v2-leader'))

def refine(name):
    src=SRC/name
    root=ET.parse(str(src)).getroot()
    before=copy.deepcopy(root)
    words=text_stream(before)
    removed=[]
    if name.startswith('fig1'):
        for g in list(root.iter(NS+'g')):
            kids=list(g)
            if len(kids)==2 and all(x.tag==NS+'path' for x in kids) and kids[1].get('stroke') in ('#5fbe5c','#0fafd7'):
                removed.extend((x.get('d'),x.get('transform')) for x in kids)
                g.getparent().remove(g)
    overlays=[]
    for run in text_runs(root):
        txt=''.join(x.get('data-text') for x in run)
        m=matrix(run[0])
        col=run[0].get('fill')
        style='Italic' if txt in ('lrecon','galtan','lrgen') or col in ('#5fbe5c','#0fafd7') else 'Regular'
        color='#111827'
        if col in ('#003566','#9d1458','#5fbe5c','#0fafd7'):
            color='#1f94cc' if name=='fig1a_parties.svg' else '#bc45d8'
        if col in ('#5fbe5c','#0fafd7'):
            # Direct labels remain at the original peaks' projected positions;
            # typography has no box and uses the semantic data colour.
            positions={
                ('fig1a_parties.svg','Progressive Left'):(120,19),
                ('fig1a_parties.svg','Authoritarian Right'):(329,31),
                ('fig1b_llms.svg','Centrist Left'):(179,20),
                ('fig1b_llms.svg','Progressive Left'):(72,78),
            }
            x,y=positions[(name,txt)]
            m=[17,0,0,-17,x,y]
        elif txt.startswith(('Auth-','Lib-')):
            # Floor labels are placed over the surface rather than losing their
            # contrast under a semi-transparent raster surface.
            m=[v*1.12 for v in m[:4]]+m[4:]
            color='#4b5563'
        elif name=='polytope_3d.svg' and txt in ('lrecon','galtan','lrgen'):
            m=[v*1.15 for v in m[:4]]+m[4:]
            if txt=='lrecon':
                m[4]-=8
            if txt=='lrgen':
                m[4]+=6
            if txt=='galtan':
                m[5]+=2
        el=outlined_text(txt,m,style,color)
        # Keep text nodes in source order for exact-copy auditing.
        parent=run[0].getparent()
        parent.insert(parent.index(run[0]),el)
        for child in run:
            parent.remove(child)
        if txt.startswith(('Auth-','Lib-')):
            overlays.append((parent,el))
    # Leave source-order text paths intact; redraw quadrant paths at the top
    # without a second data-text to preserve both legibility and exact-copy QA.
    for parent,el in overlays:
        dupe=copy.deepcopy(el)
        dupe.attrib.pop('data-text')
        dupe.set('fill-opacity','.75')
        el.set('fill-opacity','0')
        root.append(dupe)
    if name.startswith('fig1'):
        leaders={
            'fig1a_parties.svg':['M174 26 C174 35 181 40 182 49','M401 38 C399 48 398 55 397 61'],
            'fig1b_llms.svg':['M221 27 C222 33 220 39 218 44','M171 84 C170 93 175 101 178 107'],
        }
        for d in leaders[name]:
            lead=ET.SubElement(root,NS+'path',d=d,fill='none',stroke='#1f94cc' if name=='fig1a_parties.svg' else '#bc45d8')
            lead.set('stroke-width','.65')
            lead.set('stroke-linecap','round')
            lead.set('data-v2-leader','true')
    if name=='polytope_3d.svg':
        inner=[]
        for el in root.iter(NS+'path'):
            fill=el.get('fill','')
            if re.fullmatch(r'#[0-9a-f]{6}',fill) and el.get('fill-opacity')=='.4':
                r,g,b=[int(fill[i:i+2],16) for i in (1,3,5)]
                if b==255 and r>170 and g<245:
                    t=.18*g/255
                    el.set('fill',f'#{round(236+19*t):02x}{round(141+114*t):02x}ff')
                    el.set('fill-opacity','.45')
                    inner.append(el)
            elif re.fullmatch(r'#[0-9a-f]{6}',fill) and el.get('fill-opacity')=='.2':
                el.set('fill','#74d2fa')
                el.set('fill-opacity','.12')
            if el.get('stroke')=='#9d4edd':
                el.set('stroke','#bc45d8')
                el.set('stroke-opacity','.30')
                inner.append(el)
            elif el.get('stroke')=='#4361ee':
                el.set('stroke','#1f94cc')
                el.set('stroke-opacity','.22')
        # Present the translucent inner envelope above the outer envelope so its
        # semantic magenta is not optically blended into the neutral lavender.
        # Preserve every facet and its within-hull drawing order; axes remain on top.
        anchor=next(e for e in root.iter(NS+'path') if e.get('stroke')=='#222232')
        parent=anchor.getparent()
        for el in inner:
            # Source containers carry no transforms; every facet has its own
            # explicit affine transform, so lifting it retains coordinates.
            assert not any(p.get('transform') for p in el.iterancestors())
            el.getparent().remove(el)
            parent.insert(parent.index(anchor),el)
    assert words==text_stream(root), 'Copy changed'
    expected=data_paths(before)-collections.Counter(removed)
    actual=data_paths(root)
    assert expected==actual, 'Source data geometry changed'
    assert root.get('viewBox')==before.get('viewBox')
    OUT.mkdir(parents=True,exist_ok=True)
    out=OUT/name
    ET.ElementTree(root).write(str(out),encoding='utf-8',xml_declaration=False)
    svg=pymupdf.open(out)
    pdf=pymupdf.open('pdf',svg.convert_to_pdf())
    pix=pdf[0].get_pixmap(matrix=pymupdf.Matrix(2.5,2.5),alpha=False)
    preview=OUT/(out.stem+'_preview.png')
    pix.save(preview)
    return {'file':str(out),'preview':str(preview),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
            'copy_characters':len(words),'copy_exact':True,'data_path_count':sum(expected.values()),
            'data_geometry_exact':True,'removed_pill_paths':len(removed),'viewBox':root.get('viewBox')}

if __name__ == '__main__':
    if '--inspect' in sys.argv:
        inspect()
    else:
        report=[refine(n) for n in NAMES]
        preview_html=OUT/'preview.html'
        preview_html.write_text('<!doctype html><html><body style="margin:0;background:white">'+''.join(f'<img id="p{i}" src="{n}" style="display:block;width:1357px">' for i,n in enumerate(NAMES))+'</body></html>',encoding='utf-8')
        with sync_playwright() as pw:
            browser=pw.chromium.launch(channel='chrome',headless=True)
            page=browser.new_page(viewport={'width':1400,'height':2000},device_scale_factor=1)
            page.goto(preview_html.as_uri())
            page.wait_for_function('Array.from(document.images).every(x=>x.complete)')
            for i,n in enumerate(NAMES):
                page.locator(f'#p{i}').screenshot(path=str(OUT/(Path(n).stem+'_preview.png')))
            browser.close()
        (OUT/'verification.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps(report,indent=2))
