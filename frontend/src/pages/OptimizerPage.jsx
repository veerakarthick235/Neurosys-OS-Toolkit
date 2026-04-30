import { useState, useEffect } from 'react';
import { Zap, CheckCircle, XCircle, AlertTriangle, RefreshCw } from 'lucide-react';
import { getOptimizationSuggestions, applySuggestion } from '../api/client';

const severityColors = {
  critical: { bg: 'bg-red-500/10', border: 'border-red-500/20', text: 'text-red-400', badge: 'badge-error' },
  high: { bg: 'bg-amber-500/10', border: 'border-amber-500/20', text: 'text-amber-400', badge: 'badge-warning' },
  medium: { bg: 'bg-neuro-500/10', border: 'border-neuro-500/20', text: 'text-neuro-400', badge: 'badge-info' },
  low: { bg: 'bg-emerald-500/10', border: 'border-emerald-500/20', text: 'text-emerald-400', badge: 'badge-success' },
};

export default function OptimizerPage() {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [applying, setApplying] = useState(null);
  const [results, setResults] = useState({});

  const fetchSuggestions = async () => {
    setLoading(true);
    try {
      const res = await getOptimizationSuggestions();
      setSuggestions(res.data);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { fetchSuggestions(); }, []);

  const handleApply = async (id) => {
    setApplying(id);
    try {
      const res = await applySuggestion(id);
      setResults(prev => ({ ...prev, [id]: res.data }));
    } catch (e) { setResults(prev => ({ ...prev, [id]: { success: false, message: 'Failed to apply' } })); }
    setApplying(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Auto-Optimizer</h1>
          <p className="text-gray-500 text-sm mt-1">AI-powered system optimization suggestions</p>
        </div>
        <button onClick={fetchSuggestions} className="btn-primary flex items-center gap-2">
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} /> Scan System
        </button>
      </div>

      {suggestions.length === 0 && !loading && (
        <div className="glass-card p-12 text-center">
          <CheckCircle className="w-16 h-16 text-emerald-500/50 mx-auto mb-4" />
          <p className="text-xl font-semibold text-white mb-2">System is Optimized!</p>
          <p className="text-gray-400">No optimization suggestions at this time. Your system is running efficiently.</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {suggestions.map(s => {
          const colors = severityColors[s.severity] || severityColors.medium;
          const result = results[s.id];
          return (
            <div key={s.id} className={`glass-card p-6 animate-slide-up ${colors.border} border`}>
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className={`w-10 h-10 rounded-xl ${colors.bg} flex items-center justify-center`}>
                    {s.severity === 'critical' ? <AlertTriangle className={`w-5 h-5 ${colors.text}`} /> :
                     <Zap className={`w-5 h-5 ${colors.text}`} />}
                  </div>
                  <div>
                    <h3 className="font-semibold text-white text-sm">{s.title}</h3>
                    <span className={`badge ${colors.badge} mt-1`}>{s.severity.toUpperCase()}</span>
                  </div>
                </div>
                <span className="badge badge-info">{s.category}</span>
              </div>

              <p className="text-sm text-gray-400 mb-3">{s.description}</p>
              <p className="text-xs text-gray-500 mb-4"><span className="text-gray-400 font-medium">Impact:</span> {s.impact}</p>
              <p className="text-xs text-gray-500 mb-4"><span className="text-gray-400 font-medium">Action:</span> {s.action}</p>

              {result ? (
                <div className={`rounded-lg p-3 text-sm flex items-center gap-2 ${result.success ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
                  {result.success ? <CheckCircle className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
                  {result.message}
                </div>
              ) : s.auto_fixable ? (
                <button onClick={() => handleApply(s.id)} disabled={applying === s.id}
                  className="btn-primary text-sm w-full flex items-center justify-center gap-2">
                  {applying === s.id ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Zap className="w-4 h-4" />}
                  Apply Fix
                </button>
              ) : (
                <p className="text-xs text-gray-600 text-center py-2">Manual action required</p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
