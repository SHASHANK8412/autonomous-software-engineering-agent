from pydantic import BaseModel, Field
from typing import List, Optional
from app.agents.coding.schemas import CodingOutput
from app.api.v1.schemas.test_runner import TestRunResult

class ReflectionOutput(BaseModel):
    root_cause: str = Field(..., description="The root cause of the test failures.")
    fix_recommendation: str = Field(..., description="A recommendation on how to fix the issue.")
    confidence_score: float = Field(..., description="The confidence score in the fix recommendation.")


class ReflectionInput(BaseModel):
    github_issue: str
    generated_code: CodingOutput
    test_failures: TestRunResult
    reflection: Optional[ReflectionOutput] = None
