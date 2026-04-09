# Thesis: Generative AI as a Task Shock
## TUM Master's Thesis — Supervisor: Prof. Dr. Helmut Farbmacher

---

## Research Question
Do B2B software firms with more LLM-replicable products experience
lower revenue growth after the ChatGPT shock (2022Q4)?

## PRIMARY RESULT
β = -0.604, WCB p = 0.003*** (SME <$200M, Literature Rubric)
β = -0.541, WCB p = 0.002*** (SME <$500M, Literature Rubric)

## Identification Strategy
DiD: Y_it = α_i + δ_t + β(Post_t × ρ_i^lit) + ε_it
- Firm FE + Year-Quarter FE
- Wild Cluster Bootstrap (null imposed, B=999)
- Post = 1 after 2022Q4

---

## Treatment Variable: Literature Rubric Score

### Method
LLM-as-Judge with structured rubric from:
1. Eloundou et al. (2024) — E1/E0 criteria
2. Acemoglu & Restrepo (2022) — automation theory
3. Brynjolfsson et al. (2023) — LLM suitability

Scale: 1-100 continuous
  1-20:  Pure E0 (infrastructure, hardware, security)
  21-40: Mostly E0 (deep integration, proprietary data)
  41-60: Mixed
  61-80: Mostly E1 (text, documents, classification)
  81-100: Pure E1 (core entirely text/knowledge)

Input: 10-K Item 1 Business Description (~3000 chars, pre-shock)
Output: lit_score (1-100) + reasoning citation

File: data/processed/lit_continuous_scores.csv
  N scored: 116 firms (94 SME $200M + 22 in $200M-$500M)

---

## Sample
- Full universe: 143 B2B software firms (SIC 7370-7379)
- PRIMARY: SME <$200M → 94 firms with lit_score
- ROBUSTNESS: SME <$500M → 116 firms with lit_score
- Panel: 2020Q1 — 2025Q4

---

## Key Results

### Table 1 — Primary
Lit Rubric SME $200M: β=-0.604, SE=0.217, WCB p=0.003***
Lit Rubric SME $500M: β=-0.541, SE=0.202, WCB p=0.002***

### Table 2 — Robustness (Panels A–G)
Panel A LLM Judge (SME $200M):      β=-0.426, WCB p=0.031**  r=0.895
Panel B Quartile Q75/Q25:           β=-0.286, WCB p=0.005***
Panel C Placebo GM:                 β=-0.165, WCB p=0.661
Panel D SGA control (OVB check):    β=-0.476, WCB p=0.018**
Panel E Infra exclusion (n=88):     β=-0.475, WCB p=0.043**
Panel F Segment×Time FE:            β=-0.778, WCB p=0.000*** (absorbs sub-industry trends)
Panel G Continuous infra control:    β=-0.697, WCB p=0.008*** (infra proximity insignificant)

### Identification
Placebo: p=0.157 ✅
Pre-trends: 0/11 sig ✅
Size het: Full(-0.541) → $300M(-0.591) → $200M(-0.604) ✅
GM null: p>0.4 across all specs ✅ (quantity, not pricing)

---

## Key Files
data/processed/
master_panel.csv              — 143 firms, 2020-2025
lit_continuous_scores.csv     — PRIMARY treatment (116 firms)
llm_judge_scores.csv          — Holistic LLM Judge scores
segment_classification.csv    — Product segment classification (116 firms, 6 segments)
event_study_coefs.csv         — Event study coefficients
literature_rubric.json        — Rubric definition (10 criteria)
analysis/
did_main.R                    — PRIMARY DiD script (incl. Segment FE + Infra proximity)
segment_classification.py     — Segment classifier (keyword-based or Claude API)
thesis_notebook.ipynb         — Python figures (Sections 0-14)
figures/
fig1_score_distribution.png   — Literature rubric distribution
fig2_construct_validity.png   — r=0.895 (LLM Judge holistic, single panel)
fig3_event_study.png          — Pre-trends test
fig4_revenue_divergence.png   — HIGH vs LOW revenue
fig5_size_heterogeneity.png   — Monotonic size effect
fig12_two_sided_reallocation.png — 3-group revenue trajectories (infra robustness)
fig13_segment_validation.png  — Product category validation (mean score by segment)
thesis.tex                      — LaTeX manuscript

---

## Scoring Notes
- Literature rubric scored with claude-opus-4-5
- 4 firms failed JSON parsing (DOMO, UPLD, VERI, TBRG) — excluded
- API key required: export ANTHROPIC_API_KEY="sk-ant-..."
- Rubric saved: data/processed/literature_rubric.json

## Status
- [x] Firm universe (143 firms)
- [x] Panel data (Compustat/SEC EDGAR)
- [x] Literature rubric designed + scored (116 firms)
- [x] DiD estimation (primary + robustness)
- [x] Placebo + event study
- [x] Figures (5 figures)
- [x] thesis.tex (complete draft)
- [x] Three-period analysis (Early vs Advanced AI) → 1.52x intensification
- [x] Infrastructure robustness (Panel E, β=-0.475, p=0.043)
- [x] Mechanism outcomes (Table 3: GM null, R&D↑)
- [x] Appendix (A.1 descriptive, A.2 figures, A.3 tables)
- [x] fig10 (mechanism), fig11 (SGA het), fig12 (two-sided reallocation)
- [x] Segment classification (6 segments, 116 firms)
- [x] Segment×Time FE robustness (Panel F, β=-0.778, p=0.000)
- [x] Continuous infra proximity control (Panel G, β=-0.697, p=0.008)
- [x] Product category validation (fig13, Section 14)
- [ ] Overleaf sync (fig10-13) + TUM format (cover page, Eigenständigkeitserklärung)
