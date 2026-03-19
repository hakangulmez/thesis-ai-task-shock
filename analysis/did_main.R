# =============================================================
# DiD Main Regression — AI Task Shock
# =============================================================
# Estimates the effect of task replicability on software firm
# outcomes after the ChatGPT shock (2022 Q4).
#
# Design: DiD with continuous treatment intensity
#   Y_it = α_i + δ_t + β(Post_t × Replicability_i) + γX_it + ε_it
#   Firm FE + Quarter FE + clustered SE at firm level
# =============================================================

library(fixest)
library(dplyr)
library(ggplot2)
library(modelsummary)

# --- 1. Load and prepare data -------------------------------------------

df <- read.csv("data/processed/master_panel.csv")

cat("Panel dimensions:", nrow(df), "rows,", n_distinct(df$ticker), "firms\n")

# Create year-quarter identifier for FE
df <- df %>%
  mutate(
    year_quarter = paste0(fiscal_year, "Q", fiscal_quarter),
    quarter_id   = (fiscal_year - 2019) * 4 + fiscal_quarter
  )

# Reference quarter: 2022 Q3 = quarter_relative = -1
# 2022 Q4 is the first post quarter (quarter_relative = 0)
ref_qid <- (2022 - 2019) * 4 + 3  # 2022 Q3
df <- df %>%
  mutate(quarter_relative = quarter_id - ref_qid - 1)

cat("Quarter relative range:", min(df$quarter_relative), "to", max(df$quarter_relative), "\n")
cat("Pre-period rows:", sum(df$post == 0), "\n")
cat("Post-period rows:", sum(df$post == 1), "\n\n")

# --- 2. Main DiD regressions (bare — no controls) -------------------------

# Model 1: ln(Revenue)
m1 <- feols(
  ln_revenue ~ post_x_replicability | ticker + year_quarter,
  data = df,
  cluster = ~ticker
)

# Model 2: Gross Margin
m2 <- feols(
  gross_margin ~ post_x_replicability | ticker + year_quarter,
  data = df,
  cluster = ~ticker
)

# Model 3: Operating Margin
m3 <- feols(
  operating_margin ~ post_x_replicability | ticker + year_quarter,
  data = df,
  cluster = ~ticker
)

cat("=" , rep("=", 59), "\n", sep = "")
cat("MAIN DiD RESULTS (bare — no controls)\n")
cat("=" , rep("=", 59), "\n\n", sep = "")

models <- list(
  "ln(Revenue)"      = m1,
  "Gross Margin"     = m2,
  "Operating Margin"  = m3
)

msummary(models,
  stars = c("*" = 0.1, "**" = 0.05, "***" = 0.01),
  gof_map = c("nobs", "r.squared", "adj.r.squared",
              "FE: ticker", "FE: year_quarter"),
  output = "default"
)

# Save table to file
dir.create("results", showWarnings = FALSE)
msummary(models,
  stars = c("*" = 0.1, "**" = 0.05, "***" = 0.01),
  gof_map = c("nobs", "r.squared", "adj.r.squared",
              "FE: ticker", "FE: year_quarter"),
  output = "results/did_main_table.txt"
)
cat("\nRegression table saved to results/did_main_table.txt\n")

# --- 3. Event study -----------------------------------------------------

cat("\n")
cat("=" , rep("=", 59), "\n", sep = "")
cat("EVENT STUDY\n")
cat("=" , rep("=", 59), "\n\n", sep = "")

# Event study: ln(Revenue)
es1 <- feols(
  ln_revenue ~ i(quarter_relative, replicability_score, ref = -1) |
    ticker + year_quarter,
  data = df,
  cluster = ~ticker
)

# Event study: Gross Margin
es2 <- feols(
  gross_margin ~ i(quarter_relative, replicability_score, ref = -1) |
    ticker + year_quarter,
  data = df,
  cluster = ~ticker
)

# Event study: Operating Margin
es3 <- feols(
  operating_margin ~ i(quarter_relative, replicability_score, ref = -1) |
    ticker + year_quarter,
  data = df,
  cluster = ~ticker
)

# --- 4. Event study plots -----------------------------------------------

dir.create("figures", showWarnings = FALSE)

# Helper: extract event study coefficients
extract_es <- function(model, outcome_label) {
  ct <- coeftable(model)
  # Filter to interaction terms
  idx <- grepl("quarter_relative", rownames(ct))
  ct_sub <- ct[idx, , drop = FALSE]

  # Parse quarter_relative from row names
  # Format: "quarter_relative::-16:replicability_score"
  qr <- as.numeric(gsub("quarter_relative::([-0-9]+):.*", "\\1", rownames(ct_sub)))

  data.frame(
    quarter_relative = qr,
    estimate         = ct_sub[, "Estimate"],
    se               = ct_sub[, "Std. Error"],
    ci_lower         = ct_sub[, "Estimate"] - 1.96 * ct_sub[, "Std. Error"],
    ci_upper         = ct_sub[, "Estimate"] + 1.96 * ct_sub[, "Std. Error"],
    outcome          = outcome_label
  )
}

