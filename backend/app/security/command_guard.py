"""
NeuroSys OS Toolkit - Command Guard
Security layer that validates and sanitizes all commands before execution.
Uses a whitelist approach — only explicitly allowed commands can run.
"""

import re
import shlex
from typing import Tuple
from app.config import settings


class CommandGuard:
    """Validates and sanitizes system commands for safe execution."""

    # Dangerous patterns that should NEVER be executed
    DANGEROUS_PATTERNS = [
        r"rm\s+(-rf|--recursive).*(/|\*)",
        r"del\s+/[fFsSpPqQ]",
        r"format\s+[a-zA-Z]:",
        r"mkfs\.",
        r"dd\s+if=",
        r">\s*/dev/sd",
        r"chmod\s+777\s+/",
        r"chown\s+.*\s+/",
        r":\(\)\s*\{",  # fork bomb
        r"shutdown",
        r"reboot",
        r"halt",
        r"poweroff",
        r"init\s+[06]",
        r"reg\s+(delete|add)",
        r"net\s+(user|localgroup)",
        r"takeown",
        r"icacls\s+.*(/grant|/deny|/remove)",
        r"schtasks\s+/create",
        r"sc\s+(delete|stop|config)",
        r"wmic\s+.*delete",
        r"powershell.*-Enc",  # encoded commands
        r"Invoke-Expression",
        r"iex\s*\(",
        r"wget.*\|\s*(bash|sh|powershell)",
        r"curl.*\|\s*(bash|sh|powershell)",
    ]

    # Read-only commands that are always safe
    SAFE_COMMANDS = {
        # Windows
        "systeminfo", "hostname", "whoami", "ver", "date /t", "time /t",
        "ipconfig", "ipconfig /all",
        "netstat -an", "netstat -ano",
        "tasklist", "tasklist /v",
        "wmic cpu get name", "wmic os get caption",
        "wmic diskdrive get size", "wmic memorychip get capacity",
        # PowerShell read-only
        "powershell -Command Get-Process",
        "powershell -Command Get-Service",
        "powershell -Command Get-NetAdapter",
        "powershell -Command Get-Volume",
        "powershell -Command Get-Disk",
        "powershell -Command Get-NetTCPConnection",
        "powershell -Command Get-ComputerInfo",
        "powershell -Command Get-HotFix",
        # Linux
        "ps aux", "ps -ef", "top -bn1",
        "free -h", "free -m",
        "df -h", "df -i",
        "uname -a", "uptime", "w", "who",
        "ifconfig", "ip addr", "ip route",
        "cat /proc/cpuinfo", "cat /proc/meminfo",
        "lsblk", "lsusb", "lspci",
    }

    def __init__(self):
        self._compiled_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.DANGEROUS_PATTERNS
        ]

    def validate_command(self, command: str) -> Tuple[bool, str]:
        """
        Validate a command for safety.
        Returns (is_safe, reason).
        """
        if not command or not command.strip():
            return False, "Empty command"

        command = command.strip()

        # Check against dangerous patterns
        for pattern in self._compiled_patterns:
            if pattern.search(command):
                return False, f"Command matches dangerous pattern and has been blocked"

        # Check against blocked commands list
        cmd_lower = command.lower().strip()
        for blocked in settings.BLOCKED_COMMANDS:
            if blocked.lower() in cmd_lower:
                return False, f"Command contains blocked operation: {blocked}"

        # Check if it matches an allowed prefix
        is_allowed = False
        for prefix in settings.ALLOWED_COMMAND_PREFIXES:
            if cmd_lower.startswith(prefix.lower()):
                is_allowed = True
                break

        # Also check exact safe commands
        if not is_allowed:
            for safe_cmd in self.SAFE_COMMANDS:
                if cmd_lower == safe_cmd.lower() or cmd_lower.startswith(safe_cmd.lower()):
                    is_allowed = True
                    break

        if not is_allowed:
            return False, "Command not in allowed list. Only read-only system commands are permitted."

        return True, "Command is safe to execute"

    def sanitize_command(self, command: str) -> str:
        """Sanitize command string to prevent injection."""
        # Remove any command chaining operators
        sanitized = re.sub(r'[;&|`$]', '', command)
        # Remove redirection operators
        sanitized = re.sub(r'[><]', '', sanitized)
        # Remove backticks and subshell operators
        sanitized = re.sub(r'[\`\$\(\)]', '', sanitized)
        return sanitized.strip()

    def is_exact_safe_command(self, command: str) -> bool:
        """Check if command is in the exact safe commands list."""
        return command.strip().lower() in {c.lower() for c in self.SAFE_COMMANDS}


# Singleton instance
command_guard = CommandGuard()
