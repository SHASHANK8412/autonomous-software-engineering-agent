const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1';

export type WorkflowStatus = {
  workflow_id?: string | null;
  status: string;
  current_agent?: string | null;
  progress: number;
  last_message?: string | null;
  updated_at?: string | null;
};

export type DashboardLog = {
  message: string;
  level: string;
  created_at?: string | null;
};

export type RepositorySummary = {
  repository_summary?: string | null;
  source: string;
};

export type IssueItem = {
  id: number;
  github_issue: string;
  created_at?: string | null;
};

export type HistoryItem = {
  id: number;
  user_id: string;
  action: string;
  details: Record<string, unknown>;
  created_at?: string | null;
};

export async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  workflowStatus: () => fetchJson<WorkflowStatus>('/dashboard/workflow-status'),
  currentAgent: () => fetchJson<WorkflowStatus>('/dashboard/current-agent'),
  logs: () => fetchJson<DashboardLog[]>('/dashboard/logs'),
  repositorySummary: () => fetchJson<RepositorySummary>('/dashboard/repository-summary'),
  issues: () => fetchJson<IssueItem[]>('/dashboard/issues'),
  history: () => fetchJson<HistoryItem[]>('/dashboard/history'),
  startWorkflow: async (github_issue: string, repository_summary: string, user_id = 'user@example.com') => {
    const response = await fetch(`${API_BASE}/dashboard/workflow/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ github_issue, repository_summary, user_id }),
    });
    if (!response.ok) {
      throw new Error(`Failed to start workflow: ${response.status}`);
    }
    return response.json() as Promise<{ workflow_id: string; status: string }>;
  },
};

export function workflowSocketUrl() {
  const wsBase = API_BASE.replace(/^http/, 'ws');
  return `${wsBase}/dashboard/workflow/ws`;
}
