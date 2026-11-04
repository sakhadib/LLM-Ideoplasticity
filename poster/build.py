"""Build the A0 poster.

    python poster/build.py

Expands src/poster.html (copy from src/copy.md, charts inlined from charts/, model logos, math typeset by pdflatex in
Latin Modern), prints it with headless Chrome to LLM-Ideoplasticity_Poster_A0.pdf, sets the PDF metadata, writes a
flattened print fallback, renders previews to build/, and fails loudly on: overflow; spacing below the targets; type
sizes outside the scale; a TeX error or leftover math source; missing links; flip quotes that do not match the data;
wrong page size; an oversized file; or copy that did not reach the PDF.
"""
import ast
import hashlib
import html
import io
import json
import logging
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
import pymupdf
from PIL import Image
from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter

logging.getLogger('pypdf').setLevel(logging.ERROR)  # Chrome's xref size note is harmless; pypdf writes a correct one

ROOT = Path(__file__).resolve().parent
SRC = ROOT / 'src'
BUILD = ROOT / 'build'
CROPS = BUILD / 'crops'
MATH_CACHE = BUILD / 'math'
CHARTS = ROOT / 'charts'
ASSETS = ROOT / 'assets'
RUNS = ROOT.parent / 'Runs'
OUT_PDF = ROOT / 'LLM-Ideoplasticity_Poster_A0.pdf'
OUT_FLAT = ROOT / 'LLM-Ideoplasticity_Poster_A0_flattened.pdf'

TITLE = ('LLM-Ideoplasticity: Measuring Ideological Plasticity in the Political Behavior of LLMs '
         'as a Context-Conditioned Distribution')
AUTHORS = 'Adib Sakhawat; Syed Rifat Raiyan; Tahsin Islam; Takia Farhin; Hasan Mahmud; Md Kamrul Hasan'
PAGE_W_PT, PAGE_H_PT = 2383.94, 3370.39
MAX_MB = 20

# The type scale. The title is exempt, and so are superscript marks.
TYPE_SCALE = (17, 19, 21, 23, 25, 27, 30, 31, 36, 43, 44, 54)
# Spacing targets, in mm of clear space between inks
CLEAR_ABOVE_HEAD = 10.0
RULE_TO_CONTENT = 4.0
CLEAR_CLOSING = 8.0
FINE_TO_RULE = 5.0

LINKS_EXPECTED = {  # the title links to arXiv, the QR card to the project page
    'https://sakhadib.github.io/LLM-Ideoplasticity/',
    'https://arxiv.org/abs/2606.28335',
    'mailto:rifatraiyan@iut-dhaka.edu',
    'https://x.com/realRifatRaiyan',
}

# Table rows kept from the paper's Table 1, in its order. Dropped for air, in the user's order:
# Max. spread 3D, Total path length, JBS Strict %.
TABLE_KEEP = {
    'PSS': ['Mean 2D'], 'PIS': ['Mean PIS'], 'RSS': ['Mean RSS'], 'JBS': ['Directional %'], 'LDS': ['Mean'],
    'DS': ['Net drift', 'Tortuosity index'], 'IAS': ['For \u2212 Against'], 'OW': ['Volume 3D', 'Area 2D'],
}
GLYPH_KEYS = {'DeepSeek-V4': 'deepseek', 'Gemini-2.5-FL': 'gemini', 'Gemma-4-26B': 'gemma', 'Granite-3.3-8B': 'granite',
              'Llama-3-70B': 'llama3', 'Llama-4-Scout': 'llama4', 'GPT-5-mini': 'gpt5mini', 'Qwen-Turbo': 'qwen',
              'Grok-4.1-Fast': 'grok'}

ICONS = {p.stem: p.name for p in ASSETS.glob('icons/*.*') if p.suffix in ('.svg', '.png')}

# Regions of the page, in mm, for the zoomed review crops: name, x0, y0, x1, y1, dpi
CROP_REGIONS = [
    ('01_band', 0, 0, 841, 170, 75),
    ('02_sidebar_top', 0, 160, 290, 470, 80),
    ('03_sidebar_bottom', 0, 450, 290, 790, 80),
    ('04_hero_dek', 270, 160, 841, 450, 70),
    ('05_cards_top', 270, 430, 841, 650, 80),
    ('06_cards_bottom', 270, 600, 841, 800, 80),
    ('07_global', 0, 770, 570, 990, 80),
    ('08_table', 0, 950, 570, 1150, 80),
    ('09_mtmm', 550, 770, 841, 990, 80),
    ('10_why', 550, 950, 841, 1150, 80),
    ('11_bottom', 0, 1100, 841, 1189, 75),
]


# ---------------------------------------------------------------------------------------------------------------------
# Copy
# ---------------------------------------------------------------------------------------------------------------------

def parse_copy(path):
    """copy.md to a nested dict: block -> field -> str | list; '### sub' makes a nested block; JSON fences are kept by id."""
    data, block, sub, field = {}, None, None, None
    target = None
    fence = None
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.rstrip()
        if fence is not None:
            if line.startswith('```'):
                obj = json.loads('\n'.join(fence))
                data[block][obj['id']] = obj
                fence = None
            else:
                fence.append(line)
            continue
        if line.startswith('```json'):
            fence = []
            continue
        m = re.match(r'^##\s+(\w+)\s*$', line)
        if m:
            block = m.group(1)
            data[block] = {}
            target, sub, field = data[block], None, None
            continue
        m = re.match(r'^###\s+(\w+)\s*$', line)
        if m and block:
            sub = m.group(1)
            data[block][sub] = {}
            target, field = data[block][sub], None
            continue
        if target is None:
            continue
        m = re.match(r'^- (.*)$', line)
        if m and field:
            if not isinstance(target[field], list):
                target[field] = []
            target[field].append(m.group(1))
            continue
        m = re.match(r'^([a-z_0-9]+):\s*(.*)$', line)
        if m:
            field = m.group(1)
            target[field] = m.group(2)
            continue
    return data


