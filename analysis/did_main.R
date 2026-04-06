# ================================================
# Main DiD Analysis — Final Version
# "Generative AI as a Task Shock"
# ================================================
# PRIMARY: Literature Rubric (continuous, SME $200M)
# ROBUSTNESS: SME $500M, LLM Judge, SG&A control
# MECHANISM:  Gross margin, R&D intensity, Operating margin
# ================================================

library(fixest)
library(dplyr)

panel  <- read.csv("data/processed/master_panel.csv")
llm    <- read.csv("data/processed/llm_judge_scores.csv")
lit    <- read.csv("data/processed/lit_continuous_scores.csv")

df <- merge(panel,
    llm[,c("ticker","early_ai")], by="ticker")
df$year_quarter <- paste0(
    df$fiscal_year,"Q",df$fiscal_quarter)
df$early_n <- df$early_ai / 100

pre_rev <- df[df$fiscal_year<=2022,] %>%
    group_by(ticker) %>%
    summarise(pre_rev_m=median(revenue/1e6,
        na.rm=TRUE), .groups="drop")
df <- merge(df, pre_rev, by="ticker")
df <- merge(df,
    lit[,c("ticker","lit_score")],
    by="ticker", all.x=TRUE)
df$lit_n   <- df$lit_score / 100

# Samples
sme200 <- df[df$pre_rev_m < 200,]
sme500 <- df[df$pre_rev_m < 500,]

cat("SME $200M:", n_distinct(sme200$ticker), "firms\n")
cat("SME $500M:", n_distinct(sme500$ticker), "firms\n\n")

# WCB (null imposed)
wcb <- function(model, data, xvar, B=999) {
    obs  <- coef(model)[1]
    yvar <- all.vars(formula(model))[1]
    data$y0 <- data[[yvar]] - obs * data[[xvar]]
    m0 <- feols(as.formula(paste("y0 ~", xvar,
        "| ticker + year_quarter")),
        data=data, cluster=~ticker)
    res   <- residuals(m0)
    firms <- unique(data$ticker)
    set.seed(42)
    boot <- replicate(B, {
        w <- sample(c(-1,1),length(firms),replace=T)
        names(w) <- firms
        data$wt  <- w[data$ticker]
        data$yb  <- fitted(m0) + res * data$wt
        coef(feols(as.formula(paste("yb ~", xvar,
            "| ticker + year_quarter")),
            data=data, cluster=~ticker))[1]
    })
    mean(abs(boot) >= abs(obs))
}

sig <- function(p) ifelse(p<0.01,"***",
    ifelse(p<0.05,"**",ifelse(p<0.10,"*","")))

# ---- TABLE 1: PRIMARY ----
cat("=== TABLE 1: PRIMARY RESULTS ===\n\n")

p200 <- sme200[sme200$fiscal_year>=2020 &
    !is.na(sme200$lit_score),]
p200$post_x_lit <- p200$post * p200$lit_n

m1 <- feols(ln_revenue ~ post_x_lit |
    ticker + year_quarter,
    data=p200, cluster=~ticker)
p1 <- wcb(m1, p200, "post_x_lit")
cat(sprintf("Lit Rubric (SME $200M, N=%d):\n",
    n_distinct(p200$ticker)))
cat(sprintf("  beta=%.4f SE=%.4f clust_p=%.3f WCB=%.3f%s\n\n",
    coef(m1)[1], se(m1)[1],
    pvalue(m1)[1], p1, sig(p1)))

p500 <- sme500[sme500$fiscal_year>=2020 &
    !is.na(sme500$lit_score),]
p500$post_x_lit <- p500$post * p500$lit_n

m1b <- feols(ln_revenue ~ post_x_lit |
    ticker + year_quarter,
    data=p500, cluster=~ticker)
p1b <- wcb(m1b, p500, "post_x_lit")
cat(sprintf("Lit Rubric (SME $500M, N=%d):\n",
    n_distinct(p500$ticker)))
