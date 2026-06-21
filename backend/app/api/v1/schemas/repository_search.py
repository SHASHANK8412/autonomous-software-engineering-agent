from pydantic import BaseModel
from app.agents.repository_search.schemas import RepositorySearchOutput

class RepositorySearchRequest(BaseModel):
    github_issue: str
    repository_summary: str

class RepositorySearchResponse(BaseModel):
    search_results: RepositorySearchOutput
