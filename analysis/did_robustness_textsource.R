# =============================================================
# DiD Robustness: Compare treatment variable sources
# =============================================================
# Runs main DiD with three versions of replicability scores:
#   1. Baseline (product_pages: wayback + 10k fallback)
#   2. 10-K only (all firms scored from 10-K extracts)
#   3. Wayback only (106 firms with wayback text)
# =============================================================

library(fixest)
library(dplyr)

# --- Load financial panel ---
# Use master_panel which is already clean and merged
fin <- read.csv("data/processed/master_panel.csv")
# Keep only financial columns needed for re-merging
fin <- fin[, c("ticker", "fiscal_year", "fiscal_quarter", "revenue",
               "gross_margin", "operating_margin")]

# --- Load all three replicability score files ---
# Use fread to handle binary garbage in top_sentences column
read_scores <- function(path) {
  df <- data.table::fread(path, select = c("ticker", "replicability_score"))
  as.data.frame(df)
}
rep_base <- read_scores("data/processed/replicability_scores.csv")
rep_10k  <- read_scores("data/processed/replicability_scores_10k.csv")
rep_wb   <- read_scores("data/processed/replicability_scores_wayback_only.csv")

cat("Score counts — Baseline:", nrow(rep_base),
    " 10-K:", nrow(rep_10k),
    " Wayback:", nrow(rep_wb), "\n")

# --- Helper: build panel from scores ---
build_panel <- function(fin, rep_df) {
  rep_cols <- rep_df[, c("ticker", "replicability_score")]
  panel <- merge(fin, rep_cols, by = "ticker", all.x = TRUE)
  panel <- panel[!is.na(panel$replicability_score), ]
  panel$post <- as.integer(panel$fiscal_year > 2022 |
    (panel$fiscal_year == 2022 & panel$fiscal_quarter >= 4))
  panel$post_x_replicability <- panel$post * panel$replicability_score
  panel$ln_revenue <- ifelse(panel$revenue > 0, log(panel$revenue), NA)
  panel$year_quarter <- paste0(panel$fiscal_year, "Q", panel$fiscal_quarter)
  # Trim to 2020+
  panel <- panel[panel$fiscal_year >= 2020, ]
  panel
}

p_base <- build_panel(fin, rep_base)
p_10k  <- build_panel(fin, rep_10k)
p_wb   <- build_panel(fin, rep_wb)

cat("\nPanel sizes — Baseline:", nrow(p_base), "firms:", n_distinct(p_base$ticker),
    "\n              10-K:",     nrow(p_10k),  "firms:", n_distinct(p_10k$ticker),
    "\n              Wayback:",  nrow(p_wb),   "firms:", n_distinct(p_wb$ticker), "\n")

# --- Run DiD for each ---
run_did <- function(panel) {
  m1 <- feols(ln_revenue ~ post_x_replicability | ticker + year_quarter,
              data = panel, cluster = ~ticker)
  m2 <- feols(gross_margin ~ post_x_replicability | ticker + year_quarter,
              data = panel, cluster = ~ticker)
  m3 <- feols(operating_margin ~ post_x_replicability | ticker + year_quarter,
              data = panel, cluster = ~ticker)
  list(rev = m1, gm = m2, om = m3)
}

did_base <- run_did(p_base)
did_10k  <- run_did(p_10k)
did_wb   <- run_did(p_wb)

# --- Extract coefficients ---
extract <- function(model_list, label) {
  data.frame(
    Source = label,
    Outcome = c("ln(Revenue)", "Gross Margin", "Operating Margin"),
    Beta = c(coef(model_list$rev)["post_x_replicability"],
             coef(model_list$gm)["post_x_replicability"],
             coef(model_list$om)["post_x_replicability"]),
    SE = c(summary(model_list$rev)$se["post_x_replicability"],
           summary(model_list$gm)$se["post_x_replicability"],
           summary(model_list$om)$se["post_x_replicability"]),
    p = c(pvalue(model_list$rev)["post_x_replicability"],
          pvalue(model_list$gm)["post_x_replicability"],
          pvalue(model_list$om)["post_x_replicability"]),
    N_firms = c(n_distinct(model_list$rev$obs_selection$obsRemoved),
                n_distinct(model_list$gm$obs_selection$obsRemoved),
                n_distinct(model_list$om$obs_selection$obsRemoved))
  )
}

# Get firm counts from panels
n_base <- n_distinct(p_base$ticker)
n_10k  <- n_distinct(p_10k$ticker)
n_wb   <- n_distinct(p_wb$ticker)

extract2 <- function(model_list, label, n_firms) {
  data.frame(
    Source = label,
    Outcome = c("ln(Revenue)", "Gross Margin", "Operating Margin"),
    Beta = round(c(coef(model_list$rev)["post_x_replicability"],
                   coef(model_list$gm)["post_x_replicability"],
                   coef(model_list$om)["post_x_replicability"]), 3),
    SE = round(c(summary(model_list$rev)$se["post_x_replicability"],
                 summary(model_list$gm)$se["post_x_replicability"],
                 summary(model_list$om)$se["post_x_replicability"]), 3),
    p_value = round(c(pvalue(model_list$rev)["post_x_replicability"],
                      pvalue(model_list$gm)["post_x_replicability"],
                      pvalue(model_list$om)["post_x_replicability"]), 4),
    N_firms = n_firms,
    stringsAsFactors = FALSE
  )
}

tab <- rbind(
  extract2(did_base, "Baseline (mixed)", n_base),
  extract2(did_10k,  "10-K only",        n_10k),
  extract2(did_wb,   "Wayback only",     n_wb)
)

# Add significance stars
tab$Sig <- ifelse(tab$p_value < 0.01, "***",
           ifelse(tab$p_value < 0.05, "**",
           ifelse(tab$p_value < 0.10, "*", "")))

cat("\n")
cat("============================================================\n")
cat("COMPARISON: DiD COEFFICIENTS BY TEXT SOURCE\n")
cat("(Trimmed 2020+ sample, Firm + Quarter FE, clustered SE)\n")
cat("============================================================\n\n")

# Print as wide table
for (outcome in c("ln(Revenue)", "Gross Margin", "Operating Margin")) {
  cat(sprintf("%-20s", outcome))
  sub <- tab[tab$Outcome == outcome, ]
  for (i in 1:nrow(sub)) {
    cat(sprintf("  |  %-16s β=%7.3f%s (SE=%.3f, p=%.4f, n=%d)",
        sub$Source[i], sub$Beta[i], sub$Sig[i], sub$SE[i], sub$p_value[i], sub$N_firms[i]))
  }
  cat("\n")
}

# Also save to file
dir.create("results", showWarnings = FALSE)
write.csv(tab, "results/did_textsource_comparison.csv", row.names = FALSE)
cat("\nSaved: results/did_textsource_comparison.csv\n")

# Score distribution comparison
cat("\n\nSCORE DISTRIBUTIONS:\n")
for (info in list(
  list("Baseline", rep_base),
  list("10-K only", rep_10k),
  list("Wayback", rep_wb)
)) {
  s <- info[[2]]$replicability_score
  cat(sprintf("  %-10s mean=%.4f  sd=%.4f  (n=%d)\n",
      info[[1]], mean(s, na.rm=TRUE), sd(s, na.rm=TRUE), sum(!is.na(s))))
}
