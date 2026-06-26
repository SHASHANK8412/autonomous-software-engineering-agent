import { Navigate, Route, Routes } from 'react-router-dom';
import { Shell } from './components/Shell';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { RepositoryPage } from './pages/RepositoryPage';
import { IssuePage } from './pages/IssuePage';
import { WorkflowPage } from './pages/WorkflowPage';
import { LogsPage } from './pages/LogsPage';
import { PullRequestsPage } from './pages/PullRequestsPage';

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/*"
        element={
          <Shell>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/repository" element={<RepositoryPage />} />
              <Route path="/issue" element={<IssuePage />} />
              <Route path="/workflow" element={<WorkflowPage />} />
              <Route path="/logs" element={<LogsPage />} />
              <Route path="/pull-requests" element={<PullRequestsPage />} />
            </Routes>
          </Shell>
        }
      />
    </Routes>
  );
}
