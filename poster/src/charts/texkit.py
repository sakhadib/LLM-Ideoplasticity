"""Typeset chart math with real TeX (pdflatex, Latin Modern) and embed it as glyph paths.

Each snippet is boxed with \\sbox so TeX reports its width, height and depth, then set on its own tight page by
the preview package. pymupdf converts every page to SVG with text as paths, so the poster carries TeX's own
kerning and ligatures without embedding a font. Results are cached in tex_cache/ and rebuilt only when the
snippet set changes.
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path

import pymupdf

HERE = Path(__file__).resolve().parent
CACHE = HERE / 'tex_cache'

PREAMBLE = r"""\documentclass[10pt]{article}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb}
\usepackage{bm}
\usepackage[active,tightpage]{preview}
\setlength\PreviewBorder{0pt}
\pagestyle{empty}
\newsavebox\snipbox
"""
PT_TO_BP = 72 / 72.27          # TeX points to PDF points
EM_BP = 10 * PT_TO_BP          # the 10 pt design size on the page, in PDF points

# Every piece of math the charts set. Plain words and numbers stay in the page fonts.
SNIPPETS = {
    'p_pos_ctx': r'$\mathbb{P}(\textit{position}\mid\textit{context})$',
    'ches_tuple': r'$\langle \textit{lrgen},\ \textit{lrecon},\ \textit{galtan}\rangle$',
    'rss_gt': r'$\text{RSS}>1.2$',
    'rss_mid': r'$0.8\text{--}1.2$',
    'rss_lt': r'$\text{RSS}<0.8$',
    'pis_direct_zero': r'$\text{PIS}_{\text{direct}}=0$',
    'ias_gt': r'$|\text{IAS}|>0.15$',
}


def _source(snips):
    lines = [PREAMBLE, r'\begin{document}']
    for i, tex in enumerate(snips.values()):
        lines.append(r'\sbox\snipbox{' + tex + r'}\typeout{SNIP:' + str(i)
                     + r':\the\wd\snipbox:\the\ht\snipbox:\the\dp\snipbox}')
        lines.append(r'\begin{preview}\usebox\snipbox\end{preview}')
    lines.append(r'\end{document}')
    return '\n'.join(lines) + '\n'


def _inner(svg):
    """The drawing inside pymupdf's <svg> wrapper, ready to sit in a chart: plain href, no data-text."""
    body = re.search(r'<svg[^>]*>(.*)</svg>', svg, flags=re.S).group(1)
    body = body.replace('xlink:href=', 'href=')
    body = re.sub(r'\s*data-text="[^"]*"', '', body)
    return body.strip()


def build(snips=None):
    """Compile the snippets (or load them from the cache). Returns key -> metrics and SVG drawing."""
    snips = SNIPPETS if snips is None else snips
    src = _source(snips)
    digest = hashlib.sha256(src.encode('utf-8')).hexdigest()[:16]
    meta_path = CACHE / 'snippets.json'
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding='utf-8'))
        if meta.get('hash') == digest:
            return meta['snippets']
    CACHE.mkdir(exist_ok=True)
    (CACHE / 'snips.tex').write_text(src, encoding='utf-8', newline='\n')
    run = subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'snips.tex'],
                         cwd=CACHE, capture_output=True, text=True, timeout=300)
    log = (CACHE / 'snips.log').read_text(encoding='latin-1') if (CACHE / 'snips.log').exists() else ''
    dims = {int(m.group(1)): tuple(float(m.group(i)) for i in (2, 3, 4))
            for m in re.finditer(r'SNIP:(\d+):(-?[\d.]+)pt:(-?[\d.]+)pt:(-?[\d.]+)pt', log)}
    if run.returncode or len(dims) != len(snips) or not (CACHE / 'snips.pdf').exists():
        raise RuntimeError('pdflatex failed; see ' + str(CACHE / 'snips.log') + '\n' + run.stdout[-1500:])
    doc = pymupdf.open(CACHE / 'snips.pdf')
    if len(doc) != len(snips):
        raise RuntimeError(f'expected {len(snips)} pages, got {len(doc)}')
    out = {}
    for i, (key, tex) in enumerate(snips.items()):
        page = doc[i]
        wd, ht, dp = dims[i]
        out[key] = dict(tex=tex, w_bp=page.rect.width, h_bp=page.rect.height, wd_pt=wd, ht_pt=ht, dp_pt=dp,
                        svg=_inner(page.get_svg_image(text_as_path=True)))
    doc.close()
    meta_path.write_text(json.dumps(dict(hash=digest, snippets=out), indent=1), encoding='utf-8', newline='\n')
    return out


_SNIPS = None


def metrics(key, size):
    """Width, height above the baseline and depth below it, in mm, for a snippet set at em size `size` mm."""
    global _SNIPS
    if _SNIPS is None:
        _SNIPS = build()
    sn = _SNIPS[key]
    k = size / EM_BP
    return sn['w_bp'] * k, sn['ht_pt'] * PT_TO_BP * k, sn['dp_pt'] * PT_TO_BP * k


def drawing(key, x, y, size, prefix, fill):
    """SVG for a snippet with its left baseline point at (x, y) mm and em size `size` mm, ids prefixed."""
    global _SNIPS
    if _SNIPS is None:
        _SNIPS = build()
    sn = _SNIPS[key]
    k = size / EM_BP
    base_bp = sn['h_bp'] - sn['dp_pt'] * PT_TO_BP
    inner = sn['svg']
    for i in sorted(set(re.findall(r'\bid="([^"]+)"', inner)), key=len, reverse=True):
        inner = (inner.replace(f'id="{i}"', f'id="{prefix}{i}"').replace(f'href="#{i}"', f'href="#{prefix}{i}"')
                 .replace(f'url(#{i})', f'url(#{prefix}{i})'))
    for black in ('#000000', '#000', 'black'):
        inner = inner.replace(f'fill="{black}"', f'fill="{fill}"').replace(f'stroke="{black}"', f'stroke="{fill}"')
    return (f'<g transform="translate({x:.4f} {y:.4f}) scale({k:.6f}) translate(0 {-base_bp:.4f})" fill="{fill}">'
            f'{inner}</g>')


if __name__ == '__main__':
    for key, sn in build().items():
        w, h, d = metrics(key, 6.35)
        print(f'{key:16s} {w:6.2f} x {h:5.2f} + {d:4.2f} mm at 18 pt   {sn["tex"]}')
