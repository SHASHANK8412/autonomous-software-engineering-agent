from langgraph.graph import StateGraph, END
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.services.gemini_service import get_gemini_service
from app.services.vector_db_service import VectorDBService

from .schemas import RepositorySearchInput, RepositorySearchOutput
from .prompts import REPOSITORY_SEARCH_PROMPT

class RepositorySearchAgent:
    def __init__(self, llm, vector_db_service: VectorDBService):
        self.llm = llm
        self.vector_db_service = vector_db_service
        self.prompt_template = PromptTemplate(
            template=REPOSITORY_SEARCH_PROMPT,
            input_variables=["planner_request"],
        )
        self.output_parser = JsonOutputParser(pydantic_object=RepositorySearchOutput)

    def _create_graph(self):
        graph = StateGraph(RepositorySearchInput)
        graph.add_node("repository_search", self._repository_search_node)
        graph.set_entry_point("repository_search")
        graph.add_edge("repository_search", END)
        return graph.compile()

    def _repository_search_node(self, state: RepositorySearchInput):
        # Use the Gemini service to create an embedding for the issue.
        gemini_service = get_gemini_service()
        query_embedding = gemini_service.generate_content(f"Generate an embedding for this issue: {state.github_issue}")
        
        # This is a simplified embedding generation. In a real scenario, you would use a proper embedding model.
        # For demonstration, we'll use a fixed-size vector of zeros.
        # In a real implementation, the embedding from the Gemini service would be a list of floats.
        # query_embedding_vector = [0.0] * 768 # Example size
        
        # For the purpose of this example, we'll use the text as a stand-in for the embedding vector
        # as the chromadb client can handle this.
        
        # Search ChromaDB
        search_results = self.vector_db_service.retrieve_relevant_code(
            collection_name="repository_embeddings", # Assuming a collection name
            query_embedding=query_embedding, # This would be the actual embedding vector
            n_results=5
        )

        # Format the results
        relevant_files = []
        if search_results and search_results.get("documents"):
            for i, doc in enumerate(search_results["documents"][0]):
                relevant_files.append({
                    "file_path": search_results["metadatas"][0][i].get("file_path", "Unknown"),
                    "confidence_score": 1 - search_results["distances"][0][i], # Convert distance to score
                    "code_snippet": doc
                })

        return {"relevant_files": relevant_files}

    def run(self, search_input: RepositorySearchInput):
        graph = self._create_graph()
        return graph.invoke(search_input)

def get_repository_search_agent():
    gemini_service = get_gemini_service()
    vector_db_service = VectorDBService()
    return RepositorySearchAgent(gemini_service.model, vector_db_service)
