"""
Score any text input for AI task replicability.

Usage:
    python scripts/score_new_firm.py <file.txt>
    echo "product description" | python scripts/score_new_firm.py
"""

from sentence_transformers import SentenceTransformer
import numpy as np, re, sys

model = SentenceTransformer('all-MiniLM-L6-v2')

HIGH_ANCHORS = [
    "Draft and send personalized emails to customers",
    "Classify and route support tickets by topic",
    "Generate reports and dashboards from structured data",
    "Answer customer questions from a knowledge base",
    "Match candidates to job requirements",
    "Write marketing copy and social media posts",
    "Summarize documents and extract key information",
    "Automate repetitive data entry and processing tasks",
    "Monitor metrics and alert when thresholds are exceeded",
    "Extract information from documents",
    "Score and rank items based on rules",
    "Route requests through approval workflows",
    "Schedule and coordinate tasks across teams",
    "Process and reconcile transactions",
    "Search and retrieve relevant information",
    "Create documentation from technical specifications",
    "Generate product descriptions",
    "Translate text between languages",
]

LOW_ANCHORS = [
    "Monitor real-time network traffic across distributed infrastructure",
    "Detect and respond to security incidents across enterprise systems",
    "Process high-frequency financial transactions with sub-millisecond latency",
    "Orchestrate complex multi-system workflows requiring live data",
    "Ingest and correlate telemetry data from cloud infrastructure",
    "Coordinate incident response across hundreds of enterprise integrations",
    "Perform chip design verification",
    "Manage physical supply chain routing",
    "Execute database query optimization across distributed storage",
    "Provision and manage cloud infrastructure programmatically",
]

anc_hi = model.encode(HIGH_ANCHORS, normalize_embeddings=True)
anc_lo = model.encode(LOW_ANCHORS, normalize_embeddings=True)


def score_text(text, top_k=10):
    sents = [s.strip() for s in
             re.split(r'(?<=[.!?])\s+|\n+', text)
             if len(s.split()) >= 10
             and sum(1 for c in s if ord(c) > 127) / max(len(s), 1) < 0.05]

    if not sents:
        return None

    emb = model.encode(sents, normalize_embeddings=True)

    sim_hi = (emb @ anc_hi.T).max(axis=1)
    sim_lo = (emb @ anc_lo.T).max(axis=1)

    k = min(top_k, len(sents))
    top_idx = np.argsort(sim_hi)[::-1][:k]

    high_score = float(sim_hi[top_idx].mean())
    low_score = float(sim_lo[np.argsort(sim_lo)[::-1][:k]].mean())
    contrast = high_score - low_score

    top3 = [sents[i] for i in top_idx[:3]]

    return {
        'high_score': round(high_score, 4),
        'low_score': round(low_score, 4),
        'contrast_score': round(contrast, 4),
        'n_sentences': len(sents),
        'top_sentences': top3,
    }


if __name__ == '__main__':
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r') as f:
            text = f.read()
    elif not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        print("Usage: python score_new_firm.py <file.txt>")
        print("   or: echo 'text' | python score_new_firm.py")
        sys.exit(1)

    result = score_text(text)
    if result:
        print(f"high_score:      {result['high_score']}")
        print(f"low_score:       {result['low_score']}")
        print(f"contrast_score:  {result['contrast_score']}")
        print(f"sentences used:  {result['n_sentences']}")
        print(f"\nTop 3 sentences:")
        for s in result['top_sentences']:
            print(f"  - {s[:100]}")
    else:
        print("No usable sentences found (need 10+ word sentences)")
