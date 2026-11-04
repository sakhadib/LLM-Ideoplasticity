"""Build vector IUT and OIC logo files.

Emblem paths come untouched from the official IUT letterhead PDF (true vector).
A white backing silhouette (shield fill + halo, as on the user's earlier posters) is traced so the
emblem can sit on the coloured band. The white wordmark is traced with potrace from the alpha channel
of the lockup image used on the user's ACL 2023 and HaSPeR posters, keeping its exact letterforms and
placement.

Usage: python -I make_iut_lockup.py <letterhead.pdf> <ref_lockup.png> <pylibs_dir> <out_dir>
"""
import os
import sys

import numpy as np
import pymupdf
from PIL import Image
from scipy import ndimage

letterhead, ref_png, pylibs, out = sys.argv[1:5]
sys.path.append(pylibs)
import potrace  # noqa: E402  (potracer, pure Python)

os.makedirs(out, exist_ok=True)


def fmt(v):
    s = f'{v:.3f}'.rstrip('0').rstrip('.')
    return s if s else '0'


def hexcol(c):
    return '#%02x%02x%02x' % tuple(int(round(v * 255)) for v in c[:3])


def items_to_d(items, close):
    parts = []
    cur = None
    for it in items:
        op = it[0]
        if op == 'l':
            p1, p2 = it[1], it[2]
            if cur is None or abs(cur.x - p1.x) > 1e-4 or abs(cur.y - p1.y) > 1e-4:
                parts.append(f'M{fmt(p1.x)} {fmt(p1.y)}')
            parts.append(f'L{fmt(p2.x)} {fmt(p2.y)}')
            cur = p2
        elif op == 'c':
            p1, p2, p3, p4 = it[1], it[2], it[3], it[4]
            if cur is None or abs(cur.x - p1.x) > 1e-4 or abs(cur.y - p1.y) > 1e-4:
                parts.append(f'M{fmt(p1.x)} {fmt(p1.y)}')
            parts.append(f'C{fmt(p2.x)} {fmt(p2.y)} {fmt(p3.x)} {fmt(p3.y)} {fmt(p4.x)} {fmt(p4.y)}')
            cur = p4
        elif op == 're':
            r = it[1]
            parts.append(f'M{fmt(r.x0)} {fmt(r.y0)}H{fmt(r.x1)}V{fmt(r.y1)}H{fmt(r.x0)}Z')
            cur = None
        elif op == 'qu':
            q = it[1]
            parts.append(
                f'M{fmt(q.ul.x)} {fmt(q.ul.y)}L{fmt(q.ur.x)} {fmt(q.ur.y)}L{fmt(q.lr.x)} {fmt(q.lr.y)}L{fmt(q.ll.x)} {fmt(q.ll.y)}Z'
            )
            cur = None
        else:
            raise ValueError(op)
    if close:
        parts.append('Z')
    return ''.join(parts)


def drawing_to_svg(dr):
    attrs = []
    t = dr['type']
    if 'f' in t and dr.get('fill') is not None:
        attrs.append(f'fill="{hexcol(dr["fill"])}"')
        if dr.get('even_odd'):
            attrs.append('fill-rule="evenodd"')
        if dr.get('fill_opacity') not in (None, 1, 1.0):
            attrs.append(f'fill-opacity="{dr["fill_opacity"]:.3f}"')
    else:
        attrs.append('fill="none"')
    if 's' in t and dr.get('color') is not None:
        attrs.append(f'stroke="{hexcol(dr["color"])}"')
        attrs.append(f'stroke-width="{fmt(dr.get("width") or 0.1)}"')
        caps = dr.get('lineCap')
        if caps:
            attrs.append('stroke-linecap="%s"' % {0: 'butt', 1: 'round', 2: 'square'}[int(caps[0])])
        join = dr.get('lineJoin')
        if join is not None:
            attrs.append('stroke-linejoin="%s"' % {0: 'miter', 1: 'round', 2: 'bevel'}[int(join)])
        if dr.get('stroke_opacity') not in (None, 1, 1.0):
            attrs.append(f'stroke-opacity="{dr["stroke_opacity"]:.3f}"')
    return f'<path {" ".join(attrs)} d="{items_to_d(dr["items"], dr.get("closePath"))}"/>'


