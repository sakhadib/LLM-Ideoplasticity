"""Convert TeX Gyre Pagella OTF (CFF) to TrueType outlines with fontTools/cu2qu, keeping GSUB, GPOS and metrics.

Chrome's PDF backend writes CFF OpenType fonts as Type 3; TrueType outlines embed as TrueType.
Usage: python -I otf2ttf_pagella.py <dir with texgyrepagella-*.otf> <out_dir>
"""
import os
import sys

from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, newTable

fdir, outdir = sys.argv[1], sys.argv[2]
MAX_ERR = 0.5  # font units, 1000-unit em


def glyphs_to_quadratic(glyphs, max_err=MAX_ERR, reverse_direction=True):
    quad = {}
    for name in glyphs.keys():
        g = glyphs[name]
        tt_pen = TTGlyphPen(glyphs)
        cu2qu_pen = Cu2QuPen(tt_pen, max_err, reverse_direction=reverse_direction)
        g.draw(cu2qu_pen)
        quad[name] = tt_pen.glyph()
    return quad


def convert(src, dst, family, style):
    f = TTFont(os.path.join(fdir, src))
    order = f.getGlyphOrder()
    glyphset = f.getGlyphSet()
    quad = glyphs_to_quadratic(glyphset)
    maxp = f['maxp']
    maxp.tableVersion = 0x00010000
    maxp.maxZones = 1
    maxp.maxTwilightPoints = 0
    maxp.maxStorage = 0
    maxp.maxFunctionDefs = 0
    maxp.maxInstructionDefs = 0
    maxp.maxStackElements = 0
    maxp.maxSizeOfInstructions = 0
    maxp.maxComponentElements = 0
    maxp.maxPoints = 0
    maxp.maxContours = 0
    maxp.maxCompositePoints = 0
    maxp.maxCompositeContours = 0
    maxp.maxComponentDepth = 0
    post = f['post']
    post.formatType = 2.0
    post.extraNames = []
    post.mapping = {}
    post.glyphOrder = order
    f['loca'] = newTable('loca')
    glyf = newTable('glyf')
    glyf.glyphOrder = order
    glyf.glyphs = {n: quad[n] for n in order}
    f['glyf'] = glyf
    glyf.compile(f)  # computes bounds
    del f['CFF ']
    if 'VORG' in f:
        del f['VORG']
    f.sfntVersion = '\000\001\000\000'
    ps = f'PagellaPoster-{style}'
    fam = 'PagellaPoster'
    name = f['name']
    for pid, eid, lid in ((3, 1, 0x409), (1, 0, 0)):
        name.setName(fam, 1, pid, eid, lid)
        name.setName(f'{fam} {style}', 4, pid, eid, lid)
        name.setName(ps, 6, pid, eid, lid)
    f.save(os.path.join(outdir, dst))
    print('wrote', dst, os.path.getsize(os.path.join(outdir, dst)) // 1024, 'KB', len(order), 'glyphs')


for src, dst, style in (('texgyrepagella-regular.otf', 'PagellaPoster-Regular.ttf', 'Regular'),
                        ('texgyrepagella-bold.otf', 'PagellaPoster-Bold.ttf', 'Bold'),
                        ('texgyrepagella-italic.otf', 'PagellaPoster-Italic.ttf', 'Italic'),
                        ('texgyrepagella-bolditalic.otf', 'PagellaPoster-BoldItalic.ttf', 'BoldItalic')):
    convert(src, dst, 'PagellaPoster', style)
