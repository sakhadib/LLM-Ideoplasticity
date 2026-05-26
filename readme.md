# LLM-Ideoplasticity

**Measuring Ideological Plasticity in the Political Behavior of LLMs as a Context-Conditioned Distribution**

[![Website](https://img.shields.io/badge/🌐_Project_Website-Visit-00B8D4?style=for-the-badge)](https://sakhadib.github.io/LLM-Ideoplasticity/)
[![arXiv](https://img.shields.io/badge/arXiv-coming_soon-B31B1B?style=for-the-badge&logo=arxiv&logoColor=white)](#)
[![License: CC-BY-SA-4.0](https://img.shields.io/badge/License-CC--BY--SA--4.0-C9B6FF?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10+-FFD6E0?style=for-the-badge&logo=python&logoColor=black)](#)


## TL;DR

An LLM's political ideology is **not a fixed point** but a *conditional distribution*  $\mathbb{P}(\text{position} \mid \text{context})$ over a real political space.

We project nine frontier LLMs into a shared **VAA → CHES** coordinate system and decompose context along six operationally distinct axes. Key findings:

- **Local plasticity is large.** Persuasive framing displaces coordinates by up to **0.57** units (PSS); under-represented languages by up to **0.52** units (LDS).
- **Reasoning is not a regulator.** Chain-of-thought *amplifies* paraphrase instability in **17 out of 27** model-year configurations.
- **Global breadth is small.** The nine-model cohort covers only ~**⅓** of the ideological diversity of major European parties — the empirical face of *algorithmic monoculture*.
- **The shape is real.** A multi-trait multi-method (MTMM) analysis confirms three latent factors (surface instability, contextual perturbation, argumentative asymmetry) explain **83.30%** of the variance.

The core methodological claim: a single point cannot summarize LLM political behavior; it must be characterized as a **shape**.



## Authors

Adib Sakhawat, Syed Rifat Raiyan, Tahsin Islam, Takia Farhin, Hasan Mahmud, Md Kamrul Hasan

*Systems and Software Lab (SSL), Department of Computer Science and Engineering*
*Islamic University of Technology, Dhaka, Bangladesh*

`{adibsakhawat, tahsinislam, takiafarhin, rifatraiyan, hasan, hasank}@iut-dhaka.edu`



## What this repository contains


| Metric | Axis | What it measures |
|:---:|:---:|:---|
| **PSS** | Register | Displacement under persuasive vs. neutral framing |
| **PIS** | Surface form | Dispersion across 10 semantic paraphrases |
| **RSS** | Reasoning | Ratio of CoT dispersion to direct dispersion |
| **LDS** | Language | Displacement target-language vs. English baseline |
| **DS** | Multi-turn debate | Net drift, path length, tortuosity, peak velocity |
| **IAS** | Argument role | Quality gap when arguing *for* vs. *against* |
| **OW** | Aggregate | Convex-hull volume / surface / spread of pooled coords |
| **JBS** | Evaluator | Strict + directional audit of the LLM judge |


All metrics share a single externally-validated coordinate system — bagged ElasticNet regressors trained on EU Profiler / euandi VAA data, mapped to the Chapel Hill Expert Survey dimensions `lrgen`, `lrecon`, `galtan` for 2009, 2014, and 2019.



## Models evaluated

Nine current LLMs spanning closed-frontier and open-weight systems, all generations at **temperature 0**:

| # | Model | Provider | Weight |
|:-:|:---|:---|:---:|
| 1 | `deepseek-v4-flash` | DeepSeek | — |
| 2 | `gemini-2.5-flash-lite` | Google | — |
| 3 | `gemma-4-26b-a4b-it` | Google | Open |
| 4 | `granite-3.3-8b-instruct` | IBM | Open |
| 5 | `meta-llama-3-70b-instruct` | Meta | Open |
| 6 | `llama-4-scout` | Meta | Open |
| 7 | `gpt-5-mini` | OpenAI | — |
| 8 | `qwen-turbo` | Alibaba | — |
| 9 | `grok-4.1-fast` | xAI | — |

Stance judge: `gemini-2.5-flash` (zero-shot), audited via JBS before any open-ended experiment — global directional JBS of **1.43%** confirms evaluator integrity.



## Repository layout

```
.
├── docs/                               # Project website (GitHub Pages)
│   ├── index.html                      # Static paper microsite
│   └── asset/                          # All figures and visualizations
│
├── notebooks/                          # End-to-end experimental pipeline
│   ├── 1_Models_Over_VAA_CHESS.ipynb   # Train year-specific VAA→CHES regressors
│   ├── 2_PSS and JBS.ipynb             # Prompt sensitivity + judge audit
│   ├── 3_PIS.ipynb                     # Paraphrase instability
│   ├── 4_RSS.ipynb                     # Chain-of-thought vs. direct elicitation
│   ├── 5_LDS.ipynb                     # 11-language displacement
│   ├── 6_DS.ipynb                      # 8-turn adversarial debate
│   └── 7_PS.ipynb                      # Argumentative symmetry + Overton geometry
│
└── Runs/                               # All materialized experimental artifacts
    ├── PSS/                            # Prompt sensitivity (4 framings × 9 models)
    ├── PIS/                            # Paraphrase instability (10 paraphrases)
    ├── RSS/                            # Reasoning-conditioned paraphrase
    ├── LDS/                            # Multilingual displacement (11 languages)
    ├── DS/                             # Debate trajectories (8 turns each)
    ├── PS/                             # Persona / argumentative-role scoring
    ├── OW/                             # Pooled Overton Width
    └── OW_EXPERIMENT/                  # Cached inputs for OW computation
```

Each subdirectory under `Runs/` contains both the raw LLM responses (`*.json`) and the processed coordinate / score CSVs used to build the paper's tables and figures. You can fully reproduce every result **without making a single API call** by running the analysis cells against these cached artifacts.



## Notebook execution order

Notebooks are numbered and order-dependent. Each maps to a specific section of the paper:

| # | Notebook | Paper section |
|:---:|:---|:---|
| 1 | `1_Models_Over_VAA_CHESS.ipynb` | §3.1, Appendix B (projection models) |
| 2 | `2_PSS and JBS.ipynb` | §4.1 (JBS), §4.2 (PSS) |
| 3 | `3_PIS.ipynb` | §4.3 (PIS) |
| 4 | `4_RSS.ipynb` | §4.3 (RSS) |
| 5 | `5_LDS.ipynb` | §4.4 (LDS) |
| 6 | `6_DS.ipynb` | §4.5 (DS) |
| 7 | `7_PS.ipynb` | §4.6 (IAS), §4.7 (OW) |



## Quickstart

```bash
git clone https://github.com/sakhadib/LLM-Ideoplasticity.git
cd LLM-Ideoplasticity

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

jupyter lab notebooks/
```

To rerun generations from scratch you will need API keys for the providers you want to query (OpenAI, Anthropic, Google, OpenRouter, etc.). Missing keys simply skip the affected models. Otherwise, every cell that does analysis or plotting works directly from the cached artifacts in `Runs/`.



## Conventions

- **VAA waves:** `2009`, `2014`, `2019` (82 statements total).
- **Statement IDs:** `S{n}_{YY}` — e.g. `S21_09` = statement 21 from the 2009 wave.
- **Stance scale:** 5-point Likert, mapped to ordinal `{1.00, 0.75, 0.50, 0.25, 0.00}` for projection.
- **Coordinate space:** $(\texttt{lrgen}, \texttt{lrecon}, \texttt{galtan})$, all rescaled to $[0, 1]$.
- **Decoding:** all generations at temperature 0 to isolate context-induced variance from sampling noise.



## Contributing / Carrying the research forward

This repository is designed to be a **modular framework**, not a fixed benchmark. The model cohort, the projection space, and the contextual axes are all swappable. Some natural extensions:

- **New cohort.** Drop additional model names into the elicitation loops in any numbered notebook — every downstream metric will recompute automatically from the cached projection pipeline.
- **New language.** Add a target locale to `Runs/LDS/prompts.json` and rerun `5_LDS.ipynb`.
- **New paraphrases.** Extend the `p1`–`p10` prefix list in `3_PIS.ipynb` / `4_RSS.ipynb` for finer-grained surface-form audits.
- **New projection space.** Swap CHES for a non-European ideological scheme — the rest of the pipeline is space-agnostic so long as the regressor outputs a bounded $\mathbb{R}^d$ vector.
- **Stochastic decoding.** We deliberately fix temperature at 0; jointly characterizing context-conditioned displacement and sampling noise is an open direction.
- **Pluralistic judging.** Replace the single `gemini-2.5-flash` judge with an ensemble to push directional JBS even lower.

Pull requests welcome. For substantive changes, please open an issue first so we can discuss scope.



## Citation

Once the arXiv preprint is live, the BibTeX entry below will be updated with the official identifier. For now:

```bibtex
@article{sakhawat2026ideoplasticity,
  title   = {LLM-Ideoplasticity: Measuring Ideological Plasticity in the Political Behavior
             of LLMs as a Context-Conditioned Distribution},
  author  = {Sakhawat, Adib and Raiyan, Syed Rifat and Islam, Tahsin
             and Farhin, Takia and Mahmud, Hasan and Hasan, Md Kamrul},
  year    = {2026},
  note    = {Preprint. arXiv link forthcoming.}
}
```



## Acknowledgements

This work builds directly on:

- The *spinning-arrow* critique of static LLM political-compass scores — [Röttger et al. (2024)](https://aclanthology.org/2024.acl-long.816), [Ceron et al. (2024)](https://aclanthology.org/2024.tacl-1.76).
- Earlier static-instrument audits — [Hartmann et al. (2023)](https://arxiv.org/abs/2301.01768), [Rozado (2024)](https://doi.org/10.1371/journal.pone.0306621), [Motoki et al. (2024)](https://doi.org/10.1007/s11127-023-01097-2), [Feng et al. (2023)](https://aclanthology.org/2023.acl-long.656/).
- Reliability literature for LLM-as-a-judge — [Zheng et al. (2023)](https://arxiv.org/abs/2306.05685), [Zheng et al. (2024)](https://openreview.net/forum?id=shr9PXz7T0), [Pezeshkpour & Hruschka (2024)](https://aclanthology.org/2024.findings-naacl.130/), [Shi et al. (2025)](https://arxiv.org/abs/2406.07791), [Bavaresco et al. (2025)](https://aclanthology.org/2025.acl-short.20/).
- The reference data infrastructure — EU Profiler / euandi VAAs ([Reiljan et al., 2020](https://doi.org/10.1016/j.dib.2020.105968); [Trechsel & Mair, 2011](https://doi.org/10.1080/19331681.2010.531585)) and the Chapel Hill Expert Survey ([Jolly et al., 2022](https://doi.org/10.1016/j.electstud.2021.102420); [Bakker et al., 2020](https://doi.org/10.1080/13501763.2019.1582540); [Rovny et al., 2025](https://www.sciencedirect.com/science/article/pii/S2666675825004564)).



## License

Released under the Creative Commons Attribution-ShareAlike 4.0 International License. See [`LICENSE`](LICENSE) for details.



*The framework, not the cohort-specific numbers, is what we offer: an evaluation protocol that **measures** ideology where prior work could only **label** it.*