def lookup(copy, dotted):
    node = copy
    for part in dotted.split('.'):
        node = node[int(part)] if isinstance(node, list) else node[part]
    if not isinstance(node, str):
        raise TypeError(f'copy field {dotted} is not text')
    return node


def icon_img(key, cls='mi'):
    return f'<img class="{cls} mi-{key}" src="../assets/icons/{ICONS[key]}" alt="">'


# ---------------------------------------------------------------------------------------------------------------------
# Math, typeset by pdflatex
# ---------------------------------------------------------------------------------------------------------------------

TEX_HEAD = r"""\documentclass[10pt]{article}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{amsmath,amssymb}
\usepackage{bm}
\usepackage[active,tightpage]{preview}
\setlength\PreviewBorder{0pt}
\pagestyle{empty}
\newsavebox\mb
\newcommand\snip[1]{\sbox\mb{#1}\typeout{SNIP:\the\wd\mb,\the\ht\mb,\the\dp\mb}\begin{preview}\usebox\mb\end{preview}}
\begin{document}
"""


class TexMath:
    """Each expression becomes one preview page of a single pdflatex run, then an inline SVG of glyph paths.
    Sizes are in em of the surrounding text (the source is set at 10 pt), so the math scales with its context."""

    def __init__(self, cache):
        self.cache = cache
        self.items, self.index = [], {}
        self.svgs = None
        self.uses = 0
        self.digest = None

    def ref(self, tex, display):
        tex = tex.strip()
        if not tex.isascii():
            raise SystemExit(f'TeX source must be ASCII: {tex!r}')
        key = (tex, bool(display))
        if key not in self.index:
            self.index[key] = len(self.items)
            self.items.append(key)
        return f'\x02{self.index[key]}\x03'

    def compile(self):
        body = ''.join('\\snip{$' + ('\\displaystyle ' if d else '') + t + '$}\n' for t, d in self.items)
        src = TEX_HEAD + body + '\\end{document}\n'
        self.digest = hashlib.sha1(src.encode('ascii')).hexdigest()[:16]
        self.cache.mkdir(parents=True, exist_ok=True)
        pdf, meta = self.cache / f'{self.digest}.pdf', self.cache / f'{self.digest}.json'
        fresh = not (pdf.exists() and meta.exists())
        if fresh:
            (self.cache / 'snips.tex').write_text(src, encoding='ascii', newline='\n')
            r = subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', 'snips.tex'], cwd=self.cache,
                               capture_output=True, text=True, encoding='utf-8', errors='replace')
            log_path = self.cache / 'snips.log'
            log = log_path.read_text(encoding='utf-8', errors='replace') if log_path.exists() else ''
            dims = [[float(v.strip().rstrip('pt')) for v in m.split(',')] for m in re.findall(r'^SNIP:(.+)$', log, flags=re.M)]
            errors = re.findall(r'^! .*$', log, flags=re.M)
            if r.returncode != 0 or errors or len(dims) != len(self.items):
                raise SystemExit(f'pdflatex failed (exit {r.returncode}): {errors[:3]}; {len(dims)} of {len(self.items)} snippets')
            (self.cache / 'snips.pdf').replace(pdf)
            meta.write_text(json.dumps(dims), encoding='utf-8')
        dims = json.loads(meta.read_text(encoding='utf-8'))
        doc = pymupdf.open(pdf)
        if len(doc) != len(self.items) or len(dims) != len(self.items):
            raise SystemExit(f'math cache {self.digest}: {len(doc)} pages for {len(self.items)} snippets')
        self.svgs = [(page.get_svg_image(text_as_path=True), *d) for page, d in zip(doc, dims)]
        fonts = sorted({f[3].split('+')[-1] for page in doc for f in page.get_fonts()})
        return fresh, fonts

    def markup(self, i):
        svg, wd, ht, dp = self.svgs[i]
        self.uses += 1
        pre = f'tx{i}u{self.uses}_'
        s = svg[svg.index('<svg'):].strip()  # a trailing newline would render as a space before punctuation
        s = re.sub(r'\bid="', f'id="{pre}', s)
        s = s.replace('href="#', f'href="#{pre}')
        s = s.replace('stroke="#000000"', 'stroke="currentColor"').replace('fill="#000000"', 'fill="currentColor"')
        end = s.index('>')
        head = re.sub(r'\s(width|height)="[^"]*"', '', s[:end])
        head = head.replace('<svg ', f'<svg class="tx" width="{wd / 10:.4f}em" height="{(ht + dp) / 10:.4f}em" '
                                     f'fill="currentColor" style="vertical-align:{-dp / 10:.4f}em" aria-hidden="true" ', 1)
        return head + s[end:]

    def substitute(self, text):
        return re.sub('\x02(\\d+)\x03', lambda m: self.markup(int(m.group(1))), text)


MATH = TexMath(MATH_CACHE)
MATH_SPLIT = re.compile(r'(\$\$.+?\$\$|\$[^$]+\$)')


