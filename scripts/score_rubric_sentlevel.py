#!/usr/bin/env python3
"""
Sentence-level top-K SBERT scoring with Rubric V2 anchors.
Anchors derived from Eloundou et al. (2024) E1/E0 rubric definitions.

METHOD (same as build_replicability.py but with Rubric V2 anchors):
1. Split firm text into sentences (min 10 words)
2. Embed each sentence with SBERT
3. For each sentence: max cosine similarity to any E1 anchor
4. high_score = mean of top-10 sentence max-similarities
5. Same for E0 anchors → low_score
6. rubric_sent_contrast = high_score - low_score

INPUT:  text_data/product_pages/{ticker}.txt
OUTPUT: data/processed/rubric_sent_scores.csv
"""

import os
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

WB_DIR   = "text_data/product_pages"
OUT_PATH = "data/processed/rubric_sent_scores.csv"
TOP_K    = 10
MIN_WORDS = 10

E1_ANCHORS = [
    "Automate document generation and report creation",
    "Extract and classify information from contracts",
    "Generate personalized email and marketing content",
    "Summarize and organize research findings",
    "Translate and reformat legal or financial documents",
    "Match job candidates to positions using text criteria",
    "Screen and rank applicant resumes automatically",
    "Generate performance review and evaluation text",
    "Classify and route customer support tickets",
    "Generate automated responses to customer inquiries",
    "Analyze customer feedback and sentiment patterns",
    "Automate financial report writing and commentary",
    "Extract data from invoices and financial documents",
    "Generate compliance reports from structured data",
    "Generate code from natural language specifications",
    "Automate technical documentation and API descriptions",
    "Review and summarize software requirements",
    "Create and optimize advertising copy at scale",
    "Generate product descriptions from specifications",
    "Automate social media content creation",
]

E0_ANCHORS = [
    "Install configure and maintain network hardware",
    "Monitor real-time server performance and uptime",
    "Manage physical data center operations",
    "Deploy and maintain edge computing infrastructure",
    "Detect and respond to live cybersecurity threats",
    "Monitor endpoint devices for malware in real-time",
    "Perform penetration testing on live systems",
    "Analyze network packet data for intrusions",
    "Route and switch voice and data telecommunications",
    "Maintain carrier-grade network infrastructure",
    "Manage cellular and wireless spectrum operations",
    "Process real-time payment transactions and settlements",
    "Operate card issuing and payment network infrastructure",
    "Manage banking core system integrations",
    "Operate medical imaging and diagnostic equipment",
    "Manage electronic health record system integrations",
    "Monitor patient vital signs through connected devices",
    "Control industrial automation and SCADA systems",
    "Monitor supply chain physical logistics operations",
    "Operate satellite and GPS tracking infrastructure",
]

def score_firm(text, e1_embs, e0_embs, model):
    # Cümlelere böl
    sents = [s.strip() for s in text.split(".")
             if len(s.split()) >= MIN_WORDS]
    if len(sents) == 0:
        return np.nan, np.nan, np.nan, 0

    sent_embs = model.encode(sents)

    # E1: her cümle için max similarity
    e1_sims = cosine_similarity(
        sent_embs, e1_embs)
    e1_max = e1_sims.max(axis=1)

    # E0: her cümle için max similarity
    e0_sims = cosine_similarity(
        sent_embs, e0_embs)
    e0_max = e0_sims.max(axis=1)

    # Top-K ortalaması
    k = min(TOP_K, len(sents))
    high_score = np.sort(e1_max)[::-1][:k].mean()
    low_score  = np.sort(e0_max)[::-1][:k].mean()
    contrast   = high_score - low_score

    return high_score, low_score, contrast, len(sents)

def main():
    firms = pd.read_csv("data/raw/firm_universe_v1.csv")
    firms = firms[firms["meets_filters"]==True
        ].reset_index(drop=True)

    model   = SentenceTransformer("all-MiniLM-L6-v2")
    e1_embs = model.encode(E1_ANCHORS)
    e0_embs = model.encode(E0_ANCHORS)

    rows = []
    for _, firm in firms.iterrows():
        ticker = firm["ticker"]
        path   = f"{WB_DIR}/{ticker}.txt"

        if not os.path.exists(path):
            rows.append({
                "ticker": ticker,
                "company_name": firm["company_name"],
                "text_source": "missing",
                "n_sentences": 0,
                "high_score": np.nan,
                "low_score": np.nan,
                "rubric_sent_contrast": np.nan,
            })
            continue

        with open(path, encoding="utf-8",
                  errors="ignore") as f:
            content = f.read()

        if "---\n" in content:
            text = content.split("---\n", 2)[-1].strip()
        else:
            text = content.strip()

        h, l, c, n = score_firm(
            text, e1_embs, e0_embs, model)

        rows.append({
            "ticker": ticker,
            "company_name": firm["company_name"],
            "text_source": "wayback",
            "n_sentences": n,
            "high_score": round(h, 4),
            "low_score":  round(l, 4),
            "rubric_sent_contrast": round(c, 4),
        })
        print(f"  {ticker}: n={n}, contrast={c:.4f}")

    df = pd.DataFrame(rows)
    df.to_csv(OUT_PATH, index=False)

    wb = df[df["text_source"]=="wayback"]
    print(f"\nToplam: {len(df)}, Wayback: {len(wb)}")
    print(f"SD:   {wb['rubric_sent_contrast'].std():.4f}")
    print(f"mean: {wb['rubric_sent_contrast'].mean():.4f}")
    print(f"range: {wb['rubric_sent_contrast'].min():.4f}"
          f" to {wb['rubric_sent_contrast'].max():.4f}")

    print("\nBenchmark:")
    bench = wb[wb["ticker"].isin(
        ["ZIP","CRWD","DDOG","NOW","ASAN",
         "LPSN","SKIL","ADBE","BAND","VRSN"])]
    print(bench.sort_values(
        "rubric_sent_contrast", ascending=False)[
        ["ticker","rubric_sent_contrast",
         "high_score","low_score","n_sentences"]
        ].to_string(index=False))

if __name__ == "__main__":
    main()
