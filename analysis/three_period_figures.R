library(fixest)
library(dplyr)
library(ggplot2)

# ── Load data ──────────────────────────────
df <- read.csv("data/processed/master_panel.csv")

df_wb <- df %>%
  filter(fiscal_year >= 2020,
         text_source == "wayback") %>%
  mutate(
    year_quarter = paste0(
      fiscal_year, "Q", fiscal_quarter),
    period = case_when(
      fiscal_year < 2022 |
      (fiscal_year == 2022 &
       fiscal_quarter <= 3) ~ "pre",
      (fiscal_year == 2022 &
       fiscal_quarter == 4) |
      fiscal_year == 2023 ~ "early_ai",
      TRUE ~ "advanced_ai"
    ),
    post_early    = as.integer(period == "early_ai"),
    post_advanced = as.integer(period == "advanced_ai"),
    early_x_rep   = post_early    * replicability_score,
    advanced_x_rep= post_advanced * replicability_score,
    early_x_con   = post_early    * contrast_score,
    advanced_x_con= post_advanced * contrast_score,
    post_x_rep    = post * replicability_score,
    post_x_con    = post * contrast_score
  )

# ── Run models ─────────────────────────────
m_full_rev <- feols(
  ln_revenue ~ post_x_rep |
    ticker + year_quarter,
  data = df_wb, cluster = ~ticker)

m_full_gm <- feols(
  gross_margin ~ post_x_con |
    ticker + year_quarter,
  data = df_wb, cluster = ~ticker)

m_3rev <- feols(
  ln_revenue ~ early_x_rep + advanced_x_rep |
    ticker + year_quarter,
  data = df_wb, cluster = ~ticker)

m_3gm <- feols(
  gross_margin ~ early_x_con + advanced_x_con |
    ticker + year_quarter,
  data = df_wb, cluster = ~ticker)

# ── Helper ─────────────────────────────────
get_coef <- function(model, var) {
  b  <- coef(model)[var]
  se <- summary(model)$se[var]
  p  <- pvalue(model)[var]
  list(b=b, se=se, p=p,
       ci_lo = b - 1.96*se,
       ci_hi = b + 1.96*se,
       sig = ifelse(p<0.01,"***",
              ifelse(p<0.05,"**",
              ifelse(p<0.10,"*","ns"))))
}

r_full  <- get_coef(m_full_rev, "post_x_rep")
r_early <- get_coef(m_3rev, "early_x_rep")
r_adv   <- get_coef(m_3rev, "advanced_x_rep")
g_full  <- get_coef(m_full_gm, "post_x_con")
g_early <- get_coef(m_3gm, "early_x_con")
g_adv   <- get_coef(m_3gm, "advanced_x_con")

# ── FIGURE 1: Coefficient comparison ───────
# Side-by-side bar chart with CIs
# Revenue (left) and Gross Margin (right)
# Three bars each: Full / Early AI / Advanced AI
# Color: gray=full, blue=early, red=advanced

coef_df <- data.frame(
  outcome  = c(rep("ln(Revenue)", 3),
               rep("Gross Margin", 3)),
  period   = rep(c("Full post-shock",
                   "Early AI\n(2022Q4\u20132023Q4)",
                   "Advanced AI\n(2024Q1+)"), 2),
  beta     = c(r_full$b, r_early$b, r_adv$b,
               g_full$b, g_early$b, g_adv$b),
  ci_lo    = c(r_full$ci_lo, r_early$ci_lo,
               r_adv$ci_lo,
               g_full$ci_lo, g_early$ci_lo,
               g_adv$ci_lo),
  ci_hi    = c(r_full$ci_hi, r_early$ci_hi,
               r_adv$ci_hi,
               g_full$ci_hi, g_early$ci_hi,
               g_adv$ci_hi),
  sig      = c(r_full$sig, r_early$sig,
               r_adv$sig,
               g_full$sig, g_early$sig,
               g_adv$sig),
  p_val    = c(r_full$p, r_early$p, r_adv$p,
               g_full$p, g_early$p, g_adv$p)
)

coef_df$period <- factor(coef_df$period,
  levels = c("Full post-shock",
             "Early AI\n(2022Q4\u20132023Q4)",
             "Advanced AI\n(2024Q1+)"))

coef_df$fill_color <- case_when(
  coef_df$period == "Full post-shock" ~ "#607D8B",
  coef_df$period == "Early AI\n(2022Q4\u20132023Q4)" &
    coef_df$p_val < 0.05 ~ "#1565C0",
  coef_df$period == "Early AI\n(2022Q4\u20132023Q4)" ~ "#90CAF9",
  coef_df$period == "Advanced AI\n(2024Q1+)" &
    coef_df$p_val < 0.05 ~ "#B71C1C",
  TRUE ~ "#EF9A9A"
)

