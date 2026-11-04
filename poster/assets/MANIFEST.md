# Poster assets

Everything here was checked in a Chrome-printed PDF and inspected at high zoom. All assets together on an A0 page print to a **2.9 MB** PDF (limit 20 MB). Chrome's A0 page comes out at 2383.92 x 3370.08 pt (841.0 x 1188.9 mm).

## Rules for the layout

- **Use `<img>` for every SVG in `logos/`, `figures/`, `qr/` and `icons/`.** They are self-contained, with text as paths. Do not inline them: the AACL file has `.cls-*` styles and the MuPDF files use global ids, which would collide.
- The AACL logo needs a **white plate** (black text, transparent ground). Give it at least 6 mm of padding.
- `iut_emblem.svg` has a transparent interior: white grounds only. On the band use `iut_lockup_white.svg` or `iut_emblem_band.svg`.
- Print the QR card at **90 mm wide or more**.
- Set a font on `body`, or Chrome embeds Times New Roman for stray whitespace.
- JetBrains Mono: set `font-feature-settings: 'calt' 0` so `->` and `!=` do not turn into ligatures.
- MathJax needs `svg: { fontCache: 'none' }`, and the build must wait for `MathJax.startup.promise` before `page.pdf()`. See `tools/test_math.py`.

## Logos (`logos/`)

| Path | Kind | Size | Effective resolution | Notes |
|:---|:---|:---|:---|:---|
| `iut_lockup_white.svg` | vector | aspect 5.512 (1786:324) | vector; 190 mm wide gives 34.5 mm tall | Emblem + white wordmark, same arrangement as the ACL 2023 and HaSPeR posters. No fonts, no images. |
| `iut_emblem_band.svg` | vector | aspect 0.614 | vector | Emblem over a traced white shield fill and halo, for coloured grounds. |
| `iut_emblem.svg` | vector | aspect 0.612 | vector | Emblem only, hollow interior, for white grounds. |
| `oic_emblem.svg` | vector | aspect 1.005 | vector | OIC emblem. Not placed by default. |
| `iut_wordmark_white.svg` | vector | | vector | Wordmark alone. |
| `iut_wordmark_trace.svg` | vector | | vector, soft edges | Direct potrace of the old raster wordmark: exact letterforms, softer corners. Alternative only. |
| `aacl_2026_logo.svg` | vector | aspect 4.118 | vector | From `2026.aaclnet.org/assets/images/logos/aacl-2026-logo.svg`. Same design as the v2 PNG (pixel difference is edge-only). No scripts. |
| `aacl_2026_logo_v2.png` | raster RGBA | 1200 x 291 | 152 dpi at 200 mm | The file you supplied. Fallback. |
| `project_logo_band.png` | raster RGBA | 738 x 738 | 625 dpi at 30 mm | `images/llm_ideoplasticity_logo_1 (4).png` (README logo, arrowed axes), cropped. Transparent corners, sits directly on the band. |
| `project_logo_qr.png` | raster RGBA | 370 x 370 | 671 dpi at 14 mm | Variant (7), plain axes, reads better small. |

**How the IUT lockup was made.** The supplied PNG (145 x 212) and the lockup raster on the old posters (1786 x 324, emblem only 200 px wide) are too coarse. A true vector emblem exists in the official letterhead, `Desktop\IUT Stuff\IUTLetterHeadBackground.pdf`, and its 76 paths are used untouched, in their true colours (`#00A551`, `#EC1C24`, `#231F20`).

Two deliberate decisions:

1. **5% horizontal stretch.** The letterhead's emblem is squeezed compared with the logo you supplied and your earlier posters: its green outline has width/height 0.569 versus 0.597, and its nucleus is not round. Stretching x by 1.05 restores the proportions. Nothing else about the design changes.
2. **Wordmark re-set rather than traced.** The old raster gives wobbly edges when traced. An automated search of all system fonts plus EB Garamond found EB Garamond 400 is the closest match. Each glyph is placed at its matched position in the old lockup on a shared baseline. Overlap with the old wordmark is IoU 0.83, with differences only in fine letter detail. Crisp at any zoom.

