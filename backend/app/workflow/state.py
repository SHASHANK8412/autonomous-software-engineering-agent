from typing import TypedDict, List, Optional
from app.agents.planner.schemas import ExecutionPlan
from app.agents.repository_search.schemas import RepositorySearchOutput
from app.agents.coding.schemas import CodingOutput
from app.agents.reflection.schemas import ReflectionOutput
from app.api.v1.schemas.test_runner import TestRunResult

class WorkflowState(TypedDict):
    github_issue: str
    repository_summary: str
    plan: Optional[ExecutionPlan]
    retrieved_code: Optional[RepositorySearchOutput]
    generated_code: Optional[CodingOutput]
    test_results: Optional[TestRunResult]
    reflection: Optional[ReflectionOutput]
    debug_retries: int
    final_code: Optional[CodingOutput]
    review_report: Optional[dict]
    error: Optional[str]
