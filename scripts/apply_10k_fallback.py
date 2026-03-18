"""
Apply 10-K fallback for firms missing Wayback Machine product text.

Copies 10-K Item 1 extracts into product_pages/ for firms that either:
- Have no file in product_pages/
- Have NEEDS_FALLBACK: True in their header
"""

import os
import glob

PRODUCT_DIR = "text_data/product_pages"
TENK_DIR = "text_data/10k_extracts"
UNIVERSE_PATH = "data/raw/firm_universe_v1.csv"


def get_all_tickers():
    """Get all tickers that meet filters."""
    import pandas as pd
    df = pd.read_csv(UNIVERSE_PATH)
    df = df[df["meets_filters"] == True]
    return set(df["ticker"].tolist())


def get_needs_fallback():
    """Find firms missing from product_pages/ or with NEEDS_FALLBACK flag."""
    all_tickers = get_all_tickers()
    missing = set()
    thin = set()

    for ticker in all_tickers:
        path = os.path.join(PRODUCT_DIR, "%s.txt" % ticker)
        if not os.path.exists(path):
            missing.add(ticker)
            continue
        # Check for NEEDS_FALLBACK header
        with open(path, "r", encoding="utf-8") as f:
            header = f.read(500)
            if "NEEDS_FALLBACK: True" in header:
                thin.add(ticker)

    return missing, thin


def copy_with_fallback_header(ticker):
    """Copy 10-K extract to product_pages/ with modified header."""
    src = os.path.join(TENK_DIR, "%s.txt" % ticker)
    dst = os.path.join(PRODUCT_DIR, "%s.txt" % ticker)

    if not os.path.exists(src):
        return False

    with open(src, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse existing header and body
    if content.startswith("---\n"):
        parts = content.split("---\n", 2)
        if len(parts) >= 3:
            header_lines = parts[1].strip().split("\n")
            body = parts[2]
        else:
            header_lines = []
            body = content
    else:
        header_lines = []
        body = content

    # Build new header
    new_header_lines = []
    for line in header_lines:
        new_header_lines.append(line)
    new_header_lines.append("SOURCE: 10-K Item 1 Business Description")
    new_header_lines.append("FALLBACK: True")

    with open(dst, "w", encoding="utf-8") as f:
        f.write("---\n")
        for line in new_header_lines:
            f.write(line + "\n")
        f.write("---\n")
        f.write(body)

    return True


def main():
    missing, thin = get_needs_fallback()
    all_tickers = get_all_tickers()
    need_fallback = missing | thin

    print("Firms in universe:        %d" % len(all_tickers))
    print("Missing from product_pages: %d" % len(missing))
    print("Thin text (NEEDS_FALLBACK): %d" % len(thin))
    print("Total needing fallback:     %d" % len(need_fallback))
    print()

    copied = 0
    still_missing = []

    for ticker in sorted(need_fallback):
        ok = copy_with_fallback_header(ticker)
        if ok:
            copied += 1
            print("  %s  copied from 10-K" % ticker)
        else:
            still_missing.append(ticker)
            print("  %s  NO 10-K AVAILABLE" % ticker)

    # Count final coverage
    wayback_count = 0
    fallback_count = 0
    total_count = 0
    for ticker in sorted(all_tickers):
        path = os.path.join(PRODUCT_DIR, "%s.txt" % ticker)
        if os.path.exists(path):
            total_count += 1
            with open(path, "r", encoding="utf-8") as f:
                header = f.read(500)
                if "FALLBACK: True" in header:
                    fallback_count += 1
                else:
                    wayback_count += 1

    print("\n" + "=" * 50)
    print("Total firms with product text: %d / %d" % (total_count, len(all_tickers)))
    print("  Wayback Machine source:      %d" % wayback_count)
    print("  10-K fallback source:        %d" % fallback_count)

    final_missing = [t for t in sorted(all_tickers) if not os.path.exists(os.path.join(PRODUCT_DIR, "%s.txt" % t))]
    if final_missing:
        print("\nStill missing (%d):" % len(final_missing))
        for t in final_missing:
            print("  %s" % t)
    else:
        print("\nFull coverage: all %d firms have product text." % len(all_tickers))


if __name__ == "__main__":
    main()
