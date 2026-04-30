"""
NeuroSys OS Toolkit - Configuration
Central configuration management with environment variable support.
"""

from typing import List, Set
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = "NeuroSys OS Toolkit"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

    # Monitoring
    METRICS_HISTORY_SIZE: int = 60  # Keep last 60 data points
    METRICS_INTERVAL: float = 1.0  # Seconds between metric snapshots
    PROCESS_UPDATE_INTERVAL: float = 2.0  # Seconds between process list updates

    # Security
    MIN_KILLABLE_PID: int = 100  # Don't allow killing system-critical processes
    BLOCKED_COMMANDS: Set[str] = {
        "rm -rf /", "rm -rf /*", "del /f /s /q c:\\",
        "format", "mkfs", "dd if=", "shutdown", "reboot",
        "halt", "poweroff", "init 0", "init 6",
        ":(){:|:&};:", "fork bomb",
        "reg delete", "reg add",
        "net user", "net localgroup",
        "takeown", "icacls",
    }

    ALLOWED_COMMAND_PREFIXES: Set[str] = {
        "systeminfo", "tasklist", "wmic", "ipconfig",
        "netstat", "ping", "tracert", "nslookup",
        "dir", "type", "findstr", "hostname",
        "whoami", "date", "time", "ver",
        "powershell -Command Get-Process",
        "powershell -Command Get-Service",
        "powershell -Command Get-NetAdapter",
        "powershell -Command Get-Disk",
        "powershell -Command Get-Volume",
        # Linux equivalents
        "ps", "top", "htop", "free", "df",
        "ls", "cat", "grep", "uname", "uptime",
        "ifconfig", "ip addr", "who", "w",
    }

    # File System Analyzer
    JUNK_PATTERNS: List[str] = [
        "*.tmp", "*.temp", "*.log", "*.bak", "*.old",
        "*.swp", "*.swo", "~*", "thumbs.db", "desktop.ini",
        ".ds_store", "*.pyc", "__pycache__",
        "*.cache", "*.crdownload", "*.partial",
    ]
    MAX_SCAN_DEPTH: int = 5
    MAX_SCAN_FILES: int = 10000

    # AI Engine
    AI_CONFIDENCE_THRESHOLD: float = 0.6

    class Config:
        env_prefix = "NEUROSYS_"
        case_sensitive = False


settings = Settings()
