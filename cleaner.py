import re
from typing import List, Dict


# ==================================================
# Boilerplate Patterns (extendable)
# ==================================================

BOILERPLATE_PATTERNS = [
    r"\bhome\b",
    r"\bsubscribe\b",
    r"\blogin\b",
    r"\bsign up\b",
    r"\ball rights reserved\b",
    r"\bcookie\b",
    r"\bprivacy policy\b",
    r"\bterms of service\b",
    r"\bread more\b",
    r"\bclick here\b",
]


# ==================================================
# Core Cleaning Functions
# ==================================================

def is_boilerplate(text: str) -> bool:
    """
    Detects common UI / boilerplate text.
    """
    lowered = text.lower()
    for pattern in BOILERPLATE_PATTERNS:
        if re.search(pattern, lowered):
            return True
    return False


def normalize_text(text: str) -> str:
    """
    Normalizes whitespace and line breaks.
    """
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_low_quality(text: str, min_length: int = 120) -> bool:
    """
    Filters out very short or low-information chunks.
    """
    if len(text) < min_length:
        return True

    # Too many symbols / no natural language
    alpha_ratio = sum(c.isalpha() for c in text) / max(len(text), 1)
    if alpha_ratio < 0.6:
        return True

    return False


# ==================================================
# Public API
# ==================================================

def clean_records(records: List[Dict]) -> List[Dict]:
    """
    Cleans extracted records by removing boilerplate,
    low-quality chunks, and normalizing text.
    """

    cleaned = []

    for r in records:
        text = r.get("text", "")
        if not text:
            continue

        text = normalize_text(text)

        if is_boilerplate(text):
            continue

        if is_low_quality(text):
            continue

        # keep internal metadata untouched
        new_record = dict(r)
        new_record["text"] = text

        cleaned.append(new_record)

    return cleaned
