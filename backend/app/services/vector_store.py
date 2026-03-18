import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class VectorStore:
    def __init__(self, storage_dir: str | Path | None = None):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.metadata = []
        self.storage_dir = Path(storage_dir) if storage_dir else None

        if self.storage_dir:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            self._load()

    def build(self, texts: list, metadata: list):
        if not texts:
            self.index = None
            self.metadata = []
            self._save()
            return

        embeddings = self.model.encode(texts, convert_to_numpy=True)
        dim = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        self.metadata = metadata
        self._save()

    def upsert_by_key(self, key: str, text: str, metadata: dict):
        existing_index = next(
            (
                idx
                for idx, item in enumerate(self.metadata)
                if item.get("doc_key") == key
            ),
            None,
        )

        payload = {**metadata, "doc_key": key, "text": text}

        if existing_index is None:
            self.metadata.append(payload)
        else:
            self.metadata[existing_index] = payload

        texts = [item.get("text", "") for item in self.metadata if item.get("text", "").strip()]
        rebuilt_metadata = [item for item in self.metadata if item.get("text", "").strip()]
        self.build(texts, rebuilt_metadata)

    def search(self, query: str, k: int = 3, filters: dict | None = None):
        if not self.metadata:
            return []

        filters = filters or {}

        if filters:
            candidates = [
                item
                for item in self.metadata
                if all(item.get(f_key) == f_val for f_key, f_val in filters.items())
            ]
            if not candidates:
                return []

            texts = [item.get("text", "") for item in candidates]
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            q_vec = self.model.encode([query], convert_to_numpy=True)[0]

            emb_norms = np.linalg.norm(embeddings, axis=1) + 1e-12
            q_norm = np.linalg.norm(q_vec) + 1e-12
            scores = np.dot(embeddings, q_vec) / (emb_norms * q_norm)

            top_indices = np.argsort(scores)[::-1][:k]
            return [candidates[i] for i in top_indices]

        if not self.index:
            return []

        q_vec = self.model.encode([query], convert_to_numpy=True)
        _, indices = self.index.search(q_vec, k)
        results = []
        for i in indices[0]:
            if i < len(self.metadata):
                results.append(self.metadata[i])

        return results

    def _paths(self) -> tuple[Path, Path] | tuple[None, None]:
        if not self.storage_dir:
            return None, None

        index_path = self.storage_dir / "index.faiss"
        metadata_path = self.storage_dir / "metadata.json"
        return index_path, metadata_path

    def _save(self):
        index_path, metadata_path = self._paths()
        if not index_path or not metadata_path:
            return

        if self.index:
            faiss.write_index(self.index, str(index_path))
        elif index_path.exists():
            index_path.unlink()

        metadata_path.write_text(json.dumps(self.metadata, indent=2), encoding="utf-8")

    def _load(self):
        index_path, metadata_path = self._paths()
        if not index_path or not metadata_path:
            return

        if metadata_path.exists():
            self.metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if index_path.exists():
            self.index = faiss.read_index(str(index_path))
