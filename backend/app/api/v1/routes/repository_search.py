from fastapi import APIRouter, Depends, HTTPException
from app.agents.repository_search.repository_search_agent import get_repository_search_agent, RepositorySearchAgent
from app.agents.repository_search.schemas import RepositorySearchInput
from app.api.v1.schemas.repository_search import RepositorySearchRequest, RepositorySearchResponse

router = APIRouter()

@router.post("/search", response_model=RepositorySearchResponse)
def search_repository(request: RepositorySearchRequest, search_agent: RepositorySearchAgent = Depends(get_repository_search_agent)):
    try:
        search_input = RepositorySearchInput(
            github_issue=request.github_issue,
            repository_summary=request.repository_summary
        )
        result = search_agent.run(search_input)
        return {"search_results": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