es1_df <- extract_es(es1, "ln(Revenue)")
es2_df <- extract_es(es2, "Gross Margin")
es3_df <- extract_es(es3, "Operating Margin")

# Add the reference point (0 at quarter_relative = -1)
add_ref <- function(df_es) {
  ref_row <- data.frame(
    quarter_relative = -1, estimate = 0, se = 0,
    ci_lower = 0, ci_upper = 0, outcome = df_es$outcome[1]
  )
  rbind(df_es, ref_row)
}

es1_df <- add_ref(es1_df)
es2_df <- add_ref(es2_df)
es3_df <- add_ref(es3_df)

# Plot function
plot_event_study <- function(es_df, title, filename) {
  p <- ggplot(es_df, aes(x = quarter_relative, y = estimate)) +
    geom_hline(yintercept = 0, linetype = "dashed", color = "gray50") +
    geom_vline(xintercept = -0.5, linetype = "dotted", color = "red", linewidth = 0.5) +
    geom_ribbon(aes(ymin = ci_lower, ymax = ci_upper), alpha = 0.2, fill = "steelblue") +
    geom_point(color = "steelblue", size = 2) +
    geom_line(color = "steelblue", linewidth = 0.5) +
    labs(
      title    = title,
      subtitle = "Interaction: quarter × replicability_score (ref = -1)",
      x        = "Quarters relative to ChatGPT launch (2022 Q4)",
      y        = "Coefficient estimate"
    ) +
    theme_minimal(base_size = 12) +
    theme(plot.title = element_text(face = "bold"))

  ggsave(filename, p, width = 10, height = 6, dpi = 150)
  cat("Saved:", filename, "\n")
}

plot_event_study(es1_df, "Event Study: ln(Revenue) × Replicability",
                 "figures/event_study_ln_revenue.png")
plot_event_study(es2_df, "Event Study: Gross Margin × Replicability",
                 "figures/event_study_gross_margin.png")
plot_event_study(es3_df, "Event Study: Operating Margin × Replicability",
                 "figures/event_study_operating_margin.png")

# --- 5. Parallel trends pre-test ----------------------------------------

cat("\n")
cat("=" , rep("=", 59), "\n", sep = "")
cat("PARALLEL TRENDS PRE-TEST\n")
cat("=" , rep("=", 59), "\n\n", sep = "")

# Test: are pre-period event study coefficients jointly zero?
# Use Wald test on pre-period coefficients

for (label in c("ln(Revenue)", "Gross Margin", "Operating Margin")) {
  es_model <- switch(label,
    "ln(Revenue)"      = es1,
    "Gross Margin"     = es2,
    "Operating Margin"  = es3
  )

  ct <- coeftable(es_model)
  idx <- grepl("quarter_relative", rownames(ct))
  rnames <- rownames(ct)[idx]
  qr <- as.numeric(gsub("quarter_relative::([-0-9]+):.*", "\\1", rnames))

  # Pre-period coefficients (quarter_relative < -1, since -1 is reference)
  pre_names <- rnames[qr < -1]

  if (length(pre_names) > 0) {
    # Use regex pattern to match pre-period coefficients
    pre_pattern <- paste0("quarter_relative::", qr[qr < -1], ":", collapse = "|")
    wt <- wald(es_model, keep = pre_pattern)
    cat(sprintf("%-20s F = %.3f, p = %.4f %s\n",
      label, wt$stat, wt$p,
      ifelse(wt$p > 0.10, "(PASS: cannot reject parallel trends)",
             "(FAIL: pre-trends detected)")))
  }
}

# --- 6. Robustness: DiD with controls ------------------------------------

cat("\n")
cat("=" , rep("=", 59), "\n", sep = "")
cat("ROBUSTNESS: DiD WITH CONTROLS (rd_intensity + sga_intensity)\n")
cat("=" , rep("=", 59), "\n\n", sep = "")

m1_ctrl <- feols(ln_revenue ~ post_x_replicability + rd_intensity + sga_intensity |
                   ticker + year_quarter, data = df, cluster = ~ticker)
m2_ctrl <- feols(gross_margin ~ post_x_replicability + rd_intensity + sga_intensity |
                   ticker + year_quarter, data = df, cluster = ~ticker)
m3_ctrl <- feols(operating_margin ~ post_x_replicability + rd_intensity + sga_intensity |
                   ticker + year_quarter, data = df, cluster = ~ticker)

ctrl_models <- list(
  "ln(Rev) bare"   = m1,
  "ln(Rev) ctrl"   = m1_ctrl,
  "GM bare"        = m2,
  "GM ctrl"        = m2_ctrl,
  "OM bare"        = m3,
  "OM ctrl"        = m3_ctrl
)

