import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, Cpu, Terminal, Zap,
  FolderSearch, FileText, Activity
} from 'lucide-react';

const links = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/processes', icon: Cpu, label: 'Processes' },
  { to: '/ai-command', icon: Terminal, label: 'AI Command' },
  { to: '/optimizer', icon: Zap, label: 'Optimizer' },
  { to: '/filesystem', icon: FolderSearch, label: 'File System' },
  { to: '/logs', icon: FileText, label: 'Log Analyzer' },
];

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-surface-800/80 backdrop-blur-xl border-r border-white/5 z-50 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-neuro-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-neuro-500/30">
            <Activity className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight">NeuroSys</h1>
            <p className="text-xs text-gray-500 -mt-0.5">OS Toolkit v1.0</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto">
        <p className="text-xs uppercase tracking-wider text-gray-600 font-semibold px-4 mb-3">Modules</p>
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `sidebar-link ${isActive ? 'active' : ''}`
            }
            end={to === '/'}
          >
            <Icon className="w-5 h-5" />
            <span className="font-medium text-sm">{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-white/5">
        <div className="glass-card p-3 text-center">
          <p className="text-xs text-gray-500">Powered by</p>
          <p className="text-sm font-semibold bg-gradient-to-r from-neuro-400 to-cyan-300 bg-clip-text text-transparent">
            AI + psutil
          </p>
        </div>
      </div>
    </aside>
  );
}
