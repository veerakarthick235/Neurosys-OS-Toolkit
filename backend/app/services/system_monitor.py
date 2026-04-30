"""
NeuroSys OS Toolkit - System Monitor Service
Real-time system metrics collection using psutil.
Maintains a circular buffer of historical data for charting.
"""

import time
import platform
import psutil
from datetime import datetime, timezone
from collections import deque
from typing import List, Dict, Optional

from app.config import settings
from app.models.schemas import (
    SystemMetrics, CpuMetrics, MemoryMetrics,
    DiskMetrics, NetworkMetrics, SystemInfo, MetricsHistory
)


class SystemMonitor:
    """Collects and stores system metrics using psutil."""

    def __init__(self):
        self._history_size = settings.METRICS_HISTORY_SIZE
        self._cpu_history: deque = deque(maxlen=self._history_size)
        self._memory_history: deque = deque(maxlen=self._history_size)
        self._network_sent_history: deque = deque(maxlen=self._history_size)
        self._network_recv_history: deque = deque(maxlen=self._history_size)
        self._timestamp_history: deque = deque(maxlen=self._history_size)
        self._last_net_io = psutil.net_io_counters()
        self._last_net_time = time.time()
        self._start_time = time.time()

    def get_cpu_metrics(self) -> CpuMetrics:
        """Get current CPU metrics."""
        cpu_freq = psutil.cpu_freq()
        return CpuMetrics(
            percent=psutil.cpu_percent(interval=0),
            per_cpu=psutil.cpu_percent(interval=0, percpu=True),
            frequency_mhz=cpu_freq.current if cpu_freq else None,
            core_count=psutil.cpu_count(logical=False) or 0,
            logical_count=psutil.cpu_count(logical=True) or 0,
        )

    def get_memory_metrics(self) -> MemoryMetrics:
        """Get current memory metrics."""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return MemoryMetrics(
            total_gb=round(mem.total / (1024 ** 3), 2),
            used_gb=round(mem.used / (1024 ** 3), 2),
            available_gb=round(mem.available / (1024 ** 3), 2),
            percent=mem.percent,
            swap_total_gb=round(swap.total / (1024 ** 3), 2),
            swap_used_gb=round(swap.used / (1024 ** 3), 2),
            swap_percent=swap.percent,
        )

    def get_disk_metrics(self) -> List[DiskMetrics]:
        """Get disk usage for all partitions."""
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append(DiskMetrics(
                    device=partition.device,
                    mountpoint=partition.mountpoint,
                    total_gb=round(usage.total / (1024 ** 3), 2),
                    used_gb=round(usage.used / (1024 ** 3), 2),
                    free_gb=round(usage.free / (1024 ** 3), 2),
                    percent=usage.percent,
                ))
            except (PermissionError, OSError):
                continue
        return disks

    def get_network_metrics(self) -> NetworkMetrics:
        """Get network I/O metrics with rate calculation."""
        current_io = psutil.net_io_counters()
        current_time = time.time()
        elapsed = current_time - self._last_net_time

        if elapsed > 0:
            sent_rate = (current_io.bytes_sent - self._last_net_io.bytes_sent) / elapsed
            recv_rate = (current_io.bytes_recv - self._last_net_io.bytes_recv) / elapsed
        else:
            sent_rate = 0.0
            recv_rate = 0.0

        self._last_net_io = current_io
        self._last_net_time = current_time

        return NetworkMetrics(
            bytes_sent=current_io.bytes_sent,
            bytes_recv=current_io.bytes_recv,
            packets_sent=current_io.packets_sent,
            packets_recv=current_io.packets_recv,
            bytes_sent_rate=round(sent_rate, 2),
            bytes_recv_rate=round(recv_rate, 2),
        )

    def get_all_metrics(self) -> SystemMetrics:
        """Get all system metrics at once."""
        now = datetime.now(timezone.utc)
        cpu = self.get_cpu_metrics()
        memory = self.get_memory_metrics()
        network = self.get_network_metrics()

        # Record in history
        self._timestamp_history.append(now.isoformat())
        self._cpu_history.append(cpu.percent)
        self._memory_history.append(memory.percent)
        self._network_sent_history.append(network.bytes_sent_rate)
        self._network_recv_history.append(network.bytes_recv_rate)

        boot = datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc)

        return SystemMetrics(
            timestamp=now,
            cpu=cpu,
            memory=memory,
            disks=self.get_disk_metrics(),
            network=network,
            uptime_seconds=time.time() - psutil.boot_time(),
            boot_time=boot,
        )

    def get_history(self) -> MetricsHistory:
        """Get historical metrics data for charts."""
        return MetricsHistory(
            timestamps=list(self._timestamp_history),
            cpu_values=list(self._cpu_history),
            memory_values=list(self._memory_history),
            network_sent_rates=list(self._network_sent_history),
            network_recv_rates=list(self._network_recv_history),
        )

    def get_system_info(self) -> SystemInfo:
        """Get static system information."""
        boot_ts = psutil.boot_time()
        uptime_secs = time.time() - boot_ts
        days = int(uptime_secs // 86400)
        hours = int((uptime_secs % 86400) // 3600)
        minutes = int((uptime_secs % 3600) // 60)

        return SystemInfo(
            hostname=platform.node(),
            os_name=platform.system(),
            os_version=platform.version(),
            architecture=platform.machine(),
            processor=platform.processor() or "Unknown",
            python_version=platform.python_version(),
            uptime_formatted=f"{days}d {hours}h {minutes}m",
            boot_time=datetime.fromtimestamp(boot_ts).strftime("%Y-%m-%d %H:%M:%S"),
        )


# Singleton instance
system_monitor = SystemMonitor()
