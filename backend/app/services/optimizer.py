"""
NeuroSys OS Toolkit - Auto-Optimization Engine
Analyzes system state and provides optimization suggestions.
"""

import psutil
from typing import List
from app.models.schemas import OptimizationSuggestion, OptimizationSeverity, OptimizationResult


class Optimizer:
    def get_suggestions(self) -> List[OptimizationSuggestion]:
        suggestions = []
        suggestions.extend(self._check_high_cpu_processes())
        suggestions.extend(self._check_memory_pressure())
        suggestions.extend(self._check_disk_usage())
        suggestions.extend(self._check_zombie_processes())
        return suggestions

    def _check_high_cpu_processes(self) -> List[OptimizationSuggestion]:
        results = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                if (proc.info['cpu_percent'] or 0) > 50 and proc.info['pid'] > 100:
                    results.append(OptimizationSuggestion(
                        id=f"high_cpu_{proc.info['pid']}",
                        title=f"High CPU: {proc.info['name']}",
                        description=f"Process '{proc.info['name']}' (PID: {proc.info['pid']}) is using {proc.info['cpu_percent']:.1f}% CPU",
                        category="CPU", severity=OptimizationSeverity.HIGH,
                        impact="Reducing CPU load will improve system responsiveness",
                        action=f"Consider closing '{proc.info['name']}' or limiting its priority",
                        auto_fixable=False,
                        details={"pid": proc.info['pid'], "cpu_percent": proc.info['cpu_percent']}
                    ))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return results

    def _check_memory_pressure(self) -> List[OptimizationSuggestion]:
        mem = psutil.virtual_memory()
        results = []
        if mem.percent > 80:
            top_mem = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
                try:
                    if (proc.info['memory_percent'] or 0) > 2:
                        top_mem.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            top_mem.sort(key=lambda x: x.get('memory_percent', 0), reverse=True)
            names = ', '.join(p['name'] for p in top_mem[:5])
            results.append(OptimizationSuggestion(
                id="memory_pressure",
                title="High Memory Usage",
                description=f"System memory is at {mem.percent:.1f}%. Top consumers: {names}",
                category="Memory", severity=OptimizationSeverity.HIGH if mem.percent > 90 else OptimizationSeverity.MEDIUM,
                impact="Free up memory to prevent system slowdown and potential crashes",
                action="Close unnecessary applications or browser tabs",
                auto_fixable=False, details={"memory_percent": mem.percent, "top_processes": [p['name'] for p in top_mem[:5]]}
            ))
        return results

    def _check_disk_usage(self) -> List[OptimizationSuggestion]:
        results = []
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                if usage.percent > 85:
                    results.append(OptimizationSuggestion(
                        id=f"disk_{part.device.replace(':', '').replace('/', '_')}",
                        title=f"Low Disk Space: {part.mountpoint}",
                        description=f"Drive {part.mountpoint} is {usage.percent:.1f}% full ({usage.free / (1024**3):.1f} GB free)",
                        category="Storage", severity=OptimizationSeverity.CRITICAL if usage.percent > 95 else OptimizationSeverity.MEDIUM,
                        impact="Low disk space can cause system instability",
                        action="Use the File System Analyzer to find large/duplicate files",
                        auto_fixable=False, details={"mountpoint": part.mountpoint, "percent": usage.percent}
                    ))
            except (PermissionError, OSError):
                continue
        return results

    def _check_zombie_processes(self) -> List[OptimizationSuggestion]:
        zombies = []
        for proc in psutil.process_iter(['pid', 'name', 'status']):
            try:
                if proc.info['status'] == psutil.STATUS_ZOMBIE:
                    zombies.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        if zombies:
            return [OptimizationSuggestion(
                id="zombie_processes",
                title=f"{len(zombies)} Zombie Process(es) Detected",
                description=f"Found {len(zombies)} zombie processes that are consuming resources",
                category="Process", severity=OptimizationSeverity.LOW,
                impact="Zombie processes waste system resources",
                action="These processes can be safely terminated",
                auto_fixable=True, details={"zombie_pids": [z['pid'] for z in zombies]}
            )]
        return []

    def apply_suggestion(self, suggestion_id: str) -> OptimizationResult:
        if suggestion_id == "zombie_processes":
            killed = 0
            for proc in psutil.process_iter(['pid', 'status']):
                try:
                    if proc.info['status'] == psutil.STATUS_ZOMBIE:
                        psutil.Process(proc.info['pid']).kill()
                        killed += 1
                except Exception:
                    continue
            return OptimizationResult(suggestion_id=suggestion_id, success=True,
                message=f"Cleaned up {killed} zombie processes")
        return OptimizationResult(suggestion_id=suggestion_id, success=False,
            message="This optimization requires manual action")

optimizer = Optimizer()
