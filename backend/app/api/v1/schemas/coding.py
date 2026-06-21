from pydantic import BaseModel
from app.agents.coding.schemas import CodingOutput
from app.agents.planner.schemas import ExecutionPlan
from app.agents.repository_search.schemas import RepositorySearchOutput

class CodingRequest(BaseModel):
    github_issue: str
    plan: ExecutionPlan
    retrieved_code: RepositorySearchOutput

class CodingResponse(BaseModel):
    coding_results: CodingOutput
