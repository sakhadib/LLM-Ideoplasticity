"""Generate every poster chart as an inline-safe SVG fragment.

    python poster/src/charts/build_charts.py

Geometry is in millimetres at print size, and every chart is meant to print at 1:1, so its type keeps the 17 pt floor.
Words are Pagella (variable names in italic), numerals Latin Modern Roman, and math is TeX-set Latin Modern (texkit).
Cyan marks are human parties, magenta marks are LLMs. Numbers come from facts.py, which verifies them against the
paper. Svg.check() reports any span below 17 pt, any in-plot label within 1.5 mm of a rule, and any collision.
"""
import ast
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.spatial import ConvexHull
from scipy.stats import gaussian_kde
from skimage.measure import find_contours

sys.path.insert(0, str(Path(__file__).resolve().parent))
import chrono_clean  # noqa: E402
import facts as FX  # noqa: E402
import texkit  # noqa: E402
from svgkit import (AXIS, HAIR, HI_AMP, HI_STAB, ICON_DIR, INK, INSET, LABEL, LAV, LLM, LLM_DARK, LLM_DEEP,  # noqa: E402
                    LOGO_CONTOURS, MATH, MUTED, NUM, PARTY_DEEP, PARTY_TEXT, Svg, arrow, bar_right, compass, connector,
                    fit_track, fmt, icon_size, ink_box, poly_path, rdp, smooth_path, text_width)

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'poster' / 'charts'
DATA = ROOT / 'poster' / 'data'
SP_PREVIEW = Path(r'C:/Users/rifat/AppData/Local/Temp/claude/c--Users-rifat-Desktop-GitHub-LLM-Ideoplasticity/'
                  r'e7e551d2-b5db-4696-b913-c2aad2b77245/scratchpad/chart_prev')

# 'paper' follows section 4.4 of the paper (the ten-model file, see discrepancies.md); 'nine' uses the cohort only.
LDS_BASIS = 'paper'

NAMES = FX.MODEL_NAMES
SHORT = FX.POSTER_SHORT
ICONS = FX.MODEL_ICON
LANG = {'Bengali': 'Bangla', 'Mandarin (Simplified)': 'Mandarin'}
C = 75                 # side of the card compasses
CW = C + .4            # their SVGs are square: 0.2 mm of air on every side
CAP = LABEL            # captions hold the 17 pt floor too
HEAD = 19 * .3528      # 19 pt matrix headers
NUM18 = 18 * .3528     # 18 pt matrix numerals
TRACK_TINT = '#D6F1FD'  # #74D2FA at 30%, for the party reference tracks
# Interiors of a card compass's quadrants after the 1.5 mm inset, for a compass at (.2, .2)
LO_IN, HI_IN = .2 + INSET + .05, .2 + C / 2 - INSET - .05      # left (or top) quadrant
LO_IN2, HI_IN2 = .2 + C / 2 + INSET + .05, .2 + C - INSET - .05  # right (or bottom) quadrant


def lang(name):
    return LANG.get(name, name)


def caption(s, x, y, text, anchor='middle', icon_key=None):
    if anchor == 'start':
        x += .3  # italic overhangs stay inside the viewBox
    s.add('<g class="ch-caption">')
    if icon_key:
        s.named(icon_key, text, x, y, size=CAP, anchor=anchor, fill=MUTED, italic=True)
    else:
        s.text(x, y, text, size=CAP, anchor=anchor, fill=MUTED, italic=True)
    s.add('</g>')


def _tag(s, key, name, year, x=LO_IN, y=6.4, room=None):
    """Model in italic and, beneath it, logo and year: a quiet key inside an empty quadrant. The name tightens
    only as far as the quadrant needs to keep 1.5 mm clear of its rules."""
    room = room if room is not None else HI_IN - LO_IN
    s.text(x, y, name, italic=True, track=fit_track(name, LABEL, room, italic=True))
    wi = s.icon(key, x, y + 6.6 - LABEL * .74, LABEL * .92)
    s.text(x + wi + 1.6, y + 6.6, year, italic=True, fill=MUTED)


def pts_from(row, prefix, n):
    return np.array([ast.literal_eval(row[f'{prefix}{i}']) for i in range(1, n + 1)])


def hdr_contours(xy, masses=(.9, .7, .5, .25), grid=280, lim=(-.2, 1.2), bw=None):
    """Highest-density-region contours of a Gaussian KDE; returns, per mass, polygons in data coordinates."""
    k = gaussian_kde(xy.T, bw_method=bw)
    g = np.linspace(lim[0], lim[1], grid)
    X, Y = np.meshgrid(g, g)
    Z = k(np.vstack([X.ravel(), Y.ravel()])).reshape(X.shape)
    z = np.sort(Z.ravel())[::-1]
    c = np.cumsum(z)
    c /= c[-1]
    out = []
    for m in masses:
        lev = z[np.searchsorted(c, m)]
        polys = []
        for p in find_contours(Z, lev):
            polys.append(np.c_[np.interp(p[:, 1], np.arange(grid), g), np.interp(p[:, 0], np.arange(grid), g)])
        out.append(polys)
    return out


def card_compass(name, label):
    s = Svg(name, CW, CW, label)
    s.overflow = True  # a mark on the frame keeps its ring
    return s, compass(s, .2, .2, C)


# ---------------------------------------------------------------------------------------------------------------------
# Thesis and key
# ---------------------------------------------------------------------------------------------------------------------

def point_to_shape(F, D, model='qwen', year=2009):
    S = 44
    W, H = 190, 59.4
    s = Svg('point_to_shape', W, H, 'One coordinate versus the contours of the same model across all contexts')
    pss = D['pss']
    base = pss[(pss.m == model) & (pss.year == year)][['lrecon_base', 'galtan_base']].iloc[0].values
    d = D['all']
    xy = d[(d.m == model) & (d.year == year)][['lrecon', 'galtan']].values
    x_a, x_b = 8, W - S - 8

    m = compass(s, x_a, 0.2, S)
    px, py = m(*base)
    s.circle(px, py, 1.8, fill=AXIS)
    s.text(x_a + S / 2, S + 6.5, 'a point', size=8.2, anchor='middle', font='display', italic=True)
    caption(s, x_a + S / 2, S + 13.7, 'neutral register only')

    m2 = compass(s, x_b, 0.2, S)
    s.add(f'<g clip-path="url(#{s.last_clip})">')
    for polys, col in zip(hdr_contours(xy), LOGO_CONTOURS):
        for poly in polys:
            pts = [m2(u, v) for u, v in poly]
            if len(pts) < 8:
                continue
            pts = rdp(pts + [pts[0]], .1)[:-1]
            s.path(smooth_path(pts), stroke=col, sw=.85)
    s.add('</g>')
    qx, qy = m2(*base)
    s.circle(qx, qy, 1.8, fill=AXIS)
    s.text(x_b + S / 2, S + 6.5, 'a shape', size=8.2, anchor='middle', font='display', italic=True)
    caption(s, x_b + S / 2, S + 13.7, f'{len(xy)} contexts pooled')

    # The arrow leaves the point's compass and stops 0.8 mm short of the shape's frame.
    a = (x_a + S + 1.0, 22)
    b = (x_b - .8, 22)
    arrow(s, a, b, bend=-.13, r0=0, r1=0, stroke=LAV[4], sw=.7, head=3.2, width=2.5, mark=False)
    mid = (a[0] + b[0]) / 2
    s.text(mid, 9.6, 'condition on context', anchor='middle', italic=True)
    s.named(ICONS[model], NAMES[model], mid, 30.2, anchor='middle')
    s.text(mid, 37.0, str(year), anchor='middle', fill=MUTED)
    F.setdefault('chart_choices', {})['point_to_shape'] = {
        'model': NAMES[model], 'year': year, 'baseline_C4': [float(base[0]), float(base[1])], 'n_points': int(len(xy)),
        'contours': 'Gaussian KDE (Scott) on (lrecon, galtan); 90/70/50/25% highest-density regions, clipped to the frame'}
    return s


def compass_legend(F, D):
    S = 46
    W, H = 61.6, 60.4
    X, Y = 13.4, .6
    s = Svg('compass_legend', W, H, 'Key to the political compass: lrecon on x, galtan on y')
    compass(s, X, Y, S)
    q = S / 4
    for (cx, cy, a, b) in ((X + q, Y + q, 'Auth-', 'Left'), (X + 3 * q, Y + q, 'Auth-', 'Right'),
                           (X + q, Y + 3 * q, 'Lib-', 'Left'), (X + 3 * q, Y + 3 * q, 'Lib-', 'Right')):
        s.text(cx, cy - .6, a, anchor='middle')
        s.text(cx, cy + 5.2, b, anchor='middle')
    yb = Y + S + 5.6
    s.text(X, yb, '0', font='num', fill=MUTED)
    s.text(X + S, yb, '1', anchor='end', font='num', fill=MUTED)
    s.text(X + S / 2, yb, 'lrecon', anchor='middle', italic=True)
    s.text(X + S / 2, yb + 6.4, 'left → right', anchor='middle', italic=True, fill=MUTED)
    xl = X - 2.4
    s.text(xl, Y + S, '0', font='num', fill=MUTED, rotate=-90)
    s.text(xl, Y, '1', anchor='end', font='num', fill=MUTED, rotate=-90)
    s.text(xl, Y + S / 2, 'galtan', anchor='middle', italic=True, rotate=-90)
    s.text(xl - 6.2, Y + S / 2, 'lib → auth', anchor='middle', italic=True, fill=MUTED, rotate=-90)
    return s


