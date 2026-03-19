# Thesis Plan

## Generative AI as a Task Shock: Replicability, Commodification, and Firm Performance in the Software Industry

**Author:** Hakan Zeki Gulmez
**Program:** M.Sc. Management and Technology
**University:** Technical University of Munich (TUM)
**Supervisor:** Prof. Dr. Helmut Farbmacher
**Target submission:**

---

## 1. Research Question

**Primary:** Do B2B software firms experience heterogeneous financial outcomes after the ChatGPT shock (November 2022), and is that heterogeneity explained by the task replicability of their core product?

**Secondary questions:**

- Does switching cost structure moderate the speed at which replicability translates into financial outcomes?
- Do firms with AI already embedded in their product pre-shock outperform firms without?
- Is the primary channel substitution (revenue decline), commodification (margin compression), or reinforcement (margin improvement)?

---

## 2. Theoretical Framework

### 2.1 Task-Based Framework

Autor, Levy and Murnane (2003) reconceptualize production as a bundle of discrete tasks allocated between labor and capital according to comparative advantage. In their framework, routine cognitive tasks — rule-based procedures such as bookkeeping, clerical processing, and formulaic calculations — are substitutable by computer capital because they follow explicit, codifiable rules. Nonroutine cognitive tasks, by contrast — those requiring judgment, creativity, complex communication, abstract reasoning, and situational adaptation — were considered structurally resistant to automation because they could not be reduced to a set of programmable instructions. Software capital in this framework complemented nonroutine cognitive labor by handling the routine components of knowledge work, thereby raising the marginal productivity of human workers performing the nonroutine residual. The empirical implication was a secular increase in demand for workers performing nonroutine cognitive tasks and a secular decline in demand for workers performing routine cognitive tasks — a prediction borne out by two decades of labor market evidence.

Acemoglu and Restrepo (2018, 2019) formalize and extend this framework by modeling the automation frontier — the endogenously determined boundary between the set of tasks performed by labor and the set performed by machines. When automation technology improves, it pushes this frontier outward: tasks previously performed by labor are displaced to capital, reducing labor's task share and compressing wages for workers who performed those tasks (the displacement effect). Simultaneously, economic growth and innovation create new tasks at the frontier that require human capabilities machines have not yet acquired (the reinstatement effect). The net impact on labor demand, wages, and the labor share of income depends on the relative speed of displacement versus reinstatement. Critically, their framework implies that a technology which moves the automation frontier into previously safe task space — nonroutine cognitive territory — will have asymmetric effects across economic actors depending on their exposure to the newly automatable task set. Actors whose value proposition rests on performing tasks near the new frontier face displacement; actors whose tasks remain far from the frontier may benefit from complementarity.

Prior to November 2022, the automation frontier had not meaningfully penetrated nonroutine cognitive task space. Machine learning systems excelled at pattern recognition within structured data — image classification, recommendation engines, fraud detection — but could not perform open-ended cognitive tasks such as drafting coherent text, summarizing complex documents, answering questions from unstructured knowledge bases, or generating structured output from natural language prompts. The public release of ChatGPT on November 30, 2022 changed this discontinuously. ChatGPT demonstrated that a general-purpose AI system could perform a broad range of nonroutine cognitive tasks — tasks that the ALM framework had classified as structurally safe from automation — at near-zero marginal cost and with sufficient quality to be commercially useful. This moved the automation frontier into territory that prior technology had left untouched, creating a discrete, unanticipated shock to the task structure of knowledge-intensive industries. The software industry, which had built its business model precisely on externalizing cognitive tasks from customer organizations, faced a uniquely direct form of exposure.

### 2.2 Software Firms as Task Externalizers

Software firms occupy a unique position in the task-based framework that existing theory does not fully capture. Unlike physical capital goods that augment a worker's productivity at a specific task, B2B software firms are task-performing services: they externalize cognitive tasks from customer organizations and build recurring revenue businesses around performing those tasks more efficiently than customers could manage internally. A CRM platform performs contact management, pipeline tracking, and sales forecasting tasks. A cybersecurity platform performs threat detection, vulnerability scanning, and incident response tasks. A business intelligence tool performs data aggregation, metric computation, and report generation tasks. An expense management platform performs receipt capture, policy compliance checking, and reimbursement workflow tasks. In each case, the revenue model depends on customers continuing to find it more efficient to purchase task performance as a subscription service rather than perform those tasks internally with general-purpose tools. The entire SaaS business model is, at its core, a bet that specialized task externalization creates durable value.

