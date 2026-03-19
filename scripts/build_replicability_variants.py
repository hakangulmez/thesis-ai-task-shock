"""
Build replicability score variants for robustness check.

Run 1: 10-K extracts only → replicability_scores_10k.csv
Run 2: Wayback-only firms from product_pages → replicability_scores_wayback_only.csv
"""

import os
import re
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

UNIVERSE_PATH = "data/raw/firm_universe_v1.csv"

ANCHOR_SENTENCES = [
    "Draft and send personalized emails to customers",
    "Write marketing copy and social media posts",
    "Generate product descriptions from specifications",
    "Summarize documents and extract key information",
    "Translate text between languages",
    "Create documentation from technical specifications",
    "Answer customer questions from a knowledge base",
    "Classify and route support tickets by topic",
    "Search and retrieve relevant information",
    "Match candidates to job requirements",
    "Generate reports and dashboards from structured data",
    "Extract and transform data from forms and documents",
    "Score and rank items based on rules and criteria",
    "Monitor metrics and alert when thresholds are exceeded",
    "Automate repetitive data entry and processing tasks",
    "Route requests through approval workflows",
    "Schedule and coordinate tasks across teams",
    "Process and reconcile transactions automatically",
]

TOP_K = 10
MIN_WORDS = 10


def load_universe():
    df = pd.read_csv(UNIVERSE_PATH)
    df = df[df["meets_filters"] == True]
    return dict(zip(df["ticker"], df["company_name"]))


def split_sentences(text):
    raw = re.split(r'(?<=[.!?])\s+|\n+', text)
    sentences = []
    for s in raw:
        s = s.strip()
        if len(s.split()) >= MIN_WORDS:
            sentences.append(s)
    return sentences


def parse_product_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
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


def parse_10k_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if content.startswith("---\n"):
        parts = content.split("---\n", 2)
        if len(parts) >= 3:
            body = parts[2]
        else:
            body = content
    else:
        body = content
    return body.strip()


def score_firms(model, anchor_embeddings, universe, input_dir, output_path,
                filter_fn=None):
    """Score firms from input_dir, optionally filtering with filter_fn."""
    results = []
    missing = []

    for ticker in sorted(universe.keys()):
        path = os.path.join(input_dir, "%s.txt" % ticker)
        if not os.path.exists(path):
            missing.append(ticker)
            continue

        # For product_pages, parse with source detection
        if input_dir == "text_data/product_pages":
            body, source = parse_product_file(path)
            if filter_fn and not filter_fn(source):
                continue
        else:
            body = parse_10k_file(path)
            source = "10k"

        sentences = split_sentences(body)

        if len(sentences) == 0:
            results.append({
                "ticker": ticker,
                "company_name": universe[ticker],
                "replicability_score": np.nan,
                "sentence_count": 0,
                "text_source": source,
                "top_sentences": "",
            })
            continue

        sent_embeddings = model.encode(sentences, normalize_embeddings=True)
        sim_matrix = sent_embeddings @ anchor_embeddings.T
        max_sim_per_sentence = sim_matrix.max(axis=1)

        k = min(TOP_K, len(max_sim_per_sentence))
        top_indices = np.argsort(max_sim_per_sentence)[::-1][:k]
        score = float(np.mean(max_sim_per_sentence[top_indices]))

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

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = pd.DataFrame(results)
    df.to_csv(output_path, index=False)

    scored = df.dropna(subset=["replicability_score"])
    scores = scored["replicability_score"]
    print("\n%s: %d firms scored" % (output_path, len(scored)))
    print("  Mean: %.4f  SD: %.4f  Min: %.4f  Max: %.4f" % (
        scores.mean(), scores.std(), scores.min(), scores.max()))
    if missing:
        print("  Missing text: %d firms" % len(missing))

    return df


def main():
    print("Loading SBERT model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    anchor_embeddings = model.encode(ANCHOR_SENTENCES, normalize_embeddings=True)
    universe = load_universe()
    print("Firms in universe: %d" % len(universe))

    # Run 1: 10-K extracts only
    print("\n" + "=" * 60)
    print("RUN 1: 10-K EXTRACTS ONLY")
    print("=" * 60)
    score_firms(model, anchor_embeddings, universe,
                "text_data/10k_extracts",
                "data/processed/replicability_scores_10k.csv")

    # Run 2: Wayback-only firms from product_pages
    print("\n" + "=" * 60)
    print("RUN 2: WAYBACK-ONLY FIRMS")
    print("=" * 60)
    score_firms(model, anchor_embeddings, universe,
                "text_data/product_pages",
                "data/processed/replicability_scores_wayback_only.csv",
                filter_fn=lambda source: source == "wayback")


if __name__ == "__main__":
    main()
