"""Generate the poster's QR card as a vector SVG. It decodes to the given URL.

Usage: python make_qr.py [url] [--pylibs DIR] [--compact-top U] [--compact-bottom U] [--compact-label U] [--compact-radius U]
Defaults to the project page. Writes poster/assets/qr/qr_card.svg (ink frame, like the "SCAN ME" card on the
ACL 2023 poster), qr_card_white.svg (white card, band-coloured modules, like the HaSPeR code), qr_card_white_compact.svg
(the white card with a trimmed top margin and SCAN ME zone, about 100 mm tall at 96 mm wide) and qr_modules.svg.
Card units are about 1 mm at the poster's 96 mm print width.
"""
import argparse
import base64
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.dirname(HERE)

ap = argparse.ArgumentParser()
ap.add_argument('url', nargs='?', default='https://sakhadib.github.io/LLM-Ideoplasticity/')
ap.add_argument('--pylibs', default=os.environ.get('POSTER_PYLIBS', r'C:\Users\rifat\AppData\Local\Temp\claude\c--Users-rifat-Desktop-GitHub-LLM-Ideoplasticity\e7e551d2-b5db-4696-b913-c2aad2b77245\scratchpad\pylibs'))
ap.add_argument('--compact-top', type=float, default=4.95, help='white margin above the code (about 2.5 modules)')
ap.add_argument('--compact-bottom', type=float, default=13.85, help='zone below the code, SCAN ME included')
ap.add_argument('--compact-label', type=float, default=7.4, help='SCAN ME size')
ap.add_argument('--compact-radius', type=float, default=1.98, help='corner radius (2 mm at print size)')
ap.add_argument('--label-font', default='LMMonoPoster-Regular.ttf', help="SCAN ME font in assets/fonts (LaTeX's \texttt look)")
args = ap.parse_args()
sys.path.append(args.pylibs)
import segno  # noqa: E402
from fontTools.pens.boundsPen import BoundsPen  # noqa: E402
from fontTools.pens.svgPathPen import SVGPathPen  # noqa: E402
from fontTools.pens.transformPen import TransformPen  # noqa: E402
from fontTools.ttLib import TTFont  # noqa: E402

qr = segno.make(args.url, error='H', micro=False, boost_error=False)
matrix = [list(map(bool, row)) for row in qr.matrix]
N = len(matrix)
print('url', args.url, '| version', qr.version, '| error', qr.error, '| modules', N, '| mask', qr.mask)

# Clear a centred square for the logo. Must stay well below what level H can recover (30% of codewords).
BACK = 9 if N >= 37 else 7
if (BACK % 2) != (N % 2):
    BACK += 1
lo = (N - BACK) // 2
hi = lo + BACK
for r in range(lo, hi):
    for c in range(lo, hi):
        matrix[r][c] = False
print('cleared', BACK, 'x', BACK, 'modules =', round(100 * BACK * BACK / (N * N), 1), '% of the symbol')
LOGO_FRACTION = min(0.18, (BACK - 1.0) / N)


