from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from app.services.vector_db_service import VectorDBService
from app.api.v1.schemas.vector_db import StoreEmbeddingsRequest, UpdateEmbeddingsRequest, QueryRequest

router = APIRouter()

def get_vector_db_service():
    return VectorDBService()

@router.post("/collections/{collection_name}")
def create_collection(collection_name: str, vector_db_service: VectorDBService = Depends(get_vector_db_service)):
    try:
        vector_db_service.get_or_create_collection(collection_name)
        return {"message": f"Collection {collection_name} created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/collections/{collection_name}/embeddings")
def store_embeddings(collection_name: str, request: StoreEmbeddingsRequest, vector_db_service: VectorDBService = Depends(get_vector_db_service)):
    try:
        vector_db_service.store_embeddings(
            collection_name=collection_name,
            embeddings=request.embeddings,
            documents=request.documents,
            metadatas=request.metadatas,
            ids=request.ids
        )
        return {"message": "Embeddings stored successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/collections/{collection_name}/query")
def retrieve_relevant_code(collection_name: str, request: QueryRequest, vector_db_service: VectorDBService = Depends(get_vector_db_service)):
    try:
        results = vector_db_service.retrieve_relevant_code(
            collection_name=collection_name,
            query_embedding=request.query_embedding,
            n_results=request.n_results
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/collections/{collection_name}/embeddings")
def delete_repository_embeddings(collection_name: str, repository_id: str, vector_db_service: VectorDBService = Depends(get_vector_db_service)):
    try:
        vector_db_service.delete_repository_embeddings(collection_name, repository_id)
        return {"message": f"Embeddings for repository {repository_id} deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/collections/{collection_name}/embeddings")
def update_embeddings(collection_name: str, request: UpdateEmbeddingsRequest, vector_db_service: VectorDBService = Depends(get_vector_db_service)):
    try:
        vector_db_service.update_embeddings(
            collection_name=collection_name,
            embeddings=request.embeddings,
            documents=request.documents,
            metadatas=request.metadatas,
            ids=request.ids
        )
        return {"message": "Embeddings updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
