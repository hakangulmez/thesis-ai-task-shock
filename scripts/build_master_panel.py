"""
Build master panel for DiD analysis.

Merges financial panel with replicability scores,
adds post indicator, interaction term, and ln_revenue.
"""

import numpy as np
import pandas as pd

FINANCIALS_PATH = "data/raw/financials_panel.csv"
REPLICABILITY_PATH = "data/processed/replicability_scores.csv"
OUTPUT_PATH = "data/processed/master_panel.csv"


def main():
    # Load data
    fin = pd.read_csv(FINANCIALS_PATH)
    rep = pd.read_csv(REPLICABILITY_PATH)

    print("Financial panel: %d rows, %d firms" % (len(fin), fin["ticker"].nunique()))
    print("Replicability scores: %d firms" % len(rep))

    # Merge replicability onto financial panel
    rep_cols = rep[["ticker", "replicability_score", "text_source"]].copy()
    panel = fin.merge(rep_cols, on="ticker", how="left")

    # Post indicator: 1 if >= 2022 Q4 (ChatGPT launched Nov 30, 2022)
    panel["post"] = ((panel["fiscal_year"] > 2022) |
                     ((panel["fiscal_year"] == 2022) & (panel["fiscal_quarter"] >= 4))).astype(int)

    # Interaction term
    panel["post_x_replicability"] = panel["post"] * panel["replicability_score"]

    # Log revenue (where revenue > 0)
    panel["ln_revenue"] = np.where(
        panel["revenue"] > 0,
        np.log(panel["revenue"]),
        np.nan,
    )

    # Save
    panel.to_csv(OUTPUT_PATH, index=False)
    print("\nSaved %d rows to %s" % (len(panel), OUTPUT_PATH))

    # --- Summary ---
    has_rep = panel["replicability_score"].notna().sum()
    no_rep = panel["replicability_score"].isna().sum()
    print("\n" + "=" * 60)
    print("MERGE SUMMARY")
    print("  Total rows:                 %d" % len(panel))
    print("  Unique firms:               %d" % panel["ticker"].nunique())
    print("  Rows with replicability:    %d" % has_rep)
    print("  Rows missing replicability: %d" % no_rep)

    print("\nPOST INDICATOR:")
    print("  Pre-period (post=0):  %d rows" % (panel["post"] == 0).sum())
    print("  Post-period (post=1): %d rows" % (panel["post"] == 1).sum())

    print("\nMEAN REPLICABILITY BY PERIOD:")
    pre = panel[panel["post"] == 0]["replicability_score"].mean()
    post = panel[panel["post"] == 1]["replicability_score"].mean()
    print("  Pre:  %.4f" % pre)
    print("  Post: %.4f (should be same — cross-sectional)" % post)

    print("\nKEY VARIABLE SUMMARY:")
    summary_vars = ["revenue", "ln_revenue", "gross_margin", "operating_margin",
                    "replicability_score", "post", "post_x_replicability"]
    for var in summary_vars:
        if var in panel.columns:
            s = panel[var].describe()
            print("  %-25s mean=%.4f  std=%.4f  min=%.4f  max=%.4f" % (
                var, s["mean"], s["std"], s["min"], s["max"]))

    # Period coverage
    print("\nPERIOD RANGE:")
    print("  %d Q%d – %d Q%d" % (
        panel["fiscal_year"].min(), panel.loc[panel["fiscal_year"] == panel["fiscal_year"].min(), "fiscal_quarter"].min(),
        panel["fiscal_year"].max(), panel.loc[panel["fiscal_year"] == panel["fiscal_year"].max(), "fiscal_quarter"].max(),
    ))


if __name__ == "__main__":
    main()
