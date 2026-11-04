# Sources for every claim in `poster/src/copy.md`

Page numbers refer to the arXiv PDF (v3, 43 pages), as marked in `SP\paper.txt`. "Data" means a file under `Runs/`, recomputed by script.

Re-check pass (`SP\scripts\copy_verify.py`): all character budgets met; 16 table rows, every value, highlight class and bold flag match the LaTeX of Table 1 (0 mismatches); every number token found in the paper except 0.73 (rounds 0.7272, p. 5) and the hex fragments 405 and 99 in the stance colours; every verbatim string matched against its source file.

## Band, epigraph, thesis

| Field | Claim | Source |
|:---|:---|:---|
| band.title, authors, marks, affiliation, emails, links | Exact title, order, equal-contribution and corresponding marks | p. 1; LaTeX lines 139-158, 171-172 |
| band.links arXiv id | 2606.28335 | p. 1 margin; README |
| epigraph | Whitman, *Song of Myself*, § 51 (1892) | p. 1; LaTeX line 181 |
| thesis_sentence | Verbatim from the abstract, first letter capitalised | p. 1; LaTeX line 175 (checked by script) |

## Sidebar

| Field | Claim | Source |
|:---|:---|:---|
| s1_intro | Forced-choice instruments, static label, "left-libertarian" | p. 1 intro; §2 p. 2 |
| s1_intro | Materially different coordinates under paraphrase or register | p. 1; §2 "Spinning-Arrow Critique" p. 2 (framing, paraphrasing) |
| s1_intro | "the constructive alternative" | p. 9 |
| box_thesis | Text and equations; $\mathcal{I}\subset\mathbb{R}^d$; product of axes; single-axis perturbation | p. 1-2, Eq. 1; "each experiment isolates a single axis" p. 2 |
| box_contributions | Four contributions; "nine frontier models" shortened to "nine models" | p. 2 |
| s2_framework.text | Three methodological requirements | p. 2 |
| s2_framework.pipeline_caption | Pipeline description | Figure 2, p. 2 |
| coord_system.text | 82 statements | Appendix N in Table 2 p. 13; Table 17 p. 43; 30 + 30 + 22 in C.1 p. 16 |
| coord_system.text | Three CHES dimensions, $[0,1]$, year-specific bagged ElasticNet | §3.1 p. 3 |
| coord_system.text | Fixed projection, relative distances robust | §3.1 p. 3 |
| coord_system.text | Absolute coordinates are instrument outputs | Limitations p. 9-10 |
| coord_system.axes | lrgen, lrecon, galtan glosses | Table 5 p. 14 |
| coord_system vaa_wave_table | Parties and features | C.1 p. 16 |
| coord_system vaa_wave_table | CV MSE 0.0216, 0.0195, 0.0174; $R^2$ 0.7512, 0.7548, 0.8034 | Table 9 p. 17 |
| cohort.models | Nine abbreviated names | §3.4 p. 4; Table 8 p. 16 |
| cohort.text | Seven developers, closed and open-weight, temperature zero, variance attributable to context | §3.4 p. 4 |
| box_jbs | Gemini-2.5-Flash, zero-shot stance judge | §3.2 p. 3 |
| box_jbs | Three orderings; strict 13.15%; directional 1.43%; 10% ceiling | §3.2 p. 3; §4.1 p. 4; Table 12 p. 20 |
| box_jbs | No family bias; Gemini-2.5-Flash-Lite 1.52% | §3.2 p. 3; §4.1 p. 4 |
| box_jbs | Scope: categorical stance, not Likert scoring or LDS translations | §3.2 "Scope of Audit" p. 3 |

## Stage

