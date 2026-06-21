from pydantic import BaseModel, Field
from typing import List
from app.agents.coding.schemas import CodingOutput

class ReviewInput(BaseModel):
    modified_code: CodingOutput

class ReviewComment(BaseModel):
    file_path: str
    line_number: int
    comment: str
    category: str # e.g., Naming, Performance, Security, Readability

class ReviewReport(BaseModel):
    suggestions: List[ReviewComment] = Field(..., description="A list of suggestions for improvement.")
