from pydantic import BaseModel, Field
from typing import List
from app.agents.coding.schemas import CodingOutput

class ReviewComment(BaseModel):
    file_path: str
    line_number: int
    comment: str
    category: str # e.g., Naming, Performance, Security, Readability


class ReviewInput(BaseModel):
    modified_code: CodingOutput
    suggestions: List[ReviewComment] = Field(default_factory=list, description="The review suggestions generated for the modified code.")

class ReviewReport(BaseModel):
    suggestions: List[ReviewComment] = Field(..., description="A list of suggestions for improvement.")
