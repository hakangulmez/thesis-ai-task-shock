# Generative AI as a Task Shock

**Replicability, Commodification, and Firm Performance in the Software Industry**

Author: Hakan Zeki Gulmez — M.Sc. Management and Technology, TUM
Supervisor: Prof. Dr. Helmut Farbmacher

---

## Research Question

Do B2B software firms (SIC 7370-7379) experience heterogeneous financial outcomes after the ChatGPT shock (November 2022), determined by the task replicability of their core product?

## Empirical Design

Difference-in-Differences with continuous treatment intensity:

```
Y_it = alpha_i + delta_t + beta(Post_t x Replicability_i) + epsilon_it
```

- **Post_t** = 1 if quarter >= 2022 Q4 (ChatGPT launch)
- **Replicability_i** = SBERT semantic similarity score (pre-shock text only)
- Firm FE + Quarter FE + clustered SE at firm level
- Wild cluster bootstrap inference (B = 9,999)

## Sample

- 143 B2B software firms (SIC 7370-7379)
- NYSE/Nasdaq listed, IPO before 2020 Q1
- Quarterly financial data: 2020 Q1 - 2025 Q4 (trimmed)
- 2,585 firm-quarter observations (trimmed sample)

## Treatment Variables

Two SBERT-based scores constructed from pre-November 2022 product text:

| Variable | Construction | Captures |
|----------|-------------|----------|
| `replicability_score` | Mean top-10 similarity to 18 high-replicability anchor sentences | Absolute LLM task exposure |
| `contrast_score` | high_score minus low_score (10 infrastructure anchors) | Relative replicability vs. infrastructure |

Correlation between the two: r = 0.35.

## Main Results

### Mechanism 1 — Substitution (revenue decline)

Treatment: `replicability_score` | Sample: Wayback-only (106 firms), 2020+

| Outcome | Beta | SE | Conventional p | Bootstrap p |
|---------|:----:|:--:|:--------------:|:-----------:|
| **ln(Revenue)** | **-1.051** | 0.427 | **0.016** | **0.018** |
| Gross Margin | +0.038 | 0.101 | 0.705 | — |
| Operating Margin | -0.282 | 0.359 | 0.434 | — |

Firms with higher task replicability experienced significantly lower revenue growth after the ChatGPT shock.

### Mechanism 2 — Commodification (margin compression)

Treatment: `contrast_score` | Sample: Wayback-only (106 firms), 2020+

| Outcome | Beta | SE | Conventional p | Bootstrap p |
|---------|:----:|:--:|:--------------:|:-----------:|
| ln(Revenue) | -0.315 | 0.485 | 0.518 | — |
| **Gross Margin** | **-0.114** | 0.060 | **0.060** | **0.047** |
| Operating Margin | +0.064 | 0.264 | 0.810 | — |

Firms with higher relative replicability (vs. infrastructure tasks) experienced significant gross margin compression, consistent with pricing power erosion.

### Parallel Trends

All pre-tests pass (Wald joint F-test, H0: pre-period coefficients jointly zero):

| Treatment | ln(Revenue) | Gross Margin | Operating Margin |
|-----------|:-----------:|:------------:|:----------------:|
| high_score | F=0.89, p=0.54 | F=0.98, p=0.46 | F=1.00, p=0.44 |
| contrast_score | F=0.92, p=0.52 | F=0.65, p=0.77 | F=1.20, p=0.29 |

## Project Structure

```
thesis-ai-task-shock/
  scripts/                    # Data pipeline
    build_firm_universe.py    # SEC EDGAR firm list
    get_sic_codes.py          # SIC code lookup
    apply_filters.py          # Sample filters
    collect_financials.py     # XBRL financial data
    collect_product_text.py   # Wayback Machine text
    collect_10k_text.py       # 10-K business descriptions
    apply_10k_fallback.py     # 10-K fallback for missing text
    build_replicability.py    # SBERT scoring (high + low + contrast)
    build_master_panel.py     # Panel merge
  analysis/                   # R analysis scripts
    did_main.R                # Main DiD, event study, parallel trends
    did_contrast_comparison.R # Contrast score comparison
    wild_cluster_bootstrap.R  # WCR bootstrap inference
  data/
    raw/                      # SEC EDGAR downloads
    processed/                # Analysis-ready datasets
  notebooks/
    project_overview.ipynb    # Research notebook with EDA and results
  figures/                    # All generated figures
  results/                    # Regression tables
```

## Data Sources

| Source | Data | Access |
|--------|------|--------|
| SEC EDGAR XBRL API | Quarterly financials | Free, no auth |
| SEC EDGAR company_tickers_exchange.json | Firm universe | Free, no auth |
| Wayback Machine CDX API | Pre-shock product text | Free, no auth |
| SEC EDGAR filing archives | 10-K business descriptions | Free, no auth |

All treatment variables constructed from pre-November 2022 sources only.

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
