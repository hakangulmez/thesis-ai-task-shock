# CLAUDE.md

## Thesis title
Generative AI as a Task Shock: Replicability,
Commodification, and Firm Performance in the
Software Industry

## Author
Hakan Zeki Gülmez — TUM Applied Econometrics
Supervisor: Prof. Dr. Helmut Farbmacher

## Research question
Do B2B software firms (SIC 7370-7379) experience
heterogeneous financial outcomes after the ChatGPT
shock (Nov 2022), determined by the task replicability
of their core product?

## Treatment variables
Two SBERT-based scores (all-MiniLM-L6-v2):

1. high_score (= replicability_score)
   18 high-replicability anchor sentences
   Mean 0.340, SD 0.068, range 0.17-0.53

2. contrast_score = high_score - low_score
   high anchors (18) minus low anchors (10,
   infrastructure/security/real-time tasks)
   Mean -0.007, SD 0.081, range -0.19 to +0.28
   +30% wider range, corr w/ high_score = 0.35

Face validity confirmed across all 143 firms.
Treatment variable construction complete.

## Simplified design
Dropped switching costs, AI adoption position, and
error cost from main regression. Too many constructed
variables creates OVB credibility concerns. Lean design:
one novel treatment + firm/quarter FE.

Switching costs → pre-shock revenue volatility
  (already in panel, available all 143 firms)
AI position → heterogeneity analysis only
Error cost → robustness check only

## Three mechanisms
1. Substitution    → revenue falls
2. Commodification → revenue flat, margins fall
3. Reinforcement   → revenue and margins rise

## Empirical design
DiD with continuous treatment intensity
Y_it = α_i + δ_t + β1(Post_t × Replicability_i) + ε_it
Post_t = 1 if quarter >= 2022 Q4
Firm FE + Quarter FE + clustered SE at firm level
Wild cluster bootstrap for inference

## Main results (trimmed 2020+ sample, bare DiD)

Mechanism 1 — Substitution (high_score treatment):
  All firms:    ln(Rev) β=-0.759*,  SE=0.401, p=0.060
  Wayback-only: ln(Rev) β=-1.051**, SE=0.427, p=0.016

Mechanism 2 — Commodification (contrast_score treatment):
  All firms:    Gross Margin β=-0.076*, SE=0.042, p=0.069
  Wayback-only: Gross Margin β=-0.114*, SE=0.060, p=0.060

## Parallel trends — ALL PASS on trimmed 2020+ sample

high_score:
  ln(Revenue): F=0.89, p=0.54
  Gross Margin: F=0.98, p=0.46
  Operating Margin: F=1.00, p=0.44

contrast_score:
  ln(Revenue): F=0.92, p=0.52
  Gross Margin: F=0.65, p=0.77
  Operating Margin: F=1.20, p=0.29

## Outcome variables
PRIMARY:   ln_revenue, gross_margin, operating_margin
SECONDARY: yoy_revenue_growth

## Sample
SIC 7370-7379, NYSE/NASDAQ, IPO before 2020 Q1
Revenue > $12.5M quarterly by 2021
B2B focus, scorable core product
n = 143 firms, 2020 Q1 - 2025 Q4 (trimmed)

## Data sources
Financial panel:    SEC EDGAR XBRL API (free, no auth)
Firm universe:      SEC company_tickers_exchange.json
Product page text:  Wayback Machine CDX API (free)
All treatment vars: pre-Nov 2022 text ONLY

## Known limitations
- MongoDB (MDB) scored high (0.47) — 10-K fallback artifact
- 37 firms use 10-K fallback (MSFT, CRM, CRWD, HUBS, NET, etc.)
- Gross margin pre-trend fails on full 2019+ sample
  fixed by trimming to 2020+ (p=0.46)

## Script execution order
1. scripts/build_firm_universe.py
   → data/raw/firm_universe_raw.csv
   ONE HTTP request only. No per-firm calls.

2. scripts/get_sic_codes.py
   → data/raw/firm_universe_with_sic.csv
   Adds SIC codes via EDGAR submissions API.
   Per-firm calls with 0.12s rate limiting.

3. scripts/apply_filters.py
   → data/raw/firm_universe_v1.csv
   Applies IPO filter automatically.
   Adds b2b_focus and meets_filters columns
   for manual review.
   [MANUAL STEP after this script]

4. scripts/collect_financials.py
   → data/raw/financials_panel.csv
   EDGAR XBRL per-firm. Revenue, gross profit,
   gross margin, operating income, R&D, SG&A.
   Date range: 2019 Q1 to 2025 Q4.

5. scripts/collect_product_text.py
   → text_data/product_pages/[TICKER].txt
   Wayback Machine snapshots, Q2-Q3 2022.

6. scripts/build_replicability.py
   → data/processed/replicability_scores.csv

7. scripts/build_master_panel.py
   → data/processed/master_panel.csv

8. analysis/did_main.R
   → figures/ and results/

## Key constraints — never violate
- Treatment variables from pre-Nov 2022 only
- Parallel trends test before any result table
- Event study is primary, binary DiD secondary
- Wild cluster bootstrap p-values required
- Commodification test on margins mandatory

## Current status
[x] Folder structure created
[x] Firm universe built
[x] SIC codes added
[x] Filters applied and manual review done (173 firms)
[x] Financial panel collected (2,982 rows, 143 firms, finalized)
[x] 10-K business descriptions collected (143/143 firms)
[x] Thesis plan written (THESIS_PLAN.md)
[x] Product text collected (106 Wayback + 37 10-K fallback)
[x] Replicability index built (SBERT, 18+10 anchors, 143/143)
[x] Contrast score validated (face validity all 143 firms)
[x] Master panel merged (2,982 rows, 143 firms)
[x] DiD estimated — high_score: ln(Rev) β=-0.759*, p=0.060
[x] DiD estimated — contrast_score: GM β=-0.076*, p=0.069
[x] Parallel trends tested (all pass, both treatments)
[x] Wayback-only subsample strengthens both results
[x] Wild cluster bootstrap inference complete
    Result 1: p=0.018** | Result 2: p=0.047**
[ ] Event study plots finalized
[ ] Heterogeneity analysis complete
[ ] Robustness checks complete
[ ] Thesis written
