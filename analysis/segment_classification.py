"""
Segment Classification for B2B Software Firms

Classifies each firm into one of 6 product segments using either:
  1. Claude API (--use-api flag, requires ANTHROPIC_API_KEY)
  2. Keyword-based classifier on 10-K reasoning text (default, reproducible)

Output: data/processed/segment_classification.csv
"""

import os
import re
import sys
import json
import time
import argparse
import pandas as pd

# ── Config ──────────────────────────────────────────────────────────────
MODEL = "claude-sonnet-4-20250514"
TEXT_DIR = "text_data/10k_extracts"
OUTPUT = "data/processed/segment_classification.csv"

SEGMENTS = [
    "customer_engagement",
    "content_knowledge",
    "hr_workforce",
    "devtools_analytics",
    "security_infrastructure",
    "vertical_specialized",
]

SYSTEM_PROMPT = """You are classifying B2B software firms into product segments for an empirical economics study.

Given the firm's 10-K business description and LLM replicability reasoning, classify into exactly one of these segments:

1. customer_engagement — chatbots, CRM, helpdesk, messaging, customer support platforms, contact center software
2. content_knowledge — document management, content platforms, search, knowledge management, content analytics
3. hr_workforce — job matching, payroll, talent management, recruiting, workforce optimization, HCM
4. devtools_analytics — developer platforms, observability, databases, data analytics, CI/CD, APM, ad-tech/programmatic
5. security_infrastructure — cybersecurity, CDN, cloud infrastructure, networking, identity/access management
6. vertical_specialized — healthcare IT, legal tech, finance-specific, EDA, insurance, government, industry-specific SaaS

Rules:
- Choose the SINGLE best-fitting segment based on the firm's PRIMARY revenue source
- If a firm spans multiple segments, pick the one generating the most revenue
- Ad-tech and programmatic advertising platforms go under devtools_analytics
- ERP/financial operations platforms serving specific verticals go under vertical_specialized

Respond with JSON only: {"segment": "...", "confidence": 0-100, "reasoning": "one sentence"}"""

