from fastapi import APIRouter, Depends, HTTPException
from app.agents.coding.coding_agent import get_coding_agent, CodingAgent
from app.agents.coding.schemas import CodingInput
from app.api.v1.schemas.coding import CodingRequest, CodingResponse

router = APIRouter()

@router.post("/code", response_model=CodingResponse)
def generate_code(request: CodingRequest, coding_agent: CodingAgent = Depends(get_coding_agent)):
    try:
        coding_input = CodingInput(
            github_issue=request.github_issue,
            plan=request.plan,
            retrieved_code=request.retrieved_code
        )
        result = coding_agent.run(coding_input)
        return {"coding_results": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
