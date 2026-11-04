# Fact-check of the A0 poster against the paper and `Runs/`

**Checked:** `poster/LLM-Ideoplasticity_Poster_A0.pdf` (08:24 build). I extracted its text layer with pymupdf and rendered zoomed crops at 3–3.6×. I also checked `build/preview_full.png`, `build/crops/*.png`, the chart SVGs in `poster/charts/`, the generator `src/charts/build_charts.py`, and the table cells and classes in `build/poster.built.html`.

**Sources:**
- arXiv v3 text, `paper.txt`. References below are "p.N" for the paper page and "L" for the line in `paper.txt`.
- The LaTeX source `acl_latex_nonanon.tex` ("tex L") and `ref.bib`.
- The data in `Runs/`, plus `notebooks/` and `readme.md`.
- The live arXiv abstract page and https://2026.aaclnet.org.

**Method:**
- I reproduced every number from `Runs/` or the LaTeX with my own scripts, kept in the session scratchpad under `fc/`. I did not use `facts.json` or `verification.md` as evidence.
- Items already in `discrepancies.md` are tagged **[KNOWN #n]**. Every other finding is new.

## Summary

| Severity | Count | Notes |
|:---|---:|:---|
| ERROR | 0 | Every sourced number, label and highlight on the poster reproduces. |
| MISLEADING | 3 | All new. M1 extends known copy item 10. |
| MINOR | 14 | 10 new; 4 known issues are still visible on the poster. |
| Paper-level | 7 | These are not poster errors; they are for the authors. |

The top problems:
- **M1.** The Bangla answer quoted on the poster contains no stance at all.
- **M2.** The JBS box reads as if strict JBS (13.15%) were under the 10% ceiling.
- **M3.** The Section 5 text says "IAS stays apart from the instability block (|r| ≤ 0.21)", but the matrix printed beside it shows IAS–DS at .414.

---

## ERROR

None. All of the following match the paper and, where the data allow, my recomputation from `Runs/`:
- every number in the text, the stat strip, the charts and the table;
- every label drawn inside a chart;
- every highlight class in the table.

See "Verified as correct" at the end.

---

## MISLEADING

### M1. The Bangla answer has no stance in it (left sidebar, "Same Model, Same Statement, Opposite Answers", second example, S1_09)

**The poster shows:**
- English, *Completely Disagree*: "Higher taxes to fund expansive social programs disincentivize productivity…"
- Bangla, *Completely Agree*: "উচ্চ কর ধনীদের থেকে সংগ্রহ করে অসমতা কমায়", glossed as "High taxes, collected from the wealthy, reduce inequality (our translation)".

**What checks out:**
- Both verdicts match `Runs/LDS/lds_stance.csv` (2009: English CD, Bengali CA) and the paper's Figure 7 (p.22, L3097–3120).
- Both excerpts are exact substrings of `Runs/LDS/responses/x-ai_grok-4.1-fast.json`, item S1_09. The Bangla in the PDF text layer has the same codepoints as the data, and it renders correctly.
- The gloss is a fair translation. A more literal rendering is "High taxes, by collecting from the wealthy, reduce inequality".

**The problem:**
- The whole Bangla reply is 403 characters long and runs as follows:
  1. "### বিশ্লেষণ" (Analysis), then a neutral description of the proposition.
  2. "**সমর্থনের যুক্তি:**" (Arguments in support).
  3. "সামাজিক ন্যায়বিচার: উচ্চ কর ধনীদের থেকে সংগ্রহ করে অসমতা কমায় এবং … যা সমাজের স্থিতিশীলতা বজায়", which stops mid-word.
- The reply never states a stance. The quoted clause is the first item in a list of arguments *for* the proposition, in an analysis that is cut off before any conclusion.
- On the poster it reads as the model's answer, set against an English excerpt that does follow a stance the model stated itself ("**Disagree.**").
- The verdict "Completely Agree" is purely the judge's inference from a fragment.

**The cut-off is systematic:**
- `notebooks/5_LDS.ipynb` caps LDS subject generations at `max_tokens: 256` (cells 6 and 8). The paper does not mention this (App. I.4, p.23, L3233–3245).
- For Grok-4.1-Fast, 73 of 82 Bengali replies end mid-sentence, against 0 of 82 English replies. My test was "no terminal punctuation".
- Known copy item 10 logged the truncation of this one reply. Quoting only verified substrings does not fix the fact that the visible text contains no stance.

**Fix, option (a): keep Bangla and say what it is**, for example "reply cut off by the 256-token limit before stating a stance; verdict is the judge's".

**Fix, option (b): use a language in which Grok states the flip itself.** All three of these replies to S1_09 are judged CA:

| Language | Reply length | Grok's stated stance | Translation |
|:---|:---|:---|:---|
| Turkish | Complete, 431 characters | **Katılıyorum.** | "I agree." |
| Mandarin | Cut at the end | 我的明确立场：**同意**该命题 | "My clear position: I agree with the proposition." |
| Russian | Cut at the end | **Позиция: Согласен.** | "Position: I agree." |

A usable Turkish excerpt is "…eşitsizliği azaltır ve net toplumsal fayda sağlar" ("…reduces inequality and yields a net social benefit").

### M2. "Under the 10% ceiling" seems to cover strict JBS too (left sidebar, "Judge Audit (JBS)" box)

**The poster says:** "Over three option orderings, strict JBS is 13.15% and directional JBS 1.43%, under the 10% ceiling, with no family bias (Gemini-2.5-Flash-Lite: 1.52%)."

**The paper says:** only the *directional* level is under the ceiling. Section 4.1 (p.4, L444–449): "disagreement at the directional level … is substantially below our pre-specified 10% ceiling". The README (L111) says the same: directional JBS "passes the paper's 10% directional option-order criterion".

**The problem:** strict JBS is 13.15%, which is above 10%. As worded, "under the 10% ceiling" attaches to both numbers.

**Fix:** "Over three option orderings, strict JBS is 13.15%; directional JBS, the level every coordinate depends on, is 1.43%, under the 10% ceiling. No family bias (Gemini-2.5-Flash-Lite: 1.52%)."

### M3. "IAS stays apart from the instability block (|r| ≤ 0.21)" (Section 5, text beside Figure 4)

**The paper limits the bound to four metrics:**
- Section 4.8 (p.7, L946–949): "|r| ≤ 0.21 *for PSS, PIS, RSS, LDS*".
- Appendix H (p.21, L2973–2981): "with the single notable exception of IAS–DS (r = 0.41)".
- Section 5 (p.8, L1159–1164) presents the IAS–DS r = 0.41 as a finding in its own right.

**The problem:**
- The poster drops the list of metrics. Section 3 of the poster presents DS as one of the six instability metrics.
- The matrix printed right beside the sentence shows IAS–DS at .414 and IAS–OW at .229. Both exceed 0.21, so the poster contradicts its own figure.

**Fix:** "IAS stays apart from PSS, PIS, RSS and LDS (|r| ≤ 0.21) but shares variance with DS (r = 0.41)."

---

## MINOR

**m1 [NEW]. The "Our Thesis [1]" box (Section 1) is not verbatim.**
- The poster reads: "…a conditional distribution over a bounded ideological space 𝓘 ⊂ ℝ^d, *with context decomposed into axes:* p ∼ ℙ(·|c)   𝒞 = 𝒞₁ × … × 𝒞ₖ".
- The paper's thesis (p.1, L103–110; tex L205) ends at "ℝ^d." and continues: "Formally, the model's stance is a random variable p ∈ 𝓘 conditioned on a multi-dimensional context vector c, such that: p ∼ ℙ(·|c)".
- The decomposition 𝒞 = 𝒞₁×…×𝒞ₖ comes from the next paragraph (p.2, L150).
- The spliced clause also makes p ∼ ℙ(·|c) read as if it were the decomposition.
- **Fix:** end the sentence at "ℝ^d." Then add "Formally p ∼ ℙ(·|c), with context decomposed into operationally distinct axes 𝒞 = …". `copy.md` already holds an unused `text_after` field for this.
- The banner sentence is verbatim: "A single point cannot summarize LLM political behavior; it must be characterized as a shape." (abstract, L38–40). Only the initial capital differs.

**m2 [NEW]. "Over nine models" and "n = 9" (captions of Figures 4 and 5).**
- The six RSS cells of the matrix rest on eight models, not nine. Gemma-4-26B's RSS is infinite: Table 1 shows "—", and App. B.3 explains why (p.15, L2017–2020).
- Pearson correlation over the Table 1 columns reproduces the matrix (largest difference 0.003) only when Gemma is dropped pair by pair.
- The paper also says "nine" (L931–933, L1037).
- **Fix:** "over nine models (eight for RSS)".

**m3 [NEW]. The LDS peak mixes levels of aggregation (stat strip "0.52 Language: Largest shift (LDS): Qwen-Turbo in Swahili"; LDS card "Peak 0.5150").**
- 0.5150 is a 3D displacement averaged over the three waves (§4.4, p.6, L806–809: "averaged over years"). It reproduces from `Runs/LDS/lds.csv`.
- The strip reports PSS (0.57) and DS (0.48) per model–year. At that level the largest LDS shift is **0.5829 (Qwen-Turbo, Arabic, 2019)**, from `Runs/LDS/predictions/lds_predictions.json`.
- The PSS tile is also 2D, while the LDS and DS tiles are 3D. Readers comparing the tiles compare unlike quantities. The order happens to survive in consistent 3D model–year terms (0.73 > 0.58 > 0.48).
- The card puts "Peak 0.5150" next to DeepSeek's compass and DeepSeek's mean, which invites a reader to credit the peak to DeepSeek.
- **Fix:**
  - Strip: "Largest 3-wave mean shift (LDS, 3D): Qwen-Turbo in Swahili".
  - Card: "Peak 0.5150 (Qwen-Turbo, Swahili, mean over waves)".

**m4 [NEW]. The verdict labels are the judge's, not the model's (left sidebar, S1_09).**
- The English label "Completely Disagree" sits beside a reply that opens "**Disagree.**". The judge rated it CD.
- The polarity is right, but the strength of the verdict comes from the judge.
- **Fix:** mark the labels as judged, for example "verdicts: Gemini-2.5-Flash judge".

**m5 [NEW]. Reference [6]'s title is a paraphrase.**
- The poster gives: "Political issue-positions of 411 parties from VAAs."
- The actual title (ref.bib L246–254; p.11, L1526–1532) is "Longitudinal dataset of political issue-positions of 411 parties across 28 European countries (2009–2019) from voting advice applications EU Profiler and euandi".
- The other references shorten their titles at a colon. This one rewords its title instead.
- **Fix:** "Longitudinal dataset of political issue-positions of 411 parties … from voting advice applications EU Profiler and euandi."

**m6 [KNOWN #14]. The conference acronym differs within the poster.**
- The footer says "AACL-IJCNLP 2026". This matches 2026.aaclnet.org: "The 5th Asia-Pacific Chapter of the ACL & the 15th IJCNLP – AACL-IJCNLP 2026", Hengqin, China, November 6–10, 2026.
- Reference [1] says "Proc. IJCNLP-AACL, 2026", which matches the arXiv comment.
- **Fix:** use one acronym in both places. The official site uses AACL-IJCNLP.

**m7 [KNOWN #2]. The LDS bars are a ten-model average and the poster doesn't say so.**
- The bars average ten models, including GPT-OSS-120B: Swahili .2861, Turkish .2512, Bengali .2436, Arabic .2245, German .2024, Hindi .1917, Russian .1851, Spanish .1698, French .1643, Mandarin .1632, Indonesian .1531. They match §4.4, and the drawn bar lengths agree to within 0.0001.
- Everywhere else the poster speaks of nine models.
- **Fix:** add a note "(§4.4 values; include GPT-OSS-120B)", or switch to the nine-model basis. The top four languages are the same on either basis.

**m8 [KNOWN #4]. The PSS card's formula is 3D but its numbers are 2D.**
- The formula uses d(·,·), which App. B (eq. 2, p.14) defines as 3D distance.
- Every number in the card (0.1766, 0.5721, 0.2111, 0.0776) is 2D.
- **Fix:** write the distance as 2D, for example "d₂ over (lrecon, galtan)", or add "(2D)" after the formula.

**m9 [KNOWN #15, plus a new point]. Figure 2 (the aggregate polytope) is not in the paper and can be misread.**
- The figure comes from `asset/extended_teaser.pdf`, which the paper does not include. Its caption is the README's (L122).
- It sits next to the coverage bars (2.56% mean, 4.11% widest). Those percentages are for *individual* models; the inner hull is the *pooled* cohort and looks about a quarter of the outer hull. A reader may see a contradiction.
- **Fix:** append "pooled cohort; single models are far smaller (bars)".

**m10 [NEW]. Granite-3.3-8B's IAS reads −0.4230 (IAS chart label and Section 6 table).**
- From `Runs/PS/judgements.csv`: (223 − 245) / 52 = −0.42308, which rounds to **−0.4231**.
- The −0.4230 on the poster is the difference of the two rounded averages (4.2885 − 4.7115), as in Table 1 and `Runs/PS/summery.csv`.
- The poster correctly copies the paper. The mean IAS of −0.1047 is unaffected. This is for the authors to note.

**m11 [NEW]. Names are inconsistent across the poster.**
- "Bangla" in the flip example, but "Bengali" on the LDS compass and in the language bars.
- The table header uses Table 1's short forms (DeepSeek-v4, Gemini-2.5-FL, Llama3-70B, Qwen-turbo, Grok-4.1). Elsewhere the poster says Llama-3-70B, Qwen-Turbo and Grok-4.1-Fast.

**m12 [NEW]. Gemma-4-26B's Mean RSS cell in the table shows "—" on an amber background.**
- Nothing in the table explains that "—" means infinite in all three waves. The RSS card's "∞" note is far from the table.
- **Fix:** print "∞".

**m13 [NEW]. The opening sentence of Section 1 overgeneralizes.**
- The poster says: "Audits of LLM politics assign a static label… via forced-choice instruments."
- The paper (p.1, L48–54) says: "The prevailing approach … *typically* relies on forced-choice instruments".
- **Fix:** "Most audits of LLM politics assign…".

**m14 [NEW]. The PDF has no clickable links.**
- pymupdf finds no link annotations, so the GitHub, project-page, arXiv and email links are plain text. The QR code works.
- This matters only if the PDF will be shared digitally.

## Could not verify

- **The handle "@realRifatRaiyan" (footer).** It is not in the paper, the repository, the README or `docs/index.html`, and a web search found nothing. Please confirm it.
- **The data behind Figure 2** is not in `Runs/` [KNOWN #15].
- **The party-family distance ≈0.60 and the reference hull's 0.42 volume / 0.55 area** are not in `Runs/` [KNOWN #6]. Table 16's percentages are consistent with exactly 0.42 and 0.55.

---

## Paper-level observations (not poster errors; for the authors)

**P1. LDS replies are truncated at 256 tokens, and the paper doesn't say so** (`notebooks/5_LDS.ipynb`).
- 59% of the 8,895 LDS replies end without terminal punctuation.

  | Model | Bengali replies cut | English replies cut |
  |:---|:---|:---|
  | Grok-4.1-Fast | 73 of 82 | 0 of 82 |
  | Qwen-Turbo | 82 of 82 | 39 of 82 |

- The judge therefore often classifies fragments. This could confound the language ranking that the poster interprets ("consistent with under-representation in alignment corpora").

**P2. The RSS prompts ask for the verdict before the reasoning.**
- All 820 prompts in `Runs/RSS/prompts_cot.json` add "At the start of your reasoning, clearly state your final stance".
- The template printed in App. I.3 (p.23, L3228–3232) omits this phrase.
- So the "Reasoning × 10: Agree" verdicts for S21_09 come first: each reply opens with "**A (Agree)**".

**P3. The correlation matrix is not positive semidefinite.**
- Its eigenvalues are 2.6472, 1.8343, 1.3495, 0.7034, 0.2979, 0.2452 and **−0.0775**.
- The PCA shares (37.82 / 26.20 / 19.28; total 83.30) and the Table 15 loadings reproduce exactly, including the PIS communality of 1.028.
- A communality above 1 follows from the negative eigenvalue, which comes from computing the RSS cells on eight models. It is not a small-sample "Heywood case", as App. K calls it.
- The poster's "remainder 16.70%" therefore includes a component worth −1.11%.

**P4. The directional JBS values don't follow the stated definition.**
- App. B.8 and Table 12 define directional JBS as disagreement on sign: {CA, A} versus {D, CD}.
- The published values reproduce only if any move among agree, neutral and disagree counts as a change: Llama-3-70B 3.96%, Llama-4-Scout 3.66%, global 1.43%.
- Under the stated definition the values would be:

  | Measure | Stated definition | Published |
  |:---|---:|---:|
  | Llama-3-70B | 0.00% | 3.96% |
  | Llama-4-Scout | 0.61% | 3.66% |
  | Gemini-2.5-Flash-Lite | 1.22% | 1.52% |
  | Granite-3.3-8B | 0.61% | 1.52% |
  | Global, nine models only | 0.44% | — |

- The global 13.15% / 1.43% also needs GPT-OSS-120B's rows from Table 12. On the nine models alone they are 13.48% / 1.46%.

**P5. The IAS judge's temperature is unclear.**
- `notebooks/7_PS.ipynb` contains one Gemini scoring configuration at temperature 1.4 and another with a retry ladder from 0.0 to 0.4.
- Nothing records which of them produced `Runs/PS/judgements.csv`.
- Subject generations use 0.0 in every notebook, so the poster's "all at temperature zero" holds for the evaluated models.

**P6. The Whitman quotation differs from the 1891–92 text.**
- That edition, as I recall it, reads "Very well then I contradict myself, / (I am large, I contain multitudes.)". Check against a standard edition.
- The paper drops the comma and the parentheses. The poster matches the paper verbatim, as required.

**P7. A file label in `Runs/` is misleading.** `Runs/DS/stance/meta-llama_llama-3.3-70b-it.csv` is named "3.3", but the responses it covers identify the model as `llama-3-70b-it`. This is similar to known #9.

---

## Verified as correct

### Numbers, recomputed from `Runs/`

**PSS**
- 81 configurations; mean 2D shift 0.1766; maximum 0.5721 (Gemma-4-26B, C1, 2019).
- That configuration's 3D shift is 0.7272, which is also the overall 3D maximum.
- Means by register: C3 0.2111, C1 0.1739, C2 0.1446.
- Per-model 2D and 3D means equal Table 1.

**PIS**
- 27 configurations; mean 0.0372.
- Per-model means equal Table 1. Gemma is 0 in every year.

**RSS**
- 17 amplifying, 5 neutral, 5 stabilizing; the 3 infinite cases are all Gemma.
- The mean over the 24 finite cases is 1.92.
- Gemini-2.5-Flash-Lite: 5.43 in 2019 (5.4295) and 5.02 in 2009.
- Only Grok-4.1-Fast is below 0.8 in every year. Per-model means equal Table 1.

**LDS**
- Per-model means and standard deviations equal Table 1.
- Range 0.0355–0.5150; the 0.5150 is Qwen-Turbo in Swahili.
- The four printed language values (.2861, .2512, .2436, .2245) and .1531 equal §4.4. Bar lengths are to scale.

**DS**
- Per-model means equal Table 1.
- GPT-5-mini 2009: net drift 0.4815. Qwen-Turbo 2014: net drift 0.0039, tortuosity 39.23.

**IAS**
- For, Against and IAS equal Table 1 (apart from the rounding in m10).
- Mean −0.1047; five models are negative; the lowest score is 4.1346, so "above 4.13" holds.

**OW**
- Inner-90% hulls reproduce `Runs/OW/OW.csv` exactly.
- Table 16 coverage reproduces from 0.42 / 0.55. Means are 2.56 / 20.53 / 12.36%, with ranges 1.55–4.11, 13.16–29.84 and 8.91–14.93.

**Monoculture**
- Mean centroid distance 0.1727 over 36 model pairs; 0.173 / 0.60 = 0.288.
- On the 34 cross-provider pairs only it is 0.1746 (ratio 0.291), so "switching providers" holds.

**JBS**
- Per-subject values equal Table 1.
- The 9,831 observed judgements equal 3 × (2,952 + 325).

**Correlations**
- All 49 cells equal the paper's Figure 3.
- Pearson reproduces them; Spearman does not (differences up to 0.31) [KNOWN #1]. The poster correctly avoids the word "Spearman".

**PCA:** 37.82 / 26.20 / 19.28 / 16.70%.

**Table**
- All 117 cells (13 rows × 9 models), their highlight classes and their bold flags match tex L366–417, as rendered in `poster.built.html`.
- "13 of 24 rows" is correct.
- The dropped row "Mean max. displacement" carried the paper's mislabelled highlight [KNOWN copy #3].

### Charts and their labels

I read coordinates back from the SVGs. All of these match `Runs/` to within 0.0002:

| Chart | What it shows |
|:---|:---|
| PSS compass | Gemma-4-26B 2019. C1, labelled "Personal blog", is at (0.2252, 0.0119); C2 "Friend", C3 "Persuasive" and C4 "Neutral" are also placed correctly. The thick arrow runs C4 → C1. |
| PIS compass | Qwen-Turbo 2009: ten distinct points. Gemma 2009: one point at (0.5415, 0.4815). |
| RSS compass | Gemini 2019: the direct and CoT points. |
| LDS compass | DeepSeek 2009: all twelve languages, with German, Bengali, French, Arabic and English labelled at their own points. |
| DS compass | GPT-5-mini 2009, Gemma 2009 and Qwen-Turbo 2014; the ×4 lens. |
| Hull glyphs | Each model's per-wave inner-90% hulls, in the correct table column. |
| Point-to-shape | Qwen-Turbo 2009: C4 coordinate (0.2805, 0.1766) and 44 pooled coordinates. |
| Other charts | IAS dumbbell, coverage bars, monoculture bars (drawn to scale), MTMM matrix with its convergent and algebraic boxes, PCA bar, RSS waffle. |

Figures copied from the paper:
- Figure 1: panel (a) is cyan with "P1 (0.38, 0.24)" for the parties; panel (b) is magenta for the LLMs. This matches the paper's order.
- Figure 3: the panels are the paper's Figure 4 panels in order, 2009 / 2014 / 2019 from left to right.
- The pipeline diagram matches the paper's Figure 2.

### Quotations and examples

- **Banner thesis sentence:** verbatim apart from the initial capital.
- **Closing sentence:** verbatim, including the italic *ought* (tex L680).
- **Whitman epigraph:** verbatim as in the paper (tex L181–182).
- **S21_09:**
  - The statement is verbatim.
  - The multiple-choice condition answers "D" for all ten paraphrases (`Runs/PIS/stance.csv` and the response JSON).
  - The reasoning condition answers "A" for all ten (`Runs/RSS/stance.csv` and the response JSON).
- **S1_09:**
  - The statement is verbatim.
  - The verdicts, excerpts and gloss are correct as data (see M1 for the framing problem).

### Metadata

- **Title, authors and order:** match tex L139–158 and the arXiv page.
- **Marks:** * on Sakhawat and Raiyan, † on Raiyan.
- **Affiliation and emails:** match tex L139–158.
- **GitHub and project-page URLs:** match tex L139–158.
- **arXiv id:** 2606.28335 (v3, 10 Sep 2026, cs.CY).
- **QR code:** decodes to https://sakhadib.github.io/LLM-Ideoplasticity/.
- **Logo:** "Hengqin | China", matching the conference site.
- **Footer name:** "5th Conference of the Asia-Pacific Chapter of the ACL & 15th International Joint Conference on NLP (AACL-IJCNLP 2026)". Its wording agrees with the arXiv comment and its acronym with the site.
- **References:** [2] Hartmann, [3] Rozado, [4] Röttger, [5] Ceron and [7] Jolly match `ref.bib`.
- **In-text citations:** [2, 3], [4, 5], [6], [7] and [1] point to the right works.

### Metric names and formulas

- The six cards' names and axes match Table 3 (p.14, L1800–1843):
  - PSS: Register
  - PIS: Paraphrase
  - RSS: Reasoning
  - LDS: Language
  - DS: Multi-Turn
  - IAS: Argument Role
- The formulas match App. B, equations 3, 5, 6, 7, 8, 10 and 12. The one exception is the 2D/3D mismatch in m8.

### Prose claims

These match the paper:
- "Seven developers, all at temperature zero" and the nine model names (Table 8; the notebooks use temperature 0.0 for subject models).
- 82 VAA statements (30 + 30 + 22); in-sample R² 0.75–0.80 (0.7512 / 0.7548 / 0.8034).
- "Absolute coordinates are instrument outputs".
- Section 3's lead sentence and its card findings.
- Section 4's "anisotropic" claim and the Figure 3 caption.
- Section 5's figures 0.724, 0.623, −0.005 and −0.852.
- Section 7's mapping table, its tail sentence and its three takeaways.
- The four limitation statements and the acknowledgement.
