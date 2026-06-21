from fastapi import APIRouter, Depends, HTTPException
from app.services.test_runner_service import get_test_runner_service, TestRunnerService
from app.api.v1.schemas.test_runner import TestRunnerRequest, TestRunnerResponse

router = APIRouter()

@router.post("/run-tests", response_model=TestRunnerResponse)
def run_tests(request: TestRunnerRequest, test_runner: TestRunnerService = Depends(get_test_runner_service)):
    try:
        results = test_runner.run_tests(request.test_path)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
