"""
NeuroSys OS Toolkit - WebSocket Handler
Provides real-time system metrics and process updates via WebSocket.
"""

import asyncio
import json
from typing import List
from fastapi import WebSocket, WebSocketDisconnect
from app.services.system_monitor import system_monitor
from app.services.process_manager import process_manager
from app.config import settings


class ConnectionManager:
    """Manages active WebSocket connections."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for conn in self.active_connections:
            try:
                await conn.send_json(message)
            except Exception:
                disconnected.append(conn)
        for conn in disconnected:
            self.disconnect(conn)


manager = ConnectionManager()


async def metrics_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time system metrics."""
    await manager.connect(websocket)
    try:
        while True:
            metrics = system_monitor.get_all_metrics()
            data = {
                "type": "metrics",
                "data": {
                    "timestamp": metrics.timestamp.isoformat(),
                    "cpu": {"percent": metrics.cpu.percent, "per_cpu": metrics.cpu.per_cpu},
                    "memory": {"percent": metrics.memory.percent, "used_gb": metrics.memory.used_gb,
                               "total_gb": metrics.memory.total_gb, "available_gb": metrics.memory.available_gb},
                    "network": {"sent_rate": metrics.network.bytes_sent_rate,
                                "recv_rate": metrics.network.bytes_recv_rate},
                    "disks": [{"mountpoint": d.mountpoint, "percent": d.percent} for d in metrics.disks],
                    "uptime": metrics.uptime_seconds,
                }
            }
            await websocket.send_json(data)
            await asyncio.sleep(settings.METRICS_INTERVAL)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)


async def processes_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time process updates."""
    await manager.connect(websocket)
    try:
        while True:
            proc_list = process_manager.get_all_processes(sort_by="cpu", limit=50)
            data = {
                "type": "processes",
                "data": {
                    "timestamp": proc_list.timestamp.isoformat(),
                    "total_count": proc_list.total_count,
                    "processes": [
                        {"pid": p.pid, "name": p.name, "cpu_percent": p.cpu_percent,
                         "memory_percent": p.memory_percent, "memory_mb": p.memory_mb,
                         "status": p.status, "username": p.username}
                        for p in proc_list.processes
                    ]
                }
            }
            await websocket.send_json(data)
            await asyncio.sleep(settings.PROCESS_UPDATE_INTERVAL)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
