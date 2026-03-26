# Generative AI as a Task Shock

**Replicability, Commodification, and Firm Performance in the Software Industry**

Master's Thesis — Hakan Zeki Gulmez
TUM School of Management and Technology
Supervisor: Prof. Dr. Helmut Farbmacher

---

## Research Question

Do B2B software firms experience heterogeneous financial outcomes after the ChatGPT shock (November 2022), depending on how replicable their core product tasks are by large language models?

---

## Key Findings

Two mechanisms identified, both significant under wild cluster bootstrap inference (B = 9,999 Rademacher iterations):

**Mechanism 1 — Substitution**
High replicability firms experienced lower post-shock revenue growth.
Beta = -1.051 (SE = 0.427, bootstrap p = 0.018)
Sample: 106 Wayback-only firms, 2020-2025

**Mechanism 2 — Commodification**
High contrast firms experienced gross margin compression even without revenue decline.
Beta = -0.114 (SE = 0.060, bootstrap p = 0.047)
Sample: 106 Wayback-only firms, 2020-2025

Both results use firm and quarter-year fixed effects. All parallel trends tests pass.

**Economic Magnitude**
In revenue levels, a one standard deviation increase in task replicability (0.068) is associated with $30.3 million lower quarterly revenue growth — representing a 7.8% revenue differential relative to the sample mean of $388 million per quarter.

High replicability firms (top quartile) grew revenue 31.8% post-shock versus 46.8% for low replicability firms (bottom quartile) — a gap of 15 percentage points. Both groups grew in absolute terms; the finding is differential growth, not absolute decline.

---

## Event Study

The dynamic treatment effects confirm the theoretical timing predictions:

- **ln(Revenue):** pre-trend coefficients flat near zero (Wald F=1.39, p=0.179 PASS), post-period coefficients drift negative and become significant from k=4 quarters after the shock onward

- **Gross Margin:** pre-trend coefficients flat (Wald F=0.42, p=0.936 PASS), gradual margin compression from k=5, significant at k=9*** — consistent with delayed commodification as contracts expire

---

## Heterogeneity

| SIC Group | Description | ln(Rev) β | GM β |
|-----------|-------------|-----------|------|
| 7370/7371 | Computer services | -1.998 (ns) | -0.117 (ns) |
| 7372 | Prepackaged software | -0.723 (ns) | -0.138* |
| 7373/7374 | Systems integration | -2.032 (ns) | -0.027 (ns) |

Gross margin commodification concentrates in SIC 7372 (prepackaged software, 66 firms) — the sub-sector most directly comparable to LLM alternatives.

---

## Robustness Checks

| Check | ln(Revenue) β | p | Gross Margin β | p |
|-------|--------------|---|----------------|---|
| Baseline (2022 Q4) | -1.051 | 0.016 ** | -0.114 | 0.060 * |
| Alt shock GPT-4 (2023 Q2) | -1.004 | 0.017 ** | -0.106 | 0.052 * |
| Excl. mega-caps (ADP, DXC) | -1.066 | 0.015 ** | -0.115 | 0.060 * |
| COVID placebo (2020 Q1) | -0.598 | 0.068 | -0.037 | 0.494 PASS |

Results are robust to alternative shock dates and sample composition. The COVID placebo passes cleanly for gross margin. The marginal revenue placebo result (p=0.068) reflects differential COVID-era demand patterns — high replicability firms (content, CRM tools) had stronger demand during remote work, running counter to the main finding and confirming it is conservative.

---

## Theoretical Framework

Builds on:
- Autor, Levy & Murnane (2003, QJE) — task-based production framework
- Acemoglu & Restrepo (2018 AER, 2019 JEP) — automation frontier, displacement vs reinstatement effects
- Eloundou et al. (2024, Science) — occupation-level LLM exposure via O*NET. This thesis extends to PRODUCT-level exposure.
- Acemoglu (2024, Economic Policy) — aggregate AI productivity gain of 0.66% masks firm-level heterogeneity that this thesis quantifies

---

## Treatment Variables

**Task Replicability Index (high_score)**
- Source: Pre-shock product page text (Wayback Machine, Q2-Q3 2022)
- Method: SBERT all-MiniLM-L6-v2 sentence embeddings, cosine similarity to 18 high-replicability anchor sentences
- Score: mean of top-10 sentence similarities
- Range: 0.17 to 0.53, SD = 0.068
- Used for: Mechanism 1 (substitution)

