from pydantic import BaseModel, Field
from typing import List
from app.agents.planner.schemas import ExecutionPlan
from app.agents.repository_search.schemas import RepositorySearchOutput

class ModifiedFile(BaseModel):
    file_path: str = Field(..., description="The path to the modified file.")
    original_content: str = Field(..., description="The original content of the file.")
    modified_content: str = Field(..., description="The modified content of the file.")


class CodingInput(BaseModel):
    github_issue: str
    plan: ExecutionPlan
    retrieved_code: RepositorySearchOutput
    modified_files: List[ModifiedFile] = Field(default_factory=list, description="The files modified by the coding agent.")

class CodingOutput(BaseModel):
    modified_files: List[ModifiedFile] = Field(..., description="A list of modified files.")