| Field | Claim | Source |
|:---|:---|:---|
| fig1 | Caption; cyan parties, magenta LLMs; *vis-à-vis* | Figure 1, p. 1; LaTeX line 200 |
| fig1.files | Panel (a) is PDF pages-2, (b) is pages-1 | LaTeX lines 196-198 (pages-2 is set first, above) |
| stats 0.57 | 0.5721 2D maximum | §4.2 p. 4-5; §5 p. 8 ("up to 0.57 (PSS)") |
| stats 0.73 in 3D | 0.7272 | §4.2 p. 5 |
| stats 0.52 | 0.5150 range maximum; "up to 0.52 (LDS)" | §4.4 p. 6; §5 p. 8 |
| stats Qwen-Turbo in Swahili | Pair with the maximum | Data: `LDS/lds.csv` (0.5150) |
| stats 0.48 | "up to 0.48 (DS)" | §5 p. 8 |
| stats GPT-5-mini, 2009 | Pair with the maximum, 0.4815 | Data: `DS/coordinates/DS_drift_metrics.csv` |
| stats 17/27 | 17 amplifying of 27 | §4.3 p. 5; Appendix G p. 18 |
| stats 2.56% | Cohort mean of individual-model 3D hull coverage | Table 16 p. 27; Appendix L p. 26 |
| stats ≈0.29 | 0.173 / ≈0.60 | Appendix L p. 26 |
| s3_local | Single-axis isolation; temperature zero; rankings differ, *prima facie* | p. 2; p. 4; §5 p. 8 |

## Cards

| Field | Claim | Source |
|:---|:---|:---|
| all full, axis | Metric names and axis labels | Table 3 p. 14 |
| all definition | Quantity measured, condensed | Table 3 p. 14 |
| all formula | Closed forms; DS drops the $m,s$ indices and shows two of Eqs. 8-11 | Appendix B p. 14-15 |
| PSS.finding | 81 configurations; mean 0.1766; maximum 0.5721, Gemma-4-26B, C1, 2019 | §4.2 p. 4-5; data `PSS/prompt_sensitivity_scores.csv` |
| PSS.finding | C3 largest mean 0.2111 | §4.2 p. 4 |
| PSS.finding | Llama-3-70B 0.0776, most prompt-rigid | §4.2 p. 4; Table 1 p. 5 |
| PSS.chart_labels | C1 to C4 register names | Table 6 p. 15; Appendix I.1 p. 23 |
| PIS.finding | Mean 0.0372 over 27 configurations; heterogeneous; Qwen-Turbo 0.0622; Gemma-4-26B 0 every year; forced-choice | §4.3 p. 5; data `PIS/pis.csv` |
| RSS.finding | "Reasoning is not a stabilizer"; 17, 5, 5 of 27; mean 1.92 over 24 finite | §4.3 p. 5; data `RSS/rss.csv` |
| RSS.finding | Gemini-2.5-Flash-Lite 5.43 (2019); only Grok-4.1-Fast below 0.8 every year | §4.3 p. 5; Appendix G p. 20 |
| RSS.chart_note | Three formally infinite, all Gemma-4-26B | §4.3 p. 5 |
| LDS.finding | Eleven non-English languages; maximum 0.5150 | §4.4 p. 6 |
| LDS.finding | Swahili, Turkish, Bengali, Arabic largest, same order under both the paper's and the nine-model values | §4.4 p. 6; data `LDS/lds.csv` |
| LDS.finding | Under-representation in alignment corpora | §4.4 p. 6 |
| LDS.finding | DeepSeek-V4-Flash 0.3097 | §4.4 p. 6; Table 1 p. 5 |
| DS.finding | GPT-5-mini 0.3675, 0.9653, "clear outlier"; Gemma-4-26B 0.0067 "barely moves"; Qwen-Turbo 2014 0.0039 and 39.23; endpoint-only summaries miss it | §4.5 p. 6; data `DS/coordinates/DS_drift_metrics.csv` |
| IAS.finding | Above 4.13 on 0-5; mean −0.1047; five of nine; Granite-3.3-8B −0.4230; Gemini-2.5-Flash-Lite and Qwen-Turbo balanced | §4.6 p. 6; data `PS/summery.csv` |

## Flips

