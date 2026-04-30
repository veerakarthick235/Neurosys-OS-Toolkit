import { BrowserRouter, Routes, Route } from 'react-router-dom';
import DashboardLayout from './components/Layout/DashboardLayout';
import DashboardPage from './pages/DashboardPage';
import ProcessesPage from './pages/ProcessesPage';
import AICommandPage from './pages/AICommandPage';
import OptimizerPage from './pages/OptimizerPage';
import FileSystemPage from './pages/FileSystemPage';
import LogsPage from './pages/LogsPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<DashboardLayout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/processes" element={<ProcessesPage />} />
          <Route path="/ai-command" element={<AICommandPage />} />
          <Route path="/optimizer" element={<OptimizerPage />} />
          <Route path="/filesystem" element={<FileSystemPage />} />
          <Route path="/logs" element={<LogsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