def fill(text, facts=None, extra=None):
    choices = (facts or {}).get('chart_choices', {}).get('point_to_shape', {})
    text = text.replace('{{model}}', str(choices.get('model', ''))).replace('{{year}}', str(choices.get('year', '')))
    for k, v in (extra or {}).items():
        text = text.replace('{{' + k + '}}', str(v))
    return text


def inline(text, facts=None, extra=None):
    """Inline markup of copy.md to HTML. Math becomes placeholders, replaced by TeX SVGs after the whole page is expanded."""
    text = fill(text, facts, extra)
    out = []
    for p in MATH_SPLIT.split(text):
        if len(p) > 4 and p.startswith('$$') and p.endswith('$$'):
            out.append(MATH.ref(p[2:-2], True))
            continue
        if len(p) > 1 and p.startswith('$') and p.endswith('$'):
            out.append(MATH.ref(p[1:-1], False))
            continue
        p = html.escape(p, quote=False)
        marks = []

        def keep_mark(m):
            marks.append(m.group(1))
            return f'\x00{len(marks) - 1}\x00'

        p = re.sub(r'&lt;sup&gt;(.*?)&lt;/sup&gt;', keep_mark, p)  # author marks hold literal asterisks
        p = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', p)
        p = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<i>\1</i>', p)
        p = re.sub(r'\x00(\d+)\x00', lambda m: f'<sup>{marks[int(m.group(1))]}</sup>', p)
        p = re.sub(r'\[\[sc:(.+?)\]\]', r'<span class="sc">\1</span>', p)  # muted all-small-caps
        p = p.replace('~', '\u00a0')  # no-break space, as in TeX
        p = re.sub(r'/(?=[A-Z])', '/<wbr>', p)  # long slash compounds may break after the slash
        p = p.replace("'", '\u2019')  # typographic apostrophes
        p = re.sub(r'(one-third|in-sample)', r'<span class="mn">\1</span>', p)
        p = re.sub(r'\b(lrgen|lrecon|galtan)\b', r'<i class="axis">\1</i>', p)  # the paper italicizes the CHES dimensions
        p = re.sub(r'(\(?)\[\[model:(\w+)\]\]([\w.\-]+)',
                   lambda m: f'<span class="mn">{m.group(1)}{icon_img(m.group(2))}{m.group(3)}</span>', p)
        p = re.sub(r'\[\[model:(\w+)\]\]', lambda m: icon_img(m.group(1)), p)
        p = re.sub(r'\[\[cyan:(.+?)\]\]', r'<span class="c-party">\1</span>', p)
        p = re.sub(r'\[\[magenta:(.+?)\]\]', r'<span class="c-llm">\1</span>', p)
        out.append(p)
    joined = ''.join(out)
    # Keep math on one line with the brackets and punctuation that touch it
    return re.sub('([^\\s<>]*)(\x02\\d+\x03)([^\\s<>]*)', lambda m: f'<span class="mn">{m.group(1)}{m.group(2)}{m.group(3)}</span>' if (m.group(1) or m.group(3)) else m.group(2), joined)


def plain_segments(text, facts=None, extra=None):
    """The Latin-script text runs of a copy field, for checking they reached the PDF."""
    text = fill(text, facts, extra)
    text = re.sub(r'<sup>.*?</sup>', '$ $', text)
    text = re.sub(r'\[\[model:\w+\]\]', '', text)
    text = re.sub(r'\[\[(?:cyan|magenta|sc):(.+?)\]\]', r'\1', text)
    text = text.replace('**', '').replace('*', '').replace('~', ' ')
    segs = MATH_SPLIT.split(text)
    segs = [s for s in segs if not s.startswith('$')]
    return [s.strip() for s in segs if re.search(r'[A-Za-z]{3}', s) and not re.search(r'[\u0980-\u09ff]', s)]


# ---------------------------------------------------------------------------------------------------------------------
# Charts, table, flips
# ---------------------------------------------------------------------------------------------------------------------

def chart(name, opts=''):
    """Inline an SVG chart at its native size. Options: crop=x,y,w,h trims the viewBox (no scaling, so type sizes hold)."""
    svg = (CHARTS / f'{name}.svg').read_text(encoding='utf-8').strip()
    kw = dict(o.split('=') for o in opts.split(',,') if o)
    head_end = svg.index('>')
    head = svg[:head_end]
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', head).group(1).split()]
    if 'crop' in kw:
        vb = [float(v) for v in kw['crop'].split(',')]
        head = re.sub(r'viewBox="[^"]+"', 'viewBox="' + ' '.join(f'{v:g}' for v in vb) + '"', head)
    w_mm = float(kw.get('w', vb[2]))
    h_mm = w_mm * vb[3] / vb[2]
    head = re.sub(r' width="[^"]+"', '', head)
    head = re.sub(r' height="[^"]+"', '', head)
    head += f' width="{w_mm:g}mm" height="{h_mm:g}mm"'
    return head + svg[head_end:]


PLACEHOLDERS = []


def chart_or_placeholder(name, opts=''):
    """A chart that may not exist yet: inline it at its native size, or hold a box of the size given (w=, h= in mm)."""
    if (CHARTS / f'{name}.svg').exists():
        return chart(name)
    kw = dict(o.split('=') for o in opts.split(',,') if o)
    PLACEHOLDERS.append(name)
    return f'<div class="ph" style="width:{kw["w"]}mm;height:{kw["h"]}mm">{name}</div>'


