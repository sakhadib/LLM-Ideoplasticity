"""Tiny SVG writer for the poster's chart family. All geometry is in millimetres at print size.

Text is measured with the poster's own fonts, so the checks in Svg.check() see real ink: every span at 17 pt or
more, nothing outside the viewBox, no two labels touching, in-plot labels 1.5 mm clear of quadrant rules and plot
edges, box text clear of box borders, and labels clear of data marks.
"""
import base64
import io
import math
import re
from html import escape
from pathlib import Path

import numpy as np
from PIL import Image, ImageFont

import texkit

ROOT = Path(__file__).resolve().parents[3]
ICON_DIR = ROOT / 'poster' / 'assets' / 'icons'

PT = 0.3528      # mm per point
LABEL = 6.0      # 17 pt, the floor for every word in a chart
NUM = 6.0        # numerals take the same floor
MATH = 6.35      # 18 pt: Latin Modern's smaller x-height then matches Pagella at 17 pt
MIN_TEXT = 5.995
INSET = 1.5      # clear space between an in-plot label and any quadrant rule or plot edge
MARK_CLEAR = .5  # clear space between a label and a data mark

INK = '#111827'
MUTED = '#4B5563'
HAIR = '#D9DAEC'
AXIS = '#282040'    # the project logo's ink
LLM = '#EC8DFF'
LLM_DEEP = '#BC45D8'
LLM_DARK = '#7E2A99'  # one step darker in the same hue, for a third line where needed
PARTY = '#74D2FA'
PARTY_DEEP = '#1F94CC'
PARTY_TEXT = '#0E6E9C'  # party blue deep enough for text on the cyan tint (4.8:1)
PARTY_TINT = '#EAF7FE'
LAV = ['#A7A8F0', '#9194E4', '#8180DE', '#6E65CE', '#5445B5']
HI_AMP, HI_STAB, HI_MAX, HI_MIN, HI_ASYM = '#FFE7A8', '#D4EDC9', '#FFD1DC', '#C7E9F1', '#E6D7F2'
# Sampled from the paper's asset/ideoPlots/ow.pdf (see poster/data/palette_samples.json)
QUAD_FULL = {'auth_left': '#F4C2C2', 'auth_right': '#BFD4EC', 'lib_left': '#C9E4C5', 'lib_right': '#F6E6A8'}


def _tint(hex_colour, strength=.58):
    """Mix a colour toward white. Large areas take tints, so the marks on them stand out."""
    rgb = [int(hex_colour[i:i + 2], 16) for i in (1, 3, 5)]
    return '#%02X%02X%02X' % tuple(round(c * strength + 255 * (1 - strength)) for c in rgb)


QUAD = {k: _tint(v) for k, v in QUAD_FULL.items()}
# Sampled from the project logo, outer contour to inner
LOGO_CONTOURS = ['#6068FC', '#7C6CE4', '#B04CD4', '#E038B4']

FONT_TEXT = "'Pagella Poster','TeX Gyre Pagella','Palatino Linotype',Palatino,serif"
# Numerals are set in LaTeX's default face, Latin Modern Roman 10 (tabular digits, a true minus sign).
FONT_NUM = "'LM Roman Poster','Latin Modern Roman','LM Roman 10','CMU Serif',serif"
FONT_DISPLAY = "'Fraunces Poster Text','Fraunces Poster','Fraunces',Georgia,serif"

_FONT_DIR = ROOT / 'poster' / 'assets' / 'fonts'
_LM_DIR = Path('C:/Users/rifat/AppData/Local/Programs/MiKTeX/fonts/opentype/public/lm')
_fonts = {}


def _lm_file(italic, bold):
    """The layout's LM Roman Poster files when present, else MiKTeX's identical lmroman10 originals."""
    stem = {(False, False): 'regular', (False, True): 'bold', (True, False): 'italic', (True, True): 'bolditalic'}[(italic, bold)]
    for f in sorted(_FONT_DIR.glob('LMRoman*')) + sorted(_FONT_DIR.glob('LM*Roman*')):
        low = f.name.lower().replace('-', '').replace('_', '')
        if low.endswith(stem + f.suffix.lower()) and (stem != 'italic' or 'bold' not in low):
            return f
    return _LM_DIR / f'lmroman10-{stem}.otf'


