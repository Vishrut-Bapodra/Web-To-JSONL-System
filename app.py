import streamlit as st
import tempfile
from pathlib import Path

from extractor import extract_urls
from cleaner import clean_records as clean_pipeline_records
from export_profiles import apply_export_profile
from export_writer import write_export_jsonl
from qa_generator import generate_qa_dataset, write_qa_jsonl
from dataset_appender import append_jsonl_datasets


# ==================================================
# Page Configuration
# ==================================================

st.set_page_config(
    page_title="Web → JSONL Dataset Generator",
    layout="centered"
)

st.title("Web → JSONL Dataset Generator")
st.caption(
    "Extract clean, AI-ready datasets from web pages. "
    "Append multiple datasets and optionally generate chatbot training data."
)


# ==================================================
# SECTION 1 — Web Extraction
# ==================================================

st.header("1. Web Extraction")

urls_input = st.text_area(
    "Enter one or more URLs (one per line):",
    height=160,
    placeholder=(
        "https://en.wikipedia.org/wiki/Artificial_intelligence\n"
        "https://docs.python.org/3/tutorial/introduction.html"
    ),
)

generate_qa = st.checkbox(
    "Generate chatbot training data (Q/A JSONL)",
    help="Uses a pretrained OpenRouter model to generate one Q/A per cleaned text chunk."
)

urls = [u.strip() for u in urls_input.splitlines() if u.strip()]

if st.button("Extract Web Data"):
    if not urls:
        st.warning("Please enter at least one URL.")
        st.stop()

    with st.spinner("Extracting content from web pages..."):
        internal_records = extract_urls(urls)

    if not internal_records:
        st.error("No content could be extracted.")
        st.stop()

    with st.spinner("Cleaning extracted content..."):
        cleaned_internal_records = clean_pipeline_records(internal_records)

    if not cleaned_internal_records:
        st.error("All extracted content was filtered out during cleaning.")
        st.stop()

    clean_export_records = apply_export_profile(
        cleaned_internal_records,
        profile="training_minimal"
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl") as tmp:
        dataset_path = Path(tmp.name)

    write_export_jsonl(clean_export_records, dataset_path)

    st.success(f"Dataset generated. Records: {len(clean_export_records)}")

    with open(dataset_path, "rb") as f:
        st.download_button(
            "Download dataset.jsonl",
            data=f,
            file_name="dataset.jsonl",
            mime="application/json",
        )

    if generate_qa:
        with st.spinner("Generating chatbot Q/A dataset..."):
            qa_records = generate_qa_dataset(clean_export_records)

        if qa_records:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl") as tmp:
                qa_path = Path(tmp.name)

            write_qa_jsonl(qa_records, qa_path)

            st.success(f"Chatbot dataset generated. Q/A pairs: {len(qa_records)}")

            with open(qa_path, "rb") as f:
                st.download_button(
                    "Download chatbot_dataset.jsonl",
                    data=f,
                    file_name="chatbot_dataset.jsonl",
                    mime="application/json",
                )
        else:
            st.warning("Q/A dataset could not be generated.")

    st.subheader("Sample Cleaned Text")
    st.json(clean_export_records[:2])


# ==================================================
# SECTION 2 — Dataset Appender
# ==================================================

st.divider()
st.header("2. Dataset Appender")

st.caption(
    "Upload multiple JSONL datasets (same schema) and append them into a single dataset."
)

uploaded_files = st.file_uploader(
    "Upload JSONL files",
    type=["jsonl"],
    accept_multiple_files=True
)

deduplicate = st.checkbox(
    "Remove duplicate records (recommended)",
    value=True
)

add_dataset_source = st.checkbox(
    "Add dataset_source field (file name)",
    value=False
)

if st.button("Append Datasets"):
    if not uploaded_files or len(uploaded_files) < 2:
        st.warning("Please upload at least two JSONL files.")
        st.stop()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl") as tmp:
        output_path = Path(tmp.name)

    temp_input_paths = []

    for file in uploaded_files:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl")
        temp_file.write(file.read())
        temp_file.close()
        temp_input_paths.append(Path(temp_file.name))

    with st.spinner("Appending datasets..."):
        stats = append_jsonl_datasets(
            input_files=temp_input_paths,
            output_file=output_path,
            deduplicate=deduplicate,
            add_dataset_source=add_dataset_source,
        )

    st.success("Datasets appended successfully.")

    st.json(stats)

    with open(output_path, "rb") as f:
        st.download_button(
            "Download combined_dataset.jsonl",
            data=f,
            file_name="combined_dataset.jsonl",
            mime="application/json",
        )
