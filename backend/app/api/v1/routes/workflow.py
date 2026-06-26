from fastapi import APIRouter, Depends, HTTPException
from app.services.workflow_runner_service import get_workflow_runner_service, WorkflowRunnerService
from pydantic import BaseModel

router = APIRouter()

class WorkflowRequest(BaseModel):
    github_issue: str
    repository_summary: str

@router.post("/run-workflow")
async def run_workflow(request: WorkflowRequest, workflow_runner: WorkflowRunnerService = Depends(get_workflow_runner_service)):
    try:
        return workflow_runner.start_workflow(request.github_issue, request.repository_summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
