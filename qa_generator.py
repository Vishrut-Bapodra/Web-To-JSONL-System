import os, json, requests, time, random
from typing import List, Dict
from dotenv import load_dotenv
load_dotenv()



# ==================================================
# OpenRouter Configuration
# ==================================================

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

DEFAULT_MODEL = "mistralai/mistral-7b-instruct:free"


# ==================================================
# Prompt Template
# ==================================================

SYSTEM_PROMPT = (
    "You are a data annotator.\n"
    "Given a piece of text, generate exactly ONE question and ONE answer.\n"
    "Respond ONLY in valid JSON in this exact format:\n\n"
    "{\n"
    '  "question": "...",\n'
    '  "answer": "..."\n'
    "}\n\n"
    "Do not include any extra text."
)



# ==================================================
# Core Q/A Generation
# ==================================================

def generate_qa_for_text(
    text: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.2,
):
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY environment variable is not set")

    payload = {
        "model": model,
        "temperature": temperature,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"TEXT:\n{text}\n\nGenerate the JSON now.",
            },
        ],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost",
        "X-Title": "Web-to-JSONL-System",
    }

    response = requests.post(
        OPENROUTER_API_URL,
        headers=headers,
        json=payload,
        timeout=30,
    )

    response.raise_for_status()
    data = response.json()

    raw_content = data["choices"][0]["message"]["content"].strip()

    try:
        qa = json.loads(raw_content)
        question = qa.get("question")
        answer = qa.get("answer")
    except Exception:
        raise ValueError("Model did not return valid JSON")

    if not question or not answer:
        raise ValueError("Model returned empty question or answer")

    return {
        "messages": [
            {"role": "user", "content": question.strip()},
            {"role": "assistant", "content": answer.strip()},
        ]
    }

# ==================================================
# Batch Q/A Generation
# ==================================================

def generate_qa_dataset(
    records: List[Dict],
    max_items: int = 10,   # LOWER THIS for free tier
) -> List[Dict]:

    qa_records = []

    for i, r in enumerate(records):
        if i >= max_items:
            break

        text = r.get("text")
        if not text or len(text) < 80:
            continue

        try:
            qa = generate_qa_for_text(text)
            qa_records.append(qa)

            # polite delay to avoid 429
            time.sleep(random.uniform(1.5, 2.5))

        except Exception as e:
            print("Q/A generation failed:", e)
            continue

    return qa_records

# ==================================================
# JSONL Writer (Chat Format)
# ==================================================

def write_qa_jsonl(qa_records: List[Dict], output_path: str) -> None:

    if not qa_records:
        raise ValueError("No Q/A records to write")
    with open(output_path, "w", encoding="utf-8") as f:
        for record in qa_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")