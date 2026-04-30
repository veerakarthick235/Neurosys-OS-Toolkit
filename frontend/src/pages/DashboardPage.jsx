import { useState, useEffect, useCallback } from 'react';
import { Cpu, MemoryStick, HardDrive, Wifi, TrendingUp, Clock, Monitor, Server } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';
import { getSystemMetrics, getSystemHistory, getSystemInfo, getSystemPredictions, WS_METRICS_URL } from '../api/client';
import { useWebSocket } from '../hooks/useWebSocket';

function MetricCard({ icon: Icon, title, value, unit, percent, color, subtitle }) {
  const colorMap = {
    cyan: 'from-cyan-500 to-blue-500',
    purple: 'from-purple-500 to-pink-500',
    emerald: 'from-emerald-500 to-teal-500',
    amber: 'from-amber-500 to-orange-500',
  };
  const glowMap = {
    cyan: 'shadow-cyan-500/20',
    purple: 'shadow-purple-500/20',
    emerald: 'shadow-emerald-500/20',
    amber: 'shadow-amber-500/20',
  };
  return (
    <div className="glass-card p-6 animate-slide-up">
      <div className="flex items-start justify-between mb-4">
        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colorMap[color]} flex items-center justify-center shadow-lg ${glowMap[color]}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
        {percent !== undefined && (
          <span className="text-xs font-mono text-gray-500">{percent.toFixed(1)}%</span>
        )}
      </div>
      <p className="text-sm text-gray-400 mb-1">{title}</p>
      <p className="metric-value">{value}<span className="text-lg ml-1">{unit}</span></p>
      {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
      {percent !== undefined && (
        <div className="mt-3 h-1.5 bg-surface-800 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full bg-gradient-to-r ${colorMap[color]} transition-all duration-700`}
            style={{ width: `${Math.min(percent, 100)}%` }}
          />
        </div>
      )}
    </div>
  );
}

