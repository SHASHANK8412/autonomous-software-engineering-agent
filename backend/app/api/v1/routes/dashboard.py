import asyncio

from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect

from app.api.v1.schemas.dashboard import (
    CurrentAgentResponse,
    DashboardLogItem,
    HistoryItem,
    IssueItem,
    RepositorySummaryResponse,
    WorkflowStartRequest,
    WorkflowStartResponse,
    WorkflowStatusResponse,
)
from app.core.config import settings
from app.db.models import DBSessionLocal, Issue, Log, UserHistory
from app.services.redis_service import get_redis_service
from app.services.workflow_event_service import get_workflow_event_service
from app.services.workflow_runner_service import get_workflow_runner_service

router = APIRouter()
redis_service = get_redis_service()
workflow_events = get_workflow_event_service()
workflow_runner = get_workflow_runner_service()


@router.get("/workflow-status", response_model=WorkflowStatusResponse)
def workflow_status():
    snapshot = workflow_events.snapshot()
    return {
        "workflow_id": snapshot.get("workflow_id"),
        "status": snapshot.get("status", "idle"),
        "current_agent": snapshot.get("current_agent"),
        "progress": snapshot.get("progress", 0),
        "last_message": snapshot.get("last_message"),
        "updated_at": snapshot.get("updated_at"),
    }


@router.get("/current-agent", response_model=CurrentAgentResponse)
def current_agent():
    snapshot = workflow_events.snapshot()
    return {
        "current_agent": snapshot.get("current_agent"),
        "progress": snapshot.get("progress", 0),
        "status": snapshot.get("status", "idle"),
    }


@router.get("/logs", response_model=list[DashboardLogItem])
def logs(limit: int = Query(default=settings.dashboard_log_limit, ge=1, le=500)):
    session = DBSessionLocal()
    try:
        entries = session.query(Log).order_by(Log.created_at.desc()).limit(limit).all()
        return [
            {"message": entry.message, "level": entry.level, "created_at": entry.created_at.isoformat() if entry.created_at else None}
            for entry in entries
        ]
    finally:
        session.close()


@router.get("/repository-summary", response_model=RepositorySummaryResponse)
def repository_summary():
    cached = redis_service.get("dashboard:repository_summary")
    if cached:
        return {"repository_summary": cached, "source": "cache"}
    snapshot = workflow_events.snapshot()
    return {"repository_summary": snapshot.get("repository_summary"), "source": "memory"}


@router.get("/issues", response_model=list[IssueItem])
def issues(limit: int = Query(default=50, ge=1, le=500)):
    session = DBSessionLocal()
    try:
        entries = session.query(Issue).order_by(Issue.created_at.desc()).limit(limit).all()
        return [
            {"id": entry.id, "github_issue": entry.github_issue, "created_at": entry.created_at}
            for entry in entries
        ]
    finally:
        session.close()


@router.get("/history", response_model=list[HistoryItem])
def history(limit: int = Query(default=50, ge=1, le=500)):
    session = DBSessionLocal()
    try:
        entries = session.query(UserHistory).order_by(UserHistory.created_at.desc()).limit(limit).all()
        return [
            {"id": entry.id, "user_id": entry.user_id, "action": entry.action, "details": entry.details or {}, "created_at": entry.created_at}
            for entry in entries
        ]
    finally:
        session.close()


@router.post("/workflow/start", response_model=WorkflowStartResponse)
def start_workflow(request: WorkflowStartRequest):
    try:
        return workflow_runner.start_workflow(request.github_issue, request.repository_summary, request.user_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.websocket("/workflow/ws")
async def workflow_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(workflow_events.snapshot())
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return
    except Exception:
        return
