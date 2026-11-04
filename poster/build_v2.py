"""Build the v2 refinement without modifying the approved original or its sources.

    python poster/build_v2.py          # full PDF, flattened PDF, previews, QA
    python poster/build_v2.py --draft  # fast layout review; skips flattening

All copy, math, charts and tables are expanded through the original build code.
"""
import json
import sys
from pathlib import Path

import build as base

ROOT = Path(__file__).resolve().parent
base.BUILD = ROOT / 'build_v2'
base.CROPS = base.BUILD / 'crops'
base.OUT_PDF = ROOT / 'LLM-Ideoplasticity_Poster_A0_v2.pdf'
base.OUT_FLAT = ROOT / 'LLM-Ideoplasticity_Poster_A0_v2_flattened.pdf'

original_expand = base.expand


def expand_v2(template, copy, facts):
    template = template.replace('</head>', '<link rel="stylesheet" href="../src/poster_v2.css">\n</head>')
    for name in ('fig1a_parties', 'fig1b_llms', 'polytope_3d'):
        asset = ROOT / 'assets' / 'figures' / 'v2' / (name + '.svg')
        if not asset.exists():
            raise FileNotFoundError(f'Missing v2 figure: {asset}; run poster/src/figure_refine_v2.py')
        template = template.replace(f'../assets/figures/{name}.svg', f'../assets/figures/v2/{name}.svg')
    return original_expand(template, copy, facts)


base.expand = expand_v2
original_spacing = base.spacing_report


def spacing_v2(page, report):
    (base.BUILD / 'layout_report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return original_spacing(page, report)


base.spacing_report = spacing_v2
original_flatten = base.flatten


def flatten_v2(src, out, **kwargs):
    # 240 dpi provides finer type in the print fallback while remaining below 20 MB.
    return original_flatten(src, out, dpi=240, max_mb=20)


base.flatten = flatten_v2
if '--draft' in sys.argv:
    def draft_flatten(src, out, **kwargs):
        # main() expects a file to inspect; keep the draft explicitly within build_v2.
        import shutil
        shutil.copyfile(src, out)
        return 0, 0, 0
    base.OUT_FLAT = base.BUILD / 'draft_flatten_placeholder.pdf'
    base.flatten = draft_flatten

if __name__ == '__main__':
    base.main()