def table_rows(copy):
    t = copy['s6_table']['table1_abridged']
    return sum(1 for g in t['groups'] for r in g['rows'] if r['label'] in TABLE_KEEP[g['metric']])


def per_model_table(copy, opts=''):
    t = copy['s6_table']['table1_abridged']
    kw = dict(o.split('=') for o in opts.split(',,') if o)
    glyph_mm = float(kw.get('glyph', 26))
    head1 = ['<tr class="t-glyphs"><th class="t-row-h" colspan="2">' + inline(copy['s6_table']['glyph_row_label'])
             + '<span class="t-sh">' + inline(copy['s6_table']['glyph_note']) + '</span></th>']
    head2 = ['<tr class="t-names"><th colspan="2"></th>']
    for m in t['models']:
        head1.append(f'<th>{chart("hull_glyphs/" + GLYPH_KEYS[m["label"]], f"w={glyph_mm:g}")}</th>')
        head2.append(f'<th><span class="mn">{icon_img(m["icon"], "mi")}{html.escape(m["label"])}</span></th>')
    rows = [''.join(head1) + '</tr>', ''.join(head2) + '</tr>']
    for g in t['groups']:
        keep = [r for r in g['rows'] if r['label'] in TABLE_KEEP[g['metric']]]
        for i, r in enumerate(keep):
            cls = ['t-first' if i == 0 else '', 't-last' if i == len(keep) - 1 else '']
            cells = [f'<tr class="{" ".join(c for c in cls if c)}">']
            if i == 0:
                cells.append(f'<th class="t-metric" rowspan="{len(keep)}">{g["metric"]}</th>')
            cells.append(f'<td class="t-label">{html.escape(r["label"])}</td>')
            for val, hi, bold in r['cells']:
                c = (f'hi-{hi} ' if hi else '') + ('t-bold' if bold else '')
                cells.append(f'<td class="t-num {c.strip()}"><span>{html.escape(val)}</span></td>')
            cells.append('</tr>')
            rows.append(''.join(cells))
    cols = '<colgroup><col class="col-metric"><col class="col-label">' + '<col>' * len(t['models']) + '</colgroup>'
    return '<table class="fingerprints">' + cols + ''.join(rows) + '</table>'


LIKERT = ('CD', 'D', 'N', 'A', 'CA')


def likert(copy, key, used):
    """Two rows of a five-step agreement scale (completely disagree to completely agree); the judged step is filled."""
    f = copy['flips']
    flip = f[key]
    ends = (f'<div class="lk-ends"><span></span><span class="lk-scale-ends"><span>{inline(f["scale_left"])}</span>'
            f'<span>{inline(f["scale_right"])}</span></span><span></span></div>')
    used += [f['scale_left'], f['scale_right']]
    rows = []
    for field in ('row_a', 'row_b'):
        lab, code, verdict = [x.strip() for x in flip[field].split(' | ')]
        if code not in LIKERT:
            raise SystemExit(f'flip {key}: unknown step {code}')
        used += [lab, verdict]
        dots = ''.join(f'<span class="lk-slot"><span class="lk-dot{" on" if c == code else ""}"></span></span>' for c in LIKERT)
        rows.append(f'<div class="lk-row"><span class="lk-lab">{inline(lab)}</span><span class="lk-dots">{dots}</span>'
                    f'<span class="lk-v">{inline(verdict)}</span></div>')
    return '<div class="lk">' + ends + ''.join(rows) + '</div>'


def verify_flips(copy):
    """The flip example must match the stored replies and judge verdicts exactly."""
    problems = []
    f = copy['flips']
    # S21_09: Grok-4.1-Fast, multiple choice vs. chain-of-thought, ten paraphrases each
    want = {'Runs/PIS/stance.csv': 'D' * 10, 'Runs/RSS/stance.csv': 'A' * 10}
    for rel, expect in want.items():
        d = pd.read_csv(RUNS.parent / rel)
        got = ''.join(d[(d.model == 'x-ai_grok-4.1-fast') & (d.variable == 'S21_09')].sort_values('prompt_id', key=lambda s: s.str[1:].astype(int)).response)
        if got != expect:
            problems.append(f'{rel}: S21_09 responses {got!r}, poster says {expect[0]} x10')
    for field, step in (('row_a', 'D'), ('row_b', 'A')):
        if f['reasoning_flip'][field].split(' | ')[1].strip() != step:
            problems.append(f'reasoning_flip {field} step differs from the data ({step})')
    # S1_09: English vs. Bangla
    data = json.load(open(RUNS / 'LDS' / 'responses' / 'x-ai_grok-4.1-fast.json', encoding='utf-8'))
    item = next(x for x in data if x['variable'] == 'S1_09')
    resp = item['responses']
    if isinstance(resp, str):
        try:
            resp = json.loads(resp)
        except json.JSONDecodeError:
            resp = ast.literal_eval(resp)
    by = {r['language']: r for r in resp}
    lf = f['language_flip']
    for part in (lf['excerpt_bn_head'], lf['excerpt_bn_clause']):
        if part not in by['Bengali']['response']:
            problems.append(f'Bangla excerpt not verbatim in the reply: {part}')
    en = lf['excerpt_en'].strip('\u201c\u201d').rstrip('\u2026')
    if en not in by['English']['response']:
        problems.append('English excerpt not verbatim in the reply')
    for field, lang in (('row_a', 'English'), ('row_b', 'Bengali')):
        step = lf[field].split(' | ')[1].strip()
        if by[lang]['judgement']['inference'] != step:
            problems.append(f'language_flip {field}: judge says {by[lang]["judgement"]["inference"]}, poster says {step}')
    return problems


