"""
Step 3: Apply filters to software firm universe.

Automatic: IPO before 2020 (earliest EDGAR filing date).
Manual:    b2b_focus, exclude_reason, meets_filters (filled later).
"""

import sys
import time
import logging
from typing import Optional
import requests
import pandas as pd

INPUT_PATH = "data/raw/firm_universe_with_sic.csv"
OUTPUT_PATH = "data/raw/firm_universe_v1.csv"
FAILURE_LOG = "logs/ipo_filter_failures.log"

SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 thesis-research contact: go52geg@tum.de"
}
RATE_LIMIT = 0.12
MAX_RETRIES = 3
IPO_CUTOFF = "2020-01-01"

logging.basicConfig(
    filename=FAILURE_LOG,
    filemode="w",
    level=logging.WARNING,
    format="%(asctime)s %(message)s",
)
fail_logger = logging.getLogger("ipo_failures")


def fetch_earliest_filing(cik: int) -> Optional[str]:
    """Fetch earliest filing date for a CIK from EDGAR submissions API."""
    url = SUBMISSIONS_URL.format(cik=str(cik).zfill(10))
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            dates = data.get("filings", {}).get("recent", {}).get("filingDate", [])
            if not dates:
                return None

            return min(dates)
        except requests.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                wait = 2 ** (attempt + 1)
                time.sleep(wait)
            else:
                fail_logger.warning(f"CIK {cik}: {e}")
                return None


def main():
    t0 = time.time()

    df = pd.read_csv(INPUT_PATH)
    total = len(df)
    est_seconds = total * RATE_LIMIT
    print(f"Loaded {total:,} firms from {INPUT_PATH}", flush=True)
    print(f"Estimated runtime: ~{est_seconds:.0f}s ({est_seconds/60:.1f} min)\n", flush=True)

    ipo_flags = []
    failures = 0

    for i, row in df.iterrows():
        earliest = fetch_earliest_filing(row["cik"])

        if earliest is None:
            ipo_flags.append(None)
            failures += 1
        else:
            ipo_flags.append(earliest < IPO_CUTOFF)

        count = i + 1
        if count % 50 == 0 or count == total:
            elapsed = time.time() - t0
            rate = elapsed / count
            remaining = rate * (total - count)
            print(f"  [{count:,}/{total:,}] elapsed: {elapsed:.0f}s, "
                  f"remaining: {remaining:.0f}s", flush=True)

        time.sleep(RATE_LIMIT)

    df["ipo_before_2020"] = ipo_flags
    df["b2b_focus"] = ""
    df["exclude_reason"] = ""
    df["meets_filters"] = ""

    df = df[["cik", "ticker", "company_name", "exchange", "sic_code",
             "ipo_before_2020", "b2b_focus", "exclude_reason", "meets_filters"]]
    df.to_csv(OUTPUT_PATH, index=False)

    # --- Summary ---
    elapsed = time.time() - t0
    true_count = sum(1 for v in ipo_flags if v is True)
    false_count = sum(1 for v in ipo_flags if v is False)

    print(f"\n{'='*50}", flush=True)
    print(f"Total firms processed:        {total:,}", flush=True)
    print(f"ipo_before_2020 = True:       {true_count:,}", flush=True)
    print(f"ipo_before_2020 = False:      {false_count:,}", flush=True)
    print(f"Failed API lookups:           {failures:,}", flush=True)
    print(f"Time elapsed: {elapsed:.1f}s ({elapsed/60:.1f} min)", flush=True)
    print(f"Saved to {OUTPUT_PATH}", flush=True)
    print(flush=True)
    print("NEXT STEP: Open data/raw/firm_universe_v1.csv", flush=True)
    print("  Set b2b_focus and meets_filters columns.", flush=True)
    print("  Then run scripts/collect_financials.py", flush=True)


if __name__ == "__main__":
    main()
