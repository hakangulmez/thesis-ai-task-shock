"""
Build task replicability scores for all 143 firms.

Uses SBERT (all-MiniLM-L6-v2) to compute semantic similarity
between each firm's product description and a set of anchor
sentences representing highly AI-replicable tasks.

Firm score = mean of top-10 sentence similarities to anchors.
"""

import os
import re
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

PRODUCT_DIR = "text_data/product_pages"
UNIVERSE_PATH = "data/raw/firm_universe_v1.csv"
OUTPUT_PATH = "data/processed/replicability_scores.csv"

ANCHOR_SENTENCES = [
    # Communication and content
    "Draft and send personalized emails to customers",
    "Write marketing copy and social media posts",
    "Generate product descriptions from specifications",
    "Summarize documents and extract key information",
    "Translate text between languages",
    "Create documentation from technical specifications",
    # Knowledge and support
    "Answer customer questions from a knowledge base",
    "Classify and route support tickets by topic",
    "Search and retrieve relevant information",
    "Match candidates to job requirements",
    # Analytics and reporting
    "Generate reports and dashboards from structured data",
    "Extract and transform data from forms and documents",
    "Score and rank items based on rules and criteria",
    "Monitor metrics and alert when thresholds are exceeded",
    # Workflow and automation
    "Automate repetitive data entry and processing tasks",
    "Route requests through approval workflows",
    "Schedule and coordinate tasks across teams",
    "Process and reconcile transactions automatically",
]

LOW_ANCHOR_SENTENCES = [
    "Monitor real-time network traffic across distributed infrastructure",
    "Detect and respond to security incidents across enterprise systems",
    "Orchestrate complex multi-system workflows requiring live data integration",
    "Process high-frequency financial transactions with sub-millisecond latency",
    "Ingest and correlate telemetry data from cloud infrastructure in real time",
    "Coordinate incident response across hundreds of enterprise integrations",
    "Perform chip design verification across hardware simulation environments",
    "Manage physical supply chain routing across logistics networks",
    "Execute database query optimization across distributed storage systems",
    "Provision and manage cloud infrastructure resources programmatically",
]

TOP_K = 10  # number of top sentences to average
MIN_WORDS = 10  # minimum words per sentence


def load_universe():
    """Load firm universe and return ticker->company mapping."""
    df = pd.read_csv(UNIVERSE_PATH)
    df = df[df["meets_filters"] == True]
    return dict(zip(df["ticker"], df["company_name"]))


def split_sentences(text):
    """Split text into sentences using period/newline splitting."""
    # Split on period followed by space/newline, or on newlines
    raw = re.split(r'(?<=[.!?])\s+|\n+', text)
    sentences = []
    for s in raw:
        s = s.strip()
        if len(s.split()) >= MIN_WORDS:
            sentences.append(s)
    return sentences


