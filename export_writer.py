import json
from typing import List, Dict


def write_export_jsonl(records: List[Dict], output_path: str) -> None:
    """
    Writes user-facing JSONL files.
    No internal schema enforcement.
    Assumes records are already export-profiled.
    """

    if not records:
        raise ValueError("No records to write")

    with open(output_path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
