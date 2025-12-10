# backend/ingestion/extract_images.py
from pathlib import Path
import fitz  # pymupdf
import uuid


def extract_image_entries(pdf_path: str, images_dir: str):
    """
    Extract images from each page, save as PNG under images_dir.
    Returns list of dicts:
    { "id": str, "page": int, "modality": "image", "image_path": str }
    """
    pdf = fitz.open(pdf_path)
    images_dir_path = Path(images_dir)
    images_dir_path.mkdir(parents=True, exist_ok=True)

    entries = []

    for page_num in range(len(pdf)):
        page = pdf[page_num]
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = pdf.extract_image(xref)
            img_bytes = base_image["image"]
            ext = base_image["ext"]

            file_name = f"page_{page_num+1}_img_{img_index+1}.{ext}"
            file_path = images_dir_path / file_name
            with open(file_path, "wb") as f:
                f.write(img_bytes)

            entries.append(
                {
                    "id": str(uuid.uuid4()),
                    "page": page_num + 1,
                    "modality": "image",
                    "image_path": str(file_path),
                }
            )

    pdf.close()
    return entries
