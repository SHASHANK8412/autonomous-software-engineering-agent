import { Link } from 'react-router-dom';

export function LoginPage() {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(245,158,11,0.14),_transparent_28%),linear-gradient(180deg,#08101b_0%,#0b1320_100%)] px-4 py-10 text-white">
      <div className="mx-auto flex min-h-[calc(100vh-5rem)] max-w-6xl items-center">
        <div className="grid w-full gap-8 rounded-[2rem] border border-white/10 bg-white/5 p-8 shadow-glow backdrop-blur-xl lg:grid-cols-2 lg:p-12">
          <div className="space-y-6">
            <p className="text-xs uppercase tracking-[0.35em] text-mint">Secure Access</p>
            <h1 className="font-display text-4xl font-bold leading-tight">Sign in to the autonomous engineering control plane.</h1>
            <p className="max-w-xl text-base leading-7 text-slate-300">Track workflows, inspect live logs, review repository intelligence, and monitor the agent pipeline from a single professional dashboard.</p>
          </div>
          <div className="rounded-[1.5rem] border border-white/10 bg-ink-950/70 p-6">
            <label className="block text-sm text-slate-300">
              Email
              <input className="mt-2 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none ring-0 placeholder:text-slate-500" placeholder="agent@company.com" />
            </label>
            <label className="mt-4 block text-sm text-slate-300">
              Password
              <input type="password" className="mt-2 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none ring-0 placeholder:text-slate-500" placeholder="••••••••" />
            </label>
            <Link to="/dashboard" className="mt-6 inline-flex w-full items-center justify-center rounded-2xl bg-mint px-4 py-3 font-semibold text-ink-950 transition hover:brightness-110">Enter dashboard</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
