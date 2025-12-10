# backend/ingestion/extract_tables.py
from pathlib import Path
import uuid

try:
    import camelot
except ImportError:
    camelot = None


def extract_table_chunks(pdf_path: str):
    """
    Extracts tables as text blocks.
    Returns list of dicts:
    { "id": str, "page": int, "modality": "table", "text": str }
    If camelot not installed, returns [] and pipeline still works.
    """
    if camelot is None:
        return []

    tables = camelot.read_pdf(pdf_path, pages="all")
    chunks = []

    for t in tables:
        page = t.page
        df = t.df  # pandas DataFrame
        # Convert table to simple text
        table_text = "\n".join([" | ".join(row) for _, row in df.iterrows()])
        table_text = f"Table on page {page}:\n" + table_text

        chunks.append(
            {
                "id": str(uuid.uuid4()),
                "page": page,
                "modality": "table",
                "text": table_text,
            }
        )

    return chunks
