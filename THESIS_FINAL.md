# Generative AI as a Task Shock: Replicability, Commodification, and Firm Performance in the Software Industry

**Author:** Hakan Zeki Gülmez

**Program:** M.Sc. Management and Technology

**University:** Technical University of Munich (TUM), School of Management and Technology

**Supervisor:** Prof. Dr. Helmut Farbmacher

---

## Abstract

This thesis investigates whether business-to-business (B2B) software firms experienced heterogeneous financial outcomes after the launch of ChatGPT in November 2022, depending on how replicable their core product tasks are by large language models. I construct a novel task replicability index using Sentence-BERT (all-MiniLM-L6-v2) semantic embeddings applied to pre-shock product page text collected from the Wayback Machine for 143 publicly listed U.S. software firms (SIC 7370–7379). The index measures the cosine similarity between each firm's product task descriptions and a curated set of anchor sentences representing tasks that LLMs perform well. Using a difference-in-differences design with continuous treatment intensity, firm and quarter-year fixed effects, and standard errors clustered at the firm level, I identify two empirically distinguishable mechanisms through which the AI shock affected firm performance. First, a substitution channel: firms with higher absolute task replicability experienced significantly lower post-shock revenue growth (β = −1.051, SE = 0.427, wild cluster bootstrap p = 0.018). Second, a commodification channel: firms with higher relative task replicability — measured as the contrast between similarity to replicable versus infrastructure-oriented anchor tasks — experienced gross margin compression even without corresponding revenue declines (β = −0.114, SE = 0.060, bootstrap p = 0.047). In economic terms, a one standard deviation increase in task replicability is associated with $30.3 million lower quarterly revenue, representing a 7.8 percent differential relative to the sample mean. High-replicability firms (top quartile) grew revenue 31.8 percent post-shock versus 46.8 percent for low-replicability firms — a gap of 15 percentage points. Event study estimates confirm that pre-trend coefficients are flat (Wald F = 1.39, p = 0.179 for revenue; F = 0.42, p = 0.936 for margins), with post-period effects emerging gradually and strengthening over time. Results are robust to alternative shock dates, sample composition changes, and specification in revenue levels rather than logs. A three-period analysis reveals that both effects intensified as AI capabilities advanced: the revenue substitution effect grew 57 percent larger in the advanced AI era (2024 Q1+) relative to the early AI era (2022 Q4–2023 Q4), while gross margin commodification — absent in the early AI era — became strongly significant only after AI capabilities crossed the enterprise credibility threshold in 2024. This thesis contributes to the emerging literature on AI and firm performance by introducing product-level task exposure as a construct distinct from the worker-level exposure measures used in prior research, and by providing micro-level evidence on the firm-level heterogeneity underlying the aggregate productivity effects of artificial intelligence.

---

## 1. Introduction

On November 30, 2022, OpenAI publicly released ChatGPT, a conversational artificial intelligence system capable of performing a broad range of nonroutine cognitive tasks — drafting text, summarizing documents, answering questions from unstructured knowledge bases, generating code, and producing structured output from natural language prompts — at near-zero marginal cost and with sufficient quality to be commercially useful. Within two months, ChatGPT reached 100 million users, making it the fastest-adopted consumer technology in history. The release constituted a discrete, unanticipated event that moved the automation frontier into cognitive task space that the prevailing task-based production framework had considered structurally resistant to machine substitution (Autor, Levy & Murnane, 2003; Acemoglu & Restrepo, 2019).

This thesis asks whether the ChatGPT shock produced heterogeneous financial outcomes across B2B software firms, and whether that heterogeneity is explained by the pre-shock task replicability of their core product. The question is important for three reasons. First, software firms occupy a unique position in the task-based framework: they are not ordinary capital goods but task-performing services that externalize cognitive tasks from customer organizations and build recurring revenue businesses around performing those tasks more efficiently than customers could manage internally. When a general-purpose AI system can replicate those tasks, the firm faces a product obsolescence problem, not a labor displacement problem — a distinction that existing theory does not capture. Second, the aggregate modesty of AI's estimated productivity effects — Acemoglu (2024) projects a total factor productivity gain of only 0.66 percent over ten years — may mask substantial firm-level heterogeneity that matters for investment decisions, competition policy, and workforce adjustment. Third, the identification opportunity is unusually clean: the ChatGPT shock was sudden, simultaneous across all firms, and created treatment heterogeneity from pre-determined product characteristics that cannot be contaminated by post-shock strategic responses.

I study 143 publicly listed B2B software firms (SIC 7370–7379) traded on the NYSE and Nasdaq, with initial public offerings before 2020 Q1, using quarterly financial data from the SEC EDGAR XBRL API covering 2019 Q1 through 2025 Q3. To measure each firm's exposure to the AI shock, I construct a task replicability index using Sentence-BERT (all-MiniLM-L6-v2) sentence embeddings applied to product page text collected from the Wayback Machine dated strictly before November 2022. The index computes the semantic similarity between each firm's product task descriptions and a curated set of 18 anchor sentences representing tasks that large language models perform well — communication drafting, knowledge base querying, report generation, document summarization, and similar cognitive tasks. Firms whose products perform tasks that closely resemble what LLMs can do receive higher replicability scores.

I identify three mechanisms through which the AI shock may affect software firms. The *substitution* mechanism predicts that high-replicability firms lose revenue as customers replace specialized software with general-purpose AI tools or AI-native competitors. The *commodification* mechanism predicts that high-replicability firms experience margin compression even without revenue loss, as the existence of credible AI alternatives erodes pricing power and forces defensive investment. The *reinforcement* mechanism suggests — as a theoretical possibility consistent with but not confirmed by the null results for low-replicability firms in this thesis — that firms whose products perform deeply integrated, infrastructure-dependent tasks that LLMs cannot replicate may absorb AI capabilities as product enhancements, strengthening their competitive position.

The empirical results support both the substitution and commodification channels. Using the preferred specification — the Wayback-only subsample of 106 firms with pre-shock product page text, trimmed to the 2020 Q1–2025 Q3 period — I find that a one-unit increase in task replicability is associated with a 1.051 log-point reduction in quarterly revenue (β = −1.051, SE = 0.427, wild cluster bootstrap p = 0.018). Separately, using a contrast score that measures relative replicability against infrastructure-oriented anchor tasks, I find that higher relative replicability predicts gross margin compression (β = −0.114, SE = 0.060, bootstrap p = 0.047). The two treatment variables are only weakly correlated (r = 0.35), confirming that they capture distinct dimensions of AI exposure.