AXES6 = (('Register', 'PSS'), ('Paraphrase', 'PIS'), ('Reasoning', 'RSS'), ('Language', 'LDS'), ('Multi-Turn', 'DS'), ('Arg. Role', 'IAS'))


def pipeline(F, D):
    """The paper's Figure 2 with its structure and wording, at 17 pt. Math is TeX-set; the formula is part of the
    chart, so no overlay is needed."""
    ink, border, fill, deeper, flow = LAV[4], LAV[2], '#F3F2FD', '#E7E5FA', LAV[3]
    pad, lead, gap, bgap = 2.0, 1.2 * LABEL, 3.6, 1.5

    def ink_w(t, **k):
        b = ink_box(t, LABEL, **k)
        return b[2] - b[0]

    def asc(t, **k):
        return -ink_box(t, LABEL, **k)[1]

    def desc(t, **k):
        return ink_box(t, LABEL, **k)[3]

    bw = max(ink_w(a) for a, _ in AXES6) + 2 * pad + .1
    x_l = .2
    GW = 2 * pad + 3 * bw + 2 * bgap
    W = x_l + GW + .2
    cx = x_l + GW / 2
    boxes = []

    def box(x, y, w, h, f=fill):
        boxes.append((x, y, w, h, f))
        s.frames.append((x, y, w, h, pad))

    # Row A: the conditional distribution and its audit
    a1, d2 = asc('JBS Audit', weight=700), desc('precondition', italic=True)
    hA = pad + a1 + lead + d2 + pad
    fw_m, fh_m, fd_m = texkit.metrics('p_pos_ctx', MATH)
    fw = fw_m + 2 * pad + .1
    jw = max(ink_w('JBS Audit', weight=700), ink_w('precondition', italic=True)) + 2 * pad + .1
    jx = x_l + GW - jw
    yA = .2
    # Row B: the six contextual axes
    yG = yA + hA + gap
    an = max(asc(a) for a, _ in AXES6)
    db = max(desc(b, weight=700) for _, b in AXES6)
    hB = pad + an + lead + db + pad
    GH = pad + 2 * hB + bgap + pad
    # Row C and D: projection and coordinates
    vt = 'VAA → CHES Projection'
    yV = yG + GH + gap
    hV = pad + asc(vt) + desc(vt) + pad
    vw = ink_w(vt) + 2 * pad + .1
    tw_m, th_m, td_m = texkit.metrics('ches_tuple', MATH)
    yT = yV + hV + gap
    hT = pad + th_m + td_m + pad
    tw = tw_m + 2 * pad + .1
    # Row E: aggregate geometry and the score
    yE = yT + hT + 5.0
    ae = max(asc('Overton Width', weight=700), asc('Score', weight=700))
    de = max(desc('(OW)', weight=700), desc('Calculation', weight=700))
    hE = pad + ae + lead + de + pad
    ew = 47.0
    H = yE + hE + .2

    s = Svg('pipeline', W, H, 'Operational pipeline: the conditional distribution P(position | context) is gated by a JBS audit, '
                              'decomposed into six contextual axes, projected from VAA to CHES onto lrgen, lrecon and galtan, '
                              'which feeds Overton Width and the score')
    box(x_l, yA, fw, hA)
    box(jx, yA, jw, hA)
    box(x_l, yG, GW, GH, deeper)
    for i in range(6):
        box(x_l + pad + (i % 3) * (bw + bgap), yG + pad + (i // 3) * (hB + bgap), bw, hB)
    box(cx - vw / 2, yV, vw, hV)
    box(cx - tw / 2, yT, tw, hT)
    box(x_l, yE, ew, hE)
    box(x_l + GW - ew, yE, ew, hE)
    for x, y, w, h, f in boxes:
        s.rect(x, y, w, h, fill=f, stroke=border, sw=.35, rx=1.3)

    s.math('p_pos_ctx', x_l + fw / 2, yA + hA / 2 + (fh_m - fd_m) / 2, anchor='middle', fill=ink)
    s.text(jx + jw / 2, yA + pad + a1, 'JBS Audit', anchor='middle', weight=700, fill=ink)
    s.text(jx + jw / 2, yA + pad + a1 + lead, 'precondition', anchor='middle', italic=True, fill=ink)
    for i, (a, b) in enumerate(AXES6):
        bx = x_l + pad + (i % 3) * (bw + bgap)
        by = yG + pad + (i // 3) * (hB + bgap)
        s.text(bx + bw / 2, by + pad + an, a, anchor='middle', fill=ink)
        s.text(bx + bw / 2, by + pad + an + lead, b, anchor='middle', weight=700, fill=ink)
    s.text(cx, yV + pad + asc(vt), vt, anchor='middle', fill=ink)
    s.math('ches_tuple', cx, yT + pad + th_m, anchor='middle', fill=ink)
    for bx, a, b in ((x_l + ew / 2, 'Overton Width', '(OW)'), (x_l + GW - ew / 2, 'Score', 'Calculation')):
        s.text(bx, yE + pad + ae, a, anchor='middle', weight=700, fill=ink)
        s.text(bx, yE + pad + ae + lead, b, anchor='middle', weight=700, fill=ink)

    # Arrows meet every edge at a right angle and their tips land on it.
    connector(s, (x_l + fw, yA + hA / 2), (jx, yA + hA / 2), flow, mark=False)
    connector(s, (jx + jw / 2, yA + hA), (jx + jw / 2, yG), flow, mark=False)
    connector(s, (cx, yG + GH), (cx, yV), flow, mark=False)
    connector(s, (cx, yV + hV), (cx, yT), flow, mark=False)
    # The two branches leave the coordinates box just inside its ends and ease down onto the box centres.
    connector(s, (x_l + ew / 2 + 3.4, yT + hT), (x_l + ew / 2, yE), flow, axis='v', mark=False)
    connector(s, (x_l + GW - ew / 2 - 3.4, yT + hT), (x_l + GW - ew / 2, yE), flow, axis='v', mark=False)
    connector(s, (x_l + ew, yE + hE / 2), (x_l + GW - ew, yE + hE / 2), flow, opacity=.55, mark=False)
    return s


# ---------------------------------------------------------------------------------------------------------------------
# Six axes
# ---------------------------------------------------------------------------------------------------------------------

def pss_compass(F, D):
    s, m = card_compass('pss_compass', 'Gemma-4-26B in 2019: neutral baseline and three prompt registers')
    g = F['pss']['gemma_2019']
    base = m(*g['C4'])
    c1, c2, c3 = m(*g['C1']['xy']), m(*g['C2']['xy']), m(*g['C3']['xy'])
    arrow(s, base, c1, bend=.09, sw=.95, head=3.7, width=2.9, r0=2.0, r1=1.85)
    arrow(s, base, c2, bend=.30, sw=.5, r0=2.0, r1=1.55, head=2.6, width=2.0)
    arrow(s, base, c3, bend=-.30, sw=.5, r0=2.0, r1=1.55, head=2.6, width=2.0)
    s.dot(*c1, r=1.55)
    s.dot(*c2, r=1.3)
    s.dot(*c3, r=1.3)
    s.hollow(*base, r=1.7, sw=.6)
    _tag(s, 'gemma', SHORT['gemma'], '2019')
    s.text(c2[0] - 2.6, c2[1] + 2.0, 'Friend', anchor='end')
    s.text(c3[0] - 3.0, c3[1] + 5.4, 'Persuasive', anchor='end')
    s.text(HI_IN2, base[1] + 2.0, 'Neutral', anchor='end')
    s.text(LO_IN + .1, 63.0, 'Personal')
    s.text(LO_IN + .1, 69.2, 'blog')
    s.text(41.4, 65.6, '0.5721', size=NUM + 1.4, font='num', weight=700)
    s.text(41.4, 71.8, 'largest, 2D', italic=True, fill=MUTED)
    return s


def pss_bars(F, D):
    s = Svg('pss_bars', 140, 32, 'Mean PSS by prompt register')
    v = F['pss']['by_condition']
    rows = [('Persuasive', v['C3_persuasive'], True), ('Personal blog', v['C1_blog'], False), ('Friend', v['C2_friend'], False)]
    x0, scale, pitch, th = 39.8, 300, 7.6, 3.0
    for i, (lab, val, emph) in enumerate(rows):
        y = 1.4 + i * pitch
        s.text(x0 - 2.6, y + th / 2 + 2.05, lab, anchor='end')
        s.path(bar_right(x0, y, val * scale, th), fill=LLM_DEEP if emph else LLM)
        s.text(x0 + val * scale + 2.2, y + th / 2 + 1.95, f'{val:.4f}', font='num', fill=INK if emph else MUTED, weight=700 if emph else None)
    s.line(x0, 0, x0, 3 * pitch - 1.6, stroke=AXIS, sw=.25, opacity=.6)
    caption(s, 0, 29.6, 'Mean displacement by register, all models and years', anchor='start')
    return s


def pis_compass(F, D, year=2009):
    s, m = card_compass('pis_compass', 'Ten paraphrases: Qwen-Turbo disperses, Gemma-4-26B does not')
    ps = D['pis_scores']
    q = pts_from(ps[(ps.m == 'qwen') & (ps.year == year)].iloc[0], 'p', 10)[:, 1:]
    g = pts_from(ps[(ps.m == 'gemma') & (ps.year == year)].iloc[0], 'p', 10)[:, 1:]
    cq = q.mean(axis=0)
    cx, cy = m(*cq)
    for u, v in q:
        x, y = m(u, v)
        s.line(cx, cy, x, y, stroke=LLM_DEEP, sw=.28, opacity=.6)
    for u, v in q:
        s.dot(*m(u, v), r=1.1, ring=.22)
    s.path(f'M{fmt(cx - 1.3)} {fmt(cy)}H{fmt(cx + 1.3)}M{fmt(cx)} {fmt(cy - 1.3)}V{fmt(cy + 1.3)}', stroke=AXIS, sw=.42)
    gx, gy = m(*g[0])
    s.circle(gx, gy, 2.6, stroke=LLM_DEEP, sw=.28, fill='none')
    s.dot(gx, gy, r=1.4, ring=.2)
    s.marks.append(('c', gx, gy, 2.75))
    rp = m(*q[np.argmax(q[:, 0])])
    s.text(LO_IN, 6.4, 'Paraphrases')
    s.text(LO_IN, 13.0, f'×10, {year}', fill=MUTED)
    s.text(LO_IN2, 57.4, SHORT['qwen'], italic=True, track=fit_track(SHORT['qwen'], LABEL, HI_IN2 - LO_IN2, italic=True))
    s.named('qwen', 'ten points', LO_IN2, 64.0, italic=True, fill=MUTED)
    arrow(s, (LO_IN2 - .4, 55.6), rp, bend=-.16, r0=0, r1=1.45, stroke=AXIS, sw=.28, no_head=True, opacity=.75, mark=False)
    s.text(LO_IN2, 23.6, SHORT['gemma'], italic=True, track=fit_track(SHORT['gemma'], LABEL, HI_IN2 - LO_IN2, italic=True))
    s.named('gemma', 'one point', LO_IN2, 30.2, italic=True, fill=MUTED)
    arrow(s, (LO_IN2 + 4.4, 32.0), (gx, gy), bend=-.22, r0=0, r1=2.8, stroke=AXIS, sw=.28, no_head=True, opacity=.75, mark=False)
    F.setdefault('chart_choices', {})['pis_compass'] = {'year': year, 'qwen_centroid': cq.round(4).tolist(), 'gemma': g[0].round(4).tolist()}
    return s


def _ranked_two_col(s, rows, x_cols, n_left, scale, y0, pitch, label_w):
    """rows: (icon_key_or_None, label, value, emphasised, show_value). Two columns on one shared scale."""
    for i, (key, lab, val, emph, show) in enumerate(rows):
        col = 0 if i < n_left else 1
        r = i if col == 0 else i - n_left
        x = x_cols[col]
        y = y0 + r * pitch
        base = x + label_w[col]
        if key:
            s.named(key, lab, x, y + 2.0)
        else:
            s.text(x, y + 2.0, lab)
        w = val * scale
        if w > 0:
            s.line(base, y, base + w, y, stroke=LLM_DEEP if emph else LLM, sw=1.0 if emph else .8, cap='round')
            s.circle(base + w, y, 1.25, fill=LLM_DEEP if emph else LLM, stroke=LLM_DEEP, sw=.28)
        else:
            s.hollow(base, y, r=1.15, ring=0, sw=.42, mark=False)
        if show:
            s.text(base + w + 2.3, y + 1.95, f'{val:.4f}', font='num', fill=INK if emph else MUTED, weight=700 if emph else None)
    for col in (0, 1):
        n = n_left if col == 0 else len(rows) - n_left
        base = x_cols[col] + label_w[col]
        s.line(base, y0 - pitch / 2 + 1, base, y0 + (n - .5) * pitch - 1, stroke=AXIS, sw=.25, opacity=.6)


def pis_bars(F, D):
    s = Svg('pis_bars', 166, 38, 'Mean PIS for the nine models, sorted')
    t = F['table1']
    order = sorted(t, key=lambda k: -t[k]['pis'])
    rows = [(ICONS[k], SHORT[k], t[k]['pis'], k in ('qwen', 'gemma'), k in ('qwen', 'gemma')) for k in order]
    _ranked_two_col(s, rows, (0, 88), 5, 160, 2.8, 6.4, (48.5, 51))
    caption(s, 0, 36.0, f"Mean PIS across years; cohort mean {F['pis']['mean']:.4f}", anchor='start')
    return s


def pis_bars_tall(F, D):
    s = Svg('pis_bars_tall', 150, 66, 'Mean PIS for the nine models, sorted')
    t = F['table1']
    order = sorted(t, key=lambda k: -t[k]['pis'])
    x0, sc = 52, 1000
    pitch = 6.4
    for i, k in enumerate(order):
        y = 2.8 + i * pitch
        emph = k in ('qwen', 'gemma')
        s.named(ICONS[k], SHORT[k], 0, y + 2.0, slot=LABEL * .92 * 1.36)
        w = t[k]['pis'] * sc
        if w > 0:
            s.line(x0, y, x0 + w, y, stroke=LLM_DEEP if emph else LLM, sw=.8, cap='round')
            s.circle(x0 + w, y, 1.25, fill=LLM_DEEP if emph else LLM, stroke=LLM_DEEP, sw=.28)
        else:
            s.hollow(x0, y, r=1.15, ring=0, sw=.42, mark=False)
        if emph:
            s.text(x0 + w + 2.3, y + 1.95, f"{t[k]['pis']:.4f}", font='num', weight=700)
    s.line(x0, 0, x0, 2.8 + 8 * pitch + 2.4, stroke=AXIS, sw=.25, opacity=.6)
    caption(s, 0, 64.2, f"Mean PIS across years; cohort mean {F['pis']['mean']:.4f}", anchor='start')
    return s


def rss_compass(F, D, year=2019):
    s, m = card_compass('rss_compass', 'Gemini-2.5-Flash-Lite: direct paraphrases cluster tightly, chain-of-thought paraphrases spread out')
    ps = D['pis_scores']
    rs = D['rss_scores']
    direct = pts_from(ps[(ps.m == 'gemini') & (ps.year == year)].iloc[0], 'p', 10)[:, 1:]
    cot = pts_from(rs[(rs.m == 'gemini') & (rs.year == year)].iloc[0], 'p', 10)[:, 1:]
    dash = 'stroke-dasharray=".9 .6"'
    # chain of thought: filled points inside a solid outline
    hc = [m(*cot[i]) for i in ConvexHull(cot).vertices]
    s.path(poly_path(hc), fill=LLM, opacity=.28)
    s.path(poly_path(hc), stroke=LLM_DEEP, sw=.35)
    s.marks.append(('p', hc + [hc[0]], .2))
    # direct: hollow points inside a dashed outline
    hd = [m(*direct[i]) for i in ConvexHull(direct).vertices]
    s.path(poly_path(hd), stroke=LLM_DEEP, sw=.3, extra=dash)
    for u, v in cot:
        s.dot(*m(u, v), r=1.1, ring=.2)
    for u, v in direct:
        s.hollow(*m(u, v), r=.95, ring=.12, sw=.38)

    # A x3 magnifier on the direct cluster, in the empty Lib-Right quadrant, styled like the DS card's
    dc = direct.mean(axis=0)
    src = m(*dc)
    lx, ly, lr, z = 62.2, 57.6, 11.0, 3
    clip = s.uid('lens')
    s.defs.append(f'<clipPath id="{clip}"><circle cx="{fmt(lx)}" cy="{fmt(ly)}" r="{fmt(lr - .15)}"/></clipPath>')
    right = max(p[0] for p in hd)
    arrow(s, (right + 1.4, src[1]), (lx - lr, ly), bend=.08, r0=0, r1=0, stroke=AXIS, sw=.28, no_head=True, opacity=.8, mark=False)
    s.circle(lx, ly, lr, fill='#FFFFFF', stroke=AXIS, sw=.3)
    s.lenses.append((lx, ly, lr))

    def lens(u, v):
        return lx + (u - dc[0]) * C * z, ly - (v - dc[1]) * C * z

    s.add(f'<g clip-path="url(#{clip})">')
    s.path(poly_path([lens(*direct[i]) for i in ConvexHull(direct).vertices]), stroke=LLM_DEEP, sw=.36, extra=dash)
    for u, v in cot:
        s.dot(*lens(u, v), r=1.3, ring=.25, mark=False)
    for u, v in direct:
        s.hollow(*lens(u, v), r=1.25, ring=.18, sw=.42, mark=False)
    s.add('</g>')
    s.text(lx - .8, ly - lr - 1.6, 'direct', anchor='end')
    s.text(HI_IN2, ly - lr - 1.6, '×3', anchor='end', font='num', fill=MUTED)

    # The chain-of-thought outline, labelled at its left end
    left = min(hc, key=lambda p: p[0])
    s.text(left[0] - 2.0, left[1] - 1.2, 'chain of', anchor='end')
    s.text(left[0] - 2.0, left[1] + 5.4, 'thought', anchor='end')

    # Model, then the corner key, in the empty Auth-Left quadrant; the headline number in Auth-Right
    _tag(s, 'gemini', SHORT['gemini'], str(year))
    kx, b1 = LO_IN + 1.25, 21.0
    s.hollow(kx, b1 - 1.9, r=.95, ring=0, sw=.38, mark=False)
    s.text(kx + 2.6, b1, 'direct', fill=MUTED, italic=True)
    s.dot(kx, b1 + 6.6 - 1.9, r=1.1, ring=0, mark=False)
    s.text(kx + 2.6, b1 + 6.6, 'chain of', fill=MUTED, italic=True)
    s.text(kx + 2.6, b1 + 13.2, 'thought', fill=MUTED, italic=True)
    num = '5.43'
    wn = text_width(num, NUM + 1.4, 'num', weight=700)
    s.text(HI_IN2, 7.6, num, size=NUM + 1.4, anchor='end', font='num', weight=700)
    s.text(HI_IN2 - wn - 1.6, 7.6, 'RSS', anchor='end')
    F.setdefault('chart_choices', {})['rss_compass'] = {
        'year': year, 'direct_centroid': direct.mean(axis=0).round(4).tolist(), 'cot_centroid': cot.mean(axis=0).round(4).tolist(),
        'magnifier': 'x3 on the direct cluster'}
    return s


def rss_waffle(F, D):
    side, gap, ggap = 5.0, .75, 4.5
    groups = [(F['rss']['amplifying'], HI_AMP, '#B8860B', 'amplifying', 'rss_gt'),
              (F['rss']['neutral'], '#EEEEF2', '#8A8FA3', 'neutral', 'rss_mid'),
              (F['rss']['stabilizing'], HI_STAB, '#5F9E4F', 'stabilizing', 'rss_lt')]
    s = Svg('rss_waffle', 167.4, 26.9, 'The 27 model-year configurations: 17 amplifying, 5 neutral, 5 stabilizing')
    n_inf = F['rss']['infinite']
    x, y = 0, .4
    inf_x = []
    for gi, (n, fill, stroke, lab, thr) in enumerate(groups):
        start = x
        for i in range(n):
            s.rect(x, y, side, side, fill=fill, stroke=stroke, sw=.28, rx=.7)
            if gi == 0 and i >= n - n_inf:
                inf_x.append(x)
            x += side + gap
        x += ggap - gap
        s.tspans(start, y + side + 6.6, [(str(n), dict(font='num', weight=700, size=NUM + .4)), (' ' + lab, dict())])
        s.math(thr, start, y + side + 13.3, fill=MUTED)
    # The bracket under the three Gemma-4-26B cells, and its mark
    bx0, bx1, by = inf_x[0] + .4, inf_x[-1] + side - .4, y + side + 1.0
    s.path(f'M{fmt(bx0)} {fmt(by - .7)}V{fmt(by)}H{fmt(bx1)}V{fmt(by - .7)}', stroke='#B8860B', sw=.3, join='miter', cap='butt')
    il, it, ir, ib = ink_box('∞', LABEL, 'num')
    s.text((bx0 + bx1) / 2 - (il + ir) / 2, by + 1.3 - it, '∞', font='num')
    yn = y + side + 20.2
    w = s.text(0, yn, '∞', font='num', fill=MUTED)
    w += s.text(w + 1.4, yn, 'Gemma-4-26B:', italic=True, fill=MUTED) + 1.4
    s.math('pis_direct_zero', w + 1.6, yn, fill=MUTED)
    return s


def _lds_values(F):
    return F['lds']['by_language_paper_basis'] if LDS_BASIS == 'paper' else F['lds']['by_language_nine_models']


def lds_compass(F, D, model='deepseek', year=2009):
    s, m = card_compass('lds_compass', f'{NAMES[model]}: English baseline fanning out to eleven languages')
    lp = D['lds_pred9']
    g = lp[(lp.m == model) & (lp.year == year)].set_index('language')
    base = g.loc['English']
    bp = m(base.lrecon, base.galtan)
    langs = [l for l in g.index if l != 'English']
    disp = {l: float(np.hypot(g.loc[l].lrecon - base.lrecon, g.loc[l].galtan - base.galtan)) for l in langs}
    show = {'German', 'Arabic', 'French', 'Bengali'}
    bends = {'Arabic': .2}
    for l in sorted(langs, key=lambda k: disp[k]):
        p = m(g.loc[l].lrecon, g.loc[l].galtan)
        emph = l in show
        arrow(s, bp, p, bend=bends.get(l, .09), r0=1.8, r1=1.2 if not emph else 1.5, stroke=LLM_DEEP, sw=.55 if emph else .3,
              no_head=not emph, head=2.5, width=1.95, opacity=None if emph else .75)
    for l in langs:
        p = m(g.loc[l].lrecon, g.loc[l].galtan)
        s.dot(*p, r=1.3 if l in show else .95, ring=.2)
    s.hollow(*bp, r=1.7, sw=.6)
    _tag(s, ICONS[model], SHORT[model], str(year))
    # English is the hollow origin of the fan; its key sits in the empty Auth-Right quadrant.
    s.hollow(LO_IN2 + 1.75, 6.4 - 1.9, r=1.5, sw=.6, ring=0, mark=False)
    s.text(LO_IN2 + 4.6, 6.4, 'English', italic=True, fill=MUTED)
    at = {l: m(g.loc[l].lrecon, g.loc[l].galtan) for l in show}
    s.text(at['Arabic'][0], at['Arabic'][1] - 3.3, 'Arabic', anchor='middle')
    s.text(at['German'][0] + 2.6, at['German'][1] + 2.0, 'German')
    s.text(at['Bengali'][0] + 2.4, at['Bengali'][1] + 6.4, lang('Bengali'))
    s.text(at['French'][0] - 2.6, at['French'][1] - .8, 'French', anchor='end')
    F.setdefault('chart_choices', {})['lds_compass'] = {
        'model': NAMES[model], 'year': year, 'displacement_2d': {k: round(v, 4) for k, v in disp.items()}}
    return s


def lds_bars(F, D):
    v = _lds_values(F)
    order = sorted(v, key=lambda k: -v[k])
    top, rest = order[:4], order[4:]
    lo, hi = min(v[l] for l in rest), max(v[l] for l in rest)
    rng = f'{lo:.2f}–{hi:.2f}'
    W, pitch, y0, th = 120, 6.5, 3.4, 3.0
    H = y0 + 4 * pitch + 2.4
    s = Svg('lds_bars', W, H, 'Mean LDS for the four most displaced languages; the seven others lie between '
            f'{lo:.2f} and {hi:.2f}')
    x0 = 34.6
    vw = text_width('0.0000', NUM, 'num', weight=700)
    scale = (W - .2 - vw - 2.2 - x0) / v[top[0]]
    for i, l in enumerate(top):
        y = y0 + i * pitch
        s.text(x0 - 2.4, y + 2.0, lang(l), anchor='end')
        s.path(bar_right(x0, y - th / 2, v[l] * scale, th), fill=LLM)
        s.text(x0 + v[l] * scale + 2.2, y + 2.0, f'{v[l]:.4f}', font='num', weight=700)
    y = y0 + 4 * pitch
    s.text(x0 - 2.4, y + 2.0, 'seven others' if len(rest) == 7 else f'{len(rest)} others', anchor='end', italic=True, fill=MUTED)
    s.rect(x0 + lo * scale, y - th / 2, (hi - lo) * scale, th, fill=LLM, opacity=.35, rx=.6)
    s.text(x0 + hi * scale + 2.2, y + 2.0, rng, font='num', fill=MUTED)
    s.line(x0, y0 - pitch / 2 + 1, x0, y + pitch / 2 - 1, stroke=AXIS, sw=.25, opacity=.6)
    F.setdefault('chart_choices', {})['lds_bars'] = {
        'basis': LDS_BASIS, 'top_four': {lang(l): round(v[l], 4) for l in top},
        'others': {lang(l): round(v[l], 4) for l in rest}, 'others_range': rng,
        'note': 'paper basis is the ten-model file; see discrepancies.md'}
    return s


def lds_bars_tall(F, D):
    s = Svg('lds_bars_tall', 120, 76, 'Mean LDS for eleven languages, sorted')
    v = _lds_values(F)
    order = sorted(v, key=lambda k: -v[k])
    x0, sc, pitch = 33, 210, 6.2
    for i, l in enumerate(order):
        y = 2.8 + i * pitch
        emph = i < 4
        s.text(x0 - 2.6, y + 2.0, lang(l), anchor='end')
        s.path(bar_right(x0, y - 1.25, v[l] * sc, 2.5), fill=LLM_DEEP if emph else LLM)
        if emph or l == order[-1]:
            s.text(x0 + v[l] * sc + 2.2, y + 1.95, f'{v[l]:.4f}', font='num', fill=INK if emph else MUTED, weight=700 if emph else None)
    s.line(x0, 0, x0, 2.8 + 10 * pitch + 2.4, stroke=AXIS, sw=.25, opacity=.6)
    caption(s, 0, 74.0, 'Mean displacement from the English baseline', anchor='start')
    return s


def ds_compass(F, D):
    s, m = card_compass('ds_compass', 'Eight-turn debate trajectories: GPT-5-mini travels, Qwen-Turbo scribbles and returns, Gemma-4-26B barely moves')
    dc = D['ds_coords']

    def path_of(k, y):
        return pts_from(dc[(dc.m == k) & (dc.year == y)].iloc[0], 't', 8)[:, 1:]

    gpt, qwen, gem = path_of('gpt5mini', 2009), path_of('qwen', 2014), path_of('gemma', 2009)

    def draw(arr, color, sw, rdot, mapper, mark=True):
        pts = [mapper(*p) for p in arr]
        s.path(poly_path(pts, closed=False), stroke=color, sw=sw)
        if mark:
            s.marks.append(('p', pts, sw / 2))
        for p in pts[1:-1]:
            s.circle(*p, rdot, fill=color)
        s.hollow(*pts[0], r=rdot + .6, stroke=color, sw=.38, ring=.14, mark=mark)
        s.dot(*pts[-1], r=rdot + .65, fill=color, stroke=color, ring=.18, mark=mark)

    draw(gpt, LLM_DEEP, .62, .62, m)
    draw(gem, LLM_DEEP, .4, .55, m)
    draw(qwen, LLM_DARK, .34, .32, m)

    # Magnifier for Qwen-Turbo's scribble
    cx, cy, r = 61.8, 62.8, 10.8
    z = 4.0
    qc = (np.array([qwen[:, 0].min(), qwen[:, 1].min()]) + np.array([qwen[:, 0].max(), qwen[:, 1].max()])) / 2
    src_u = m(float(qwen[:, 0].max()), float(qc[1]))
    clip = s.uid('lens')
    s.defs.append(f'<clipPath id="{clip}"><circle cx="{fmt(cx)}" cy="{fmt(cy)}" r="{fmt(r - .15)}"/></clipPath>')
    arrow(s, (src_u[0] + 1.5, src_u[1]), (cx - r, cy + 3.4), bend=.10, r0=0, r1=0, stroke=AXIS, sw=.28, no_head=True, opacity=.8, mark=False)
    s.circle(cx, cy, r, fill='#FFFFFF', stroke=AXIS, sw=.3)
    s.lenses.append((cx, cy, r))

    def lens(u, v):
        return cx + (u - qc[0]) * C * z, cy - (v - qc[1]) * C * z

    s.add(f'<g clip-path="url(#{clip})">')
    draw(qwen, LLM_DARK, .42, .52, lens, mark=False)
    s.add('</g>')

    # Quiet key in the empty Auth-Left quadrant
    s.text(LO_IN, 6.4, 'Eight turns')
    s.text(LO_IN, 13.0, 'hollow start,', italic=True, fill=MUTED)
    s.text(LO_IN, 19.6, 'solid end', italic=True, fill=MUTED)

    gp = m(*gem[0])
    _tag(s, 'gemma', SHORT['gemma'], '2009', x=LO_IN2, y=gp[1] - 1.6, room=HI_IN2 - LO_IN2)
    arrow(s, (LO_IN2 - .6, gp[1] - 2.4), gp, bend=.16, r0=0, r1=1.7, stroke=AXIS, sw=.28, no_head=True, opacity=.75, mark=False)
    _tag(s, 'gpt', SHORT['gpt5mini'], '2009', x=LO_IN, y=44.2)
    _tag(s, 'qwen', SHORT['qwen'], '2014', x=LO_IN2, y=43.8, room=HI_IN2 - LO_IN2)
    s.text(HI_IN2, 50.4, '×4', anchor='end', font='num', fill=MUTED)
    return s


def ias_dumbbell(F, D):
    W, H = 138, 76
    s = Svg('ias_dumbbell', W, H, 'Judged quality of arguments for and against, per model, sorted by IAS')
    t = F['table1']
    order = sorted(t, key=lambda k: t[k]['ias'])
    x0, x1 = 52, 109
    lo, hi = 4.1, 4.8
    X = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    yh, y0, pitch = 6.1, 13.4, 6.4
    y_last = y0 + 8 * pitch
    yb = H - 2.0  # the axis line sits on the bottom edge, below the last row's descenders
    slot = LABEL * .92 * 1.36
    # Column heads: the key for the deep rows, the marker key, and the value column
    s.line(1.6, yh - 1.9, 6.6, yh - 1.9, stroke=LLM_DEEP, sw=1.0)
    s.hollow(1.6, yh - 1.9, r=1.4, sw=.5, ring=0, mark=False)
    s.dot(6.6, yh - 1.9, r=1.5, fill=LLM_DEEP, stroke=LLM_DEEP, ring=0, mark=False)
    s.math('ias_gt', 10.0, yh, fill=MUTED)
    xk = x0
    s.hollow(xk + 1.5, yh - 1.9, r=1.4, sw=.5, ring=0, mark=False)
    xk += 4.6
    xk += s.text(xk, yh, 'for', italic=True, fill=MUTED) + 4.0
    s.dot(xk + 1.5, yh - 1.9, r=1.5, fill=LLM_DEEP, stroke=LLM_DEEP, ring=0, mark=False)
    s.text(xk + 4.6, yh, 'against', italic=True, fill=MUTED)
    s.text(W, yh, 'IAS', anchor='end', fill=MUTED)
    for tick in (4.2, 4.4, 4.6, 4.8):
        s.line(X(tick), y0 - 3.4, X(tick), y_last + 2.4, stroke=HAIR, sw=.25)
        s.text(X(tick), yb, f'{tick:.1f}', anchor='middle', font='num', fill=MUTED)
    s.text(X(4.2) - text_width('4.2', NUM, 'num') / 2 - 2.4, yb, 'judged quality (0–5)', anchor='end', italic=True, fill=MUTED)
    for i, k in enumerate(order):
        y = y0 + i * pitch
        f, a, ias = t[k]['ias_for'], t[k]['ias_against'], t[k]['ias']
        emph = abs(ias) > .15
        s.named(ICONS[k], SHORT[k], 0, y + 2.05, slot=slot)
        if abs(f - a) > 1e-9:
            s.line(X(f), y, X(a), y, stroke=LLM_DEEP if emph else LLM, sw=1.0 if emph else .6)
            s.dot(X(a), y, r=1.6, fill=LLM_DEEP if emph else LLM, stroke=LLM_DEEP, ring=.28)
            s.hollow(X(f), y, r=1.5, sw=.5, ring=.25)
        else:
            s.dot(X(a), y, r=1.6, fill=LLM, stroke=LLM_DEEP, ring=.28)
            s.circle(X(f), y, 2.5, stroke=LLM_DEEP, sw=.42)
        sign = '\u2212' if ias < -1e-12 else '+' if ias > 1e-12 else ''
        s.text(W, y + 1.95, f'{sign}{abs(ias):.4f}', anchor='end', font='num', fill=INK if emph else MUTED)
    return s


# ---------------------------------------------------------------------------------------------------------------------
# Global compression
# ---------------------------------------------------------------------------------------------------------------------

def coverage_bars(F, D):
    W, H = 377.3, 74
    s = Svg('coverage_bars', W, H, 'Coverage of the European party reference by the LLM cohort, drawn to scale')
    cov = F['coverage']
    rows = [('2D plane', 'area2_pct'), ('1D axis', 'lrgen_pct'), ('3D volume', 'vol3_pct')]
    x0 = 76
    tw = W - x0 - .3
    th = 13.5
    pitch = 24.2
    y0 = 1.6
    for i, (a, key) in enumerate(rows):
        y = y0 + i * pitch
        s.text(0, y + 6.0, a, size=8.6, font='display', weight=600)
        if key == 'area2_pct':
            s.tspans(0, y + 12.8, [('lrecon', dict(italic=True)), ('–', dict(fill=MUTED)), ('galtan', dict(italic=True))])
        elif key == 'lrgen_pct':
            s.tspans(0, y + 12.8, [('lrgen', dict(italic=True)), (' thickness (3D ÷ 2D)', dict(fill=MUTED))])
        else:
            s.text(0, y + 12.8, 'all three axes', fill=MUTED)
        s.rect(x0, y, tw, th, fill=TRACK_TINT, stroke=PARTY_DEEP, sw=.42, rx=1.2)
        mean = cov['mean'][key]
        fw = tw * mean / 100
        s.path(bar_right(x0 + .21, y + .21, fw, th - .42, r=1.0), fill=LLM)
        for k, v in cov['per_model'].items():
            xt = x0 + tw * v[key] / 100
            s.line(xt, y - 1.4, xt, y + th + 1.4, stroke=LLM_DEEP, sw=.34)
        lo_v, hi_v = cov['range'][key]
        xv = x0 + tw * hi_v / 100 + 5.0
        wv = s.text(xv, y + th / 2 + 3.5, f'{mean:.2f}%', size=10.2, font='display', weight=600)
        s.text(xv + wv + 3.4, y + th / 2 + 2.1, f'cohort mean; models {lo_v:.2f}–{hi_v:.2f}%', italic=True)
        s.text(x0 + tw - 2.2, y + th / 2 + 2.1, '100%', anchor='end', font='num', fill=PARTY_TEXT)
    yl = H - 2.0
    x = x0
    s.add('<g class="ch-caption">')
    s.rect(x, yl - 3.9, 9, 4.4, fill=TRACK_TINT, stroke=PARTY_DEEP, sw=.42, rx=.7)
    x += 11
    x += s.text(x, yl, 'European parties (CHES hull, 2009–2019)', size=CAP, fill=MUTED, italic=True) + 7
    s.rect(x, yl - 3.9, 9, 4.4, fill=LLM, rx=.7)
    x += 11
    x += s.text(x, yl, 'cohort mean', size=CAP, fill=MUTED, italic=True) + 7
    s.line(x + 1, yl - 4.8, x + 1, yl + 1.0, stroke=LLM_DEEP, sw=.34)
    x += 3.4
    s.text(x, yl, 'one model', size=CAP, fill=MUTED, italic=True)
    s.add('</g>')
    return s


def _approx(s, x, y, num, size, font, weight=None, anchor='start'):
    """'≈ number' with the same small gap whatever the face: 0.3 em of the number's size. LM Roman has no ≈,
    so for LM numbers the sign comes from Pagella."""
    sym_font = 'text' if font == 'num' else font
    w_sym = text_width('≈', size, sym_font)
    gap = .3 * size
    w_num = text_width(num, size, font, weight=weight)
    x0 = x - (w_sym + gap + w_num if anchor == 'end' else 0)
    s.text(x0, y, '≈', size=size, font=sym_font)
    s.text(x0 + w_sym + gap, y, num, size=size, font=font, weight=weight)
    return w_sym + gap + w_num


def monoculture(F, D):
    W, H = 150, 46
    s = Svg('monoculture', W, H, 'Mean inter-model centroid distance against the typical distance between European party families, to scale')
    mono = F['monoculture']
    scale = 172  # mm per CHES unit
    x0 = 2.4
    rows = [('Major party families', mono['party_family_distance_paper'], '#74D2FA', PARTY_DEEP, '0.60', True, 5.0),
            ('Nine LLMs, all 36 pairs', mono['mean_inter_model_centroid_distance'], LLM, LLM_DEEP, '0.173', False, 22.0)]
    for lab, d, fill, stroke, val, approx, y in rows:
        s.text(0, y, lab)
        yy = y + 6.2
        s.line(x0, yy, x0 + d * scale, yy, stroke=stroke, sw=.8)
        s.circle(x0, yy, 2.1, fill=fill, stroke=stroke, sw=.42)
        s.circle(x0 + d * scale, yy, 2.1, fill=fill, stroke=stroke, sw=.42)
        if approx:
            _approx(s, x0 + d * scale + 4.0, yy + 2.0, val, NUM + .4, 'num', weight=700)
        else:
            s.text(x0 + d * scale + 4.0, yy + 2.0, val, size=NUM + .4, font='num', weight=700)
    w = _approx(s, W, 30.4, '0.29', 10.2, 'display', weight=600, anchor='end')
    s.text(W - w - 2.0, 30.4, 'ratio', anchor='end', italic=True, fill=MUTED)
    caption(s, 0, 43.6, 'Mean distance between centroids in CHES space, to scale', anchor='start')
    return s


# OKLab (Ottosson 2020) for perceptual colour ramps
def _lin(c):
    c = c / 255
    return np.where(c <= .04045, c / 12.92, ((c + .055) / 1.055) ** 2.4)


def _to_oklab(hexc):
    r, g, b = _lin(np.array([int(hexc[i:i + 2], 16) for i in (1, 3, 5)], dtype=float))
    l_ = np.cbrt(.4122214708 * r + .5363325363 * g + .0514459929 * b)
    m_ = np.cbrt(.2119034982 * r + .6806995451 * g + .1073969566 * b)
    s_ = np.cbrt(.0883024619 * r + .2817188376 * g + .6299787005 * b)
    return np.array([.2104542553 * l_ + .7936177850 * m_ - .0040720468 * s_,
                     1.9779984951 * l_ - 2.4285922050 * m_ + .4505937099 * s_,
                     .0259040371 * l_ + .7827717662 * m_ - .8086757660 * s_])


def _from_oklab(lab):
    L, a, b = lab
    l_ = (L + .3963377774 * a + .2158037573 * b) ** 3
    m_ = (L - .1055613458 * a - .0638541728 * b) ** 3
    s_ = (L - .0894841775 * a - 1.2914855480 * b) ** 3
    rgb = np.array([4.0767416621 * l_ - 3.3077115913 * m_ + .2309699292 * s_,
                    -1.2684380046 * l_ + 2.6097574011 * m_ - .3413193965 * s_,
                    -.0041960863 * l_ - .7034186147 * m_ + 1.7076147010 * s_])
    rgb = np.clip(rgb, 0, 1)
    srgb = np.where(rgb <= .0031308, 12.92 * rgb, 1.055 * rgb ** (1 / 2.4) - .055)
    return '#%02X%02X%02X' % tuple(int(round(v * 255)) for v in srgb)


def _lum(hexc):
    r, g, b = _lin(np.array([int(hexc[i:i + 2], 16) for i in (1, 3, 5)], dtype=float))
    return .2126 * r + .7152 * g + .0722 * b


def _contrast(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + .05) / (lb + .05)


def diverging(v, pos=LAV[4], neg='#6B7280'):
    """White at 0, toward #5445B5 for positive and a neutral grey for negative correlations, linear in OKLab."""
    white = _to_oklab('#FFFFFF')
    end = _to_oklab(pos if v >= 0 else neg)
    return _from_oklab(white + (end - white) * min(abs(v), 1))


def mtmm(F, D):
    W = 140.0
    order = F['mtmm']['order']
    M = F['mtmm']['matrix']
    rows, cols = order[1:], order[:-1]
    n = len(rows)
    lab_w = max(ink_box(r, HEAD)[2] for r in rows)
    x0 = .3 + lab_w + 2.2
    cw = (W - x0 - .3) / n
    ch = cw
    y0 = .3
    col_base = y0 + n * ch + 2.4 - ink_box('PSS', HEAD)[1]
    H = col_base + .6
    s = Svg('mtmm', W, H, 'Cross-metric correlations, lower triangle')
    gap = .4
    conv = {tuple(sorted(p)) for p in F['mtmm']['convergent']}
    alg = {tuple(sorted(p)) for p in F['mtmm']['algebraic']}
    worst = (99, None)
    for r, rname in enumerate(rows):
        s.text(x0 - 2.2, y0 + (r + .5) * ch - ink_box(rname, HEAD)[1] / 2, rname, size=HEAD, anchor='end')
        for c in range(r + 1):
            v = M[r + 1][c]
            col = diverging(v)
            x, y = x0 + c * cw, y0 + r * ch
            s.rect(x + gap / 2, y + gap / 2, cw - gap, ch - gap, fill=col, rx=.55)
            white_c, ink_c = _contrast('#FFFFFF', col), _contrast(INK, col)
            fg, con = ('#FFFFFF', white_c) if white_c >= ink_c else (INK, ink_c)
            worst = min(worst, (con, f'{rname}-{cols[c]}'))
            sign = '\u2212' if v < 0 else ''
            txt = sign + f'{abs(v):.3f}'[1:]
            l, t, rr, b = ink_box('8', NUM18, 'num')
            # Centred in its cell, as in any heatmap; the user found decimal-aligned values lopsided (2026-11-03)
            s.text(x + cw / 2, y + ch / 2 - (t + b) / 2, txt, size=NUM18, anchor='middle', font='num', fill=fg, register=False)
            pair = tuple(sorted((rname, cols[c])))
            if pair in conv:
                s.rect(x + 1.0, y + 1.0, cw - 2.0, ch - 2.0, stroke=INK, sw=.6, rx=.5)
            elif pair in alg:
                s.rect(x + 1.0, y + 1.0, cw - 2.0, ch - 2.0, stroke=INK, sw=.6, rx=.5, extra='stroke-dasharray="1.6 1"')
    if worst[0] < 4.5:
        raise RuntimeError(f'mtmm: cell {worst[1]} has contrast {worst[0]:.2f}')
    for c, cname in enumerate(cols):
        s.text(x0 + (c + .5) * cw, col_base, cname, size=HEAD, anchor='middle')
    # Legend in the empty upper triangle: the scale, then the two outlines
    lx = x0 + 2 * cw + 2.5
    bar_w = W - .3 - lx - 6
    s.text(lx, y0 + 5.2, 'correlation', italic=True, fill=MUTED)
    gid = s.uid('ramp')
    stops = ''.join(f'<stop offset="{i / 20:.3f}" stop-color="{diverging(-1 + i / 10)}"/>' for i in range(21))
    s.defs.append(f'<linearGradient id="{gid}" x1="0" x2="1" y1="0" y2="0">{stops}</linearGradient>')
    s.rect(lx, y0 + 7.6, bar_w, 4.0, fill=f'url(#{gid})', stroke=HAIR, sw=.2, rx=.5)
    s.text(lx, y0 + 18.0, '\u22121', font='num', fill=MUTED)
    s.text(lx + bar_w / 2, y0 + 18.0, '0', anchor='middle', font='num', fill=MUTED)
    s.text(lx + bar_w, y0 + 18.0, '+1', anchor='end', font='num', fill=MUTED)
    ky = y0 + ch + 11.6
    s.rect(lx, ky - 4.6, 7.0, 5.0, fill=diverging(.6), stroke=INK, sw=.6, rx=.5)
    xk = lx + 9.2
    xk += s.text(xk, ky, 'convergent', italic=True, fill=MUTED) + 6.0
    s.rect(xk, ky - 4.6, 7.0, 5.0, fill=diverging(-.85), stroke=INK, sw=.6, rx=.5, extra='stroke-dasharray="1.6 1"')
    s.text(xk + 9.2, ky, 'algebraic', italic=True, fill=MUTED)
    F.setdefault('chart_choices', {})['mtmm'] = {'lowest_cell_contrast': round(worst[0], 2), 'at': worst[1],
                                                 'scale': 'white at 0; +1 #5445B5; -1 #6B7280; linear in OKLab'}
    return s


def pca_bars(F, D):
    W, H = 240, 30
    s = Svg('pca_bars', W, H, 'Share of variance in three principal components')
    p = F['pca']
    parts = [('PC1', p['PC1'][0], p['PC1'][1], LAV[4], '#FFFFFF'), ('PC2', p['PC2'][0], p['PC2'][1], LAV[3], '#FFFFFF'),
             ('PC3', p['PC3'][0], p['PC3'][1], LAV[1], INK), ('', 'remainder', 100 - p['total'], '#ECECF6', MUTED)]
    gap = .5
    x = 0
    y = 8.0
    th = 11
    for tag, name, share, fill, tc in parts:
        w = (W - 3 * gap) * share / 100
        s.rect(x, y, w, th, fill=fill, rx=.9)
        s.tspans(x + .3, y - 2.2, [(tag + ' ' if tag else '', dict()), (name, dict(italic=not tag, fill=INK if tag else MUTED))])
        s.text(x + w / 2, y + th / 2 + 2.0, f'{share:.2f}%', anchor='middle', font='num', fill=tc, weight=700 if tag else None, register=False)
        x += w + gap
    caption(s, 0, H - 2.4, f"Three components explain {p['total']:.2f}% of the variance (exploratory, n = 9)", anchor='start')
    return s


NEEDS = (('Manipulative framings',), ('Multilingual deployments',), ('Multi-turn agents',), ('Cohort-level monoculture',))
INSTRUMENTS = (('PSS', 'Register'), ('LDS', 'Language'), ('DS', 'Multi-turn'), ('OW', 'Aggregate'))


def instrument_matrix(F, D):
    """Each practitioner need has its own instrument (the diagonal); a single-prompt compass score answers none."""
    W = 257.67                      # the full column, so the chart prints 1:1
    ROW, HEAD_I, LAST = 20 * .3528, 26 * .3528, 19 * .3528
    rule, dot_c, ring_c, x_c = '#E4E5F2', LAV[4], '#C9CAE6', '#8B8FA3'
    name = 'instrument_matrix'

    def iw(t, size, **k):
        b = ink_box(t, size, **k)
        return b[2] - b[0]

    lab_w = max(iw(line, ROW) for need in NEEDS for line in need)
    heads = [max(iw(h, HEAD_I, font='display', weight=600), text_width(a, LABEL, caps=True)) for h, a in INSTRUMENTS]
    last_w = max(iw(t, LAST, italic=True) for t in ('single-prompt', 'compass score'))
    g1, gh = 4.0, 3.2
    pitch = (W - .3 - lab_w - g1 - heads[0] / 2 - heads[-1] / 2 - 2 * gh - last_w - .3) / 3
    cols = [.3 + lab_w + g1 + heads[0] / 2 + i * pitch for i in range(4)]
    x_rule = cols[-1] + heads[-1] / 2 + gh
    x_last = x_rule + gh + last_w / 2

    head_base = .5 - ink_box('PSS', HEAD_I, font='display', weight=600)[1]
    axis_base = head_base + 6.6
    top = axis_base + 3.0
    lead = 1.02 * ROW  # line pitch, should a need ever wrap
    # Every need fits one line, so all rows share one height and the diagonal steps evenly
    rh = [13.6] * len(NEEDS)
    tops = [top + sum(rh[:r]) for r in range(5)]
    H = tops[-1] + .4
    s = Svg(name, W, H, 'Each practitioner need has its own instrument: manipulative framings need PSS, '
                        'multilingual deployments LDS, multi-turn agents DS and cohort-level monoculture OW; '
                        'a single-prompt compass score answers none')

    # Hairlines rather than bands: they match the poster's table rules and are the quieter of the two
    for y in tops:
        s.line(0, y, W, y, stroke=rule, sw=.25)
    s.line(x_rule, .6, x_rule, tops[-1], stroke=rule, sw=.3)

    for (h, a), cx in zip(INSTRUMENTS, cols):
        s.text(cx, head_base, h, size=HEAD_I, anchor='middle', font='display', weight=600, fill=LAV[4])
        s.text(cx, axis_base, a, anchor='middle', fill=MUTED, caps=True)
    s.text(x_last, axis_base - 1.05 * LAST, 'single-prompt', size=LAST, anchor='middle', italic=True, fill=MUTED)
    s.text(x_last, axis_base, 'compass score', size=LAST, anchor='middle', italic=True, fill=MUTED)

    cap = -ink_box('M', ROW)[1]
    for r, need in enumerate(NEEDS):
        cy = tops[r] + rh[r] / 2
        first = cy - (len(need) - 1) * lead / 2 + cap / 2
        for i, line in enumerate(need):
            s.text(.3, first + i * lead, line, size=ROW)
        for c, cx in enumerate(cols):
            if c == r:
                s.circle(cx, cy, 2.75, fill=dot_c)
            else:
                s.circle(cx, cy, 1.25, stroke=ring_c, sw=.3)
        d = 2.25
        s.path(f'M{fmt(x_last - d)} {fmt(cy - d)}L{fmt(x_last + d)} {fmt(cy + d)}M{fmt(x_last + d)} {fmt(cy - d)}L{fmt(x_last - d)} {fmt(cy + d)}',
               stroke=x_c, sw=.6)
    F.setdefault('chart_choices', {})['instrument_matrix'] = {
        'size_mm': [W, round(H, 2)], 'column_pitch_mm': round(pitch, 2), 'rows_mm': [round(v, 2) for v in rh],
        'rows_pt': 20, 'note': 'rows at 20 pt so the four columns keep their 17 pt small-caps axis words apart; '
                               'the paper\'s "practitioners refusing manipulative framings" is shortened to '
                               '"Manipulative framings" so every row is one line and parallel with the other three'}
    return s


def hull_glyph(F, D, key):
    S = 34
    s = Svg(f'hull_{key}', S, S, f"{NAMES[key]}: inner-90% hulls in 2009, 2014 and 2019")
    m = compass(s, .2, .2, S - .4, rx=1.1, axis_sw=.2, frame_sw=.2)
    h = F['hulls_2d'][key]['by_year']
    s.add(f'<g clip-path="url(#{s.last_clip})">')
    for y in FX.YEARS:
        s.path(poly_path([m(u, v) for u, v in h[y]]), fill=LLM, opacity=.36)
    for y in FX.YEARS:
        s.path(poly_path([m(u, v) for u, v in h[y]]), stroke=LLM_DEEP, sw=.26)
    s.add('</g>')
    return s


def band_contours(F, D):
    W, H = 841, 130
    s = Svg('band_contours', W, H, '')
    xy = D['all'][['lrecon', 'galtan']].values
    masses = [.98, .94, .9, .85, .8, .74, .68, .62, .55, .48, .41, .34, .27, .2, .13, .07]
    contours = hdr_contours(xy, masses=masses, grid=340, lim=(-.3, 1.3), bw=.2)
    scale = 700.0
    cx, cy = 590, 72
    ux, uy = .42, .24

    def T(u, v):
        return cx + (u - ux) * scale, cy - (v - uy) * scale

    out = []
    for polys in contours:
        for poly in polys:
            pts = [T(u, v) for u, v in poly]
            run = []
            margin = 3
            for p in pts:
                if -margin <= p[0] <= W + margin and -margin <= p[1] <= H + margin:
                    run.append(p)
                else:
                    if len(run) > 4:
                        out.append(run)
                    run = []
            if len(run) > 4:
                out.append(run)
    d = []
    for run in out:
        closed = math.hypot(run[0][0] - run[-1][0], run[0][1] - run[-1][1]) < .5
        pts = rdp(run, .22)
        if closed and len(pts) > 3:
            pts = pts[:-1]
        if len(pts) >= 2:
            d.append(smooth_path(pts, closed=closed, nd=1))
    s.add(f'<g fill="none" stroke="#FFFFFF" stroke-width=".32" stroke-linejoin="round" stroke-linecap="round"><path d="{"".join(d)}"/></g>')
    return s


# ---------------------------------------------------------------------------------------------------------------------

ROUND3 = '## From the charts agent, round 3'


def append_discrepancies(F):
    """Never rewrite the log: create it if missing, then append this round's findings once."""
    path = DATA / 'discrepancies.md'
    if not path.exists():
        FX.write_discrepancies(F, path)
        copy_log = DATA / 'discrepancies_copy.md'
        if copy_log.exists():
            with open(path, 'a', encoding='utf-8', newline='\n') as fh:
                fh.write('\n' + copy_log.read_text(encoding='utf-8'))
    text = path.read_text(encoding='utf-8')
    if ROUND3 in text:
        return
    nine = F['lds']['by_language_nine_models']
    rest9 = sorted(nine.values())[:7]
    note = f"""
{ROUND3}

1. **Directional JBS follows the notebook, not its stated definition.** Appendix B.8 and Table 12 define directional JBS by sign ({{CA, A}} against {{D, CD}}). The published values (1.43% global; Llama-3-70B 3.96%, Llama-4-Scout 3.66%) reproduce only when neutral is a bucket of its own, as `notebooks/2_PSS and JBS.ipynb` computes it. By sign alone they would be 0.00% and 0.61%. `facts.py` uses the notebook's rule, so its checks pass. The fact-check report lists this as P4.
2. **The LDS "seven others" range depends on the basis.** On the paper's basis (ten models, item 2), the seven smaller language means span {F['chart_choices']['lds_bars']['others_range']}, as `lds_bars` prints. On the nine cohort models they span {rest9[0]:.2f}–{rest9[-1]:.2f}, although the top four are the same languages.
3. **The matrix's RSS cells rest on eight models.** Gemma-4-26B's RSS is infinite, so Pearson on Table 1 reproduces those six cells only with Gemma dropped pair by pair. A caption that says "nine models" should add "(eight for RSS)" (fact-check m2).
"""
    with open(path, 'a', encoding='utf-8', newline='\n') as fh:
        fh.write(note)


def write_contact_sheet(names):
    fonts = ROOT / 'poster' / 'assets' / 'fonts' / 'fonts.css'
    head = f'<link rel="stylesheet" href="{fonts.as_uri()}">' if fonts.exists() else ''
    if not fonts.exists() or 'LM Roman Poster' not in fonts.read_text(encoding='utf-8'):
        # Until the layout's fonts.css carries the family, preview with MiKTeX's identical originals
        lm = Path('C:/Users/rifat/AppData/Local/Programs/MiKTeX/fonts/opentype/public/lm')
        head += ('<style>' + ''.join(
            f"@font-face{{font-family:'LM Roman Poster';font-weight:{w};font-style:{st};src:url('{(lm / f).as_uri()}')}}"
            for w, st, f in ((400, 'normal', 'lmroman10-regular.otf'), (700, 'normal', 'lmroman10-bold.otf'),
                             (400, 'italic', 'lmroman10-italic.otf'))) + '</style>')
        print('contact sheet: LM Roman Poster not in fonts.css yet; previewing with MiKTeX lmroman10')
    cells = []
    for n in names:
        if n.startswith('chrono_2d_'):
            body = f'<img src="{(OUT / (n + ".svg")).as_uri()}" style="width:47mm;height:47mm;display:block">'
        else:
            body = (OUT / f'{n}.svg').read_text(encoding='utf-8')
        band = n == 'band_contours'
        style = ' style="background:#5445B5"' if band else ''
        cells.append(f'<figure id="{n}" class="cell{" wide" if band else ""}"{style}>{body}<figcaption>{n}</figcaption></figure>')
    html = ('<!doctype html><html><head><meta charset="utf-8"><title>Chart contact sheet</title>' + head +
            '<style>body{margin:6mm;background:#fff;font-family:Consolas,monospace;display:flex;flex-wrap:wrap;gap:8mm;align-items:flex-start;width:1040mm}'
            '.cell{margin:0;padding:3mm;border:.2mm solid #eee}.cell figcaption{font-size:4mm;color:#999;margin-top:1mm}.wide{width:860mm}'
            '.wide figcaption{color:#fff}</style></head><body>' + ''.join(cells) + '</body></html>')
    p = OUT / 'contact_sheet.html'
    p.write_text(html, encoding='utf-8', newline='\n')
    return p


def render_contact_sheet(page_path, names):
    from playwright.sync_api import sync_playwright
    SP_PREVIEW.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(channel='chrome')
        pg = b.new_page(viewport={'width': 4060, 'height': 2400}, device_scale_factor=1)
        pg.goto(page_path.as_uri())
        pg.evaluate('document.fonts.ready')
        pg.wait_for_timeout(800)
        pg.screenshot(path=str(OUT / 'contact_sheet.png'), full_page=True)
        pg2 = b.new_page(viewport={'width': 4060, 'height': 2400}, device_scale_factor=2.6)
        pg2.goto(page_path.as_uri())
        pg2.evaluate('document.fonts.ready')
        pg2.wait_for_timeout(800)
        for n in names:
            pg2.locator(f'#{n}').screenshot(path=str(SP_PREVIEW / f'{n}.png'))
        fams = pg.evaluate("Array.from(document.fonts).filter(f=>f.status==='loaded').map(f=>f.family+' '+f.weight+' '+f.style)")
        print('fonts loaded:', fams)
        b.close()


def main():
    F, Chk, D = FX.build()
    DATA.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'hull_glyphs').mkdir(exist_ok=True)
    texkit.build()

    charts = [point_to_shape, compass_legend, pipeline, pss_compass, pss_bars, pis_compass, pis_bars, pis_bars_tall, rss_compass, rss_waffle,
              lds_compass, lds_bars, lds_bars_tall, ds_compass, ias_dumbbell, coverage_bars, monoculture, mtmm, pca_bars,
              instrument_matrix, band_contours]
    names = []
    warnings = []
    sizes = {}
    for fn in charts:
        s = fn(F, D)
        (OUT / f'{s.name}.svg').write_text(s.render(), encoding='utf-8', newline='\n')
        names.append(s.name)
        sizes[s.name] = [round(s.w, 2), round(s.h, 2)]
        warnings += s.check()
    glyph_names = []
    for k in FX.MODEL_KEYS:
        s = hull_glyph(F, D, k)
        (OUT / 'hull_glyphs' / f'{k}.svg').write_text(s.render(), encoding='utf-8', newline='\n')
        tmp = f'_g_{k}'
        (OUT / f'{tmp}.svg').write_text(s.render(), encoding='utf-8', newline='\n')
        glyph_names.append(tmp)
    chrono = chrono_clean.clean_all()
    chrono_names = [f'chrono_2d_{y}' for y in chrono]
    sheet = write_contact_sheet(names + glyph_names + chrono_names)
    for tmp in glyph_names:
        (OUT / f'{tmp}.svg').unlink()

    F['chart_files'] = {n: {'file': f'poster/charts/{n}.svg', 'width_mm': sizes[n][0], 'height_mm': sizes[n][1]} for n in names}
    F['chart_files']['hull_glyphs'] = {'file': 'poster/charts/hull_glyphs/<model_key>.svg', 'width_mm': 34, 'height_mm': 34}
    for y, (dst, st) in chrono.items():
        F['chart_files'][f'chrono_2d_{y}'] = {'file': f'poster/charts/{dst.name}', 'viewBox': st['viewBox'], 'kb': st['out_kb']}
    (DATA / 'facts.json').write_text(json.dumps(F, indent=1), encoding='utf-8', newline='\n')
    bad = FX.write_verification(Chk, DATA / 'verification.md')
    append_discrepancies(F)
    print(f'{len(Chk.rows)} checks; {len(bad)} mismatches (see discrepancies.md for why)')
    print('layout warnings:', len(warnings))
    for w in warnings:
        print('  ', w)
    render_contact_sheet(sheet, names + glyph_names + chrono_names)
    print('sizes mm', {n: sizes[n] for n in ('mtmm', 'lds_bars', 'pipeline', 'rss_compass', 'ias_dumbbell', 'rss_waffle', 'coverage_bars')})
    print('sizes KB', {p.name: p.stat().st_size // 1024 for p in OUT.glob('*.svg')})
    print('chrono', {y: st for y, (_, st) in chrono.items()})
    print('icons available:', sorted(p.name for p in ICON_DIR.glob('*.*') if p.suffix in ('.svg', '.png')) if ICON_DIR.exists() else 'none yet')


if __name__ == '__main__':
    main()