## QR (`qr/`)

| Path | Kind | Notes |
|:---|:---|:---|
| `qr_card_white.svg` | vector + 370 px logo | **Recommended.** White card, modules in `#5445B5` (7.25:1), "SCAN ME" in JetBrains Mono. Calm on the band, close to the HaSPeR code. Aspect 0.864. |
| `qr_card.svg` | vector + 370 px logo | Ink `#111827` frame with white label, closest to the ACL 2023 card. Aspect 0.883. |
| `qr_modules.svg` | vector | Bare code with quiet zone, no logo image. |

Target: `https://sakhadib.github.io/LLM-Ideoplasticity/`. QR version 6, error correction H, 41 modules, 4-module quiet zone, centre 9 x 9 modules cleared (4.8% of the symbol), logo 18% of the code's width. Modules are unioned into one outline, so print seams cannot appear.

**Verification.** Both cards were printed through Chrome at 95 mm on the band colour, rendered from the PDF, and decoded by two independent decoders (zxing-cpp and OpenCV) at 72, 96, 150 and 300 dpi of the page. At 72 and 96 dpi they also passed Gaussian blur at sigma 0.6 and 1.0, 8-degree rotation with blur, and a washed-out print with a shading gradient. Every test decoded to the exact URL on both decoders. At 72 dpi the card is 270 px wide, about 5.5 px per module.

**The user's convention.** The ACL 2023 QR points to a Google Drive folder (`drive.google.com/drive/folders/1hTQ-mN8DW4UvQZxmF101vIkrBFJZct1o`). The HaSPeR QR points to the GitHub repo (`github.com/Starscream-11813/HaSPeR`), with a GitHub icon at its centre. Both go to the project's resources rather than to the paper. The project page serves that role here (it links to the paper, code and data), so it stays as the default. To retarget:

```
python poster/assets/tools/make_qr.py https://github.com/sakhadib/LLM-Ideoplasticity --pylibs <dir with segno>
```

## Fonts (`fonts/`, load `fonts/fonts.css`)

All embed in Chrome's PDF as TrueType (Type0/CID). **No Type 3**, confirmed with pymupdf.

| CSS family | Weights | Files | Use for |
|:---|:---|:---|:---|
| `Fraunces Poster` | 400, 500, 600, italic 400, 500 | opsz 144 | Main title only. Hairlines get too thin below about 90 pt. |
| `Fraunces Poster Mid` | 500, 600, italic 500 | opsz 72 | Subtitle, thesis sentence, big stats. |
| `Fraunces Poster Text` | 500, 600, italic 500 | opsz 36 | Section heads, card names. |
| `Pagella Poster` | 400, 700, italic 400, 700 | TeX Gyre Pagella, outlines converted to TrueType | Body, captions, chart words. |
| `JetBrains Mono Poster` | 400, 500, 600 | static instances | Table numbers, chart numerals. |
| `Bangla Poster` | 400, 600 | Noto Serif Bengali | Bangla example. |

`tokens.css` names only `Fraunces Poster`. Use the Mid and Text families explicitly as above; at 50 pt the opsz 144 cut looks noticeably thinner than opsz 36.

- **Pagella** has real `smcp`, `c2sc`, `tnum`, `pnum`, `lnum`, `onum`, `liga`, `frac`. Use `font-variant-caps: small-caps` for box titles. Default figures are lining; `font-variant-numeric: lining-nums tabular-nums` works. It lacks only `ℝ` and `ℙ` of the symbols tested (use MathJax for those); `→ ≈ × ∼ ≤ ≥ ∈ ⟨ ⟩ †` are all present.
- **Palatino Linotype would not be better:** it has `smcp` but no `tnum` or `lnum`, and it lacks `→ ∼ ∈ ⟨ ⟩`.
- **Fraunces** figures are lining by default, with no `tnum`. It lacks `→ ∼ ∈` and Greek. Its `≈` is present.
- **Bangla:** conjuncts in সোশ্যাল ওয়েলফেয়ার স্টেটের মূল ধারণা shape correctly. Chose Noto Serif Bengali over Nirmala UI (sans) to suit the serif page.
- Pagella had to be converted because CFF OpenType risks Type 3 output in Chrome's PDF backend. The conversion keeps GSUB, GPOS and metrics.
- Licences: OFL for Fraunces, JetBrains Mono and Noto Serif Bengali (`fonts/licenses/`); GUST Font License for Pagella. EB Garamond (OFL) appears only as outlines in the wordmark.

