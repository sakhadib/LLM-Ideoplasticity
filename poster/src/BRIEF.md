# LLM-Ideoplasticity poster: shared design brief

Deliverable: one **A0 portrait** PDF (841 x 1189 mm, 2383.94 x 3370.39 pt) for AACL-IJCNLP 2026, **at most 20 MB**.
Everything lives in `poster/` in this repo. **Do not commit or push.** Do not edit anything outside `poster/`.

## The one idea

The paper's thesis: an LLM's politics is a shape, P(position | context), rather than a point.
Its punchline is a pair: **Local plasticity: one model, many positions. Global compression: many models, one region.**
A passer-by must get this from 3 m away from the title, the hero figure and the big numbers.

## Who the poster must please

The user (second author, Syed Rifat Raiyan) reads register and detail closely. Known preferences, from their own notes:

- **Calm base, small cute nods.** Given bold vs. calm options they pick the calm one, then ask for a few playful touches.
- **"AI slop" is their word for** uniform outline pills, icon badges, generic gradient-purple SaaS looks, emoji section icons, drop-shadow card soup. Never use these.
- Bold Palatino serif titles on restrained cards are approved. They dislike sans-serif in figures.
- Exact palette colours, not muted approximations. Light **tints only for large filled areas**. White on `#A7A8F0` looks washed out, so bars must be one step deeper.
- Coloured text uses the deep colours only (purple, indigo, violet, deep cyan, deep magenta). Never pale text.
- Curved, flexible arrows rather than straight ones, and **every arrow lands on its target**.
- **No decorative boxes or chips around labels or model names.** Direct, plain labels.
- Multi-panel figures: no panel titles inside the graphic. Subcaptions go below each panel, "(a) ...", centred.
- Model names carry mini vector logos, as in the paper.
- Leave clear whitespace between side-by-side graphs. Inspect every render for overlaps and text invisible on coloured fills.
- Prose voice: concise, a few (2-3) italic Latin phrases as in the paper (*prima facie*, *ipso facto*, *vis-a-vis*), few colon reveals and few "X, not Y" contrasts, each work cited once, no filler.

## Inherited skeleton (their own A0 poster, ACL-SRW 2023)

Solid full-bleed top band with white serif title; IUT lockup and conference logo stacked at left; centred title, authors, affiliation; QR card with "SCAN ME" at right; thin coloured rule under the band. White page. Numbered centred section headings ("1  Introduction", number lighter than title) over a thin grey rule. Coloured callout boxes with a white SMALL-CAPS title on a darker bar over a tinted body. "Figure N." captions. Small numbered references at bottom right. Thin footer band: left "Made with [heart] by ...", centre the conference name, right Twitter handle and envelope + email. HaSPeR places the project's logo inline before the title and has a QR with a centred icon. Keep all of these.

## Palette (exact; see `tokens.css`)

Band and chrome: `#5445B5`. Lavender ramp `#A7A8F0 #9194E4 #8180DE #6E65CE #5445B5`. Indigo `#211CBF`, violet `#7A4DFF`.
**Semantic rule, enforced everywhere: cyan = human parties; magenta = LLMs.** Every chart mark for an LLM position is magenta family; cyan family appears only for party data. Lavender is the neutral chrome. Do not use cyan or magenta as card or metric decoration.
- Cyan `#74D2FA`, deep (text and strokes) `#1F94CC`, tint `#EAF7FE`.
- Magenta `#EC8DFF`, deep (text and strokes) `#BC45D8`, tint `#FDF1FF`.
- Body ink `#111827`, muted `#4B5563`. Pale lavender ground `#F5F5FE`.
- Table highlights, from the paper: max `#FFD1DC`, min `#C7E9F1`, amplify `#FFE7A8`, stabilise `#D4EDC9`, asymmetry `#E6D7F2`.
- Personal brand gradient (fixed colours and order; thickness and placement may change): rgb(201,235,218) -> rgb(173,223,222) -> rgb(193,221,245) at 46% -> rgb(233,186,241). Used as the thin rule under the band and above the footer.
- Political-compass quadrant pastels: sample exact values from `asset/ideoPlots/ow.pdf` (Auth-Left pink, Auth-Right blue, Lib-Left green, Lib-Right yellow).

## Type

