# backend/embedding/text_embedder.py
import os
from sentence_transformers import SentenceTransformer
import numpy as np


class TextEmbedder:
    def __init__(self):
        model_name = os.getenv(
            "TEXT_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.model = SentenceTransformer(model_name)

    def embed(self, text: str) -> np.ndarray:
        if not text or not text.strip():
            text = "empty text"
        vec = self.model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return vec.astype("float32")