msummary(ctrl_models,
  stars = c("*" = 0.1, "**" = 0.05, "***" = 0.01),
  gof_map = c("nobs", "r.squared", "adj.r.squared",
              "FE: ticker", "FE: year_quarter"),
  output = "default"
)

msummary(ctrl_models,
  stars = c("*" = 0.1, "**" = 0.05, "***" = 0.01),
  gof_map = c("nobs", "r.squared", "adj.r.squared",
              "FE: ticker", "FE: year_quarter"),
  output = "results/did_robustness_controls.txt"
)
cat("Saved: results/did_robustness_controls.txt\n")

# --- 7. Gross margin pre-trends investigation ----------------------------

cat("\n")
cat("=" , rep("=", 59), "\n", sep = "")
cat("GROSS MARGIN PRE-TRENDS INVESTIGATION\n")
cat("=" , rep("=", 59), "\n\n", sep = "")

median_rep <- median(df$replicability_score, na.rm = TRUE)
cat("Median replicability score:", median_rep, "\n\n")

df <- df %>%
  mutate(rep_group = ifelse(replicability_score >= median_rep, "High", "Low"))

# Pre-period only (post == 0)
pre_df <- df %>%
  filter(post == 0, !is.na(gross_margin)) %>%
  group_by(year_quarter, rep_group) %>%
  summarise(
    mean_gm = mean(gross_margin, na.rm = TRUE),
    se_gm   = sd(gross_margin, na.rm = TRUE) / sqrt(n()),
    n       = n(),
    .groups  = "drop"
  )

# Create ordered factor for year_quarter
pre_df <- pre_df %>%
  mutate(
    yq_num = as.numeric(gsub("(\\d+)Q(\\d+)", "\\1", year_quarter)) +
             (as.numeric(gsub("(\\d+)Q(\\d+)", "\\2", year_quarter)) - 1) / 4
  ) %>%
  arrange(yq_num)

pre_df$year_quarter <- factor(pre_df$year_quarter,
                              levels = unique(pre_df$year_quarter[order(pre_df$yq_num)]))

p_gm <- ggplot(pre_df, aes(x = year_quarter, y = mean_gm,
                            color = rep_group, group = rep_group)) +
  geom_point(size = 2) +
  geom_line(linewidth = 0.6) +
  geom_ribbon(aes(ymin = mean_gm - 1.96 * se_gm,
                  ymax = mean_gm + 1.96 * se_gm,
                  fill = rep_group),
              alpha = 0.15, color = NA) +
  scale_color_manual(values = c("High" = "coral", "Low" = "steelblue")) +
  scale_fill_manual(values = c("High" = "coral", "Low" = "steelblue")) +
  labs(
    title    = "Gross Margin Pre-Trends: High vs Low Replicability",
    subtitle = sprintf("Split at median replicability = %.3f | Pre-period only (2019 Q1 – 2022 Q3)", median_rep),
    x        = "Quarter",
    y        = "Mean Gross Margin",
    color    = "Replicability",
    fill     = "Replicability"
  ) +
  theme_minimal(base_size = 12) +
  theme(
    plot.title = element_text(face = "bold"),
    axis.text.x = element_text(angle = 45, hjust = 1, size = 8)
  )

ggsave("figures/gross_margin_pretrends.png", p_gm, width = 12, height = 6, dpi = 150)
cat("Saved: figures/gross_margin_pretrends.png\n")

# Print the actual values
cat("\nPre-period mean gross margin by group and quarter:\n")
wide <- pre_df %>%
  select(year_quarter, rep_group, mean_gm) %>%
  tidyr::pivot_wider(names_from = rep_group, values_from = mean_gm)
print(as.data.frame(wide), digits = 4)

# --- 8. Robustness: trimmed pre-period (2020+) ---------------------------

cat("\n")
cat("=" , rep("=", 59), "\n", sep = "")
cat("ROBUSTNESS: TRIMMED PRE-PERIOD (year >= 2020)\n")
cat("=" , rep("=", 59), "\n\n", sep = "")

df_trim <- df %>% filter(fiscal_year >= 2020)
cat("Trimmed panel:", nrow(df_trim), "rows,", n_distinct(df_trim$ticker), "firms\n")
cat("Pre-period rows:", sum(df_trim$post == 0), "\n")
cat("Post-period rows:", sum(df_trim$post == 1), "\n\n")

# Recompute interaction for trimmed data (already in data, no change needed)
m1_trim <- feols(ln_revenue ~ post_x_replicability | ticker + year_quarter,
                 data = df_trim, cluster = ~ticker)
m2_trim <- feols(gross_margin ~ post_x_replicability | ticker + year_quarter,
                 data = df_trim, cluster = ~ticker)
m3_trim <- feols(operating_margin ~ post_x_replicability | ticker + year_quarter,
                 data = df_trim, cluster = ~ticker)