def _font(font, italic, weight):
    w = int(weight or 400)
    if font in ('num', 'data'):
        f = _lm_file(bool(italic), w >= 600)
        if f not in _fonts:
            _fonts[f] = ImageFont.truetype(str(f), 1000)
        return _fonts[f]
    if font == 'display':
        name = 'FrauncesPosterText-MediumItalic.ttf' if italic else ('FrauncesPosterText-SemiBold.ttf' if w >= 600 else 'FrauncesPosterText-Medium.ttf')
    else:
        name = {(False, False): 'PagellaPoster-Regular.ttf', (True, False): 'PagellaPoster-Italic.ttf',
                (False, True): 'PagellaPoster-Bold.ttf', (True, True): 'PagellaPoster-BoldItalic.ttf'}[(bool(italic), w >= 600)]
    if name not in _fonts:
        _fonts[name] = ImageFont.truetype(str(_FONT_DIR / name), 1000)
    return _fonts[name]


_smcp = {}


def _caps_width(s, size):
    """Width of Pagella small caps (the font's smcp glyphs), in mm."""
    if not _smcp:
        from fontTools.ttLib import TTFont
        tt = TTFont(str(_FONT_DIR / 'PagellaPoster-Regular.ttf'))
        gsub = tt['GSUB'].table
        mapping = {}
        for fr in gsub.FeatureList.FeatureRecord:
            if fr.FeatureTag == 'smcp':
                for li in fr.Feature.LookupListIndex:
                    for st in gsub.LookupList.Lookup[li].SubTable:
                        st = getattr(st, 'ExtSubTable', st)
                        mapping.update(getattr(st, 'mapping', {}))
        _smcp.update(cmap=tt.getBestCmap(), hmtx=tt['hmtx'], upm=tt['head'].unitsPerEm, map=mapping)
    tot = 0
    for ch in s:
        g = _smcp['cmap'][ord(ch)]
        tot += _smcp['hmtx'][_smcp['map'].get(g, g) if ch.islower() else g][0]
    return tot / _smcp['upm'] * size


def text_width(s, size, font='text', italic=False, weight=None, track=0, caps=False):
    """Advance width in mm of a string at a font size in mm, measured with the poster's own fonts."""
    if caps:
        return _caps_width(s, size) + (track or 0) * len(s)
    return _font(font, italic, weight).getlength(s) / 1000 * size + (track or 0) * len(s)


def ink_box(s, size, font='text', italic=False, weight=None, track=0):
    """Ink extents (left, top, right, bottom) in mm, relative to the left end of the baseline."""
    if not s.strip():
        return 0, 0, 0, 0
    l, t, r, b = _font(font, italic, weight).getbbox(s, anchor='ls')
    k = size / 1000
    return l * k, t * k, r * k + (track or 0) * (len(s) - 1), b * k


def fit_track(s, size, avail, italic=False, weight=None, limit=-.16):
    """The letter-spacing (<= 0, >= limit mm) that keeps a label's ink within `avail` mm."""
    l, _, r, _ = ink_box(s, size, 'text', italic, weight)
    over = (r - l) - avail
    if over <= 0:
        return 0
    return max(limit, -over / max(len(s) - 1, 1) - .005)


def fmt(v):
    s = f'{v:.2f}'.rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s


_icons = {}


