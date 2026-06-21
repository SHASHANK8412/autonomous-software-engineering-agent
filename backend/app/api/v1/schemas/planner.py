from pydantic import BaseModel
from app.agents.planner.schemas import ExecutionPlan

class PlannerRequest(BaseModel):
    github_issue: str
    repository_summary: str

class PlannerResponse(BaseModel):
    plan: ExecutionPlan