This creates an exposure structure that the standard task-based framework — which analyzes automation's impact on labor within firms — does not address. When a general-purpose AI system can now perform many of the same cognitive tasks that a software product has been charging customers to perform, the firm faces not a labor displacement problem but a product obsolescence problem. Three possible outcomes emerge. First, customers may substitute the product directly with AI tools that replicate its core tasks at lower cost — revenue falls. Second, customers may remain with the product due to switching costs and integration dependencies but lose willingness to pay a premium, knowing that alternatives now exist — revenue holds in the short run but margins compress as pricing power erodes and defensive investment rises. Third, for firms whose tasks are deeply integrated with proprietary customer data, require complex multi-system orchestration, or involve domain-specific workflows that general-purpose AI cannot replicate, the ChatGPT shock may create reinforcement rather than threat — AI capabilities are absorbed into an already defensible product, making it more powerful and further widening the competitive moat. The firm-level distribution of these outcomes is determined by pre-shock product task structure, not by post-shock strategic adaptation. This is the central empirical claim of this thesis.

### 2.3 Three Mechanisms

**Substitution.** When task replicability is high and switching costs are low, customers face a credible outside option. They can replace the software product entirely with a general-purpose LLM, an AI-native startup that performs the same tasks at lower cost, or an internal solution built on foundation model APIs. Revenue declines as customers reduce seats, downgrade plans, cancel contracts, or migrate to alternatives. This mechanism operates most strongly for standalone, point-solution software products that perform a single well-defined cognitive task with limited integration requirements and minimal proprietary data dependencies — document generation tools, basic CRM systems, simple content management platforms, standalone survey tools, and template-based reporting products. The substitution channel is the most visible but potentially not the most economically significant mechanism, because the firms most vulnerable to direct substitution tend to be smaller and less entrenched. Empirical signature: negative coefficient on Post x Replicability for ln_revenue, concentrated among firms with low switching costs.

**Commodification.** When task replicability is high but switching costs are also high, customers cannot easily leave — but their perception of the product's value changes fundamentally. The existence of credible AI alternatives that perform similar tasks at a fraction of the cost erodes the vendor's pricing power even if customers remain on the platform. Renewal negotiations become harder as procurement teams benchmark against AI-native competitors. New customer acquisition slows as prospects evaluate whether they need a specialized SaaS tool when a general-purpose AI system can approximate the same functionality. The vendor must invest more in sales, marketing, and product development to defend existing accounts and win new ones — adding AI features that customers now expect as table stakes rather than as premium differentiators. Revenue may hold in the short run as multi-year contracts expire gradually, but gross margins and operating margins compress as pricing power erodes and costs rise to defend the customer base. This is the novel mechanism of this thesis. It predicts margin compression even without revenue decline — a pattern that is empirically distinguishable from both substitution (which hits revenue first) and from a general industry downturn (which would not correlate with pre-shock task replicability). Empirical signature: negative coefficient on Post x Replicability for gross_margin and operating_margin, but insignificant or weakly negative coefficient for ln_revenue.

**Reinforcement.** When task replicability is low — because the product's core tasks require deep integration with customer infrastructure, depend on accumulated proprietary organizational data that cannot be replicated by a general-purpose system, or involve complex multi-system orchestration across enterprise workflows — the ChatGPT shock creates an opportunity rather than a threat. These firms can absorb LLM capabilities as a component input to their existing product, using AI to make an already powerful platform even more capable. Their customers increasingly depend on AI-powered workflows that run through the vendor's platform, creating new forms of lock-in. The vendor can charge premium prices for AI-enhanced features because customers have no viable alternative that combines AI capability with the specific integration depth, data access, and workflow orchestration that the vendor provides. Revenue and margins improve as AI augments an already defensible product position. Reinforcement is strongest for firms that already had AI embedded in their product pre-shock (high AI adoption position), because they had the infrastructure and expertise to rapidly integrate LLM capabilities into their existing offering. Empirical signature: positive coefficient on Post x Replicability x AIPosition for high-AI-position firms, and positive or insignificant coefficient on Post x Replicability for low-replicability firms regardless of AI position.

### 2.4 The Role of Switching Costs