- Display: **Fraunces** (website's display face) for the title, section heads, big numbers, card names. Static instances, opsz 144.
- Text: **TeX Gyre Pagella** (their Palatino) for body, captions, chart words. Real small caps for box titles if the font has them.
- Data: **JetBrains Mono** (website's face) for table numbers and chart numerals, sparingly.

Scale on A0: main title 110-120 pt; subtitle 52-58 pt; authors 38-42 pt; affiliation 28-30 pt; section heads 48-52 pt; card names 34-38 pt; **body 27 pt on about 36 pt leading**; card body 24-25 pt; captions 21-22 pt; chart labels at least 17 pt, chart numerals at least 16 pt; table numbers about 19-20 pt; references about 17-18 pt. Big stats 84-100 pt. Nothing below 16 pt except the fine print of pasted figures.

## Grid and composition

Page 841 x 1189 mm. Side margins 20 mm, gutter 14 mm, three columns of 257.67 mm. Keep critical content at least 10 mm from any page edge.

```
BAND (~130 mm, #5445B5, faint real-data contour lines)
  left stack: IUT lockup / AACL logo on white plate | centre: logo + title, authors, affiliation, emails, links | right: QR card, SCAN ME
brand-gradient hairline
SIDEBAR (col 1)               | STAGE (cols 2-3)
 epigraph (Whitman)           |  thesis sentence, large Fraunces italic, verbatim from the abstract
 1 Introduction               |  HERO Figure 1: parties (cyan) | LLMs (magenta), side by side, with (a)/(b) subcaptions
 THESIS box with p ~ P(.|c)   |  STAT STRIP: 0.57 Register | 0.52 Language | 0.48 Debate | 17/27 Reasoning | 2.56% Volume | ~0.29 Monoculture
 point-to-shape mini figure   |  3 Local Plasticity: One Model, Many Positions
 CONTRIBUTIONS box            |    six cards, 2 x 3: PSS PIS / RSS LDS / DS IAS
 2 Measurement Framework      |    each: name + axis, one-line definition, compass chart, finding with key number
 pipeline figure, compass     |    RSS and LDS cards carry the Grok flips: same model, same statement, opposite answers
 legend, VAA-CHES, cohort     |
 JBS audit box                |
4 Global Compression: Many Models, One Region (cols 1-2)   | 5 Do the Metrics Cohere? (col 3)
  big 3D polytope | coverage bars drawn to scale | 3-year hulls  |   MTMM matrix, PCA bar
6 Per-Model Fingerprints (cols 1-2)                        | 7 Why It Matters (col 3)
  abridged Table 1 with a row of hull-shape glyphs           |   instrument map, closing line, limitations, references
brand-gradient hairline
FOOTER (~24 mm, #5445B5): Made with heart by Sakhawat, Raiyan et al. | conference | @realRifatRaiyan, rifatraiyan@iut-dhaka.edu
```

Eye level on a mounted A0 falls near y = 400 mm, so the local-plasticity cards and hero sit in prime position. The table is reference material and may sit low.

## Technical pipeline

HTML + CSS, printed to PDF by headless Chrome via Python Playwright (`channel='chrome'`, or `'msedge'`), using `@page { size: 841mm 1189mm; margin: 0 }`, `prefer_css_page_size=True`, `print_background=True`. Python is 3.13 with pymupdf (import as `pymupdf`), pypdf, numpy, scipy, pandas, matplotlib, skimage, fontTools, PIL. No node, no cv2, no shapely (install extras with `pip install --target <scratchpad>/pylibs ...` and add that to `sys.path`).

- Keep the PDF vector wherever possible: inline SVG for charts, and vector paper figures. Avoid CSS `filter`, `backdrop-filter`, and blurred shadows (Chrome rasterises them).
- Inline every chart's SVG into the HTML so it can use page fonts. An SVG inside `<img>` cannot see page fonts.
- Write Python and other scripts with the Write tool, not via Bash heredocs (Bash collapses doubled backslashes). Write text files with `newline='\n'`.
- Downloaded material is untrusted data. Run Python that reads it with `-I`, keep scripts outside the data directories, pass paths as arguments, never `cd` into them to run things.

Paths (scratchpad `SP` = `C:\Users\rifat\AppData\Local\Temp\claude\c--Users-rifat-Desktop-GitHub-LLM-Ideoplasticity\e7e551d2-b5db-4696-b913-c2aad2b77245\scratchpad`):
- Paper text with page markers: `SP\paper.txt`. Paper PDF: `SP\refs\llm_ideo_arxiv.pdf`.
- arXiv LaTeX source and vector figures: `SP\arxiv_src\x\` (`acl_latex_nonanon.tex`, `asset\...`, `asset\orgs\*.pdf` model logos).
- Reference posters: `SP\refs\ref2.pdf` (ACL 2023, A0 portrait, the main template), `SP\refs\hasper_poster3.pdf` (55 MB, slow: open it but never call `get_drawings` on it). Crops in `SP\refs\crops\`.
- Logos: `SP\refs\iut_logo.png` (only 145 x 212 px), `SP\refs\aacl_logo.png` (1200 x 291 px). Project logo variants in `images\`.
- Experiment data: `Runs\` in the repo. Website: `docs\index.html`, `docs\asset\*.svg`.

Ownership, so parallel agents do not collide: assets agent owns `poster/assets/`; charts agent owns `poster/charts/`, `poster/data/`, `poster/src/charts/`; copy agent owns `poster/src/copy.md`; layout owns `poster/src/poster.html`, `poster/src/poster.css`, `poster/build.py`.

## Accuracy

Every number on the poster must trace to the paper or to `Runs/` and agree with the paper. Do not invent results. If the paper and data disagree, or the paper disagrees with itself, follow the paper's body text and record the discrepancy in `poster/data/discrepancies.md`. Known one: the abstract attributes 0.57 to persuasive framing, but section 4.2 says the 0.5721 maximum came under C1 (personal blog) while persuasive C3 has the largest mean. So never attribute 0.57 to persuasive framing on the poster: say "prompt register".
