import { useWorkflowStream } from '../hooks/useWorkflowStream';

export function WorkflowPage() {
  const { workflowStatus } = useWorkflowStream();
  return (
    <section className="space-y-4">
      <h2 className="font-display text-3xl font-bold text-white">Workflow</h2>
      <div className="rounded-3xl border border-white/10 bg-white/5 p-6 text-slate-200 shadow-glow">
        <p className="text-sm uppercase tracking-[0.3em] text-slate-400">Current agent</p>
        <p className="mt-3 text-2xl font-semibold text-white">{workflowStatus?.current_agent ?? 'Idle'}</p>
        <p className="mt-2 text-sm text-slate-300">Progress: {workflowStatus?.progress ?? 0}%</p>
      </div>
    </section>
  );
}
