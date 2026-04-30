import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import { useWebSocket } from '../../hooks/useWebSocket';
import { WS_METRICS_URL } from '../../api/client';

export default function DashboardLayout() {
  const { isConnected } = useWebSocket(WS_METRICS_URL);

  return (
    <div className="min-h-screen bg-surface-900">
      <Sidebar />
      <div className="ml-64">
        <Header wsConnected={isConnected} />
        <main className="p-8 animate-fade-in">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