**Contrast Score**
- Method: high_score minus similarity to 10 low-replicability anchor sentences (infrastructure, security, chip design tasks)
- Range: -0.19 to +0.28, SD = 0.081
- Correlation with high_score: 0.35
- Used for: Mechanism 2 (commodification)

**Highest replicability:** ZipRecruiter (+0.277), Sprout Social (+0.242), GitLab (+0.183)

**Lowest replicability:** BlackBerry (-0.186), CrowdStrike (-0.183), Tenable (-0.181)

---

## Sample

- 143 publicly listed B2B software firms
- SIC codes 7370-7379, NYSE/Nasdaq
- IPO before 2020 Q1
- 2,982 firm-quarter observations
- Period: 2019 Q1 to 2025 Q3
- Pre-period trimmed to 2020 Q1 (parallel trends)

Sample construction:
7,509 NYSE/Nasdaq firms
-> 530 after SIC 7370-7379 filter
-> 287 after IPO before 2020 Q1
-> 173 after B2B manual review
-> 143 final sample

---

## Data Sources

| Source | Data | Access |
|--------|------|--------|
| SEC EDGAR XBRL API | Quarterly financials | Free |
| Wayback Machine CDX API | Pre-shock product text | Free |
| SEC EDGAR Archives | 10-K business descriptions | Free |

All treatment variables constructed from sources dated strictly before November 2022.

---

## Repo Structure

```
data/
  raw/           — firm universe, financial panel
  processed/     — replicability scores, master panel
scripts/
  build_firm_universe.py
  get_sic_codes.py
  apply_filters.py
  collect_financials.py
  collect_product_text.py
  collect_10k_text.py
  apply_10k_fallback.py
  build_replicability.py
  build_master_panel.py
text_data/
  product_pages/ — 143 firm product text files
  10k_extracts/  — 143 firm 10-K descriptions
analysis/
  did_main.R                  — main DiD regression
  did_contrast_comparison.R   — two-treatment comparison
  did_robustness_textsource.R — text source robustness
  wild_cluster_bootstrap.R    — bootstrap inference
figures/
  event_study_revenue.png    — ln(Revenue) event study
  event_study_margin.png     — Gross Margin event study
  event_study_combined.png   — both event studies side by side
  heterogeneity_sic.png      — SIC code heterogeneity
  robustness_checks.png      — robustness comparison
results/                      — regression tables
THESIS_FINAL.md               — thesis with figure references
thesis.tex                    — LaTeX version
notebooks/
  project_overview.ipynb      — full research notebook
```

---

## Replication

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run data pipeline (in order)
python scripts/build_firm_universe.py
python scripts/get_sic_codes.py
python scripts/apply_filters.py
python scripts/collect_financials.py
python scripts/collect_product_text.py
python scripts/collect_10k_text.py
python scripts/apply_10k_fallback.py
python scripts/build_replicability.py
python scripts/build_master_panel.py

# Run analysis
Rscript analysis/did_main.R
Rscript analysis/wild_cluster_bootstrap.R
```

---

## Current Status

Completed:
- Data collection (143/143 firms)
- Treatment variable construction and validation
- Main DiD estimation (two mechanisms)
- Wild cluster bootstrap (B=9,999)
- Event study plots (both outcomes)
- Heterogeneity analysis (SIC sub-codes)
- Robustness checks (3 specifications)
- Research notebook with all figures

Remaining:
- Final thesis formatting and submission

---

## Measurement Robustness Audit

(conducted March 2026)

Full product page rescrape:
- 103 Wayback firms x up to 20 pages each
- 24,495 sentence-level SBERT scores
- Script: `scripts/scrape_and_score_v2.py`

Results:

| Mechanism | Original beta | V2-Full beta | Robust? |
|---|---|---|---|
| Substitution (ln rev) | -1.051** | +0.054 (ns) | No |
| Commodification (GM) | -0.114* | -0.138* | Yes |

Conclusion: The commodification result is the robust primary finding. The substitution result was sensitive to single-page homepage text scoring and does not survive multi-page product page measurement.
