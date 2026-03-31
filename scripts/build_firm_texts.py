#!/usr/bin/env python3
"""
Firma metinlerini hazırlar.
INPUT:  text_data/10k_extracts/{ticker}.txt
        text_data/product_pages/{ticker}.txt
        data/raw/firm_universe_v1.csv
OUTPUT: data/processed/firm_texts_combined.csv
"""

import os
import pandas as pd


def read_text_file(path, max_chars=None):
    """Read text file, strip header before '---', optionally truncate."""
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8", errors="ignore") as f:
        content = f.read()
    if "---\n" in content:
        content = content.split("---\n", 2)[-1]
    content = content.strip()
    if max_chars:
        content = content[:max_chars]
    return content


def count_sentences(text, min_words=8):
    """Count sentences with at least min_words words."""
    return len([s for s in text.split(".") if len(s.split()) >= min_words])


def main():
    firms = pd.read_csv("data/raw/firm_universe_v1.csv")
    firms = firms[firms["meets_filters"] == True].reset_index(drop=True)

    rows = []
    for _, firm in firms.iterrows():
        ticker = firm["ticker"]
        company = firm["company_name"]

        tenk_text = read_text_file(f"text_data/10k_extracts/{ticker}.txt", max_chars=1500)
        wb_text_full = read_text_file(f"text_data/product_pages/{ticker}.txt")
        wb_sents = count_sentences(wb_text_full)
        wb_text = wb_text_full[:1000]

        if wb_sents >= 20 and wb_text:
            combined = (
                f"=== 10-K BUSINESS DESCRIPTION ===\n{tenk_text}\n\n"
                f"=== PRODUCT PAGE (Wayback 2022) ===\n{wb_text}"
            )
            source = "combined"
        else:
            combined = tenk_text
            source = "10k_only"

        rows.append({
            "ticker": ticker,
            "company_name": company,
            "combined_text": combined,
            "source": source,
            "wb_sentences": wb_sents,
            "text_length": len(combined),
        })

    df = pd.DataFrame(rows)
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv("data/processed/firm_texts_combined.csv", index=False)

    n_combined = (df["source"] == "combined").sum()
    n_10k = (df["source"] == "10k_only").sum()

    print(f"Toplam firma:      {len(df)}")
    print(f"Combined (10K+WB): {n_combined}")
    print(f"10K only:          {n_10k}")
    print(f"\nText uzunluğu:")
    print(f"  Combined ort: {df[df['source']=='combined']['text_length'].mean():.0f} karakter")
    print(f"  10K only ort: {df[df['source']=='10k_only']['text_length'].mean():.0f} karakter")

    row = df[df["ticker"] == "ZIP"].iloc[0]
    print(f"\nÖrnek — ZIP ({row['source']}):")
    print(row["combined_text"][:500])


if __name__ == "__main__":
    main()
