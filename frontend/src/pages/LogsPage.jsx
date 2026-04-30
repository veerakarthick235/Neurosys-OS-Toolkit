import { useState, useEffect } from 'react';
import { FileText, AlertCircle, AlertTriangle, Info, RefreshCw, Brain, Upload } from 'lucide-react';
import { getSystemLogs, analyzeLogs } from '../api/client';

export default function LogsPage() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [customLog, setCustomLog] = useState('');
  const [showCustom, setShowCustom] = useState(false);
  const [filter, setFilter] = useState('all');

  const fetchSystemLogs = async () => {
    setLoading(true);
    try {
      const res = await getSystemLogs(50);
      setAnalysis(res.data);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { fetchSystemLogs(); }, []);

  const handleCustomAnalyze = async () => {
    if (!customLog.trim()) return;
    setLoading(true);
    try {
      const res = await analyzeLogs(customLog);
      setAnalysis(res.data);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const levelIcon = (level) => {
    switch (level) {
      case 'error': return <AlertCircle className="w-4 h-4 text-red-400" />;
      case 'warning': return <AlertTriangle className="w-4 h-4 text-amber-400" />;
      default: return <Info className="w-4 h-4 text-neuro-400" />;
    }
  };

  const levelBadge = (level) => {
    switch (level) {
      case 'error': return 'badge-error';
      case 'warning': return 'badge-warning';
      case 'debug': return 'text-gray-600 bg-gray-500/10';
      default: return 'badge-info';
    }
  };

  const filteredEntries = analysis?.entries?.filter(e =>
    filter === 'all' || e.level === filter
  ) || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Log Analyzer</h1>
          <p className="text-gray-500 text-sm mt-1">AI-powered log analysis with pattern detection</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setShowCustom(!showCustom)}
            className="px-4 py-2.5 bg-surface-700 text-gray-300 rounded-xl border border-white/5 hover:bg-surface-600 transition-colors text-sm flex items-center gap-2">
            <Upload className="w-4 h-4" /> Custom Log
          </button>
          <button onClick={fetchSystemLogs} className="btn-primary flex items-center gap-2">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> System Logs
          </button>
        </div>
      </div>

      {/* Custom Log Input */}
      {showCustom && (
        <div className="glass-card p-5 animate-slide-up">
          <h3 className="text-sm font-semibold text-gray-300 mb-3">Paste Log Content</h3>
          <textarea className="input-dark h-40 font-mono text-xs resize-none"
            placeholder="Paste your log content here..."
            value={customLog} onChange={e => setCustomLog(e.target.value)} />
          <button onClick={handleCustomAnalyze} className="btn-primary mt-3 flex items-center gap-2">
            <Brain className="w-4 h-4" /> Analyze
          </button>
        </div>
      )}

      {analysis && (
        <>
          {/* AI Summary */}
          <div className="glass-card p-6 border-l-4 border-neuro-500">
            <div className="flex items-start gap-3">
              <Brain className="w-5 h-5 text-neuro-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-sm font-semibold text-white mb-2">AI Analysis Summary</h3>
                <p className="text-sm text-gray-300">{analysis.ai_summary}</p>
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard label="Total Entries" value={analysis.total_entries} color="neuro" />
            <StatCard label="Errors" value={analysis.error_count} color="red" />
            <StatCard label="Warnings" value={analysis.warning_count} color="amber" />
            <StatCard label="Info" value={analysis.info_count} color="emerald" />
          </div>

          {/* Patterns */}
          {analysis.patterns?.length > 0 && (
            <div className="glass-card p-5">
              <h3 className="text-sm font-semibold text-gray-300 mb-4">Detected Patterns</h3>
              <div className="space-y-3">
                {analysis.patterns.map((p, i) => (
                  <div key={i} className="bg-surface-800/50 rounded-xl p-4 border border-white/5">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-amber-400">Pattern detected ({p.count}x)</span>
                    </div>
                    <p className="text-sm text-gray-300 mb-1">{p.explanation}</p>
                    <p className="text-xs text-neuro-400">💡 {p.recommendation}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {analysis.recommendations?.length > 0 && (
            <div className="glass-card p-5">
              <h3 className="text-sm font-semibold text-gray-300 mb-3">Recommendations</h3>
              <ul className="space-y-2">
                {analysis.recommendations.map((r, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-gray-400">
                    <span className="text-neuro-400 mt-0.5">→</span> {r}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Filter & Log Entries */}
          <div className="glass-card overflow-hidden">
            <div className="p-4 border-b border-white/5 flex items-center gap-2">
              <span className="text-sm text-gray-400">Filter:</span>
              {['all', 'error', 'warning', 'info', 'debug'].map(f => (
                <button key={f} onClick={() => setFilter(f)}
                  className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
                    filter === f ? 'bg-neuro-600/20 text-neuro-400' : 'text-gray-500 hover:text-gray-300'
                  }`}>
                  {f.charAt(0).toUpperCase() + f.slice(1)}
                </button>
              ))}
            </div>
            <div className="max-h-96 overflow-y-auto divide-y divide-white/5">
              {filteredEntries.slice(0, 100).map((entry, i) => (
                <div key={i} className="flex items-start gap-3 px-4 py-2.5 hover:bg-surface-600/20 transition-colors">
                  {levelIcon(entry.level)}
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 mb-0.5">
                      <span className={`badge ${levelBadge(entry.level)} text-[10px]`}>{entry.level.toUpperCase()}</span>
                      {entry.timestamp && <span className="text-[10px] text-gray-600 font-mono">{entry.timestamp}</span>}
                    </div>
                    <p className="text-xs text-gray-400 font-mono truncate">{entry.message}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function StatCard({ label, value, color }) {
  const colors = {
    neuro: 'from-neuro-400 to-cyan-300',
    red: 'from-red-400 to-rose-300',
    amber: 'from-amber-400 to-orange-300',
    emerald: 'from-emerald-400 to-teal-300',
  };
  return (
    <div className="glass-card p-4 text-center">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className={`text-2xl font-bold bg-gradient-to-r ${colors[color]} bg-clip-text text-transparent`}>{value}</p>
    </div>
  );
}
