"""
Step 5: Collect product page text from Wayback Machine.

For each firm: one CDX wildcard query to get all archived URLs,
score them, fetch the top 3 pages, concatenate extracted text.
"""

import re
import sys
import time
import logging
from typing import Optional, List, Tuple
from html.parser import HTMLParser
import requests
import pandas as pd

INPUT_PATH = "data/manual/firm_domains.csv"
OUTPUT_DIR = "text_data/product_pages"
FAILURE_LOG = "logs/wayback_failures.log"

CDX_URL = "https://web.archive.org/cdx/search/cdx"
WAYBACK_URL = "https://web.archive.org/web/{timestamp}/{url}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 thesis-research contact: go52geg@tum.de"
}

CDX_WAIT = 5.0
FETCH_WAIT = 7.0
RETRY_WAIT = 30
TOP_N_PAGES = 3
MIN_WORDS = 150

CDX_PARAMS = {
    "output": "json",
    "fl": "timestamp,original,statuscode",
    "filter": "statuscode:200",
    "from": "20220401",
    "to": "20221001",
    "collapse": "urlkey",
    "limit": "500",
}

# URL scoring rules (patterns match before /, ?, .html, or end-of-string)
_END = r"(/|$|\?|\.html)"
POSITIVE_PATTERNS = [
    (r"/products?" + _END, 3),
    (r"/platform" + _END, 3),
    (r"/features?" + _END, 2),
    (r"/solutions?" + _END, 2),
    (r"/how-it-works" + _END, 2),
    (r"/overview" + _END, 1),
    (r"/why-", 1),
    (r"/capabilities", 1),
]
NEGATIVE_PATTERNS = [
    (r"/blogs?" + _END, -2),
    (r"/news" + _END, -2),
    (r"/pricing" + _END, -2),
    (r"/about" + _END, -2),
    (r"/legal" + _END, -3),
    (r"/terms" + _END, -3),
    (r"/privacy" + _END, -3),
    (r"/careers?" + _END, -3),
    (r"/login" + _END, -3),
    (r"/signup" + _END, -3),
    (r"/press" + _END, -2),
    (r"/investor" + _END, -2),
    (r"/support" + _END, -1),
    (r"/docs" + _END, -1),
    (r"/documentation" + _END, -1),
    (r"/customer-stories" + _END, -1),
    (r"/case-stud", -1),
    (r"/webinar", -1),
    (r"/events?" + _END, -1),
    (r"\.(pdf|png|jpg|css|js|xml|json|zip|mp4|svg)($|\?)", -5),
    (r"-identification" + _END, -3),
    (r"-status" + _END, -2),
    (r"-updates?" + _END, -2),
    (r"/release-notes", -2),
    (r"/changelog", -2),
    (r"/api" + _END, -2),
    (r"/integrations?" + _END, -1),
    (r"/downloads?" + _END, -2),
    (r"/vs[-/]", -1),
    (r"/comparison", -1),
    (r"/accessibility", -2),
    (r"/sitemap", -3),
    (r"/cookie", -3),
    (r"/demo" + _END, -1),
    (r"/contact" + _END, -2),
    (r"/resources?" + _END, -1),
]

# Task-related verbs for text filtering
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

# Junk line patterns to remove
JUNK_PATTERNS = [
    r"cookie", r"cookies", r"sign up", r"sign in", r"log ?in", r"log ?out",
    r"create (a |an )?account", r"forgot (your )?password", r"subscribe",
    r"privacy policy", r"terms of (service|use)", r"all rights reserved",
    r"©\s*\d{4}", r"support@", r"contact us", r"follow us",
    r"accept all", r"reject all", r"manage preferences",
    r"browse experience", r"we use cookies",
    r"sorry,", r"something went wrong",
    r"already exists", r"try again",
    r"^//\s*\w", r"submitting this form",
    r"recovery email", r"provide a recovery",
    r"/accessibility", r"read press release",
    r"read announcement",
]
JUNK_RE = re.compile("|".join(JUNK_PATTERNS), re.IGNORECASE)

logging.basicConfig(
    filename=FAILURE_LOG,
    filemode="w",
    level=logging.WARNING,
    format="%(asctime)s %(message)s",
)
fail_logger = logging.getLogger("wayback_failures")


def score_url(url: str, domain: str) -> int:
    """Score a URL by relevance to product description."""
    url_lower = url.lower()
    path = url_lower.split(domain.lower())[-1] if domain.lower() in url_lower else url_lower

    score = 0

    for pattern, points in POSITIVE_PATTERNS:
        if re.search(pattern, path):
            score += points

    for pattern, points in NEGATIVE_PATTERNS:
        if re.search(pattern, path):
            score += points

    # Homepage gets 1 point
    if re.match(r"^https?://[^/]+/?$", url):
        score += 1

    # Depth penalty: prefer shallower pages
    segments = [s for s in path.strip("/").split("/") if s]
    depth = len(segments)
    if depth <= 1:
        score += 2  # top-level page bonus
    elif depth >= 3:
        score -= (depth - 2)  # penalty for deep pages

    # Query string penalty
    if "?" in url:
        score -= 1

    return score