# ── Keyword-based classifier ───────────────────────────────────────────
# Manual overrides for firms where keywords are ambiguous
MANUAL_OVERRIDES = {
    # Customer engagement / support / CRM
    "EGAN":  "customer_engagement",   # Knowledge mgmt for contact centers
    "LPSN":  "customer_engagement",   # Conversational AI, chatbots
    "FRSH":  "customer_engagement",   # Helpdesk, IT ticketing, CRM
    "FIVN":  "customer_engagement",   # Contact center cloud
    "EGHT":  "customer_engagement",   # UCaaS / contact center
    "BRZE":  "customer_engagement",   # Customer engagement platform
    "CXM":   "customer_engagement",   # Sprinklr - social/customer experience
    "PD":    "devtools_analytics",    # PagerDuty - incident management / DevOps
    "HUBS":  "customer_engagement",   # HubSpot CRM
    "BLKB":  "customer_engagement",   # Blackbaud CRM / fundraising
    "RNG":   "customer_engagement",   # RingCentral UCaaS / comms
    "OOMA":  "customer_engagement",   # VoIP / business comms
    "BAND":  "security_infrastructure",  # Telecom infrastructure (CPaaS)

    # Content / knowledge management
    "YEXT":  "content_knowledge",     # Search / knowledge graph
    "BOX":   "content_knowledge",     # Cloud content management
    "WK":    "content_knowledge",     # Workiva - document/reporting
    "INLX":  "content_knowledge",     # Intellicheck - document mgmt
    "BLIN":  "content_knowledge",     # Bridgeline - web CMS / search
    "SPT":   "content_knowledge",     # Sprout Social - social content
    "ONTF":  "content_knowledge",     # ON24 - webinar content platform
    "DBX":   "content_knowledge",     # Dropbox - file storage / content
    "AVPT":  "content_knowledge",     # AvePoint - M365 data mgmt

    # HR / workforce
    "ZIP":   "hr_workforce",          # ZipRecruiter - job matching
    "PCTY":  "hr_workforce",          # Paylocity - HCM/payroll
    "PAYC":  "hr_workforce",          # Paycom - HCM/payroll
    "SKIL":  "content_knowledge",     # Skillsoft - digital learning content

    # DevTools / analytics / data
    "DDOG":  "devtools_analytics",    # Observability / APM
    "DT":    "devtools_analytics",    # Dynatrace - observability
    "GTLB":  "devtools_analytics",    # GitLab - DevOps platform
    "MDB":   "devtools_analytics",    # MongoDB - database
    "ESTC":  "devtools_analytics",    # Elastic - search/analytics
    "CFLT":  "devtools_analytics",    # Confluent - data streaming
    "AI":    "devtools_analytics",    # C3.ai - AI/ML platform
    "PATH":  "devtools_analytics",    # UiPath - RPA / automation
    "APPN":  "devtools_analytics",    # Appian - low-code platform
    "PRGS":  "devtools_analytics",    # Progress Software - dev tools
    "MGNI":  "devtools_analytics",    # Magnite - programmatic ad-tech
    "PUBM":  "devtools_analytics",    # PubMatic - ad-tech SSP
    "RAMP":  "devtools_analytics",    # LiveRamp - data connectivity
    "CDLX":  "devtools_analytics",    # Cardlytics - purchase analytics
    "TTD":   "devtools_analytics",    # The Trade Desk - ad-tech DSP
    "TEAD":  "devtools_analytics",    # Teads - ad-tech
    "PEGA":  "devtools_analytics",    # Pegasystems - BPM / low-code
    "PDFS":  "devtools_analytics",    # PDF Solutions - semiconductor analytics
    "FDS":   "devtools_analytics",    # FactSet - financial data/analytics
    "CLVT":  "devtools_analytics",    # Clarivate - IP/data analytics
    "MCHX":  "devtools_analytics",    # Marchex - call analytics
    "NTWK":  "devtools_analytics",    # NETSOL - leasing/finance software

    # Security / infrastructure / cloud
    "NET":   "security_infrastructure",  # Cloudflare - CDN / security
    "CRWD":  "security_infrastructure",  # CrowdStrike - endpoint security
    "ZS":    "security_infrastructure",  # Zscaler - zero trust security
    "DOCN":  "security_infrastructure",  # DigitalOcean - cloud infra
    "FSLY":  "security_infrastructure",  # Fastly - edge cloud / CDN
    "S":     "security_infrastructure",  # SentinelOne - cybersecurity
    "QLYS":  "security_infrastructure",  # Qualys - vuln management
    "VRNS":  "security_infrastructure",  # Varonis - data security
    "TENB":  "security_infrastructure",  # Tenable - vuln scanning
    "TLS":   "security_infrastructure",  # Telos - cybersecurity
    "CVLT":  "security_infrastructure",  # Commvault - data protection
    "BB":    "security_infrastructure",  # BlackBerry - cybersecurity
    "BLZE":  "security_infrastructure",  # Backblaze - cloud storage infra
    "BKYI":  "security_infrastructure",  # BIO-key - biometric auth
    "AWRE":  "security_infrastructure",  # Aware - biometric auth
    "OKTA":  "security_infrastructure",  # Okta - identity mgmt
    "VRSN":  "security_infrastructure",  # VeriSign - DNS infra
    "NTNX":  "security_infrastructure",  # Nutanix - HCI infra
    "RPD":   "security_infrastructure",  # Rapid7 - cybersecurity
    "NTCT":  "security_infrastructure",  # NetScout - network security
    "RBBN":  "security_infrastructure",  # Ribbon - telecom infra
    "IDN":   "security_infrastructure",  # Intellicheck - identity verification
    "DMRC":  "security_infrastructure",  # Digimarc - digital watermarking

    # Vertical / specialized SaaS
    "HCAT":  "vertical_specialized",  # Health Catalyst - healthcare analytics
    "CCLD":  "vertical_specialized",  # CareCloud - healthcare RCM
    "DOCS":  "vertical_specialized",  # Doximity - physician platform
    "GWRE":  "vertical_specialized",  # Guidewire - insurance
    "VEEV":  "vertical_specialized",  # Veeva - life sciences
    "CEVA":  "vertical_specialized",  # CEVA - semiconductor IP
    "MANH":  "vertical_specialized",  # Manhattan - supply chain / WMS
    "DSGX":  "vertical_specialized",  # Descartes - logistics
    "SPSC":  "vertical_specialized",  # SPS Commerce - EDI / supply chain
    "STEM":  "vertical_specialized",  # Stem - energy storage
    "SSTI":  "vertical_specialized",  # ShotSpotter - gunshot detection
    "DUOT":  "vertical_specialized",  # DUOS - machine vision
    "TCX":   "vertical_specialized",  # Tucows - fiber/domains
    "EVTC":  "vertical_specialized",  # EVERTEC - payment processing (LatAm)
    "MQ":    "vertical_specialized",  # Marqeta - card issuing infra
    "QTWO":  "vertical_specialized",  # Q2 - digital banking
    "ALKT":  "vertical_specialized",  # Alkami - digital banking
    "JKHY":  "vertical_specialized",  # Jack Henry - core banking
    "TDC":   "vertical_specialized",  # Teradata - enterprise data platform
    "BSY":   "vertical_specialized",  # Bentley - infrastructure engineering
    "PTC":   "vertical_specialized",  # PTC - CAD/PLM/IoT
    "TYL":   "vertical_specialized",  # Tyler Technologies - gov software
    "CSGS":  "vertical_specialized",  # CSG Systems - billing/telecom
    "CRNC":  "vertical_specialized",  # Cerence - automotive AI
    "VRME":  "vertical_specialized",  # VerifyMe - physical authentication
    "SLP":   "vertical_specialized",  # Simulations Plus - pharma modeling
    "AGYS":  "vertical_specialized",  # Agilysys - hospitality POS

    # Firms that could go either way — classified by primary revenue
    "ASAN":  "content_knowledge",     # Project mgmt = workflow/content
    "BL":    "vertical_specialized",  # BlackLine - accounting automation
    "BILL":  "vertical_specialized",  # BILL - financial operations
    "INTA":  "vertical_specialized",  # Intapp - professional services
    "FA":    "hr_workforce",          # First Advantage - background screening
    "HSTM":  "content_knowledge",     # HealthStream - learning mgmt
    "PRCH":  "vertical_specialized",  # Porch - home services
    "CREX":  "security_infrastructure", # Creative Realities - managed field tech
    "RDVT":  "security_infrastructure", # RedVisor - identity verification
    "GDYN":  "devtools_analytics",    # Grid Dynamics - digital transformation
    "PCOR":  "vertical_specialized",  # Procore - construction mgmt
    "APPF":  "vertical_specialized",  # AppFolio - property mgmt
    "TRAK":  "vertical_specialized",  # RepoTrax - compliance/supply chain
    "IIIV":  "vertical_specialized",  # i3 Verticals - payment/govt
    "MAPS":  "vertical_specialized",  # WM Technology - cannabis marketplace
    "SMSI":  "vertical_specialized",  # Smith Micro - family safety apps
    "AEYE":  "content_knowledge",     # AudioEye - web accessibility
    "EXFY":  "vertical_specialized",  # Expensify - expense mgmt
}

