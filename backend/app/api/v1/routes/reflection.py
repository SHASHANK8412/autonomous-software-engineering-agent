from fastapi import APIRouter, Depends, HTTPException
from app.agents.reflection.reflection_agent import get_reflection_agent, ReflectionAgent
from app.agents.reflection.schemas import ReflectionInput
from app.api.v1.schemas.reflection import ReflectionRequest, ReflectionResponse

router = APIRouter()

@router.post("/reflect", response_model=ReflectionResponse)
def reflect_on_code(request: ReflectionRequest, reflection_agent: ReflectionAgent = Depends(get_reflection_agent)):
    try:
        reflection_input = ReflectionInput(
            github_issue=request.github_issue,
            generated_code=request.generated_code,
            test_failures=request.test_failures
        )
        result = reflection_agent.run(reflection_input)
        return {"reflection": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
