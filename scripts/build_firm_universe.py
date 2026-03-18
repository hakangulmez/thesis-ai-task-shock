"""
Step 1: Build firm universe from SEC EDGAR.

One HTTP request to company_tickers_exchange.json.
Filters for NYSE/Nasdaq, saves to data/raw/firm_universe_raw.csv.
"""

import sys
import requests
import pandas as pd

URL = "https://www.sec.gov/files/company_tickers_exchange.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 thesis-research contact: go52geg@tum.de"
}
OUTPUT_PATH = "data/raw/firm_universe_raw.csv"


def main():
    # --- Fetch data ---
    try:
        resp = requests.get(URL, headers=HEADERS, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"ERROR: Failed to fetch SEC data: {e}")
        sys.exit(1)

    payload = resp.json()
    columns = payload["fields"]
    rows = payload["data"]

    df_all = pd.DataFrame(rows, columns=columns)
    df_all.columns = ["cik", "company_name", "ticker", "exchange"]
    total = len(df_all)

    # --- Filter for NYSE / Nasdaq ---
    df = df_all[df_all["exchange"].isin(["NYSE", "Nasdaq"])].copy()
    df = df[["cik", "ticker", "company_name", "exchange"]]
    df = df.sort_values("ticker").reset_index(drop=True)

    # --- Save ---
    df.to_csv(OUTPUT_PATH, index=False)

    # --- Summary ---
    nyse = (df["exchange"] == "NYSE").sum()
    nasdaq = (df["exchange"] == "Nasdaq").sum()

    print(f"Total firms in JSON file:       {total:,}")
    print(f"After NYSE/Nasdaq filter:       {len(df):,}")
    print(f"  NYSE:   {nyse:,}")
    print(f"  Nasdaq: {nasdaq:,}")
    print()
    print("First 10 rows:")
    print(df.head(10).to_string(index=False))
    print()
    print(f"Saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
