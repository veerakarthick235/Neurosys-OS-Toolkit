import { useState, useEffect } from 'react';
import { Send, Sparkles, Terminal, Clock, Shield, AlertTriangle } from 'lucide-react';
import { executeCommand, getSamplePrompts } from '../api/client';

export default function AICommandPage() {
  const [query, setQuery] = useState('');
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [prompts, setPrompts] = useState([]);

  useEffect(() => {
    getSamplePrompts().then(r => setPrompts(r.data)).catch(() => {});
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim() || loading) return;
    setLoading(true);
    try {
      const res = await executeCommand(query);
      setHistory(prev => [{ ...res.data, id: Date.now() }, ...prev]);
      setQuery('');
    } catch (e) {
      setHistory(prev => [{ id: Date.now(), interpretation: { original_query: query, interpreted_command: '', category: 'Error', confidence: 0, is_safe: false }, error: 'Failed to connect to server' }, ...prev]);
    }
    setLoading(false);
  };

  const handlePromptClick = (prompt) => { setQuery(prompt); };

  // Group prompts by category
  const groupedPrompts = prompts.reduce((acc, p) => {
    if (!acc[p.category]) acc[p.category] = [];
    acc[p.category].push(p);
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">AI Command Interpreter</h1>
        <p className="text-gray-500 text-sm mt-1">Type natural language commands — AI translates them to system operations</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Input */}
          <form onSubmit={handleSubmit} className="glass-card p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-neuro-500 to-cyan-400 flex items-center justify-center flex-shrink-0">
                <Terminal className="w-5 h-5 text-white" />
              </div>
              <input className="input-dark flex-1" placeholder="Ask me anything... e.g., 'Show my IP address'"
                value={query} onChange={e => setQuery(e.target.value)} />
              <button type="submit" disabled={loading} className="btn-primary flex items-center gap-2">
                {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Send className="w-4 h-4" />}
                Execute
              </button>
            </div>
          </form>

          {/* Results */}
          <div className="space-y-4">
            {history.length === 0 && (
              <div className="glass-card p-12 text-center">
                <Sparkles className="w-12 h-12 text-neuro-500/50 mx-auto mb-4" />
                <p className="text-gray-400">Type a command in natural language to get started</p>
                <p className="text-gray-600 text-sm mt-1">Try: "Show me system information" or "What's using the most CPU?"</p>
              </div>
            )}

            {history.map(item => (
              <div key={item.id} className="glass-card p-5 animate-slide-up">
                {/* Query */}
                <div className="flex items-start gap-3 mb-4">
                  <div className="w-8 h-8 rounded-lg bg-neuro-600/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Terminal className="w-4 h-4 text-neuro-400" />
                  </div>
                  <div>
                    <p className="text-white font-medium">{item.interpretation?.original_query}</p>
                    {item.interpretation?.interpreted_command && (
                      <p className="text-xs font-mono text-gray-500 mt-1 bg-surface-800 rounded px-2 py-1 inline-block">
                        → {item.interpretation.interpreted_command}
                      </p>
                    )}
                  </div>
                </div>

                {/* Meta */}
                <div className="flex items-center gap-3 mb-3 text-xs">
                  {item.interpretation?.category && (
                    <span className="badge badge-info">{item.interpretation.category}</span>
                  )}
                  {item.interpretation?.confidence > 0 && (
                    <span className="text-gray-500">Confidence: {(item.interpretation.confidence * 100).toFixed(0)}%</span>
                  )}
                  {item.interpretation?.is_safe ? (
                    <span className="flex items-center gap-1 text-emerald-400"><Shield className="w-3 h-3" /> Safe</span>
                  ) : (
                    <span className="flex items-center gap-1 text-amber-400"><AlertTriangle className="w-3 h-3" /> {item.interpretation?.warning || 'Blocked'}</span>
                  )}
                  {item.execution_time_ms > 0 && (
                    <span className="flex items-center gap-1 text-gray-500"><Clock className="w-3 h-3" /> {item.execution_time_ms.toFixed(0)}ms</span>
                  )}
                </div>

                {/* Output */}
                {item.output && (
                  <pre className="bg-surface-900 rounded-xl p-4 text-xs text-gray-300 font-mono overflow-x-auto max-h-64 overflow-y-auto whitespace-pre-wrap border border-white/5">
                    {item.output}
                  </pre>
                )}
                {item.error && !item.output && (
                  <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-sm text-red-400">
                    {item.error}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Sidebar: Sample Prompts */}
        <div className="space-y-4">
          <div className="glass-card p-5">
            <h3 className="text-sm font-semibold text-gray-300 mb-4 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-neuro-400" /> Sample Prompts
            </h3>
            <div className="space-y-4">
              {Object.entries(groupedPrompts).map(([cat, items]) => (
                <div key={cat}>
                  <p className="text-xs uppercase tracking-wider text-gray-600 font-semibold mb-2">{cat}</p>
                  <div className="space-y-1.5">
                    {items.map((p, i) => (
                      <button key={i} onClick={() => handlePromptClick(p.prompt)}
                        className="w-full text-left px-3 py-2 rounded-lg text-sm text-gray-400 hover:bg-surface-600 hover:text-white transition-colors">
                        {p.prompt}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
