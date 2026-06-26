from __future__ import annotations

from datetime import datetime
from threading import Lock
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.db.models import AIResponse, DBSessionLocal, Issue, Log, UserHistory, WorkflowState as DBWorkflowState
from app.services.redis_service import get_redis_service


class WorkflowEventService:
    _instance: Optional["WorkflowEventService"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return
        self._lock = Lock()
        self._state: Dict[str, Any] = {
            "workflow_id": None,
            "status": "idle",
            "current_agent": None,
            "progress": 0,
            "last_message": None,
            "updated_at": None,
            "repository_summary": None,
            "logs": [],
            "history": [],
        }
        self.redis = get_redis_service()
        self._initialized = True

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return dict(self._state)

    def _persist_snapshot(self) -> None:
        snapshot = self.snapshot()
        self.redis.set("dashboard:workflow_state", snapshot, ex=settings.workflow_cache_ttl)
        if snapshot.get("repository_summary"):
            self.redis.set("dashboard:repository_summary", snapshot["repository_summary"], ex=settings.workflow_cache_ttl)

        session = DBSessionLocal()
        try:
            workflow_id = snapshot.get("workflow_id") or "latest"
            state_row = session.query(DBWorkflowState).filter(DBWorkflowState.workflow_id == workflow_id).first()
            if state_row is None:
                state_row = DBWorkflowState(workflow_id=workflow_id, state_data=snapshot)
                session.add(state_row)
            else:
                state_row.state_data = snapshot
            session.commit()
        finally:
            session.close()

    def update(self, **kwargs: Any) -> Dict[str, Any]:
        with self._lock:
            for key, value in kwargs.items():
                if value is not None:
                    self._state[key] = value
            self._state["updated_at"] = datetime.utcnow().isoformat()
            snapshot = dict(self._state)
        self._persist_snapshot()
        return snapshot

    def add_log(self, message: str, level: str = "INFO") -> None:
        entry = {
            "message": message,
            "level": level,
            "created_at": datetime.utcnow().isoformat(),
        }
        with self._lock:
            logs: List[Dict[str, Any]] = list(self._state.get("logs", []))
            logs.append(entry)
            self._state["logs"] = logs[-settings.dashboard_log_limit :]
            self._state["last_message"] = message
            self._state["updated_at"] = entry["created_at"]
        session = DBSessionLocal()
        try:
            session.add(Log(message=message, level=level))
            session.commit()
        finally:
            session.close()
        self._persist_snapshot()

    def set_repository_summary(self, summary: str) -> None:
        self.update(repository_summary=summary)

    def set_current_agent(self, agent_name: str, progress: Optional[int] = None, message: Optional[str] = None) -> None:
        payload: Dict[str, Any] = {"current_agent": agent_name}
        if progress is not None:
            payload["progress"] = progress
        if message is not None:
            payload["last_message"] = message
        self.update(**payload)
        if message:
            self.add_log(message)

    def mark_issue(self, github_issue: str) -> None:
        session = DBSessionLocal()
        try:
            session.add(Issue(github_issue=github_issue))
            session.commit()
        finally:
            session.close()

    def record_history(self, user_id: str, action: str, details: Optional[Dict[str, Any]] = None) -> None:
        session = DBSessionLocal()
        try:
            session.add(UserHistory(user_id=user_id, action=action, details=details or {}))
            session.commit()
        finally:
            session.close()

    def log_ai_response(self, prompt: str, response: Any) -> None:
        session = DBSessionLocal()
        try:
            session.add(AIResponse(prompt=prompt, response=response))
            session.commit()
        finally:
            session.close()
        self._persist_snapshot()


workflow_event_service = WorkflowEventService()


def get_workflow_event_service() -> WorkflowEventService:
    return workflow_event_service
