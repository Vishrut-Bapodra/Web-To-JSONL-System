from typing import List, Dict


# ----------------------------
# Profile: Training Minimal
# ----------------------------

def export_training_minimal(records: List[Dict]) -> List[Dict]:

    exported = []

    for r in records:
        if not r.get("text"):
            continue
        exported.append({
            "text": r["text"]
        })
    
    return exported


# ----------------------------
# Profile: Training With Source
# ----------------------------

def export_training_with_source(records: List[Dict]) -> List[Dict]:

    exported = []
    for r in records:
        if not r.get("text"):
            continue

        exported.append({
            "text": r["text"],
            "source_url": r.get("source_url")
        })

    return exported


# ----------------------------
# Profile: Debug / Internal
# ----------------------------

def export_debug_full(records: List[Dict]) -> List[Dict]:
    return records


# ----------------------------
# Profile Selector
# ----------------------------

def apply_export_profile(records: List[Dict], profile: str = "training_minimal") -> List[Dict]:

    if profile == "training_minimal":
        return export_training_minimal(records)
    
    if profile == "training_with_source":
        return export_training_with_source(records)
    
    if profile == "debug_full":
        return export_debug_full(records)
    
    raise ValueError(f"Unknown export profile: {profile}")