| Field | Claim | Source |
|:---|:---|:---|
| reasoning_flip.statement | S21_09 text | Figure 6 p. 21; data, exact match |
| reasoning_flip left | "D" ten times | Data: `PIS/responses/x-ai_grok-4.1-fast.json`, `PIS/stance.csv` |
| reasoning_flip right | Judged "A" ten times; excerpt from p1 | Data: `RSS/responses/x-ai_grok-4.1-fast.json`, `RSS/stance.csv`; Figure 6 inset |
| language_flip.statement | S1_09 text | Figure 7 p. 22; data, exact match |
| language_flip.statement_bn | Bangla statement | Data: `LDS/responses/x-ai_grok-4.1-fast.json`, exact match |
| language_flip left | Verdict CD; excerpt | Same file, language English; `LDS/lds_stance.csv`; §4.4 p. 6 |
| language_flip right | Verdict CA; excerpts | Same file, language Bengali; `LDS/lds_stance.csv`; §4.4 p. 6 |
| language_flip.right_gloss | English gloss | Our translation of the Bangla excerpt, labelled as such |
| flips.scale | Stance colours | Commented caption in the LaTeX, line 1455 |

## Lower half

| Field | Claim | Source |
|:---|:---|:---|
| s4_global.finding | Qwen-Turbo 4.11%; mean 2.56%, 20.53%, 12.36% | Table 16 p. 27; Appendix L p. 26 |
| s4_global.finding | Anisotropic | Appendix L p. 26; §5 p. 8 |
| s4_global.finding | Nine alignment regimes from seven providers | §5 p. 8 |
| s4_global.coverage_caption | Reference CHES party hull, per model | Tables 11 and 16, p. 18 and p. 27; values in `poster/data/facts.json` |
| s4_global.monoculture | 0.173; ≈0.60; less than one-third | Appendix L p. 26; §5 p. 8-9 |
| s4_global.temporal | Party landscape shifts and reorients | Appendix E.2 p. 18 |
| s4_global.temporal | Envelope "stays narrow" | README's caption ("remains consistently narrow"); chosen over the paper's "inert" and "static", see discrepancies |
| s4_global.polytope_caption | Central 90% hulls, pooled nine LLMs, aggregate | README, "Aggregate Overton geometry across 2009, 2014, and 2019"; Figure 4 caption p. 19 |
| s4_global.chrono_caption | Year-specific, lrecon-galtan, $[0,1]$, outer parties, inner pooled LLMs | Figure 4 caption, p. 19 |
| s5_mtmm.text | Distinct but related facets; 0.724; 0.623; $|r|\le 0.21$; $-0.005$; $-0.852$ algebraic | §4.8 p. 7; Figure 3 p. 7 |
| s5_mtmm.matrix_caption | Spearman, nine models; structure over cells at $n=9$ | §4.8 p. 7 |
| s5_mtmm.pca_caption | 83.30%; exploratory | §4.8 p. 7; Appendix K p. 25; Table 15 p. 27 |
| s5_mtmm.pca_caption | "Suggestive rather than definitive" | README, Key findings row 5 |
| s5_mtmm.pca_components | 37.82, 26.20, 19.28 and names | Appendix K p. 25; Table 15 p. 27 |
| s6_table | All values and highlights | Table 1 p. 5; LaTeX lines 364-417 |
| s6_table.legend | Highlight meanings | Table 1 caption, p. 5 |
| s7_why.map, map_lead, map_tail | Instrument map | §5 p. 8 |
| s7_why.takeaways 1 | "let's think step by step" | §5 p. 8 |
| s7_why.takeaways 2 | Different conditional distributions | §5 p. 8 |
| s7_why.takeaways 3 | Framework generalizes; numbers will date rapidly | Limitations p. 10; §5 p. 9 |
| s7_why.closing | Verbatim | §6 p. 9 (checked by script) |
| limits 1 | European coordinate system, *ipso facto* | Limitations p. 9 |
| limits 2 | One judge; JBS does not audit Likert quality scoring | Limitations p. 9 |
| limits 3 | Temperature zero; joint estimation left to future work | Limitations p. 9 |
| limits 4 | Snapshots; rapidly dating numbers; PCA exploratory | Limitations p. 10; Appendix K p. 25 |
| ack | SSL computing resources; reviewers | Acknowledgements p. 10 |
| refs | Six works plus this paper | `ref.bib` keys hartmann2023political, rozado2024political, rottger2024political, ceron2024beyond, reiljan2020longitudinal, jolly2022chapel; [1] per README's citation and the arXiv comment |
| footer.center | Conference name | 2026.aaclnet.org; logo; see discrepancies for the naming mismatch |
| footer.right | Handle and email | Their ACL 2023 and ICCV 2025 posters; corresponding author, p. 1 |

