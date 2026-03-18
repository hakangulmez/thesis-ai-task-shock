"""
Step 2: Get software firms (SIC 7370-7379) from EDGAR browse API.

Instead of querying 7,509 firms one by one, queries EDGAR's
company search by SIC code (10 SIC codes, paginated).
Cross-references with firm_universe_raw.csv for exchange info.
"""

import sys
import time
import logging
import xml.etree.ElementTree as ET
from typing import Optional
import requests
import pandas as pd

INPUT_PATH = "data/raw/firm_universe_raw.csv"
OUTPUT_PATH = "data/raw/firm_universe_with_sic.csv"
FAILURE_LOG = "logs/sic_lookup_failures.log"

BROWSE_URL = ("https://www.sec.gov/cgi-bin/browse-edgar"
              "?action=getcompany&SIC={sic}&owner=include"
              "&match=&start={start}&count=100&output=atom")
HEADERS = {
    "User-Agent": "Mozilla/5.0 thesis-research contact: go52geg@tum.de"
}
RATE_LIMIT = 0.12
MAX_RETRIES = 3
SOFTWARE_SICS = list(range(7370, 7380))
NS = {"atom": "http://www.w3.org/2005/Atom"}

logging.basicConfig(
    filename=FAILURE_LOG,
    filemode="w",
    level=logging.WARNING,
    format="%(asctime)s %(message)s",
)
fail_logger = logging.getLogger("sic_failures")


def fetch_page(sic: int, start: int) -> Optional[str]:
    """Fetch one page of EDGAR browse results with retries."""
    url = BROWSE_URL.format(sic=sic, start=start)
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                wait = 2 ** (attempt + 1)
                time.sleep(wait)
            else:
                fail_logger.warning(f"SIC {sic} start={start}: {e}")
                return None


def parse_ciks(xml_text: str) -> list:
    """Extract CIK numbers from ATOM XML response."""
    root = ET.fromstring(xml_text)
    ciks = []
    for entry in root.findall("atom:entry", NS):
        content = entry.find("atom:content", NS)
        if content is None:
            continue
        # Namespace-unaware search for cik element
        for elem in content.iter():
            if elem.tag.endswith("}cik") or elem.tag == "cik":
                cik_text = elem.text
                if cik_text:
                    ciks.append(int(cik_text))
                break
    return ciks


def get_all_ciks_for_sic(sic: int) -> list:
    """Paginate through all firms for a given SIC code."""
    all_ciks = []
    start = 0
    while True:
        xml_text = fetch_page(sic, start)
        if xml_text is None:
            print(f"  WARNING: Failed to fetch SIC {sic} start={start}", flush=True)
            break

        ciks = parse_ciks(xml_text)
        all_ciks.extend(ciks)

        if len(ciks) < 100:
            break
        start += 100
        time.sleep(RATE_LIMIT)

    return all_ciks


def main():
    t0 = time.time()

    # --- Load existing universe for cross-reference ---
    df_universe = pd.read_csv(INPUT_PATH)
    print(f"Loaded {len(df_universe):,} firms from {INPUT_PATH}", flush=True)

    # --- Query EDGAR by SIC code ---
    records = []
    total_requests = 0

    for sic in SOFTWARE_SICS:
        ciks = get_all_ciks_for_sic(sic)
        pages = (len(ciks) // 100) + 1 if len(ciks) > 0 else 1
        total_requests += pages
        for cik in ciks:
            records.append({"cik": cik, "sic_code": sic})
        print(f"  SIC {sic}: {len(ciks):,} firms ({pages} requests)", flush=True)
        time.sleep(RATE_LIMIT)

    df_sic = pd.DataFrame(records)

    if df_sic.empty:
        print("ERROR: No firms found for SIC 7370-7379", flush=True)
        sys.exit(1)

    # Deduplicate (a firm could appear under multiple SIC codes)
    df_sic = df_sic.drop_duplicates(subset="cik", keep="first")

    # --- Cross-reference with universe for exchange/ticker/name ---
    df_merged = df_sic.merge(
        df_universe[["cik", "ticker", "company_name", "exchange"]],
        on="cik",
        how="inner",
    )

    df_merged = df_merged[["cik", "ticker", "company_name", "exchange", "sic_code"]]
    df_merged = df_merged.sort_values("ticker").reset_index(drop=True)

    df_merged.to_csv(OUTPUT_PATH, index=False)

    # --- Summary ---
    elapsed = time.time() - t0
    sic_only = len(df_sic)
    matched = len(df_merged)
    unmatched = sic_only - matched

    print(f"\n{'='*50}", flush=True)
    print(f"Total HTTP requests:          {total_requests}", flush=True)
    print(f"Firms with SIC 7370-7379:     {sic_only:,} (all exchanges)", flush=True)
    print(f"Matched to NYSE/Nasdaq:       {matched:,}", flush=True)
    print(f"Not on NYSE/Nasdaq:           {unmatched:,}", flush=True)
    print(flush=True)
    print("Breakdown by SIC code:", flush=True)
    for sic, count in df_merged["sic_code"].value_counts().sort_index().items():
        print(f"  {sic}: {count}", flush=True)
    print(flush=True)
    print(f"Time elapsed: {elapsed:.1f}s", flush=True)
    print(f"Saved to {OUTPUT_PATH}", flush=True)


if __name__ == "__main__":
    main()