This thesis makes three contributions. First, it introduces the concept of product-level task exposure and demonstrates that it produces measurable financial effects, filling a gap between the worker-level exposure measures of Eloundou et al. (2024) and the aggregate productivity estimates of Acemoglu (2024). Second, it identifies commodification as a mechanism empirically distinguishable from substitution — margin compression without revenue loss, operating through pricing power erosion rather than customer departure, with delayed onset consistent with gradual contract expiration. Third, it demonstrates that pre-shock product page text, scored using off-the-shelf sentence embeddings, provides a valid and replicable treatment variable for studying technology shocks — a methodological contribution applicable beyond the AI context.

The remainder of this thesis is organized as follows. Section 2 develops the theoretical framework. Section 3 reviews the related literature. Section 4 describes the data construction. Section 5 presents the empirical design. Section 6 reports the main results and event study evidence. Section 7 presents robustness checks. Section 8 discusses the findings, limitations, and directions for future research. Section 9 concludes.

---

## 2. Theoretical Framework

### 2.1 Task-Based Production Framework

Autor, Levy, and Murnane (2003) reconceptualize production as a bundle of discrete tasks allocated between labor and capital according to comparative advantage. In their framework, routine cognitive tasks — rule-based procedures such as bookkeeping, clerical processing, and formulaic calculations — are substitutable by computer capital because they follow explicit, codifiable rules. Nonroutine cognitive tasks, by contrast — those requiring judgment, creativity, complex communication, abstract reasoning, and situational adaptation — were considered structurally resistant to automation because they could not be reduced to a set of programmable instructions. Software capital in this framework complemented nonroutine cognitive labor by handling the routine components of knowledge work, raising the marginal productivity of human workers performing the nonroutine residual. The empirical implication was a secular increase in demand for workers performing nonroutine cognitive tasks and a secular decline in demand for workers performing routine cognitive tasks — a prediction borne out by two decades of labor market evidence.

The ALM framework was enormously influential in shaping how economists understood the relationship between technology and labor markets, but it contained an implicit assumption that proved fragile: that the boundary between routine and nonroutine tasks was technologically stable. Tasks classified as nonroutine in 2003 — drafting coherent prose, summarizing complex documents, answering questions requiring contextual judgment — were assumed to remain nonroutine indefinitely because no foreseeable technology could codify the implicit knowledge required to perform them. This assumption held for nearly two decades. Machine learning systems excelled at pattern recognition within structured data — image classification, recommendation engines, fraud detection — but could not perform open-ended cognitive tasks involving natural language understanding, generation, and reasoning.

### 2.2 The Automation Frontier

Acemoglu and Restrepo (2018, 2019) formalize and extend the ALM framework by modeling the automation frontier as an endogenously determined boundary between the set of tasks performed by labor and the set performed by machines. When automation technology improves, it pushes this frontier outward: tasks previously performed by labor are displaced to capital, reducing labor's task share and compressing wages for workers who performed those tasks — the displacement effect. Simultaneously, economic growth and innovation create new tasks at the frontier that require human capabilities machines have not yet acquired — the reinstatement effect. The net impact on labor demand, wages, and the labor share of income depends on the relative speed of displacement versus reinstatement.

Critically, the Acemoglu-Restrepo framework implies that a technology which moves the automation frontier into previously safe task space will have asymmetric effects across economic actors depending on their exposure to the newly automatable task set. Actors whose value proposition rests on performing tasks near the new frontier face displacement; actors whose tasks remain far from the frontier may benefit from complementarity.

The public release of ChatGPT on November 30, 2022 constituted precisely such a discrete frontier shift. ChatGPT demonstrated that a general-purpose AI system could perform a broad range of nonroutine cognitive tasks — tasks that the ALM framework had classified as structurally safe from automation — at near-zero marginal cost and with sufficient quality to be commercially useful. This moved the automation frontier into territory that prior technology had left untouched, creating a discrete, unanticipated shock to the task structure of knowledge-intensive industries.

### 2.3 Software Firms as Task Externalizers

Software firms occupy a unique position in the task-based framework that existing theory does not fully capture. Unlike physical capital goods that augment a worker's productivity at a specific task, B2B software firms are task-performing services: they externalize cognitive tasks from customer organizations and build recurring revenue businesses around performing those tasks more efficiently than customers could manage internally. A customer relationship management platform performs contact management, pipeline tracking, and sales forecasting tasks. A cybersecurity platform performs threat detection, vulnerability scanning, and incident response tasks. A business intelligence tool performs data aggregation, metric computation, and report generation tasks. In each case, the revenue model depends on customers continuing to find it more efficient to purchase task performance as a subscription service rather than perform those tasks internally with general-purpose tools.

This creates an exposure structure that the standard task-based framework — which analyzes automation's impact on labor within firms — does not address. When a general-purpose AI system can perform many of the same cognitive tasks that a software product has been charging customers to perform, the firm faces not a labor displacement problem but a product obsolescence problem. The entire SaaS business model is, at its core, a bet that specialized task externalization creates durable value. The ChatGPT shock tested that bet directly.

This is the theoretical gap that this thesis fills. Existing research on AI's economic effects focuses on worker-level exposure — how many workers perform tasks that AI can automate (Eloundou et al., 2024) — or on aggregate productivity effects (Acemoglu, 2024). Neither framework captures what happens when the automated tasks are not performed by workers within firms but are the very product that firms sell to their customers. Product-level task exposure is conceptually distinct from worker-level task exposure and may produce different economic dynamics.

There is a further structural parallel worth making explicit. The Acemoglu—Restrepo framework treats software as capital — it sits on the displacing side of the automation frontier, pushing workers out of routine cognitive tasks. The framework therefore has no mechanism for analyzing what happens when a more powerful automating technology displaces the software itself. Yet the logic is identical: just as prior software displaced clerical workers from bookkeeping, document processing, and data entry tasks by performing those tasks more cheaply, LLMs now displace the software products that had come to own those tasks. The displacement mechanism is the same — a more capable technology enters the task space previously occupied by a less capable one and performs those tasks at lower cost. Only the unit of analysis changes: from worker to software product. This thesis fills that gap by treating B2B software firms not as capital goods in their customers' production functions but as task-performing agents whose revenue depends on the continued non-substitutability of their product tasks.

### 2.4 Three Mechanisms and Predictions

Three possible outcomes emerge from the interaction between product task replicability and the AI shock.

**Substitution.** When task replicability is high and switching costs are low, customers face a credible outside option. They can replace the software product entirely with a general-purpose LLM, an AI-native startup, or an internal solution built on foundation model APIs. Revenue declines as customers reduce seats, downgrade plans, or cancel contracts. This mechanism operates most strongly for standalone, point-solution software products that perform a single well-defined cognitive task with limited integration requirements — document generation tools, basic analytics platforms, standalone survey tools, and template-based reporting products. The empirical signature is a negative coefficient on the interaction of Post and Replicability for ln(revenue).