## Italic Latin, total three

*vis-à-vis* (fig1), *prima facie* (s3_local), *ipso facto* (limits). *et al.* is not counted.

## Added during layout

- "in-sample R2 0.75-0.80": Table 9 and section 3.1 (R2 0.7512, 0.7548, 0.8034).
- Pipeline figure: the paper's Figure 2, redrawn natively with the same boxes and labels so they hold 17 pt.
- Wording was shortened for fit in `copy.md`; no number changed.

## Round 3 (decided list and the user's requests)

Superseded rows above follow the entries here.

| Field | Claim | Source |
|:---|:---|:---|
| s1_intro.text | "typically" (fact-check m13) | §1 p. 1: "typically relies on forced-choice instruments" |
| box_thesis.text_before | Verbatim, ends at R^d | §1 p. 1 (tex L205) |
| box_thesis.formal_a/b, eq1, eq2 | p ~ P(.|c); C = C1 x ... x Ck over operationally distinct axes | §1 pp. 1-2 (eq. 1; L150) |
| box_jbs.text | Only directional JBS is under the 10% ceiling (fact-check M2) | §4.1 p. 4; README L111 |
| box_jbs.title_note | Gemini-2.5-Flash, zero-shot stance judge | §3.2 p. 3 |
| coord_system.text | 82 statements; CHES dimensions and their glosses; R2 0.75-0.80 | §1 p. 2; §3.1 p. 3; Table 9 |
| coord_system.compass_caption | Compass axes, both on [0, 1] | §3.1 p. 3 (min-max rescaled targets) |
| stats.items 0 | 0.5721 is Gemma-4-26B, C1 (personal blog), 2019, 2D; 3D 0.7272 | §4.2 p. 5 |
| stats.items 1 | 0.5150 is Qwen-Turbo in Swahili, averaged over waves (fact-check m3) | §4.4 p. 6; `Runs/LDS/lds.csv` |
| stats.items 2 | 0.4815 is GPT-5-mini's 2009 net drift | `Runs/DS/coordinates/DS_drift_metrics.csv`; §5 p. 8 ("up to 0.48") |
| stats.items 3-5 | 17/27; 2.56%; about 0.29 | §4.3 p. 5; Table 16 p. 27; Appendix L |
| cards.LDS.finding | Peak attributed to Qwen-Turbo in Swahili; "under-represented languages" shift most | Abstract p. 1 ("under-represented languages displace coordinates"); §4.4 p. 6 |
| cards.*.formula | Typeset by pdflatex from App. B equations 3, 5, 6, 7, 8, 10, 12 | Appendix B pp. 14-15 |
| flips.reasoning_flip | Grok-4.1-Fast, S21_09: ten multiple-choice "D", ten reasoning "A" | `Runs/PIS/stance.csv`, `Runs/RSS/stance.csv` (checked by `build.py`) |
| flips.language_flip | English CD, Bangla CA (judge); excerpts verbatim | `Runs/LDS/responses/x-ai_grok-4.1-fast.json`, S1_09 (checked by `build.py`) |
| flips.judge_note | Verdicts are the judge's (fact-check M1, m4) | §3.2 p. 3 |
| fig1.caption | P1, P2 mark the two highest peaks | Figure 1 p. 1 |
| s4_global.polytope_caption | Single models cover 1.55-4.11% of the 3D party hull | Table 16 p. 27 |
| s5_mtmm.text | IAS apart from PSS, PIS, RSS, LDS (abs r <= 0.21), shares variance with DS (r = 0.41) (fact-check M3) | §4.8 p. 7; Appendix H p. 21; §5 p. 8 |
| s5_mtmm.matrix_caption | Nine models, eight for RSS (Gemma's RSS is infinite) (fact-check m2) | Table 1 p. 5; Appendix B.3 p. 15 |
| s6_table | 10 of 24 rows; Gemma's Mean RSS printed as the infinity sign (fact-check m12) | Table 1 p. 5; §4.3 p. 5 |
| limits | Same four limitations, shortened | Limitations pp. 9-10 |
| refs [1] | AACL-IJCNLP, the conference's own acronym (fact-check m6) | 2026.aaclnet.org |
| refs [6] | Verbatim title prefix, then an ellipsis (fact-check m5) | `ref.bib` reiljan2020longitudinal |

The per-year panels (old Figure 3) were cut for height, so the matrix is now Figure 3.

## Round 4: bold insight sentences (each marked by a bulb)

| Field | Bold sentence | Source |
|:---|:---|:---|
| cards.PSS.finding | Register alone can shift a model substantially. | README key finding 1 ("Context can move projected positions substantially"); §4.2 p. 4 |
| cards.PIS.finding | Paraphrase effects are modest but uneven. | §4.3 p. 5: "in aggregate, modest ... but heterogeneous across models" |
| cards.RSS.finding | Reasoning is not a stabilizer. | §4.3 p. 5, verbatim |
| cards.LDS.finding | Language is hidden context. | §5 p. 8: "Language and argumentative role as hidden context" |
| cards.DS.finding | Drift and trajectory are dissociable. | §4.5 p. 6: "Drift and trajectory geometry are dissociable" |
| cards.IAS.finding | Asymmetry is small but systematic. | §5 p. 8: "small in magnitude but directional and systematic" |
| s4_global.finding | Each model's own envelope is small. | §5 p. 8 ("Aggregate monoculture under local plasticity"); Table 16 p. 27 |
| s5_mtmm.text | Yes, as distinct facets of one phenomenon. | §4.8 p. 7: "distinct but related facets of one phenomenon" |
| s7_why.map_lead | The diagnostic instruments are not interchangeable. | §5 p. 8, verbatim |

Evidence after each bold sentence keeps the numbers listed above; the PSS and IAS evidence was trimmed for fit (no number changed).
Takeaways, reworded to one line each: "“Let's think step by step” often amplifies political variability" (§5 p. 8: it "often does the opposite" of damping) and
"Across languages, one model may draw from different distributions" (§5 p. 8: "may be drawing from substantially different conditional distributions").
Section 7's instrument matrix restates the §5 p. 8 map (PSS, LDS, DS, OW) and its tail sentence.

## Round 5: the dek (replaces the stat strip and the `stats` block)

| Field | Claim | Source |
|:---|:---|:---|
| dek.local_text | up to 0.57 (PSS), 0.52 (LDS), 0.48 (DS) | §5 Discussion p. 8: "Prompt framing displaces coordinates by up to 0.57 (PSS), multilingual presentation by up to 0.52 (LDS), and adversarial dialogue by up to 0.48 (DS)"; maxima 0.5721 (§4.2), 0.5150 (§4.4), 0.4815 (`DS_drift_metrics.csv`) |
| dek.local_text | chain-of-thought amplified paraphrase instability in 17 of 27 configurations (RSS) | §4.3 p. 5 |
| dek.global_text | the average model's envelope fills 2.56% of the European party volume (OW) | Table 16 p. 27, cohort mean of 3D volume coverage |
| dek.global_text | the models sit ≈ 0.29 as far apart as party families do | Appendix L p. 25 (cohort monoculture ratio ≈ 0.29; inter-model 0.173 vs. party-family ≈ 0.60) |
| dek.local_phrase, global_phrase | one model, many positions; many models, one region | Poster's punchline pair (BRIEF), restating §5 "Local plasticity is not global breadth" |

The header no longer prints the GitHub, project-page and arXiv links: the title links to arXiv and the QR card to the project page.