def fetch_with_retry(url: str, params: Optional[dict] = None) -> Optional[requests.Response]:
    """Fetch URL with one retry on 429/connection error."""
    for attempt in range(2):
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=60)
            if resp.status_code == 429:
                if attempt == 0:
                    print("    429 rate limited, waiting %ds..." % RETRY_WAIT, flush=True)
                    time.sleep(RETRY_WAIT)
                    continue
                return None
            if resp.status_code >= 400:
                if attempt == 0:
                    time.sleep(5)
                    continue
                return None
            return resp
        except requests.RequestException:
            if attempt == 0:
                print("    Connection error, waiting %ds..." % RETRY_WAIT, flush=True)
                time.sleep(RETRY_WAIT)
                continue
            return None
    return None


def find_best_snapshots(domain: str) -> List[Tuple[str, str, int]]:
    """Single CDX wildcard query. Returns top N (timestamp, url, score) by score."""
    params = dict(CDX_PARAMS)
    params["url"] = domain + "/*"

    resp = fetch_with_retry(CDX_URL, params=params)
    if resp is None:
        return []

    try:
        data = resp.json()
    except Exception:
        return []

    if len(data) < 2:
        return []

    # Score all URLs
    scored = []
    seen_urls = set()
    for row in data[1:]:
        timestamp, original = row[0], row[1]
        # Skip broken URLs (e.g., domain.com./something)
        if domain + "./" in original or domain + ".." in original:
            continue
        # Deduplicate by base URL (ignore query string for dedup)
        base = original.split("?")[0].rstrip("/").lower()
        if base in seen_urls:
            continue
        seen_urls.add(base)
        s = score_url(original, domain)
        scored.append((s, timestamp, original))

    if not scored:
        return []

    scored.sort(key=lambda x: (x[0], x[1]), reverse=True)

    # Return top N distinct pages
    top = scored[:TOP_N_PAGES]
    print("    CDX: %d unique URLs, top scores: %s" % (
        len(scored),
        ", ".join("%+d" % t[0] for t in top)), flush=True)
    for s, ts, url in top:
        print("      %+d  %s" % (s, url[:90]), flush=True)

    return [(ts, url, s) for s, ts, url in top]


class TextExtractor(HTMLParser):
    """Extract visible text from HTML, skipping script/style/nav/header/footer."""

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
            self.result = []  # Discard nav/header content before main

    def handle_endtag(self, tag):
        if tag in self.SKIP_TAGS and self.skip_depth > 0:
            self.skip_depth -= 1

    def handle_data(self, data):
        if self.skip_depth == 0:
            text = data.strip()
            if text:
                self.result.append(text)


def extract_text(html: str) -> str:
    """Extract and clean text from HTML."""
    parser = TextExtractor()
    try:
        parser.feed(html)
    except Exception:
        pass

    lines = parser.result

    # Deduplicate while preserving order
    seen = set()
    unique_lines = []
    for line in lines:
        normalized = line.strip().lower()
        if normalized not in seen:
            seen.add(normalized)
            unique_lines.append(line.strip())

    # Remove junk lines
    cleaned = [l for l in unique_lines if not JUNK_RE.search(l)]

    # Two-tier filtering:
    # Tier 1: lines with task verbs (high quality)
    # Tier 2: lines >= 40 chars (likely descriptive even without verbs)
    tier1 = []
    tier2 = []
    for line in cleaned:
        if len(line) < 20:
            continue
        words = set(re.findall(r"[a-z]+", line.lower()))
        if words & TASK_VERBS:
            tier1.append(line)
        elif len(line) >= 40:
            tier2.append(line)

    # Combine: all tier1, then tier2 for additional context
    combined = tier1 + tier2

    # Join and truncate to 3000 words
    text = "\n".join(combined)
    words = text.split()
    if len(words) > 3000:
        text = " ".join(words[:3000])

    return text


