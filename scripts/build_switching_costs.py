"""
Build switching cost proxy from 10-K RPO disclosures.

Extracts ASC 606 remaining performance obligations (RPO)
contract duration from each firm's 10-K text. Longer RPO
horizons indicate stickier contracts → higher switching costs.

Duration scoring:
  1 (short)  → "next 12 months" / "one year"     → normalized 0.0
  2 (medium) → "two years" / "24 months"          → normalized 0.5
  3 (long)   → "three years" / "36 months"        → normalized 1.0
"""

import os
import re
import pandas as pd

TENK_DIR = "text_data/10k_extracts"
UNIVERSE_PATH = "data/raw/firm_universe_v1.csv"
OUTPUT_PATH = "data/processed/switching_costs.csv"


def load_universe():
    """Load firm universe and return ticker->company mapping."""
    df = pd.read_csv(UNIVERSE_PATH)
    df = df[df["meets_filters"] == True]
    return dict(zip(df["ticker"], df["company_name"]))


def extract_rpo_passages(text):
    """Find all passages mentioning remaining performance obligations."""
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    passages = []
    # Search for RPO-related sentences
    patterns = [
        r'remaining\s+performance\s+obligat',
        r'transaction\s+price\s+allocated\s+to\s+remaining',
        r'unsatisfied\s+(?:or\s+partially\s+unsatisfied\s+)?performance\s+obligat',
        r'expect\s+to\s+recognize.*?(?:revenue|obligation)',
        r'backlog',
    ]

    for pat in patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            start = max(0, m.start() - 100)
            end = min(len(text), m.end() + 400)
            passage = text[start:end].strip()
            passages.append(passage)

    return passages


def score_duration(passages):
    """Score contract duration from RPO passages.

    Returns (raw_score, best_passage):
      1 = short (12 months / one year)
      2 = medium (two years / 24 months)
      3 = long (three+ years / 36+ months / beyond)
    """
    if not passages:
        return None, ""

    combined = " ".join(passages).lower()

    # Look for longest duration mentioned — that's the RPO horizon
    score = None
    best_passage = passages[0]  # default to first passage

    # Score 3: long contracts (three+ years, 36+ months, beyond)
    long_patterns = [
        r'(?:three|four|five|six|seven|3|4|5|6|7)\s+years',
        r'(?:36|48|60)\s+months',
        r'beyond\s+(?:the\s+)?(?:next\s+)?(?:12|24|twenty.?four|twelve)\s+months',
        r'remainder.*?(?:thereafter|beyond)',
        r'thereafter',
        r'over\s+the\s+next\s+(?:three|four|five|3|4|5)\s+years',
    ]
    for pat in long_patterns:
        m = re.search(pat, combined)
        if m:
            score = 3
            # Find the passage containing this match
            for p in passages:
                if re.search(pat, p.lower()):
                    best_passage = p
                    break
            break

    # Score 2: medium contracts (two years, 24 months)
    if score is None:
        medium_patterns = [
            r'(?:two|2)\s+years',
            r'24\s+months',
            r'over\s+the\s+next\s+(?:two|2)\s+years',
            r'next\s+(?:24|twenty.?four)\s+months',
        ]
        for pat in medium_patterns:
            m = re.search(pat, combined)
            if m:
                score = 2
                for p in passages:
                    if re.search(pat, p.lower()):
                        best_passage = p
                        break
                break

    # Score 1: short contracts (12 months, one year, next year)
    if score is None:
        short_patterns = [
            r'(?:next|within)\s+(?:12|twelve)\s+months',
            r'(?:next|within)\s+(?:one|1)\s+year',
            r'over\s+the\s+next\s+(?:12|twelve)\s+months',
            r'within\s+the\s+next\s+year',
        ]
        for pat in short_patterns:
            m = re.search(pat, combined)
            if m:
                score = 1
                for p in passages:
                    if re.search(pat, p.lower()):
                        best_passage = p
                        break
                break

    # If we found RPO passages but couldn't parse a duration,
    # check if there's any mention of recognizing revenue
    if score is None and passages:
        # RPO mentioned but no clear duration → likely short
        recognize_pat = r'expect\s+to\s+recognize'
        if re.search(recognize_pat, combined):
            score = 1
            for p in passages:
                if re.search(recognize_pat, p.lower()):
                    best_passage = p
                    break

    return score, best_passage[:300] if best_passage else ""