# Keyword patterns as fallback for any firms not in manual overrides
KEYWORD_RULES = [
    ("security_infrastructure", [
        r"cybersecur", r"firewall", r"endpoint.{0,20}secur", r"zero.trust",
        r"CDN|edge.cloud", r"cloud.infra", r"DNS|domain.name", r"biometric",
        r"identity.{0,15}(verif|manag|access)", r"data.protection",
        r"vulnerability.scan", r"threat.detect", r"network.secur",
    ]),
    ("customer_engagement", [
        r"(customer|contact).{0,15}(support|service|center|engage)",
        r"chatbot", r"helpdesk|help.desk", r"CRM", r"messaging.platform",
        r"conversational.AI", r"UCaaS", r"VoIP",
    ]),
    ("hr_workforce", [
        r"payroll", r"HCM|human.capital", r"recruit", r"talent.manage",
        r"job.match", r"workforce.{0,15}(manage|optim)",
    ]),
    ("content_knowledge", [
        r"document.manage", r"content.manage", r"knowledge.manage",
        r"search.{0,15}(engine|platform)", r"learning.manage",
        r"web.content", r"file.{0,10}(sync|shar|stor)",
    ]),
    ("devtools_analytics", [
        r"observabil", r"APM|application.performance", r"CI/CD",
        r"developer.platform", r"database", r"data.stream",
        r"ad.tech|programmatic|SSP|DSP", r"data.analytics",
        r"low.code", r"RPA|robotic.process", r"call.analytics",
    ]),
    ("vertical_specialized", [
        r"healthcare|health.care|life.science", r"insurance",
        r"banking|financial.institution", r"government|public.sector",
        r"construction", r"property.manage", r"supply.chain",
        r"semiconductor|EDA", r"energy.storage", r"hospitality",
        r"legal.tech", r"pharma",
    ]),
]


