import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// ─── System ────────────────────────────────────
export const getSystemMetrics = () => api.get('/api/system/metrics');
export const getSystemHistory = () => api.get('/api/system/history');
export const getSystemInfo = () => api.get('/api/system/info');
export const getSystemPredictions = () => api.get('/api/system/predictions');

// ─── Processes ─────────────────────────────────
export const getProcesses = (sortBy = 'cpu', limit = 100) =>
  api.get(`/api/processes/?sort_by=${sortBy}&limit=${limit}`);
export const getTopProcesses = (n = 10, by = 'cpu') =>
  api.get(`/api/processes/top?n=${n}&by=${by}`);
export const searchProcesses = (q) =>
  api.get(`/api/processes/search?q=${q}`);
export const killProcess = (pid) =>
  api.post(`/api/processes/${pid}/kill`);

// ─── AI Commands ───────────────────────────────
export const interpretCommand = (query) =>
  api.post('/api/ai/interpret', { query });
export const executeCommand = (query) =>
  api.post('/api/ai/execute', { query });
export const getSamplePrompts = () =>
  api.get('/api/ai/prompts');

// ─── Optimizer ─────────────────────────────────
export const getOptimizationSuggestions = () =>
  api.get('/api/optimizer/suggestions');
export const applySuggestion = (id) =>
  api.post(`/api/optimizer/apply/${id}`);

// ─── File System ───────────────────────────────
export const scanDirectory = (path, maxDepth = 5) =>
  api.post('/api/filesystem/scan', { path, max_depth: maxDepth });
export const getDuplicates = () =>
  api.get('/api/filesystem/duplicates');
export const getJunkFiles = () =>
  api.get('/api/filesystem/junk');

// ─── Logs ──────────────────────────────────────
export const getSystemLogs = (maxLines = 100) =>
  api.get(`/api/logs/system?max_lines=${maxLines}`);
export const analyzeLogs = (content) =>
  api.post('/api/logs/analyze', { content });

// ─── WebSocket URL helper ──────────────────────
export const WS_METRICS_URL = 'ws://localhost:8000/ws/metrics';
export const WS_PROCESSES_URL = 'ws://localhost:8000/ws/processes';

export default api;
