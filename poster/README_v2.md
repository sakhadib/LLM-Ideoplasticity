# Poster v2

The v2 poster refines the existing layout without altering its displayed copy or data. The original poster and sources remain intact.

Changes: Pagella typography and direct labels in the hero figures; clearer cyan/magenta semantics in the polytope; open-sided result panels; quieter rules; adjusted header balance and spacing. Existing narrative statistics, math, model logos, lightbulbs, and footer remain.

Build with `python poster/build_v2.py`. New figure assets can be regenerated with `python poster/src/figure_refine_v2.py`. The v2 style overrides live in `poster/src/poster_v2.css` and reuse the original copy and build pipeline.

Deliverables:

- `LLM-Ideoplasticity_Poster_A0_v2.pdf`: regular PDF with vector text/charts and original links.
- `LLM-Ideoplasticity_Poster_A0_v2_flattened.pdf`: 240 dpi print fallback.

Both are one-page A0 portrait PDFs below 20 MB. Run `python poster/verify_v2_copy.py` for exact-copy, math, chart, table, original-file hash, and link checks. Run `python poster/preflight_v2.py` for font, print, QR, and regular-versus-flattened checks. The QR preflight uses the zxingcpp dependency already present in the original Claude scratchpad; install zxing-cpp if rebuilding elsewhere.

Visual previews and validation reports are in `poster/build_v2/`. SVG copy and geometry checks are in `poster/assets/figures/v2/verification.json`.
