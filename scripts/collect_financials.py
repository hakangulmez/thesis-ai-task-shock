"""
Step 4: Collect quarterly financial data from SEC EDGAR XBRL.

Reads firm_universe_v1.csv (meets_filters == True),
fetches companyfacts for each firm, extracts quarterly
revenue, COGS, operating income, R&D, and SG&A.
"""

import re
import sys
import time
import logging
from typing import Optional, List, Dict, Any
import requests
import pandas as pd

INPUT_PATH = "data/raw/firm_universe_v1.csv"
OUTPUT_PATH = "data/raw/financials_panel.csv"
FAILURE_LOG = "logs/financials_failures.log"

FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 thesis-research contact: go52geg@tum.de"
}
RATE_LIMIT = 0.12
MAX_RETRIES = 3
DATE_MIN = "2019-01-01"
DATE_MAX = "2025-12-31"

# Frame pattern for quarterly duration data: CY2020Q1, CY2020Q2, etc.
QUARTERLY_FRAME_RE = re.compile(r"^CY(\d{4})Q([1-4])$")

# Tag priority lists — first match wins
REVENUE_TAGS = [
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "RevenueFromContractWithCustomerIncludingAssessedTax",
    "Revenues",
    "SalesRevenueNet",
    "SalesRevenueGoodsNet",
    "SalesRevenueServicesNet",
]
COGS_TAGS = [
    "CostOfRevenue",
    "CostOfGoodsAndServicesSold",
    "CostOfGoodsSold",
    "CostOfGoodsAndServiceExcludingDepreciationDepletionAndAmortization",
]
OPINC_TAGS = [
    "OperatingIncomeLoss",
]
RD_TAGS = [
    "ResearchAndDevelopmentExpense",
    "ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost",
    "ResearchAndDevelopmentExpenseSoftwareExcludingAcquiredInProcessCost",
]
SGA_TAGS = [
    "SellingGeneralAndAdministrativeExpense",
    "GeneralAndAdministrativeExpense",
    "SellingAndMarketingExpense",
]

logging.basicConfig(
    filename=FAILURE_LOG,
    filemode="w",
    level=logging.WARNING,
    format="%(asctime)s %(message)s",
)
fail_logger = logging.getLogger("financials")


def fetch_facts(cik: int) -> Optional[dict]:
    """Fetch XBRL companyfacts JSON for a CIK with retries."""
    url = FACTS_URL.format(cik=str(cik).zfill(10))
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** (attempt + 1))
            else:
                fail_logger.warning(f"CIK {cik}: {e}")
                return None


def extract_quarterly(
    gaap: dict, tag_list: List[str]
) -> Dict[str, Dict[str, Any]]:
    """
    Extract quarterly values for the first matching tag.

    Returns dict keyed by 'CYyyyyQq' frame string, values are
    dicts with 'val', 'end', 'tag' keys.
    """
    for tag in tag_list:
        if tag not in gaap:
            continue
        entries = gaap[tag].get("units", {}).get("USD", [])
        if not entries:
            continue

        result = {}
        for e in entries:
            frame = e.get("frame", "")
            m = QUARTERLY_FRAME_RE.match(frame)
            if not m:
                continue
            end_date = e.get("end", "")
            if not end_date:
                continue
            if end_date < DATE_MIN or end_date > DATE_MAX:
                continue

            year, qtr = int(m.group(1)), int(m.group(2))
            key = f"CY{year}Q{qtr}"

            # Keep the entry with the latest filing date (most accurate)
            if key not in result or e.get("filed", "") > result[key]["filed"]:
                result[key] = {
                    "val": e["val"],
                    "end": end_date,
                    "year": year,
                    "quarter": qtr,
                    "tag": tag,
                    "filed": e.get("filed", ""),
                }

        if result:
            return result

    return {}