def outlines(m, r_convex=0.26, r_concave=0.12):
    """Union the dark modules into closed outlines with lightly rounded corners, so no seams can appear in print."""
    n = len(m)
    out = {}

    def add(a, b):
        out.setdefault(a, []).append(b)

    for r in range(n):
        for c in range(n):
            if not m[r][c]:
                continue
            # Clockwise on screen; an edge is kept only if the neighbour across it is light.
            if r == 0 or not m[r - 1][c]:
                add((c, r), (c + 1, r))
            if c == n - 1 or not m[r][c + 1]:
                add((c + 1, r), (c + 1, r + 1))
            if r == n - 1 or not m[r + 1][c]:
                add((c + 1, r + 1), (c, r + 1))
            if c == 0 or not m[r][c - 1]:
                add((c, r + 1), (c, r))
    parts = []
    while out:
        start = next(iter(out))
        loop = [start]
        cur = start
        prev_dir = None
        while True:
            nexts = out[cur]
            if len(nexts) == 1 or prev_dir is None:
                nxt = nexts.pop(0)
            else:
                # Diagonal contact: take the right turn so that each cell's outline stays separate.
                best = None
                for cand in nexts:
                    d = (cand[0] - cur[0], cand[1] - cur[1])
                    cross = prev_dir[0] * d[1] - prev_dir[1] * d[0]
                    if best is None or cross > best[0]:
                        best = (cross, cand)
                nxt = best[1]
                nexts.remove(nxt)
            if not nexts:
                del out[cur]
            prev_dir = (nxt[0] - cur[0], nxt[1] - cur[1])
            cur = nxt
            if cur == start:
                break
            loop.append(cur)
        # Merge collinear points
        pts = []
        k = len(loop)
        for i in range(k):
            a, b, c2 = loop[i - 1], loop[i], loop[(i + 1) % k]
            d1 = (b[0] - a[0], b[1] - a[1])
            d2 = (c2[0] - b[0], c2[1] - b[1])
            if d1[0] * d2[1] - d1[1] * d2[0] != 0:
                pts.append(b)
        k = len(pts)
        seg = []
        for i in range(k):
            a, b, c2 = pts[i - 1], pts[i], pts[(i + 1) % k]
            la = abs(b[0] - a[0]) + abs(b[1] - a[1])
            lb = abs(c2[0] - b[0]) + abs(c2[1] - b[1])
            d1 = ((b[0] - a[0]) / la, (b[1] - a[1]) / la)
            d2 = ((c2[0] - b[0]) / lb, (c2[1] - b[1]) / lb)
            cross = d1[0] * d2[1] - d1[1] * d2[0]
            rad = r_convex if cross > 0 else r_concave
            rad = min(rad, la / 2, lb / 2)
            p0 = (b[0] - d1[0] * rad, b[1] - d1[1] * rad)
            p1 = (b[0] + d2[0] * rad, b[1] + d2[1] * rad)
            seg.append((p0, b, p1))
        d = f'M{seg[0][2][0]:.3g} {seg[0][2][1]:.3g}'
        for i in range(1, k + 1):
            p0, ctrl, p1 = seg[i % k]
            d += f'L{p0[0]:.3g} {p0[1]:.3g}Q{ctrl[0]} {ctrl[1]} {p1[0]:.3g} {p1[1]:.3g}'
        parts.append(d + 'Z')
    return ''.join(parts)


module_d = outlines(matrix)

logo_path = os.path.join(ASSETS, 'logos', 'project_logo_qr.png')
logo_b64 = base64.b64encode(open(logo_path, 'rb').read()).decode('ascii')

jb = TTFont(os.path.join(ASSETS, 'fonts', args.label_font))
gs = jb.getGlyphSet()
cmap = jb.getBestCmap()
upem = jb['head'].unitsPerEm


def text_path(txt, size, cx, baseline, tracking=0.14):
    scale = size / upem
    advs = [gs[cmap[ord(ch)]].width * scale + tracking * size for ch in txt]
    width = sum(advs) - tracking * size
    x = cx - width / 2
    d = ''
    for ch, adv in zip(txt, advs):
        pen = SVGPathPen(gs, ntos=lambda v: f'{v:.3f}'.rstrip('0').rstrip('.'))
        gs[cmap[ord(ch)]].draw(TransformPen(pen, (scale, 0, 0, -scale, x, baseline)))
        d += pen.getCommands()
        x += adv
    return d


