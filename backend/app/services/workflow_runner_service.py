from __future__ import annotations

import threading
import uuid
from typing import Any, Dict

from app.services.workflow_event_service import get_workflow_event_service
from app.workflow.graph import create_main_workflow


class WorkflowRunnerService:
    def __init__(self):
        self.events = get_workflow_event_service()

    def start_workflow(self, github_issue: str, repository_summary: str, user_id: str = "anonymous") -> Dict[str, Any]:
        workflow_id = str(uuid.uuid4())
        self.events.update(
            workflow_id=workflow_id,
            status="running",
            current_agent="Planner",
            progress=0,
            last_message="Workflow started",
            repository_summary=repository_summary,
        )
        self.events.mark_issue(github_issue)
        self.events.record_history(user_id, "workflow_started", {"workflow_id": workflow_id, "github_issue": github_issue})

        thread = threading.Thread(
            target=self._run,
            args=(workflow_id, github_issue, repository_summary, user_id),
            daemon=True,
        )
        thread.start()
        return {"workflow_id": workflow_id, "status": "running"}

    def _run(self, workflow_id: str, github_issue: str, repository_summary: str, user_id: str) -> None:
        try:
            workflow = create_main_workflow()
            initial_state = {
                "workflow_id": workflow_id,
                "github_issue": github_issue,
                "repository_summary": repository_summary,
                "debug_retries": 0,
                "status": "running",
            }
            result = workflow.invoke(initial_state)
            self.events.update(
                workflow_id=workflow_id,
                status="completed",
                current_agent="Review",
                progress=100,
                last_message="Workflow completed",
            )
            self.events.record_history(user_id, "workflow_completed", {"workflow_id": workflow_id, "result_keys": list(result.keys())})
        except Exception as exc:
            self.events.update(
                workflow_id=workflow_id,
                status="failed",
                last_message=str(exc),
            )
            self.events.add_log(f"Workflow failed: {exc}", level="ERROR")
            self.events.record_history(user_id, "workflow_failed", {"workflow_id": workflow_id, "error": str(exc)})


workflow_runner_service = WorkflowRunnerService()


def get_workflow_runner_service() -> WorkflowRunnerService:
    return workflow_runner_service
