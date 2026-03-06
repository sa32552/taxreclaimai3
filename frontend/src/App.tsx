
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import VATRecovery from './pages/VATRecovery';
import Forms from './pages/Forms';
import Layout from './components/Layout';
import './index.css';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/vat-recovery" element={<VATRecovery />} />
          <Route path="/forms" element={<Forms />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
