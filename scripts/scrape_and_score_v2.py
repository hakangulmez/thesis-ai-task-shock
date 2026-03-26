"""
Full pipeline: scrape Wayback pages + build sentence-level similarity table.

Part A: For each Wayback firm, query CDX, fetch up to 20 product pages,
        save individual page text files.
Part B: For all 143 firms (Wayback + 10-K), compute per-sentence SBERT
        similarity to 18 high + 10 low anchor sentences.

Output:
  text_data/pages_v2/{TICKER}/*.txt  — individual page text files
  text_data/pages_v2/manifest.csv    — metadata for all fetched pages
  data/processed/sentence_similarities.csv — per-sentence scores
"""

import os
import re
import csv
import sys
import time
import logging
from html.parser import HTMLParser
from typing import Optional, List, Tuple

import requests
import numpy as np
import pandas as pd

# ── Config ──────────────────────────────────────────────────────────

DOMAINS_PATH = "data/manual/firm_domains.csv"
PRODUCT_DIR = "text_data/product_pages"
PAGES_DIR = "text_data/pages_v2"
MANIFEST_PATH = os.path.join(PAGES_DIR, "manifest.csv")
SENTENCE_OUT = "data/processed/sentence_similarities.csv"
LOG_PATH = "logs/full_scrape.log"

CDX_URL = "https://web.archive.org/cdx/search/cdx"
WAYBACK_URL = "https://web.archive.org/web/{timestamp}/{url}"
HEADERS = {"User-Agent": "Mozilla/5.0 thesis-research contact: go52geg@tum.de"}

CDX_WAIT = 3.0
FETCH_WAIT = 4.0
RETRY_WAIT = 15
MAX_PAGES = 20
MIN_PAGE_WORDS = 30
MIN_SENT_WORDS = 10

CDX_PARAMS = {
    "output": "json",
    "fl": "timestamp,original,statuscode",
    "filter": "statuscode:200",
    "from": "20220101",
    "to": "20221201",
    "collapse": "urlkey",
    "limit": "1000",
}

# ── URL patterns ────────────────────────────────────────────────────

_END = r"(/|$|\?|\.html)"

HIGH_VALUE_PATTERNS = [
    r"/features?" + _END,
    r"/capabilities" + _END,
    r"/how-it-works" + _END,
    r"/products?" + _END,
    r"/platform" + _END,
    r"/solutions?" + _END,
    r"/why-us" + _END,
    r"/use-cases?" + _END,
    r"/what-we-do" + _END,
    r"/modules?" + _END,
    r"/overview" + _END,
    r"/tools?" + _END,
    r"/integrations?" + _END,
]

JUNK_PATTERNS_URL = [
    r"/blogs?" + _END, r"/press" + _END, r"/news" + _END,
    r"/events?" + _END, r"/careers?" + _END, r"/pricing" + _END,
    r"/login" + _END, r"/signup" + _END, r"/demo" + _END,
    r"/contact" + _END, r"/legal" + _END, r"/privacy" + _END,
    r"/terms" + _END, r"/about" + _END, r"/404" + _END,
    r"\.(pdf|jpg|png|ashx|css|js|xml|json|zip|mp4|svg|gif|ico|woff)($|\?)",
    r"/(au|uk|de|fr|es|ja|zh|pt|it|nl|kr|in|sg|br|mx|ar|cl|co|se|no|dk|fi|pl|cz|hu|ro|tr|ru|tw|hk|nz|ie|at|ch|be|lu|il|ae|sa|za|ph|th|vn|id|my|ap)(/|$)",
    r"/investor" + _END, r"/support" + _END, r"/docs" + _END,
    r"/documentation" + _END, r"/customer-stories" + _END,
    r"/case-stud", r"/webinar", r"/release-notes", r"/changelog",
    r"/api" + _END, r"/downloads?" + _END, r"/accessibility",
    r"/sitemap", r"/cookie", r"/resources?" + _END,
    r"-identification" + _END, r"-status" + _END,
    r"-updates?" + _END, r"/vs[-/]", r"/comparison",
    r"/logos?" + _END, r"/author/", r"/tag/", r"/category/",
    r"/page/\d+", r"\.atom", r"\.rss",
    r"/feed", r"/wp-content", r"/wp-admin",
    r"\.well-known", r"/robots\.txt",
]

