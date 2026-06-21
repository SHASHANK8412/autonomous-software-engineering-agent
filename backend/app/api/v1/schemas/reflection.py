from pydantic import BaseModel
from app.agents.reflection.schemas import ReflectionOutput
from app.agents.coding.schemas import CodingOutput
from app.api.v1.schemas.test_runner import TestRunResult

class ReflectionRequest(BaseModel):
    github_issue: str
    generated_code: CodingOutput
    test_failures: TestRunResult

class ReflectionResponse(BaseModel):
    reflection: ReflectionOutput