def _load_icon(key):
    """A model logo as dict(kind, aspect, ...). Logos print at about 6 mm, so rasters are kept small.
    A PNG with an opaque white ground gets that ground removed, so it can sit on the pastel quadrants."""
    if key in _icons:
        return _icons[key]
    svg, png = ICON_DIR / f'{key}.svg', ICON_DIR / f'{key}.png'
    res = None
    if svg.exists():
        src = svg.read_text(encoding='utf-8')

        def shrink(m):
            im = Image.open(io.BytesIO(base64.b64decode(re.sub(r'\s+', '', m.group(2)))))
            if max(im.size) > 200:
                im = im.resize((200, round(200 * im.size[1] / im.size[0])), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, 'PNG', optimize=True)
            return m.group(1) + base64.b64encode(buf.getvalue()).decode('ascii')

        src = re.sub(r'(data:image/png;base64,)([A-Za-z0-9+/=\s]+)', shrink, src)
        head = re.search(r'<svg([^>]*)>', src, flags=re.S).group(1)
        vb = re.search(r'viewBox="([^"]+)"', head).group(1)
        nums = [float(v) for v in vb.split()]
        inner = re.search(r'<svg[^>]*>(.*)</svg>', src, flags=re.S).group(1)
        res = dict(kind='svg', aspect=nums[2] / nums[3], vb=vb, inner=inner)
    elif png.exists():
        im = Image.open(png).convert('RGBA')
        arr = np.asarray(im).astype(float)
        if arr[..., 3].min() > 250:
            alpha = 255 - arr[..., :3].min(axis=2)
            safe = np.maximum(alpha, 1)[..., None] / 255
            rgb = np.clip((arr[..., :3] - (1 - safe) * 255) / safe, 0, 255)
            arr = np.dstack([rgb, alpha])
        ys, xs = np.nonzero(arr[..., 3] > 10)
        arr = arr[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
        im = Image.fromarray(arr.round().astype('uint8'), 'RGBA')
        if max(im.size) > 160:
            f = 160 / max(im.size)
            im = im.resize((round(im.size[0] * f), round(im.size[1] * f)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, 'PNG', optimize=True)
        res = dict(kind='png', aspect=im.size[0] / im.size[1], b64=base64.b64encode(buf.getvalue()).decode('ascii'))
    _icons[key] = res
    return res


def icon_size(key, size):
    """Width and height of a logo fitted to a box of height `size` and width 1.36 x size, as in the paper's tables."""
    ic = _load_icon(key)
    if ic is None:
        return 0, 0
    h = min(size, 1.36 * size / ic['aspect'])
    return h * ic['aspect'], h


# ----- geometry helpers for the checks ----------------------------------------

def _pt_box(px, py, b):
    dx = max(b[0] - px, 0, px - b[2])
    dy = max(b[1] - py, 0, py - b[3])
    return math.hypot(dx, dy)


def _poly_box(pts, b):
    best = 1e9
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) / .25) + 1)
        for i in range(n + 1):
            t = i / n
            best = min(best, _pt_box(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, b))
    if len(pts) == 1:
        best = _pt_box(pts[0][0], pts[0][1], b)
    return best