trim_models <- list(
  "ln(Rev) full"   = m1,
  "ln(Rev) 2020+"  = m1_trim,
  "GM full"        = m2,
  "GM 2020+"       = m2_trim,
  "OM full"        = m3,
  "OM 2020+"       = m3_trim
)

msummary(trim_models,
  stars = c("*" = 0.1, "**" = 0.05, "***" = 0.01),
  gof_map = c("nobs", "r.squared", "adj.r.squared",
              "FE: ticker", "FE: year_quarter"),
  output = "default"
)

msummary(trim_models,
  stars = c("*" = 0.1, "**" = 0.05, "***" = 0.01),
  gof_map = c("nobs", "r.squared", "adj.r.squared",
              "FE: ticker", "FE: year_quarter"),
  output = "results/did_robustness_trimmed.txt"
)
cat("Saved: results/did_robustness_trimmed.txt\n")

# Parallel trends on trimmed sample
cat("\nParallel trends pre-test (trimmed 2020+ sample):\n")
es1_trim <- feols(ln_revenue ~ i(quarter_relative, replicability_score, ref = -1) |
                    ticker + year_quarter, data = df_trim, cluster = ~ticker)
es2_trim <- feols(gross_margin ~ i(quarter_relative, replicability_score, ref = -1) |
                    ticker + year_quarter, data = df_trim, cluster = ~ticker)
es3_trim <- feols(operating_margin ~ i(quarter_relative, replicability_score, ref = -1) |
                    ticker + year_quarter, data = df_trim, cluster = ~ticker)

for (label in c("ln(Revenue)", "Gross Margin", "Operating Margin")) {
  es_model <- switch(label,
    "ln(Revenue)"      = es1_trim,
    "Gross Margin"     = es2_trim,
    "Operating Margin"  = es3_trim
  )
  ct <- coeftable(es_model)
  idx <- grepl("quarter_relative", rownames(ct))
  rnames <- rownames(ct)[idx]
  qr <- as.numeric(gsub("quarter_relative::([-0-9]+):.*", "\\1", rnames))
  pre_qr <- qr[qr < -1]
  if (length(pre_qr) > 0) {
    pre_pattern <- paste0("quarter_relative::", pre_qr, ":", collapse = "|")
    wt <- wald(es_model, keep = pre_pattern)
    cat(sprintf("  %-20s F = %.3f, p = %.4f %s\n",
      label, wt$stat, wt$p,
      ifelse(wt$p > 0.10, "(PASS)", "(FAIL)")))
  }
}

# =============================================================
# 9. EVENT STUDY — WAYBACK-ONLY, 2020+ (PREFERRED SPEC)
# =============================================================

cat("\n")
cat("=" , rep("=", 69), "\n", sep = "")
cat("EVENT STUDY — WAYBACK-ONLY, 2020+ (PREFERRED SPECIFICATION)\n")
cat("=" , rep("=", 69), "\n\n", sep = "")

df_wb <- df %>%
  filter(fiscal_year >= 2020, text_source == "wayback")

cat("Wayback-only 2020+ panel:", nrow(df_wb), "rows,",
    n_distinct(df_wb$ticker), "firms\n")
cat("Quarter relative range:", min(df_wb$quarter_relative),
    "to", max(df_wb$quarter_relative), "\n\n")

# --- Event study A: ln_revenue x replicability_score ---
es_rev <- feols(
  ln_revenue ~ i(quarter_relative, replicability_score, ref = -1) |
    ticker + year_quarter,
  data = df_wb, cluster = ~ticker
)

# --- Event study B: gross_margin x contrast_score ---
es_gm <- feols(
  gross_margin ~ i(quarter_relative, contrast_score, ref = -1) |
    ticker + year_quarter,
  data = df_wb, cluster = ~ticker
)

# --- Extract coefficients ---
extract_es2 <- function(model, outcome_label, treatment_label) {
  ct <- coeftable(model)
  idx <- grepl("quarter_relative", rownames(ct))
  ct_sub <- ct[idx, , drop = FALSE]
  qr <- as.numeric(gsub("quarter_relative::([-0-9]+):.*", "\\1", rownames(ct_sub)))
  pvals <- ct_sub[, "Pr(>|t|)"]

  out <- data.frame(
    quarter_relative = qr,
    estimate         = ct_sub[, "Estimate"],
    se               = ct_sub[, "Std. Error"],
    ci_lower         = ct_sub[, "Estimate"] - 1.96 * ct_sub[, "Std. Error"],
    ci_upper         = ct_sub[, "Estimate"] + 1.96 * ct_sub[, "Std. Error"],
    pvalue           = pvals,
    outcome          = outcome_label,
    treatment        = treatment_label,
    stringsAsFactors = FALSE
  )
  # Add reference point
  ref_row <- data.frame(
    quarter_relative = -1, estimate = 0, se = 0,
    ci_lower = 0, ci_upper = 0, pvalue = NA,
    outcome = outcome_label, treatment = treatment_label,
    stringsAsFactors = FALSE
  )
  rbind(out, ref_row)
}