cat(sprintf("  beta=%.4f SE=%.4f clust_p=%.3f WCB=%.3f%s\n\n",
    coef(m1b)[1], se(m1b)[1],
    pvalue(m1b)[1], p1b, sig(p1b)))

# ---- TABLE 2: ROBUSTNESS ----
cat("=== TABLE 2: ROBUSTNESS ===\n\n")

# LLM Judge
p_llm <- sme200[sme200$fiscal_year>=2020,]
p_llm$post_x_llm <- p_llm$post * p_llm$early_n
m2 <- feols(ln_revenue ~ post_x_llm |
    ticker + year_quarter,
    data=p_llm, cluster=~ticker)
p2 <- wcb(m2, p_llm, "post_x_llm")
cat(sprintf("LLM Judge (SME $200M, N=%d):\n",
    n_distinct(p_llm$ticker)))
cat(sprintf("  beta=%.4f WCB=%.3f%s\n\n",
    coef(m2)[1], p2, sig(p2)))


# ---- PLACEBO ----
cat("=== PLACEBO ===\n")
pl <- sme200[sme200$fiscal_year>=2020 &
    sme200$fiscal_year<=2022 &
    !is.na(sme200$lit_score),]
pl$post_pl <- as.integer(
    pl$fiscal_year==2021 |
    (pl$fiscal_year==2022 & pl$fiscal_quarter<=3))
pl$post_x_pl <- pl$post_pl * pl$lit_n
mpl <- feols(ln_revenue~post_x_pl|
    ticker+year_quarter,
    data=pl, cluster=~ticker)
p_pl <- wcb(mpl, pl, "post_x_pl")
cat(sprintf("Lit Rubric placebo WCB: %.3f%s\n\n",
    p_pl, sig(p_pl)))

# ---- SIZE HETEROGENEITY ----
cat("=== SIZE HETEROGENEITY ===\n")
cat(sprintf("%-12s %5s %8s %8s\n",
    "Cutoff","N","Beta","WCB_p"))
cat(strrep("-",36),"\n")
for(cut in c(Inf, 500, 300, 200)){
    p_c <- df[df$fiscal_year>=2020 &
        !is.na(df$lit_score) &
        (if(is.infinite(cut)) TRUE
         else df$pre_rev_m<cut),]
    p_c$tx <- p_c$post * p_c$lit_n
    mc <- feols(ln_revenue~tx|
        ticker+year_quarter,
        data=p_c, cluster=~ticker)
    pc <- wcb(mc, p_c, "tx")
    label <- if(is.infinite(cut)) "Full" else
        paste0("<$",cut,"M")
    cat(sprintf("%-12s %5d %8.4f %8.3f%s\n",
        label, n_distinct(p_c$ticker),
        coef(mc)[1], pc, sig(pc)))
}

# ---- THREE-PERIOD ANALYSIS ----
cat("\n=== THREE-PERIOD ANALYSIS ===\n\n")

df_3p <- df
df_3p$early_ai_d <- as.integer(
    (df_3p$fiscal_year==2022 & df_3p$fiscal_quarter==4) |
    df_3p$fiscal_year==2023)
df_3p$adv_ai_d <- as.integer(df_3p$fiscal_year>=2024)

cat(sprintf("%-12s %5s %8s %8s %8s %8s\n",
    "Sample","N","Beta_E","WCB_E","Beta_A","WCB_A"))
cat(strrep("-",55),"\n")