def year_panels(copy, used):
    subs = [s.strip() for s in lookup(copy, 's4_global.chrono_subs').split('|')]
    used += subs
    cells = []
    for y, sub in zip((2009, 2014, 2019), subs):
        if (CHARTS / f'chrono_2d_{y}.svg').exists():
            fig = chart(f'chrono_2d_{y}')
        else:
            fig = f'<img src="../assets/figures/polytope_chrono_2d_{y}.svg" alt="{y}">'
        cells.append(f'<div class="yr">{fig}<div class="subcap">{inline(sub)}</div></div>')
    return '<div class="yrs">' + ''.join(cells) + '</div>'


# ---------------------------------------------------------------------------------------------------------------------
# Expansion
# ---------------------------------------------------------------------------------------------------------------------

def expand(template, copy, facts):
    used = []
    extra = {'rows': table_rows(copy)}

    def copy_sub(m):
        text = lookup(copy, m.group(1))
        if m.group(3) is not None:  # '#n' picks one part of a ' | '-separated field
            text = text.split(' | ')[int(m.group(3))]
        used.append(text)
        return inline(text, facts, extra)

    s = re.sub(r'\{\{table(\|([^}]*))?\}\}', lambda m: per_model_table(copy, m.group(2) or ''), template)
    s = re.sub(r'\{\{likert:(\w+)\}\}', lambda m: likert(copy, m.group(1), used), s)
    s = s.replace('{{years}}', year_panels(copy, used))
    s = re.sub(r'\{\{chart\?:([\w/]+)(\|([^}]*))?\}\}', lambda m: chart_or_placeholder(m.group(1), m.group(3) or ''), s)
    s = re.sub(r'\{\{chart:([\w/]+)(\|([^}]*))?\}\}', lambda m: chart(m.group(1), m.group(3) or ''), s)
    s = re.sub(r'\{\{c:([\w.]+)(#(\d+))?\}\}', copy_sub, s)
    s = re.sub(r'\[\[model:(\w+)\]\]', lambda m: icon_img(m.group(1)), s)
    fresh, tex_fonts = MATH.compile()
    s = MATH.substitute(s)
    return s, used, extra, fresh, tex_fonts


def leftover_math(built):
    """Math source left in the visible page: a '$' or a TeX command outside SVGs, scripts and styles."""
    visible = re.sub(r'<(svg|script|style)\b.*?</\1>', '', built, flags=re.S)
    visible = re.sub(r'<[^>]+>', ' ', visible)
    return re.findall(r'.{0,30}(?:\$|\\[a-zA-Z]+\{|\\\().{0,30}', visible)


# ---------------------------------------------------------------------------------------------------------------------
# Checks run inside the page
# ---------------------------------------------------------------------------------------------------------------------

