import requests
from bs4 import BeautifulSoup
from typing import Tuple
from readability.readability import Document


# -----------------------------------
# Category 1: Static HTML Pages
# -----------------------------------
# Works best for:
# - News & Media websites
# - Blogs & editorial sites
# - Documentation & knowledge bases
# - Wikipedia
# - Academic articles (HTML pages)
# ----------------------------------

def extract_static_html(url: str) -> Tuple[str, str, float]:
    
    response = requests.get(
        url,
        timeout=15,
        verify=False,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    response.raise_for_status()

    doc = Document(response.text)
    html = doc.summary()

    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(separator=" ", strip=True)

    return text, "static_html", 0.9


# --------------------------------------------------
# Category 2: DOM-Based Extraction
# --------------------------------------------------
# Works best for:
# - Forums (Reddit threads, StackOverflow)
# - Job listings
# - Business directories
# - Review & rating websites
# --------------------------------------------------

def extract_dom_based(url: str) -> Tuple[str, str, float]:

    response = requests.get(
        url,
        timeout=15,
        verify=False,
        headers={"User-Agent": "Mozilla/5.0"}
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    elements = soup.find_all(["p","li","h1","h2","h3"])
    text_parts = [el.get_text(strip=True) for el in elements if el.get_text(strip=True)]

    text = " ".join(text_parts)

    return text, "dom_based", 0.8


# --------------------------------------------------
# Category 3: JS-Rendered Pages (Browser-Based)
# --------------------------------------------------
# Works best for:
# - E-commerce platforms (Amazon, Shopify, Walmart)
# - Real estate platforms (Zillow, Realtor)
# - Travel & hospitality sites (Booking, Airbnb)
# --------------------------------------------------

def extract_js_rendered(url: str) -> Tuple[str, str, float]:

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=30000)
        page.wait_for_load_state("networkidle")

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(separator=" ", strip =True)

    return text, "js_rendered", 0.7


# --------------------------------------------------
# Strategy 4: API-Based Extraction (Placeholder)
# --------------------------------------------------
# Intended for:
# - Social media platforms (Reddit, Twitter/X)
# - Financial platforms (Yahoo Finance, APIs)
# --------------------------------------------------
# NOTE: Actual API logic will be implemented later.
# --------------------------------------------------

def extract_api_based(url: str) -> Tuple[str, str, float]:
    """
    Placeholder for API-driven extraction.
    Currently not implemented because of no API.
    """

    return "", "api_based", 0.6



# --------------------------------------------------
# Strategy 5: Fallback / Minimal Extraction
# --------------------------------------------------
# Used when:
# - Site blocks scraping
# - JS rendering fails
# - Page is empty or hostile
# --------------------------------------------------

def extract_fallback(url: str, reason: str = "") -> Tuple[str, str, float]:

    text = "Content could not be reliably extracted from this page."
    if reason:
        text += f" Reason: {reason}"
    
    return text, "fallback", 0.2