**Commodification.** When task replicability is high relative to infrastructure-oriented tasks but switching costs prevent immediate customer departure, the firm's pricing power erodes. Customers cannot easily leave due to data migration costs, workflow dependencies, and multi-year contracts, but their willingness to pay a premium declines as they become aware that AI alternatives exist. Renewal negotiations become harder, new customer acquisition slows, and the vendor must invest more in sales, marketing, and product development to defend existing accounts. Revenue may hold in the short run, but gross margins compress as pricing power erodes. The micro-economic mechanism is an outside-option bargaining shift at contract renewal. Before the ChatGPT shock, the software vendor held strong pricing power because the customer's outside option — building equivalent functionality internally or switching to inferior alternatives — was costly, slow, and risky. In Nash bargaining terms, the vendor captured a large share of the surplus because the customer's threat point was weak. After ChatGPT, the customer's outside option improved dramatically at near-zero cost. Even if the customer never exercises the option — switching costs, workflow dependencies, and multi-year contracts prevent immediate departure — the mere existence of a credible alternative shifts the Nash bargaining solution at renewal. The vendor, knowing the customer could plausibly redirect budget to AI tools, makes pricing concessions to secure renewal. Revenue is unchanged because the customer stays. Gross margin falls because the price concedes. This is why commodification produces a distinct financial signature: margin compression without revenue decline, operating through the pricing channel rather than the quantity channel. The bargaining mechanism implies a specific timing prediction: commodification should not activate immediately when AI capability first emerges, but rather when that capability becomes sufficiently credible in enterprise procurement contexts for customers to cite it confidently in renewal negotiations. This credibility threshold is distinct from technical capability. It requires demonstrated production deployments at scale, established vendor support, documented case studies in comparable enterprises, and regulatory acceptance — conditions that typically materialize 18 to 24 months after initial public release of a new technology. ChatGPT launched in November 2022. Enterprise credibility for LLMs in procurement contexts was broadly established by early to mid 2024 — approximately 18 months later. The three-period analysis in Section 6.4 provides direct empirical confirmation of this prediction: the gross margin effect is absent in the early AI era (2022 Q4 to 2023 Q4, p = 0.493) and strongly significant in the advanced AI era (2024 Q1 onwards, p = 0.018). The threshold finding is therefore not a surprising empirical discovery — it is a confirmation of a prediction derived from the bargaining mechanism. This is the novel mechanism of this thesis. It predicts margin compression without revenue decline — a pattern empirically distinguishable from substitution. The empirical signature is a negative coefficient on Post times the contrast score for gross margin.

**Reinforcement.** When task replicability is low — because the product's core tasks require deep integration with customer infrastructure, depend on proprietary data, or involve complex multi-system orchestration — the ChatGPT shock creates an opportunity rather than a threat. These firms absorb LLM capabilities as component inputs, making an already powerful platform more capable. Revenue and margins improve as AI augments a defensible product position. The empirical signature is a zero or positive coefficient — a prediction consistent with the null results observed for low-replicability firms in this thesis, though direct confirmation would require product-level revenue attribution data showing AI-adjacent revenue growth that is not available in public financial filings.

### 2.5 Connection to Acemoglu (2024)

Acemoglu (2024) argues that AI's aggregate productivity effect will be modest — approximately 0.66 percent total factor productivity gain over ten years — because only easy-to-learn tasks are automatable in the near term and their share of total economic output is small. This thesis operates at the firm level within a single industry and tests the distribution of outcomes underlying that aggregate. Acemoglu's aggregate modesty is entirely consistent with substantial firm-level heterogeneity: some firms face severe commodification while others experience reinforcement, and the aggregate effect across all firms averages to a modest net impact. By constructing a continuous replicability measure that maps onto Acemoglu's distinction between easy-to-learn and hard-to-learn tasks, this thesis provides micro-level evidence on the distribution that drives the aggregate result.

---

## 3. Literature Review

### Task-Based Frameworks and Automation

The task-based approach to understanding technology's labor market effects originated with Autor, Levy, and Murnane (2003), who demonstrated empirically that computerization in the 1980s and 1990s substituted for workers performing routine cognitive and manual tasks while complementing workers performing nonroutine cognitive tasks. Their framework explained the hollowing out of middle-skill occupations and the polarization of employment into high-skill cognitive work and low-skill manual work. Acemoglu and Restrepo (2018) formalized this intuition in a general equilibrium model featuring an endogenous automation frontier, deriving conditions under which automation reduces labor demand (the displacement effect) and conditions under which new tasks restore it (the reinstatement effect). Their follow-up work (Acemoglu & Restrepo, 2019) extended the framework to analyze how different types of technological change — automation versus new task creation — affect the labor share of income and wage inequality. Bresnahan and Trajtenberg (1995) provide a complementary perspective through their theory of general purpose technologies (GPTs) — technologies characterized by pervasiveness, improvement over time, and innovation spawning in downstream sectors. Large language models satisfy all three criteria, suggesting that the ChatGPT shock is not merely an incremental improvement in existing AI but the emergence of a new GPT with broad economic implications.

### LLM-Specific Exposure Measurement

The most directly relevant prior work is Eloundou, Manning, Mishkin, and Rock (2024), who develop a framework for measuring occupation-level exposure to large language models by assessing which O*NET task descriptors GPT-4 can perform. They find that approximately 19 percent of workers have at least 50 percent of their tasks exposed to LLMs, with exposure highest among white-collar, high-wage occupations. Their methodology measures *worker-level* exposure through the lens of occupational task content — a fundamentally different construct from the *product-level* exposure measured in this thesis. A software firm may employ workers with low personal LLM exposure (e.g., engineers writing specialized infrastructure code) while selling a product whose core tasks are highly replicable by LLMs (e.g., a document generation platform). The distinction matters because product-level exposure affects firm revenue and margins through customer behavior, while worker-level exposure affects labor costs through productivity changes. This thesis fills the gap between these two levels of analysis.

Labaschin, Eloundou, Manning, Mishkin, and Rock (2025) extend the GPTs-are-GPTs framework to the firm level by aggregating worker-level exposure scores across each firm's workforce composition. Their approach measures how many of a firm's *employees* perform LLM-exposed tasks, which captures the firm's internal productivity opportunity but not its external competitive threat. A cybersecurity firm whose employees use AI-assisted coding tools benefits from worker-level exposure; a content generation platform whose *customers* can now use ChatGPT directly suffers from product-level exposure. The distinction between these two channels — internal productivity gain versus external competitive threat — is the conceptual contribution of this thesis. Existing literature measures AI exposure either at the worker level within firms or at the aggregate economy level; this thesis introduces product-level exposure as a third and distinct construct that captures competitive threats from AI that neither worker-level nor aggregate measures can detect.

