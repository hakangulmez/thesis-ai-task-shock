"""
Step 5: Collect product page text from Wayback Machine.

For each firm: one CDX wildcard query to get all archived URLs,
score them, fetch the top 5 pages, concatenate extracted text.

v2: Aggressive URL scoring to prioritize product/features pages.
    Only re-scrapes firms with low-quality (homepage-only) text.
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
TOP_N_PAGES = 5
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

# URL scoring rules — aggressive v2
# HIGH VALUE (score = 10): product-descriptive pages
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
]
# JUNK (score = -10): exclude entirely
JUNK_PATTERNS_URL = [
    r"/blogs?" + _END,
    r"/press" + _END,
    r"/news" + _END,
    r"/events?" + _END,
    r"/careers?" + _END,
    r"/pricing" + _END,
    r"/login" + _END,
    r"/signup" + _END,
    r"/demo" + _END,
    r"/contact" + _END,
    r"/legal" + _END,
    r"/privacy" + _END,
    r"/terms" + _END,
    r"/about" + _END,
    r"/404" + _END,
    r"\.(pdf|jpg|png|ashx|css|js|xml|json|zip|mp4|svg|gif|ico|woff)($|\?)",
    r"/(au|uk|de|fr|es|ja|zh|pt|it|nl|kr|in|sg|br|mx|ar|cl|co|se|no|dk|fi|pl|cz|hu|ro|tr|ru|tw|hk|nz|ie|at|ch|be|lu|il|ae|sa|za|ph|th|vn|id|my|kr|ap)(/|$)",
    r"/investor" + _END,
    r"/support" + _END,
    r"/docs" + _END,
    r"/documentation" + _END,
    r"/customer-stories" + _END,
    r"/case-stud",
    r"/webinar",
    r"/release-notes",
    r"/changelog",
    r"/api" + _END,
    r"/downloads?" + _END,
    r"/accessibility",
    r"/sitemap",
    r"/cookie",
    r"/resources?" + _END,
    r"-identification" + _END,
    r"-status" + _END,
    r"-updates?" + _END,
    r"/vs[-/]",
    r"/comparison",
    r"/logos?" + _END,
]
MIN_URL_SCORE = 5  # only fetch URLs scoring >= 5 (or homepage fallback)

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
    """Score a URL by relevance to product description.

    Returns:
        10  — high-value product/features/solutions page
         1  — homepage (root domain, fallback only)
       -10  — junk (blog, press, locale, media files, etc.)
    """
    url_lower = url.lower()
    path = url_lower.split(domain.lower())[-1] if domain.lower() in url_lower else url_lower

    # Check junk first — reject immediately
    for pattern in JUNK_PATTERNS_URL:
        if re.search(pattern, path):
            return -10

    # Homepage: root domain only
    if re.match(r"^https?://[^/]+/?$", url):
        return 1

    # High-value product pages
    for pattern in HIGH_VALUE_PATTERNS:
        if re.search(pattern, path):
            return 10

    # Everything else: unknown subpage, score 0
    return 0


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

    # Filter: only URLs scoring >= MIN_URL_SCORE
    qualifying = [(s, ts, url) for s, ts, url in scored if s >= MIN_URL_SCORE]

    if qualifying:
        top = qualifying[:TOP_N_PAGES]
    else:
        # Fallback: use homepage if no qualifying URLs
        homepage = [(s, ts, url) for s, ts, url in scored if s == 1]
        if homepage:
            top = homepage[:1]
            print("    CDX: no qualifying URLs (score >= %d), falling back to homepage" %
                  MIN_URL_SCORE, flush=True)
        else:
            print("    CDX: no qualifying URLs and no homepage found", flush=True)
            return []

    print("    CDX: %d unique URLs, %d qualifying (score >= %d), fetching %d" % (
        len(scored), len(qualifying), MIN_URL_SCORE, len(top)), flush=True)
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


QUALITY_PATH = "data/processed/wayback_quality.csv"


def load_rescrape_tickers():
    """Load tickers that need re-scraping (Category B or C from quality audit)."""
    try:
        qdf = pd.read_csv(QUALITY_PATH)
    except FileNotFoundError:
        print("WARNING: %s not found — will process all firms" % QUALITY_PATH, flush=True)
        return None

    # Only re-scrape firms with best_category != 'A'
    rescrape = set(qdf[qdf["best_category"] != "A"]["ticker"].tolist())
    skip = set(qdf[qdf["best_category"] == "A"]["ticker"].tolist())
    print("Quality audit: %d Category A (skip), %d Category B/C (re-scrape)" % (
        len(skip), len(rescrape)), flush=True)
    return rescrape


def main():
    t0 = time.time()

    df = pd.read_csv(INPUT_PATH)

    # Load re-scrape list from quality audit
    rescrape_tickers = load_rescrape_tickers()

    # Filter to only firms that need re-scraping
    if rescrape_tickers is not None:
        df = df[df["ticker"].isin(rescrape_tickers)].reset_index(drop=True)
        print("Filtered to %d firms needing re-scrape\n" % len(df), flush=True)

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
