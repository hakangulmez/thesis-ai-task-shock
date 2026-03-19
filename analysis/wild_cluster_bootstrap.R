# =============================================================
# Wild Cluster Bootstrap Inference
# =============================================================
# Implements the WCR (Wild Cluster Restricted) bootstrap
# following Cameron, Gelbach & Miller (2008) and
# Webb (2023, Stata Journal) with Rademacher weights.
#
# Two main results:
#   1. replicability_score on ln_revenue (WB-only, 2020+)
#   2. contrast_score on gross_margin (WB-only, 2020+)
# =============================================================

library(fixest)
library(dplyr)

set.seed(42)
B <- 9999  # bootstrap iterations

# --- Load data ---
df <- read.csv("data/processed/master_panel.csv")
df <- df %>%
  mutate(year_quarter = paste0(fiscal_year, "Q", fiscal_quarter)) %>%
  filter(fiscal_year >= 2020, text_source == "wayback")

cat("Wayback-only, 2020+ panel:", nrow(df), "rows,", n_distinct(df$ticker), "firms\n\n")

# =============================================================
# Wild Cluster Bootstrap (Restricted)
# =============================================================
# Under H0: beta = 0, the restricted model has no treatment.
# 1. Estimate restricted model (no treatment variable)
# 2. Get residuals and fitted values from restricted model
# 3. For each bootstrap rep:
#    a. Draw Rademacher weights (+1/-1) at cluster level
#    b. Construct y* = fitted + weight_g * residual
#    c. Re-estimate unrestricted model on y*
#    d. Compute t-statistic
# 4. Bootstrap p-value = fraction of |t*| >= |t_observed|
# =============================================================

wild_cluster_boot <- function(data, outcome, treatment, B = 9999) {

  # Drop rows with NA in outcome or treatment to ensure alignment
  keep_cols <- c(outcome, treatment, "ticker", "year_quarter")
  data <- data[complete.cases(data[, keep_cols]), ]

  clusters <- unique(data$ticker)
  G <- length(clusters)

  # Unrestricted model (with treatment)
  fml_u <- as.formula(paste0(outcome, " ~ ", treatment, " | ticker + year_quarter"))
  m_u <- feols(fml_u, data = data, cluster = ~ticker)

  beta_obs <- coef(m_u)[treatment]
  se_obs <- summary(m_u)$se[treatment]
  t_obs <- beta_obs / se_obs
  p_conv <- pvalue(m_u)[treatment]

  cat(sprintf("  Observed: beta = %.4f, SE = %.4f, t = %.4f, p(conventional) = %.4f\n",
              beta_obs, se_obs, t_obs, p_conv))

  # Restricted model (without treatment)
  fml_r <- as.formula(paste0(outcome, " ~ 1 | ticker + year_quarter"))
  m_r <- feols(fml_r, data = data)

  # Get residuals and fitted from restricted model
  resid_r <- residuals(m_r)
  fitted_r <- fitted(m_r)

  cat(sprintf("  N = %d, G = %d, residual length = %d\n", nrow(data), G, length(resid_r)))

  # Map cluster membership
  cluster_map <- match(data$ticker, clusters)

  # Bootstrap
  t_boot <- numeric(B)

  cat(sprintf("  Running %d bootstrap iterations (G = %d clusters)...\n", B, G))

  for (b in 1:B) {
    # Rademacher weights: +1 or -1 per cluster
    weights_g <- sample(c(-1, 1), G, replace = TRUE)
    weights_i <- weights_g[cluster_map]

    # Construct bootstrap outcome
    data$y_boot <- fitted_r + weights_i * resid_r

    # Re-estimate unrestricted model on bootstrap outcome
    fml_boot <- as.formula(paste0("y_boot ~ ", treatment, " | ticker + year_quarter"))
    m_boot <- tryCatch(
      suppressMessages(feols(fml_boot, data = data, cluster = ~ticker)),
      error = function(e) NULL,
      warning = function(w) suppressMessages(feols(fml_boot, data = data, cluster = ~ticker))
    )

    if (!is.null(m_boot) && treatment %in% names(coef(m_boot))) {
      b_beta <- coef(m_boot)[treatment]
      b_se <- summary(m_boot)$se[treatment]
      t_boot[b] <- b_beta / b_se
    } else {
      t_boot[b] <- 0
    }
  }

  # Two-sided bootstrap p-value
  p_boot <- mean(abs(t_boot) >= abs(t_obs))

  cat(sprintf("  Bootstrap p-value: %.4f (two-sided, B = %d)\n", p_boot, B))

  list(
    outcome = outcome,
    treatment = treatment,
    beta = beta_obs,
    se = se_obs,
    t_obs = t_obs,
    p_conventional = p_conv,
    p_bootstrap = p_boot,
    G = G,
    N = nobs(m_u),
    t_boot = t_boot
  )
}