CHECK_JS = r"""
(scale) => {
  const mm = v => v / (96 / 25.4);
  const page = document.querySelector('.page').getBoundingClientRect();
  const box = el => { const r = el.getBoundingClientRect(); return [mm(r.left - page.left), mm(r.top - page.top), mm(r.right - page.left), mm(r.bottom - page.top)]; };
  const nameOf = c => (c.tagName + '.' + (c.className.baseVal === undefined ? c.className : c.className.baseVal)).slice(0, 40);
  const out = {overflow: [], stacks: [], outside: [], widows: [], sizes: {}, heads: [], marks: {}};
  // Anything that extends past its [data-fit] box (outermost SVGs only: what they contain is clipped to them)
  document.querySelectorAll('[data-fit]').forEach(el => {
    const r = el.getBoundingClientRect();
    let maxB = r.top, maxR = r.left, minL = r.right, minT = r.bottom, who = '';
    el.querySelectorAll('*').forEach(c => {
      if (c.closest('.contours') || c.parentElement.closest('svg')) return;
      if (c.classList.contains('bulb-c')) return;  // the corner bulbs sit half outside their boxes by design
      const q = c.getBoundingClientRect();
      if (q.width === 0 || q.height === 0) return;
      if (q.bottom > maxB) who = nameOf(c);
      maxB = Math.max(maxB, q.bottom); maxR = Math.max(maxR, q.right);
      minL = Math.min(minL, q.left); minT = Math.min(minT, q.top);
    });
    const over = {b: mm(maxB - r.bottom), r: mm(maxR - r.right), l: mm(r.left - minL), t: mm(r.top - minT)};
    if (over.b > .4 || over.r > .4 || over.l > .4 || over.t > 2.5) {
      out.overflow.push({el: el.dataset.fit, bottom: +over.b.toFixed(1), right: +over.r.toFixed(1), left: +over.l.toFixed(1), top: +over.t.toFixed(1), who});
    }
  });
  // Free height in the stacks, and the measured gap above each block
  document.querySelectorAll('[data-stack]').forEach(el => {
    const r = el.getBoundingClientRect();
    let used = 0, prev = null;
    const kids = [], gaps = [];
    Array.from(el.children).forEach(c => {
      const q = c.getBoundingClientRect();
      used += q.height;
      const name = String((c.dataset && (c.dataset.fit || c.dataset.stack)) || c.className || c.tagName).slice(0, 12);
      kids.push(name + ':' + mm(q.height).toFixed(0));
      if (prev) gaps.push({gap: +mm(q.top - prev.bottom).toFixed(1), name});
      prev = q;
    });
    out.stacks.push({el: el.dataset.stack, height: +mm(r.height).toFixed(1), free: +mm(r.height - used).toFixed(1), kids: kids.join(' '), gapList: gaps});
  });
  // Nothing crosses the page
  document.querySelectorAll('.page *').forEach(c => {
    if (c.closest('.contours') || c.parentElement.closest('svg')) return;
    const q = c.getBoundingClientRect();
    if (q.width === 0 || q.height === 0) return;
    if (q.right > page.right + 2 || q.bottom > page.bottom + 2 || q.left < page.left - 2 || q.top < page.top - 2) out.outside.push(nameOf(c));
  });
  // Single-word last lines
  document.querySelectorAll('.sec, .cap, .subcap, p, li').forEach(el => {
    const range = document.createRange();
    range.selectNodeContents(el);
    const rects = Array.from(range.getClientRects()).filter(r => r.width > 1);
    if (rects.length < 2) return;
    const lastTop = Math.max(...rects.map(r => r.top));
    const lastW = rects.filter(r => Math.abs(r.top - lastTop) < 6).reduce((a, r) => a + r.width, 0);
    if (lastW < el.getBoundingClientRect().width * 0.12) out.widows.push((el.textContent || '').trim().slice(-48));
  });
  // Type sizes outside the scale (the title and superscripts are exempt)
  document.querySelectorAll('.page *').forEach(el => {
    if (el.closest('svg') || el.closest('sup') || el.closest('.t1')) return;
    const own = Array.from(el.childNodes).some(n => n.nodeType === 3 && n.textContent.trim());
    if (!own) return;
    const pt = parseFloat(getComputedStyle(el).fontSize) * 72 / 96;
    if (!scale.some(a => Math.abs(a - pt) < 0.06)) {
      const k = pt.toFixed(2);
      (out.sizes[k] = out.sizes[k] || []).push(nameOf(el));
    }
  });
  // Geometry for the ink-based spacing checks
  document.querySelectorAll('h2.sec').forEach(h => out.heads.push({text: h.textContent.trim().slice(0, 32), box: box(h), col: box(h.parentElement)}));
  ['.rule-top', '.thesis', '.th-line', '.th-epi', '.closing', '.closing span', '.fine', '.rule-foot', '.lower', '.upper', '.dek', '.hero .cap'].forEach(sel => {
    const e = document.querySelector(sel);
    if (e) out.marks[sel] = box(e);
  });
  out.fonts = Array.from(document.fonts).filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight + ' ' + f.style);
  out.mathjax = document.querySelectorAll('mjx-container, script[src*="tex-svg"], script[src*="mathjax"]').length;
  out.tex = document.querySelectorAll('svg.tx').length;
  return out;
}
"""


def norm(s):
    s = unicodedata.normalize('NFKC', s)
    s = re.sub(r'[\s\u00ad]+', '', s)
    return s.replace('\u2019', "'").replace('\u2018', "'").replace('\u201c', '"').replace('\u201d', '"')


# ---------------------------------------------------------------------------------------------------------------------
# Ink-based spacing checks on the rendered page
# ---------------------------------------------------------------------------------------------------------------------

class Ink:
    def __init__(self, page, dpi=150):
        pix = page.get_pixmap(dpi=dpi, alpha=False)
        a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
        self.ink = a.min(axis=2) < 250
        self.s = dpi / 25.4

    def rows(self, x0, x1):
        X0, X1 = max(int(x0 * self.s) + 2, 0), int(x1 * self.s) - 2
        return self.ink[:, X0:X1].any(axis=1)

    def first(self, x0, x1, y0, y1):
        """First ink row (mm) scanning from y0 towards y1."""
        r = self.rows(x0, x1)
        a, b = int(y0 * self.s), int(y1 * self.s)
        rng = range(a, b, 1) if b >= a else range(a, b, -1)
        for i in rng:
            if 0 <= i < len(r) and r[i]:
                return i / self.s
        return None