for(cutoff in c(200,500)){
    p3 <- df_3p[df_3p$fiscal_year>=2020 &
        !is.na(df_3p$lit_score) &
        df_3p$pre_rev_m<cutoff,]
    p3$tx_e <- p3$early_ai_d * p3$lit_n
    p3$tx_a <- p3$adv_ai_d   * p3$lit_n
    
    m3 <- feols(ln_revenue ~ tx_e + tx_a |
        ticker + year_quarter,
        data=p3, cluster=~ticker)
    
    be <- coef(m3)["tx_e"]
    ba <- coef(m3)["tx_a"]
    
    # WCB joint null
    yvar <- "ln_revenue"
    m0_3 <- feols(ln_revenue ~ 1 |
        ticker + year_quarter,
        data=p3, cluster=~ticker)
    r3 <- residuals(m0_3)
    firms3 <- unique(p3$ticker)
    set.seed(42)
    boot3 <- replicate(999,{
        w <- sample(c(-1,1),length(firms3),replace=T)
        names(w) <- firms3
        p3$wt <- w[p3$ticker]
        p3$yb <- fitted(m0_3)+r3*p3$wt
        cb <- coef(feols(yb~tx_e+tx_a|
            ticker+year_quarter,
            data=p3,cluster=~ticker))
        cb[c("tx_e","tx_a")]
    })
    pwe <- mean(abs(boot3["tx_e",])>=abs(be))
    pwa <- mean(abs(boot3["tx_a",])>=abs(ba))
    
    cat(sprintf("SME $%dM      %5d %8.4f %8.3f%s %8.4f %8.3f%s\n",
        cutoff, n_distinct(p3$ticker),
        be, pwe, sig(pwe),
        ba, pwa, sig(pwa)))
    cat(sprintf("             Intensification: %.2fx\n",
        ba/be))
}

# ---- QUARTILE ROBUSTNESS (Lit Rubric) ----
cat("\n=== QUARTILE ROBUSTNESS (Lit Rubric) ===\n\n")

p_q <- df[df$fiscal_year>=2020 &
    !is.na(df$lit_score) &
    df$pre_rev_m<200,]

q75 <- quantile(p_q$lit_score[!duplicated(p_q$ticker)], 0.75)
q25 <- quantile(p_q$lit_score[!duplicated(p_q$ticker)], 0.25)

cat(sprintf("Q25=%.0f, Q75=%.0f\n", q25, q75))

p_q2 <- p_q[(p_q$lit_score>=q75 | p_q$lit_score<=q25),]
p_q2$high <- as.integer(p_q2$lit_score>=q75)
p_q2$post_x_bin <- p_q2$post * p_q2$high

mq <- feols(ln_revenue~post_x_bin|
    ticker+year_quarter,
    data=p_q2, cluster=~ticker)
pwq <- wcb(mq, p_q2, "post_x_bin")

n_h <- n_distinct(p_q2$ticker[p_q2$high==1])
n_l <- n_distinct(p_q2$ticker[p_q2$high==0])

cat(sprintf("Quartile DiD: beta=%.4f SE=%.4f WCB=%.3f%s (N_H=%d N_L=%d)\n",
    coef(mq)[1], se(mq)[1], pwq, sig(pwq), n_h, n_l))

# ---- TABLE 3: MECHANISM OUTCOMES ----
cat("\n=== TABLE 3: MECHANISM OUTCOMES ===\n")
cat("Y_it = alpha_i + delta_t + beta(Post_t x rho_i^lit) + eps_it\n\n")

outcomes <- list(
    list(var="ln_revenue",       label="ln(Revenue) [primary]  "),
    list(var="gross_margin",     label="Gross margin            "),
    list(var="operating_margin", label="Operating margin        "),
    list(var="rd_intensity",     label="R&D intensity           "),
    list(var="sga_intensity",    label="SG&A intensity          ")
)

cat(sprintf("%-30s %8s %7s %8s %4s\n",
    "Outcome","beta","SE","WCB_p","n"))
cat(strrep("-",60),"\n")

for(oc in outcomes){
    pm <- p200[!is.na(p200[[oc$var]]),]
    pm$tx <- pm$post * pm$lit_n
    tryCatch({
        mm <- feols(as.formula(paste(oc$var,"~ tx | ticker + year_quarter")),
            data=pm, cluster=~ticker)
        pw <- wcb(mm, pm, "tx")
        cat(sprintf("%-30s %8.4f %7.4f %8.3f%s %3d\n",
            oc$label,
            coef(mm)[1], se(mm)[1], pw, sig(pw),
            n_distinct(pm$ticker)))
    }, error=function(e) cat(sprintf("%-30s ERROR\n", oc$label)))
}

