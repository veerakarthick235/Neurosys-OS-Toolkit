import { useState, useEffect, useCallback } from 'react';
import { Search, Skull, RefreshCw, ArrowUpDown } from 'lucide-react';
import { getProcesses, killProcess, searchProcesses } from '../api/client';

export default function ProcessesPage() {
  const [processes, setProcesses] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [sortBy, setSortBy] = useState('cpu');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [killConfirm, setKillConfirm] = useState(null);

  const fetchProcesses = useCallback(async () => {
    setLoading(true);
    try {
      if (searchQuery.trim()) {
        const res = await searchProcesses(searchQuery);
        setProcesses(res.data);
        setTotalCount(res.data.length);
      } else {
        const res = await getProcesses(sortBy, 80);
        setProcesses(res.data.processes);
        setTotalCount(res.data.total_count);
      }
    } catch (e) { console.error(e); }
    setLoading(false);
  }, [sortBy, searchQuery]);

  useEffect(() => { fetchProcesses(); const id = setInterval(fetchProcesses, 5000); return () => clearInterval(id); }, [fetchProcesses]);

  const handleKill = async (pid) => {
    try {
      const res = await killProcess(pid);
      if (res.data.success) {
        setProcesses(prev => prev.filter(p => p.pid !== pid));
      }
      alert(res.data.message);
    } catch (e) { alert('Failed to kill process'); }
    setKillConfirm(null);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Process Monitor</h1>
        <p className="text-gray-500 text-sm mt-1">View and manage running processes — {totalCount} total</p>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input className="input-dark pl-10" placeholder="Search processes..."
            value={searchQuery} onChange={e => setSearchQuery(e.target.value)} />
        </div>
        <select className="input-dark w-48" value={sortBy} onChange={e => setSortBy(e.target.value)}>
          <option value="cpu">Sort by CPU</option>
          <option value="memory">Sort by Memory</option>
          <option value="pid">Sort by PID</option>
          <option value="name">Sort by Name</option>
        </select>
        <button onClick={fetchProcesses} className="btn-primary flex items-center gap-2">
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Refresh
        </button>
      </div>

      {/* Table */}
      <div className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/5">
                {['PID','Name','Status','CPU %','Memory %','Memory','Threads','User'].map(h => (
                  <th key={h} className="text-left px-4 py-3 text-gray-400 font-medium text-xs uppercase tracking-wider">{h}</th>
                ))}
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {processes.map(proc => (
                <tr key={proc.pid} className="hover:bg-surface-600/30 transition-colors">
                  <td className="px-4 py-3 font-mono text-neuro-400">{proc.pid}</td>
                  <td className="px-4 py-3 font-medium text-gray-200 max-w-[200px] truncate">{proc.name}</td>
                  <td className="px-4 py-3">
                    <span className={`badge ${proc.status === 'running' ? 'badge-success' : proc.status === 'sleeping' ? 'badge-info' : 'badge-warning'}`}>
                      {proc.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-surface-800 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full" style={{ width: `${Math.min(proc.cpu_percent, 100)}%` }} />
                      </div>
                      <span className="text-xs text-gray-400 w-12">{proc.cpu_percent.toFixed(1)}%</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-surface-800 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full" style={{ width: `${Math.min(proc.memory_percent, 100)}%` }} />
                      </div>
                      <span className="text-xs text-gray-400 w-12">{proc.memory_percent.toFixed(1)}%</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-gray-400 text-xs">{proc.memory_mb.toFixed(1)} MB</td>
                  <td className="px-4 py-3 text-gray-400">{proc.num_threads}</td>
                  <td className="px-4 py-3 text-gray-500 text-xs truncate max-w-[120px]">{proc.username || '-'}</td>
                  <td className="px-4 py-3">
                    {killConfirm === proc.pid ? (
                      <div className="flex items-center gap-1">
                        <button onClick={() => handleKill(proc.pid)} className="px-2 py-1 bg-red-600 text-white rounded text-xs">Confirm</button>
                        <button onClick={() => setKillConfirm(null)} className="px-2 py-1 bg-surface-600 text-gray-400 rounded text-xs">Cancel</button>
                      </div>
                    ) : (
                      <button onClick={() => setKillConfirm(proc.pid)} className="btn-danger flex items-center gap-1 text-xs">
                        <Skull className="w-3 h-3" /> Kill
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
