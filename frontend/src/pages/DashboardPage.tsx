import { MetricCard } from '../components/MetricCard';
import { useWorkflowStream } from '../hooks/useWorkflowStream';

function ProgressBar({ progress }: { progress: number }) {
  return (
    <div className="h-3 overflow-hidden rounded-full bg-white/10">
      <div className="h-full rounded-full bg-gradient-to-r from-mint via-emerald-400 to-sun transition-all" style={{ width: `${progress}%` }} />
    </div>
  );
}

export function DashboardPage() {
  const { workflowStatus, logs, repositorySummary, issues, history, connected } = useWorkflowStream();
  const progress = workflowStatus?.progress ?? 0;

  return (
    <div className="space-y-6">
      <section className="grid gap-4 lg:grid-cols-4">
        <MetricCard label="Connection" value={connected ? 'Live' : 'Offline'} description="WebSocket dashboard stream" />
        <MetricCard label="Status" value={workflowStatus?.status ?? 'Idle'} description="Current workflow state" />
        <MetricCard label="Current Agent" value={workflowStatus?.current_agent ?? 'None'} description="Active agent in the pipeline" />
        <MetricCard label="Progress" value={`${progress}%`} description="End-to-end workflow completion" />
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.4fr_1fr]">
        <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-glow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Workflow</p>
              <h2 className="mt-2 font-display text-2xl font-bold text-white">Live execution progress</h2>
            </div>
            <span className="rounded-full border border-mint/30 bg-mint/10 px-3 py-1 text-xs font-semibold text-mint">{workflowStatus?.last_message ?? 'Waiting'}</span>
          </div>
          <div className="mt-6 space-y-3">
            <ProgressBar progress={progress} />
            <div className="flex items-center justify-between text-sm text-slate-300">
              <span>{workflowStatus?.workflow_id ?? 'No workflow running'}</span>
              <span>{workflowStatus?.updated_at ? new Date(workflowStatus.updated_at).toLocaleString() : '—'}</span>
            </div>
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-glow">
          <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Repository Summary</p>
          <p className="mt-3 text-sm leading-7 text-slate-200">{repositorySummary?.repository_summary ?? 'No repository summary cached yet.'}</p>
          <div className="mt-6 grid grid-cols-2 gap-4 text-sm text-slate-300">
            <div>
              <p className="text-slate-500">Issues</p>
              <p className="mt-1 text-xl font-semibold text-white">{issues.length}</p>
            </div>
            <div>
              <p className="text-slate-500">History</p>
              <p className="mt-1 text-xl font-semibold text-white">{history.length}</p>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-2">
        <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-glow">
          <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Live Logs</p>
          <div className="mt-4 space-y-3">
            {logs.slice(0, 8).map((log, index) => (
              <div key={`${log.created_at}-${index}`} className="rounded-2xl border border-white/10 bg-ink-900/60 px-4 py-3 text-sm text-slate-200">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>{log.level}</span>
                  <span>{log.created_at ? new Date(log.created_at).toLocaleTimeString() : '—'}</span>
                </div>
                <p className="mt-2">{log.message}</p>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-glow">
          <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Recent History</p>
          <div className="mt-4 space-y-3">
            {history.slice(0, 8).map(item => (
              <div key={item.id} className="rounded-2xl border border-white/10 bg-ink-900/60 px-4 py-3 text-sm text-slate-200">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>{item.user_id}</span>
                  <span>{item.created_at ? new Date(item.created_at).toLocaleString() : '—'}</span>
                </div>
                <p className="mt-2 font-medium text-white">{item.action}</p>
                <pre className="mt-2 overflow-auto text-xs text-slate-400">{JSON.stringify(item.details, null, 2)}</pre>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