def spacing_report(page, report):
    ink = Ink(page)
    lines, problems = [], []
    marks = report['marks']
    for h in report['heads']:
        x0, y0, x1, y1 = h['box']
        cx0, _, cx1, _ = h['col']
        top = ink.first(cx0, cx1, y0, y1)                 # the heading's own ink
        above = ink.first(cx0, cx1, top - .3, top - 60)   # nearest ink above it
        below = ink.first(cx0, cx1, y1 + .4, y1 + 40)     # first content under its rule
        clear = (top - above) if above is not None else 99
        to_content = (below - y1) if below is not None else 99
        need = 8.0 if h['text'].startswith('1') else CLEAR_ABOVE_HEAD
        lines.append(f"  {h['text']:<34} clear above {clear:5.1f}   rule to content {to_content:4.1f}")
        if clear < need - .05:
            problems.append(f"{h['text']}: {clear:.1f} mm clear above, needs {need:g}")
        if to_content < RULE_TO_CONTENT - .05:
            problems.append(f"{h['text']}: {to_content:.1f} mm from rule to content, needs {RULE_TO_CONTENT:g}")
    if '.closing span' in marks:
        cx0, cy0, cx1, cy1 = marks['.closing span']
        top = ink.first(cx0, cx1, cy0 - 3, cy1 + 3)
        bot = ink.first(cx0, cx1, cy1 + 3, cy0 - 3)
        above = ink.first(20, 821, top - .3, top - 40)
        below = ink.first(20, 821, bot + .3, bot + 40)
        ca, cb = top - above, below - bot
        lines.append(f'  closing line                       clear above {ca:5.1f}   clear below {cb:5.1f}')
        if min(ca, cb) < CLEAR_CLOSING - .05:
            problems.append(f'closing line: {ca:.1f} / {cb:.1f} mm clear, needs {CLEAR_CLOSING:g}')
    if '.fine' in marks and '.rule-foot' in marks:
        fx0, fy0, fx1, fy1 = marks['.fine']
        rule_top = marks['.rule-foot'][1]
        last = ink.first(20, 821, rule_top - .3, fy0)
        gap = rule_top - last
        lines.append(f'  fine print to footer rule          {gap:5.1f}')
        if gap < FINE_TO_RULE - .05:
            problems.append(f'fine print: {gap:.1f} mm above the footer rule, needs {FINE_TO_RULE:g}')
    if '.dek' in marks:
        dx0, dy0, dx1, dy1 = marks['.dek']
        top = ink.first(dx0, dx1, dy0 - 2, dy1)
        above = ink.first(dx0, dx1, top - .3, top - 60)
        bottom = ink.first(dx0, dx1, dy1 + 2, dy0)
        lines.append(f'  dek: clear above {top - above:5.1f}   height {bottom - top:5.1f} (ink)')
        if top - above < 8 - .05:
            problems.append(f'dek: {top - above:.1f} mm clear above, needs 8')
    if '.th-line' in marks and '.rule-top' in marks:
        rule_bot = marks['.rule-top'][3]
        tx0, ty0, tx1, ty1 = marks['.th-line']
        top = ink.first(tx0, tx1, rule_bot + .3, ty1)
        ex0, ey0, ex1, ey1 = marks['.th-epi']
        ebot = ink.first(ex0, ex1, ey1 + 2, ey0)
        nxt = ink.first(20, 821, ebot + .3, ebot + 40)
        lines.append(f'  thesis line: rule to ink {top - rule_bot:4.1f}; epigraph ink to next ink {nxt - ebot:4.1f}')
    return lines, problems


# ---------------------------------------------------------------------------------------------------------------------

def flatten(src_pdf, out_pdf, dpi=200, max_mb=20):
    """Print-safety fallback: the page as one high-quality JPEG in a one-page A0 PDF, for a print shop whose RIP mishandles the vector file."""
    src = pymupdf.open(src_pdf)
    pix = src[0].get_pixmap(dpi=dpi, alpha=False)  # MuPDF: clean on hairlines and soft masks
    im = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    data, used_q = b'', None
    for q in (92, 90, 88, 86, 84, 82, 80):
        buf = io.BytesIO()
        im.save(buf, 'JPEG', quality=q, subsampling=0, optimize=True, dpi=(dpi, dpi))
        data, used_q = buf.getvalue(), q
        if len(data) < (max_mb - .4) * 1e6:
            break
    out = pymupdf.open()
    page = out.new_page(width=PAGE_W_PT, height=PAGE_H_PT)
    page.insert_image(page.rect, stream=data)
    out.set_metadata({'title': TITLE + ' (flattened for printing)', 'author': AUTHORS, 'subject': 'AACL-IJCNLP 2026 poster'})
    out.save(out_pdf)
    return pix.width, pix.height, used_q


# ---------------------------------------------------------------------------------------------------------------------

