# Thesis Plan

## Title

Generative AI as a Task Shock: Replicability, Commodification, and Firm Performance in the Software Industry

## Research Question

Do software firms (SIC 7370-7379) experience heterogeneous financial outcomes after the ChatGPT shock (November 2022), determined by the task replicability of their core product and their switching cost structure?

## Theoretical Framework

The release of ChatGPT in November 2022 represents an exogenous technology shock to the software industry. Unlike previous waves of automation that primarily affected routine manual and cognitive tasks, large language models (LLMs) can replicate complex knowledge-intensive tasks — code generation, text analysis, customer support, and content creation — at near-zero marginal cost. This creates a natural experiment: firms whose core product functionality overlaps with LLM capabilities face competitive pressure, while firms whose products complement or integrate AI capabilities may benefit.

Building on the task-based framework of Acemoglu & Autor (2011) and the automation models of Acemoglu & Restrepo (2018, 2019), we conceptualize generative AI as a "task shock" that simultaneously enables substitution, commodification, and reinforcement across different product categories. The key insight is that the impact depends not on whether a firm "uses AI" but on whether AI replicates the firm's value proposition. A code editor whose core feature is syntax completion faces substitution; an ERP system with deep workflow integration faces commodification of its AI-adjacent features but retains value through switching costs.

The heterogeneity of firm responses is governed by two interacting dimensions: task replicability (how easily can an LLM replicate what the product does?) and switching costs (how locked-in are existing customers?). High replicability with low switching costs predicts revenue decline (substitution). High replicability with high switching costs predicts margin compression (commodification — customers stay but demand lower prices or equivalent AI features). Low replicability predicts stable or rising performance (reinforcement), especially when firms integrate AI to extend their moat.

## Three Mechanisms

### 1. Substitution
**Definition:** Revenue declines as customers replace the firm's product with LLM-based alternatives.
**Conditions:** High task replicability + low switching costs.
**Example:** A simple text-editing SaaS loses customers to ChatGPT or free AI writing tools.
**Prediction:** Negative coefficient on Post × Replicability for ln(revenue).

### 2. Commodification
**Definition:** Revenue remains stable but margins compress as the firm must add AI features or compete on price.
**Conditions:** High task replicability + high switching costs.
**Example:** An established CRM platform must integrate AI features (at cost) to retain customers who now expect AI-powered functionality as table stakes.
**Prediction:** Negative coefficient on Post × Replicability for gross_margin and operating_margin, but insignificant for ln(revenue).

### 3. Reinforcement
**Definition:** Revenue and margins rise as AI capabilities complement the firm's existing moat.
**Conditions:** Low task replicability + high switching costs or strong integration depth.
**Example:** A cybersecurity platform uses AI to enhance threat detection, deepening its competitive advantage.
**Prediction:** Positive or insignificant coefficient on Post × Replicability; positive interaction with switching costs.

## Empirical Design

### Sample Description
- **Industry:** SIC 7370-7379 (Computer Programming, Data Processing, and Other Computer Related Services)
- **Exchanges:** NYSE and NASDAQ
- **Period:** 2019 Q1 to 2025 Q4 (28 quarters, 16 pre-shock, 12 post-shock)
- **IPO filter:** Listed before 2020 Q1
- **Revenue filter:** Minimum $12.5M quarterly revenue by 2021
- **Focus:** B2B software firms with a scorable core product
- **Current sample:** 155 firms, 3,034 firm-quarter observations

### Identification Strategy
The ChatGPT release (November 30, 2022) serves as the treatment event. Treatment intensity is continuous, measured by pre-shock task replicability scores derived from product page text dated Q2-Q3 2022. The key identifying assumption is that pre-shock replicability scores are uncorrelated with post-shock trends conditional on firm and time fixed effects (parallel trends).

### Main Regression Equation
```
Y_it = α_i + δ_t + β1(Post_t × Replicability_i) + β2(Post_t × SwitchingCost_i) + γX_it + ε_it
```

Where:
- `Y_it`: ln(revenue), gross_margin, or operating_margin for firm i in quarter t
- `α_i`: Firm fixed effects
- `δ_t`: Quarter fixed effects
- `Post_t`: Indicator = 1 if quarter >= 2023 Q1
- `Replicability_i`: Pre-shock task replicability score [0-1]
- `SwitchingCost_i`: Pre-shock switching cost index [0-1]
- `X_it`: Time-varying controls (log assets, R&D intensity)
- `ε_it`: Clustered at firm level

### Parallel Trends Requirement
Before presenting any regression results, we must:
1. Run an event study specification with leads and lags
2. Show that pre-shock coefficients on Replicability × Quarter dummies are jointly insignificant
3. Use the Callaway & Sant'Anna (2021) approach for robustness

### Inference
- Standard errors clustered at firm level
- Wild cluster bootstrap p-values (required given ~155 clusters)
- Sensitivity analysis: varying the treatment cutoff, alternative clustering