TASK_VERBS = {
    "automate", "manage", "track", "monitor", "analyze", "generate",
    "connect", "integrate", "deploy", "detect", "route", "sync",
    "report", "alert", "search", "extract", "schedule", "collaborate",
    "share", "review", "approve", "optimize", "streamline", "simplify",
    "secure", "protect", "scale", "build", "create", "deliver",
    "enable", "accelerate", "transform", "discover", "unify", "orchestrate",
    "visualize", "predict", "configure", "customize", "empower", "reduce",
    "improve", "increase", "enhance", "drive", "support", "provide",
    "help", "offer", "design", "develop", "test", "process", "handle",
    "store", "access", "control", "identify", "prevent", "resolve",
    "measure", "capture", "engage", "convert", "retain", "acquire",
    "run", "migrate", "audit", "backup", "recover", "encrypt",
    "authenticate", "validate", "govern", "enforce", "prioritize",
    "correlate", "aggregate", "normalize", "ingest", "enrich",
}

JUNK_LINE_PATTERNS = [
    r"cookie", r"cookies", r"sign up", r"sign in", r"log ?in", r"log ?out",
    r"create (a |an )?account", r"forgot (your )?password", r"subscribe",
    r"privacy policy", r"terms of (service|use)", r"all rights reserved",
    r"©\s*\d{4}", r"support@", r"contact us", r"follow us",
    r"accept all", r"reject all", r"manage preferences",
    r"browse experience", r"we use cookies",
    r"sorry,", r"something went wrong", r"already exists", r"try again",
    r"^//\s*\w", r"submitting this form", r"recovery email",
    r"read press release", r"read announcement",
    r"-----BEGIN PGP", r"equal.{0,10}opportunity",
    r"affirmative action", r"protected veteran",
    r"we are hiring", r"join our team", r"talented people like you",
]
JUNK_LINE_RE = re.compile("|".join(JUNK_LINE_PATTERNS), re.IGNORECASE)

# ── Anchor sentences ────────────────────────────────────────────────