def main():
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    BUILD.mkdir(exist_ok=True)
    CROPS.mkdir(exist_ok=True)
    copy = parse_copy(SRC / 'copy.md')
    facts = json.load(open(ROOT / 'data' / 'facts.json', encoding='utf-8'))
    problems = verify_flips(copy)
    template = (SRC / 'poster.html').read_text(encoding='utf-8')
    built, used, extra, fresh, tex_fonts = expand(template, copy, facts)
    print(f'math: {len(MATH.items)} expressions, {MATH.uses} placements, pdflatex {"ran" if fresh else "cached"} ({MATH.digest}); TeX fonts {tex_fonts}')
    left = leftover_math(built)
    if left:
        problems.append(f'{len(left)} unreplaced math sources, e.g. {left[:3]}')
    if re.search(r'mathjax|tex-svg\.js|mjx-', built, flags=re.I):
        problems.append('MathJax remains in the built page')
    built_path = BUILD / 'poster.built.html'
    built_path.write_text(built, encoding='utf-8', newline='\n')

    raw_pdf = BUILD / 'poster.raw.pdf'
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel='chrome')
        except Exception:
            browser = p.chromium.launch(channel='msedge')
        page = browser.new_page(viewport={'width': 3179, 'height': 4494})
        msgs = []
        page.on('console', lambda m: msgs.append(m.text) if m.type in ('error', 'warning') else None)
        page.on('pageerror', lambda e: msgs.append('PAGEERROR ' + str(e)))
        page.on('requestfailed', lambda r: msgs.append('REQFAILED ' + r.url[:140]))
        page.goto(built_path.resolve().as_uri(), wait_until='load', timeout=180000)
        page.evaluate('document.fonts.ready')
        page.wait_for_timeout(300)
        page.emulate_media(media='print')
        report = page.evaluate(CHECK_JS, list(TYPE_SCALE))
        page.pdf(path=str(raw_pdf), print_background=True, prefer_css_page_size=True,
                 margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'})
        browser.close()

    reader = PdfReader(str(raw_pdf))
    writer = PdfWriter(clone_from=reader)
    writer.add_metadata({'/Title': TITLE, '/Author': AUTHORS, '/Subject': 'AACL-IJCNLP 2026 poster',
                         '/Keywords': 'LLM, political ideology, conditional distribution, VAA, CHES, Overton window'})
    with open(OUT_PDF, 'wb') as fh:
        writer.write(fh)

    doc = pymupdf.open(OUT_PDF)
    pg = doc[0]
    w_pt, h_pt = pg.rect.width, pg.rect.height
    pg.get_pixmap(dpi=int(round(1700 / (h_pt / 72))), alpha=False).save(BUILD / 'preview_full.png')
    pg.get_pixmap(dpi=int(round(640 / (h_pt / 72))), alpha=False).save(BUILD / 'thumb.png')
    mm_pt = 72 / 25.4
    for name, x0, y0, x1, y1, dpi in CROP_REGIONS:
        clip = pymupdf.Rect(x0 * mm_pt, y0 * mm_pt, x1 * mm_pt, min(y1 * mm_pt, h_pt))
        pg.get_pixmap(dpi=dpi, clip=clip, alpha=False).save(CROPS / f'{name}.png')

    print('stacks (mm of free height):')
    for s in report['stacks']:
        print(f"  {s['el']:<12} h={s['height']:<7} free={s['free']:<7} | {s['kids']}")
        print('      gaps:', ' '.join(f"{g['name']}={g['gap']}" for g in s['gapList']))
        if s['free'] < -.4:
            problems.append(f"stack {s['el']} overflows by {-s['free']} mm")
    if report['overflow']:
        print('overflow:')
        for o in report['overflow']:
            print('  ', o)
            problems.append(f"overflow in {o['el']}")
    if report['outside']:
        problems.append('outside page: ' + ', '.join(sorted(set(report['outside']))[:10]))
    if report['widows']:
        print('short last lines:', report['widows'])
    if report['sizes']:
        for k, v in sorted(report['sizes'].items(), key=lambda kv: float(kv[0])):
            print(f'  size {k} pt outside the scale: {sorted(set(v))[:6]}')
        problems.append(f"{len(report['sizes'])} type sizes outside the scale")
    if report['mathjax']:
        problems.append('MathJax elements in the page')
    if msgs:
        print('browser messages:', msgs[:12])

    lines, gap_problems = spacing_report(pg, report)
    print('spacing (mm of clear space between inks):')
    print('\n'.join(lines))
    problems += gap_problems

    if len(doc) != 1:
        problems.append(f'{len(doc)} pages')
    if abs(w_pt - PAGE_W_PT) > 1.5 or abs(h_pt - PAGE_H_PT) > 1.5:
        problems.append(f'page size {w_pt:.2f} x {h_pt:.2f} pt')
    size_mb = OUT_PDF.stat().st_size / 1e6
    if size_mb > MAX_MB:
        problems.append(f'file is {size_mb:.1f} MB')

    # Copy reached the PDF
    pdf_text = norm(pg.get_text('text'))
    missing = [seg[:90] for text in used for seg in plain_segments(text, facts, extra) if norm(seg) not in pdf_text]
    if missing:
        problems.append(f'{len(missing)} copy segments missing from the PDF')
        for m in missing[:30]:
            print('  missing', m)

    # Reference numbers: [2]-[5] appear only in the reference list; [1], [6], [7] also as citations
    raw_text = pg.get_text('text')
    for n in range(1, 8):
        need = 2 if n in (1, 6, 7) else 1
        if raw_text.count(f'[{n}]') < need:
            problems.append(f'reference number [{n}] missing from the reference list')

    # Links
    uris = sorted({l.get('uri') for l in pg.get_links() if l.get('uri')})
    print('links:', uris)
    lost = LINKS_EXPECTED - set(uris)
    if lost:
        problems.append(f'links missing: {sorted(lost)}')

    fonts = sorted({f[3] for f in pg.get_fonts()})
    types = sorted({f[2] for f in pg.get_fonts()})
    if any('MJX' in f or 'MathJax' in f for f in fonts):
        problems.append('MathJax fonts in the PDF')
    if any('JetBrains' in f for f in fonts):
        problems.append('JetBrains Mono is still embedded (numerals should be LM Roman, mono lines LM Mono)')
    if any(t == 'Type3' for t in types):
        problems.append('Type 3 fonts in the PDF')
    if PLACEHOLDERS:
        problems.append(f'placeholders held for missing charts: {PLACEHOLDERS}')

    w_px, h_px, q = flatten(OUT_PDF, OUT_FLAT)
    flat_mb = OUT_FLAT.stat().st_size / 1e6
    print(f'flattened: {w_px} x {h_px} px, JPEG quality {q}, {flat_mb:.2f} MB')
    if flat_mb > MAX_MB:
        problems.append(f'flattened file is {flat_mb:.1f} MB')

    print(f'pages {len(doc)} | {w_pt:.2f} x {h_pt:.2f} pt | {size_mb:.2f} MB | images {len(pg.get_images())} | font types {types} | TeX svgs {report["tex"]}')
    print('fonts:', fonts)
    print(f'{len(used)} copy fields used; {extra["rows"]} table rows')
    if problems:
        print('PROBLEMS:')
        for pr in problems:
            print('  -', pr)
        sys.exit(1)
    print('OK')


if __name__ == '__main__':
    main()
