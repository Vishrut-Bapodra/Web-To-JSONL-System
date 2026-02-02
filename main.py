import argparse
from pathlib import Path
from extractor import extract_urls
from jsonl_writer import write_jsonl


#----------------------------
# CLI Argument Parsing
#----------------------------

def parse_arg():
    parser = argparse.ArgumentParser(
        description="Web-to-JSONL Dataset Generator"
    )

    parser.add_argument(
        "--urls",
        nargs="+",
        required=True,
        help="One or more URLs to extract data from"
    )

    parser.add_argument(
        "--output",
        default="output.jsonl",
        help="Path to output JSONL file (default: output.jsonl)"
    )

    return parser.parse_args()


#----------------------------
# Main Execution
#----------------------------

def main():
    args = parse_arg()

    urls = args.urls
    output_path = Path(args.output)

    print("Starting extraction...")
    print(f"URLs: {len(urls)}")

    records = extract_urls(urls)

    if not records:
        print("No records produced. Exiting.")
        return
    
    write_jsonl(records, output_path)

    print(f"Extraction complete.")
    print(f"Total JSONL records written: {len(records)}")
    print(f"Output file: {output_path.resolve()}")

if __name__ == "__main__":
    main()