es_rev_df <- extract_es2(es_rev, "ln(Revenue)", "replicability_score")
es_gm_df  <- extract_es2(es_gm,  "Gross Margin", "contrast_score")

# --- Print coefficients ---
cat("Event Study A: ln(Revenue) x replicability_score\n")
cat(sprintf("%-5s %10s %10s %10s %10s\n", "k", "Beta", "SE", "95% CI", "p"))
cat(strrep("-", 55), "\n")
for (i in order(es_rev_df$quarter_relative)) {
  r <- es_rev_df[i, ]
  cat(sprintf("%4d  %9.4f %9.4f  [%6.3f, %6.3f]  %s\n",
    r$quarter_relative, r$estimate, r$se, r$ci_lower, r$ci_upper,
    ifelse(is.na(r$pvalue), "ref", sprintf("%.4f", r$pvalue))))
}

cat("\nEvent Study B: Gross Margin x contrast_score\n")
cat(sprintf("%-5s %10s %10s %10s %10s\n", "k", "Beta", "SE", "95% CI", "p"))
cat(strrep("-", 55), "\n")
for (i in order(es_gm_df$quarter_relative)) {
  r <- es_gm_df[i, ]
  cat(sprintf("%4d  %9.4f %9.4f  [%6.3f, %6.3f]  %s\n",
    r$quarter_relative, r$estimate, r$se, r$ci_lower, r$ci_upper,
    ifelse(is.na(r$pvalue), "ref", sprintf("%.4f", r$pvalue))))
}

# --- Plot A: ln(Revenue) event study ---
es_rev_df <- es_rev_df[order(es_rev_df$quarter_relative), ]
es_rev_df$period <- ifelse(es_rev_df$quarter_relative < 0, "pre", "post")
es_rev_df$sig_post <- ifelse(
  es_rev_df$period == "post" & !is.na(es_rev_df$pvalue) & es_rev_df$pvalue < 0.05,
  "sig", "ns"
)

p_rev <- ggplot(es_rev_df, aes(x = quarter_relative, y = estimate)) +
  annotate("rect", xmin = -Inf, xmax = -0.5, ymin = -Inf, ymax = Inf,
           fill = "gray90", alpha = 0.5) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "gray40", linewidth = 0.5) +
  geom_vline(xintercept = -0.5, color = "black", linewidth = 0.7) +
  geom_ribbon(aes(ymin = ci_lower, ymax = ci_upper), alpha = 0.15, fill = "steelblue") +
  geom_errorbar(aes(ymin = ci_lower, ymax = ci_upper), width = 0.2, color = "steelblue", alpha = 0.6) +
  geom_point(aes(color = sig_post), size = 2.5) +
  geom_line(color = "steelblue", linewidth = 0.4) +
  scale_color_manual(values = c("ns" = "steelblue", "sig" = "red"), guide = "none") +
  labs(
    title    = "Event Study: ln(Revenue) × Replicability Score",
    subtitle = "Wayback-only sample (106 firms), 2020+, ref = k=-1 (2022 Q3)",
    x        = "Quarters Relative to ChatGPT Launch (2022 Q4)",
    y        = "Coefficient (Post × Replicability)",
    caption  = "Firm + Quarter FE, clustered SE | Red = significant at 5%"
  ) +
  theme_minimal(base_size = 12) +
  theme(plot.title = element_text(face = "bold"),
        plot.caption = element_text(color = "gray50", size = 8))

ggsave("figures/event_study_revenue.png", p_rev, width = 10, height = 6, dpi = 150)
cat("\nSaved: figures/event_study_revenue.png\n")

# --- Plot B: Gross Margin event study ---
es_gm_df <- es_gm_df[order(es_gm_df$quarter_relative), ]
es_gm_df$period <- ifelse(es_gm_df$quarter_relative < 0, "pre", "post")
es_gm_df$sig_post <- ifelse(
  es_gm_df$period == "post" & !is.na(es_gm_df$pvalue) & es_gm_df$pvalue < 0.05,
  "sig", "ns"
)

