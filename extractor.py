from typing import List
from urllib.parse import urlparse
from strategies import (
    extract_static_html,
    extract_dom_based,
    extract_js_rendered,
    extract_fallback
)
from chunker import build_chunk_records
from jsonl_writer import build_record, build_fallback_record


# --------------------------------------------------
# Site Type Detection (Heuristic, Not Perfect)
# --------------------------------------------------

def detect_site_type(url: str) -> str:
    domain = urlparse(url).netloc.lower()

    if any(k in domain for k in ["amazon", "ebay", "walmart","shopify"]):
        return "ecommerce"
    if any(k in domain for k in ["zillow", "realtor", "redfin"]):
        return "real_estate"
    if any(k in domain for k in ["wikipedia", "news", "bbc", "cnn", "thehindu"]):
        return "news"
    if any(k in domain for k in ["docs", "developer", "python.org"]):
        return "docs"
    if any(k in domain for k in ["reddit", "stackoverflow", "quora"]):
        return "forum"
    if any(k in domain for k in ["linkedin", "indeed", "glassdoor"]):
        return "job"
    if any(k in domain for k in ["arxiv", "pubmed"]):
        return "academic"

    return "unknown"

# --------------------------------------------------
# Primary Strategy Selection
# --------------------------------------------------

def choose_primary_strategy(site_type: str) -> str:

    if site_type in ["news", "academic"]:
        return "static_html"

    if site_type in ["docs", "forum", "job"]:
        return "dom_based"

    if site_type in ["ecommerce", "real_estate"]:
        return "js_rendered"

    return "dom_based"


# --------------------------------------------------
# Strategy Executor
# --------------------------------------------------

def run_strategy(strategy: str, url: str):
    if strategy == "static_html":
        return extract_static_html(url)

    if strategy == "dom_based":
        return extract_dom_based(url)

    if strategy == "js_rendered":
        return extract_js_rendered(url)

    return extract_fallback(url, reason="Unknown strategy")


# --------------------------------------------------
# Core Extraction Pipeline (Robust)
# --------------------------------------------------

def extract_url_to_records(url: str) -> List[dict]:
    site_type = detect_site_type(url)
    primary_strategy = choose_primary_strategy(site_type)

    try:
        # ---- First attempt ----
        text, used_strategy, confidence = run_strategy(primary_strategy, url)

        # ---- Quality check ----
        if not text or len(text.strip()) < 300:
            # Retry with DOM-based extraction before giving up
            text, used_strategy, confidence = extract_dom_based(url)

        # ---- Final validation ----
        if not text or len(text.strip()) < 300:
            raise ValueError("Extracted text too small after retries")

        # ---- Chunking ----
        chunk_records = build_chunk_records(
            text=text,
            source_url=url,
            site_type=site_type,
            extraction_strategy=used_strategy,
            base_confidence=confidence,
        )

        if not chunk_records:
            raise ValueError("No valid chunks produced")

        # ---- Schema enforcement ----
        return [
            build_record(**record)
            for record in chunk_records
        ]

    except Exception as e:
        # Absolute safety net
        return [
            build_fallback_record(
                source_url=url,
                site_type=site_type,
                reason=str(e),
            )
        ]


# --------------------------------------------------
# Batch Processing
# --------------------------------------------------

def extract_urls(urls: List[str]) -> List[dict]:
    all_records = []

    for url in urls:
        records = extract_url_to_records(url)
        all_records.extend(records)

    return all_records