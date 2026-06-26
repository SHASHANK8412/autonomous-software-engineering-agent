from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class WorkflowStatusResponse(BaseModel):
    workflow_id: Optional[str]
    status: str
    current_agent: Optional[str]
    progress: int
    last_message: Optional[str]
    updated_at: Optional[str]


class CurrentAgentResponse(BaseModel):
    current_agent: Optional[str]
    progress: int
    status: str


class DashboardLogItem(BaseModel):
    message: str
    level: str
    created_at: Optional[str]


class RepositorySummaryResponse(BaseModel):
    repository_summary: Optional[str]
    source: str = Field(default="cache")


class IssueItem(BaseModel):
    id: int
    github_issue: str
    created_at: Optional[datetime]


class HistoryItem(BaseModel):
    id: int
    user_id: str
    action: str
    details: Dict[str, Any]
    created_at: Optional[datetime]


class WorkflowStartRequest(BaseModel):
    github_issue: str
    repository_summary: str
    user_id: str = "anonymous"


class WorkflowStartResponse(BaseModel):
    workflow_id: str
    status: str
