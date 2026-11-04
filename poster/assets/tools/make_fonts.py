"""Build static poster fonts from downloaded variable TTFs, so Chrome embeds them as TrueType rather than Type 3.

Usage: python -I make_fonts.py <download_dir> <out_dir>
"""
import os
import sys

from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

dl, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)


def set_names(font, family, style, ps):
    name = font['name']
    full = f'{family} {style}'
    for rec in list(name.names):
        if rec.nameID in (16, 17, 21, 22, 25):
            name.removeNames(nameID=rec.nameID)
    for pid, eid, lid in ((3, 1, 0x409), (1, 0, 0)):
        name.setName(family, 1, pid, eid, lid)
        name.setName('Regular', 2, pid, eid, lid)
        name.setName(full, 4, pid, eid, lid)
        name.setName(ps, 6, pid, eid, lid)
    if 'STAT' in font:
        del font['STAT']


def instance(src, axes, family, style, fname):
    vf = TTFont(os.path.join(dl, src))
    st = instancer.instantiateVariableFont(vf, axes, inplace=False)
    ps = (family + '-' + style).replace(' ', '')
    set_names(st, family, style, ps)
    if 'OS/2' in st and 'wght' in axes:
        st['OS/2'].usWeightClass = int(axes['wght'])
    path = os.path.join(out, fname)
    st.save(path)
    print('wrote', fname, os.path.getsize(path) // 1024, 'KB', 'fvar' in st)


FR = 'Fraunces[SOFT,WONK,opsz,wght].ttf'
FI = 'Fraunces-Italic[SOFT,WONK,opsz,wght].ttf'
for w, nm in ((400, 'Regular'), (500, 'Medium'), (600, 'SemiBold')):
    instance(FR, {'opsz': 144, 'SOFT': 0, 'WONK': 0, 'wght': w}, 'FrauncesPoster', nm, f'FrauncesPoster-{nm}.ttf')
for w, nm in ((400, 'Italic'), (500, 'MediumItalic')):
    instance(FI, {'opsz': 144, 'SOFT': 0, 'WONK': 0, 'wght': w}, 'FrauncesPoster', nm, f'FrauncesPoster-{nm}.ttf')
# Optical size 72: a middle ground for big stats and the subtitle.
for w, nm in ((500, 'Medium'), (600, 'SemiBold')):
    instance(FR, {'opsz': 72, 'SOFT': 0, 'WONK': 0, 'wght': w}, 'FrauncesPosterMid', nm, f'FrauncesPosterMid-{nm}.ttf')
instance(FI, {'opsz': 72, 'SOFT': 0, 'WONK': 0, 'wght': 500}, 'FrauncesPosterMid', 'MediumItalic', 'FrauncesPosterMid-MediumItalic.ttf')
# Optical size 36: sturdier thin strokes for card names and small headings.
for w, nm in ((500, 'Medium'), (600, 'SemiBold')):
    instance(FR, {'opsz': 36, 'SOFT': 0, 'WONK': 0, 'wght': w}, 'FrauncesPosterText', nm, f'FrauncesPosterText-{nm}.ttf')
instance(FI, {'opsz': 36, 'SOFT': 0, 'WONK': 0, 'wght': 500}, 'FrauncesPosterText', 'MediumItalic', 'FrauncesPosterText-MediumItalic.ttf')

JB = 'JetBrainsMono[wght].ttf'
for w, nm in ((400, 'Regular'), (500, 'Medium'), (600, 'SemiBold')):
    instance(JB, {'wght': w}, 'JetBrainsMonoPoster', nm, f'JetBrainsMonoPoster-{nm}.ttf')

BN = 'NotoSerifBengali[wdth,wght].ttf'
for w, nm in ((400, 'Regular'), (600, 'SemiBold')):
    instance(BN, {'wdth': 100, 'wght': w}, 'BanglaPoster', nm, f'BanglaPoster-{nm}.ttf')
