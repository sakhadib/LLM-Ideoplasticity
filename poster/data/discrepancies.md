# Discrepancies found while verifying the poster's chart data

Recomputed from `Runs/` against arXiv v3 (`paper.txt`). `verification.md` lists all checks. The poster follows the paper's body text.

## Worth raising with the authors

1. **The Figure 3 matrix is Pearson, not Spearman.** Section 4.8 and Figure 3 call it a Spearman matrix. Pearson correlation over Table 1 columns reproduces all cells within 0.0005 (inputs: PSS 3D mean, PIS mean, RSS mean (Gemma-4-26B dropped), DS net drift, LDS mean, |IAS|, OW 3D volume). Spearman on the same inputs differs by up to 0.31. The chart shows the paper's numbers unchanged; poster wording should say "cross-metric correlations", or the authors should decide which name stands.
2. **Section 4.4's LDS language values and mean include GPT-OSS-120B.** The text says "nine cohort models", and Appendix F says GPT-OSS-120B contributes to no metric but JBS. Yet the mean .2032 and all eight quoted language means match only `Runs/OW_EXPERIMENT/lds_predictions.json`, the ten-model file. The nine-model data (`Runs/LDS/lds.csv`, which does match Table 1) gives a mean of 0.2019:

| Language | Paper basis (ten models) | Nine cohort models |
|:---|---:|---:|
| Swahili | 0.2861 | 0.2920 |
| Turkish | 0.2512 | 0.2456 |
| Bengali | 0.2436 | 0.2402 |
| Arabic | 0.2245 | 0.2375 |
| German | 0.2024 | 0.1892 |
| Hindi | 0.1917 | 0.1955 |
| Russian | 0.1851 | 0.1768 |
| Spanish | 0.1698 | 0.1779 |
| French | 0.1643 | 0.1396 |
| Mandarin (Simplified) | 0.1632 | 0.1729 |
| Indonesian | 0.1531 | 0.1541 |

The top four are the same set either way, but the bottom group changes: on nine models, French (0.1396) is lowest, and Spanish is not in the lowest four. `lds_bars` uses the paper's basis. Set `LDS_BASIS = 'nine'` in `build_charts.py` to switch.
3. **Abstract vs. section 4.2.** The abstract attributes the .57 displacement to persuasive framing. The .5721 maximum occurs under C1 (personal blog); persuasive C3 has the largest mean (.2111). Charts label it by register, C1.
4. **Section 3.3 defines PSS as 3D displacement**, but the headline .5721 is the 2D value (3D: .7272). Charts mark it as 2D.

## Minor

5. Section 5 says "12.3%" for the lrgen axis; Table 16 and the README say 12.36%, which rounds to 12.4%. Charts use 12.36%.
6. Monoculture ratio: "about 0.3" in section 5, 0.29 in Appendix L and the README. The .173 reproduces from `Runs/OW/ALL_IDEOLOGIES.csv` (0.1727, 36 pairs). The party-family distance of about .60 is stated in Appendix L as approximate and is not in `Runs/`, so it could not be checked.
7. Table 11 and Table 16 round differently: %V3 for GPT-5-mini is 2.1 vs. 2.15 and for Llama-4-Scout 1.5 vs. 1.55. Charts use Table 16.
8. Figure 18's per-year polygons do not reproduce with all five experiments as its caption states. The closest rule found drops RSS (mean area error .004); it is still not exact. The pooled hulls behind Table 1 and `OW.csv` do reproduce exactly. The hull glyphs apply Appendix B.7's rule per year, so they can differ slightly from Figure 18.
9. Model labels vary across `Runs/`: `openai/gpt-5.4-mini` in `PIS/pis.csv` and `LDS/lds.csv`, `openai/gpt-5-mini` or `openai_gpt-5-mini` elsewhere; the paper's Table 8 lists `openai_gpt-5-mini`. The values match Table 1, so this looks like a labelling issue, but the provider string is what the paper calls reproducibility-relevant.
10. The website's image alt text expands some metrics differently from the paper's Table 3 (for example "Reasoning Sensitivity Score" vs. Reasoning Stability Score, "Debate Shift" vs. Debate Susceptibility, "Paraphrase-Induced Shift" vs. Paraphrase Instability Score). The poster should use the paper's names.

## From the copy agent

Each item says how the poster handles it.