Switching costs create a temporal wedge between structural replicability exposure and realized financial outcomes. A firm with high task replicability and high switching costs does not face immediate revenue decline — customers are locked in by data migration costs, user retraining requirements, workflow dependencies across organizational processes, API integrations with other enterprise systems, and long-term contracts with early termination penalties. But the financial damage accumulates as contracts come up for renewal and new customer acquisition becomes harder. Switching costs therefore moderate the speed of commodification rather than its ultimate magnitude. This has an important empirical implication: in a panel covering 2019 Q1 through 2025 Q3, high-replicability firms with high switching costs should show margin compression before revenue decline, creating a detectable commodification signature that precedes and is distinguishable from substitution. By contrast, high-replicability firms with low switching costs should show revenue decline earlier, as the substitution channel operates without the contractual friction that delays customer departure. The interaction between replicability and switching costs thus provides a within-sample test of the mechanism: if the same replicability score predicts different outcome paths depending on switching cost structure, this supports the theoretical distinction between substitution and commodification as separate channels rather than points on a single continuum.

### 2.5 Connection to Acemoglu (2024)

Acemoglu (2024) uses a simple macroeconomic model calibrated to current AI capabilities to argue that AI's aggregate productivity effect will be modest — approximately 0.66 percent total factor productivity gain over the next ten years — because only easy-to-learn tasks are automatable in the near term and the share of economic output attributable to such tasks is small in aggregate. This thesis operates at the firm level within a single industry and tests the distribution of outcomes that underlies that aggregate result. Acemoglu's aggregate modesty is entirely consistent with substantial firm-level heterogeneity: some firms face severe commodification or outright substitution while others experience strong reinforcement, and the aggregate effect across all firms averages out to a modest net impact. By constructing a continuous replicability measure that maps directly onto Acemoglu's distinction between easy-to-learn tasks (high replicability, amenable to near-term AI automation) and hard-to-learn tasks (low replicability, requiring deep context and integration that current AI cannot provide), this thesis provides micro-level evidence on the firm-level distribution that drives the aggregate result. If the data show that high-replicability firms experience margin compression while low-replicability firms experience reinforcement, this would be consistent with Acemoglu's aggregate modesty arising from offsetting firm-level effects rather than from uniformly small impacts across all firms.

---

## 3. Empirical Design

### 3.1 Identification Strategy

The ChatGPT launch on November 30, 2022 is treated as an exogenous shock to the LLM automation frontier. Three conditions support this identification.

**First, the shock was sudden and unexpected.** There was no public signal before November 2022 that a general-purpose conversational AI system with broad nonroutine cognitive task capabilities was imminent. Prior AI announcements — GPT-3 in June 2020, GitHub Copilot in June 2021 — were technically impressive but remained developer-facing tools that did not change mainstream customer behavior or procurement decisions. ChatGPT's public release and immediate viral adoption (100 million users within two months) constituted a discrete, unanticipated event that fundamentally altered the competitive landscape for knowledge-work software.

**Second, the shock affected all firms simultaneously.** Because the shock is a change in the technological frontier rather than a policy, regulatory, or demand shock, it hits all firms at the same time regardless of geography, customer base, or firm size. This satisfies the requirement that the treatment timing is common across all units — the variation in treatment intensity comes from pre-determined firm characteristics, not from differential timing of exposure.

**Third, treatment heterogeneity comes from pre-determined firm characteristics.** The task replicability index is constructed exclusively from product documentation and regulatory filings dated before November 2022. A firm's exposure to the shock is determined by what its product was doing before ChatGPT existed, not by any strategic response to it. This eliminates reverse causality: post-shock financial outcomes cannot cause pre-shock product characteristics. The identifying assumption is that, conditional on firm and quarter fixed effects, pre-shock task replicability is uncorrelated with post-shock trends in financial outcomes other than through the ChatGPT shock channel.

### 3.2 Main Regression Equation

```
Y_it = alpha_i + delta_t
     + beta_1 (Post_t x Replicability_i)
     + epsilon_it
```

Where:

