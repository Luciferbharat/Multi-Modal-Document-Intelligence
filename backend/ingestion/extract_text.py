# backend/ingestion/extract_text.py
from pathlib import Path
import fitz  # pymupdf
import uuid

def _chunk_text(text: str, chunk_size: int = 800, overlap: int = 100):
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def extract_text_chunks(pdf_path: str):
    """
    Returns list of dicts:
    { "id": str, "page": int, "modality": "text", "text": str }
    """
    pdf = fitz.open(pdf_path)
    all_chunks = []

    for page_num in range(len(pdf)):
        page = pdf[page_num]
        text = page.get_text()
        if not text.strip():
            continue

        chunks = _chunk_text(text)
        for ch in chunks:
            all_chunks.append(
                {
                    "id": str(uuid.uuid4()),
                    "page": page_num + 1,   # 1-based for human readable
                    "modality": "text",
                    "text": ch,
                }
            )

    pdf.close()
    return all_chunks
