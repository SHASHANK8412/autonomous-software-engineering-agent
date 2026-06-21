from pydantic import BaseModel, Field
from typing import List
from app.agents.reflection.schemas import ReflectionOutput
from app.agents.coding.schemas import CodingOutput

class DebugInput(BaseModel):
    reflection: ReflectionOutput
    original_code: CodingOutput
    max_retries: int = 3

class DebugOutput(BaseModel):
    final_code: CodingOutput
    success: bool
    retries: int
