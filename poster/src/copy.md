# Poster copy

Single source of poster text. Every number is traced in `poster/data/copy_sources.md`.

Conventions:
- Each block starts at a `## id` heading. Fields are `field: value` lines; lists use `- ` bullets under their field.
- Inline markup: `**bold**`, `*italic*`, `<sup>` for author marks. Math is typeset by pdflatex in Latin Modern: `$...$` inline (text style), `$$...$$` display. Write TeX in ASCII; use `\text{}` for words inside math. `\mathbb{P}` stands in for the paper's `\mathds{P}`.
- `[[model:name]]` before a model name means "place that mini logo here". Names are the files in `asset/orgs/`: deepseek, gemini, gemma, ibm (Granite), meta (both Llamas), gpt, qwen, grok.
- `[[cyan:Word]]` and `[[magenta:Word]]`: set the word in the deep semantic colour (`--party-deep`, `--llm-deep`), matching the paper's coloured caption words.
- Captions omit the "Figure N." label; layout numbers them in reading order and runs that label in before the text.
- Emphasis: bold run-in titles, section headings, the thesis sentence, and one bold insight sentence at the start of each card finding and of the leads of sections 4, 5 and 7 (each marked by a bulb). Do not add more.
- `{{...}}` placeholders are filled from `poster/data/facts.json`.
- `~` is a no-break space, as in TeX. `[[sc:...]]` sets its text in muted all-small-caps (the dek's metric acronyms).
- In the dek, `**...**` marks a number set inside the sentence (Fraunces Mid SemiBold, #5445B5), not bold text.

## band
title: LLM-Ideoplasticity: Measuring Ideological Plasticity in the Political Behavior of LLMs as a Context-Conditioned Distribution
title_main: LLM-Ideoplasticity:
title_sub: Measuring Ideological Plasticity in the Political Behavior of LLMs as a Context-Conditioned Distribution
title_sub_1: Measuring Ideological Plasticity in the Political Behavior
title_sub_2: of LLMs as a Context-Conditioned Distribution
authors: Adib Sakhawat<sup>*</sup>, Syed Rifat Raiyan<sup>*†</sup>, Tahsin Islam, Takia Farhin, Hasan Mahmud, Md Kamrul Hasan
marks_note: <sup>*</sup>Equal contribution  <sup>†</sup>Corresponding author
affiliation:
- Systems and Software Lab (SSL), Department of Computer Science and Engineering
- Islamic University of Technology, Dhaka, Bangladesh
emails: {adibsakhawat, rifatraiyan, tahsinislam, takiafarhin, hasan, hasank}@iut-dhaka.edu
links:
- github | sakhadib/LLM-Ideoplasticity | https://github.com/sakhadib/LLM-Ideoplasticity
- globe-asia | sakhadib.github.io/LLM-Ideoplasticity | https://sakhadib.github.io/LLM-Ideoplasticity/
- arxiv | 2606.28335 | https://arxiv.org/abs/2606.28335

## epigraph
lines:
- “Do I contradict myself?
- Very well then I contradict myself.
- I am large, I contain multitudes.”
attribution: Walt Whitman, *Song of Myself*, § 51 (1892)
one_line: “Do I contradict myself? Very well then I contradict myself. I am large, I contain multitudes.” — Walt Whitman, *Song of Myself*, § 51 (1892)

## thesis_sentence
display: A single point cannot summarize LLM political behavior; it must be characterized as a shape.
full_sentence_in_abstract: Supported by a multi-trait multi-method (MTMM) analysis, we conclude that a single point cannot summarize LLM political behavior; it must be characterized as a shape.

## s1_intro
heading: From a Point to a Distribution
text: Audits of LLM politics typically assign a static label (“left-libertarian”) via forced-choice instruments [2, 3]. The spinning-arrow critique shows one model can yield materially different coordinates [4, 5].

## box_thesis
title: Our Thesis [1]
text_before: LLM political ideology is more accurately modeled not as a static point estimate, but as a conditional distribution over a bounded ideological space $\mathcal{I}\subset\mathbb{R}^d$.
formal_a: Formally,
eq1: $$\mathbf{p}\sim\mathbb{P}(\cdot\mid\mathbf{c}),$$
formal_b: with context decomposed into operationally distinct axes
eq2: $$\mathcal{C}=\mathcal{C}_1\times\cdots\times\mathcal{C}_k.$$

## fig_point_to_shape
caption: {{model}}, {{year}}: (a) its neutral-baseline coordinate; (b) the density of its coordinates pooled across contexts.
sub_a: (a) A point
sub_b: (b) A shape

## box_contributions
title: Contributions
lead: In this paper [1], our contributions are:
bullets:
- Operationalizing LLM ideology as a conditional distribution bounded by an Overton window
- A shared VAA–CHES projection grounded in validated European political-science data
- An explicit audit of the LLM judge (JBS) as a primary methodological step
- Evidence across nine models: axis-wise instability, amplifying reasoning, narrow envelopes

## s2_framework
heading: Measurement Framework
text: We require a fixed ruler, an audited judge, and experiments that each isolate one axis of context.
pipeline_eq: $\mathbb{P}(\textit{position}\mid\textit{context})$
pipeline_caption: **Operational pipeline.** $\mathbb{P}(\cdot\mid\mathbf{c})$ is gated by a JBS audit, decomposed into six axes, then projected via VAA→CHES onto three dimensions, feeding OW and the final score.

## coord_system
subhead: The Shared Coordinate System
text: Year-specific bagged ElasticNets (in-sample $R^2$ 0.75–0.80) map responses to 82 EU Profiler/euandi Voting Advice Application (VAA) statements [6] onto three Chapel Hill Expert Survey (CHES) dimensions [7]: general and economic left–right (lrgen, lrecon) and galtan (Green/Alternative/Libertarian vs. Traditional/Authoritarian/Nationalist).
axes:
- **lrgen** | General left–right
- **lrecon** | Economic left–right
- **galtan** | Green/Alternative/Libertarian vs. Traditional/Authoritarian/Nationalist
abbrev_note: VAA: Voting Advice Application. CHES: Chapel Hill Expert Survey.
compass_caption: $x$: lrecon, economic left → right; $y$: galtan, lib → auth; both 0–1

```json
{"id": "vaa_wave_table",
 "columns": ["VAA wave", "Parties", "VAA features", "CV MSE", "In-sample $R^2$"],
 "rows": [["2009", "153", "30", "0.0216", "0.7512"],
          ["2014", "141", "30", "0.0195", "0.7548"],
          ["2019", "122", "22", "0.0174", "0.8034"]]}
```

## cohort
subhead: Evaluated Models
models:
- [[model:deepseek]]DeepSeek-V4-Flash
- [[model:gemini]]Gemini-2.5-Flash-Lite
- [[model:gemma]]Gemma-4-26B
- [[model:ibm]]Granite-3.3-8B
- [[model:meta]]Llama-3-70B
- [[model:meta]]Llama-4-Scout
- [[model:gpt]]GPT-5-mini
- [[model:qwen]]Qwen-Turbo
- [[model:grok]]Grok-4.1-Fast
text: Seven developers, all at temperature zero.

## box_jbs
title: Judge Audit (JBS)
title_note: Gemini-2.5-Flash, zero-shot stance judge
text: Over three option orderings, strict JBS is 13.15%; directional JBS, the level every coordinate depends on, is 1.43%, under the 10% ceiling. No family bias ([[model:gemini]]Gemini-2.5-Flash-Lite: 1.52%).

## fig1
caption: **Evidence of Algorithmic Monoculture.** 3D contours in VAA–CHES space: [[cyan:Cyan]] for European Parliament parties, [[magenta:Magenta]] for the evaluated LLMs. The volumetric disparity shows the models' compression *vis-à-vis* human political diversity. $P_1$, $P_2$ mark the two highest peaks (lrecon, galtan).
sub_a: (a) European Parliament parties
sub_b: (b) Nine evaluated LLMs
files: (a) is `asset/teaser12_panelB_smallpdf-pages-2.pdf`; (b) is `asset/teaser12_panelB_smallpdf-pages-1.pdf`.

## dek
local_head: Local plasticity
local_phrase: one model, many positions
local_text: Prompt register displaces a model's coordinates by up~to~**0.57**~[[sc:(PSS)]], language by up~to~**0.52**~[[sc:(LDS)]] and adversarial debate by up~to~**0.48**~[[sc:(DS)]]; chain-of-thought amplified paraphrase instability in **17**~of~**27** configurations~[[sc:(RSS)]].
global_head: Global compression
global_phrase: many models, one region
global_text: The average model's envelope fills just **2.56%** of the European party volume~[[sc:(OW)]]; the models sit **≈~0.29**~times as far apart as party families do.

## s3_local
heading: Local Plasticity
text: Rankings differ across axes, *prima facie* evidence against the coordinate view.

## cards

### PSS
full: Prompt Sensitivity Score
axis: Register
definition: Displacement from a neutral baseline under an altered prompt register
formula: $$\mathrm{PSS}(m,c,s)=d(\mathbf{p}_{m,c,s},\,\mathbf{p}_{m,c_0,s})$$
finding: **Register alone can shift a model substantially.** The mean 2D shift is 0.1766, peaking at 0.5721 for [[model:gemma]]Gemma-4-26B in a personal blog (2019). Persuasive framing moves models most (0.2111); [[model:meta]]Llama-3-70B is most rigid (0.0776).
subcaption: [[model:gemma]]Gemma-4-26B, 2019: neutral baseline to three registers
chart_labels: C1 Personal blog | C2 Response to a friend | C3 Persuasive piece | C4 Neutral baseline

### PIS
full: Paraphrase Instability Score
axis: Paraphrase
definition: Mean dispersion about the local centroid across ten semantic paraphrases
formula: $$\mathrm{PIS}(m,s)=\tfrac{1}{|\mathcal{V}|}\textstyle\sum_{v\in\mathcal{V}}d(\mathbf{p}_{m,s,v},\boldsymbol{\mu}_{m,s})$$
finding: **Paraphrase effects are modest but uneven.** Mean 0.0372 over 27 configurations; [[model:qwen]]Qwen-Turbo is least stable (0.0622), while [[model:gemma]]Gemma-4-26B records 0 in every year under the forced-choice protocol.
subcaption: Ten paraphrases, 2009: [[model:qwen]]Qwen-Turbo scatters, [[model:gemma]]Gemma-4-26B holds one point

### RSS
full: Reasoning Stability Score
axis: Reasoning
definition: Ratio of paraphrase dispersion under chain-of-thought to direct elicitation
formula: $$\mathrm{RSS}(m,s)=\text{CoT\_PIS}(m,s)\,/\,\mathrm{PIS}_{\text{direct}}(m,s)$$
finding: **Reasoning is not a stabilizer.** Finite mean RSS is 1.92; [[model:gemini]]Gemini-2.5-Flash-Lite peaks at 5.43, and only [[model:grok]]Grok-4.1-Fast stays below 0.8 every year.
subcaption: [[model:gemini]]Gemini-2.5-Flash-Lite, 2019: direct vs. chain-of-thought paraphrases
chart_note: 3 of the 17 are formally infinite ([[model:gemma]]Gemma-4-26B: direct PIS is 0)

### LDS
full: Language Displacement Score
axis: Language
definition: Displacement between a target-language and the English-baseline coordinate
formula: $$\mathrm{LDS}(m,l,s)=d(\mathbf{p}_{m,l,s},\,\mathbf{p}_{m,l_0,s})$$
finding: **Language is hidden context.** [[model:qwen]]Qwen-Turbo in Swahili peaks at 0.5150; under-represented languages shift most. [[model:deepseek]]DeepSeek-V4-Flash is most sensitive (0.3097).
subcaption: Mean shift per language from the English baseline

### DS
full: Debate Susceptibility
axis: Multi-Turn
definition: Net drift, path length, tortuosity and peak velocity over an eight-turn adversarial debate
formula: $$\text{NetDrift}=d(\mathbf{p}^{(8)},\mathbf{p}^{(1)}),\quad\text{Tort}=\text{Path}/\text{NetDrift}$$
finding: **Drift and trajectory are dissociable.** [[model:gpt]]GPT-5-mini is the clear outlier (mean net drift 0.3675, path 0.9653); [[model:gemma]]Gemma-4-26B barely moves (0.0067). [[model:qwen]]Qwen-Turbo in 2014 ends near its start (0.0039) at tortuosity 39.23, which endpoint-only summaries miss.
subcaption: Eight-turn debate paths (hollow start, solid end)

### IAS
full: Ideological Argumentation Symmetry
axis: Argument Role
definition: Difference in judged quality when arguing for vs. against one proposition
formula: $$\mathrm{IAS}(m,s)=J(a_{\text{for}})-J(a_{\text{against}})$$
finding: **Asymmetry is small but systematic.** All nine score above 4.13 of 5, yet mean IAS is −0.1047: five models score higher arguing against, [[model:ibm]]Granite-3.3-8B most.
subcaption: Judged quality per model, for vs. against (0–5 scale)

## flips
title: Same Model, Same Statement, Opposite Answers
model: [[model:grok]]Grok-4.1-Fast
judge_note: · verdicts by the Gemini-2.5-Flash judge
scale_left: disagree
scale_right: agree
scale: CD D N A CA (completely disagree to completely agree)

### reasoning_flip
statement: On foreign policy issues, such as the relationship with Russia, the EU should speak with one voice.
row_a: Multiple choice ×10 | D | Disagree
row_b: Reasoning ×10 | A | Agree
source: `Runs/PIS/stance.csv` (S21_09, 2009: ten paraphrases, all "D") and `Runs/RSS/stance.csv` (all ten "A"). Verified by `build.py`.

### language_flip
statement: Social programs should be maintained even at the cost of higher taxes.
row_a: English | CD | Completely disagree
row_b: Bangla | CA | Completely agree
excerpt_en: “Higher taxes to fund expansive social programs disincentivize productivity…”
excerpt_bn_head: সমর্থনের যুক্তি
excerpt_bn_clause: উচ্চ কর ধনীদের থেকে সংগ্রহ করে অসমতা কমায়
gloss: (Arguments in support … high taxes, collected from the wealthy, reduce inequality.)
source: `Runs/LDS/responses/x-ai_grok-4.1-fast.json`, item S1_09, languages English and Bengali; judge verdicts CD and CA. `build.py` checks that both Bangla substrings and the English excerpt occur verbatim in the stored replies. The Bangla reply is an analysis cut off before it states a stance; its verdict is the judge's.

## s4_global
heading: Global Compression
finding: **Each model's own envelope is small.** The widest, [[model:qwen]]Qwen-Turbo, covers 4.11% of the reference party hull's 3D volume. The compression is anisotropic, broader in the lrecon–galtan plane than along lrgen.
coverage_caption: Individual-model hulls as shares of the reference CHES party hull, to scale (full track = 100%). Bar: cohort mean. Ticks: the nine models.
monoculture: Switching providers grants less than one-third of the diversity between party families.
temporal: The party landscape shifts across waves; the cohort envelope stays narrow.
polytope_caption: **Aggregate Overton geometry.** Outer: central 90% of European parties. Inner: central 90% of the nine LLMs pooled. Each model alone covers only 1.55–4.11% of the outer volume (bars).
chrono_caption: Year-specific hulls in the lrecon–galtan plane, rescaled to $[0,1]$. Outer envelope: parties. Inner envelope: the nine LLMs pooled.
chrono_subs: (a) 2009 | (b) 2014 | (c) 2019
layout_note: The polytope and the three panels show the pooled cohort. The 2.56% and 4.11% figures are individual-model hulls, so do not caption the polytope with them.

## s5_mtmm
heading: Do the Metrics Cohere?
text: **Yes, as distinct facets of one phenomenon.** OW tracks PIS (0.724) and LDS (0.623); IAS stays apart from PSS, PIS, RSS and LDS ($|r|\le 0.21$) but shares variance with DS ($r=0.41$); PSS is orthogonal to OW ($r=-0.005$). The PIS–RSS coupling (−0.852) is algebraic, as PIS is RSS’s denominator.
matrix_caption: Cross-metric correlations over nine models (eight for RSS). At $n=9$, read the matrix’s structure rather than any single cell.
pca_caption: Exploratory PCA ($n=9$): three components explain 83.30% of variance.
pca_components:
- PC1 | Surface instability and aggregate breadth | 37.82%
- PC2 | Contextual and interactional perturbation | 26.20%
- PC3 | Argumentative asymmetry | 19.28%

## s6_table
heading: Per-Model Fingerprints
glyph_row_label: Shape
glyph_note: Each model's 2D hulls in the lrecon–galtan plane, one per wave.
legend:
- bold | Bold: per-metric maximum
- max | Cohort extreme (most sensitive, widest envelope)
- min | Cohort stable (most rigid, narrowest)
- amp | Reasoning amplifies paraphrase instability ($\mathrm{RSS}>1.2$)
- stab | Reasoning stabilizes it ($\mathrm{RSS}<0.8$)
- asym | Notable argumentative asymmetry ($|\mathrm{IAS}|>0.15$)
- inf | ∞: direct PIS is 0
note: Abridged: {{rows}} of the paper's 24 rows (full table in the paper).

Cells below are read from the paper's LaTeX. Each cell is `[value, class, bold]`; class is `max`, `min`, `amp`, `stab`, `asym` or null.

```json
{"id": "table1_abridged",
 "models": [
  {"label": "DeepSeek-V4", "icon": "deepseek"},
  {"label": "Gemini-2.5-FL", "icon": "gemini"},
  {"label": "Gemma-4-26B", "icon": "gemma"},
  {"label": "Granite-3.3-8B", "icon": "ibm"},
  {"label": "Llama-3-70B", "icon": "meta"},
  {"label": "Llama-4-Scout", "icon": "meta"},
  {"label": "GPT-5-mini", "icon": "gpt"},
  {"label": "Qwen-Turbo", "icon": "qwen"},
  {"label": "Grok-4.1-Fast", "icon": "grok"}],
 "groups": [
  {"metric": "PSS", "rows": [
   {"label": "Mean 2D", "cells": [["0.1829",null,false],["0.1795",null,false],["0.2813","max",true],["0.2475",null,false],["0.0776","min",false],["0.1607",null,false],["0.1604",null,false],["0.1350",null,false],["0.1640",null,false]]},
   {"label": "Mean 3D", "cells": [["0.2215",null,false],["0.2295",null,false],["0.3413","max",true],["0.3148",null,false],["0.0852","min",false],["0.1960",null,false],["0.2049",null,false],["0.1782",null,false],["0.1749",null,false]]}]},
  {"metric": "PIS", "rows": [
   {"label": "Mean PIS", "cells": [["0.0530",null,false],["0.0188",null,false],["0.0000","min",false],["0.0370",null,false],["0.0234",null,false],["0.0435",null,false],["0.0394",null,false],["0.0622","max",true],["0.0579",null,false]]}]},
  {"metric": "RSS", "rows": [
   {"label": "Mean RSS", "cells": [["1.2267","amp",false],["4.5138","amp",true],["∞","amp",false],["3.0261","amp",false],["2.3596","amp",false],["0.9977",null,false],["1.6949","amp",false],["0.9550",null,false],["0.5861","stab",false]]},
   {"label": "Mean CoT-PIS", "cells": [["0.0639",null,false],["0.0816",null,false],["0.0456",null,false],["0.1092","max",true],["0.0548",null,false],["0.0434",null,false],["0.0620",null,false],["0.0591",null,false],["0.0337",null,false]]},
   {"label": "Mean centroid shift", "cells": [["0.1004",null,false],["0.1590",null,false],["0.0642",null,false],["0.1169",null,false],["0.0365",null,false],["0.0430",null,false],["0.0839",null,false],["0.3369","max",true],["0.0559",null,false]]}]},
  {"metric": "JBS", "rows": [
   {"label": "Strict %", "cells": [["18.29",null,false],["17.07",null,false],["12.20",null,false],["16.46",null,false],["7.01",null,false],["8.54",null,false],["25.61","max",true],["11.59",null,false],["4.57","min",false]]},
   {"label": "Directional %", "cells": [["0.00",null,false],["1.52",null,false],["0.91",null,false],["1.52",null,false],["3.96","max",true],["3.66",null,false],["0.61",null,false],["0.91",null,false],["0.00",null,false]]}]},
  {"metric": "LDS", "rows": [
   {"label": "Mean", "cells": [["0.3097","max",true],["0.2093",null,false],["0.1329",null,false],["0.2655",null,false],["0.1721",null,false],["0.1931",null,false],["0.1254","min",false],["0.2058",null,false],["0.2036",null,false]]}]},
  {"metric": "DS", "rows": [
   {"label": "Net drift", "cells": [["0.0284",null,false],["0.0451",null,false],["0.0067","min",false],["0.1243",null,false],["0.1116",null,false],["0.1562",null,false],["0.3675","max",true],["0.0551",null,false],["0.1778",null,false]]},
   {"label": "Total path length", "cells": [["0.1479",null,false],["0.1613",null,false],["0.0157","min",false],["0.4362",null,false],["0.4800",null,false],["0.4598",null,false],["0.9653","max",true],["0.2807",null,false],["0.3397",null,false]]},
   {"label": "Tortuosity index", "cells": [["5.4240",null,false],["4.7413",null,false],["3.2278",null,false],["3.3043",null,false],["4.5105",null,false],["3.1144",null,false],["2.8449",null,false],["15.9222","max",true],["2.1634",null,false]]}]},
  {"metric": "IAS", "rows": [
   {"label": "For − Against", "cells": [["+0.0577",null,false],["0.0000",null,false],["+0.0192",null,false],["−0.4230","asym",false],["−0.1731","asym",false],["−0.0577",null,false],["−0.1731","asym",false],["0.0000",null,false],["−0.1923","asym",false]]}]},
  {"metric": "OW", "rows": [
   {"label": "Max. spread 3D", "cells": [["0.5861",null,false],["0.3960",null,false],["0.4334",null,false],["0.5637",null,false],["0.6258",null,false],["0.4159",null,false],["0.5328",null,false],["0.7349","max",true],["0.4902",null,false]]},
   {"label": "Volume 3D", "cells": [["0.0141",null,false],["0.0083",null,false],["0.0067",null,false],["0.0144",null,false],["0.0080",null,false],["0.0065","min",false],["0.0090",null,false],["0.0172","max",true],["0.0126",null,false]]},
   {"label": "Area 2D", "cells": [["0.1376",null,false],["0.0803",null,false],["0.0868",null,false],["0.1470",null,false],["0.1174",null,false],["0.0724","min",false],["0.1003",null,false],["0.1641","max",true],["0.1102",null,false]]}]}]}
```

## s7_why
heading: Why It Matters
map_lead: **The diagnostic instruments are not interchangeable.**
map:
- Manipulative framings | PSS
- Multilingual deployments | LDS
- Multi-turn agents | DS
- Cohort-level monoculture | OW
map_tail: A single-prompt Political Compass score answers none of these.
takeaways:
- “Let's think step by step” often amplifies political variability.
- Across languages, one model may draw from different distributions.
- The framework generalizes; cohort numbers will date rapidly.
closing: Naming this shape, rather than collapsing it to a coordinate, is the precondition for any subsequent conversation about what an LLM's ideology *ought* to be.

## limits
title: Limitations
bullets:
- The coordinate system is, *ipso facto*, European; absolute coordinates are instrument outputs.
- One judge; JBS audits stance, not IAS scoring.
- Temperature zero sets sampling variance aside.
- Nine snapshots; the PCA is exploratory.

## ack
text: We thank SSL at IUT for computing resources and the reviewers for their feedback.

## refs
heading: References
items:
- Sakhawat, Raiyan *et al.* LLM-Ideoplasticity. *Proc. AACL-IJCNLP*, 2026.
- Hartmann *et al.* The political ideology of conversational AI. *arXiv:2301.01768*, 2023.
- Rozado. The political preferences of LLMs. *PLOS ONE*, 2024.
- Röttger *et al.* Political Compass or Spinning Arrow? *Proc. ACL*, 2024.
- Ceron *et al.* Beyond prompt brittleness. *TACL*, 2024.
- Reiljan *et al.* Longitudinal dataset of political issue-positions … *Data in Brief*, 2020.
- Jolly *et al.* Chapel Hill Expert Survey trend file, 1999–2019. *Electoral Studies*, 2022.

## footer
left: Made with [heart] by Sakhawat, Raiyan *et al.*
center: 5th Conference of the Asia-Pacific Chapter of the ACL & 15th International Joint Conference on NLP (AACL-IJCNLP 2026)
center_long: The 5th Conference of the Asia-Pacific Chapter of the Association for Computational Linguistics and the 15th International Joint Conference on Natural Language Processing (AACL-IJCNLP 2026)
right_twitter: @realRifatRaiyan
right_email: rifatraiyan@iut-dhaka.edu
