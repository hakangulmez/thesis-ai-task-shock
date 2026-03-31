#!/usr/bin/env python3
"""
Rubric-based SBERT contrast scoring.
Anchor sentences derived from Eloundou et al. (2024) rubric definitions.

INPUT:  data/processed/firm_texts_combined.csv
OUTPUT: data/processed/rubric_v2_scores.csv
"""

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os

TEXTS_PATH  = "data/processed/firm_texts_combined.csv"
OUTPUT_PATH = "data/processed/rubric_v2_scores.csv"

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

def main():
    texts = pd.read_csv(TEXTS_PATH)
    print(f"Firms: {len(texts)}")

    model = SentenceTransformer("all-MiniLM-L6-v2")
    e1_embs = model.encode(E1_ANCHORS)
    e0_embs = model.encode(E0_ANCHORS)

    rows = []
    for _, row in texts.iterrows():
        text = str(row["combined_text"])[:1000]
        firm_emb = model.encode([text])
        e1_sim = cosine_similarity(firm_emb, e1_embs)[0].mean()
        e0_sim = cosine_similarity(firm_emb, e0_embs)[0].mean()
        rows.append({
            "ticker":      row["ticker"],
            "company_name": row["company_name"],
            "source":      row["source"],
            "e1_sim":      round(e1_sim, 4),
            "e0_sim":      round(e0_sim, 4),
            "rubric_v2":   round(e1_sim - e0_sim, 4),
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved: {OUTPUT_PATH}")
    print(f"SD: {df['rubric_v2'].std():.4f}")
    print(f"Range: {df['rubric_v2'].min():.4f} to {df['rubric_v2'].max():.4f}")

if __name__ == "__main__":
    main()
