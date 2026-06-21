from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class StoreEmbeddingsRequest(BaseModel):
    embeddings: List[List[float]]
    documents: List[str]
    metadatas: List[Dict[str, Any]]
    ids: List[str]

class UpdateEmbeddingsRequest(BaseModel):
    embeddings: List[List[float]]
    documents: List[str]
    metadatas: List[Dict[str, Any]]
    ids: List[str]

class QueryRequest(BaseModel):
    query_embedding: List[float]
    n_results: int = 5
