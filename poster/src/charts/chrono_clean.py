"""Clean copies of the paper's per-year 2D hull panels (the poster's Figure 3), without their axis text.

The source panels (poster/assets/figures/polytope_chrono_2d_{year}.svg) set every label, at 4-5 pt in DejaVu
Sans, as glyph <use> elements carrying a data-text attribute. Those, and the glyph definitions they reference,
are removed; hulls, points, crosses, axis lines and ticks stay. Each per-year file also holds all three panels
behind a cropped viewBox, so elements lying wholly outside the panel are dropped, and ids get a per-year prefix.
"""
import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / 'poster' / 'assets' / 'figures'
OUT = ROOT / 'poster' / 'charts'
SVG_NS, XLINK = 'http://www.w3.org/2000/svg', 'http://www.w3.org/1999/xlink'
ET.register_namespace('', SVG_NS)
ET.register_namespace('xlink', XLINK)
ET.register_namespace('inkscape', 'http://www.inkscape.org/namespaces/inkscape')
Q = lambda tag: f'{{{SVG_NS}}}{tag}'
HREF = f'{{{XLINK}}}href'

_NUM = re.compile(r'[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?')
_TOK = re.compile(r'[MmLlHhVvCcSsQqTtAaZz]|[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?')


def _matrix(t):
    """Affine matrix (a, b, c, d, e, f) of an SVG transform attribute (matrix and translate only)."""
    if not t:
        return (1, 0, 0, 1, 0, 0)
    m = re.match(r'\s*matrix\(([^)]*)\)\s*$', t)
    if m:
        return tuple(float(v) for v in _NUM.findall(m.group(1)))
    m = re.match(r'\s*translate\(([^)]*)\)\s*$', t)
    if m:
        v = [float(x) for x in _NUM.findall(m.group(1))] + [0]
        return (1, 0, 0, 1, v[0], v[1])
    raise ValueError(f'unhandled transform {t}')


def _mul(m, n):
    a, b, c, d, e, f = m
    A, B, C, D, E, F = n
    return (a * A + c * B, b * A + d * B, a * C + c * D, b * C + d * D, a * E + c * F + e, b * E + d * F + f)


def _path_points(d):
    """Every coordinate the path visits, control points included (a superset of its extent)."""
    pts, cx, cy, cmd = [], 0.0, 0.0, None
    toks = _TOK.findall(d)
    i = 0
    nargs = {'M': 2, 'L': 2, 'T': 2, 'H': 1, 'V': 1, 'C': 6, 'S': 4, 'Q': 4, 'A': 7, 'Z': 0}
    while i < len(toks):
        if re.match(r'[A-Za-z]', toks[i]):
            cmd = toks[i]
            i += 1
            if cmd in 'Zz':
                continue
        if cmd is None:
            raise ValueError('path data without a command')
        up = cmd.upper()
        n = nargs[up]
        vals = [float(v) for v in toks[i:i + n]]
        i += n
        rel = cmd.islower()
        if up == 'H':
            cx = vals[0] + (cx if rel else 0)
        elif up == 'V':
            cy = vals[0] + (cy if rel else 0)
        elif up == 'A':
            cx, cy = vals[5] + (cx if rel else 0), vals[6] + (cy if rel else 0)
        else:
            for j in range(0, n, 2):
                px, py = vals[j] + (cx if rel else 0), vals[j + 1] + (cy if rel else 0)
                pts.append((px, py))
            cx, cy = pts[-1]
        pts.append((cx, cy))
        if up == 'M':
            cmd = 'l' if rel else 'L'
    return pts


def _bbox(el, m):
    """Extent of an element in root coordinates, or None if it draws nothing."""
    m = _mul(m, _matrix(el.get('transform')))
    pts = []
    if el.tag == Q('path') and el.get('d'):
        for x, y in _path_points(el.get('d')):
            pts.append((m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5]))
    boxes = [b for b in (_bbox(ch, m) for ch in el) if b]
    if pts:
        xs, ys = zip(*pts)
        boxes.append((min(xs), min(ys), max(xs), max(ys)))
    if not boxes:
        return None
    return (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))


def clean(year, margin=4.0):
    src = SRC / f'polytope_chrono_2d_{year}.svg'
    tree = ET.parse(src)
    root = tree.getroot()
    vb = [float(v) for v in root.get('viewBox').split()]
    view = (vb[0] - margin, vb[1] - margin, vb[0] + vb[2] + margin, vb[1] + vb[3] + margin)
    defs = root.find(Q('defs'))
    stats = dict(text_uses=0, dropped=0, kept=0)

    def strip_text(parent):
        for ch in list(parent):
            if ch.tag == Q('use') and ch.get('data-text') is not None and (ch.get(HREF) or '').startswith('#font_'):
                parent.remove(ch)
                stats['text_uses'] += 1
            else:
                strip_text(ch)

    for ch in list(root):
        if ch is defs:
            continue
        if ch.tag == Q('use') and ch.get('data-text') is not None:
            root.remove(ch)
            stats['text_uses'] += 1
            continue
        strip_text(ch)
        b = _bbox(ch, (1, 0, 0, 1, 0, 0))
        if b is None or b[2] < view[0] or b[0] > view[2] or b[3] < view[1] or b[1] > view[3]:
            root.remove(ch)
            stats['dropped'] += 1
        else:
            stats['kept'] += 1
    body = ET.tostring(root, encoding='unicode')
    used = set(re.findall(r'url\(#([^)]+)\)', body)) | set(re.findall(r'href="#([^"]+)"', body))
    for ch in list(defs):
        if ch.get('id') not in used:
            defs.remove(ch)
    prefix = f'cy{year}-'
    out = ET.tostring(root, encoding='unicode')
    ids = set(re.findall(r'\bid="([^"]+)"', out))
    out = re.sub(r'\bid="([^"]+)"', lambda m: f'id="{prefix}{m.group(1)}"', out)
    out = re.sub(r'url\(#([^)]+)\)', lambda m: f'url(#{prefix}{m.group(1)})' if m.group(1) in ids else m.group(0), out)
    out = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{prefix}{m.group(1)}"' if m.group(1) in ids else m.group(0), out)
    if re.search(r'data-text=', out):
        raise RuntimeError('text glyphs survived cleaning')
    dst = OUT / f'chrono_2d_{year}.svg'
    dst.write_text(out + '\n', encoding='utf-8', newline='\n')
    stats.update(src_kb=src.stat().st_size // 1024, out_kb=dst.stat().st_size // 1024, viewBox=root.get('viewBox'))
    return dst, stats


def clean_all():
    return {year: clean(year) for year in (2009, 2014, 2019)}


if __name__ == '__main__':
    for year, (dst, st) in clean_all().items():
        print(year, dst.name, st)