p_gm2 <- ggplot(es_gm_df, aes(x = quarter_relative, y = estimate)) +
  annotate("rect", xmin = -Inf, xmax = -0.5, ymin = -Inf, ymax = Inf,
           fill = "gray90", alpha = 0.5) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "gray40", linewidth = 0.5) +
  geom_vline(xintercept = -0.5, color = "black", linewidth = 0.7) +
  geom_ribbon(aes(ymin = ci_lower, ymax = ci_upper), alpha = 0.15, fill = "#E67E22") +
  geom_errorbar(aes(ymin = ci_lower, ymax = ci_upper), width = 0.2, color = "#E67E22", alpha = 0.6) +
  geom_point(aes(color = sig_post), size = 2.5) +
  geom_line(color = "#E67E22", linewidth = 0.4) +
  scale_color_manual(values = c("ns" = "#E67E22", "sig" = "red"), guide = "none") +
  labs(
    title    = "Event Study: Gross Margin × Contrast Score",
    subtitle = "Wayback-only sample (106 firms), 2020+, ref = k=-1 (2022 Q3)",
    x        = "Quarters Relative to ChatGPT Launch (2022 Q4)",
    y        = "Coefficient (Post × Contrast)",
    caption  = "Firm + Quarter FE, clustered SE | Red = significant at 5%"
  ) +
  theme_minimal(base_size = 12) +
  theme(plot.title = element_text(face = "bold"),
        plot.caption = element_text(color = "gray50", size = 8))

ggsave("figures/event_study_margin.png", p_gm2, width = 10, height = 6, dpi = 150)
cat("Saved: figures/event_study_margin.png\n")

# --- Pre-trend Wald tests (WB-only 2020+) ---
cat("\n--- Parallel Trends Pre-Test (Wayback-only, 2020+) ---\n")

for (info in list(
  list("ln(Revenue)", es_rev),
  list("Gross Margin", es_gm)
)) {
  label <- info[[1]]
  es_model <- info[[2]]
  ct <- coeftable(es_model)
  rnames <- rownames(ct)[grepl("quarter_relative", rownames(ct))]
  qr <- as.numeric(gsub("quarter_relative::([-0-9]+):.*", "\\1", rnames))
  pre_qr <- qr[qr < -1]
  if (length(pre_qr) > 0) {
    pre_pattern <- paste0("quarter_relative::", pre_qr, ":", collapse = "|")
    wt <- wald(es_model, keep = pre_pattern)
    cat(sprintf("  %-20s F = %.3f, p = %.4f %s\n",
      label, wt$stat, wt$p,
      ifelse(wt$p > 0.10, "(PASS)", "(FAIL)")))
  }
}

# =============================================================
# 10. HETEROGENEITY BY SIC CODE
# =============================================================

cat("\n")
cat("=" , rep("=", 69), "\n", sep = "")
cat("HETEROGENEITY BY SIC CODE — WAYBACK-ONLY, 2020+\n")
cat("=" , rep("=", 69), "\n\n", sep = "")

# Merge SIC codes from universe
universe <- read.csv("data/raw/firm_universe_v1.csv")
sic_map <- universe[, c("ticker", "sic_code")]
df_wb <- merge(df_wb, sic_map, by = "ticker", all.x = TRUE)

# Create SIC groups
df_wb$sic_group <- ifelse(df_wb$sic_code %in% c(7370, 7371), "7370/7371",
                   ifelse(df_wb$sic_code == 7372, "7372",
                   ifelse(df_wb$sic_code %in% c(7373, 7374), "7373/7374", "Other")))

cat("SIC group distribution (firms):\n")
sic_firm_counts <- tapply(df_wb$ticker, df_wb$sic_group, function(x) length(unique(x)))
print(sic_firm_counts)
cat("\n")

# --- Mechanism 1: ln_revenue x replicability_score by SIC ---
cat("MECHANISM 1: ln(Revenue) x replicability_score\n")
cat(sprintf("%-12s %8s %10s %10s %10s %6s\n",
    "SIC Group", "N firms", "Beta", "SE", "p-value", "Sig"))
cat(strrep("-", 62), "\n")

for (grp in c("7370/7371", "7372", "7373/7374")) {
  sub <- df_wb[df_wb$sic_group == grp, ]
  n_firms <- length(unique(sub$ticker))
  m <- tryCatch(
    feols(ln_revenue ~ post_x_replicability | ticker + year_quarter,
          data = sub, cluster = ~ticker),
    error = function(e) NULL
  )
  if (!is.null(m)) {
    b <- coef(m)["post_x_replicability"]
    se <- summary(m)$se["post_x_replicability"]
    p <- pvalue(m)["post_x_replicability"]
    sig <- ifelse(p < 0.01, "***", ifelse(p < 0.05, "**", ifelse(p < 0.10, "*", "")))
    cat(sprintf("%-12s %8d %10.4f %10.4f %10.4f %6s\n", grp, n_firms, b, se, p, sig))
  } else {
    cat(sprintf("%-12s %8d %10s\n", grp, n_firms, "FAILED"))
  }
}

# --- Mechanism 2: gross_margin x contrast_score by SIC ---
cat("\nMECHANISM 2: Gross Margin x contrast_score\n")
cat(sprintf("%-12s %8s %10s %10s %10s %6s\n",
    "SIC Group", "N firms", "Beta", "SE", "p-value", "Sig"))
cat(strrep("-", 62), "\n")

