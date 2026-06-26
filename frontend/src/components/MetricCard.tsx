type MetricCardProps = {
  label: string;
  value: string;
  description?: string;
};

export function MetricCard({ label, value, description }: MetricCardProps) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/5 p-5 shadow-glow">
      <p className="text-xs uppercase tracking-[0.3em] text-slate-400">{label}</p>
      <p className="mt-3 font-display text-3xl font-bold text-white">{value}</p>
      {description ? <p className="mt-2 text-sm text-slate-300">{description}</p> : null}
    </div>
  );
}
