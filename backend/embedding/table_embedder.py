# backend/embedding/table_embedder.py
from backend.embedding.text_embedder import TextEmbedder
import numpy as np


class TableEmbedder:
    def __init__(self, text_embedder: TextEmbedder):
        self.text_embedder = text_embedder

    def embed_table_text(self, table_text: str) -> np.ndarray:
        # Optionally: preprocess table more smartly here.
        return self.text_embedder.embed(table_text)
