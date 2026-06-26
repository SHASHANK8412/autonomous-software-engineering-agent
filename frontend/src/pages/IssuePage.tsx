import { useWorkflowStream } from '../hooks/useWorkflowStream';

export function IssuePage() {
  const { issues } = useWorkflowStream();
  return (
    <section className="space-y-4">
      <h2 className="font-display text-3xl font-bold text-white">Issues</h2>
      <div className="grid gap-4 lg:grid-cols-2">
        {issues.map(issue => (
          <article key={issue.id} className="rounded-3xl border border-white/10 bg-white/5 p-5 text-slate-200 shadow-glow">
            <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Issue #{issue.id}</p>
            <p className="mt-3 leading-7">{issue.github_issue}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