def trace(mask, turdsize=2, alphamax=1.0, opttolerance=0.2):
    # potracer treats False as the foreground it traces, so invert the mask here.
    bm = potrace.Bitmap(~mask)
    plist = bm.trace(turdsize=turdsize, turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY, alphamax=alphamax,
                     opticurve=True, opttolerance=opttolerance)
    return plist


def plist_to_d(plist, scale=1.0, dx=0.0, dy=0.0, sx=None):
    sx = scale if sx is None else sx

    def P(p):
        return f'{fmt(p.x * sx + dx)} {fmt(p.y * scale + dy)}'
    parts = []
    for curve in plist:
        parts.append('M' + P(curve.start_point))
        for seg in curve.segments:
            if seg.is_corner:
                parts.append('L' + P(seg.c) + 'L' + P(seg.end_point))
            else:
                parts.append('C' + P(seg.c1) + ' ' + P(seg.c2) + ' ' + P(seg.end_point))
        parts.append('Z')
    return ''.join(parts)


# The letterhead emblem is squeezed about 5% horizontally compared with the logo the user supplied and their
# earlier posters (green bounding box 0.569 vs 0.597), so all outputs apply this x-stretch. See MANIFEST.md.
SX = 1.05

# ---- Letterhead: vector emblems ------------------------------------------------------------------
doc = pymupdf.open(letterhead)
page = doc[0]
draws = page.get_drawings()
iut = [d for d in draws if d['rect'].x1 < 150 and d['rect'].y1 < 150]
oic = [d for d in draws if d['rect'].x0 > 470 and d['rect'].y1 < 150]
print('iut drawings', len(iut), 'oic drawings', len(oic), 'other', len(draws) - len(iut) - len(oic))


def bbox(ds, pad_stroke=True):
    x0 = min(d['rect'].x0 for d in ds)
    y0 = min(d['rect'].y0 for d in ds)
    x1 = max(d['rect'].x1 for d in ds)
    y1 = max(d['rect'].y1 for d in ds)
    return x0, y0, x1, y1


ib = bbox(iut)
ob = bbox(oic)
print('iut bbox', [round(v, 2) for v in ib], 'oic bbox', [round(v, 2) for v in ob])
iut_paths = '\n'.join(drawing_to_svg(d) for d in iut)
oic_paths = '\n'.join(drawing_to_svg(d) for d in oic)


def write_svg(path, vb, body, comment):
    w, h = vb[2], vb[3]
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{fmt(vb[0])} {fmt(vb[1])} {fmt(w)} {fmt(h)}">\n')
        f.write(f'<!-- {comment} -->\n')
        f.write(body)
        f.write('\n</svg>\n')
    print('wrote', path, os.path.getsize(path))


pad = 0.3
write_svg(os.path.join(out, 'iut_emblem.svg'),
          (ib[0] * SX - pad, ib[1] - pad, (ib[2] - ib[0]) * SX + 2 * pad, ib[3] - ib[1] + 2 * pad),
          f'<g transform="scale({SX} 1)">\n{iut_paths}\n</g>',
          'IUT emblem, vector paths from the official IUT letterhead PDF, x-stretched 5% to the logo proportions. Transparent interior: for white grounds.')
write_svg(os.path.join(out, 'oic_emblem.svg'),
          (ob[0] - pad, ob[1] - pad, ob[2] - ob[0] + 2 * pad, ob[3] - ob[1] + 2 * pad),
          oic_paths, 'OIC emblem, vector paths from the official IUT letterhead PDF. Not placed by default.')

