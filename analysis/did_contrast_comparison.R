# =============================================================
# DiD Comparison: High Score vs Contrast Score
# =============================================================
# Runs DiD with both treatment variables side by side:
#   1. post_x_replicability (high_score only — original)
#   2. post_x_contrast (high_score - low_score)
# On full sample, trimmed 2020+, and wayback-only subsample.
# =============================================================

library(fixest)
library(dplyr)
library(modelsummary)

df <- read.csv("data/processed/master_panel.csv")

# Year-quarter identifiers
df <- df %>%
  mutate(year_quarter = paste0(fiscal_year, "Q", fiscal_quarter))

cat("Full panel:", nrow(df), "rows,", n_distinct(df$ticker), "firms\n")
cat("  text_source breakdown:\n")
print(table(df$text_source[!duplicated(df$ticker)]))

# --- Trimmed 2020+ sample ---
df_trim <- df %>% filter(fiscal_year >= 2020)
cat("\nTrimmed 2020+ panel:", nrow(df_trim), "rows,", n_distinct(df_trim$ticker), "firms\n")

# --- Wayback-only subsample (trimmed 2020+) ---
df_wb <- df_trim %>% filter(text_source == "wayback")
cat("Wayback-only (2020+):", nrow(df_wb), "rows,", n_distinct(df_wb$ticker), "firms\n\n")

# === PANEL A: TRIMMED 2020+ (ALL FIRMS) ===
cat("=" , rep("=", 69), "\n", sep = "")
cat("PANEL A: TRIMMED 2020+ — ALL 143 FIRMS\n")
cat("=" , rep("=", 69), "\n\n", sep = "")

m1_high <- feols(ln_revenue ~ post_x_replicability | ticker + year_quarter,
                 data = df_trim, cluster = ~ticker)
m1_cont <- feols(ln_revenue ~ post_x_contrast | ticker + year_quarter,
                 data = df_trim, cluster = ~ticker)
m2_high <- feols(gross_margin ~ post_x_replicability | ticker + year_quarter,
                 data = df_trim, cluster = ~ticker)
m2_cont <- feols(gross_margin ~ post_x_contrast | ticker + year_quarter,
                 data = df_trim, cluster = ~ticker)
m3_high <- feols(operating_margin ~ post_x_replicability | ticker + year_quarter,
                 data = df_trim, cluster = ~ticker)
m3_cont <- feols(operating_margin ~ post_x_contrast | ticker + year_quarter,
                 data = df_trim, cluster = ~ticker)

panel_a <- list(
  "ln(Rev) high" = m1_high, "ln(Rev) contrast" = m1_cont,
  "GM high"      = m2_high, "GM contrast"       = m2_cont,
  "OM high"      = m3_high, "OM contrast"       = m3_cont
)

msummary(panel_a,
  stars = c("*" = 0.1, "**" = 0.05, "***" = 0.01),
  gof_map = c("nobs", "r.squared"),
  output = "default"
)

# === PANEL B: WAYBACK-ONLY SUBSAMPLE (2020+) ===
cat("\n")
cat("=" , rep("=", 69), "\n", sep = "")
cat("PANEL B: WAYBACK-ONLY SUBSAMPLE (2020+)\n")
cat("=" , rep("=", 69), "\n\n", sep = "")

w1_high <- feols(ln_revenue ~ post_x_replicability | ticker + year_quarter,
                 data = df_wb, cluster = ~ticker)
w1_cont <- feols(ln_revenue ~ post_x_contrast | ticker + year_quarter,
                 data = df_wb, cluster = ~ticker)
w2_high <- feols(gross_margin ~ post_x_replicability | ticker + year_quarter,
                 data = df_wb, cluster = ~ticker)
w2_cont <- feols(gross_margin ~ post_x_contrast | ticker + year_quarter,
                 data = df_wb, cluster = ~ticker)
w3_high <- feols(operating_margin ~ post_x_replicability | ticker + year_quarter,
                 data = df_wb, cluster = ~ticker)
w3_cont <- feols(operating_margin ~ post_x_contrast | ticker + year_quarter,
                 data = df_wb, cluster = ~ticker)

panel_b <- list(
  "ln(Rev) high" = w1_high, "ln(Rev) contrast" = w1_cont,
  "GM high"      = w2_high, "GM contrast"       = w2_cont,
  "OM high"      = w3_high, "OM contrast"       = w3_cont
)

msummary(panel_b,
  stars = c("*" = 0.1, "**" = 0.05, "***" = 0.01),
  gof_map = c("nobs", "r.squared"),
  output = "default"
)

# === PARALLEL TRENDS — CONTRAST SCORE ===
cat("\n")
cat("=" , rep("=", 69), "\n", sep = "")
cat("PARALLEL TRENDS PRE-TEST — CONTRAST SCORE\n")
cat("=" , rep("=", 69), "\n\n", sep = "")

# Need quarter_relative for event study
ref_qid <- (2022 - 2019) * 4 + 3
df_trim <- df_trim %>%
  mutate(
    quarter_id = (fiscal_year - 2019) * 4 + fiscal_quarter,
    quarter_relative = quarter_id - ref_qid - 1
  )
df_wb <- df_wb %>%
  mutate(
    quarter_id = (fiscal_year - 2019) * 4 + fiscal_quarter,
    quarter_relative = quarter_id - ref_qid - 1
  )