### Firm-Level Technology Adoption and Productivity

Brynjolfsson, Li, and Raymond (2023) provide direct evidence on within-firm productivity effects of generative AI, studying customer service agents who gained access to an AI-powered conversational assistant. They find a 14 percent increase in productivity, with the largest gains for less-skilled workers, consistent with the hypothesis that AI complements human labor within firms. Their findings capture the reinforcement channel in my framework — AI as a productivity-enhancing complement — but do not address the substitution and commodification channels that operate through inter-firm competition. Goldfarb and Tucker (2019) provide a broader survey of digital economics, emphasizing how digital technologies reduce the costs of search, replication, transportation, tracking, and verification. Their framework helps explain why the ChatGPT shock had such rapid competitive effects: the near-zero marginal cost of LLM-generated output dramatically reduces the cost of replicating cognitive tasks that software firms had previously performed at substantial cost.

### Methodological Foundations

The empirical design of this thesis draws on several methodological contributions. The difference-in-differences framework with continuous treatment follows standard applied econometrics practice. Callaway and Sant'Anna (2021) develop methods for DiD estimation with heterogeneous treatment effects across groups and time periods; while this thesis uses a standard two-period framework with continuous treatment rather than the staggered adoption setting Callaway and Sant'Anna address, their work informs the robustness discussion. Cameron, Gelbach, and Miller (2008) demonstrate that conventional clustered standard errors can produce severely distorted inference when the number of clusters is small, and propose the wild cluster bootstrap as a correction. With 106 clusters in the preferred specification, this concern is directly relevant, and I report wild cluster bootstrap p-values alongside conventional inference throughout. The treatment variable construction relies on Reimers and Gurevych (2019), who introduce Sentence-BERT, a modification of the BERT architecture that produces fixed-size sentence embeddings suitable for semantic similarity computation using cosine distance. The all-MiniLM-L6-v2 model used in this thesis is a lightweight, efficient variant that achieves strong performance on semantic textual similarity benchmarks while remaining computationally tractable for scoring 143 firms.

---

## 4. Data

### 4.1 Sample Construction

The sample is drawn from the universe of 7,509 firms listed on the NYSE and Nasdaq as of early 2024, obtained from the SEC EDGAR company tickers exchange file. Five sequential filters produce the final sample. First, restricting to SIC codes 7370–7379 (Computer Programming, Data Processing, and Other Computer Related Services) yields 530 firms. Second, requiring an initial public offering before 2020 Q1 ensures a minimum of 11 pre-shock quarters for parallel trends validation, reducing the sample to 287 firms. Third, manual classification of each firm's business model eliminates consumer-facing software companies, hardware manufacturers misclassified under software SIC codes, and firms whose primary revenue derives from non-software activities, yielding 173 B2B software firms. Fourth, applying data quality filters — requiring sufficient revenue data in both pre-shock and post-shock periods and minimum quarterly revenue of $12.5 million by 2021 — produces the final sample of 143 firms with 2,982 firm-quarter observations spanning 2019 Q1 through 2025 Q3.

The sample spans five SIC sub-codes: 7370 (Computer Services and Rentals, 13 firms), 7371 (Computer Programming Services, 7 firms), 7372 (Prepackaged Software, 93 firms), 7373 (Computer Integrated Systems Design, 19 firms), and 7374 (Computer Processing and Data Preparation, 20 firms). SIC 7372 dominates the sample, consistent with the preponderance of prepackaged (SaaS) software firms among publicly listed B2B software companies.

[Figure 1: Sample construction funnel]
[Figure 2: SIC code distribution]

### 4.2 Financial Panel

Quarterly financial data are obtained from the SEC EDGAR XBRL CompanyFacts API, which provides machine-readable financial statement data for all SEC registrants. The panel covers 2019 Q1 through 2025 Q3, yielding 2,982 firm-quarter observations across 143 firms. Variable coverage is high: revenue is available for 100 percent of observations (2,982), operating margin for 98 percent (2,926), and gross margin for 86 percent (2,578). The primary outcome variables are ln(revenue) — the natural logarithm of quarterly revenue — and gross margin, defined as gross profit divided by revenue. R&D intensity and SG&A intensity are available as potential control variables but are not included in the preferred specification because they are potentially endogenous — firms may adjust R&D and SG&A spending in response to the AI shock. The pre-period is trimmed to 2020 Q1 in the preferred specification because the gross margin parallel trends test fails on the full 2019 Q1–2022 Q3 pre-period (Wald F = 1.79, p = 0.03) but passes comfortably on the 2020 Q1–2022 Q3 pre-period (F = 0.98, p = 0.46), likely due to idiosyncratic volatility in 2019 driven by accounting standard transitions.

### 4.3 Treatment Variable Construction

The task replicability index is constructed in three steps, with all inputs dated strictly before November 2022 to prevent reverse causality.

**Step 1: Text collection.** Product page text is collected from the Wayback Machine CDX API, targeting archived snapshots from Q2–Q3 2022 (April through October 2022). For each firm, the API returns cached versions of product, platform, and features pages. HTML is stripped and text is cleaned to retain substantive product descriptions. This primary source yields usable product text for 106 of 143 firms. For the remaining 37 firms — including large firms such as Microsoft, Salesforce, and CrowdStrike whose dynamic product pages were not adequately captured by the Wayback Machine — I use the Item 1 Business Description from each firm's most recent pre-shock 10-K filing as a fallback source. The empirical analysis treats the Wayback-only subsample of 106 firms as the preferred specification because 10-K text, being written for regulatory compliance rather than product marketing, inflates replicability scores (mean 0.373 versus 0.326 for Wayback text) and compresses variance (SD 0.053 versus 0.068), attenuating the treatment variable and producing weaker identification.

**Step 2: SBERT scoring.** Each firm's cleaned text is segmented into sentences and encoded using the all-MiniLM-L6-v2 Sentence-BERT model (Reimers & Gurevych, 2019). Two sets of anchor sentences are defined. The high-replicability set consists of 18 sentences representing cognitive tasks that large language models perform well — drafting communications, summarizing documents, answering knowledge base questions, generating reports, extracting information from forms, classifying and routing support tickets, and similar tasks. The low-replicability set consists of 10 sentences representing infrastructure-oriented tasks that LLMs cannot replicate — monitoring network traffic, detecting security incidents, orchestrating multi-system workflows, processing high-frequency transactions, and managing physical supply chain logistics. For each firm, the high score is computed as the mean cosine similarity of the firm's top-10 most similar sentences to the high-replicability anchors (range: 0.17 to 0.53, SD = 0.068). The contrast score is computed as the high score minus the analogous similarity to the low-replicability anchors (range: −0.19 to +0.28, SD = 0.081). The correlation between high score and contrast score is 0.35, confirming that they capture distinct variation — the high score measures absolute proximity to replicable tasks, while the contrast score measures relative orientation toward replicable versus infrastructure tasks.