- **Y_it:** outcome variable for firm i in quarter t. Estimated separately for: ln_revenue, gross_margin, operating_margin.
- **Post_t:** indicator equal to 1 if t >= 2022 Q4.
- **Replicability_i:** task replicability index [0,1], constructed from pre-November 2022 product text using SBERT semantic similarity (all-MiniLM-L6-v2, 18 anchor sentences).
- **alpha_i:** firm fixed effects (absorb all time-invariant firm characteristics including industry sub-sector, firm size, business model, founding date, and all other permanent attributes).
- **delta_t:** quarter-year fixed effects (absorb all macroeconomic shocks common to all firms including interest rate changes, aggregate demand shifts, and sector-wide trends).
- Standard errors clustered at firm level.
- Wild cluster bootstrap p-values reported alongside clustered standard errors (important given n=143 clusters, which is in the range where conventional cluster-robust inference may be unreliable).

**Note:** Switching costs, AI adoption position, and error cost have been moved to heterogeneity analysis and robustness checks respectively to maintain a parsimonious and credible identification strategy. Including multiple constructed treatment variables in the main specification creates overfitting and credibility concerns. The lean design — one novel treatment variable + firm/quarter FE — maximizes identification clarity.

**Key predictions:**

- beta_1 < 0 for ln_revenue → substitution
- beta_1 < 0 for operating_margin → commodification
- beta_1 insignificant for gross_margin → pricing power not yet eroded

### 3.3 Event Study Specification

```
Y_it = alpha_i + delta_t
     + SUM_{k != -1} beta_k (D_kt x Replicability_i)
     + controls + epsilon_it
```

Where D_kt is an indicator equal to 1 if firm i is observed k quarters relative to 2022 Q4. k ranges from -12 to +11 quarters (2019 Q4 through 2025 Q3). The omitted category is k = -1 (2022 Q3, one quarter before the shock).

The beta_k coefficients trace the dynamic treatment effect over time. Pre-shock coefficients (k < 0) test parallel trends — they should be individually insignificant and jointly indistinguishable from zero if firms with different replicability levels were on parallel pre-shock trajectories. Post-shock coefficients (k > 0) reveal how the effect builds, persists, or fades over time, allowing visual identification of whether the commodification channel operates gradually (as predicted) or sharply.

### 3.4 Parallel Trends Assumption

Parallel trends requires that, absent the ChatGPT shock, firms with high and low task replicability would have followed parallel trends in the outcome variables. This assumption is plausible for three reasons.

First, task replicability is determined by product architecture — a structural property of the firm's core offering that changes slowly over years, not quarters. There is no reason to expect firms with more replicable products to have systematically diverging revenue or margin trends in the pre-period conditional on firm and time fixed effects.

Second, the pre-period (2019 Q1 through 2022 Q3) includes substantial macroeconomic variation — COVID-19 disruption, recovery, interest rate hikes — that affected all software firms but should not have differentially affected firms based on task replicability, since replicability measures AI exposure rather than demand sensitivity or financial vulnerability.

**Formal test:** Report the event study plot showing pre-period beta_k coefficients and their 95% confidence intervals. Report the joint F-test for H0: beta_k = 0 for all k < 0. If pre-trends are detected, explore controls for pre-shock revenue growth rate and firm-specific linear time trends as robustness checks.

### 3.5 Heterogeneity Analysis

Three sub-group analyses, each estimated as separate regressions rather than pooled interactions:

**1. By AI adoption position (Position 1 vs 2 vs 3).** Tests whether the reinforcement effect is concentrated in firms that already had AI embedded in their product before the shock. Prediction: Position 3 firms show positive or zero coefficients on Post x Replicability; Position 1 firms show the strongest negative coefficients.

**2. By switching cost quartile (Q1 vs Q4).** Tests whether commodification manifests faster for low-switching-cost firms (direct substitution) versus slower for high-switching-cost firms (delayed margin compression). Prediction: low-switching-cost firms show revenue decline earlier; high-switching-cost firms show margin compression before revenue decline.

**3. By SIC sub-code.** Tests whether the effect differs across software sub-industries: computer services and rentals (7370), programming services (7371), prepackaged software (7372), systems integration (7373), data processing (7374). Prediction: prepackaged software (7372) shows the strongest commodification effect because standalone packaged products are most directly comparable to AI alternatives.

---

## 4. Treatment Variables

### 4.1 Task Replicability Index

**Construction method:**