def process_firm(ticker: str, company_name: str, domain: str) -> Optional[dict]:
    """Process one firm: one CDX query, fetch top 3 pages, concatenate text."""

    # Step 1: Single CDX query to get top URLs
    snapshots = find_best_snapshots(domain)
    if not snapshots:
        fail_logger.warning("%s (%s): no CDX snapshots found for %s" % (ticker, company_name, domain))
        return None

    time.sleep(CDX_WAIT)

    # Step 2: Fetch top pages and concatenate text
    all_text_parts = []
    fetched_urls = []
    for i, (timestamp, original_url, url_score) in enumerate(snapshots):
        wayback_url = WAYBACK_URL.format(timestamp=timestamp, url=original_url)
        resp = fetch_with_retry(wayback_url)
        if resp is not None:
            text = extract_text(resp.text)
            if text and len(text.split()) >= 5:
                all_text_parts.append(text)
                fetched_urls.append(wayback_url)
                print("    Fetched page %d: %d words  %s" % (
                    i + 1, len(text.split()), original_url[:80]), flush=True)
        if i < len(snapshots) - 1:
            time.sleep(FETCH_WAIT)

    if not all_text_parts:
        fail_logger.warning("%s (%s): all page fetches failed or empty" % (ticker, company_name))
        return None

    # Concatenate and deduplicate across pages
    combined_text = "\n".join(all_text_parts)

    # Deduplicate lines across pages
    seen = set()
    deduped_lines = []
    for line in combined_text.split("\n"):
        normalized = line.strip().lower()
        if normalized and normalized not in seen:
            seen.add(normalized)
            deduped_lines.append(line)
    combined_text = "\n".join(deduped_lines)

    # Truncate to 3000 words
    words = combined_text.split()
    if len(words) > 3000:
        combined_text = " ".join(words[:3000])

    word_count = len(combined_text.split())
    needs_fallback = word_count < MIN_WORDS

    # Use the first fetched URL as the primary snapshot reference
    best_ts = snapshots[0][0]
    date_str = "%s-%s-%s" % (best_ts[:4], best_ts[4:6], best_ts[6:8])

    return {
        "ticker": ticker,
        "company_name": company_name,
        "domain": domain,
        "snapshot_urls": fetched_urls,
        "snapshot_date": date_str,
        "pages_fetched": len(fetched_urls),
        "text": combined_text,
        "word_count": word_count,
        "needs_fallback": needs_fallback,
    }


def main():
    t0 = time.time()

    df = pd.read_csv(INPUT_PATH)

    total = len(df)
    est_min = total * (CDX_WAIT + FETCH_WAIT * TOP_N_PAGES) / 60
    print("Loaded %d firms from %s" % (total, INPUT_PATH), flush=True)
    print("Estimated runtime: ~%.0f min\n" % est_min, flush=True)

    successes = 0
    failures = 0
    failed_tickers = []
    word_counts = []
    fallback_tickers = []

    for i, (_, row) in enumerate(df.iterrows()):
        ticker = row["ticker"]
        company_name = row["company_name"]
        domain = row["domain"]

        print("  %s (%s)..." % (ticker, domain), flush=True)
        result = process_firm(ticker, company_name, domain)

        if result is None:
            failures += 1
            failed_tickers.append(ticker)
            print("    FAILED", flush=True)
        else:
            # Save text file
            output_path = "%s/%s.txt" % (OUTPUT_DIR, ticker)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("---\n")
                f.write("TICKER: %s\n" % result["ticker"])
                f.write("COMPANY: %s\n" % result["company_name"])
                f.write("DOMAIN: %s\n" % result["domain"])
                f.write("PAGES_FETCHED: %d\n" % result["pages_fetched"])
                for j, surl in enumerate(result["snapshot_urls"]):
                    f.write("SNAPSHOT_URL_%d: %s\n" % (j + 1, surl))
                f.write("SNAPSHOT_DATE: %s\n" % result["snapshot_date"])
                if result["needs_fallback"]:
                    f.write("NEEDS_FALLBACK: True\n")
                f.write("---\n")
                f.write(result["text"])

            successes += 1
            word_counts.append(result["word_count"])
            if result["needs_fallback"]:
                fallback_tickers.append(ticker)
                print("    OK: %d words (NEEDS FALLBACK)" % result["word_count"], flush=True)
            else:
                print("    OK: %d words (%d pages)" % (result["word_count"], result["pages_fetched"]), flush=True)

        count = i + 1
        if count % 10 == 0 or count == total:
            elapsed = time.time() - t0
            rate = elapsed / count
            remaining = rate * (total - count)
            print("  [%d/%d] ok=%d fail=%d  elapsed: %.0fs  remaining: %.0fs" % (
                count, total, successes, failures, elapsed, remaining), flush=True)

        time.sleep(CDX_WAIT)

    # --- Summary ---
    elapsed = time.time() - t0
    mean_wc = sum(word_counts) / len(word_counts) if word_counts else 0

    print("\n" + "=" * 50, flush=True)
    print("Firms successfully collected:  %d" % successes, flush=True)
    print("Firms failed:                  %d" % failures, flush=True)
    print("Mean word count:               %.0f" % mean_wc, flush=True)
    if word_counts:
        print("Min word count:                %d" % min(word_counts), flush=True)
        print("Max word count:                %d" % max(word_counts), flush=True)
    print("Time elapsed: %.0fs (%.1f min)" % (elapsed, elapsed / 60), flush=True)

    if fallback_tickers:
        print("\nNeed fallback (%d):" % len(fallback_tickers), flush=True)
        for t in sorted(fallback_tickers):
            print("  %s" % t, flush=True)

    if failed_tickers:
        print("\nFailed firms:", flush=True)
        for t in sorted(failed_tickers):
            print("  %s" % t, flush=True)

    print("\nSaved to %s/" % OUTPUT_DIR, flush=True)
    if failures > 0:
        print("Failures logged to %s" % FAILURE_LOG, flush=True)


if __name__ == "__main__":
    main()
