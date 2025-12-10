# backend/embedding/image_embedder.py
from backend.embedding.text_embedder import TextEmbedder
import numpy as np


class ImageEmbedder:
    def __init__(self, text_embedder: TextEmbedder):
        self.text_embedder = text_embedder

    def embed_ocr_text(self, ocr_text: str) -> np.ndarray:
        # Could prepend "Image: ..." to make distribution different.
        text = "Image content: " + (ocr_text or "")
        return self.text_embedder.embed(text)
