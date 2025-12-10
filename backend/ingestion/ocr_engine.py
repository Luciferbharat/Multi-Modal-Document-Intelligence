# backend/ingestion/ocr_engine.py
from typing import List, Dict
from PIL import Image
import pytesseract


def run_ocr_on_images(image_entries: List[Dict]):
    """
    Takes list from extract_images, returns list of dict:
    { "id", "page", "modality": "image", "text": "OCR text..." }
    """
    ocr_docs = []

    for entry in image_entries:
        img_path = entry["image_path"]
        try:
            img = Image.open(img_path)
            text = pytesseract.image_to_string(img)
            text = text.strip()
        except Exception:
            text = ""

        if not text:
            # Still include minimal text so image isn't completely ignored
            text = f"Image on page {entry['page']} (no clear OCR text)."

        ocr_docs.append(
            {
                "id": entry["id"],
                "page": entry["page"],
                "modality": "image",
                "text": f"Image on page {entry['page']}: {text}",
            }
        )

    return ocr_docs