HIGH_ANCHORS = [
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

LOW_ANCHORS = [
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

# ── Logging ─────────────────────────────────────────────────────────

logging.basicConfig(
    filename=LOG_PATH, filemode="a", level=logging.INFO,
    format="%(asctime)s %(message)s",
)
log = logging.getLogger("scrape_v2")


# ── URL helpers ─────────────────────────────────────────────────────

def score_url(url: str, domain: str) -> int:
    url_lower = url.lower()
    path = url_lower.split(domain.lower())[-1] if domain.lower() in url_lower else url_lower
    for p in JUNK_PATTERNS_URL:
        if re.search(p, path):
            return -10
    if re.match(r"^https?://[^/]+/?$", url):
        return 1
    for p in HIGH_VALUE_PATTERNS:
        if re.search(p, path):
            return 10
    return 0


def classify_url(url: str, domain: str) -> str:
    path = url.lower().split(domain.lower())[-1] if domain.lower() in url.lower() else url.lower()
    if re.match(r"^https?://[^/]+/?$", url):
        return "homepage"
    mapping = [
        (r"/features?", "features"), (r"/products?", "product"),
        (r"/platform", "platform"), (r"/solutions?", "solutions"),
        (r"/capabilities", "capabilities"), (r"/how-it-works", "how_it_works"),
        (r"/use-cases?", "use_cases"), (r"/modules?", "modules"),
        (r"/overview", "overview"), (r"/integrations?", "integrations"),
        (r"/tools?", "tools"), (r"/services?", "services"),
    ]
    for pat, label in mapping:
        if re.search(pat, path):
            return label
    return "other_product"


# ── HTML extraction ─────────────────────────────────────────────────

class TextExtractor(HTMLParser):
    SKIP_TAGS = {"script", "style", "noscript", "svg", "nav", "header", "footer"}

    def __init__(self):
        super().__init__()
        self.result = []
        self.skip_depth = 0
        self.found_main = False

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
        if tag in ("main", "article") and not self.found_main:
            self.found_main = True
            self.result = []

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS and self.skip_depth > 0:
            self.skip_depth -= 1

    def handle_data(self, data):
        if self.skip_depth == 0:
            text = data.strip()
            if text:
                self.result.append(text)


def extract_text(html: str) -> str:
    parser = TextExtractor()
    try:
        parser.feed(html)
    except Exception:
        pass

    seen = set()
    unique = []
    for line in parser.result:
        n = line.strip().lower()
        if n not in seen:
            seen.add(n)
            unique.append(line.strip())

    cleaned = [l for l in unique if not JUNK_LINE_RE.search(l)]

    tier1, tier2 = [], []
    for line in cleaned:
        if len(line) < 20:
            continue
        words = set(re.findall(r"[a-z]+", line.lower()))
        if words & TASK_VERBS:
            tier1.append(line)
        elif len(line) >= 40:
            tier2.append(line)

    return "\n".join(tier1 + tier2)


def is_garbage(text: str) -> bool:
    if not text:
        return True
    non_ascii = sum(1 for c in text if ord(c) > 127)
    return non_ascii > len(text) * 0.05


# ── Network helpers ─────────────────────────────────────────────────

def fetch_with_retry(url: str, params=None, max_retries=2) -> Optional[requests.Response]:
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=12)
            if resp.status_code == 429:
                wait = RETRY_WAIT * (attempt + 1)
                log.info("429 rate limited, waiting %ds" % wait)
                time.sleep(wait)
                continue
            if resp.status_code >= 400:
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                return None
            return resp
        except requests.RequestException as e:
            wait = RETRY_WAIT * (attempt + 1)
            log.info("Connection error (%s), waiting %ds" % (str(e)[:80], wait))
            time.sleep(wait)
    return None


def cdx_query(domain: str) -> List[Tuple[str, str, int, str]]:
    """Query CDX for domain. Returns list of (timestamp, url, score, url_type)."""
    # Try targeted path queries first, then wildcard
    path_prefixes = ["feature", "product", "platform", "solution",
                     "capabilit", "how-it-works", "use-case",
                     "overview", "module", "tool", "integration", "service"]

    all_results = {}  # url_base -> (score, timestamp, url)

    # Targeted queries
    for prefix in path_prefixes:
        for base in [domain, "www." + domain]:
            params = dict(CDX_PARAMS)
            params["url"] = base + "/" + prefix + "*"
            params["limit"] = "100"
            resp = fetch_with_retry(CDX_URL, params=params)
            if resp is None:
                continue
            try:
                data = resp.json()
            except Exception:
                continue
            if len(data) < 2:
                continue
            for row in data[1:]:
                ts, orig = row[0], row[1]
                base_url = orig.split("?")[0].rstrip("/").lower()
                if base_url in all_results:
                    continue
                s = score_url(orig, domain)
                if s > 0:
                    all_results[base_url] = (s, ts, orig)
            time.sleep(1.5)

    # Always get homepage
    for base in [domain, "www." + domain]:
        params = dict(CDX_PARAMS)
        params["url"] = "https://" + base + "/"
        params["limit"] = "5"
        resp = fetch_with_retry(CDX_URL, params=params)
        if resp is not None:
            try:
                data = resp.json()
                if len(data) >= 2:
                    row = data[1]
                    base_url = row[1].split("?")[0].rstrip("/").lower()
                    if base_url not in all_results:
                        all_results[base_url] = (1, row[0], row[1])
            except Exception:
                pass
        time.sleep(1.0)

    # If fewer than 5 results, try wildcard
    if len(all_results) < 5:
        for base in [domain, "www." + domain]:
            params = dict(CDX_PARAMS)
            params["url"] = base + "/*"
            params["limit"] = "500"
            resp = fetch_with_retry(CDX_URL, params=params)
            if resp is None:
                continue
            try:
                data = resp.json()
            except Exception:
                continue
            for row in data[1:]:
                ts, orig = row[0], row[1]
                base_url = orig.split("?")[0].rstrip("/").lower()
                if base_url in all_results:
                    continue
                s = score_url(orig, domain)
                if s > 0:
                    all_results[base_url] = (s, ts, orig)
            time.sleep(CDX_WAIT)

    # Sort by score desc, take top MAX_PAGES
    ranked = sorted(all_results.values(), key=lambda x: x[0], reverse=True)[:MAX_PAGES]
    results = []
    for s, ts, url in ranked:
        utype = classify_url(url, domain)
        results.append((ts, url, s, utype))

    return results


# ── Sentence splitting ──────────────────────────────────────────────

def split_sentences(text: str) -> List[str]:
    raw = re.split(r'(?<=[.!?])\s+|\n+', text)
    return [s.strip() for s in raw if len(s.split()) >= MIN_SENT_WORDS]


# ── Identify 10-K fallback firms ────────────────────────────────────

def is_10k_fallback(ticker: str) -> bool:
    path = os.path.join(PRODUCT_DIR, "%s.txt" % ticker)
    if not os.path.exists(path):
        return False
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        head = f.read(500)
    if "FALLBACK: True" in head:
        return True
    if "FILING_DATE:" in head and "ACCESSION:" in head:
        return True
    return False


# ── PART A: Scrape ──────────────────────────────────────────────────

def scrape_all_wayback_firms():
    """Scrape Wayback pages for all non-10K firms."""
    domains = pd.read_csv(DOMAINS_PATH)
    scores = pd.read_csv("data/processed/replicability_scores.csv")

    # Identify which firms to scrape (wayback only)
    wb_tickers = []
    fb_tickers = []
    for _, row in domains.iterrows():
        ticker = row["ticker"]
        if is_10k_fallback(ticker):
            fb_tickers.append(ticker)
        else:
            wb_tickers.append(ticker)

    print("Wayback firms to scrape: %d" % len(wb_tickers), flush=True)
    print("10-K fallback firms (skip scraping): %d" % len(fb_tickers), flush=True)

    # Load existing manifest for resumability
    completed = set()
    if os.path.exists(MANIFEST_PATH):
        mf = pd.read_csv(MANIFEST_PATH)
        completed = set(mf["ticker"].unique())
    # Also skip firms that already have pages_v2 directories with files
    for d in os.listdir(PAGES_DIR) if os.path.isdir(PAGES_DIR) else []:
        dpath = os.path.join(PAGES_DIR, d)
        if os.path.isdir(dpath) and any(f.endswith(".txt") for f in os.listdir(dpath)):
            completed.add(d)
    print("Already completed: %d firms" % len(completed), flush=True)

    manifest_rows = []
    domain_map = dict(zip(domains["ticker"], domains["domain"]))
    company_map = dict(zip(domains["ticker"], domains["company_name"]))

    t_start = time.time()
    todo = [t for t in sorted(wb_tickers) if t not in completed]
    print("Remaining to scrape: %d firms\n" % len(todo), flush=True)

    for idx, ticker in enumerate(todo):
        domain = domain_map[ticker]
        company = company_map[ticker]
        firm_dir = os.path.join(PAGES_DIR, ticker)
        os.makedirs(firm_dir, exist_ok=True)

        elapsed = time.time() - t_start
        rate = elapsed / max(idx, 1)
        eta = rate * (len(todo) - idx)
        print("=" * 60, flush=True)
        print("[%d/%d] %s (%s)  ETA: %.0fm" % (
            idx + 1, len(todo), ticker, domain, eta / 60), flush=True)

        # CDX query
        snapshots = cdx_query(domain)
        if not snapshots:
            log.info("%s: no CDX results" % ticker)
            print("  No CDX results", flush=True)
            continue

        print("  Found %d URLs to fetch" % len(snapshots), flush=True)

        # Fetch pages
        pages_saved = 0
        seen_text = set()  # cross-page dedup
        for i, (ts, orig_url, url_score, url_type) in enumerate(snapshots):
            wb_url = WAYBACK_URL.format(timestamp=ts, url=orig_url)
            resp = fetch_with_retry(wb_url)
            if resp is None:
                continue

            text = extract_text(resp.text)
            if not text or len(text.split()) < MIN_PAGE_WORDS:
                continue
            if is_garbage(text):
                log.info("%s: garbage text from %s" % (ticker, orig_url[:80]))
                continue

            # Cross-page dedup: skip if >80% of lines already seen
            lines = text.strip().split("\n")
            new_lines = [l for l in lines if l.strip().lower() not in seen_text]
            if len(new_lines) < len(lines) * 0.2:
                continue
            for l in lines:
                seen_text.add(l.strip().lower())

            # Save page text
            safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', url_type)
            fname = "%s_%02d.txt" % (safe_name, pages_saved)
            fpath = os.path.join(firm_dir, fname)
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(text)

            manifest_rows.append({
                "ticker": ticker,
                "company_name": company,
                "filename": fname,
                "original_url": orig_url,
                "url_type": url_type,
                "url_score": url_score,
                "timestamp": ts,
                "word_count": len(text.split()),
                "text_source": "wayback",
            })
            pages_saved += 1
            print("  [%d] %4d words  %-15s %s" % (
                pages_saved, len(text.split()), url_type, orig_url[:65]), flush=True)

            if i < len(snapshots) - 1:
                time.sleep(FETCH_WAIT)

        log.info("%s: %d pages saved" % (ticker, pages_saved))
        print("  → %d pages saved" % pages_saved, flush=True)

        # Append to manifest after each firm (for resumability)
        if manifest_rows:
            write_header = not os.path.exists(MANIFEST_PATH)
            with open(MANIFEST_PATH, "a", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=manifest_rows[0].keys())
                if write_header:
                    w.writeheader()
                w.writerows(manifest_rows)
            manifest_rows = []

    print("\n" + "=" * 60, flush=True)
    print("PART A COMPLETE: Scraping finished in %.0f minutes" % (
        (time.time() - t_start) / 60), flush=True)


# ── PART B: Build sentence similarities ─────────────────────────────

def build_sentence_similarities():
    """Compute per-sentence SBERT similarities for all 143 firms."""
    from sentence_transformers import SentenceTransformer

    print("\n" + "=" * 60, flush=True)
    print("PART B: Building sentence similarity table", flush=True)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    anc_hi = model.encode(HIGH_ANCHORS, normalize_embeddings=True)
    anc_lo = model.encode(LOW_ANCHORS, normalize_embeddings=True)

    domains = pd.read_csv(DOMAINS_PATH)
    company_map = dict(zip(domains["ticker"], domains["company_name"]))
    all_tickers = sorted(domains["ticker"].tolist())

    all_rows = []

    for ticker in all_tickers:
        company = company_map.get(ticker, "")

        if is_10k_fallback(ticker):
            # Use 10-K text
            path = os.path.join(PRODUCT_DIR, "%s.txt" % ticker)
            if not os.path.exists(path):
                continue
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            if content.startswith("---\n"):
                parts = content.split("---\n", 2)
                body = parts[2] if len(parts) >= 3 else content
            else:
                body = content
            sents = split_sentences(body)
            for i, s in enumerate(sents):
                all_rows.append({
                    "ticker": ticker, "company_name": company,
                    "text_source": "10k_fallback",
                    "page_url": "10-K filing", "page_type": "10k",
                    "sentence_idx": i, "sentence": s,
                })
        else:
            # Use scraped pages
            firm_dir = os.path.join(PAGES_DIR, ticker)
            has_v2_pages = os.path.isdir(firm_dir) and any(f.endswith(".txt") for f in os.listdir(firm_dir))
            if not has_v2_pages:
                # Fall back to existing product text
                path = os.path.join(PRODUCT_DIR, "%s.txt" % ticker)
                if os.path.exists(path):
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    if content.startswith("---\n"):
                        parts = content.split("---\n", 2)
                        body = parts[2] if len(parts) >= 3 else content
                    else:
                        body = content
                    sents = split_sentences(body)
                    for i, s in enumerate(sents):
                        all_rows.append({
                            "ticker": ticker, "company_name": company,
                            "text_source": "wayback_v1",
                            "page_url": "legacy", "page_type": "unknown",
                            "sentence_idx": i, "sentence": s,
                        })
                continue

            # Read manifest for this firm
            if os.path.exists(MANIFEST_PATH):
                mf = pd.read_csv(MANIFEST_PATH)
                firm_mf = mf[mf["ticker"] == ticker]
            else:
                firm_mf = pd.DataFrame()

            seen_sents = set()
            for fname in sorted(os.listdir(firm_dir)):
                if not fname.endswith(".txt"):
                    continue
                fpath = os.path.join(firm_dir, fname)
                with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()

                # Get URL info from manifest
                mf_row = firm_mf[firm_mf["filename"] == fname]
                if len(mf_row) > 0:
                    page_url = str(mf_row.iloc[0]["original_url"])
                    page_type = str(mf_row.iloc[0]["url_type"])
                else:
                    page_url = fname
                    page_type = fname.split("_")[0]

                sents = split_sentences(text)
                for s in sents:
                    s_norm = s.strip().lower()
                    if s_norm in seen_sents:
                        continue
                    seen_sents.add(s_norm)
                    all_rows.append({
                        "ticker": ticker, "company_name": company,
                        "text_source": "wayback_v2",
                        "page_url": page_url, "page_type": page_type,
                        "sentence_idx": len([r for r in all_rows if r["ticker"] == ticker]),
                        "sentence": s,
                    })

    print("Total sentences collected: %d" % len(all_rows), flush=True)

    if not all_rows:
        print("ERROR: No sentences collected!", flush=True)
        return

    # Encode all sentences
    sentences = [r["sentence"] for r in all_rows]
    print("Encoding %d sentences with SBERT..." % len(sentences), flush=True)
    sent_emb = model.encode(sentences, normalize_embeddings=True,
                            batch_size=256, show_progress_bar=True)

    # Compute similarities
    print("Computing similarities...", flush=True)
    sim_hi = sent_emb @ anc_hi.T  # (N, 18)
    sim_lo = sent_emb @ anc_lo.T  # (N, 10)

    max_hi = sim_hi.max(axis=1)
    best_hi = sim_hi.argmax(axis=1)
    max_lo = sim_lo.max(axis=1)
    best_lo = sim_lo.argmax(axis=1)

    # Build output dataframe
    for i, row in enumerate(all_rows):
        row["max_sim_hi"] = round(float(max_hi[i]), 4)
        row["max_sim_lo"] = round(float(max_lo[i]), 4)
        row["best_anchor_hi"] = HIGH_ANCHORS[best_hi[i]][:60]
        row["best_anchor_lo"] = LOW_ANCHORS[best_lo[i]][:60]
        row["contrast_sim"] = round(float(max_hi[i] - max_lo[i]), 4)

    df = pd.DataFrame(all_rows)

    # Re-index sentence_idx per firm
    df["sentence_idx"] = df.groupby("ticker").cumcount()

    os.makedirs(os.path.dirname(SENTENCE_OUT), exist_ok=True)
    df.to_csv(SENTENCE_OUT, index=False)
    print("\nSaved %d rows to %s" % (len(df), SENTENCE_OUT), flush=True)

    # Summary
    print("\n" + "=" * 60, flush=True)
    print("SENTENCE SIMILARITY SUMMARY", flush=True)
    print("  Total firms:     %d" % df["ticker"].nunique(), flush=True)
    print("  Total sentences: %d" % len(df), flush=True)
    print("  By source:", flush=True)
    for src, cnt in df["text_source"].value_counts().items():
        n_firms = df[df["text_source"] == src]["ticker"].nunique()
        print("    %-15s %5d sentences, %3d firms" % (src, cnt, n_firms), flush=True)
    print("  By page_type:", flush=True)
    for pt, cnt in df["page_type"].value_counts().head(15).items():
        print("    %-20s %5d" % (pt, cnt), flush=True)

    stats = df.groupby("ticker").agg(
        n_sents=("sentence_idx", "count"),
        mean_hi=("max_sim_hi", "mean"),
        mean_lo=("max_sim_lo", "mean"),
    )
    print("\n  Sentences per firm: mean=%.0f, min=%d, max=%d" % (
        stats["n_sents"].mean(), stats["n_sents"].min(), stats["n_sents"].max()), flush=True)


# ── Main ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--part", choices=["A", "B", "AB"], default="AB",
                        help="Run part A (scrape), B (score), or AB (both)")
    args = parser.parse_args()

    print("=" * 60, flush=True)
    print("PIPELINE: part=%s" % args.part, flush=True)
    print("=" * 60, flush=True)

    if "A" in args.part:
        scrape_all_wayback_firms()

    if "B" in args.part:
        build_sentence_similarities()

    print("\nPIPELINE COMPLETE", flush=True)
