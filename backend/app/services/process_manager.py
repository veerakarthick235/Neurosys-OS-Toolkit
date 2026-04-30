"""
NeuroSys OS Toolkit - Process Manager Service
Manages system processes: listing, filtering, and controlled termination.
"""

import psutil
from datetime import datetime
from typing import List, Optional

from app.config import settings
from app.models.schemas import ProcessInfo, ProcessListResponse, ProcessKillResponse


class ProcessManager:
    """Manages system processes using psutil."""

    def get_all_processes(self, sort_by: str = "cpu", limit: int = 100) -> ProcessListResponse:
        """Get all running processes, sorted and limited."""
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent',
                                          'memory_percent', 'memory_info',
                                          'username', 'create_time', 'num_threads',
                                          'cmdline']):
            try:
                info = proc.info
                mem_info = info.get('memory_info')
                mem_mb = round(mem_info.rss / (1024 * 1024), 2) if mem_info else 0.0
                create_time = info.get('create_time')
                create_str = datetime.fromtimestamp(create_time).strftime(
                    "%Y-%m-%d %H:%M:%S") if create_time else None
                cmdline = info.get('cmdline')
                cmd_str = ' '.join(cmdline[:3]) if cmdline else None

                processes.append(ProcessInfo(
                    pid=info['pid'],
                    name=info.get('name', 'Unknown'),
                    status=info.get('status', 'unknown'),
                    cpu_percent=info.get('cpu_percent', 0.0) or 0.0,
                    memory_percent=round(info.get('memory_percent', 0.0) or 0.0, 2),
                    memory_mb=mem_mb,
                    username=info.get('username'),
                    create_time=create_str,
                    num_threads=info.get('num_threads', 0) or 0,
                    command=cmd_str,
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # Sort
        sort_key_map = {
            "cpu": lambda p: p.cpu_percent,
            "memory": lambda p: p.memory_percent,
            "pid": lambda p: p.pid,
            "name": lambda p: p.name.lower(),
        }
        sort_func = sort_key_map.get(sort_by, sort_key_map["cpu"])
        processes.sort(key=sort_func, reverse=(sort_by in ("cpu", "memory")))

        total = len(processes)
        if limit > 0:
            processes = processes[:limit]

        return ProcessListResponse(
            processes=processes,
            total_count=total,
            timestamp=datetime.utcnow(),
        )

    def get_top_processes(self, n: int = 10, by: str = "cpu") -> List[ProcessInfo]:
        """Get top N processes by CPU or memory usage."""
        result = self.get_all_processes(sort_by=by, limit=n)
        return result.processes

    def kill_process(self, pid: int) -> ProcessKillResponse:
        """Kill a process by PID with safety checks."""
        # Safety check: don't kill critical system processes
        if pid < settings.MIN_KILLABLE_PID:
            return ProcessKillResponse(
                success=False,
                pid=pid,
                message=f"Cannot kill system-critical process (PID < {settings.MIN_KILLABLE_PID})"
            )

        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()

            # Don't kill our own process
            if pid == psutil.Process().pid:
                return ProcessKillResponse(
                    success=False,
                    pid=pid,
                    message="Cannot kill the NeuroSys server process"
                )

            proc.terminate()

            # Wait up to 3 seconds for graceful termination
            try:
                proc.wait(timeout=3)
            except psutil.TimeoutExpired:
                proc.kill()  # Force kill if not terminated

            return ProcessKillResponse(
                success=True,
                pid=pid,
                message=f"Process '{proc_name}' (PID: {pid}) terminated successfully"
            )

        except psutil.NoSuchProcess:
            return ProcessKillResponse(
                success=False,
                pid=pid,
                message=f"Process with PID {pid} does not exist"
            )
        except psutil.AccessDenied:
            return ProcessKillResponse(
                success=False,
                pid=pid,
                message=f"Access denied: insufficient permissions to kill PID {pid}"
            )
        except Exception as e:
            return ProcessKillResponse(
                success=False,
                pid=pid,
                message=f"Error killing process: {str(e)}"
            )

    def search_processes(self, query: str) -> List[ProcessInfo]:
        """Search processes by name."""
        result = self.get_all_processes(sort_by="cpu", limit=0)
        query_lower = query.lower()
        return [p for p in result.processes if query_lower in p.name.lower()]


# Singleton instance
process_manager = ProcessManager()
