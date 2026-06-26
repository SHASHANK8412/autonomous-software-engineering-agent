import { useWorkflowStream } from '../hooks/useWorkflowStream';

export function LogsPage() {
  const { logs } = useWorkflowStream();
  return (
    <section className="space-y-4">
      <h2 className="font-display text-3xl font-bold text-white">Logs</h2>
      <div className="space-y-3">
        {logs.map((log, index) => (
          <div key={`${log.created_at}-${index}`} className="rounded-3xl border border-white/10 bg-white/5 p-5 text-slate-200 shadow-glow">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>{log.level}</span>
              <span>{log.created_at ? new Date(log.created_at).toLocaleString() : '—'}</span>
            </div>
            <p className="mt-3 leading-7">{log.message}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