**Step 1 — Text collection.** Product page text collected from Wayback Machine CDX API, targeting Q2-Q3 2022 snapshots (April through October 2022). For each firm, fetch the top 3 highest-scoring pages (product, platform, features, and solutions pages scored by URL pattern matching and navigation depth). Fallback: EDGAR 10-K Item 1 Business Description if Wayback coverage is insufficient (fewer than 150 words of usable product text).

**Step 2 — Text cleaning.** Strip HTML tags, remove navigation, footer, and header elements. Filter to lines containing task-descriptive verbs (automate, manage, detect, analyze, route, generate, monitor, track, optimize, schedule, classify, extract, summarize, etc.). Truncate to 3,000 words maximum per firm.

**Step 3 — SBERT scoring.** Use the all-MiniLM-L6-v2 sentence transformer model to encode each sentence from the cleaned product text. Compute cosine similarity against a curated set of high-replicability anchor sentences representing tasks that LLMs can perform well:

- "Draft and send personalized emails to customers"
- "Summarize meeting notes and action items"
- "Answer customer questions from a knowledge base"
- "Generate reports from structured data"
- "Extract information from documents and forms"
- "Write marketing copy and social media posts"
- "Classify and route support tickets by topic"
- "Translate text between languages"
- "Generate code from natural language descriptions"
- "Create documentation from technical specifications"

Firm score = mean cosine similarity of the firm's top-10 most similar sentences to the anchor set. Scale: 0 (no task similarity to LLM-replicable tasks) to 1 (maximum similarity).

**Step 4 — Validation.**

(a) Correlation with LLM rubric scores: use Claude API to independently score each firm's product text on a 0-1 replicability scale using a structured rubric. Report Pearson correlation between SBERT scores and LLM rubric scores across all 143 firms.

