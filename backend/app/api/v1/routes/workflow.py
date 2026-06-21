from fastapi import APIRouter, Depends, HTTPException
from app.workflow.graph import create_main_workflow
from app.workflow.state import WorkflowState
from pydantic import BaseModel

router = APIRouter()

class WorkflowRequest(BaseModel):
    github_issue: str
    repository_summary: str

@router.post("/run-workflow")
async def run_workflow(request: WorkflowRequest):
    try:
        workflow = create_main_workflow()
        initial_state = {
            "github_issue": request.github_issue,
            "repository_summary": request.repository_summary,
            "debug_retries": 0,
        }
        
        # In a real application, you would run this asynchronously
        # and provide a way to check the status.
        final_state = workflow.invoke(initial_state)
        
        return final_state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