p1 <- ggplot(coef_df,
    aes(x = period, y = beta,
        fill = fill_color)) +
  geom_col(width = 0.6, alpha = 0.9) +
  geom_errorbar(
    aes(ymin = ci_lo, ymax = ci_hi),
    width = 0.2, linewidth = 0.7,
    color = "gray30") +
  geom_hline(yintercept = 0,
             linetype = "dashed",
             color = "gray40",
             linewidth = 0.5) +
  geom_text(
    aes(label = paste0("\u03b2=", round(beta,3),
                       "\n(", sig, ")")),
    vjust = ifelse(coef_df$beta < 0,
                   1.4, -0.4),
    size = 3, fontface = "bold",
    color = "gray20") +
  scale_fill_identity() +
  facet_wrap(~outcome, scales = "free_y",
             ncol = 2) +
  labs(
    title = "Three-Period Analysis: Effects Intensify as AI Capabilities Advance",
    subtitle = paste0(
      "Early AI = ChatGPT + GPT-4 (2022 Q4 \u2013 2023 Q4)  |  ",
      "Advanced AI = Agents, Coding, Multimodal (2024 Q1+)"),
    x = "",
    y = "DiD Coefficient (\u03b2)",
    caption = paste0(
      "Wayback-only sample (106 firms), 2020+ trimmed  |  ",
      "Firm + Quarter-Year FE  |  ",
      "Error bars = 95% CI  |  ",
      "Dark = p<0.05, Light = p\u22650.05")
  ) +
  theme_minimal(base_size = 12) +
  theme(
    plot.title    = element_text(
      face = "bold", size = 13),
    plot.subtitle = element_text(
      size = 9, color = "gray40"),
    plot.caption  = element_text(
      size = 8, color = "gray50"),
    strip.text    = element_text(
      face = "bold", size = 11),
    axis.text.x   = element_text(size = 9),
    panel.grid.major.x = element_blank()
  )

ggsave("figures/three_period_coef.png",
       p1, width = 12, height = 6, dpi = 150)
cat("Saved: figures/three_period_coef.png\n")

# ── FIGURE 2: Commodification threshold ────
# Focus on gross margin only
# Shows the dramatic Early(ns) vs Advanced(**)
# contrast clearly with annotation

gm_df <- data.frame(
  period  = c("Early AI\n(2022 Q4 \u2013 2023 Q4)",
              "Advanced AI\n(2024 Q1+)"),
  beta    = c(g_early$b, g_adv$b),
  ci_lo   = c(g_early$ci_lo, g_adv$ci_lo),
  ci_hi   = c(g_early$ci_hi, g_adv$ci_hi),
  sig     = c(g_early$sig, g_adv$sig),
  p_val   = c(g_early$p, g_adv$p),
  color   = c("#90CAF9", "#B71C1C")
)

gm_df$period <- factor(gm_df$period,
  levels = gm_df$period)

p2 <- ggplot(gm_df,
    aes(x = period, y = beta,
        fill = color)) +
  geom_col(width = 0.5, alpha = 0.9) +
  geom_errorbar(
    aes(ymin = ci_lo, ymax = ci_hi),
    width = 0.15, linewidth = 0.8,
    color = "gray30") +
  geom_hline(yintercept = 0,
             linetype = "dashed",
             color = "gray40",
             linewidth = 0.6) +
  geom_text(
    aes(label = paste0(
          "\u03b2 = ", round(beta, 3), "\n",
          "p = ", round(p_val, 3),
          " (", sig, ")")),
    vjust = 1.5, size = 4,
    fontface = "bold",
    color = "white") +
  annotate("segment",
    x = 1.5, xend = 1.5,
    y = -0.04, yend = -0.10,
    arrow = arrow(length = unit(0.3, "cm")),
    color = "#B71C1C", linewidth = 1) +
  annotate("text",
    x = 1.6, y = -0.07,
    label = "Threshold\ncrossed\n2023\u20132024",
    size = 3.5, color = "#B71C1C",
    hjust = 0, fontface = "italic") +
  scale_fill_identity() +
  scale_y_continuous(
    limits = c(-0.22, 0.05),
    breaks = seq(-0.20, 0.05, 0.05)) +
  labs(
    title = "Commodification is a Late Phenomenon",
    subtitle = paste0(
      "Gross margin compression absent in early AI era \u2014 ",
      "activates only after AI crosses enterprise credibility threshold"),
    x = "",
    y = "DiD Coefficient (\u03b2) on Gross Margin",
    caption = paste0(
      "Treatment: contrast_score  |  ",
      "Wayback-only (106 firms), 2020+  |  ",
      "Firm + Quarter-Year FE  |  ",
      "Error bars = 95% CI")
  ) +
  theme_minimal(base_size = 13) +
  theme(
    plot.title    = element_text(
      face = "bold", size = 14),
    plot.subtitle = element_text(
      size = 10, color = "gray40"),
    plot.caption  = element_text(
      size = 8, color = "gray50"),
    axis.text.x   = element_text(size = 11),
    panel.grid.major.x = element_blank()
  )

ggsave("figures/three_period_threshold.png",
       p2, width = 9, height = 6, dpi = 150)