## Treatment Variables

All treatment variables are measured using **pre-November 2022 data only** to avoid endogeneity.

### 1. Task Replicability Index [0-1]
**Source:** Product page text from Wayback Machine snapshots (Q2-Q3 2022).
**Method:** SBERT (Sentence-BERT) semantic similarity between the firm's product description and a set of reference phrases describing LLM-replicable tasks (e.g., "generate code from natural language," "automate text analysis," "create content from prompts"). Higher similarity = higher replicability.
**Construction:** Embed product page text and reference phrases using `all-MiniLM-L6-v2`. Compute cosine similarity. Normalize to [0-1] across the sample.

### 2. AI Adoption Position [1/2/3]
**Source:** Product page text (pre-shock).
**Method:** LLM-based classification using a structured rubric:
- **Position 1 (Threatened):** Core product overlaps with LLM capabilities
- **Position 2 (Adapting):** Product adjacent to AI — must integrate or compete
- **Position 3 (Reinforced):** Product complementary to AI — benefits from integration
**Note:** Groups are never pooled in regressions.

### 3. Switching Cost Index [0-1]
**Source:** Net Revenue Retention (NRR) rates and contract duration from 10-K filings and earnings calls (pre-shock).
**Construction:** Composite of NRR (normalized) and average contract length. Higher switching costs = more customer lock-in.

### 4. Error Cost Index [0-6]
**Source:** Domain classification of the firm's primary market.
**Method:** Score based on the cost of errors in the firm's domain (e.g., cybersecurity = high error cost, content creation = low error cost). Derived from industry classification.

## Data Sources

| Source | Data | Access |
|--------|------|--------|
| SEC EDGAR company_tickers_exchange.json | Firm universe (CIK, ticker, exchange) | Free, single HTTP request |
| SEC EDGAR submissions API | SIC codes, filing history | Free, per-firm |
| SEC EDGAR XBRL companyfacts API | Quarterly financials (revenue, margins, R&D, SG&A) | Free, per-firm |
| Wayback Machine CDX API | Product page snapshots (pre-shock text) | Free |
| Product pages (archived) | Product descriptions for replicability scoring | Via Wayback Machine |
| 10-K filings / earnings calls | NRR, contract terms for switching costs | SEC EDGAR |

## Current Status

- [x] Folder structure created
- [x] Firm universe built (7,509 → 530 SIC-filtered → 155 final)
- [x] SIC codes added via EDGAR browse API
- [x] Filters applied and manual review done (173 → 155 after foreign filer exclusion)
- [x] Financial panel collected (3,034 rows, 155 firms)
- [ ] Product text collected (Wayback Machine)
- [ ] Replicability index built (SBERT)
- [ ] Switching costs built
- [ ] Master panel merged
- [ ] DiD estimated
- [ ] Event study plotted
- [ ] Commodification test done
- [ ] Heterogeneity by AI position done

## Upcoming Steps

| Step | Script | Description |
|------|--------|-------------|
| 5 | `scripts/collect_product_text.py` | Scrape product page snapshots from Wayback Machine (Q2-Q3 2022) |
| 6 | `scripts/build_replicability.py` | Compute SBERT semantic similarity scores for task replicability |
| 7 | `scripts/build_switching_costs.py` | Construct switching cost index from NRR and contract data |
| 8 | `scripts/build_master_panel.py` | Merge financials with treatment variables into master panel |
| 9 | `analysis/did_main.R` | Run DiD regressions, event studies, bootstrap inference |
| 10 | `analysis/robustness.R` | Parallel trends, placebo tests, alternative specifications |

## Key References

- Acemoglu, D., & Autor, D. (2011). Skills, tasks and technologies: Implications for employment and earnings. *Handbook of Labor Economics*, 4, 1043-1171.
- Acemoglu, D., & Restrepo, P. (2018). The race between man and machine: Implications of technology for growth, factor shares, and employment. *American Economic Review*, 108(6), 1488-1542.
- Acemoglu, D., & Restrepo, P. (2019). Automation and new tasks: How technology displaces and reinstates labor. *Journal of Economic Perspectives*, 33(2), 3-30.
- Acemoglu, D. (2024). The simple macroeconomics of AI. *NBER Working Paper*.
- Callaway, B., & Sant'Anna, P. H. (2021). Difference-in-differences with multiple time periods. *Journal of Econometrics*, 225(2), 200-230.
- Autor, D. H. (2024). Applying AI to rebuild middle class jobs. *NBER Working Paper*.
- Eloundou, T., Manning, S., Mishkin, P., & Rock, D. (2023). GPTs are GPTs: An early look at the labor market impact potential of large language models. *arXiv preprint*.
- Brynjolfsson, E., Li, D., & Raymond, L. (2023). Generative AI at work. *NBER Working Paper*.