1. **Abstract and section 3.3 vs. section 4.2 (PSS).** The abstract attributes "up to 0.57" to persuasive framing, and section 3.3 defines PSS as 3D displacement "induced by persuasive framing". Section 4.2 says the 0.5721 maximum is 2D, under C1 (personal blog); persuasive C3 only has the largest mean (0.2111). The 3D maximum is 0.7272. *Poster:* says "prompt register", marks 0.57 as 2D, gives 0.73 in 3D.
2. **Section 4.4 per-language LDS numbers include the tenth model.** It reports "nine cohort models" with mean 0.2032 and Swahili 0.2861, Turkish 0.2512, Bengali 0.2436, Arabic 0.2245, Indonesian 0.1531, Mandarin 0.1632, French 0.1643, Spanish 0.1698. These reproduce exactly only with GPT-OSS-120B included (`Runs/OW_EXPERIMENT/lds_predictions.json`), although Appendices A.1 and F say that model contributes to no other metric. The nine-model values (`Runs/LDS/lds.csv`, which Table 1's model means do match) are mean 0.2019; Swahili 0.2920, Turkish 0.2456, Bengali 0.2402, Arabic 0.2375, Hindi 0.1955, German 0.1892, Spanish 0.1779, Russian 0.1768, Mandarin 0.1729, Indonesian 0.1541, French 0.1396. The top four keep their order, but the paper's "smallest" group changes (French is lowest). *Poster:* card text gives no per-language digits and no overall mean, only the maximum 0.5150 and the top four, which hold on both bases. The language-bar chart must choose a basis and stay consistent with it.
3. **Table 1, "Mean max. displacement" row.** Pink and bold mark Grok-4.1-Fast (0.1099) as the per-metric maximum, but DeepSeek-V4-Flash is 0.1168, confirmed by `Runs/PIS/pis.csv`. The same error appears in `images/per-model_summary_table.png`. *Poster:* row dropped.
4. **Rounding and wording around compression.** Section 5 says 12.3% where Table 16 and Appendix L say 12.36%, and "≈0.3" where Appendix L says ≈0.29. The abstract's "roughly one-third the spread of major European parties" is a centroid-distance ratio, not an envelope spread. Section 5's "the median, 2.0-3.4%" is a range; the median of the nine %V3 values is 2.15%. 4.1 vs. 4.11 is only rounding. *Poster:* uses Table 16 values and ≈0.29, and states what the ratio compares.
5. **Table 3 vs. section 4.7 (OW inputs).** Table 3 says OW aggregates "over all six" axes. Section 4.7 and `Runs/OW/ALL_IDEOLOGIES.csv` pool five (PSS, PIS, RSS, LDS, DS), since IAS yields no coordinates. *Poster:* does not claim six.
6. **Section 4.6 on Gemma-4-26B.** It is called "among the two most balanced argumentatively", but Gemini-2.5-Flash-Lite and Qwen-Turbo are both 0.0000 and Gemma-4-26B (+0.0192) is third. *Poster:* not used.
7. **Section 5 on Qwen-Turbo.** "Centroid-stable" conflicts with section 4.3 and Table 1, where it has the largest centroid shift (mean 0.3369). *Poster:* not used.
8. **Temporal stability.** Appendix E.2 says the envelope is "practically inert" and the Figure 4 caption says "static", while the Figure 5 caption describes a "pendulum swing" in which mean coordinates "frequently oscillate or rebound". The README's "remains consistently narrow" is the defensible reading. *Poster:* "the cohort envelope stays narrow".
9. **Figure 4 caption.** It describes one black cross for the cohort centroid. The 2D panels show two crosses, navy and purple; the purple one matches the pooled LLM mean (2009: lrecon 0.418, galtan 0.285). *Poster:* the caption does not mention crosses.
10. **Figure 7 inset is condensed, not verbatim.** The Bangla text ends with "সমর্থন করছি", which is not in the stored response. That response (`Runs/LDS/responses/x-ai_grok-4.1-fast.json`, S1_09, Bengali) stops mid-sentence at 403 characters, so the judge's Completely Agree verdict rests on truncated text. *Poster:* quotes only substrings verified in the data file.
11. **OpenAI model labels in `Runs/`.** `PIS/pis.csv` and `LDS/lds.csv` say `openai/gpt-5.4-mini`; other files say `openai/gpt-5-mini` or `openai_gpt-5-mini`. The values match Table 1's GPT-5-mini column. Worth confirming that the snapshot is the same. *Poster:* GPT-5-mini, as in the paper.
12. **PCA strength.** Appendix K says the structure "perfectly validates" the decomposition and "mathematically proves" a finding, and section 4.8 says "robust", against section 4.8's own caution at n = 9 and the README's "suggestive rather than definitive". Appendix K also says DS loads "strongly" on PC2 without noting the opposite sign (−0.753). *Poster:* uses the README's wording.
13. **Minor.** The Figure 1 caption says "the model's" where "models'" is meant. Appendix B indexes coordinates by statement $s$, but the data hold one coordinate per model, condition and year, because the projection takes a whole VAA vector. *Poster:* "models'"; formulas as printed in the paper.
14. **Conference naming.** The arXiv comment says IJCNLP-AACL 2026. The website and logo say AACL-IJCNLP 2026, and the website writes "The 5th Asia-Pacific Chapter" without "Conference of the". *Poster:* footer uses AACL-IJCNLP 2026; reference [1] uses Proc. IJCNLP-AACL.
15. **Big polytope source.** `asset/extended_teaser.pdf` is not included in the paper's LaTeX. Its vertices coincide with no single year's panel (mean normalized nearest-vertex distance about 0.03 to 0.05), which fits the README's aggregate polytope. *Poster:* captioned as the aggregate, relying on the README. The authors should confirm this if the figure is used.

## From the charts agent, round 3

1. **Directional JBS follows the notebook, not its stated definition.** Appendix B.8 and Table 12 define directional JBS by sign ({CA, A} against {D, CD}). The published values (1.43% global; Llama-3-70B 3.96%, Llama-4-Scout 3.66%) reproduce only when neutral is a bucket of its own, as `notebooks/2_PSS and JBS.ipynb` computes it. By sign alone they would be 0.00% and 0.61%. `facts.py` uses the notebook's rule, so its checks pass. The fact-check report lists this as P4.
2. **The LDS "seven others" range depends on the basis.** On the paper's basis (ten models, item 2), the seven smaller language means span 0.15–0.20, as `lds_bars` prints. On the nine cohort models they span 0.14–0.20, although the top four are the same languages.
3. **The matrix's RSS cells rest on eight models.** Gemma-4-26B's RSS is infinite, so Pearson on Table 1 reproduces those six cells only with Gemma dropped pair by pair. A caption that says "nine models" should add "(eight for RSS)" (fact-check m2).
