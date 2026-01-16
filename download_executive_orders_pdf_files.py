import os
import csv
import requests
from urllib.parse import urlparse

# https://www.federalregister.gov/presidential-documents/executive-orders
# -------- CONFIG --------
CSV_FILE = "documents_signed_from_01_20_2025_to_01_11_2026_signed_by_donald_trump_of_type_presidential_document_and_of_presidential_document_type_executive_order.csv"          # path to your CSV file
PDF_COLUMN = "pdf_url"          # column name containing PDF URLs
OUTPUT_DIR = "data"             # directory to save PDFs
TIMEOUT = 30                    # seconds
# ------------------------

def ensure_directory(path: str):
    """Create directory if it does not exist."""
    os.makedirs(path, exist_ok=True)

def get_filename_from_url(url: str, index: int) -> str:
    """Extract filename from URL or generate one."""
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path)
    if not filename.lower().endswith(".pdf"):
        filename = f"document_{index}.pdf"
    return filename

def download_pdf(url: str, output_path: str):
    """Download a single PDF."""
    response = requests.get(url, stream=True, timeout=TIMEOUT)
    response.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

def main():
    ensure_directory(OUTPUT_DIR)

    with open(CSV_FILE, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        if PDF_COLUMN not in reader.fieldnames:
            raise ValueError(f"Column '{PDF_COLUMN}' not found in CSV.")

        for index, row in enumerate(reader, start=1):
            url = row.get(PDF_COLUMN)

            if not url:
                print(f"[SKIP] Row {index}: Empty URL")
                continue

            try:
                filename = get_filename_from_url(url, index)
                output_path = os.path.join(OUTPUT_DIR, filename)

                print(f"[DOWNLOADING] {url}")
                download_pdf(url, output_path)
                print(f"[SAVED] {output_path}")

            except Exception as e:
                print(f"[ERROR] Row {index}: {e}")

if __name__ == "__main__":
    main()

# python download_executive_orders_pdf_files.py