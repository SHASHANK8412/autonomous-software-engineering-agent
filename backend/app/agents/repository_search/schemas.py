from pydantic import BaseModel, Field
from typing import List
from app.agents.planner.schemas import PlannerInput

class SearchResult(BaseModel):
    file_path: str = Field(..., description="The path to the relevant file.")
    confidence_score: float = Field(..., description="The confidence score of the relevance of the file.")
    code_snippet: str = Field(..., description="A snippet of the relevant code.")

class RepositorySearchInput(PlannerInput):
    relevant_files: List[SearchResult] = Field(default_factory=list, description="Relevant files discovered during repository search.")

class RepositorySearchOutput(BaseModel):
    relevant_files: List[SearchResult] = Field(..., description="A list of relevant files found in the repository.")