# =============================================================
# Result 1: replicability_score on ln_revenue
# =============================================================
cat("=" , rep("=", 59), "\n", sep = "")
cat("RESULT 1: replicability_score -> ln(Revenue)\n")
cat("Sample: Wayback-only, 2020+ trimmed\n")
cat("=" , rep("=", 59), "\n")

r1 <- wild_cluster_boot(df, "ln_revenue", "post_x_replicability", B)

# =============================================================
# Result 2: contrast_score on gross_margin
# =============================================================
cat("\n")
cat("=" , rep("=", 59), "\n", sep = "")
cat("RESULT 2: contrast_score -> Gross Margin\n")
cat("Sample: Wayback-only, 2020+ trimmed\n")
cat("=" , rep("=", 59), "\n")

r2 <- wild_cluster_boot(df, "gross_margin", "post_x_contrast", B)

# =============================================================
# Summary table
# =============================================================
cat("\n\n")
cat("=" , rep("=", 69), "\n", sep = "")
cat("WILD CLUSTER BOOTSTRAP INFERENCE SUMMARY\n")
cat("Method: WCR bootstrap, Rademacher weights, B = 9999\n")
cat("=" , rep("=", 69), "\n\n")

cat(sprintf("%-35s %12s %12s\n", "", "Result 1", "Result 2"))
cat(sprintf("%-35s %12s %12s\n", "", "ln(Revenue)", "Gross Margin"))
cat(strrep("-", 69), "\n")
cat(sprintf("%-35s %12s %12s\n", "Treatment", "high_score", "contrast"))
cat(sprintf("%-35s %12.4f %12.4f\n", "Beta", r1$beta, r2$beta))
cat(sprintf("%-35s %12.4f %12.4f\n", "Clustered SE", r1$se, r2$se))
cat(sprintf("%-35s %12.4f %12.4f\n", "t-statistic", r1$t_obs, r2$t_obs))
cat(sprintf("%-35s %12.4f %12.4f\n", "p-value (conventional clustered)", r1$p_conventional, r2$p_conventional))
cat(sprintf("%-35s %12.4f %12.4f\n", "p-value (wild cluster bootstrap)", r1$p_bootstrap, r2$p_bootstrap))
cat(sprintf("%-35s %12d %12d\n", "N (observations)", r1$N, r2$N))
cat(sprintf("%-35s %12d %12d\n", "G (clusters)", r1$G, r2$G))
cat(strrep("-", 69), "\n")

# Significance assessment
for (r in list(r1, r2)) {
  sig_conv <- ifelse(r$p_conventional < 0.01, "***",
              ifelse(r$p_conventional < 0.05, "**",
              ifelse(r$p_conventional < 0.10, "*", "ns")))
  sig_boot <- ifelse(r$p_bootstrap < 0.01, "***",
              ifelse(r$p_bootstrap < 0.05, "**",
              ifelse(r$p_bootstrap < 0.10, "*", "ns")))
  cat(sprintf("\n%s -> %s:\n", r$treatment, r$outcome))
  cat(sprintf("  Conventional: %s (p=%.4f)\n", sig_conv, r$p_conventional))
  cat(sprintf("  Bootstrap:    %s (p=%.4f)\n", sig_boot, r$p_bootstrap))
  if (sig_conv == sig_boot) {
    cat("  => Inference UNCHANGED by bootstrap correction\n")
  } else {
    cat("  => Inference CHANGES with bootstrap correction\n")
  }
}

cat("\nDone.\n")
