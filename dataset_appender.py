import json
import re
import hashlib
from pathlib import Path
from typing import List, Dict


class DatasetAppendError(Exception):
    pass


# ==================================================
# Text Normalization
# ==================================================

def normalize_text(text: str) -> str:
    """
    Normalizes text for deduplication:
    - lowercase
    - remove punctuation
    - normalize whitespace
    """
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def text_fingerprint(text: str) -> str:
    """
    Generates a stable fingerprint for near-duplicate detection.
    """
    normalized = normalize_text(text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


# ==================================================
# Validation
# ==================================================

def _validate_jsonl_record(record: Dict) -> None:
    if not isinstance(record, dict):
        raise DatasetAppendError("Record is not a JSON object")
    if "text" not in record or not record["text"].strip():
        raise DatasetAppendError("Missing or empty text field")


# ==================================================
# Dataset Appender
# ==================================================

def append_jsonl_datasets(
    input_files: List[Path],
    output_file: Path,
    deduplicate: bool = True,
    add_dataset_source: bool = False,
    use_fingerprint: bool = True,
) -> Dict[str, int]:
    """
    Appends multiple JSONL datasets with improved deduplication.

    Dedup strategy:
    - normalize text
    - optional fingerprint-based comparison
    """

    seen = set()
    written = 0
    skipped_duplicates = 0
    skipped_invalid = 0

    with open(output_file, "w", encoding="utf-8") as out_f:
        for file_path in input_files:
            if not file_path.exists():
                raise DatasetAppendError(f"File not found: {file_path}")

            with open(file_path, "r", encoding="utf-8") as in_f:
                for line in in_f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        record = json.loads(line)
                        _validate_jsonl_record(record)

                        raw_text = record["text"]
                        key = (
                            text_fingerprint(raw_text)
                            if use_fingerprint
                            else normalize_text(raw_text)
                        )

                        if deduplicate:
                            if key in seen:
                                skipped_duplicates += 1
                                continue
                            seen.add(key)

                        if add_dataset_source:
                            record["dataset_source"] = file_path.name

                        out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
                        written += 1

                    except Exception:
                        skipped_invalid += 1
                        continue

    return {
        "written_records": written,
        "skipped_duplicates": skipped_duplicates,
        "skipped_invalid": skipped_invalid,
        "input_files": len(input_files),
        "dedup_strategy": "fingerprint" if use_fingerprint else "normalized_text",
    }
