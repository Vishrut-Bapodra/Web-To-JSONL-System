from typing import List, Dict
import re


#---------------------------
# Chunking Defaults (SANE)
#---------------------------

DEFAULT_MAX_CHARS = 1200
DEFAULT_MIN_CHARS = 200
DEFAULT_OVERLAP = 100

#---------------------------
# Text Normalization
#---------------------------

def normalize_text(text: str) -> str:

    if not text:
        return ""
    
    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


#---------------------------
# Core Chunking Logic
#---------------------------

def chunk_text(text: str, max_chars: int = DEFAULT_MAX_CHARS, min_chars: int = DEFAULT_MIN_CHARS, overlap: int = DEFAULT_OVERLAP) -> List[str]:

    text = normalize_text(text)
    if len(text) < min_chars:
        return[]
    
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + max_chars, text_length)
        chunk = text[start:end].strip()

        if len(chunk) >= min_chars:
            chunks.append(chunk)

        if end == text_length:
            break

        start = end - overlap
    
    return chunks


#---------------------------
# Chunk Record Builder
#---------------------------

def build_chunk_records(text: str, source_url: str, site_type: str, extraction_strategy: str, base_confidence: float) -> List[Dict]:

    chunks = chunk_text(text)
    records = []

    for chunk in chunks:
        records.append({
            "text": chunk,
            "source_url": source_url,
            "site_type": site_type,
            "extraction_strategy": extraction_strategy,
            "confidence": round(base_confidence, 2)
        })

    return records