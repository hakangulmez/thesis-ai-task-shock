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
figures/                      — all plots
results/                      — regression tables
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
- Main DiD estimation
- Wild cluster bootstrap inference
- Parallel trends validation

Remaining:
- Event study plots
- Heterogeneity analysis
- Robustness checks
- Thesis writing