for (grp in c("7370/7371", "7372", "7373/7374")) {
  sub <- df_wb[df_wb$sic_group == grp, ]
  n_firms <- length(unique(sub$ticker))
  m <- tryCatch(
    feols(gross_margin ~ post_x_contrast | ticker + year_quarter,
          data = sub, cluster = ~ticker),
    error = function(e) NULL
  )
  if (!is.null(m)) {
    b <- coef(m)["post_x_contrast"]
    se <- summary(m)$se["post_x_contrast"]
    p <- pvalue(m)["post_x_contrast"]
    sig <- ifelse(p < 0.01, "***", ifelse(p < 0.05, "**", ifelse(p < 0.10, "*", "")))
    cat(sprintf("%-12s %8d %10.4f %10.4f %10.4f %6s\n", grp, n_firms, b, se, p, sig))
  } else {
    cat(sprintf("%-12s %8d %10s\n", grp, n_firms, "FAILED"))
  }
}

# =============================================================
# 11. ROBUSTNESS CHECKS
# =============================================================

cat("\n")
cat("=" , rep("=", 69), "\n", sep = "")
cat("ROBUSTNESS CHECKS — WAYBACK-ONLY, 2020+\n")
cat("=" , rep("=", 69), "\n\n")

# Recreate df_wb without SIC merge artifacts
df_wb2 <- df %>%
  filter(fiscal_year >= 2020, text_source == "wayback")

# --- ROBUSTNESS 1: Alternative shock date (GPT-4, 2023 Q2) ---
cat("--- ROBUSTNESS 1: Alternative Shock Date (GPT-4, 2023 Q2) ---\n\n")

df_wb2$post_gpt4 <- as.integer(
  (df_wb2$fiscal_year > 2023) |
  (df_wb2$fiscal_year == 2023 & df_wb2$fiscal_quarter >= 2)
)
df_wb2$post_gpt4_x_rep <- df_wb2$post_gpt4 * df_wb2$replicability_score
df_wb2$post_gpt4_x_con <- df_wb2$post_gpt4 * df_wb2$contrast_score

r1_rev <- feols(ln_revenue ~ post_gpt4_x_rep | ticker + year_quarter,
                data = df_wb2, cluster = ~ticker)
r1_gm  <- feols(gross_margin ~ post_gpt4_x_con | ticker + year_quarter,
                data = df_wb2, cluster = ~ticker)

cat(sprintf("%-40s %10s %10s %10s %6s\n",
    "Specification", "Beta", "SE", "p-value", "Sig"))
cat(strrep("-", 80), "\n")

# Original results for comparison
orig_rev <- feols(ln_revenue ~ post_x_replicability | ticker + year_quarter,
                  data = df_wb2, cluster = ~ticker)
orig_gm  <- feols(gross_margin ~ post_x_contrast | ticker + year_quarter,
                  data = df_wb2, cluster = ~ticker)

print_row <- function(label, model, varname) {
  b <- coef(model)[varname]
  se <- summary(model)$se[varname]
  p <- pvalue(model)[varname]
  sig <- ifelse(p < 0.01, "***", ifelse(p < 0.05, "**", ifelse(p < 0.10, "*", "")))
  cat(sprintf("%-40s %10.4f %10.4f %10.4f %6s\n", label, b, se, p, sig))
}

print_row("ln(Rev): Original (2022 Q4)", orig_rev, "post_x_replicability")
print_row("ln(Rev): GPT-4 date (2023 Q2)", r1_rev, "post_gpt4_x_rep")
print_row("Gross Margin: Original (2022 Q4)", orig_gm, "post_x_contrast")
print_row("Gross Margin: GPT-4 date (2023 Q2)", r1_gm, "post_gpt4_x_con")

# --- ROBUSTNESS 2: COVID placebo test ---
cat("\n--- ROBUSTNESS 2: COVID Placebo Test (fake shock at 2020 Q1) ---\n\n")

# Restrict to pre-shock data only (fiscal_year <= 2022, quarter < Q4 if 2022)
df_placebo <- df %>%
  filter(text_source == "wayback",
         fiscal_year >= 2020,
         (fiscal_year < 2022) | (fiscal_year == 2022 & fiscal_quarter <= 3))

# Placebo post: 1 if >= 2021 Q1 (so 2020 is all pre, 2021-2022Q3 is post)
df_placebo$post_placebo <- as.integer(df_placebo$fiscal_year >= 2021)
df_placebo$placebo_x_rep <- df_placebo$post_placebo * df_placebo$replicability_score
df_placebo$placebo_x_con <- df_placebo$post_placebo * df_placebo$contrast_score

cat("Placebo sample:", nrow(df_placebo), "rows,",
    n_distinct(df_placebo$ticker), "firms\n")
cat("Pre (2020): ", sum(df_placebo$post_placebo == 0), "rows\n")
cat("Post (2021-2022Q3):", sum(df_placebo$post_placebo == 1), "rows\n\n")

