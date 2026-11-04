# Poster charts

Regenerate with `python poster/src/charts/build_charts.py`. It also rewrites `poster/data/facts.json`, `verification.md` and `contact_sheet.html/.png`, and cleans the three `chrono_2d_*` panels. It appends to `poster/data/discrepancies.md` and never rewrites that file.

**Math** is set with real TeX (pdflatex, Latin Modern) by `src/charts/texkit.py` and embedded as glyph paths. The results are cached in `src/charts/tex_cache/`; pdflatex reruns only when a snippet changes.

**Using a chart:**
- Paste the file's `<svg>` inline in the HTML so it can use the page fonts from `assets/fonts/fonts.css`; an SVG inside `<img>` cannot see them.
- Each file is 1 unit = 1 mm, with `width` and `height` in mm. Print it at 1:1: every span is 17 pt or more only at that scale.
- `mtmm` is exactly 140 mm wide, so `w=140` is 1:1.
- The compasses are 75.4 mm square, to match the 75.4 mm card column. Each has 0.2 mm of air on every side and `overflow="visible"`, so a mark on the frame keeps its ring.
- Ids are prefixed per file, and nothing is duplicated across charts. There is no `<style>`.

**Captions:** the line under a chart is in `<g class="ch-caption">`. To set your own, hide it with `.ch-caption{display:none}` and crop with `viewBox`.

**Type:**
- Words are Pagella, with variable names (*lrecon*, *galtan*, *lrgen*) in Pagella italic.
- Numerals are Latin Modern Roman (`'LM Roman Poster'`, 400 and 700, from `assets/fonts/fonts.css`), with true minus signs. No chart uses JetBrains Mono.
  - LM digits are tabular within a weight but not across weights, so a column that must align, such as the IAS values and the `mtmm` cells, uses one weight. In `mtmm`, every cell is right-aligned at one offset, so the decimal points line up.
  - LM has no ≈, so "≈" stays in Pagella.
  - Fraunces display figures (the coverage percentages and the monoculture ratio) are unchanged.
- Years and model names are Pagella; model tags inside a plot are italic.
- Math is Latin Modern: ℙ(*position* | *context*), ⟨*lrgen*, *lrecon*, *galtan*⟩, RSS > 1.2, RSS < 0.8, |IAS| > 0.15 and PIS<sub>direct</sub> = 0.

| File | W x H mm | Shows |
|:---|---:|:---|
| `point_to_shape` | 190 x 59.4 | Qwen-Turbo 2009: neutral-register dot vs. KDE contours of its 44 contexts |
| `compass_legend` | 61.6 x 60.4 | Key to every small compass |
| `pipeline` | 109.34 x 107.49 | The paper's Figure 2 at 17 pt, formula included |
| `pss_compass` | 75.4 x 75.4 | Gemma-4-26B 2019: C4 to C1, C2, C3; 0.5721 |
| `pis_compass` | 75.4 x 75.4 | Qwen-Turbo vs. Gemma-4-26B, 2009, ten paraphrases |
| `rss_compass` | 75.4 x 75.4 | Gemini-2.5-Flash-Lite 2019: direct (hollow, dashed) vs. chain of thought (solid), x3 lens |
| `rss_waffle` | 167.4 x 26.9 | 17 / 5 / 5 of 27 configurations; one LM ∞ under a bracket marks the three infinite cells, since LM's ∞ is wider than a cell |
| `lds_compass` | 75.4 x 75.4 | DeepSeek-V4-Flash 2009: English to eleven languages |
| `lds_bars` | 120 x 31.8 | The four largest language means; the seven others as one range |
| `ds_compass` | 75.4 x 75.4 | Debate paths: GPT-5-mini 2009, Qwen-Turbo 2014 (x4 lens), Gemma-4-26B 2009 |
| `ias_dumbbell` | 138 x 76 | For vs. against, sorted by IAS; all nine values, emphasis by colour |
| `coverage_bars` | 377.3 x 74 | Coverage drawn to scale: 2D, 1D, 3D |
| `monoculture` | 150 x 46 | 0.60 vs. 0.173, to scale; ratio about 0.29; the caption sits below y = 38 |
| `mtmm` | 140 x 132.45 | Cross-metric correlations, lower triangle, diverging |
| `pca_bars` | 240 x 30 | 37.82 / 26.20 / 19.28 / remainder |
| `instrument_matrix` | 257.67 x 73.38 | Section 7: each need's instrument on the diagonal; the single-prompt compass score answers none. Full column width, 1:1; no lead or tail text |
| `hull_glyphs/<key>` | 34 x 34 | Per-model hulls for the table header; keys in `facts.json` |
| `band_contours` | 841 x 130 | White KDE contours of all nine LLMs for the top band; set opacity in CSS |
| `chrono_2d_{2009,2014,2019}` | square viewBox, 339.5 units | The paper's per-year 2D hulls without their 4–5 pt axis text; use as `<img>` |
| `pss_bars`, `pis_bars`, `pis_bars_tall`, `lds_bars_tall` | 140 x 32, 166 x 38, 150 x 66, 120 x 76 | Not on the poster; kept current |

**For the layout:**
- `pipeline` now draws ℙ(*position* | *context*) itself, so drop the `.pipe-eq` MathJax overlay. The chart is 109.34 mm wide; widen `.pipe-row`'s first column to match.
- The chrono panels are cleaned copies. Point the Figure 3 `<img>` tags at `charts/chrono_2d_{year}.svg` and keep the same width, since the aspect ratio is unchanged.

**Wording:**
- Say "cross-metric correlations" for `mtmm`. The paper calls the matrix Spearman, but it reproduces only as Pearson (`data/discrepancies.md`, item 1).
- Attribute 0.5721 to prompt register, C1, in 2D, not to persuasive framing.
- Write "Bangla", not "Bengali". `lds_bars` follows section 4.4's basis, which includes GPT-OSS-120B (discrepancies, item 2).

**Colour check:**
- The party cyan and LLM magenta fail the dataviz CVD check against each other (delta E 3 to 4 for deuteranopia; see `data/palette_validation.json`). They are the paper's semantic colours, so keep them, but label them directly wherever both appear. These charts already do.
- Every `mtmm` cell holds at least 4.5:1 against its numerals. The weakest is OW–PIS, at 4.67:1 with ink.
