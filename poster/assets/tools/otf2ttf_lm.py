"""Convert Latin Modern OTF (CFF) to TrueType outlines with fontTools/cu2qu, keeping GSUB, GPOS and metrics.

Same method as otf2ttf_pagella.py: Chrome's PDF backend writes CFF OpenType fonts as Type 3, TrueType outlines embed
as TrueType. kern (GPOS), liga and tnum (GSUB) carry over unchanged.
Usage: python -I otf2ttf_lm.py <MiKTeX fonts/opentype/public/lm dir> <out_dir>
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
        tt_pen = TTGlyphPen(glyphs)
        glyphs[name].draw(Cu2QuPen(tt_pen, max_err, reverse_direction=reverse_direction))
        quad[name] = tt_pen.glyph()
    return quad


def convert(src, dst, fam, style):
    f = TTFont(os.path.join(fdir, src))
    order = f.getGlyphOrder()
    quad = glyphs_to_quadratic(f.getGlyphSet())
    maxp = f['maxp']
    maxp.tableVersion = 0x00010000
    for k in ('maxZones', 'maxTwilightPoints', 'maxStorage', 'maxFunctionDefs', 'maxInstructionDefs', 'maxStackElements',
              'maxSizeOfInstructions', 'maxComponentElements', 'maxPoints', 'maxContours', 'maxCompositePoints',
              'maxCompositeContours', 'maxComponentDepth'):
        setattr(maxp, k, 1 if k == 'maxZones' else 0)
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
    name = f['name']
    for pid, eid, lid in ((3, 1, 0x409), (1, 0, 0)):
        name.setName(fam, 1, pid, eid, lid)
        name.setName(f'{fam} {style}', 4, pid, eid, lid)
        name.setName(f'{fam}-{style}', 6, pid, eid, lid)
    out = os.path.join(outdir, dst)
    f.save(out)
    g = TTFont(out)
    feats = sorted({fr.FeatureTag for fr in g['GSUB'].table.FeatureList.FeatureRecord}) if 'GSUB' in g else []
    gpos = sorted({fr.FeatureTag for fr in g['GPOS'].table.FeatureList.FeatureRecord}) if 'GPOS' in g else []
    cm = g.getBestCmap()
    missing = [c for c in '0123456789−∞†' if ord(c) not in cm]
    print(f'wrote {dst} {os.path.getsize(out) // 1024} KB, {len(order)} glyphs, GSUB {feats}, GPOS {gpos}, missing {missing or "none"}')


for src, dst, fam, style in (('lmroman10-regular.otf', 'LMRomanPoster-Regular.ttf', 'LMRomanPoster', 'Regular'),
                             ('lmroman10-bold.otf', 'LMRomanPoster-Bold.ttf', 'LMRomanPoster', 'Bold'),
                             ('lmroman10-italic.otf', 'LMRomanPoster-Italic.ttf', 'LMRomanPoster', 'Italic'),
                             ('lmmono10-regular.otf', 'LMMonoPoster-Regular.ttf', 'LMMonoPoster', 'Regular')):
    convert(src, dst, fam, style)
