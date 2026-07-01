"""Vector database service with a local in-memory fallback.

The application prefers ChromaDB when it is available, but repository search
should not fail outright if the database service is offline during local
development.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List

try:
    import chromadb
    from chromadb.utils import embedding_functions
except Exception:  # pragma: no cover - optional dependency path
    chromadb = None
    embedding_functions = None


class VectorDBService:
    def __init__(self, host: str = "localhost", port: str = "8000"):
        self.client = None
        self.embedding_function = None
        self._collections: dict[str, list[dict[str, Any]]] = {}

        if chromadb is not None:
            try:
                self.client = chromadb.HttpClient(host=host, port=port)
                self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
            except Exception:
                self.client = None
                self.embedding_function = None

    def get_or_create_collection(self, collection_name):
        """Get or create a collection."""
        if self.client is not None:
            return self.client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
            )

        self._collections.setdefault(collection_name, [])
        return collection_name

    def store_embeddings(self, collection_name, embeddings, documents, metadatas, ids):
        """Store embeddings in the specified collection."""
        collection = self.get_or_create_collection(collection_name)
        if self.client is not None:
            collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )
            return

        stored_items = self._collections.setdefault(collection, [])
        for index, item_id in enumerate(ids):
            stored_items.append(
                {
                    "id": item_id,
                    "embedding": embeddings[index],
                    "document": documents[index],
                    "metadata": metadatas[index],
                }
            )

    def retrieve_relevant_code(self, collection_name, query_embedding, n_results=5):
        """Retrieve relevant code from the specified collection."""
        collection = self.get_or_create_collection(collection_name)
        if self.client is not None:
            return collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
            )

        items = self._collections.get(collection, [])
        ranked_items = sorted(
            items,
            key=lambda item: self._distance(query_embedding, item["embedding"]),
        )[:n_results]

        return {
            "documents": [[item["document"] for item in ranked_items]],
            "metadatas": [[item["metadata"] for item in ranked_items]],
            "distances": [[self._distance(query_embedding, item["embedding"]) for item in ranked_items]],
            "ids": [[item["id"] for item in ranked_items]],
        }

    def delete_repository_embeddings(self, collection_name, repository_id):
        """Delete all embeddings for a given repository."""
        collection = self.get_or_create_collection(collection_name)
        if self.client is not None:
            collection.delete(where={"repository_id": repository_id})
            return

        items = self._collections.get(collection, [])
        self._collections[collection] = [item for item in items if item["metadata"].get("repository_id") != repository_id]

    def update_embeddings(self, collection_name, embeddings, documents, metadatas, ids):
        """Update embeddings in the specified collection."""
        collection = self.get_or_create_collection(collection_name)
        if self.client is not None:
            collection.update(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )
            return

        self._collections[collection] = []
        self.store_embeddings(collection, embeddings, documents, metadatas, ids)

    def _distance(self, left: List[float], right: List[float]) -> float:
        """Compute a small cosine distance for the in-memory fallback."""

        numerator = sum(l_value * r_value for l_value, r_value in zip(left, right))
        left_norm = math.sqrt(sum(value * value for value in left))
        right_norm = math.sqrt(sum(value * value for value in right))
        if not left_norm or not right_norm:
            return 1.0
        similarity = numerator / (left_norm * right_norm)
        return 1.0 - similarity
