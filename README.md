# Generative AI as a Task Shock
### Product-Level LLM Substitution in B2B Software Markets

**Master's Thesis** | TU Munich School of Management  
**Supervisor:** Prof. Dr. Helmut Farbmacher  
**Author:** Hakan Zeki Gülmez

---

## Research Question

Do B2B software firms whose products are more replicable by large language models experience lower revenue growth after the ChatGPT shock (2022Q4)?

## Key Finding

> *"The primary economic impact of generative AI operates not only through labor markets, but through product markets, as general-purpose systems substitute for the software products that previously automated those tasks."*

| Specification | N | β | WCB p |
|---|---|---|---|
| **Lit Rubric SME <$200M (primary)** | **94** | **−0.604** | **0.003\*\*\*** |
| Lit Rubric SME <$500M | 116 | −0.541 | 0.002\*\*\* |
| LLM Judge holistic | 98 | −0.426 | 0.031\*\* |
| R&D intensity (alt outcome) | 88 | +0.080 | 0.018\*\* |
| Quartile Q75/Q25 | 65 | −0.286 | 0.005\*\*\* |
| Placebo GM treatment | 86 | −0.165 | 0.661 |
| Early AI era (2022Q4–2023Q4) | 94 | −0.451 | 0.022\*\* |
| Advanced AI era (2024Q1+) | 94 | −0.686 | 0.008\*\*\* |

---

## Conceptual Contribution

**Product-level vs worker-level exposure:**  
Prior literature (Eloundou 2024, Labaschin 2025) measures how AI affects workers *within* firms. This paper measures how AI affects the *products firms sell* — a firm can benefit from AI internally while facing demand contraction externally.

**Second-order displacement:**  
AI displacing software products that had themselves displaced workers from cognitive tasks (1990s–2000s). B2B software firms are *task externalizers*: they build subscription businesses performing cognitive tasks that customers outsource. When LLMs perform those tasks at near-zero cost, the externalizer faces product obsolescence.

---

## Pipeline
scripts/collect_10k_text.py     → text_data/10k_extracts/
scripts/score_rubric_*.py       → (scoring via API, see thesis_notebook.ipynb Section 2)
analysis/did_main.R             → DiD estimates (Table 1–3, 6)
analysis/thesis_notebook.ipynb  → All figures (Fig 1–9) + Table 4–5

### Full notebook pipeline (12 sections):
| Section | Content | Output |
|---|---|---|
| 0 | Setup & data loading | — |
| 1 | Sample construction | Funnel stats |
| 2 | Literature rubric scoring | Score examples |
| 3 | Score distribution & validation | Fig 1, Fig 2 |
| 4 | DiD results summary | Table 1, 2 |
| 5 | Event study & placebo | Fig 3 |
| 6 | Revenue divergence | Fig 4 |
| 7 | Firm-level evidence | Table 5, Fig 8 |
| 8 | Size heterogeneity | Table 3, Fig 5 |
| 9 | Scoring pipeline & funnel | Fig 6, Fig 7 |
| 10 | Three-period analysis | Table 6, Fig 9 |
| 11 | Results summary | All results |
| 12 | Mechanism & SG&A heterogeneity | Fig 10, Fig 11 |

---

## Treatment Variable: Literature-Grounded Replicability Score

Scored via LLM-as-judge using a structured rubric from:
- **Eloundou et al. (2024)** — E1/E0 task classification
- **Acemoglu & Restrepo (2022)** — automation feasibility criteria  
- **Brynjolfsson et al. (2023)** — LLM suitability framework

| Scale | Description | Examples |
|---|---|---|
| 1–20 | Pure E0: infrastructure, hardware, security | DDOG (18), ZS (15), NET (18) |
| 21–40 | Mostly E0: deep integration, proprietary data | TTD (32), CRWD (28) |
| 41–60 | Mixed | PAYC (52), HUBS (72→) |
| 61–80 | Mostly E1: text, documents, classification | LPSN (72), YEXT (78) |
| 81–100 | Pure E1: core text/knowledge | ZIP (82) |

**Construct validity:** r=0.895 with LLM Judge holistic