## Figures (`figures/`, true aspect ratios in `figures/figures.json`)

| Path | Source PDF | Aspect w/h | Intended width | Effective resolution |
|:---|:---|:---|:---|:---|
| `fig1a_parties.svg` | `teaser12_panelB_smallpdf-pages-2.pdf` (cyan, confirmed by the .tex order and by eye) | 1.847 | 257 mm | Lines, floor, labels vector; surface raster **149 dpi** |
| `fig1b_llms.svg` | `...pages-1.pdf` (magenta, confirmed) | 1.847 | 257 mm | Same, **149 dpi** |
| `polytope_3d.svg` | `extended_teaser.pdf` | 1.031 | 200 mm | vector |
| `polytope_chrono_2d.svg` | `extended_teaser_chrono_2d.pdf` | 3.208 | 330 mm | vector |
| `polytope_chrono_2d_{2009,2014,2019}.svg` | same, one panel each | 1.000 | | vector |
| `polytope_chrono_3d.svg` | `extended_teaser_chrono.pdf` (bold year titles inside) | 3.397 | | vector |
| `polytope_chrono_3d_{2009,2014,2019}.svg` | same, one panel each, **year titles cropped out** | 1.054, 1.020, 1.011 | | vector |
| `pipeline.svg` | `IdeoPlasticityLLM_pipeline2.pdf` (the paper's Figure 2) | 1.037 | 170 mm | vector; box gradients are tiny raster patches, smooth and clean at this size |

The per-panel files suit the user's rule of subcaptions below panels, with no titles inside the graphic.

**Fidelity.** Each figure was printed via `<img>` at its intended width, rendered, and compared side by side and numerically with a direct render of the source PDF. Hull transparency, terrain masks and gradients all match. Only sub-pixel anti-aliasing differs. **No figure failed, so the `show_pdf_page` fallback is not needed.**

**Hero resolution.** Only the translucent surface is raster (1396 x 625 and 1395 x 638, with a soft mask). Contour lines, floor, ticks and labels are vector, so they are perfectly sharp.
- No sharper source exists: `docs/asset/f1.svg` and `f1-2.svg` embed the same rasters, and the GIF is only 1100 x 329 overall.
- A 2x upscale would gain nothing visible, because the raster holds a smooth pastel surface with no line work. It was not done.
- Faint mesh facets in the surface exist in the source itself.

## Model logos (`icons/`, map in `icons/model_icons.json`, key `files`)

| Model | File | Kind |
|:---|:---|:---|
| DeepSeek-V4-Flash | `deepseek.svg` | vector |
| Gemini-2.5-Flash-Lite | `gemini.png` | 512 x 512 RGBA |
| Gemma-4-26B | `gemma.png` | 384 x 384 RGBA |
| Granite-3.3-8B | `ibm.svg` (aspect 2.39) | vector |
| Llama-3-70B, Llama-4-Scout | `meta.png` (aspect 1.5) | 512 x 342 RGBA |
| GPT-5-mini | `gpt.svg` | vector |
| Qwen-Turbo | `qwen.png` | 384 x 384 RGBA |
| Grok-4.1-Fast | `grok.svg` | vector |

Mapping is from the paper's macros (`\GeminiI`, `\GemmaI`, `\GraniteI` to ibm, `\LlamaI` to meta, and so on). True colours kept. Inline style that looks right beside 27 pt text: `height: 0.95em; vertical-align: -0.13em; margin-right: 0.35em`.

The four PNGs are deliberate. Gemma's and Qwen's PDFs hold rasters: Gemma's SVG conversion showed stray edge lines, so its alpha was rebuilt with an exact circle, and Qwen's mask covered the whole page, so its white surround was made transparent. Meta's and Gemini's gradients converted to many tiny patches with faint seams, so they are rendered cleanly from source. All exceed 1000 dpi at 9 mm, and Chrome de-duplicates repeated uses.

`icons/ui/`: `twitter`, `envelope`, `github`, `globe` in `_white`, `_ink`, `_purple` (Font Awesome Free 5, CC BY 4.0, the family the old posters use); `heart_red.svg`; `arxiv_white.svg` and `arxiv_colour.svg` (official vector mark, replacing `docs/arxiv-logo.png`).

## Round 3 additions

- `qr/qr_card_white_compact.svg`: the white card with a 2.5-module top margin, a trimmed SCAN ME zone and 2 mm corners. At 96 mm wide it is 99.3 mm tall. Written by `make_qr.py` (options `--compact-top`, `--compact-bottom`, `--compact-label`, `--compact-radius`). `test_qr.py ... qr_card_white_compact.svg` decoded it in every test, on both decoders, at 72 to 300 dpi, with blur, rotation and low contrast.
- `icons/ui/globe_asia_{white,ink,purple}.svg`: Font Awesome 5 Free Solid `globe-asia` (U+F57E, LaTeX `aGlobeAsia`), from `make_ui_icons.py`. The band's project-page link uses it.
- The poster no longer uses MathJax: `build.py` typesets all math with pdflatex in Latin Modern. `vendor/tex-svg.js` and its `boldsymbol` extension are kept but unused.

## Round 4 additions

- **Latin Modern** (LaTeX's default font), from MiKTeX `fonts/opentype/public/lm/`, converted from CFF to TrueType outlines by `tools/otf2ttf_lm.py` (same method as Pagella, so Chrome embeds TrueType, not Type 3). kern, liga and tnum carry over. Families in `fonts.css`: `'LM Roman Poster'` 400, 700, italic 400 (`LMRomanPoster-*.ttf`) and `'LM Mono Poster'` 400 (`LMMonoPoster-Regular.ttf`). Digits, U+2212 and ∞ are all native glyphs, so ∞ needs no fallback. Licence: GUST Font License (`fonts/licenses/GUST_LatinModern.txt`).
- The table numerals are LM Roman (bold maxima in LM Roman Bold); the band's email line is LM Mono. JetBrains Mono is no longer used anywhere; `build.py` fails if it is embedded.
- QR cards: "SCAN ME" is now LM Mono (`make_qr.py --label-font`, default `LMMonoPoster-Regular.ttf`). All three cards decoded in all 36 tests on both decoders.
- `icons/ui/bulb.svg`: the insight bulb, drawn by hand. It has amber glass (#FFE7A8 with a #FFF6D9 highlight), a flat #FFD86B glow and a tiny filament curl. The screw base is two lavender bands (#9194E4, #6E65CE). The outline is thin #5445B5, with three short rays and a white keyline so it holds on coloured title bars. It uses no filters and no raster. It prints 9 mm tall on box corners and 0.95 em inline.
- Author marks (* and †) are set in Times New Roman, like LaTeX's `	extdagger` with Times; the asterisk too, so the pair matches.

## MathJax (`vendor/tex-svg.js`)

MathJax 3 es5, 2.1 MB, local. Confirmed with all network requests blocked: `\mathbb{P}(\text{position}\mid\text{context})` and `p \sim \mathbb{P}(\cdot \mid \mathbf{c})` print as vector paths, with zero images and no math fonts in the PDF. It does not add to the PDF's weight beyond those paths.

## Rebuilding

Scripts are in `tools/` and take paths as arguments; `tools/chrome.py` is the shared print helper. `make_iut_lockup.py` must run before `build_wordmark.py`, which reuses `tools/wordmark_fit.json`. `make_icons.py` must run before `make_raster_icons.py`. `make_project_logos.py` must run before `make_qr.py`, which needs `segno`. Font sources come from `github.com/google/fonts` (`ofl/fraunces`, `ofl/jetbrainsmono`, `ofl/notoserifbengali`, `ofl/ebgaramond`) and MiKTeX (`tex-gyre`).