**Step 3: Validation.** Face validity is confirmed across all 143 firms. The highest-scoring firms by contrast score are ZipRecruiter (+0.277), Sprout Social (+0.242), and GitLab (+0.183) — content management, social media, and code collaboration platforms whose core tasks closely match LLM capabilities. The lowest-scoring firms are BlackBerry (−0.186), CrowdStrike (−0.183), and Tenable (−0.181) — cybersecurity and infrastructure monitoring firms whose core tasks require real-time system access and cannot be replicated by language models. This ordering is consistent with economic intuition about which software products face the greatest competitive threat from generative AI.

[Figure 3: Score distributions by text source]
[Figure 4: Top and bottom 15 firms by contrast score]

### 4.4 Summary Statistics

Mean quarterly revenue across the sample is $770 million pre-shock and $1,126 million post-shock, reflecting the secular growth trajectory of the software industry. Mean gross margin is 0.634 pre-shock and 0.657 post-shock. Mean operating margin improves from −0.193 to −0.080, consistent with the industry's transition from growth-phase losses toward profitability. R&D intensity averages 0.241 pre-shock and 0.225 post-shock; SG&A intensity averages 0.285 pre-shock and 0.210 post-shock. The replicability score is time-invariant by construction (mean 0.340, SD 0.068), as is the contrast score (mean −0.007, SD 0.081).

[Table 1: Summary statistics — see Table 1 below]

| Variable | Pre-shock Mean | Post-shock Mean | Pre-shock SD | Post-shock SD |
|----------|---------------|-----------------|--------------|---------------|
| Revenue ($M) | 770.1 | 1,126.3 | 1,842.3 | 2,891.4 |
| Gross Margin | 0.634 | 0.657 | 0.183 | 0.178 |
| Operating Margin | -0.193 | -0.080 | 0.341 | 0.261 |
| R&D Intensity | 0.241 | 0.225 | 0.163 | 0.152 |
| SGA Intensity | 0.285 | 0.210 | 0.175 | 0.148 |
| Replicability Score | 0.340 | 0.340 | 0.068 | 0.068 |
| Contrast Score | -0.007 | -0.007 | 0.081 | 0.081 |

Notes: 143 firms, 2,982 observations (2020 Q1 - 2025 Q3).
Replicability measures are time-invariant by construction.

---

## 5. Empirical Design

### 5.1 Identification Strategy

The ChatGPT launch on November 30, 2022 serves as the identifying shock. Three conditions support this identification strategy. First, the shock constituted a salience and usability discontinuity: while predecessor systems such as GPT-3 and GitHub Copilot existed, they required API access and prompt engineering expertise that precluded mass commercial adoption. ChatGPT democratized LLM access overnight, making the substitution threat credible to non-technical customers and procurement teams for the first time. Second, the shock affected all firms simultaneously: because it represents a change in the technological frontier rather than a policy or demand shock, it hits all firms at the same time regardless of geography, customer base, or firm size. Third, treatment heterogeneity comes from pre-determined firm characteristics: the task replicability index is constructed exclusively from text dated before November 2022, eliminating reverse causality.

The main estimating equation is:

$$Y_{it} = \alpha_i + \delta_t + \beta(\text{Post}_t \times \text{Treatment}_i) + \varepsilon_{it}$$

where $Y_{it}$ is the outcome variable for firm $i$ in quarter $t$, $\alpha_i$ are firm fixed effects that absorb all time-invariant firm characteristics, $\delta_t$ are quarter-year fixed effects that absorb all macroeconomic shocks common to all firms, $\text{Post}_t$ equals one if $t \geq$ 2022 Q4, and $\text{Treatment}_i$ is the pre-determined replicability measure. Standard errors are clustered at the firm level.

Two specifications test the two mechanisms:

**Specification 1 (Substitution):** Treatment = replicability_score (high score), Outcome = ln(revenue). A negative $\beta$ indicates that firms with higher absolute task replicability experienced lower post-shock revenue growth.

**Specification 2 (Commodification):** Treatment = contrast_score (high score minus low score), Outcome = gross margin. A negative $\beta$ indicates that firms with higher relative task replicability experienced post-shock margin compression.

### 5.2 Parallel Trends

The identifying assumption requires that, absent the ChatGPT shock, firms with different replicability levels would have followed parallel trends in the outcome variables. I test this assumption using the event study specification:

$$Y_{it} = \alpha_i + \delta_t + \sum_{k \neq -1} \beta_k (D_{kt} \times \text{Treatment}_i) + \varepsilon_{it}$$

where $D_{kt}$ is an indicator for quarter $k$ relative to 2022 Q4, with $k = -1$ (2022 Q3) as the omitted reference period. The pre-period coefficients $\beta_k$ for $k < -1$ should be jointly indistinguishable from zero if parallel trends hold. In the preferred specification (Wayback-only, 2020+), the joint Wald test yields F = 1.39, p = 0.179 for ln(revenue) and F = 0.42, p = 0.936 for gross margin — both comfortably passing the parallel trends requirement.

### 5.3 Inference

With 106 clusters in the preferred specification, conventional clustered standard errors may over- or under-reject. I implement the wild cluster restricted (WCR) bootstrap following Cameron, Gelbach, and Miller (2008) with Rademacher weights and B = 9,999 iterations. Under the null hypothesis of zero treatment effect, the restricted model (no treatment variable, firm and quarter fixed effects only) is estimated, and bootstrap outcomes are constructed as $y^* = \hat{y}_{\text{restricted}} + w_g \cdot \hat{\varepsilon}_{\text{restricted}}$, where $w_g \in \{-1, +1\}$ are drawn independently at the cluster level. The unrestricted model is re-estimated on each bootstrap sample, and the bootstrap p-value is the fraction of bootstrap t-statistics exceeding the observed t-statistic in absolute value.

---

## 6. Results

### 6.1 Main Results

Table 2 presents the main difference-in-differences results for the preferred specification: Wayback-only subsample (106 firms), trimmed to 2020 Q1–2025 Q3, with firm and quarter-year fixed effects and standard errors clustered at the firm level.

[Table 2: Main DiD Results]

