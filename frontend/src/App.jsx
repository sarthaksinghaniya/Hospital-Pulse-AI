import { lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar.jsx';
import Header from './components/Header.jsx';

const Dashboard = lazy(() => import('./pages/Dashboard.jsx'));
const PatientRisk = lazy(() => import('./pages/PatientRisk.jsx'));
const Monitoring = lazy(() => import('./pages/Monitoring.jsx'));
const Alerts = lazy(() => import('./pages/Alerts.jsx'));

function App() {
  return (
    <div className="min-h-screen bg-shell text-text-primary">
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex-1 flex flex-col min-h-screen">
          <Header />
          <main className="flex-1 p-4 sm:p-6 lg:p-8 space-y-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/risk" element={<PatientRisk />} />
              <Route path="/monitoring" element={<Monitoring />} />
              <Route path="/alerts" element={<Alerts />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </div>
  );
}

export default App;