function ChartCard({ title, data, dataKey, color, gradientId }) {
  return (
    <div className="glass-card p-6 animate-slide-up">
      <h3 className="text-sm font-semibold text-gray-300 mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={color} stopOpacity={0.3} />
              <stop offset="95%" stopColor={color} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f293d" />
          <XAxis dataKey="time" tick={{ fontSize: 10, fill: '#6b7280' }} axisLine={false} tickLine={false} />
          <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#6b7280' }} axisLine={false} tickLine={false} />
          <Tooltip
            contentStyle={{ backgroundColor: '#151c2b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', color: '#e5e7eb' }}
          />
          <Area type="monotone" dataKey={dataKey} stroke={color} fill={`url(#${gradientId})`} strokeWidth={2} dot={false} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function DashboardPage() {
  const [metrics, setMetrics] = useState(null);
  const [history, setHistory] = useState(null);
  const [sysInfo, setSysInfo] = useState(null);
  const [predictions, setPredictions] = useState(null);
  const { data: wsData, isConnected } = useWebSocket(WS_METRICS_URL);

  const fetchData = useCallback(async () => {
    try {
      const [mRes, hRes, iRes, pRes] = await Promise.all([
        getSystemMetrics(), getSystemHistory(), getSystemInfo(), getSystemPredictions()
      ]);
      setMetrics(mRes.data);
      setHistory(hRes.data);
      setSysInfo(iRes.data);
      setPredictions(pRes.data);
    } catch (e) { console.error('Fetch error:', e); }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  // Update from WebSocket
  useEffect(() => {
    if (wsData?.data) {
      setMetrics(prev => ({
        ...prev,
        cpu: wsData.data.cpu,
        memory: wsData.data.memory,
        network: wsData.data.network,
      }));
    }
  }, [wsData]);

  // Build chart data from history
  const chartData = history?.timestamps?.map((ts, i) => ({
    time: new Date(ts).toLocaleTimeString('en', { minute: '2-digit', second: '2-digit' }),
    cpu: history.cpu_values[i],
    memory: history.memory_values[i],
  })) || [];

  const cpu = metrics?.cpu || wsData?.data?.cpu;
  const mem = metrics?.memory || wsData?.data?.memory;
  const net = metrics?.network || wsData?.data?.network;
  const disks = metrics?.disks || wsData?.data?.disks || [];

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">System Dashboard</h1>
        <p className="text-gray-500 text-sm mt-1">Real-time system performance monitoring</p>
      </div>

      {/* System Info Bar */}
      {sysInfo && (
        <div className="glass-card p-4 flex items-center gap-8 text-sm">
          <div className="flex items-center gap-2 text-gray-400">
            <Monitor className="w-4 h-4 text-neuro-400" />
            <span>{sysInfo.hostname}</span>
          </div>
          <div className="flex items-center gap-2 text-gray-400">
            <Server className="w-4 h-4 text-neuro-400" />
            <span>{sysInfo.os_name} {sysInfo.architecture}</span>
          </div>
          <div className="flex items-center gap-2 text-gray-400">
            <Clock className="w-4 h-4 text-neuro-400" />
            <span>Uptime: {sysInfo.uptime_formatted}</span>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
            <span className="text-xs text-gray-500">{isConnected ? 'Live data' : 'Polling'}</span>
          </div>
        </div>
      )}

      {/* Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        <MetricCard icon={Cpu} title="CPU Usage" value={cpu?.percent?.toFixed(1) || '0'}
          unit="%" percent={cpu?.percent || 0} color="cyan"
          subtitle={`${cpu?.logical_count || cpu?.per_cpu?.length || '-'} logical cores`} />
        <MetricCard icon={MemoryStick} title="Memory" value={mem?.used_gb?.toFixed(1) || '0'}
          unit="GB" percent={mem?.percent || 0} color="purple"
          subtitle={`of ${mem?.total_gb?.toFixed(1) || '-'} GB total`} />
        <MetricCard icon={HardDrive} title="Disk" value={disks[0]?.percent?.toFixed(1) || '0'}
          unit="%" percent={disks[0]?.percent || 0} color="emerald"
          subtitle={disks[0] ? `${disks[0].free_gb} GB free` : ''} />
        <MetricCard icon={Wifi} title="Network ↑/↓"
          value={`${((net?.bytes_sent_rate || net?.sent_rate || 0) / 1024).toFixed(1)}`}
          unit="KB/s" color="amber"
          subtitle={`↓ ${((net?.bytes_recv_rate || net?.recv_rate || 0) / 1024).toFixed(1)} KB/s`} />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="CPU Usage History" data={chartData} dataKey="cpu"
          color="#22d3ee" gradientId="cpuGrad" />
        <ChartCard title="Memory Usage History" data={chartData} dataKey="memory"
          color="#a78bfa" gradientId="memGrad" />
      </div>

      {/* Predictions */}
      {predictions && predictions.length > 0 && (
        <div className="glass-card p-6">
          <h3 className="text-sm font-semibold text-gray-300 mb-4 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-neuro-400" /> Resource Predictions
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {predictions.map((pred, i) => (
              <div key={i} className="bg-surface-800/50 rounded-xl p-4 border border-white/5">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-gray-300">{pred.metric}</span>
                  <span className={`badge ${pred.trend === 'increasing' ? 'badge-warning' : pred.trend === 'decreasing' ? 'badge-success' : 'badge-info'}`}>
                    {pred.trend}
                  </span>
                </div>
                <p className="text-2xl font-bold text-white">{pred.current_value?.toFixed(1)}%</p>
                {pred.alert && (
                  <p className="text-xs text-amber-400 mt-2 flex items-center gap-1">⚠️ {pred.alert}</p>
                )}
                <p className="text-xs text-gray-500 mt-1">Confidence: {(pred.confidence * 100).toFixed(0)}%</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
