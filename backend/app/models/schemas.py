"""
NeuroSys OS Toolkit - Pydantic Schemas
All request/response models for the API.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


# ─── System Metrics ───────────────────────────────────────────────

class CpuMetrics(BaseModel):
    percent: float = Field(..., description="Overall CPU usage percentage")
    per_cpu: List[float] = Field(default_factory=list, description="Per-core usage")
    frequency_mhz: Optional[float] = None
    core_count: int = 0
    logical_count: int = 0


class MemoryMetrics(BaseModel):
    total_gb: float
    used_gb: float
    available_gb: float
    percent: float
    swap_total_gb: float = 0.0
    swap_used_gb: float = 0.0
    swap_percent: float = 0.0


class DiskMetrics(BaseModel):
    device: str
    mountpoint: str
    total_gb: float
    used_gb: float
    free_gb: float
    percent: float


class NetworkMetrics(BaseModel):
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    bytes_sent_rate: float = 0.0  # bytes/sec
    bytes_recv_rate: float = 0.0  # bytes/sec


class SystemMetrics(BaseModel):
    timestamp: datetime
    cpu: CpuMetrics
    memory: MemoryMetrics
    disks: List[DiskMetrics]
    network: NetworkMetrics
    uptime_seconds: float = 0.0
    boot_time: Optional[datetime] = None


class SystemInfo(BaseModel):
    hostname: str
    os_name: str
    os_version: str
    architecture: str
    processor: str
    python_version: str
    uptime_formatted: str
    boot_time: str


class MetricsHistory(BaseModel):
    timestamps: List[str]
    cpu_values: List[float]
    memory_values: List[float]
    network_sent_rates: List[float]
    network_recv_rates: List[float]


# ─── Process Management ──────────────────────────────────────────

class ProcessStatus(str, Enum):
    RUNNING = "running"
    SLEEPING = "sleeping"
    STOPPED = "stopped"
    ZOMBIE = "zombie"
    UNKNOWN = "unknown"


class ProcessInfo(BaseModel):
    pid: int
    name: str
    status: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    username: Optional[str] = None
    create_time: Optional[str] = None
    num_threads: int = 0
    command: Optional[str] = None


class ProcessListResponse(BaseModel):
    processes: List[ProcessInfo]
    total_count: int
    timestamp: datetime


class ProcessKillResponse(BaseModel):
    success: bool
    pid: int
    message: str


# ─── AI Command Interpreter ──────────────────────────────────────

class AICommandRequest(BaseModel):
    query: str = Field(..., description="Natural language command", min_length=1, max_length=500)


class AICommandInterpretation(BaseModel):
    original_query: str
    interpreted_command: str
    description: str
    category: str
    confidence: float
    is_safe: bool
    warning: Optional[str] = None


class AICommandResult(BaseModel):
    interpretation: AICommandInterpretation
    output: Optional[str] = None
    error: Optional[str] = None
    executed: bool = False
    execution_time_ms: float = 0.0


class AISamplePrompt(BaseModel):
    category: str
    prompt: str
    description: str


# ─── Resource Prediction ─────────────────────────────────────────

class ResourcePrediction(BaseModel):
    metric: str
    current_value: float
    predicted_values: List[float]
    prediction_timestamps: List[str]
    trend: str  # "increasing", "decreasing", "stable"
    alert: Optional[str] = None
    confidence: float


# ─── Auto-Optimization ───────────────────────────────────────────

class OptimizationSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OptimizationSuggestion(BaseModel):
    id: str
    title: str
    description: str
    category: str
    severity: OptimizationSeverity
    impact: str
    action: str
    auto_fixable: bool = False
    details: Optional[Dict[str, Any]] = None


class OptimizationResult(BaseModel):
    suggestion_id: str
    success: bool
    message: str
    before_value: Optional[str] = None
    after_value: Optional[str] = None


# ─── File System Analyzer ────────────────────────────────────────

class ScanRequest(BaseModel):
    path: str = Field(..., description="Directory path to scan")
    max_depth: int = Field(default=5, ge=1, le=10)


class DuplicateGroup(BaseModel):
    hash: str
    size_bytes: int
    size_formatted: str
    files: List[str]
    wasted_bytes: int


class JunkFile(BaseModel):
    path: str
    size_bytes: int
    size_formatted: str
    reason: str


class FileSystemSummary(BaseModel):
    total_files: int
    total_dirs: int
    total_size_bytes: int
    total_size_formatted: str
    largest_files: List[Dict[str, Any]]
    extension_breakdown: Dict[str, Dict[str, Any]]
    scan_path: str
    scan_duration_ms: float


class DuplicateResponse(BaseModel):
    groups: List[DuplicateGroup]
    total_wasted_bytes: int
    total_wasted_formatted: str
    total_duplicate_files: int


class JunkResponse(BaseModel):
    files: List[JunkFile]
    total_junk_bytes: int
    total_junk_formatted: str
    total_junk_files: int


# ─── Log Analyzer ────────────────────────────────────────────────

class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogEntry(BaseModel):
    timestamp: Optional[str] = None
    level: str
    source: str
    message: str
    line_number: int = 0


class LogAnalysis(BaseModel):
    total_entries: int
    error_count: int
    warning_count: int
    info_count: int
    entries: List[LogEntry]
    ai_summary: str
    patterns: List[Dict[str, Any]]
    recommendations: List[str]


# ─── Generic ─────────────────────────────────────────────────────

class HealthCheck(BaseModel):
    status: str = "healthy"
    version: str
    uptime: str
