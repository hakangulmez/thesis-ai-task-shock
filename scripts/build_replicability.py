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
    anchor_embeddings = model.encode(ANCHOR_SENTENCES, normalize_embeddings=True)

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
                "sentence_count": 0,
                "text_source": source,
                "top_sentences": "",
            })
            continue

        # Encode firm sentences
        sent_embeddings = model.encode(sentences, normalize_embeddings=True)

        # Cosine similarity: (n_sentences, n_anchors)
        # Embeddings are already normalized, so dot product = cosine sim
        sim_matrix = sent_embeddings @ anchor_embeddings.T

        # Max similarity per sentence across all anchors
        max_sim_per_sentence = sim_matrix.max(axis=1)

        # Top-K sentence scores
        k = min(TOP_K, len(max_sim_per_sentence))
        top_indices = np.argsort(max_sim_per_sentence)[::-1][:k]
        score = float(np.mean(max_sim_per_sentence[top_indices]))

        # Top 3 sentences for validation
        top3_indices = top_indices[:3]
        top3_sentences = [sentences[i] for i in top3_indices]
        top3_str = " | ".join(top3_sentences)

        results.append({
            "ticker": ticker,
            "company_name": universe[ticker],
            "replicability_score": round(score, 4),
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
    scores = scored["replicability_score"]

    print("\n" + "=" * 60)
    print("SCORE DISTRIBUTION (n=%d)" % len(scores))
    print("  Min:  %.4f" % scores.min())
    print("  P25:  %.4f" % scores.quantile(0.25))
    print("  P50:  %.4f" % scores.quantile(0.50))
    print("  P75:  %.4f" % scores.quantile(0.75))
    print("  Max:  %.4f" % scores.max())

    print("\nTOP 10 HIGHEST (most replicable):")
    top10 = scored.nlargest(10, "replicability_score")
    for _, row in top10.iterrows():
        print("  %-6s  %.4f  %s" % (row["ticker"], row["replicability_score"], row["company_name"]))

    print("\nBOTTOM 10 LOWEST (least replicable):")
    bot10 = scored.nsmallest(10, "replicability_score")
    for _, row in bot10.iterrows():
        print("  %-6s  %.4f  %s" % (row["ticker"], row["replicability_score"], row["company_name"]))

    # Source breakdown
    print("\nTEXT SOURCE BREAKDOWN:")
    src_counts = df["text_source"].value_counts()
    for src, count in src_counts.items():
        print("  %-15s %d" % (src, count))


if __name__ == "__main__":
    main()
