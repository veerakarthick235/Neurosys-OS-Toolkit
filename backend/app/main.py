"""
NeuroSys OS Toolkit - FastAPI Application Entry Point
"""

import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import system, processes, ai_commands, optimizer, filesystem, logs
from app.api.websocket import metrics_websocket, processes_websocket

# ─── App Initialization ──────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered OS Utility System — Real-time monitoring, intelligent command execution, and system optimization.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS ─────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────

app.include_router(system.router)
app.include_router(processes.router)
app.include_router(ai_commands.router)
app.include_router(optimizer.router)
app.include_router(filesystem.router)
app.include_router(logs.router)

# ─── WebSocket Endpoints ─────────────────────────────────────────

app.websocket("/ws/metrics")(metrics_websocket)
app.websocket("/ws/processes")(processes_websocket)

# ─── Startup ──────────────────────────────────────────────────────

_start_time = time.time()

@app.get("/", tags=["Health"])
async def root():
    uptime = time.time() - _start_time
    mins = int(uptime // 60)
    secs = int(uptime % 60)
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "uptime": f"{mins}m {secs}s",
        "docs": "/docs",
    }

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
