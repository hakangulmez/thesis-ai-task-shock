# CLAUDE.md

## Thesis title
Generative AI as a Task Shock: Replicability,
Commodification, and Firm Performance in the
Software Industry

## Author
Hakan Zeki Gülmez — TUM Applied Econometrics
Supervisor: Prof. Dr. Helmut Farbmacher

## Research question
Do software firms (SIC 7370-7379) experience
heterogeneous financial outcomes after the ChatGPT
shock (Nov 2022), determined by the task replicability
of their core product and their switching cost structure?

## Three mechanisms
1. Substitution    → revenue falls
2. Commodification → revenue flat, margins fall
3. Reinforcement   → revenue and margins rise

## Treatment variables (ALL pre-Nov 2022 only)
1. task_replicability_i  [0-1]   SBERT semantic score
2. ai_position_i         [1/2/3] LLM rubric classification
3. switching_cost_i      [0-1]   NRR + contract duration
4. error_cost_i          [0-6]   domain classification

## Outcome variables
PRIMARY:   ln_revenue, gross_margin, operating_margin
SECONDARY: yoy_revenue_growth

## Empirical design
DiD with continuous treatment intensity
Y_it = α_i + δ_t + β1(Post_t × Replicability_i)
                 + β2(Post_t × SwitchingCost_i)
                 + γX_it + ε_it
Post_t = 1 if quarter >= 2023 Q1
Firm FE + Quarter FE + clustered SE at firm level
Wild cluster bootstrap for inference

## Sample
SIC 7370-7379, NYSE/NASDAQ, IPO before 2020 Q1
Revenue > $12.5M quarterly by 2021
B2B focus, scorable core product
Expected n = 70-100 firms, 2019 Q1 - 2025 Q4

## Data sources
Financial panel:    SEC EDGAR XBRL API (free, no auth)
Firm universe:      SEC company_tickers_exchange.json
Product page text:  Wayback Machine CDX API (free)
All treatment vars: pre-Nov 2022 text ONLY

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

7. scripts/build_switching_costs.py
   → data/processed/switching_costs.csv

8. scripts/build_master_panel.py
   → data/processed/master_panel.csv

9. analysis/did_main.R
   → figures/ and results/

## Key constraints — never violate
- Treatment variables from pre-Nov 2022 only
- Parallel trends test before any result table
- Event study is primary, binary DiD secondary
- Wild cluster bootstrap p-values required
- Commodification test on margins mandatory
- Never pool AI position groups

## Current status
[x] Folder structure created
[x] Firm universe built
[x] SIC codes added
[x] Filters applied and manual review done (173 firms)
[x] Financial panel collected (2,982 rows, 143 firms, finalized)
[x] 10-K business descriptions collected (143/143 firms)
[x] Thesis plan written (THESIS_PLAN.md)
[x] Product text collected (106 Wayback + 37 10-K fallback)
[x] Replicability index built (SBERT, 143/143 firms)
[ ] Switching costs built
[x] Master panel merged (2,982 rows, 143 firms)
[ ] DiD estimated
[ ] Event study plotted
[ ] Commodification test done
[ ] Heterogeneity by position done
