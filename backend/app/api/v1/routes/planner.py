from fastapi import APIRouter, Depends, HTTPException
from app.agents.planner.planner_agent import get_planner_agent, PlannerAgent
from app.agents.planner.schemas import PlannerInput
from app.api.v1.schemas.planner import PlannerRequest, PlannerResponse

router = APIRouter()

@router.post("/plan", response_model=PlannerResponse)
def create_plan(request: PlannerRequest, planner_agent: PlannerAgent = Depends(get_planner_agent)):
    try:
        planner_input = PlannerInput(
            github_issue=request.github_issue,
            repository_summary=request.repository_summary
        )
        result = planner_agent.run(planner_input)
        return {"plan": result['plan']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