# Trimmed 2020+ — high_score
cat("Trimmed 2020+ — HIGH SCORE:\n")
for (info in list(
  list("ln(Revenue)", "ln_revenue"),
  list("Gross Margin", "gross_margin"),
  list("Operating Margin", "operating_margin")
)) {
  fml <- as.formula(paste0(info[[2]],
    " ~ i(quarter_relative, replicability_score, ref = -1) | ticker + year_quarter"))
  es <- feols(fml, data = df_trim, cluster = ~ticker)
  ct <- coeftable(es)
  rnames <- rownames(ct)[grepl("quarter_relative", rownames(ct))]
  qr <- as.numeric(gsub("quarter_relative::([-0-9]+):.*", "\\1", rnames))
  pre_names <- rnames[qr < -1]
  if (length(pre_names) > 0) {
    pre_pattern <- paste0("quarter_relative::", qr[qr < -1], ":", collapse = "|")
    wt <- wald(es, keep = pre_pattern)
    cat(sprintf("  %-20s F = %.3f, p = %.4f %s\n",
      info[[1]], wt$stat, wt$p,
      ifelse(wt$p > 0.10, "(PASS)", "(FAIL)")))
  }
}

# Trimmed 2020+ — contrast_score
cat("\nTrimmed 2020+ — CONTRAST SCORE:\n")
for (info in list(
  list("ln(Revenue)", "ln_revenue"),
  list("Gross Margin", "gross_margin"),
  list("Operating Margin", "operating_margin")
)) {
  fml <- as.formula(paste0(info[[2]],
    " ~ i(quarter_relative, contrast_score, ref = -1) | ticker + year_quarter"))
  es <- feols(fml, data = df_trim, cluster = ~ticker)
  ct <- coeftable(es)
  rnames <- rownames(ct)[grepl("quarter_relative", rownames(ct))]
  qr <- as.numeric(gsub("quarter_relative::([-0-9]+):.*", "\\1", rnames))
  pre_names <- rnames[qr < -1]
  if (length(pre_names) > 0) {
    pre_pattern <- paste0("quarter_relative::", qr[qr < -1], ":", collapse = "|")
    wt <- wald(es, keep = pre_pattern)
    cat(sprintf("  %-20s F = %.3f, p = %.4f %s\n",
      info[[1]], wt$stat, wt$p,
      ifelse(wt$p > 0.10, "(PASS)", "(FAIL)")))
  }
}

# Wayback-only — contrast_score
cat("\nWayback-only (2020+) — CONTRAST SCORE:\n")
for (info in list(
  list("ln(Revenue)", "ln_revenue"),
  list("Gross Margin", "gross_margin"),
  list("Operating Margin", "operating_margin")
)) {
  fml <- as.formula(paste0(info[[2]],
    " ~ i(quarter_relative, contrast_score, ref = -1) | ticker + year_quarter"))
  es <- feols(fml, data = df_wb, cluster = ~ticker)
  ct <- coeftable(es)
  rnames <- rownames(ct)[grepl("quarter_relative", rownames(ct))]
  qr <- as.numeric(gsub("quarter_relative::([-0-9]+):.*", "\\1", rnames))
  pre_names <- rnames[qr < -1]
  if (length(pre_names) > 0) {
    pre_pattern <- paste0("quarter_relative::", qr[qr < -1], ":", collapse = "|")
    wt <- wald(es, keep = pre_pattern)
    cat(sprintf("  %-20s F = %.3f, p = %.4f %s\n",
      info[[1]], wt$stat, wt$p,
      ifelse(wt$p > 0.10, "(PASS)", "(FAIL)")))
  }
}

# === COMPACT SUMMARY TABLE ===
cat("\n\n")
cat("=" , rep("=", 69), "\n", sep = "")
cat("COMPACT SUMMARY: β ON post_x_treatment\n")
cat("=" , rep("=", 69), "\n\n")

extract_row <- function(model, label, sample, treatment) {
  b <- coef(model)[1]
  se <- summary(model)$se[1]
  p <- pvalue(model)[1]
  sig <- ifelse(p < 0.01, "***", ifelse(p < 0.05, "**", ifelse(p < 0.10, "*", "")))
  cat(sprintf("%-15s %-12s %-10s β=%7.3f%s  SE=%.3f  p=%.4f  n=%d\n",
    label, sample, treatment, b, sig, se, p, nobs(model)))
}

cat("Outcome         Sample       Treatment   Coefficient\n")
cat(strrep("-", 80), "\n")
extract_row(m1_high, "ln(Revenue)", "All 2020+", "high")
extract_row(m1_cont, "ln(Revenue)", "All 2020+", "contrast")
extract_row(w1_high, "ln(Revenue)", "WB only", "high")
extract_row(w1_cont, "ln(Revenue)", "WB only", "contrast")
cat(strrep("-", 80), "\n")
extract_row(m2_high, "Gross Margin", "All 2020+", "high")
extract_row(m2_cont, "Gross Margin", "All 2020+", "contrast")
extract_row(w2_high, "Gross Margin", "WB only", "high")
extract_row(w2_cont, "Gross Margin", "WB only", "contrast")
cat(strrep("-", 80), "\n")
extract_row(m3_high, "Op Margin", "All 2020+", "high")
extract_row(m3_cont, "Op Margin", "All 2020+", "contrast")
extract_row(w3_high, "Op Margin", "WB only", "high")
extract_row(w3_cont, "Op Margin", "WB only", "contrast")

cat("\nDone.\n")
