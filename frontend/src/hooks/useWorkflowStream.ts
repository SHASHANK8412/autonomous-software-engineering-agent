import { useEffect, useMemo, useState } from 'react';
import { api, workflowSocketUrl, WorkflowStatus, DashboardLog, RepositorySummary, IssueItem, HistoryItem } from '../lib/api';

export function useWorkflowStream() {
  const [workflowStatus, setWorkflowStatus] = useState<WorkflowStatus | null>(null);
  const [logs, setLogs] = useState<DashboardLog[]>([]);
  const [repositorySummary, setRepositorySummary] = useState<RepositorySummary | null>(null);
  const [issues, setIssues] = useState<IssueItem[]>([]);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    let cancelled = false;

    Promise.all([
      api.workflowStatus(),
      api.logs(),
      api.repositorySummary(),
      api.issues(),
      api.history(),
    ]).then(([status, fetchedLogs, summary, fetchedIssues, fetchedHistory]) => {
      if (cancelled) return;
      setWorkflowStatus(status);
      setLogs(fetchedLogs);
      setRepositorySummary(summary);
      setIssues(fetchedIssues);
      setHistory(fetchedHistory);
    }).catch(() => undefined);

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    const socket = new WebSocket(workflowSocketUrl());

    socket.onopen = () => setConnected(true);
    socket.onclose = () => setConnected(false);
    socket.onerror = () => setConnected(false);
    socket.onmessage = event => {
      try {
        const payload = JSON.parse(event.data) as WorkflowStatus & { logs?: DashboardLog[]; repository_summary?: string | null; history?: HistoryItem[] };
        setWorkflowStatus({
          workflow_id: payload.workflow_id,
          status: payload.status,
          current_agent: payload.current_agent,
          progress: payload.progress,
          last_message: payload.last_message,
          updated_at: payload.updated_at,
        });
        if (payload.logs) {
          setLogs(payload.logs as DashboardLog[]);
        }
        if (payload.repository_summary) {
          setRepositorySummary({ repository_summary: payload.repository_summary, source: 'stream' });
        }
        if (payload.history) {
          setHistory(payload.history);
        }
      } catch {
        // ignore malformed messages
      }
    };

    return () => socket.close();
  }, []);

  return useMemo(() => ({ workflowStatus, logs, repositorySummary, issues, history, connected }), [workflowStatus, logs, repositorySummary, issues, history, connected]);
}