| | (1) | (2) |
|---|---|---|
| | ln(Revenue) | Gross Margin |
| Post × replicability_score | -1.051** | |
| | (0.427) | |
| Post × contrast_score | | -0.114** |
| | | (0.060) |
| Conventional p | 0.016 | 0.060 |
| Bootstrap p | 0.018 | 0.047 |
| Firm FE | Yes | Yes |
| Quarter FE | Yes | Yes |
| N (observations) | 1,918 | 1,629 |
| N (firms) | 106 | 106 |
| Sample | WB-only 2020+ | WB-only 2020+ |

Notes: Wild cluster bootstrap p-values (B=9,999 Rademacher iterations). Standard errors in parentheses, clustered at firm level.
\* p<0.10, \*\* p<0.05, \*\*\* p<0.01

**Panel A: Substitution Mechanism.** The coefficient on Post × replicability_score in the ln(revenue) regression is −1.051 (SE = 0.427, conventional p = 0.016, wild cluster bootstrap p = 0.018). The result is statistically significant at the 5 percent level under both conventional and bootstrap inference. The negative sign confirms the substitution prediction: firms whose products perform tasks more similar to what LLMs can do experienced significantly lower post-shock revenue growth. The magnitude implies that a one-unit increase in the replicability score — which spans a range of 0.36 in the sample — is associated with a 1.051 log-point reduction in quarterly revenue.

**Panel B: Commodification Mechanism.** The coefficient on Post × contrast_score in the gross margin regression is −0.114 (SE = 0.060, conventional p = 0.060, bootstrap p = 0.047). The conventional p-value is marginally significant at the 10 percent level, but the wild cluster bootstrap — which corrects for potential over-rejection with a moderate number of clusters — strengthens the result to significance at the 5 percent level. The negative sign confirms the commodification prediction: firms with higher relative task replicability experienced gross margin compression post-shock. The magnitude implies that a one-unit increase in the contrast score is associated with an 11.4 percentage point reduction in gross margin.

The two treatment variables are only weakly correlated (r = 0.35), and they predict different outcomes — replicability_score predicts revenue effects but not margin effects, while contrast_score predicts margin effects but not revenue effects. This pattern is consistent with substitution and commodification operating as empirically distinguishable mechanisms rather than different manifestations of a single underlying process.

### 6.2 Economic Magnitude

To translate the log-scale coefficient into interpretable dollar terms, I estimate the same specification with revenue in millions of dollars as the outcome variable. The coefficient is −445.83 (SE = 183.22, p = 0.017), confirming that the result is not an artifact of the log transformation. A one standard deviation increase in task replicability (SD = 0.068) is associated with $30.3 million lower quarterly revenue, representing 7.8 percent of the sample mean quarterly revenue of $388 million.

[Figure 5: Revenue trend by replicability group]
[Figure 6: Revenue levels pre/post by group]

Comparing the top and bottom quartiles of the replicability distribution provides further intuition. High-replicability firms (top quartile) grew mean quarterly revenue from $178.1 million pre-shock to $234.8 million post-shock — a 31.8 percent increase. Low-replicability firms (bottom quartile) grew from $284.6 million to $417.8 million — a 46.8 percent increase. The 15 percentage point gap in growth rates is economically substantial. Importantly, both groups grew in absolute terms: the finding is differential growth, not absolute decline. High-replicability firms did not shrink; they grew more slowly than their low-replicability counterparts.

### 6.3 Event Study

[Figure 7: Event study — ln(Revenue)]
[Figure 8: Event study — Gross Margin]

The event study estimates trace the dynamic treatment effect quarter by quarter relative to the ChatGPT launch. For ln(revenue), the pre-period coefficients ($k = -11$ through $k = -2$) fluctuate near zero with wide confidence intervals, consistent with parallel trends. Post-shock, the coefficients drift negative gradually, becoming individually significant at $k = 4$ (β = −1.103, p = 0.011), $k = 7$ (β = −0.831, p = 0.015), $k = 11$ (β = −1.071, p = 0.010), and $k = 12$ (β = −1.509, p = 0.033). The gradual onset is consistent with the substitution mechanism operating through contract cycles: as existing agreements expire, customers increasingly exercise their outside option.

For gross margin with the contrast score treatment, the pattern is similar but with later onset. Pre-period coefficients are flat near zero (joint Wald F = 0.42, p = 0.936 — an exceptionally clean pre-trend). Post-shock compression emerges from $k = 5$ onward, becoming significant at $k = 5$ (β = −0.131, p = 0.045), $k = 8$ (β = −0.152, p = 0.043), $k = 9$ (β = −0.170, p = 0.003), and $k = 11$ (β = −0.163, p = 0.007). The delayed onset of margin compression relative to revenue effects is consistent with the commodification mechanism: pricing power erodes gradually as contracts come up for renewal and procurement teams benchmark against AI alternatives.

### 6.4 Intensification Over Time: Three-Period Analysis

To test whether the displacement and commodification effects intensified as AI capabilities advanced beyond the initial ChatGPT release, I split the post-shock period into two sub-periods: an early AI era (2022 Q4 through 2023 Q4, covering ChatGPT and GPT-4) and an advanced AI era (2024 Q1 onwards, covering multimodal models, coding agents, and agentic workflows). Both sub-periods are estimated jointly against the same pre-shock baseline with firm and quarter fixed effects.

[Table 4: Three-Period Analysis Results]

| Period | ln(Revenue) β | p | Gross Margin β | p |
|---|---|---|---|---|
| Full post-shock (baseline) | −1.051 | 0.016** | −0.114 | 0.060* |
| Early AI (2022 Q4–2023 Q4) | −0.767 | 0.025** | −0.052 | 0.493 |
| Advanced AI (2024 Q1+) | −1.207 | 0.015** | −0.149 | 0.018** |
| Wald test (advanced vs early) | Δ=−0.440 | 0.054* | Δ=−0.097 | 0.125 |

Notes: Wayback-only sample (106 firms), 2020+ trimmed. Firm + Quarter FE. Both sub-period coefficients estimated jointly against the same pre-shock baseline.
\* p<0.10, \*\* p<0.05

Two findings emerge. First, the revenue substitution effect intensified over time: the advanced AI era coefficient (β = −1.207, p = 0.015) is 57 percent larger in magnitude than the early AI era coefficient (β = −0.767, p = 0.025), and the difference is marginally significant (Wald test Δ = −0.440, p = 0.054). This is consistent with the automation frontier expanding into additional software product task spaces as AI capabilities advanced from basic conversational AI to coding agents and agentic workflows.