class Svg:
    def __init__(self, name, w, h, label=''):
        self.name, self.w, self.h = name, w, h
        self.prefix = 'ch-' + re.sub(r'[^a-z0-9]+', '-', name.lower())
        self.label = label
        self.defs = []
        self.body = []
        self.boxes = []    # (x0, y0, x1, y1, text): ink boxes of labels and logos
        self.small = []    # spans below the 17 pt floor
        self.plots = []    # (x, y, size): compass areas whose rules labels must clear
        self.frames = []   # (x, y, w, h, pad): boxes whose text keeps `pad` clear of the border
        self.marks = []    # ('c', x, y, r) or ('p', points, half width): data marks labels must not touch
        self.lenses = []   # (cx, cy, r): magnifier insets
        self.overflow = False
        self._n = 0

    # ----- primitives -----------------------------------------------------
    def uid(self, stem='x'):
        self._n += 1
        return f'{self.prefix}-{stem}{self._n}'

    def add(self, s):
        self.body.append(s)

    def rect(self, x, y, w, h, fill='none', stroke=None, sw=.25, rx=0, opacity=None, extra=''):
        a = f'x="{fmt(x)}" y="{fmt(y)}" width="{fmt(w)}" height="{fmt(h)}" fill="{fill}"'
        if rx:
            a += f' rx="{fmt(rx)}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{fmt(sw)}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        self.add(f'<rect {a} {extra}/>')

    def line(self, x0, y0, x1, y1, stroke=HAIR, sw=.25, opacity=None, cap=None, extra=''):
        a = f'x1="{fmt(x0)}" y1="{fmt(y0)}" x2="{fmt(x1)}" y2="{fmt(y1)}" stroke="{stroke}" stroke-width="{fmt(sw)}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        if cap:
            a += f' stroke-linecap="{cap}"'
        self.add(f'<line {a} {extra}/>')

    def path(self, d, fill='none', stroke=None, sw=.3, opacity=None, join='round', cap='round', extra=''):
        a = f'd="{d}" fill="{fill}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{fmt(sw)}" stroke-linejoin="{join}" stroke-linecap="{cap}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        self.add(f'<path {a} {extra}/>')

    def circle(self, x, y, r, fill='none', stroke=None, sw=.25, opacity=None):
        a = f'cx="{fmt(x)}" cy="{fmt(y)}" r="{fmt(r)}" fill="{fill}"'
        if stroke:
            a += f' stroke="{stroke}" stroke-width="{fmt(sw)}"'
        if opacity is not None:
            a += f' opacity="{opacity}"'
        self.add(f'<circle {a}/>')

    def dot(self, x, y, r=1.25, fill=LLM, stroke=LLM_DEEP, sw=.32, ring=.32, ring_color='#FFFFFF', mark=True):
        """A mark with a surface ring, so it stays legible where it crosses lines."""
        if ring:
            self.circle(x, y, r + ring, fill=ring_color, opacity=.92)
        self.circle(x, y, r, fill=fill, stroke=stroke, sw=sw)
        if mark:
            self.marks.append(('c', x, y, r + ring))

    def hollow(self, x, y, r=1.25, stroke=LLM_DEEP, sw=.42, ring=.28, mark=True):
        if ring:
            self.circle(x, y, r + ring, fill='#FFFFFF', opacity=.92)
        self.circle(x, y, r, fill='#FFFFFF', stroke=stroke, sw=sw)
        if mark:
            self.marks.append(('c', x, y, r + ring))

    def text(self, x, y, s, size=LABEL, anchor='start', font='text', fill=INK, italic=False, weight=None,
             rotate=None, track=None, cls=None, register=True, caps=False):
        if size < MIN_TEXT:
            self.small.append((size, s))
        if font == 'data':
            font = 'num'
        fam = {'text': FONT_TEXT, 'num': FONT_NUM, 'display': FONT_DISPLAY}[font]
        a = f'x="{fmt(x)}" y="{fmt(y)}" font-family="{fam}" font-size="{fmt(size)}" fill="{fill}"'
        if anchor != 'start':
            a += f' text-anchor="{anchor}"'
        if italic:
            a += ' font-style="italic"'
        if weight:
            a += f' font-weight="{weight}"'
        if track:
            a += f' letter-spacing="{track:.3f}"'
        if font == 'display':
            a += ' style="font-variant-numeric:lining-nums"'
        elif caps:
            a += ' style="font-variant-caps:small-caps"'
        if rotate is not None:
            a += f' transform="rotate({fmt(rotate)} {fmt(x)} {fmt(y)})"'
        if cls:
            a += f' class="{cls}"'
        self.add(f'<text {a}>{escape(s)}</text>')
        adv = text_width(s, size, font, italic, weight, track or 0, caps=caps)
        if register:
            l, t, r, b = (0, -.69 * size, adv, .12 * size) if caps else ink_box(s, size, font, italic, weight, track or 0)
            x0 = x - (adv if anchor == 'end' else adv / 2 if anchor == 'middle' else 0)
            if rotate is None:
                self.boxes.append((x0 + l, y + t, x0 + r, y + b, s))
            elif abs(rotate + 90) < 1e-6:  # rotate(-90) about (x, y) maps (px, py) to (x + py - y, y - px + x)
                self.boxes.append((x + t, y - (x0 + r - x), x + b, y - (x0 + l - x), s))
        return adv

    def tspans(self, x, y, parts, size=LABEL, anchor='start', cls=None):
        """One line mixing fonts: parts = [(text, dict(font=, fill=, italic=, weight=, size=)), ...]"""
        total = sum(text_width(t, o.get('size', size), o.get('font', 'text'), o.get('italic', False), o.get('weight'))
                    for t, o in parts)
        x0 = x - (total if anchor == 'end' else total / 2 if anchor == 'middle' else 0)
        cur = x0
        ink = []
        for t, o in parts:
            sz, fnt, it, wt = o.get('size', size), o.get('font', 'text'), o.get('italic', False), o.get('weight')
            lead = len(t) - len(t.lstrip(' '))
            if lead:  # SVG collapses leading spaces, so advance by hand
                cur += text_width(' ' * lead, sz, fnt, it, wt)
                t = t[lead:]
            if t:
                core = t.rstrip(' ')
                l, tp, r, b = ink_box(core, sz, fnt, it, wt)
                ink.append((cur + l, y + tp, cur + r, y + b))
                cur += self.text(cur, y, core, size=sz, font=fnt, fill=o.get('fill', INK), italic=it, weight=wt, cls=cls, register=False)
                trail = len(t) - len(core)
                if trail:
                    cur += text_width(' ' * trail, sz, fnt, it, wt)
        if ink:
            self.boxes.append((min(b[0] for b in ink), min(b[1] for b in ink), max(b[2] for b in ink), max(b[3] for b in ink),
                               ''.join(t for t, _ in parts).strip()))
        return total

    def math(self, key, x, y, size=MATH, anchor='start', fill=INK, register=True):
        """TeX-set math (Latin Modern) with its baseline at y. Returns its width."""
        w, h, d = texkit.metrics(key, size)
        x0 = x - (w if anchor == 'end' else w / 2 if anchor == 'middle' else 0)
        self.add(texkit.drawing(key, x0, y, size, self.uid('m') + '-', fill))
        if size < MIN_TEXT:
            self.small.append((size, key))
        if register:
            self.boxes.append((x0, y - h, x0 + w, y + d, f'[math {key}]'))
        return w

    def icon(self, key, x, y, size, register=True):
        """Inline a model logo, vertically centred in a box of height `size` at (x, y). Returns its width.
        Until the assets agent's file exists, leave a named hook and reserve no space."""
        ic = _load_icon(key)
        if ic is None:
            self.add(f'<g data-icon-hook="{key}" data-x="{fmt(x)}" data-y="{fmt(y)}" data-size="{fmt(size)}"></g>')
            return 0
        w, h = icon_size(key, size)
        y0 = y + (size - h) / 2
        if register:
            self.boxes.append((x, y0, x + w, y0 + h, f'[logo {key}]'))
        if ic['kind'] == 'png':
            self.add(f'<image x="{fmt(x)}" y="{fmt(y0)}" width="{fmt(w)}" height="{fmt(h)}" href="data:image/png;base64,{ic["b64"]}"/>')
            return w
        inner = ic['inner']
        pref = self.uid('i')
        for i in set(re.findall(r'\bid="([^"]+)"', inner)):
            inner = inner.replace(f'id="{i}"', f'id="{pref}{i}"').replace(f'url(#{i})', f'url(#{pref}{i})').replace(f'href="#{i}"', f'href="#{pref}{i}"')
        self.add(f'<svg x="{fmt(x)}" y="{fmt(y0)}" width="{fmt(w)}" height="{fmt(h)}" viewBox="{ic["vb"]}">{inner}</svg>')
        return w

    def named(self, key, name, x, y, size=LABEL, anchor='start', fill=INK, italic=False, icon_scale=1.0, slot=None, track=None):
        """Text preceded by a model's logo. y is the text baseline. With `slot`, every logo gets the same width,
        so a column of names aligns."""
        s = size * 0.92 * icon_scale
        gap = size * .28
        wi, _ = icon_size(key, s)
        sw = slot if slot is not None else wi
        w_icon = sw + gap if sw else 0
        total = text_width(name, size, 'text', italic, None, track or 0) + w_icon
        x0 = x - (total if anchor == 'end' else total / 2 if anchor == 'middle' else 0)
        if wi:
            self.icon(key, x0 + (sw - wi) / 2, y - size * .74, s)
        self.text(x0 + w_icon, y, name, size=size, fill=fill, italic=italic, track=track)
        return total

    # ----- output ---------------------------------------------------------
    def check(self):
        out = []
        eps = .05
        for size, s in self.small:
            out.append(f'{self.name}: "{s}" is {size / PT:.1f} pt, below the 17 pt floor')
        B = self.boxes
        for i, (x0, y0, x1, y1, s) in enumerate(B):
            if x0 < -eps or y0 < -eps or x1 > self.w + eps or y1 > self.h + eps:
                out.append(f'{self.name}: "{s}" leaves the viewBox ({x0:.1f},{y0:.1f},{x1:.1f},{y1:.1f})')
            for a0, c0, a1, c1, t in B[i + 1:]:
                if x0 < a1 - eps and a0 < x1 - eps and y0 < c1 - eps and c0 < y1 - eps:
                    out.append(f'{self.name}: "{s}" overlaps "{t}"')
        for px, py, S in self.plots:
            xd, yd = px + S / 2, py + S / 2
            for x0, y0, x1, y1, s in B:
                if not (x1 > px and x0 < px + S and y1 > py and y0 < py + S):
                    continue
                clear = min(x0 - px, px + S - x1, y0 - py, py + S - y1)
                if x0 < xd < x1:
                    out.append(f'{self.name}: "{s}" crosses the vertical rule')
                else:
                    clear = min(clear, x0 - xd if x0 >= xd else xd - x1)
                if y0 < yd < y1:
                    out.append(f'{self.name}: "{s}" crosses the horizontal rule')
                else:
                    clear = min(clear, y0 - yd if y0 >= yd else yd - y1)
                if clear < INSET - 1e-6:
                    out.append(f'{self.name}: "{s}" is {clear:.2f} mm from a rule or edge (needs {INSET})')
        for x0, y0, x1, y1, s in B:
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            inside = [f for f in self.frames if f[0] <= cx <= f[0] + f[2] and f[1] <= cy <= f[1] + f[3]]
            if inside:
                fx, fy, fw, fh, pad = min(inside, key=lambda f: f[2] * f[3])
                clear = min(x0 - fx, fx + fw - x1, y0 - fy, fy + fh - y1)
                if clear < pad - 1e-6:
                    out.append(f'{self.name}: "{s}" has {clear:.2f} mm of padding (needs {pad})')
            for mk in self.marks:
                if mk[0] == 'c':
                    d = _pt_box(mk[1], mk[2], (x0, y0, x1, y1)) - mk[3]
                    where = f'mark at ({mk[1]:.1f}, {mk[2]:.1f})'
                else:
                    d = _poly_box(mk[1], (x0, y0, x1, y1)) - mk[2]
                    where = f'line from ({mk[1][0][0]:.1f}, {mk[1][0][1]:.1f}) to ({mk[1][-1][0]:.1f}, {mk[1][-1][1]:.1f})'
                if d < MARK_CLEAR:
                    out.append(f'{self.name}: "{s}" is {d:.2f} mm from a {where}')
            for lx, ly, lr in self.lenses:
                far = max(math.hypot(px - lx, py - ly) for px in (x0, x1) for py in (y0, y1))
                if far > lr - 1.0 and _pt_box(lx, ly, (x0, y0, x1, y1)) < lr + .3:
                    out.append(f'{self.name}: "{s}" touches the magnifier')
        return sorted(set(out), key=out.index)

    def render(self):
        defs = f'<defs>{"".join(self.defs)}</defs>' if self.defs else ''
        lab = f' role="img" aria-label="{escape(self.label)}"' if self.label else ' aria-hidden="true"'
        ovf = ' overflow="visible"' if self.overflow else ''
        return (f'<svg xmlns="http://www.w3.org/2000/svg" class="ch {self.prefix}" viewBox="0 0 {fmt(self.w)} {fmt(self.h)}" '
                f'width="{fmt(self.w)}mm" height="{fmt(self.h)}mm"{ovf}{lab}>{defs}{"".join(self.body)}</svg>\n')