def classify_keyword(ticker, reasoning, text_10k=""):
    """Classify using manual overrides first, then keyword matching."""
    if ticker in MANUAL_OVERRIDES:
        return MANUAL_OVERRIDES[ticker], 90, f"Manual classification based on primary business"

    # Combine reasoning and 10-K text for keyword search
    combined = (str(reasoning) + " " + str(text_10k)[:2000]).lower()

    scores = {}
    for seg, patterns in KEYWORD_RULES:
        score = sum(1 for p in patterns if re.search(p, combined, re.IGNORECASE))
        scores[seg] = score

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "vertical_specialized", 50, "No strong keyword match; defaulted to vertical_specialized"

    conf = min(90, 60 + scores[best] * 10)
    return best, conf, f"Keyword match ({scores[best]} patterns for {best})"


def classify_api(client, ticker, text_10k, lit_reasoning):
    """Classify using Claude API."""
    user_msg = (
        f"TICKER: {ticker}\n\n"
        f"10-K BUSINESS DESCRIPTION:\n{text_10k[:4000]}\n\n"
        f"LLM REPLICABILITY REASONING:\n{lit_reasoning}"
    )
    resp = client.messages.create(
        model=MODEL,
        max_tokens=256,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    parsed = json.loads(raw)
    return parsed["segment"], parsed["confidence"], parsed["reasoning"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--use-api", action="store_true",
                        help="Use Claude API instead of keyword classifier")
    args = parser.parse_args()

    client = None
    if args.use_api:
        from anthropic import Anthropic
        client = Anthropic()

    lit = pd.read_csv("data/processed/lit_continuous_scores.csv")

    results = []
    tickers = lit["ticker"].tolist()

    for i, ticker in enumerate(tickers):
        row = lit[lit["ticker"] == ticker].iloc[0]
        reasoning = str(row.get("reasoning", ""))

        # Read 10-K text
        txt_path = os.path.join(TEXT_DIR, f"{ticker}.txt")
        text_10k = ""
        if os.path.exists(txt_path):
            with open(txt_path) as f:
                text_10k = f.read()

        try:
            if args.use_api and client:
                segment, confidence, reason = classify_api(
                    client, ticker, text_10k, reasoning)
                if (i + 1) % 10 == 0:
                    time.sleep(1)
            else:
                segment, confidence, reason = classify_keyword(
                    ticker, reasoning, text_10k)

            results.append({
                "ticker": ticker,
                "segment": segment,
                "confidence": confidence,
                "reasoning": reason,
            })
            print(f"[{i+1}/{len(tickers)}] {ticker}: {segment} ({confidence}%)")
        except Exception as e:
            print(f"[{i+1}/{len(tickers)}] {ticker}: ERROR — {e}")

    df = pd.DataFrame(results)

    # Validate segments
    invalid = df[~df["segment"].isin(SEGMENTS)]
    if len(invalid) > 0:
        print(f"\nWARNING: {len(invalid)} firms with invalid segments:")
        print(invalid[["ticker", "segment"]])

    df.to_csv(OUTPUT, index=False)
    print(f"\nSaved {len(df)} firms to {OUTPUT}")

    # Distribution summary
    print("\n=== SEGMENT DISTRIBUTION ===")
    dist = df.groupby("segment").agg(
        n_firms=("ticker", "count"),
        mean_conf=("confidence", "mean"),
    ).sort_values("n_firms", ascending=False)
    print(dist.round(1).to_string())


if __name__ == "__main__":
    main()
