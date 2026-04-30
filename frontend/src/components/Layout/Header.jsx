import { Wifi, WifiOff } from 'lucide-react';

export default function Header({ wsConnected }) {
  return (
    <header className="h-16 bg-surface-800/50 backdrop-blur-xl border-b border-white/5 flex items-center justify-between px-8">
      <div />
      <div className="flex items-center gap-4">
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium ${
          wsConnected
            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
            : 'bg-red-500/10 text-red-400 border border-red-500/20'
        }`}>
          {wsConnected ? <Wifi className="w-3.5 h-3.5" /> : <WifiOff className="w-3.5 h-3.5" />}
          {wsConnected ? 'Live' : 'Offline'}
        </div>
      </div>
    </header>
  );
}