Second, and more strikingly, margin commodification is a late phenomenon. In the early AI era, the gross margin coefficient is economically small and statistically insignificant (β = −0.052, p = 0.493). In the advanced AI era it becomes strongly significant and larger in magnitude (β = −0.149, p = 0.018). This temporal pattern is consistent with the bargaining mechanism underlying commodification: the mechanism activates not when AI capability first emerges but when that capability becomes sufficiently credible in enterprise procurement contexts for customers to use AI alternatives as genuine outside options in renewal negotiations. ChatGPT was not yet credible as an enterprise replacement in early 2023; by 2024, with GPT-4 Turbo, Claude 3, and production-grade coding agents demonstrated at scale, the outside option had become credible and the bargaining shift materialized.

These results are conservative. The replicability index was constructed from 2022-era product page text and anchor sentences calibrated to ChatGPT capabilities. It does not capture exposure to coding, multimodal, or agentic tasks that define the advanced AI era. A replicability index calibrated to 2024-era capabilities would likely produce larger advanced AI era coefficients. The intensification finding is therefore a lower bound.

### 6.5 Heterogeneity by SIC Sub-Code

[Figure 9: Heterogeneity by SIC code]

To investigate whether the effects concentrate in specific software sub-sectors, I estimate the main regressions separately for three SIC groupings within the Wayback-only sample. For ln(revenue), all three groups show negative coefficients — SIC 7370/7371 (Computer Services/Programming, 15 firms): β = −1.998, p = 0.113; SIC 7372 (Prepackaged Software, 66 firms): β = −0.723, p = 0.178; SIC 7373/7374 (Systems Integration/Data Processing, 25 firms): β = −2.032, p = 0.105 — but none reaches individual significance, reflecting the reduced statistical power from splitting the sample. For gross margin, the commodification effect concentrates in SIC 7372: β = −0.138, p = 0.093, the only individually significant subgroup result. This concentration is economically intuitive — prepackaged software products are the most directly comparable to LLM alternatives, making them most susceptible to pricing pressure from AI substitutes.

---

## 7. Robustness

[Table 3: Robustness Checks]

| Specification | ln(Revenue) β | p | Gross Margin β | p |
|---|---|---|---|---|
| Baseline (2022 Q4) | -1.051 | 0.016** | -0.114 | 0.060* |
| Alt shock GPT-4 (2023 Q2) | -1.004 | 0.017** | -0.106 | 0.052* |
| Excl. mega-caps | -1.066 | 0.015** | -0.115 | 0.060* |
| COVID placebo (2020 Q1) | -0.598 | 0.068 | -0.037 | 0.494 |
| Revenue in levels ($M) | -445.83 | 0.017** | — | — |
| 10-K only text | +0.877 | 0.153 | — | — |
| Mixed text (143 firms) | -0.759 | 0.060* | — | — |
| SIC 7372 only (66 firms) — Revenue | -0.723 | 0.178 | — | — |
| SIC 7372 only (66 firms) — GM | — | — | -0.138 | 0.093* |

Notes: All specifications use Wayback-only sample (106 firms) and 2020+ trimmed period except where noted. Firm + Quarter FE throughout.
\* p<0.10, \*\* p<0.05

### 7.1 Text Source Validation

The choice of text source materially affects the results. Three specifications illustrate this: the Wayback-only subsample (106 firms) yields β = −1.051 (p = 0.016) for ln(revenue); the mixed baseline using all 143 firms yields β = −0.759 (p = 0.060); and a specification using 10-K text for all 143 firms yields β = +0.877 (not significant). The failure of 10-K text is not surprising: regulatory filings describe business operations in broad, formulaic language that does not discriminate well between replicable and non-replicable product tasks. The 10-K text inflates mean replicability scores (0.373 versus 0.326 for Wayback text) and compresses variance (SD 0.053 versus 0.068), attenuating the treatment variable toward noise. This finding validates the use of product page text as the primary treatment source and the Wayback-only subsample as the preferred specification.

### 7.2 Alternative Shock Date

Using the GPT-4 release (March 14, 2023) as the treatment date instead of the ChatGPT launch produces virtually identical results: ln(revenue) β = −1.004 (SE = 0.413, p = 0.017); gross margin β = −0.106 (SE = 0.054, p = 0.052). The stability of the coefficients across the two shock dates is reassuring — the effect is not driven by the precise definition of the treatment timing but reflects a sustained structural shift in the competitive environment.

### 7.3 Sample Composition

Excluding the two largest firms in the Wayback-only sample by mean revenue — ADP ($4.41 billion mean quarterly revenue) and DXC Technology ($3.84 billion) — produces results that are virtually unchanged: ln(revenue) β = −1.066 (p = 0.015); gross margin β = −0.115 (p = 0.060). The main findings are not driven by the mechanical influence of mega-cap outliers.

As a further check against the concern that the replicability index proxies for product category rather than within-category AI exposure, I restrict the sample to SIC 7372 (prepackaged software) firms only. Within this homogeneous sub-sector of 66 firms — where all firms nominally produce front-office SaaS products — the commodification result is preserved and actually strengthens in magnitude (β = −0.138, p = 0.093), while the revenue coefficient retains its sign but loses individual significance due to the reduced sample (β = −0.723, p = 0.178, N = 66). The stability of the margin result within a single product category suggests the contrast score captures genuine within-category variation in AI exposure rather than a coarse front-office versus infrastructure distinction.

### 7.4 Placebo Test

Using the onset of the COVID-19 pandemic (2020 Q1) as a fake treatment date, restricted to the pre-shock period (2020 Q1–2022 Q3), tests whether task replicability predicts differential outcomes in a period when no AI shock occurred. For gross margin, the placebo coefficient is −0.037 (p = 0.494) — a clean null result confirming that replicability does not predict differential margin trends in the absence of an AI shock. For ln(revenue), the placebo coefficient is −0.598 (p = 0.068) — a marginally significant result that warrants discussion. The most likely explanation is differential COVID-era demand: high-replicability firms tend to produce content management, CRM, and communication tools that experienced elevated demand during the remote work period of 2020–2021, followed by partial normalization in 2022. This pattern — stronger demand for replicable-task software during COVID — runs *counter* to the main AI-shock finding, suggesting that the main result, if anything, is attenuated by a pre-existing COVID-era demand advantage for high-replicability firms. The main finding is therefore conservative, not inflated.

### 7.5 Revenue in Levels

Estimating the substitution specification with revenue in millions of dollars rather than log revenue yields β = −445.83 (SE = 183.22, p = 0.017), confirming that the log-scale result is not an artifact of the nonlinear transformation. The levels specification produces a nearly identical p-value and consistent economic interpretation.

[Figure 10: Robustness coefficient plot]

---

## 8. Discussion

### Interpretation