# ----- compass --------------------------------------------------------------

def compass(s, x, y, size, rx=1.4, axis_sw=.3, frame_sw=.25, frame=True):
    """Draw the pastel political compass. Returns map(lrecon, galtan) -> (x_mm, y_mm)."""
    cid = s.uid('clip')
    s.defs.append(f'<clipPath id="{cid}"><rect x="{fmt(x)}" y="{fmt(y)}" width="{fmt(size)}" height="{fmt(size)}" rx="{fmt(rx)}"/></clipPath>')
    h = size / 2
    s.add(f'<g clip-path="url(#{cid})">')
    s.rect(x, y, h + .02, h + .02, fill=QUAD['auth_left'])
    s.rect(x + h, y, h, h + .02, fill=QUAD['auth_right'])
    s.rect(x, y + h, h + .02, h, fill=QUAD['lib_left'])
    s.rect(x + h, y + h, h, h, fill=QUAD['lib_right'])
    s.add('</g>')
    s.line(x + h, y, x + h, y + size, stroke=AXIS, sw=axis_sw, opacity=.8)
    s.line(x, y + h, x + size, y + h, stroke=AXIS, sw=axis_sw, opacity=.8)
    if frame:
        s.rect(x, y, size, size, stroke=AXIS, sw=frame_sw, rx=rx, opacity=.55)
    s.last_clip = cid
    s.plots.append((x, y, size))

    def m(u, v):
        return x + u * size, y + (1 - v) * size
    return m