# ---- White backing silhouette -------------------------------------------------------------------
DPI = 1800
S = DPI / 72.0
clip = pymupdf.Rect(ib[0] - 4, ib[1] - 4, ib[2] + 4, ib[3] + 4)
pix = page.get_pixmap(matrix=pymupdf.Matrix(S * SX, S), clip=clip, alpha=False, colorspace=pymupdf.csGRAY)
arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
ink = arr < 200
print('silhouette raster', arr.shape, 'ink px', ink.sum())
lab, n = ndimage.label(~ink)
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
outside = np.isin(lab, list(border))
shape = ~outside
shape = ndimage.binary_fill_holes(shape)
print('holes-filled shape px', shape.sum(), 'white-region components', n)
emblem_w_px = (ib[2] - ib[0]) * S * SX
halo_px = 0.032 * emblem_w_px
dist = ndimage.distance_transform_edt(~shape)
dilated = dist <= halo_px
# Slight open/close so hairline nicks between ribbon and shield do not produce slivers
dilated = ndimage.binary_closing(dilated, iterations=int(0.004 * emblem_w_px) + 1)
dilated = ndimage.binary_fill_holes(dilated)
pl = trace(dilated, turdsize=200, alphamax=1.15, opttolerance=0.4)
# Back to letterhead (unstretched) coordinates so one group transform covers backing and emblem paths.
back_d = plist_to_d(pl, scale=1 / S, dx=clip.x0, dy=clip.y0, sx=1 / (S * SX))
ys, xs = np.where(dilated)
bx0, bx1 = xs.min() / (S * SX) + clip.x0, xs.max() / (S * SX) + clip.x0
by0, by1 = ys.min() / S + clip.y0, ys.max() / S + clip.y0
print('backing bbox pts', round(bx0, 2), round(by0, 2), round(bx1, 2), round(by1, 2), 'halo pt', round(halo_px / S, 3))
backing = f'<path fill="#ffffff" fill-rule="evenodd" d="{back_d}"/>'
write_svg(os.path.join(out, 'iut_emblem_band.svg'),
          (bx0 * SX - 0.2, by0 - 0.2, (bx1 - bx0) * SX + 0.4, by1 - by0 + 0.4),
          f'<g transform="scale({SX} 1)">\n{backing}\n{iut_paths}\n</g>',
          'IUT emblem for coloured grounds: official vector paths over a traced white backing (shield fill and halo).')

# ---- Reference lockup: wordmark trace ------------------------------------------------------------
ref = Image.open(ref_png).convert('RGBA')
alpha = np.asarray(ref.split()[3]).astype(float) / 255
H, W = alpha.shape
col = alpha.max(axis=0)
gaps = np.where(col < 0.05)[0]
# The widest transparent gap in the left third separates emblem and wordmark.
runs = np.split(gaps, np.where(np.diff(gaps) > 1)[0] + 1)
runs = [r for r in runs if len(r) and r[0] < W / 3 and r[0] > 50]
gap = max(runs, key=len)
split_x = int((gap[0] + gap[-1]) / 2)
print('emblem/wordmark split at x =', split_x, 'gap', gap[0], gap[-1])
UP = 4
word_alpha = alpha.copy()
word_alpha[:, :split_x] = 0
big = np.asarray(Image.fromarray((word_alpha * 255).astype(np.uint8)).resize((W * UP, H * UP), Image.BICUBIC)).astype(float) / 255
big = ndimage.gaussian_filter(big, sigma=0.8)
pl = trace(big >= 0.5, turdsize=40, alphamax=1.0, opttolerance=0.35)
word_d = plist_to_d(pl, scale=1 / UP)
print('word paths', len(pl))
write_svg(os.path.join(out, 'iut_wordmark_white.svg'),
          (split_x, 0, W - split_x, H),
          f'<path fill="#ffffff" fill-rule="evenodd" d="{word_d}"/>',
          'ISLAMIC UNIVERSITY OF TECHNOLOGY wordmark, traced from the lockup on the user\'s earlier posters.')

# ---- Compose the lockup in the reference's pixel frame ----------------------------------------------
emb_alpha = alpha[:, :split_x]
ys, xs = np.where(emb_alpha > 0.5)
rx0, rx1, ry0, ry1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
print('reference emblem bbox px', rx0, ry0, rx1, ry1)
k = min((rx1 - rx0) / ((bx1 - bx0) * SX), (ry1 - ry0) / (by1 - by0))
cx_r, cy_r = (rx0 + rx1) / 2, (ry0 + ry1) / 2
cx_b, cy_b = (bx0 + bx1) / 2, (by0 + by1) / 2
tx, ty = cx_r - k * SX * cx_b, cy_r - k * cy_b
print('emblem scale', round(k, 4), 'translate', round(tx, 2), round(ty, 2))
body = (f'<g transform="translate({fmt(tx)} {fmt(ty)}) scale({k * SX:.5f} {k:.5f})">\n{backing}\n{iut_paths}\n</g>\n'
        f'<path fill="#ffffff" fill-rule="evenodd" d="{word_d}"/>')
write_svg(os.path.join(out, 'iut_lockup_white.svg'), (0, 0, W, H), body,
          'IUT lockup for coloured grounds: official vector emblem + traced white wordmark, in the arrangement of the user\'s earlier posters.')
