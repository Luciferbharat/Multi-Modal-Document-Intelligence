# backend/retrieval/retriever.py
from pathlib import Path
import json
from typing import List, Dict

import numpy as np
import faiss

from backend.embedding.text_embedder import TextEmbedder


class Retriever:
    def __init__(self, vector_dir: Path):
        self.vector_dir = Path(vector_dir)
        self.index_path = self.vector_dir / "index.faiss"
        self.emb_path = self.vector_dir / "embeddings.npy"
        self.docs_path = self.vector_dir / "docs.json"

        self.text_embedder = TextEmbedder()
        self.index = None
        self.docs = None

    def index_exists(self) -> bool:
        return self.index_path.exists() and self.docs_path.exists()

    def _load_index_and_docs(self):
        if self.index is None:
            if not self.index_exists():
                raise RuntimeError("Index files not found.")

            embeddings = np.load(self.emb_path)
            dim = embeddings.shape[1]
            index = faiss.IndexFlatIP(dim)  # cosine if embeddings are normalized
            index.add(embeddings)
            self.index = index

        if self.docs is None:
            with open(self.docs_path, "r", encoding="utf-8") as f:
                self.docs = json.load(f)

    def build_and_save_index(self, docs: List[Dict], embeddings: List[np.ndarray]):
        self.vector_dir.mkdir(parents=True, exist_ok=True)

        embs = np.vstack(embeddings).astype("float32")
        dim = embs.shape[1]

        index = faiss.IndexFlatIP(dim)
        index.add(embs)

        faiss.write_index(index, str(self.index_path))
        np.save(self.emb_path, embs)

        with open(self.docs_path, "w", encoding="utf-8") as f:
            json.dump(docs, f, ensure_ascii=False, indent=2)

        self.index = index
        self.docs = docs

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        self._load_index_and_docs()

        q_emb = self.text_embedder.embed(query)
        q_emb = q_emb.reshape(1, -1)

        scores, idxs = self.index.search(q_emb, top_k)
        idxs = idxs[0]
        scores = scores[0]

        results = []
        for i, score in zip(idxs, scores):
            if i < 0 or i >= len(self.docs):
                continue
            doc = self.docs[i]
            results.append(
                {
                    "text": doc["text"],
                    "page": doc["page"],
                    "modality": doc["modality"],
                    "score": float(score),
                }
            )
        return results