# ----- curves and arrows ----------------------------------------------------

def _quad(p0, c, p1, t):
    a = (1 - t) ** 2
    b = 2 * (1 - t) * t
    d = t ** 2
    return a * p0[0] + b * c[0] + d * p1[0], a * p0[1] + b * c[1] + d * p1[1]


def _quad_tan(p0, c, p1, t):
    return (2 * (1 - t) * (c[0] - p0[0]) + 2 * t * (p1[0] - c[0]),
            2 * (1 - t) * (c[1] - p0[1]) + 2 * t * (p1[1] - c[1]))


def _subquad(p0, c, p1, t0, t1):
    a = _quad(p0, c, p1, t0)
    b = _quad(p0, c, p1, t1)
    q0 = (p0[0] + (c[0] - p0[0]) * t0, p0[1] + (c[1] - p0[1]) * t0)
    q1 = (c[0] + (p1[0] - c[0]) * t0, c[1] + (p1[1] - c[1]) * t0)
    r = (q0[0] + (q1[0] - q0[0]) * ((t1 - t0) / (1 - t0)), q0[1] + (q1[1] - q0[1]) * ((t1 - t0) / (1 - t0)))
    return a, r, b


def _t_at_distance(p0, c, p1, center, dist, from_end=False):
    """Parameter where the curve is `dist` from `center`, scanning from the near end."""
    ts = [i / 400 for i in range(401)]
    if from_end:
        ts = ts[::-1]
    for t in ts:
        q = _quad(p0, c, p1, t)
        if math.hypot(q[0] - center[0], q[1] - center[1]) >= dist:
            return t
    return ts[-1]


