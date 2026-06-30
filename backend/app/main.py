from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes.dashboard import router as dashboard_router
from app.api.v1.routes.workflow import router as workflow_router
from app.api.v1.routes.planner import router as planner_router
from app.api.v1.routes.repository_search import router as repository_search_router
from app.api.v1.routes.coding import router as coding_router
from app.api.v1.routes.test_runner import router as test_runner_router
from app.api.v1.routes.reflection import router as reflection_router
from app.api.v1.routes.vector_db import router as vector_db_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.db.models import init_db

app = FastAPI(title="Autonomous Software Engineering Agent")
configure_logging()
register_exception_handlers(app)

logger = get_logger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event() -> None:
    logger.info("Starting Autonomous Software Engineering Agent backend")
    init_db()

app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["dashboard"])
app.include_router(workflow_router, prefix="/api/v1/workflow", tags=["workflow"])
app.include_router(planner_router, prefix="/api/v1/planner", tags=["planner"])
app.include_router(repository_search_router, prefix="/api/v1/repository-search", tags=["repository-search"])
app.include_router(coding_router, prefix="/api/v1/coding", tags=["coding"])
app.include_router(test_runner_router, prefix="/api/v1/test-runner", tags=["test-runner"])
app.include_router(reflection_router, prefix="/api/v1/reflection", tags=["reflection"])
app.include_router(vector_db_router, prefix="/api/v1/vector-db", tags=["vector-db"])