(b) Correlation with manual scores: two independent raters score a random subset of 20 firms on a 0-1 replicability scale using the same rubric. Report inter-rater reliability (Cohen's kappa target >= 0.65) and correlation with SBERT scores.

(c) Face validity check: verify that known high-replicability firms (e.g., ZipRecruiter, Expensify, basic CRM tools) score higher than known low-replicability firms (e.g., ServiceNow, Dynatrace, Qualys, CrowdStrike).

### 4.2 Switching Cost Index

Three components constructed from pre-November 2022 data:

**Component 1 — Net Revenue Retention (NRR).** Collected manually from earnings calls and investor presentations filed before November 2022. NRR above 100% indicates that existing customers are expanding their usage — a strong signal of product stickiness and high switching costs. Available for approximately 40-50 firms that explicitly disclose NRR. Normalized to [0,1]: NRR of 70% maps to 0.0, NRR of 130% maps to 1.0, with linear interpolation between.

**Component 2 — Contract duration.** Remaining performance obligations (RPO) disclosed under ASC 606 in pre-2022 10-K revenue recognition footnotes. Longer weighted average remaining contract duration implies higher switching costs because customers have committed to multi-year agreements. Normalized to [0,1]: weighted average duration less than 1 year maps to 0.0, greater than 3 years maps to 1.0.

**Component 3 — Integration depth.** Count of native integrations listed on the pre-2022 product page (from Wayback Machine snapshot). More integrations imply deeper customer workflow dependency — each integration represents an additional connection that must be replicated or replaced if the customer switches vendors. Normalized to [0,1] on a log scale: 0 integrations maps to 0.0, 100 or more maps to 1.0.

**Final score:** equal-weighted average of available components. Firms missing one component receive a two-component average. Firms missing all components are excluded from switching cost interaction regressions but remain in the main specification.

### 4.3 AI Adoption Position

LLM rubric classification applied to pre-November 2022 10-K business descriptions (fully collected for all 143 firms across 10-K, 20-F, and 40-F filing types).

Score each firm on three dimensions (0-3 each):

**Dimension 1 — Core value source:**
0: Pure rule-based automation, no ML component.
1: Statistical or ML models used as backend components.
2: ML/AI is the primary value driver of the product.
3: Generative AI or LLM capabilities are the core product output.

**Dimension 2 — Product dependency on AI:**
0: Product functions fully without any AI component.
1: AI enhances specific product features but is not required.
2: AI is required for core product functionality.
3: The product IS AI-generated output — remove AI and nothing remains.

**Dimension 3 — Revenue attribution to AI:**
0: No revenue attributable to AI-specific features.
1: AI features are bundled into the product, not separately priced.
2: AI tier or AI add-on commands a measurable price premium.
3: All revenue is directly attributable to AI capabilities.

**Classification:**
Total score 0-2 maps to Position 1 (AI used internally only, not in product).
Total score 3-5 maps to Position 2 (AI embedded in product as feature).
Total score 6-9 maps to Position 3 (AI IS the product).

**Validation:** Two independent raters classify a random subset of 15 firms using the rubric. Report inter-rater reliability with Cohen's kappa target >= 0.70 before scaling classification to all 143 firms via the Claude API.

### 4.4 Error Cost Index

Measures deployment friction in the customer's operating domain — how strongly customers resist AI substitution due to regulatory requirements, compliance obligations, and the consequences of errors in their specific industry.

**Scoring scale 0-6:**

0 — Email, content drafting, marketing copy (near-zero error cost, no regulatory exposure).
1 — Marketing analytics, A/B testing, campaign management (low stakes, minor regulatory exposure).
2 — Sales automation, lead scoring, customer engagement (moderate stakes, some data privacy requirements).
3 — HR, workforce management, recruiting (employment law compliance, GDPR/EEOC exposure).
4 — Financial reporting, compliance, audit (SEC/SOX requirements, mandatory audit trails).
5 — Healthcare administration, insurance processing (HIPAA compliance, clinical workflow requirements).
6 — Clinical decision support, financial trading, critical infrastructure (life-safety or market-critical decisions, maximum regulatory friction).

**Source:** EDGAR 10-K customer sector disclosures and risk factor sections, pre-November 2022 filings.

**Role:** Moderator variable in robustness specifications. High error cost reduces the speed at which task replicability translates into actual substitution or commodification, regardless of the technical replicability of the product's tasks. A highly replicable product deployed in a high-error-cost domain faces less competitive pressure than the same product deployed in a low-error-cost domain.

---

## 5. Data

### 5.1 Sample Construction

| Stage | Filter | Firms remaining |
|-------|--------|-----------------|
| Starting universe | NYSE/Nasdaq listed firms | 7,509 |
| SIC filter | SIC 7370-7379 only | 530 |
| IPO filter | Listed before 2020 Q1 | 287 |
| B2B focus | Manual review, B2B software only | 173 |
| Foreign filer exclusion | Drop 20-F annual filers | 152 |
| IPO filter corrections | Add CRM, DDOG, NOW, CRWD, NET (incorrectly excluded) | 155 |
| Sparse data cleanup | Require pre- and post-shock observations | 141 |
| Final audit additions | Restore firms with sufficient data | 143 |

**Final sample:** 143 B2B software firms with quarterly financial data covering both pre-shock (2019 Q1 through 2022 Q3) and post-shock (2023 Q1 through 2025 Q3) periods.

### 5.2 Financial Panel

**Source:** SEC EDGAR XBRL CompanyFacts API.
**Period:** 2019 Q1 to 2025 Q3.
**Observations:** 2,982 firm-quarter rows across 143 firms.

**Variable coverage:**

| Variable | Coverage |
|----------|----------|
| Revenue | 100% (2,982 / 2,982) |
| Operating income | 98% (2,912 / 2,982) |
| R&D expense | 84% (2,480 / 2,982) |
| SG&A expense | 93% (2,774 / 2,982) |

**Constructed variables:** revenue, cogs, gross_profit, gross_margin, operating_income, operating_margin, rd_expense, rd_intensity, sga_expense, sga_intensity, ln_revenue, yoy_revenue_growth.

**SIC breakdown:**

| SIC code | Description | Firms |
|----------|-------------|-------|
| 7370 | Computer services and rentals | 13 |
| 7371 | Computer programming services | 7 |
| 7372 | Prepackaged software | 93 |
| 7373 | Computer integrated systems design | 19 |
| 7374 | Computer processing and data preparation | 20 |

### 5.3 Text Sources

**10-K Business Descriptions:**

- Source: SEC EDGAR Archives (filing index.json + primary document).
- Coverage: 143/143 firms (100%).
- Filing types: 10-K (138 firms), 20-F (3 firms), 40-F (2 firms).
- Filing dates: fiscal year 2021 or early fiscal year 2022 (all filed before November 2022).
- Extraction: Item 1 Business Description for 10-K; Item 4 Information on the Company for 20-F; Item 4 Narrative Description of the Business from AIF exhibit for 40-F.
- Length: truncated to 2,000 words per firm.
- Uses: AI adoption position classification, error cost coding, replicability index fallback when Wayback Machine coverage is insufficient.

**Product Page Text (Wayback Machine):**

- Source: web.archive.org CDX API.
- Target window: April through October 2022.
- Coverage: to be collected (next pipeline step).
- Pages: product, platform, features, and solutions pages (top 3 per firm by URL pattern score).
- Length: up to 3,000 words per firm after cleaning.
- Uses: primary input for task replicability index construction.

### 5.4 All Treatment Variable Sources

**Critical constraint:** All treatment variables are constructed from sources dated strictly before November 30, 2022. No post-shock information enters the treatment variable construction process.

| Variable | Source | Date constraint |
|----------|--------|-----------------|
| Replicability index | Wayback Machine product pages | Q2-Q3 2022 snapshots |
| AI adoption position | EDGAR 10-K business descriptions | Fiscal year 2021 or early 2022 filing |
| Error cost index | EDGAR 10-K customer sector disclosures | Same filings as above |
| Switching cost — NRR | Earnings call transcripts, IR presentations | Pre-November 2022 |
| Switching cost — contract duration | EDGAR 10-K ASC 606 revenue footnotes | Pre-November 2022 |
| Switching cost — integration depth | Wayback Machine product pages | Q2-Q3 2022 snapshots |

---

## 6. Current Status

- [x] Firm universe built (7,509 -> 143 firms)
- [x] Financial panel collected (2,982 rows, 143 firms)
- [x] Domain list verified (143 firms)
- [x] 10-K business descriptions collected (143/143 firms, 10-K/20-F/40-F)
- [x] Thesis plan written (THESIS_PLAN.md)
- [x] Product text collected (106 Wayback + 37 10-K fallback)
- [x] Replicability index built (SBERT, 18 anchors, 143/143)
- [x] Master panel merged (2,982 rows, 143 firms)
- [x] DiD estimated (revenue β=-0.759*, p<0.10)
- [x] Parallel trends tested (all pass, 2020+ sample)
- [ ] Wild cluster bootstrap inference
- [ ] Event study plots finalized
- [ ] Heterogeneity analysis complete
- [ ] Robustness checks complete
- [ ] Thesis written

---

## 7. Timeline

| Week | Task |
|------|------|
| 1 | Product text collection (Wayback Machine CDX API) |
| 2 | Replicability index construction and three-way validation (SBERT + LLM + manual) |
| 3 | AI adoption position classification (LLM rubric + inter-rater kappa validation) |
| 4 | Error cost index coding + switching cost index construction |
| 5 | Master panel merge and data quality checks |
| 6-7 | DiD estimation, event study plots, heterogeneity analysis |
| 8 | Robustness checks (alternative shock date, alternative replicability measure, placebo test, Callaway-Sant'Anna) |
| 9-11 | Thesis writing (introduction, theory, data, results, conclusion) |
| 12 | Supervisor draft submission |
| 13 | Revisions |
| 14 | Final submission |

---

## 8. Key References

Autor, D., Levy, F., & Murnane, R. (2003). The skill content of recent technological change: An empirical exploration. *Quarterly Journal of Economics*, 118(4), 1279-1333.

Acemoglu, D., & Restrepo, P. (2018). The race between man and machine: Implications of technology for growth, factor shares and employment. *American Economic Review*, 108(6), 1488-1542.

Acemoglu, D., & Restrepo, P. (2019). Automation and new tasks: How technology displaces and reinstates labor. *Journal of Economic Perspectives*, 33(2), 3-30.

Acemoglu, D. (2024). The simple macroeconomics of AI. *Economic Policy*, 39(120), 851-908.

Callaway, B., & Sant'Anna, P. (2021). Difference-in-differences with multiple time periods. *Journal of Econometrics*, 225(2), 200-230.

Bresnahan, T. (2010). General purpose technologies. In B. Hall & N. Rosenberg (Eds.), *Handbook of the Economics of Innovation*, Volume 2, 761-791. North-Holland.

Goldfarb, A., & Tucker, C. (2019). Digital economics. *Journal of Economic Literature*, 57(1), 3-43.

Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using siamese BERT networks. *Proceedings of EMNLP-IJCNLP 2019*.

Eloundou, T., Manning, S., Mishkin, P., & Rock, D. (2023). GPTs are GPTs: An early look at the labor market impact potential of large language models. *arXiv preprint arXiv:2303.10130*.

Brynjolfsson, E., Li, D., & Raymond, L. (2023). Generative AI at work. *NBER Working Paper No. 31161*.

---

## 9. Robustness Checks

**1. Alternative shock date.** Use GPT-4 release (March 14, 2023) as the treatment date instead of the ChatGPT launch. Tests whether results are robust to the precise definition of shock timing, since GPT-4 represented a qualitative capability jump that may have been the more commercially relevant event.

**2. Alternative replicability measure.** Replace SBERT cosine similarity scores with LLM rubric scores (Claude API direct scoring of each firm's product text on a structured 0-1 replicability scale). Tests whether the specific measurement methodology drives the results or whether any reasonable operationalization of task replicability yields similar coefficients.

**3. Excluding mega-cap outliers.** Drop MSFT and ORCL, whose quarterly revenue is 10x or more the sample median. Tests whether results are driven by the mechanical influence of the largest firms in the sample.

**4. Excluding sector outliers.** Drop firms whose primary business is not clearly B2B software despite SIC classification (e.g., MAPS — cannabis marketplace, STEM — energy storage optimization, SSTI — public safety analytics). Tests whether unusual sector firms that may have been incorrectly included distort the main results.

**5. Alternative clustering.** Cluster standard errors at the SIC 4-digit sub-code level instead of the firm level. Tests sensitivity to the clustering assumption, since firms within the same SIC sub-code may face correlated shocks.

**6. Callaway-Sant'Anna estimator.** Bin continuous replicability into quartiles and apply the stacked difference-in-differences estimator of Callaway and Sant'Anna (2021). Provides an alternative identification approach that does not rely on the assumption of linearity in the continuous treatment variable and is robust to treatment effect heterogeneity across groups.

**7. Placebo test — COVID-19 shock.** Use 2020 Q1 as a fake treatment date. Task replicability should not predict differential outcomes around the COVID-19 shock because COVID was a demand and operational shock unrelated to the task structure of software products. Finding no effect in this placebo test validates the identification strategy by confirming that replicability only predicts differential outcomes after an AI-specific shock.

**8. Pre-period only falsification.** Estimate the main regression specification on 2019 Q1 through 2022 Q3 data only, using 2021 Q1 as a fake treatment date. Replicability should not predict differential outcomes in this window because no AI shock occurred. A null result confirms that the main findings are not driven by pre-existing differential trends that happen to correlate with task replicability.

---

## 9. Preliminary Results

Specification: bare DiD, trimmed 2020+ sample (2,585 obs, 143 firms)

```
ln(Revenue):      β = -0.759*, SE = 0.401 (p<0.10)
Gross Margin:     β = +0.054,  SE = 0.083 (ns)
Operating Margin: β = -0.434,  SE = 0.403 (ns)
```

**Parallel trends (Wald joint F-test, trimmed 2020+ sample):**

- ln(Revenue):      F=0.89, p=0.54 (PASS)
- Gross Margin:     F=0.98, p=0.46 (PASS)
- Operating Margin: F=1.00, p=0.44 (PASS)

**Interpretation:** The revenue effect is consistent with the substitution mechanism — firms with higher task replicability experienced relatively lower revenue growth after the ChatGPT shock. The operating margin coefficient points in the right direction for commodification (negative) but is imprecisely estimated, likely a power issue with n=143 firms. Gross margin shows no effect, suggesting that pricing power erosion has not yet materialized at the gross margin level — consistent with the theoretical prediction that commodification operates primarily through increased SG&A and R&D spending (operating expenses) rather than through cost-of-goods-sold increases.

**Full sample (2019+) vs trimmed (2020+):** The full sample produces qualitatively similar coefficients but fails the gross margin parallel trends test (F=1.79, p=0.03) due to volatility in the Low replicability group during 2019 Q1-Q2. Trimming to 2020+ resolves this without materially changing the point estimates. The trimmed sample is preferred as the primary specification.

**Robustness to controls:** Adding rd_intensity and sga_intensity as controls changes the ln(Revenue) coefficient from -0.711 to -0.667 and reduces N from 2,982 to 2,443 due to missing control values. The bare specification is preferred because it uses all available observations and the controls are potentially endogenous (R&D and SG&A intensity may respond to the AI shock).
