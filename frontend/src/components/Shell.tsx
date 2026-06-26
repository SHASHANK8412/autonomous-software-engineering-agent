import { Link, NavLink } from 'react-router-dom';
import { PropsWithChildren } from 'react';

const navItems = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/repository', label: 'Repository' },
  { to: '/issue', label: 'Issue' },
  { to: '/workflow', label: 'Workflow' },
  { to: '/logs', label: 'Logs' },
  { to: '/pull-requests', label: 'Pull Requests' },
];

export function Shell({ children }: PropsWithChildren) {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(74,222,128,0.14),_transparent_36%),linear-gradient(180deg,#08101b_0%,#09111d_100%)] text-slate-100">
      <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-4 py-4 lg:px-8">
        <header className="flex items-center justify-between rounded-3xl border border-white/10 bg-white/5 px-5 py-4 backdrop-blur-xl shadow-glow">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-mint">Agent Control Plane</p>
            <h1 className="font-display text-2xl font-bold text-white">Autonomous Software Engineering</h1>
          </div>
          <Link to="/login" className="rounded-full border border-white/15 bg-white/10 px-4 py-2 text-sm font-medium text-white transition hover:bg-white/15">
            Sign out
          </Link>
        </header>

        <div className="mt-6 grid flex-1 gap-6 lg:grid-cols-[240px_1fr]">
          <aside className="rounded-3xl border border-white/10 bg-white/5 p-4 backdrop-blur-xl">
            <nav className="space-y-2">
              {navItems.map(item => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) =>
                    [
                      'block rounded-2xl px-4 py-3 text-sm font-medium transition',
                      isActive ? 'bg-mint text-ink-950' : 'text-slate-300 hover:bg-white/10 hover:text-white',
                    ].join(' ')
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </aside>

          <main className="rounded-3xl border border-white/10 bg-ink-950/60 p-4 shadow-glow backdrop-blur-xl lg:p-6">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
