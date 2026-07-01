from pydantic import BaseModel, Field
from typing import List, Optional
from app.agents.reflection.schemas import ReflectionOutput
from app.agents.coding.schemas import CodingOutput
from app.api.v1.schemas.test_runner import TestRunResult

class DebugInput(BaseModel):
    reflection: ReflectionOutput
    original_code: CodingOutput
    max_retries: int = 3
    final_code: Optional[CodingOutput] = None
    retries: int = 0
    success: bool = False
    test_results: Optional[TestRunResult] = None

class DebugOutput(BaseModel):
    final_code: CodingOutput
    success: bool
    retries: int