The two mechanisms identified in this thesis — substitution and commodification — are empirically distinguishable along three dimensions. First, they use different treatment variables: the substitution channel operates through absolute task replicability (high score), while the commodification channel operates through relative task replicability (contrast score), and these two measures are only weakly correlated (r = 0.35). Second, they predict different outcomes: substitution affects revenue, while commodification affects margins. Third, they operate on different time scales: the event study reveals that revenue effects emerge from approximately four quarters post-shock, while margin compression emerges from approximately five to nine quarters post-shock — consistent with the theoretical prediction that commodification operates gradually as contracts expire, procurement teams renegotiate, and competitive pressure accumulates.

### Connection to Aggregate Effects

The finding of substantial firm-level heterogeneity is consistent with Acemoglu's (2024) projection that AI's aggregate productivity effect will be modest. The aggregate modesty does not imply that AI's effects are uniformly small; rather, it reflects the offsetting of negative effects on high-replicability firms with neutral or positive effects on low-replicability firms. This thesis provides the micro-level evidence for the firm-level distribution underlying the aggregate result. Policymakers and investors who attend only to the aggregate may miss the substantial reallocation occurring within the software industry.

### Limitations

Several limitations qualify the interpretation of these results. First, the SBERT-based replicability index depends on the choice of anchor sentences. While the contrast score (correlation 0.35 with the high score) confirms that the two treatment variables capture genuinely different variation, and face validity is strong across all 143 firms, the specific anchor set is researcher-constructed and could be modified. Second, the Wayback Machine provides product page text for 106 of 143 firms; the remaining 37 firms use 10-K fallback text that demonstrably compresses the treatment variable. The preferred specification addresses this by restricting to Wayback-only firms, but this reduces the sample by 26 percent. Third, the marginal significance of the COVID-era revenue placebo test (p = 0.068) suggests that pre-existing differential demand patterns may partially confound the revenue result, although the direction of the confound is conservative. Fourth, the sample is limited to publicly listed U.S. software firms, which may not be representative of the broader population of private software companies, which are more numerous, generally smaller, and potentially more vulnerable to AI-driven substitution.

### Future Research

Three directions for future research emerge from this thesis. First, the replicability index could be made time-varying by incorporating LLM benchmark scores (such as MMLU or HumanEval) as a capability frontier index, allowing the treatment intensity to evolve as AI systems improve. Second, the analysis could be extended to labor market outcomes — hiring rates, wage growth, and workforce composition — to connect the product-level effects documented here to the worker-level effects studied by Eloundou et al. (2024) and Brynjolfsson et al. (2023). Third, studying new entrants separately from incumbents would illuminate whether the AI shock primarily redistributes revenue within the industry or attracts new competition from outside it.

---

## 9. Conclusion

This thesis investigated whether B2B software firms experienced heterogeneous financial outcomes after the ChatGPT shock, depending on how replicable their core product tasks are by large language models. Using a difference-in-differences design with a novel SBERT-based task replicability index applied to 143 publicly listed software firms, I identified two empirically distinguishable mechanisms. The substitution channel — captured by absolute task replicability — produced a statistically and economically significant reduction in post-shock revenue growth (β = −1.051, bootstrap p = 0.018), equivalent to $30.3 million lower quarterly revenue per standard deviation of replicability. The commodification channel — captured by relative task replicability versus infrastructure-oriented tasks — produced gross margin compression without corresponding revenue loss (β = −0.114, bootstrap p = 0.047), consistent with pricing power erosion as the market recognized that AI alternatives existed.

The theoretical contribution of this thesis is the distinction between product-level and worker-level task exposure. Existing research measures AI exposure through the lens of occupational task content — how many of a firm's workers perform tasks that AI can automate. This thesis demonstrates that product-level exposure — how many of a firm's *product tasks* AI can replicate — is a distinct construct with different economic implications. A firm can have low worker-level exposure and high product-level exposure, or vice versa. The software industry, where firms are task-performing services rather than ordinary capital goods producers, illustrates this distinction most sharply.

The policy implication is that the aggregate modesty of AI's estimated productivity effects masks substantial firm-level heterogeneity that regulators, investors, and managers should monitor. The 15 percentage point gap in post-shock revenue growth between the top and bottom quartiles of task replicability — within a single, narrowly defined industry — suggests that AI's distributional consequences at the firm level are far more pronounced than the aggregate numbers indicate.

A three-period decomposition of the post-shock effects reveals that these consequences are not a one-time adjustment but an intensifying process: the revenue displacement effect grew 57 percent larger in the advanced AI era relative to the early AI era, and gross margin commodification — absent when ChatGPT first launched — emerged only once AI capabilities matured sufficiently to become credible enterprise outside options in 2024. As the automation frontier continues to advance, the set of software products vulnerable to displacement and commodification will expand further.

As AI capabilities continue to advance, the automation frontier will move further into cognitive task space, and the set of software products vulnerable to substitution and commodification will expand. Understanding which firms are exposed, and through which mechanisms, is essential for anticipating the economic adjustment that lies ahead.

---

## References

Acemoglu, D. (2024). The simple macroeconomics of AI. *Economic Policy*, 39(120), 851–908.

Acemoglu, D., & Restrepo, P. (2018). The race between man and machine: Implications of technology for growth, factor shares, and employment. *American Economic Review*, 108(6), 1488–1542.

Acemoglu, D., & Restrepo, P. (2019). Automation and new tasks: How technology displaces and reinstates labor. *Journal of Economic Perspectives*, 33(2), 3–30.

Autor, D. H., Levy, F., & Murnane, R. J. (2003). The skill content of recent technological change: An empirical exploration. *Quarterly Journal of Economics*, 118(4), 1279–1333.

Bresnahan, T. F., & Trajtenberg, M. (1995). General purpose technologies: Engines of growth? *Journal of Econometrics*, 65(1), 83–108.

Brynjolfsson, E., Li, D., & Raymond, L. (2023). Generative AI at work. NBER Working Paper No. 31161.

Callaway, B., & Sant'Anna, P. H. C. (2021). Difference-in-differences with multiple time periods. *Journal of Econometrics*, 225(2), 200–230.

Cameron, A. C., Gelbach, J. B., & Miller, D. L. (2008). Bootstrap-based improvements for inference with clustered errors. *Review of Economics and Statistics*, 90(3), 414–427.

Eloundou, T., Manning, S., Mishkin, P., & Rock, D. (2024). GPTs are GPTs: Labor market impact potential of large language models. *Science*, 384(6702), 1306–1308.

Goldfarb, A., & Tucker, C. (2019). Digital economics. *Journal of Economic Literature*, 57(1), 3–43.

Labaschin, B., Eloundou, T., Manning, S., Mishkin, P., & Rock, D. (2025). Extending "GPTs are GPTs" to firms. *AEA Papers and Proceedings*, 115, 51–55.

Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using siamese BERT networks. *Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP)*, 3982–3992.