def normalize_score(raw_score):
    """Normalize duration score to [0, 1]."""
    if raw_score is None:
        return None
    mapping = {1: 0.0, 2: 0.5, 3: 1.0}
    return mapping.get(raw_score)


def main():
    universe = load_universe()
    print("Firms in universe: %d" % len(universe))

    results = []
    missing_text = []

    for ticker in sorted(universe.keys()):
        path = os.path.join(TENK_DIR, "%s.txt" % ticker)
        if not os.path.exists(path):
            missing_text.append(ticker)
            continue

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Strip YAML header
        if content.startswith("---\n"):
            parts = content.split("---\n", 2)
            text = parts[2] if len(parts) >= 3 else content
        else:
            text = content

        passages = extract_rpo_passages(text)
        raw_score, raw_text = score_duration(passages)
        norm_score = normalize_score(raw_score)

        results.append({
            "ticker": ticker,
            "company_name": universe[ticker],
            "rpo_duration_score": norm_score,
            "rpo_duration_raw": raw_score,
            "rpo_raw_text": raw_text,
            "has_rpo": len(passages) > 0,
        })

    # Save
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df = pd.DataFrame(results)
    df.to_csv(OUTPUT_PATH, index=False)
    print("Saved %d rows to %s" % (len(df), OUTPUT_PATH))

    if missing_text:
        print("\nMissing 10-K text (%d): %s" % (len(missing_text), ", ".join(missing_text)))

    # --- Summary statistics ---
    has_rpo = df[df["has_rpo"] == True]
    no_rpo = df[df["has_rpo"] == False]
    scored = df.dropna(subset=["rpo_duration_score"])

    print("\n" + "=" * 60)
    print("RPO DISCLOSURE SUMMARY")
    print("  Firms with RPO passages:    %d / %d" % (len(has_rpo), len(df)))
    print("  Firms without RPO passages: %d / %d" % (len(no_rpo), len(df)))
    print("  Firms with scored duration: %d / %d" % (len(scored), len(df)))

    if len(scored) > 0:
        print("\nDURATION SCORE DISTRIBUTION:")
        for raw_val, norm_val, label in [(1, 0.0, "short"), (2, 0.5, "medium"), (3, 1.0, "long")]:
            count = len(scored[scored["rpo_duration_raw"] == raw_val])
            print("  %s (%.1f): %d firms" % (label, norm_val, count))

    # Examples for validation
    print("\nEXAMPLES — LONG CONTRACTS (score=1.0):")
    long_firms = scored[scored["rpo_duration_raw"] == 3].head(5)
    for _, row in long_firms.iterrows():
        print("  %-6s %s" % (row["ticker"], row["company_name"]))
        print("         \"%s...\"" % row["rpo_raw_text"][:150])
        print()

    print("EXAMPLES — SHORT CONTRACTS (score=0.0):")
    short_firms = scored[scored["rpo_duration_raw"] == 1].head(5)
    for _, row in short_firms.iterrows():
        print("  %-6s %s" % (row["ticker"], row["company_name"]))
        print("         \"%s...\"" % row["rpo_raw_text"][:150])
        print()

    print("EXAMPLES — NO RPO FOUND:")
    no_rpo_sample = no_rpo.head(5)
    for _, row in no_rpo_sample.iterrows():
        print("  %-6s %s" % (row["ticker"], row["company_name"]))


if __name__ == "__main__":
    main()
