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

## Main treatment variable
task_replicability_i [0-1]
SBERT all-MiniLM-L6-v2, 18 anchor sentences
Score range: 0.14-0.53, mean 0.318, SD 0.070

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
ln(Revenue):      β = -0.759*, SE = 0.401, p<0.10
Gross Margin:     β = +0.054,  SE = 0.083, ns
Operating Margin: β = -0.434,  SE = 0.403, ns

## Parallel trends — ALL PASS on trimmed 2020+ sample
ln(Revenue):      F=0.89, p=0.54
Gross Margin:     F=0.98, p=0.46
Operating Margin: F=1.00, p=0.44

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
[x] Replicability index built (SBERT, 18 anchors, 143/143)
[x] Master panel merged (2,982 rows, 143 firms)
[x] DiD estimated (revenue β=-0.759*, p<0.10)
[x] Parallel trends tested (all pass, 2020+ sample)
[ ] Wild cluster bootstrap inference
[ ] Event study plots finalized
[ ] Heterogeneity analysis complete
[ ] Robustness checks complete
[ ] Thesis written