def process_firm(cik: int, ticker: str, company_name: str) -> List[dict]:
    """Process one firm: fetch facts, extract all metrics, build rows."""
    data = fetch_facts(cik)
    if data is None:
        return []

    gaap = data.get("facts", {}).get("us-gaap", {})
    if not gaap:
        return []

    revenue_q = extract_quarterly(gaap, REVENUE_TAGS)
    cogs_q = extract_quarterly(gaap, COGS_TAGS)
    opinc_q = extract_quarterly(gaap, OPINC_TAGS)
    rd_q = extract_quarterly(gaap, RD_TAGS)
    sga_q = extract_quarterly(gaap, SGA_TAGS)

    if not revenue_q:
        return []

    rows = []
    for key in sorted(revenue_q.keys()):
        rev = revenue_q[key]
        rev_val = rev["val"]

        cogs_val = cogs_q[key]["val"] if key in cogs_q else None
        opinc_val = opinc_q[key]["val"] if key in opinc_q else None
        rd_val = rd_q[key]["val"] if key in rd_q else None
        sga_val = sga_q[key]["val"] if key in sga_q else None

        # Derived fields
        gross_profit = (rev_val - cogs_val) if cogs_val is not None else None
        gross_margin = (gross_profit / rev_val) if (gross_profit is not None and rev_val) else None
        op_margin = (opinc_val / rev_val) if (opinc_val is not None and rev_val) else None
        rd_intensity = (rd_val / rev_val) if (rd_val is not None and rev_val) else None
        sga_intensity = (sga_val / rev_val) if (sga_val is not None and rev_val) else None

        # Track which tags were used
        tags_used = [rev["tag"]]
        if key in cogs_q:
            tags_used.append(cogs_q[key]["tag"])
        if key in opinc_q:
            tags_used.append(opinc_q[key]["tag"])

        rows.append({
            "cik": cik,
            "ticker": ticker,
            "company_name": company_name,
            "period_end": rev["end"],
            "fiscal_year": rev["year"],
            "fiscal_quarter": rev["quarter"],
            "revenue": rev_val,
            "cogs": cogs_val,
            "gross_profit": gross_profit,
            "gross_margin": round(gross_margin, 4) if gross_margin is not None else None,
            "operating_income": opinc_val,
            "operating_margin": round(op_margin, 4) if op_margin is not None else None,
            "rd_expense": rd_val,
            "rd_intensity": round(rd_intensity, 4) if rd_intensity is not None else None,
            "sga_expense": sga_val,
            "sga_intensity": round(sga_intensity, 4) if sga_intensity is not None else None,
            "data_source": "; ".join(tags_used),
        })

    return rows


def main():
    t0 = time.time()

    df = pd.read_csv(INPUT_PATH)
    df = df[df["meets_filters"] == True].reset_index(drop=True)
    total = len(df)
    est = total * RATE_LIMIT
    print(f"Loaded {total:,} firms (meets_filters == True)", flush=True)
    print(f"Estimated runtime: ~{est:.0f}s ({est/60:.1f} min)\n", flush=True)

    all_rows = []
    failures = 0
    no_data = 0

    for i, row in df.iterrows():
        firm_rows = process_firm(row["cik"], row["ticker"], row["company_name"])

        if firm_rows:
            all_rows.extend(firm_rows)
        elif fetch_facts(int(row["cik"])) is None:
            # Already retried inside process_firm; count as failure
            failures += 1
        else:
            no_data += 1

        count = i + 1
        if count % 10 == 0 or count == total:
            elapsed = time.time() - t0
            rate = elapsed / count
            remaining = rate * (total - count)
            print(f"  [{count:,}/{total:,}] rows so far: {len(all_rows):,}  "
                  f"elapsed: {elapsed:.0f}s  remaining: {remaining:.0f}s", flush=True)

        time.sleep(RATE_LIMIT)

    panel = pd.DataFrame(all_rows)
    panel = panel.sort_values(["ticker", "fiscal_year", "fiscal_quarter"]).reset_index(drop=True)
    panel.to_csv(OUTPUT_PATH, index=False)

    # --- Summary ---
    elapsed = time.time() - t0
    firms_with_data = panel["cik"].nunique() if not panel.empty else 0
    print(f"\n{'='*50}", flush=True)
    print(f"Firms processed:              {total:,}", flush=True)
    print(f"Firms with financial data:    {firms_with_data:,}", flush=True)
    print(f"Firms with no XBRL data:      {no_data:,}", flush=True)
    print(f"Failed API lookups:           {failures:,}", flush=True)
    print(f"Total firm-quarter rows:      {len(panel):,}", flush=True)
    if not panel.empty:
        print(f"Date range: {panel['period_end'].min()} to {panel['period_end'].max()}", flush=True)
        print(f"\nQuarters per firm (median):   {panel.groupby('cik').size().median():.0f}", flush=True)
        print(f"\nRevenue coverage:             {panel['revenue'].notna().sum():,}/{len(panel):,}", flush=True)
        print(f"COGS coverage:                {panel['cogs'].notna().sum():,}/{len(panel):,}", flush=True)
        print(f"Operating income coverage:    {panel['operating_income'].notna().sum():,}/{len(panel):,}", flush=True)
        print(f"R&D expense coverage:         {panel['rd_expense'].notna().sum():,}/{len(panel):,}", flush=True)
        print(f"SG&A expense coverage:        {panel['sga_expense'].notna().sum():,}/{len(panel):,}", flush=True)
    print(f"\nTime elapsed: {elapsed:.1f}s ({elapsed/60:.1f} min)", flush=True)
    print(f"Saved to {OUTPUT_PATH}", flush=True)


if __name__ == "__main__":
    main()