---

## Identification

| Check | Result |
|---|---|
| Pre-period placebo | p=0.157 ✅ |
| Event study pre-trends | 0/11 quarters significant ✅ |
| Gross margin effect | p>0.4 (quantity channel confirmed) ✅ |
| Placebo treatment (GM) | p=0.661 (LLM-specificity confirmed) ✅ |
| R&D intensity response | β=+0.080, p=0.018** (defensive R&D) ✅ |
| Pre-shock SG&A control | β attenuates ~21% to −0.476** (p=0.018), OVB limited ✅ |
| Firm-level scatter | r=−0.274, p=0.008 ✅ |
| Size heterogeneity | Monotonic strengthening ✅ |
| SG&A heterogeneity | Substitution concentrated in low-SG&A high-rep firms ✅ |

---

## Key Files
```
thesis-ai-task-shock/
├── analysis/
│   ├── did_main.R                  Primary DiD + robustness + three-period
│   └── thesis_notebook.ipynb       12 sections, 11 figures (fig2 updated, fig10-11 added)
├── data/processed/
│   ├── master_panel.csv            143 firms, 2020Q1–2025Q4
│   ├── lit_continuous_scores.csv   Literature rubric scores (116 firms)
│   ├── llm_judge_scores.csv        Holistic LLM Judge scores (143 firms)
│   ├── event_study_coefs.csv       Quarter-by-quarter event study
│   └── literature_rubric.json      10-criterion rubric definition
├── figures/
│   ├── fig1_score_distribution.png Score distribution + top/bottom firms
│   ├── fig2_construct_validity.png r=0.895 (LLM Judge holistic)
│   ├── fig3_event_study.png        Pre-trends: 0/11 significant
│   ├── fig4_revenue_divergence.png HIGH vs LOW revenue trajectories
│   ├── fig4b_quartile_divergence.png Q75 vs Q25 revenue divergence
│   ├── fig5_size_heterogeneity.png Monotonic effect by firm size
│   ├── fig6_scoring_pipeline.png   10-K → rubric → score pipeline
│   ├── fig7_sample_funnel.png      7509 → 94 firms
│   ├── fig8_score_revenue_scatter.png r=−0.274, p=0.008
│   ├── fig9_three_period.png       1.52x intensification
│   ├── fig10_mechanism_outcomes.png DiD betas by outcome variable
│   └── fig11_sga_heterogeneity.png SG&A moderation within high-rep
├── scripts/
│   └── collect_10k_text.py         SEC EDGAR 10-K scraper
└── README.md
```

---

## Setup
```bash
# R packages
install.packages(c("fixest", "dplyr"))

# Python packages
pip install pandas numpy matplotlib scipy anthropic

# Scoring (requires API key)
export ANTHROPIC_API_KEY="sk-ant-..."
python3 -c "# See thesis_notebook.ipynb Section 2 for scoring pipeline" 
```

---

## References

| Paper | Role |
|---|---|
| Eloundou et al. (2024) *Science* | E1/E0 rubric basis |
| Acemoglu & Restrepo (2022) *Econometrica* | Automation theory |
| Brynjolfsson et al. (2023) *NBER* | LLM suitability criteria |
| Babina et al. (2024) *JFE* | AI & firm performance |
| Farrell & Klemperer (2007) *HIO* | Switching cost theory |
| Cameron et al. (2008) *REStat* | Wild cluster bootstrap |

## Robustness Structure

| Panel | Test | β | p |
|---|---|---|---|
| A | LLM Judge holistic (alt treatment) | −0.426 | 0.031\*\* |
| B | Quartile Q75/Q25 (binary) | −0.286 | 0.005\*\*\* |
| C | Placebo GM treatment (specificity) | −0.165 | 0.661 |
| D | Pre-shock SG&A control (OVB check) | −0.476 | 0.018\*\* |

## License
Code: MIT License © 2026 Hakan Zeki Gülmez  
Methodology and framework (TCDC): CC BY 4.0 — please cite as: Gülmez, H.Z. (2026). Generative AI as a Task Shock. M.Sc. Thesis, TU Munich.