def parse_product_file(path):
    """Read product text file, return body text and source type."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse YAML header
    source = "wayback"
    if content.startswith("---\n"):
        parts = content.split("---\n", 2)
        if len(parts) >= 3:
            header = parts[1]
            body = parts[2]
            if "FALLBACK: True" in header:
                source = "10k_fallback"
        else:
            body = content
    else:
        body = content

    return body.strip(), source


def main():
    print("Loading SBERT model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Encoding anchor sentences...")
    high_embeddings = model.encode(ANCHOR_SENTENCES, normalize_embeddings=True)
    low_embeddings = model.encode(LOW_ANCHOR_SENTENCES, normalize_embeddings=True)

    universe = load_universe()
    print("Firms in universe: %d" % len(universe))

    results = []
    missing = []

    for ticker in sorted(universe.keys()):
        path = os.path.join(PRODUCT_DIR, "%s.txt" % ticker)
        if not os.path.exists(path):
            missing.append(ticker)
            continue

        body, source = parse_product_file(path)
        sentences = split_sentences(body)

        if len(sentences) == 0:
            print("  %s  WARNING: no usable sentences" % ticker)
            results.append({
                "ticker": ticker,
                "company_name": universe[ticker],
                "replicability_score": np.nan,
                "high_score": np.nan,
                "low_score": np.nan,
                "contrast_score": np.nan,
                "sentence_count": 0,
                "text_source": source,
                "top_sentences": "",
            })
            continue

        # Encode firm sentences
        sent_embeddings = model.encode(sentences, normalize_embeddings=True)

        # High-replicability similarity
        sim_high = sent_embeddings @ high_embeddings.T
        max_sim_high = sim_high.max(axis=1)
        k = min(TOP_K, len(max_sim_high))
        top_idx_high = np.argsort(max_sim_high)[::-1][:k]
        high_score = float(np.mean(max_sim_high[top_idx_high]))

        # Low-replicability similarity
        sim_low = sent_embeddings @ low_embeddings.T
        max_sim_low = sim_low.max(axis=1)
        k_low = min(TOP_K, len(max_sim_low))
        top_idx_low = np.argsort(max_sim_low)[::-1][:k_low]
        low_score = float(np.mean(max_sim_low[top_idx_low]))

        # Contrast score
        contrast_score = high_score - low_score

        # Top 3 sentences (from high anchors) for validation
        top3_indices = top_idx_high[:3]
        top3_sentences = [sentences[i] for i in top3_indices]
        top3_str = " | ".join(top3_sentences)

        results.append({
            "ticker": ticker,
            "company_name": universe[ticker],
            "replicability_score": round(high_score, 4),
            "high_score": round(high_score, 4),
            "low_score": round(low_score, 4),
            "contrast_score": round(contrast_score, 4),
            "sentence_count": len(sentences),
            "text_source": source,
            "top_sentences": top3_str,
        })

    # Save
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_PATH, index=False)
    print("\nSaved %d scores to %s" % (len(df), OUTPUT_PATH))

    if missing:
        print("\nMissing product text (%d): %s" % (len(missing), ", ".join(missing)))

    # --- Summary statistics ---
    scored = df.dropna(subset=["replicability_score"])

    for col, label in [("high_score", "HIGH SCORE (replicable anchors)"),
                       ("low_score", "LOW SCORE (non-replicable anchors)"),
                       ("contrast_score", "CONTRAST SCORE (high - low)")]:
        vals = scored[col]
        print("\n" + "=" * 60)
        print("%s DISTRIBUTION (n=%d)" % (label, len(vals)))
        print("  Min:  %.4f" % vals.min())
        print("  P25:  %.4f" % vals.quantile(0.25))
        print("  P50:  %.4f" % vals.quantile(0.50))
        print("  P75:  %.4f" % vals.quantile(0.75))
        print("  Max:  %.4f" % vals.max())
        print("  Mean: %.4f  SD: %.4f" % (vals.mean(), vals.std()))

    print("\n" + "=" * 60)
    print("TOP 10 BY CONTRAST SCORE (most replicable relative to infra):")
    top10 = scored.nlargest(10, "contrast_score")
    for _, row in top10.iterrows():
        print("  %-6s  contrast=%.4f  high=%.4f  low=%.4f  %s" % (
            row["ticker"], row["contrast_score"], row["high_score"],
            row["low_score"], row["company_name"]))

    print("\nBOTTOM 10 BY CONTRAST SCORE (least replicable relative to infra):")
    bot10 = scored.nsmallest(10, "contrast_score")
    for _, row in bot10.iterrows():
        print("  %-6s  contrast=%.4f  high=%.4f  low=%.4f  %s" % (
            row["ticker"], row["contrast_score"], row["high_score"],
            row["low_score"], row["company_name"]))

    # Correlation
    corr = scored["high_score"].corr(scored["contrast_score"])
    print("\nCorrelation(high_score, contrast_score): %.4f" % corr)
    corr_hl = scored["high_score"].corr(scored["low_score"])
    print("Correlation(high_score, low_score):      %.4f" % corr_hl)

    # Source breakdown
    print("\nTEXT SOURCE BREAKDOWN:")
    src_counts = df["text_source"].value_counts()
    for src, count in src_counts.items():
        print("  %-15s %d" % (src, count))


if __name__ == "__main__":
    main()