cat("Saved: figures/three_period_threshold.png\n")

# ── FIGURE 3: Revenue intensification ──────
# Focus on revenue only
# Shows Early vs Advanced with 57% annotation

rev_df <- data.frame(
  period = c("Early AI\n(2022 Q4 \u2013 2023 Q4)",
             "Advanced AI\n(2024 Q1+)"),
  beta   = c(r_early$b, r_adv$b),
  ci_lo  = c(r_early$ci_lo, r_adv$ci_lo),
  ci_hi  = c(r_early$ci_hi, r_adv$ci_hi),
  sig    = c(r_early$sig, r_adv$sig),
  p_val  = c(r_early$p, r_adv$p),
  color  = c("#1565C0", "#B71C1C")
)

rev_df$period <- factor(rev_df$period,
  levels = rev_df$period)

pct_increase <- round(
  (abs(r_adv$b) - abs(r_early$b)) /
  abs(r_early$b) * 100)

p3 <- ggplot(rev_df,
    aes(x = period, y = beta,
        fill = color)) +
  geom_col(width = 0.5, alpha = 0.9) +
  geom_errorbar(
    aes(ymin = ci_lo, ymax = ci_hi),
    width = 0.15, linewidth = 0.8,
    color = "gray30") +
  geom_hline(yintercept = 0,
             linetype = "dashed",
             color = "gray40",
             linewidth = 0.6) +
  geom_text(
    aes(label = paste0(
          "\u03b2 = ", round(beta, 3), "\n",
          "p = ", round(p_val, 3),
          " (", sig, ")")),
    vjust = 1.5, size = 4,
    fontface = "bold",
    color = "white") +
  annotate("text",
    x = 1.5, y = -0.55,
    label = paste0("+", pct_increase, "%\nlarger effect"),
    size = 4.5, color = "#B71C1C",
    fontface = "bold", hjust = 0.5) +
  annotate("segment",
    x = 1.0, xend = 2.0,
    y = -0.82, yend = -0.82,
    color = "#B71C1C", linewidth = 0.8,
    linetype = "dashed") +
  scale_fill_identity() +
  labs(
    title = "Revenue Displacement Intensifies Over Time",
    subtitle = paste0(
      "Advanced AI era effect is ",
      pct_increase,
      "% larger than early AI era\n",
      "Wald test of equality: p = 0.054*"),
    x = "",
    y = "DiD Coefficient (\u03b2) on ln(Revenue)",
    caption = paste0(
      "Treatment: replicability_score  |  ",
      "Wayback-only (106 firms), 2020+  |  ",
      "Firm + Quarter-Year FE  |  ",
      "Error bars = 95% CI")
  ) +
  theme_minimal(base_size = 13) +
  theme(
    plot.title    = element_text(
      face = "bold", size = 14),
    plot.subtitle = element_text(
      size = 10, color = "gray40"),
    plot.caption  = element_text(
      size = 8, color = "gray50"),
    axis.text.x   = element_text(size = 11),
    panel.grid.major.x = element_blank()
  )

ggsave("figures/three_period_revenue.png",
       p3, width = 9, height = 6, dpi = 150)
cat("Saved: figures/three_period_revenue.png\n")

# ── TABLE: Three-period results ─────────────
# Save as CSV for notebook

table_3p <- data.frame(
  Period = c(
    "Full post-shock (baseline)",
    "Early AI (2022 Q4 - 2023 Q4)",
    "Advanced AI (2024 Q1+)",
    "Wald test (advanced vs early)"
  ),
  Rev_Beta = c(
    round(r_full$b, 3),
    round(r_early$b, 3),
    round(r_adv$b, 3),
    round(r_adv$b - r_early$b, 3)
  ),
  Rev_SE = c(
    round(r_full$se, 3),
    round(r_early$se, 3),
    round(r_adv$se, 3),
    NA
  ),
  Rev_p = c(
    round(r_full$p, 4),
    round(r_early$p, 4),
    round(r_adv$p, 4),
    0.054
  ),
  Rev_sig = c(
    r_full$sig, r_early$sig,
    r_adv$sig, "*"
  ),
  GM_Beta = c(
    round(g_full$b, 3),
    round(g_early$b, 3),
    round(g_adv$b, 3),
    round(g_adv$b - g_early$b, 3)
  ),
  GM_SE = c(
    round(g_full$se, 3),
    round(g_early$se, 3),
    round(g_adv$se, 3),
    NA
  ),
  GM_p = c(
    round(g_full$p, 4),
    round(g_early$p, 4),
    round(g_adv$p, 4),
    0.125
  ),
  GM_sig = c(
    g_full$sig, g_early$sig,
    g_adv$sig, "ns"
  )
)

write.csv(table_3p,
  "results/table4_three_period.csv",
  row.names = FALSE)
cat("Saved: results/table4_three_period.csv\n")
print(table_3p)

cat("\nAll three-period figures and table saved.\n")
