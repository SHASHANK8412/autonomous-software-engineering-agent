import chromadb
from chromadb.utils import embedding_functions

class VectorDBService:
    def __init__(self, host="localhost", port="8000"):
        self.client = chromadb.HttpClient(host=host, port=port)
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()

    def get_or_create_collection(self, collection_name):
        """Get or create a collection."""
        return self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function
        )

    def store_embeddings(self, collection_name, embeddings, documents, metadatas, ids):
        """Store embeddings in the specified collection."""
        collection = self.get_or_create_collection(collection_name)
        collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def retrieve_relevant_code(self, collection_name, query_embedding, n_results=5):
        """Retrieve relevant code from the specified collection."""
        collection = self.get_or_create_collection(collection_name)
        return collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

    def delete_repository_embeddings(self, collection_name, repository_id):
        """Delete all embeddings for a given repository."""
        collection = self.get_or_create_collection(collection_name)
        # This is a simple way to delete by repository_id.
        # A more robust implementation might require querying for all ids with the repository_id metadata.
        collection.delete(where={"repository_id": repository_id})

    def update_embeddings(self, collection_name, embeddings, documents, metadatas, ids):
        """Update embeddings in the specified collection."""
        collection = self.get_or_create_collection(collection_name)
        collection.update(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
