from pydantic import BaseModel, Field
from typing import Any, Dict

class TestRunResult(BaseModel):
    stdout: str
    stderr: str
    report: Dict[str, Any]

class TestRunnerRequest(BaseModel):
    test_path: str = Field(".", description="The path to run tests on.")

class TestRunnerResponse(BaseModel):
    results: TestRunResult
