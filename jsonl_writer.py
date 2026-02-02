# print("✅ jsonl_writer.py loaded from:", __file__)
import json
from datetime import datetime
from typing import List, Dict, Optional

# ----------------------------
# LOCKED JSONL SCHEMA
# ----------------------------

REQUIRED_FIELDS = {
    "text",
    "source_url",
    "site_type",
    "extraction_strategy",
    "confidence",
    "scraped_at",
}


def validate_record(record: Dict) -> None:
    missing = REQUIRED_FIELDS - record.keys()
    if missing:
        raise ValueError(f"JSONL record missing required fields: {missing}")

    if not isinstance(record["text"], str):
        raise ValueError("Field 'text' must be a string")

    if not isinstance(record["confidence"], (int, float)):
        raise ValueError("Field 'confidence' must be a number")

    if not (0.0 <= record["confidence"] <= 1.0):
        raise ValueError("Field 'confidence' must be between 0 and 1")


def build_record(
    *,
    text: str,
    source_url: str,
    site_type: str,
    extraction_strategy: str,
    confidence: float,
) -> Dict:

    record = {
        "text": text.strip() if text else "",
        "source_url": source_url,
        "site_type": site_type,
        "extraction_strategy": extraction_strategy,
        "confidence": round(float(confidence), 2),
        "scraped_at": datetime.utcnow().isoformat() + "Z",
    }

    validate_record(record)
    return record


def write_jsonl(records: List[Dict], output_path: str) -> None:
    if not records:
        raise ValueError("No records provided")

    with open(output_path, "w", encoding="utf-8") as f:
        for record in records:
            validate_record(record)
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def build_fallback_record(
    *,
    source_url: str,
    site_type: str = "unknown",
    reason: Optional[str] = None,
) -> Dict:
    text = "Content could not be reliably extracted from this page."
    if reason:
        text += f" Reason: {reason}"

    return build_record(
        text=text,
        source_url=source_url,
        site_type=site_type,
        extraction_strategy="fallback",
        confidence=0.2,
    )
