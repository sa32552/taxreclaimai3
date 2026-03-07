
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import VATRecovery from './pages/VATRecovery';
import Forms from './pages/Forms';
import AuditLogs from './pages/AuditLogs';
import Layout from './components/Layout';
import './index.css';

import { AuthGuard } from './components/AuthGuard';

function App() {
  return (
    <Router>
      <AuthGuard>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/upload" element={<Upload />} />
            <Route path="/vat-recovery" element={<VATRecovery />} />
            <Route path="/forms" element={<Forms />} />
            <Route path="/audit-logs" element={<AuditLogs />} />
          </Routes>
        </Layout>
      </AuthGuard>
    </Router>
  );
}

export default App;