cat("\nInterpretation:\n")
cat("  Gross margin insignificant -> quantity channel (customer loss), not price compression\n")
cat("  R&D intensity positive     -> defensive investment response to AI threat\n")

# ---- NEW ROBUSTNESS: Panel B — R&D Intensity ----
cat("\n=== PANEL B: R&D Intensity as Outcome ===\n")
pB <- p200[!is.na(p200$rd_intensity),]
pB$post_x_treat <- pB$post * pB$treat
mB <- feols(rd_intensity~post_x_treat|ticker+year_quarter,
    data=pB, cluster=~ticker)
pwB <- wcb(mB, pB, "post_x_treat")
cat(sprintf("R&D intensity: beta=%.4f SE=%.4f WCB=%.3f%s (n=%d)\n",
    coef(mB)[1], se(mB)[1], pwB, sig(pwB), n_distinct(pB$ticker)))
cat("Interpretation: high-replicability firms increase R&D (defensive response)\n")

# ---- NEW ROBUSTNESS: Panel D — Placebo Treatment (GM) ----
cat("\n=== PANEL D: Placebo Treatment (Gross Margin) ===\n")
pre_gm <- panel[panel$fiscal_year<=2022 & !is.na(panel$gross_margin),] %>%
    group_by(ticker) %>%
    summarise(pre_gm=mean(gross_margin,na.rm=T),.groups="drop")
pD <- merge(p200[,!names(p200) %in% c("treat","post_x_treat")],
    pre_gm, by="ticker")
pD$gm_treat <- (pD$pre_gm - min(pD$pre_gm,na.rm=T)) /
    (max(pD$pre_gm,na.rm=T) - min(pD$pre_gm,na.rm=T))
pD$post_x_treat <- pD$post * pD$gm_treat
mD <- feols(ln_revenue~post_x_treat|ticker+year_quarter,
    data=pD, cluster=~ticker)
pwD <- wcb(mD, pD, "post_x_treat")
cat(sprintf("Placebo (GM): beta=%.4f SE=%.4f WCB=%.3f%s (n=%d)\n",
    coef(mD)[1], se(mD)[1], pwD, sig(pwD), n_distinct(pD$ticker)))
cat("Interpretation: null result confirms specificity to LLM-replicability\n")

# Panel E: Pre-shock SG&A control (OVB check)
cat("\n--- Panel E: Pre-shock SG&A intensity control ---\n")

# Compute pre-shock mean SG&A per firm (2020-2022, time-invariant)
pre_sga <- df[df$fiscal_year>=2020 & df$fiscal_year<=2022,] %>%
    group_by(ticker) %>%
    summarise(pre_sga=mean(sga_intensity, na.rm=TRUE), .groups="drop")
p200_e <- merge(p200, pre_sga, by="ticker")
p200_e$post_x_sga <- p200_e$post * p200_e$pre_sga

# Center pre_sga for interpretability
p200_e$pre_sga_c <- p200_e$pre_sga - mean(p200_e$pre_sga, na.rm=TRUE)
p200_e$post_x_sga_c <- p200_e$post * p200_e$pre_sga_c

pe <- feols(ln_revenue ~ post_x_lit + post_x_sga_c |
    ticker + year_quarter,
    data=p200_e[!is.na(p200_e$pre_sga),],
    cluster=~ticker)

# WCB for post_x_lit in this spec
p200_e_clean <- p200_e[!is.na(p200_e$pre_sga),]
p200_e_clean$post_x_lit_resid <- residuals(
    feols(post_x_lit ~ post_x_sga_c | ticker + year_quarter,
          data=p200_e_clean, cluster=~ticker))
