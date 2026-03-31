#!/usr/bin/env python3
"""
SBERT ile firma metinlerini O*NET task'larına benzerlik skoru hesaplar.

INPUT:  data/processed/firm_texts_combined.csv
        data/raw/eloundou/full_labelset.tsv
OUTPUT: data/processed/onet_similarity_scores.csv

METHOD:
1. O*NET task'larını embed et (all-MiniLM-L6-v2)
   - Cache: data/processed/task_embeddings.npy
2. Firma metnini embed et
3. Cosine similarity → top-K task
4. Firma skoru = top-K task'ların alpha/beta/gamma ortalaması
"""

import argparse
import os
import json

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

INPUT_PATH = "data/processed/firm_texts_combined.csv"
TASKS_PATH = "data/raw/eloundou/full_labelset.tsv"
OUTPUT_PATH = "data/processed/onet_similarity_scores.csv"
EMBED_CACHE = "data/processed/task_embeddings.npy"
TASK_DEDUP_CACHE = "data/processed/task_dedup.csv"

TEST_TICKERS = ["ZIP", "CRWD", "DDOG", "NOW", "ASAN"]


def load_tasks():
    """Load and deduplicate O*NET tasks using HUMAN rater scores.

    The raw file has:
      - alpha/beta/gamma: GPT-4 rater (too generous, inflated)
      - human_labels: human rater E0/E1/E2 (conservative, preferred)

    We convert human_labels to numeric:
      alpha: E1→1, else→0           (LLM alone can do it)
      beta:  E1→1, E2→0.5, E0→0    (LLM + code interpreter)
      gamma: E1→1, E2→1, E0→0      (LLM + all tools)
    """
    if os.path.exists(TASK_DEDUP_CACHE):
        return pd.read_csv(TASK_DEDUP_CACHE)

    labels = pd.read_csv(TASKS_PATH, sep="\t")

    # Convert human_labels E0/E1/E2 to numeric scores
    labels["h_alpha"] = (labels["human_labels"] == "E1").astype(float)
    labels["h_beta"] = labels["human_labels"].map({"E1": 1.0, "E2": 0.5, "E0": 0.0}).fillna(0.0)
    labels["h_gamma"] = labels["human_labels"].isin(["E1", "E2"]).astype(float)

    # Deduplicate: one row per unique task text, averaging human scores across occupations
    tasks = (
        labels.groupby("Task")
        .agg(
            alpha=("h_alpha", "mean"),
            beta=("h_beta", "mean"),
            gamma=("h_gamma", "mean"),
            n_occs=("O*NET-SOC Code", "nunique"),
            example_soc=("O*NET-SOC Code", "first"),
            task_id=("Task ID", "first"),
        )
        .reset_index()
    )
    tasks.to_csv(TASK_DEDUP_CACHE, index=False)
    print(f"Deduplicated tasks: {len(labels)} → {len(tasks)} unique (human rater scores)")
    return tasks


def get_task_embeddings(model, tasks):
    """Embed tasks, with caching."""
    if os.path.exists(EMBED_CACHE):
        print(f"Loading cached task embeddings from {EMBED_CACHE}")
        return np.load(EMBED_CACHE)

    print(f"Embedding {len(tasks)} tasks...")
    embeddings = model.encode(tasks["Task"].tolist(), show_progress_bar=True, batch_size=256)
    np.save(EMBED_CACHE, embeddings)
    print(f"Saved task embeddings to {EMBED_CACHE}")
    return embeddings


def score_firm(model, firm_text, task_embeddings, tasks, k):
    """Compute firm exposure as mean of top-K most similar tasks."""
    firm_emb = model.encode([firm_text])
    # Cosine similarity
    sims = np.dot(task_embeddings, firm_emb.T).flatten()
    norms = np.linalg.norm(task_embeddings, axis=1) * np.linalg.norm(firm_emb)
    sims = sims / (norms + 1e-10)

    top_idx = np.argsort(sims)[-k:][::-1]
    top_tasks = tasks.iloc[top_idx]
    top_sims = sims[top_idx]

    firm_alpha = top_tasks["alpha"].mean()
    firm_beta = top_tasks["beta"].mean()
    firm_gamma = top_tasks["gamma"].mean()

    top_task_ids = json.dumps(top_tasks["task_id"].tolist()[:k])
    top_task_sims = json.dumps([round(float(s), 4) for s in top_sims[:k]])
    preview = " | ".join(top_tasks["Task"].str[:60].tolist()[:3])

    return {
        "firm_alpha": round(firm_alpha, 4),
        "firm_beta": round(firm_beta, 4),
        "firm_gamma": round(firm_gamma, 4),
        "top_task_ids": top_task_ids,
        "top_task_sims": top_task_sims,
        "top_tasks_preview": preview,
    }


def main():
    parser = argparse.ArgumentParser(description="O*NET task similarity scoring")
    parser.add_argument("--k", type=int, default=20, help="Top-K tasks (default=20)")
    parser.add_argument("--test", action="store_true", help="Run on 5 test firms")
    parser.add_argument("--tickers", nargs="+", help="Score specific tickers")
    parser.add_argument("--all", action="store_true", help="Score all firms")
    args = parser.parse_args()

    # Load data
    firms = pd.read_csv(INPUT_PATH)
    tasks = load_tasks()

    if args.test:
        firms = firms[firms["ticker"].isin(TEST_TICKERS)].reset_index(drop=True)
    elif args.tickers:
        firms = firms[firms["ticker"].isin(args.tickers)].reset_index(drop=True)
    elif not args.all:
        print("Specify --test, --tickers, or --all")
        return

    print(f"Model: all-MiniLM-L6-v2 | K={args.k} | Firms={len(firms)}")
    print(f"Tasks: {len(tasks)} unique task descriptions\n")

    # Load model and embeddings
    model = SentenceTransformer("all-MiniLM-L6-v2")
    task_embeddings = get_task_embeddings(model, tasks)

    # Score firms
    results = []
    for i, (_, row) in enumerate(firms.iterrows()):
        ticker = row["ticker"]
        scores = score_firm(model, row["combined_text"], task_embeddings, tasks, args.k)
        scores["ticker"] = ticker
        scores["company_name"] = row["company_name"]
        scores["k"] = args.k
        results.append(scores)

        print(
            f"[{i+1}/{len(firms)}] {ticker:6s}  "
            f"α={scores['firm_alpha']:.3f}  β={scores['firm_beta']:.3f}  γ={scores['firm_gamma']:.3f}  "
            f"| {scores['top_tasks_preview'][:80]}"
        )

    df = pd.DataFrame(results)
    col_order = [
        "ticker", "company_name", "k",
        "firm_alpha", "firm_beta", "firm_gamma",
        "top_task_ids", "top_task_sims", "top_tasks_preview",
    ]
    df = df[col_order]
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved: {OUTPUT_PATH} ({len(df)} firms)")

    # Summary
    print(f"\n=== Summary (K={args.k}) ===")
    for col in ["firm_alpha", "firm_beta", "firm_gamma"]:
        print(f"  {col}: mean={df[col].mean():.3f}  SD={df[col].std():.3f}  range=[{df[col].min():.3f}, {df[col].max():.3f}]")


if __name__ == "__main__":
    main()
