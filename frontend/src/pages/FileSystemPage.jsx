import { useState } from 'react';
import { FolderSearch, ScanLine, Copy, Trash2, HardDrive, FileText } from 'lucide-react';
import { scanDirectory, getDuplicates, getJunkFiles } from '../api/client';

export default function FileSystemPage() {
  const [path, setPath] = useState('.');
  const [summary, setSummary] = useState(null);
  const [duplicates, setDuplicates] = useState(null);
  const [junk, setJunk] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('summary');

  const handleScan = async () => {
    setLoading(true);
    try {
      const scanRes = await scanDirectory(path);
      setSummary(scanRes.data);
      const [dupRes, junkRes] = await Promise.all([getDuplicates(), getJunkFiles()]);
      setDuplicates(dupRes.data);
      setJunk(junkRes.data);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const tabs = [
    { key: 'summary', label: 'Summary', icon: HardDrive },
    { key: 'duplicates', label: `Duplicates${duplicates ? ` (${duplicates.total_duplicate_files})` : ''}`, icon: Copy },
    { key: 'junk', label: `Junk${junk ? ` (${junk.total_junk_files})` : ''}`, icon: Trash2 },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">File System Analyzer</h1>
        <p className="text-gray-500 text-sm mt-1">Scan directories for duplicates, junk files, and disk usage</p>
      </div>

      {/* Scan Input */}
      <div className="glass-card p-4 flex items-center gap-4">
        <FolderSearch className="w-5 h-5 text-neuro-400 flex-shrink-0" />
        <input className="input-dark flex-1" placeholder="Enter directory path to scan..."
          value={path} onChange={e => setPath(e.target.value)} />
        <button onClick={handleScan} disabled={loading} className="btn-primary flex items-center gap-2">
          {loading ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <ScanLine className="w-4 h-4" />}
          Scan
        </button>
      </div>

      {summary && (
        <>
          {/* Tabs */}
          <div className="flex gap-2 border-b border-white/5 pb-2">
            {tabs.map(t => (
              <button key={t.key} onClick={() => setActiveTab(t.key)}
                className={`flex items-center gap-2 px-4 py-2 rounded-t-lg text-sm font-medium transition-colors ${
                  activeTab === t.key ? 'bg-surface-700 text-neuro-400 border-b-2 border-neuro-500' : 'text-gray-500 hover:text-gray-300'
                }`}>
                <t.icon className="w-4 h-4" /> {t.label}
              </button>
            ))}
          </div>

          {/* Summary Tab */}
          {activeTab === 'summary' && (
            <div className="space-y-6 animate-fade-in">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatCard label="Total Files" value={summary.total_files.toLocaleString()} />
                <StatCard label="Total Directories" value={summary.total_dirs.toLocaleString()} />
                <StatCard label="Total Size" value={summary.total_size_formatted} />
                <StatCard label="Scan Time" value={`${summary.scan_duration_ms.toFixed(0)}ms`} />
              </div>

              {/* Largest Files */}
              <div className="glass-card p-5">
                <h3 className="text-sm font-semibold text-gray-300 mb-4">Largest Files</h3>
                <div className="space-y-2">
                  {summary.largest_files?.map((f, i) => (
                    <div key={i} className="flex items-center justify-between py-2 px-3 bg-surface-800/50 rounded-lg">
                      <div className="flex items-center gap-3 min-w-0">
                        <FileText className="w-4 h-4 text-gray-500 flex-shrink-0" />
                        <span className="text-sm text-gray-300 truncate">{f.path}</span>
                      </div>
                      <span className="text-sm font-medium text-neuro-400 flex-shrink-0 ml-4">{f.size_formatted}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Extensions */}
              {summary.extension_breakdown && (
                <div className="glass-card p-5">
                  <h3 className="text-sm font-semibold text-gray-300 mb-4">File Types Breakdown</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {Object.entries(summary.extension_breakdown).sort((a, b) => b[1].total_size - a[1].total_size).slice(0, 12).map(([ext, info]) => (
                      <div key={ext} className="bg-surface-800/50 rounded-lg p-3 border border-white/5">
                        <p className="text-sm font-mono text-neuro-400">{ext}</p>
                        <p className="text-xs text-gray-500">{info.count} files · {info.total_size_formatted}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Duplicates Tab */}
          {activeTab === 'duplicates' && duplicates && (
            <div className="space-y-4 animate-fade-in">
              <div className="glass-card p-4 flex items-center justify-between">
                <p className="text-sm text-gray-400">{duplicates.total_duplicate_files} duplicate files found</p>
                <p className="text-sm font-medium text-amber-400">Wasted: {duplicates.total_wasted_formatted}</p>
              </div>
              {duplicates.groups?.map((g, i) => (
                <div key={i} className="glass-card p-5">
                  <div className="flex items-center justify-between mb-3">
                    <span className="badge badge-warning">{g.size_formatted} each</span>
                    <span className="text-xs text-gray-500">MD5: {g.hash.substring(0, 12)}...</span>
                  </div>
                  <div className="space-y-1.5">
                    {g.files.map((f, j) => (
                      <p key={j} className="text-sm text-gray-400 font-mono bg-surface-800/50 rounded px-3 py-1.5 truncate">{f}</p>
                    ))}
                  </div>
                </div>
              ))}
              {duplicates.groups?.length === 0 && (
                <div className="glass-card p-8 text-center text-gray-500">No duplicate files found</div>
              )}
            </div>
          )}

          {/* Junk Tab */}
          {activeTab === 'junk' && junk && (
            <div className="space-y-4 animate-fade-in">
              <div className="glass-card p-4 flex items-center justify-between">
                <p className="text-sm text-gray-400">{junk.total_junk_files} junk files found</p>
                <p className="text-sm font-medium text-amber-400">Total: {junk.total_junk_formatted}</p>
              </div>
              <div className="glass-card overflow-hidden">
                <table className="w-full text-sm">
                  <thead><tr className="border-b border-white/5">
                    <th className="text-left px-4 py-3 text-gray-400 font-medium text-xs">File</th>
                    <th className="text-left px-4 py-3 text-gray-400 font-medium text-xs">Size</th>
                    <th className="text-left px-4 py-3 text-gray-400 font-medium text-xs">Reason</th>
                  </tr></thead>
                  <tbody className="divide-y divide-white/5">
                    {junk.files?.map((f, i) => (
                      <tr key={i} className="hover:bg-surface-600/30">
                        <td className="px-4 py-2 text-gray-300 font-mono truncate max-w-[300px]">{f.path}</td>
                        <td className="px-4 py-2 text-gray-400">{f.size_formatted}</td>
                        <td className="px-4 py-2 text-gray-500 text-xs">{f.reason}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function StatCard({ label, value }) {
  return (
    <div className="glass-card p-4 text-center">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className="text-xl font-bold bg-gradient-to-r from-neuro-400 to-cyan-300 bg-clip-text text-transparent">{value}</p>
    </div>
  );
}
