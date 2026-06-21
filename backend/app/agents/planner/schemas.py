from pydantic import BaseModel, Field
from typing import List

class PlanStep(BaseModel):
    step: str = Field(..., description="A single step in the execution plan.")
    reason: str = Field(..., description="The reason for this step.")
    priority: int = Field(..., description="The priority of this step.")
    files_involved: List[str] = Field(..., description="A list of files involved in this step.")

class ExecutionPlan(BaseModel):
    plan: List[PlanStep] = Field(..., description="The ordered execution plan.")

class PlannerInput(BaseModel):
    github_issue: str
    repository_summary: str