r2_rev <- feols(ln_revenue ~ placebo_x_rep | ticker + year_quarter,
                data = df_placebo, cluster = ~ticker)
r2_gm  <- feols(gross_margin ~ placebo_x_con | ticker + year_quarter,
                data = df_placebo, cluster = ~ticker)

cat(sprintf("%-40s %10s %10s %10s %6s %8s\n",
    "Specification", "Beta", "SE", "p-value", "Sig", "Result"))
cat(strrep("-", 86), "\n")

for (info in list(
  list("ln(Rev): Placebo (2020 Q1)", r2_rev, "placebo_x_rep"),
  list("Gross Margin: Placebo (2020 Q1)", r2_gm, "placebo_x_con")
)) {
  b <- coef(info[[2]])[info[[3]]]
  se <- summary(info[[2]])$se[info[[3]]]
  p <- pvalue(info[[2]])[info[[3]]]
  sig <- ifelse(p < 0.01, "***", ifelse(p < 0.05, "**", ifelse(p < 0.10, "*", "")))
  result <- ifelse(p > 0.10, "PASS", "FAIL")
  cat(sprintf("%-40s %10.4f %10.4f %10.4f %6s %8s\n", info[[1]], b, se, p, sig, result))
}
cat("PASS = null result (p > 0.10) — no pre-existing differential trends\n")

# --- ROBUSTNESS 3: Exclude mega-caps ---
cat("\n--- ROBUSTNESS 3: Exclude Mega-Caps (ADP, DXC) ---\n\n")

df_nomega <- df_wb2 %>%
  filter(!(ticker %in% c("ADP", "DXC")))

cat("Sample without mega-caps:", nrow(df_nomega), "rows,",
    n_distinct(df_nomega$ticker), "firms\n\n")

r3_rev <- feols(ln_revenue ~ post_x_replicability | ticker + year_quarter,
                data = df_nomega, cluster = ~ticker)
r3_gm  <- feols(gross_margin ~ post_x_contrast | ticker + year_quarter,
                data = df_nomega, cluster = ~ticker)

cat(sprintf("%-40s %10s %10s %10s %6s\n",
    "Specification", "Beta", "SE", "p-value", "Sig"))
cat(strrep("-", 80), "\n")
print_row("ln(Rev): Original (106 firms)", orig_rev, "post_x_replicability")
print_row("ln(Rev): Excl. mega-caps (104 firms)", r3_rev, "post_x_replicability")
print_row("Gross Margin: Original (106 firms)", orig_gm, "post_x_contrast")
print_row("Gross Margin: Excl. mega-caps (104)", r3_gm, "post_x_contrast")

# =============================================================
# COMPREHENSIVE ROBUSTNESS SUMMARY
# =============================================================
cat("\n\n")
cat("=" , rep("=", 79), "\n", sep = "")
cat("COMPREHENSIVE ROBUSTNESS SUMMARY\n")
cat("=" , rep("=", 79), "\n\n", sep = "")

cat(sprintf("%-35s %-14s %8s %8s %8s %5s\n",
    "Check", "Outcome", "Beta", "SE", "p", "Sig"))
cat(strrep("-", 80), "\n")

summary_row <- function(label, outcome, model, varname) {
  b <- coef(model)[varname]
  se <- summary(model)$se[varname]
  p <- pvalue(model)[varname]
  sig <- ifelse(p < 0.01, "***", ifelse(p < 0.05, "**", ifelse(p < 0.10, "*", "")))
  cat(sprintf("%-35s %-14s %8.4f %8.4f %8.4f %5s\n", label, outcome, b, se, p, sig))
}

summary_row("Baseline (2022 Q4)", "ln(Revenue)", orig_rev, "post_x_replicability")
summary_row("Alt shock (GPT-4, 2023 Q2)", "ln(Revenue)", r1_rev, "post_gpt4_x_rep")
summary_row("Placebo (2020 Q1)", "ln(Revenue)", r2_rev, "placebo_x_rep")
summary_row("Excl. mega-caps", "ln(Revenue)", r3_rev, "post_x_replicability")
cat(strrep("-", 80), "\n")
summary_row("Baseline (2022 Q4)", "Gross Margin", orig_gm, "post_x_contrast")
summary_row("Alt shock (GPT-4, 2023 Q2)", "Gross Margin", r1_gm, "post_gpt4_x_con")
summary_row("Placebo (2020 Q1)", "Gross Margin", r2_gm, "placebo_x_con")
summary_row("Excl. mega-caps", "Gross Margin", r3_gm, "post_x_contrast")
cat(strrep("-", 80), "\n")

cat("\nAll regressions: Firm + Quarter FE, clustered SE, Wayback-only, 2020+\n")
cat("* p<0.10, ** p<0.05, *** p<0.01\n")

cat("\nDone. All outputs saved to results/ and figures/\n")
