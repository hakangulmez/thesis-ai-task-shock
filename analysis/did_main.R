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

cat("\nDone. All outputs saved to results/ and figures/\n")