def arrow(s, a, b, bend=.15, r0=1.6, r1=1.6, stroke=LLM_DEEP, sw=.55, head=2.4, width=1.9, opacity=None, no_head=False, mark=True):
    """Curved arrow from a to b; the tip touches the target's edge at distance r1 from b.
    `mark=False` for leader lines, which labels may touch at their own end."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    c = ((a[0] + b[0]) / 2 - dy * bend, (a[1] + b[1]) / 2 + dx * bend)
    t0 = _t_at_distance(a, c, b, a, r0)
    t_tip = _t_at_distance(a, c, b, b, r1, from_end=True)
    tip = _quad(a, c, b, t_tip)
    if no_head:
        p, r, q = _subquad(a, c, b, t0, t_tip)
    else:
        t_base = _t_at_distance(a, c, b, b, r1 + head * .78, from_end=True)
        p, r, q = _subquad(a, c, b, t0, t_base)
    op = f' opacity="{opacity}"' if opacity is not None else ''
    s.add(f'<path d="M{fmt(p[0])} {fmt(p[1])}Q{fmt(r[0])} {fmt(r[1])} {fmt(q[0])} {fmt(q[1])}" fill="none" stroke="{stroke}" '
          f'stroke-width="{fmt(sw)}" stroke-linecap="round"{op}/>')
    if not no_head:
        tx, ty = _quad_tan(a, c, b, t_tip)
        n = math.hypot(tx, ty)
        tx, ty = tx / n, ty / n
        nx, ny = -ty, tx
        bx, by = tip[0] - tx * head, tip[1] - ty * head
        nb = (tip[0] - tx * head * .72, tip[1] - ty * head * .72)
        s.add(f'<path d="M{fmt(tip[0])} {fmt(tip[1])}L{fmt(bx + nx * width / 2)} {fmt(by + ny * width / 2)}'
              f'L{fmt(nb[0])} {fmt(nb[1])}L{fmt(bx - nx * width / 2)} {fmt(by - ny * width / 2)}Z" fill="{stroke}"{op}/>')
    if mark:
        s.marks.append(('p', [_quad(a, c, b, t0 + (t_tip - t0) * i / 24) for i in range(25)], sw / 2 + .05))
    mid = _quad(a, c, b, .5)
    mt = _quad_tan(a, c, b, .5)
    return dict(mid=mid, angle=math.degrees(math.atan2(mt[1], mt[0])), point=lambda t: _quad(a, c, b, t),
                tangent=lambda t: _quad_tan(a, c, b, t))


def connector(s, p0, p3, stroke, sw=.4, head=1.6, width=1.3, opacity=None, bulge=.5, axis=None, mark=True):
    """Cubic arrow that leaves p0 and enters p3 along one axis ('v' or 'h'; by default that of their larger
    separation), so it meets both box edges at a right angle. The tip touches p3 exactly; the shaft stops at the
    base of the small head."""
    dx, dy = p3[0] - p0[0], p3[1] - p0[1]
    if axis == 'v' or (axis is None and abs(dy) >= abs(dx)):
        p1, p2 = (p0[0], p0[1] + dy * bulge), (p3[0], p3[1] - dy * bulge)
        tan = (0, 1 if dy > 0 else -1)
    else:
        p1, p2 = (p0[0] + dx * bulge, p0[1]), (p3[0] - dx * bulge, p3[1])
        tan = (1 if dx > 0 else -1, 0)
    base = (p3[0] - tan[0] * head, p3[1] - tan[1] * head)
    p2b = (p2[0] - tan[0] * head * .5, p2[1] - tan[1] * head * .5) if p2 != p3 else p2
    op = f' opacity="{opacity}"' if opacity is not None else ''
    s.add(f'<path d="M{fmt(p0[0])} {fmt(p0[1])}C{fmt(p1[0])} {fmt(p1[1])} {fmt(p2b[0])} {fmt(p2b[1])} {fmt(base[0])} {fmt(base[1])}" '
          f'fill="none" stroke="{stroke}" stroke-width="{fmt(sw)}" stroke-linecap="butt"{op}/>')
    nx, ny = -tan[1], tan[0]
    s.add(f'<path d="M{fmt(p3[0])} {fmt(p3[1])}L{fmt(base[0] + nx * width / 2)} {fmt(base[1] + ny * width / 2)}'
          f'L{fmt(base[0] - nx * width / 2)} {fmt(base[1] - ny * width / 2)}Z" fill="{stroke}"{op}/>')
    if mark:
        pts = []
        for i in range(25):
            t = i / 24
            mt = 1 - t
            pts.append((mt ** 3 * p0[0] + 3 * mt * mt * t * p1[0] + 3 * mt * t * t * p2[0] + t ** 3 * p3[0],
                        mt ** 3 * p0[1] + 3 * mt * mt * t * p1[1] + 3 * mt * t * t * p2[1] + t ** 3 * p3[1]))
        s.marks.append(('p', pts, sw / 2 + .05))


# ----- smooth closed paths --------------------------------------------------

def rdp(points, eps):
    """Ramer-Douglas-Peucker simplification."""
    if len(points) < 3:
        return list(points)
    (x0, y0), (x1, y1) = points[0], points[-1]
    dx, dy = x1 - x0, y1 - y0
    n = math.hypot(dx, dy)
    dmax, idx = 0, 0
    for i in range(1, len(points) - 1):
        if n < 1e-9:  # a closed loop: measure from the shared endpoint
            d = math.hypot(points[i][0] - x0, points[i][1] - y0)
        else:
            d = abs(dy * (points[i][0] - x0) - dx * (points[i][1] - y0)) / n
        if d > dmax:
            dmax, idx = d, i
    if dmax <= eps:
        return [points[0], points[-1]]
    return rdp(points[:idx + 1], eps)[:-1] + rdp(points[idx:], eps)


def smooth_path(points, closed=True, tension=.5, nd=2):
    """Catmull-Rom spline through points, as cubic Beziers."""
    f = lambda v: (f'{v:.{nd}f}'.rstrip('0').rstrip('.') or '0')
    n = len(points)
    if n < 3:
        return 'M' + 'L'.join(f'{f(x)} {f(y)}' for x, y in points)
    d = [f'M{f(points[0][0])} {f(points[0][1])}']
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        if closed:
            p0, p1, p2, p3 = points[(i - 1) % n], points[i], points[(i + 1) % n], points[(i + 2) % n]
        else:
            p0, p1, p2, p3 = points[max(i - 1, 0)], points[i], points[i + 1], points[min(i + 2, n - 1)]
        k = tension / 3 * 2 / 2
        c1 = (p1[0] + (p2[0] - p0[0]) * k / 1.0 / 1.5, p1[1] + (p2[1] - p0[1]) * k / 1.0 / 1.5)
        c2 = (p2[0] - (p3[0] - p1[0]) * k / 1.0 / 1.5, p2[1] - (p3[1] - p1[1]) * k / 1.0 / 1.5)
        d.append(f'C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p2[0])} {f(p2[1])}')
    if closed:
        d.append('Z')
    return ''.join(d)


def poly_path(points, closed=True):
    d = 'M' + 'L'.join(f'{fmt(x)} {fmt(y)}' for x, y in points)
    return d + ('Z' if closed else '')


def bar_right(x, y, w, h, r=.9):
    """Horizontal bar: square at the baseline, rounded at the data end."""
    r = min(r, w, h / 2)
    return (f'M{fmt(x)} {fmt(y)}H{fmt(x + w - r)}A{fmt(r)} {fmt(r)} 0 0 1 {fmt(x + w)} {fmt(y + r)}'
            f'V{fmt(y + h - r)}A{fmt(r)} {fmt(r)} 0 0 1 {fmt(x + w - r)} {fmt(y + h)}H{fmt(x)}Z')