def card(path, frame_col, label_col, module_col, label_on_frame=True, comment=''):
    W = 95.0                # mm-like units; the SVG scales freely
    F = 2.4 if label_on_frame else 0.0
    QUIET = 4
    inner_w = W - 2 * F
    m = inner_w / (N + 2 * QUIET)
    qr_w = m * N
    label_h = 15.0
    H = F + inner_w + label_h + (0 if label_on_frame else 0)
    ox = F + m * QUIET
    oy = F + m * QUIET
    logo_w = qr_w * LOGO_FRACTION
    lx = ox + (qr_w - logo_w) / 2
    ly = oy + (qr_w - logo_w) / 2
    if label_on_frame:
        body = f'<rect width="{W}" height="{H:.3f}" rx="5" fill="{frame_col}"/>'
        body += f'<rect x="{F}" y="{F}" width="{inner_w}" height="{inner_w}" rx="3" fill="#ffffff"/>'
    else:
        body = f'<rect width="{W}" height="{H:.3f}" rx="5" fill="#ffffff"/>'
    body += f'<g transform="translate({ox:.4f} {oy:.4f}) scale({m:.5f})"><path fill="{module_col}" d="{module_d}"/></g>'
    # White rounded backing under the logo, inside the cleared square
    bk = m * (BACK - 0.6)
    bx = ox + (qr_w - bk) / 2
    body += f'<rect x="{bx:.3f}" y="{oy + (qr_w - bk) / 2:.3f}" width="{bk:.3f}" height="{bk:.3f}" rx="{m * 1.2:.3f}" fill="#ffffff"/>'
    body += f'<image x="{lx:.3f}" y="{ly:.3f}" width="{logo_w:.3f}" height="{logo_w:.3f}" href="data:image/png;base64,{logo_b64}"/>'
    baseline = F + inner_w + label_h * (0.72 if label_on_frame else 0.58)
    body += f'<path fill="{label_col}" d="{text_path("SCAN ME", 9.2, W / 2, baseline)}"/>'
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H:.3f}">\n<!-- {comment} Target: {args.url} -->\n{body}\n</svg>\n')
    print('wrote', path, os.path.getsize(path) // 1024, 'KB', 'module', round(m, 3), 'of', W, 'wide; aspect', round(W / H, 3), 'logo', round(100 * logo_w / qr_w, 1), '% of QR width')


def card_compact(path, module_col, label_col, top, bottom, label, radius, comment=''):
    """The white card with the side quiet zones kept (4 modules) and a trimmed top margin and label zone."""
    W = 95.0
    m = W / (N + 8)
    qr_w = m * N
    ox, oy = 4 * m, top
    H = top + qr_w + bottom
    body = f'<rect width="{W}" height="{H:.3f}" rx="{radius}" fill="#ffffff"/>'
    body += f'<g transform="translate({ox:.4f} {oy:.4f}) scale({m:.5f})"><path fill="{module_col}" d="{module_d}"/></g>'
    bk = m * (BACK - 0.6)
    body += f'<rect x="{ox + (qr_w - bk) / 2:.3f}" y="{oy + (qr_w - bk) / 2:.3f}" width="{bk:.3f}" height="{bk:.3f}" rx="{m * 1.2:.3f}" fill="#ffffff"/>'
    logo_w = qr_w * LOGO_FRACTION
    body += f'<image x="{ox + (qr_w - logo_w) / 2:.3f}" y="{oy + (qr_w - logo_w) / 2:.3f}" width="{logo_w:.3f}" height="{logo_w:.3f}" href="data:image/png;base64,{logo_b64}"/>'
    cap = 0.73 * label  # JetBrains Mono cap height
    baseline = oy + qr_w + (bottom + cap) / 2 + 0.25
    body += f'<path fill="{label_col}" d="{text_path("SCAN ME", label, W / 2, baseline)}"/>'
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H:.3f}">\n<!-- {comment} Target: {args.url} -->\n{body}\n</svg>\n')
    print('wrote', path, 'aspect', round(W / H, 3), '| top margin', round(top / m, 2), 'modules | gap code to label',
          round((baseline - cap - oy - qr_w) / m, 2), 'modules | height at 96 mm wide', round(H * 96 / W, 1), 'mm')


os.makedirs(os.path.join(ASSETS, 'qr'), exist_ok=True)
card(os.path.join(ASSETS, 'qr', 'qr_card.svg'), '#111827', '#ffffff', '#111827', True, 'Ink frame, modelled on the SCAN ME card of the ACL 2023 poster.')
card(os.path.join(ASSETS, 'qr', 'qr_card_white.svg'), '#ffffff', '#5445B5', '#5445B5', False, 'White card with band-coloured modules (7.25:1), modelled on the HaSPeR code.')
card_compact(os.path.join(ASSETS, 'qr', 'qr_card_white_compact.svg'), '#5445B5', '#5445B5', args.compact_top, args.compact_bottom,
             args.compact_label, args.compact_radius, 'Compact white card for the band: trimmed top margin and SCAN ME zone, 2 mm corners.')
with open(os.path.join(ASSETS, 'qr', 'qr_modules.svg'), 'w', encoding='utf-8', newline='\n') as f:
    Q = 4
    f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-Q} {-Q} {N + 2 * Q} {N + 2 * Q}">\n<rect x="{-Q}" y="{-Q}" width="{N + 2 * Q}" height="{N + 2 * Q}" fill="#fff"/>\n<path fill="#111827" d="{module_d}"/>\n</svg>\n')
