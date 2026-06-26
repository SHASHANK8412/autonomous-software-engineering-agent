import { useWorkflowStream } from '../hooks/useWorkflowStream';

export function RepositoryPage() {
  const { repositorySummary } = useWorkflowStream();
  return (
    <section className="space-y-4">
      <h2 className="font-display text-3xl font-bold text-white">Repository</h2>
      <div className="rounded-3xl border border-white/10 bg-white/5 p-6 text-slate-200 shadow-glow">
        <p className="text-sm uppercase tracking-[0.3em] text-slate-400">Summary</p>
        <p className="mt-3 leading-7">{repositorySummary?.repository_summary ?? 'Repository summary will appear here when cached.'}</p>
      </div>
    </section>
  );
}