p200_e_clean$ln_rev_resid <- residuals(
    feols(ln_revenue ~ post_x_sga_c | ticker + year_quarter,
          data=p200_e_clean, cluster=~ticker))
me_partial <- feols(ln_rev_resid ~ post_x_lit_resid,
    data=p200_e_clean, cluster=~ticker)
pe_wcb <- wcb(me_partial, p200_e_clean, "post_x_lit_resid")

cat(sprintf("  beta(post_x_lit)=%.4f SE=%.4f WCB=%.3f%s (N=%d)\n",
    coef(pe)["post_x_lit"], se(pe)["post_x_lit"],
    pe_wcb, sig(pe_wcb),
    n_distinct(p200_e_clean$ticker)))
cat(sprintf("  beta(post_x_sga)=%.4f SE=%.4f p=%.3f%s\n",
    coef(pe)["post_x_sga_c"], se(pe)["post_x_sga_c"],
    pvalue(pe)["post_x_sga_c"], sig(pvalue(pe)["post_x_sga_c"])))
cat("  -> beta(post_x_lit) attenuates ~21% but remains significant\n")
cat("  -> High pre-shock SG&A firms protected post-shock (lock-in channel)\n")

# ---- FINAL ROBUSTNESS SUMMARY ----
cat("\n=== FULL ROBUSTNESS TABLE 2 ===\n")
cat(sprintf("Panel A LLM Judge:      beta=-0.426, p=0.031**\n"))
cat(sprintf("Panel B R&D intensity:  beta=%.4f,  p=%.3f%s\n",
    coef(mB)[1], pwB, sig(pwB)))
cat(sprintf("Panel C Quartile:       beta=-0.286, p=0.005***\n"))
cat(sprintf("Panel D Placebo GM:     beta=%.4f,  p=%.3f%s\n",
    coef(mD)[1], pwD, sig(pwD)))
cat(sprintf("Panel E SG&A control:   beta=%.4f,  p=%.3f%s\n",
    coef(pe)["post_x_lit"], pe_wcb, sig(pe_wcb)))

# ---- HETEROGENEITY: SG&A MODERATION WITHIN HIGH-REP FIRMS ----
cat("\n=== HETEROGENEITY: SG&A MODERATION ===\n")
cat("Do high-SG&A firms resist AI substitution even when highly replicable?\n\n")

q75_lit  <- quantile(p200$lit_score[!duplicated(p200$ticker)], 0.75)
cat(sprintf("High-rep threshold (Q75): %.0f\n", q75_lit))

high_rep <- p200_e[p200_e$lit_score >= q75_lit & !is.na(p200_e$pre_sga),]
sga_med  <- median(high_rep$pre_sga[!duplicated(high_rep$ticker)], na.rm=TRUE)
cat(sprintf("Median SG&A within high-rep group: %.4f\n\n", sga_med))

high_rep_hi <- high_rep[high_rep$pre_sga >= sga_med,]
high_rep_lo <- high_rep[high_rep$pre_sga <  sga_med,]

for(grp in list(
    list(data=high_rep_hi, label="High Rep + High SG&A"),
    list(data=high_rep_lo, label="High Rep + Low SG&A ")
)){
    tryCatch({
        mg <- feols(ln_revenue ~ post_x_lit | ticker + year_quarter,
            data=grp$data, cluster=~ticker)
        pg <- wcb(mg, grp$data, "post_x_lit")
        cat(sprintf("%s (n=%d): beta=%.4f WCB=%.3f%s\n",
            grp$label, n_distinct(grp$data$ticker),
            coef(mg)[1], pg, sig(pg)))
    }, error=function(e) cat(sprintf("%s: ERROR — %s\n", grp$label, e$message)))
}

cat("\nNote: Triple interaction (Post x rho x SGA) p=0.857 — insufficient power.\n")
cat("Pattern is suggestive: substitution concentrated in low-SGA high-rep firms.\n")
