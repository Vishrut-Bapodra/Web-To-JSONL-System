# Web-to-JSONL Dataset Generator

A production-oriented system that converts unstructured web pages into **clean, AI-ready JSONL datasets**, with optional chatbot Q/A generation and dataset aggregation.

This project focuses on **data quality, explainability, and realistic ML workflows**, not just scraping.

---

## What This Project Does

The system takes one or more web URLs and produces **high-quality datasets** suitable for:

- fine-tuning language models  
- Retrieval-Augmented Generation (RAG)  
- embeddings and semantic search  
- chatbot and assistant training  
- dataset curation and aggregation  

It removes boilerplate, filters low-quality text, and outputs **market-standard JSONL**.

---

## Key Features

### 1. Web → Clean Dataset
- Scrapes arbitrary web pages  
- Extracts main content using multiple strategies  
- Chunks text into usable units  
- Removes boilerplate (navigation, cookies, UI noise)  
- Outputs clean `{"text": ...}` JSONL  

### 2. Optional Chatbot Q/A Generation
- Uses pretrained models via **OpenRouter**  
- Generates Q/A pairs **only when explicitly requested**  
- Outputs a separate chat-format JSONL file  
- Designed for chatbot fine-tuning  

### 3. Dataset Appender
- Combines multiple JSONL datasets into one  
- Improved deduplication (normalized + fingerprint-based)  
- Optional dataset source tagging  
- Safe, deterministic behavior  

### 4. Clean Architecture
- Internal metadata is never exposed by default  
- Clear separation between extraction, cleaning, export, and augmentation  
- No custom model training required  

---

## Typical Use Cases

- Build domain-specific RAG knowledge bases  
- Curate datasets for LLM fine-tuning  
- Generate chatbot training data from documentation or news  
- Aggregate multiple datasets into a single corpus  
- Clean noisy web text for downstream ML tasks  

---

## Project Structure

Web-to-JSONL-System/
│

├── app.py # Streamlit UI and control layer

├── extractor.py # Web extraction orchestration

├── strategies.py # Site-specific extraction strategies

├── chunker.py # Text chunking logic

├── cleaner.py # Boilerplate & noise removal

│

├── export_profiles.py # Controls what data is exposed

├── export_writer.py # Writes user-facing JSONL

├── jsonl_writer.py # Internal schema-enforced writer

│

├── qa_generator.py # Optional Q/A generation (OpenRouter)

├── dataset_appender.py # Append & deduplicate datasets

│

├── requirements.txt

├── .env

└── README.md


---

## How the Pipeline Works

Web URLs

↓

Extraction (HTML parsing, strategies)

↓

Chunking (semantic text units)

↓

Cleaning (remove boilerplate & noise)

↓

Export Profiling (select output format)

↓

JSONL Dataset

↓

(Optional) Q/A Generation


---

## Output Formats

### Default Dataset (`dataset.jsonl`)
```json
{"text": "Clean extracted content..."}
Optional Chatbot Dataset (chatbot_dataset.jsonl)
{
  "messages": [
    {"role": "user", "content": "What is Python used for?"},
    {"role": "assistant", "content": "Python is used for web development, data analysis, automation, and more."}
  ]
}
Combined Dataset (Appender)
{"text": "...", "dataset_source": "news.jsonl"}
Installation
pip install -r requirements.txt
Create a .env file:

OPENROUTER_API_KEY=your_api_key_here
Running the App
streamlit run app.py
