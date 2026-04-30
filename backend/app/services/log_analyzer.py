"""
NeuroSys OS Toolkit - Log Analyzer
Parses system logs and provides AI-style explanations for errors.
"""

import re
import os
import platform
from typing import List, Dict
from datetime import datetime
from app.models.schemas import LogEntry, LogAnalysis


# Common error patterns with human-readable explanations
ERROR_PATTERNS = {
    r"out of memory|oom|cannot allocate": {
        "explanation": "The system ran out of available memory (RAM). A process tried to allocate more memory than was available.",
        "recommendation": "Close unused applications, increase virtual memory/swap, or add more RAM."
    },
    r"permission denied|access denied|unauthorized": {
        "explanation": "A process or user attempted to access a resource without sufficient privileges.",
        "recommendation": "Check file permissions, run as administrator if needed, or verify user access rights."
    },
    r"disk full|no space left|insufficient disk": {
        "explanation": "The disk partition has no remaining free space for write operations.",
        "recommendation": "Use the File System Analyzer to find and remove large/duplicate files."
    },
    r"connection refused|econnrefused": {
        "explanation": "A network connection attempt was rejected by the target host, likely because no service is listening on that port.",
        "recommendation": "Verify the target service is running and check firewall rules."
    },
    r"timeout|timed out|deadline exceeded": {
        "explanation": "An operation took longer than the allowed time limit to complete.",
        "recommendation": "Check network connectivity, system load, or increase timeout values."
    },
    r"segmentation fault|segfault|sigsegv": {
        "explanation": "A program tried to access memory it doesn't have permission to access, causing a crash.",
        "recommendation": "Update the application, check for known bugs, or report the issue to the developer."
    },
    r"file not found|no such file|enoent": {
        "explanation": "The system tried to access a file or directory that doesn't exist at the specified path.",
        "recommendation": "Verify the file path, check if the file was moved or deleted."
    },
    r"cpu.*100%|cpu.*spike|high cpu": {
        "explanation": "CPU utilization reached maximum capacity, potentially causing system slowdown.",
        "recommendation": "Identify the high-CPU process using the Process Monitor and consider terminating it."
    },
    r"service.*failed|service.*stopped|service.*crash": {
        "explanation": "A system service encountered an error and stopped running.",
        "recommendation": "Check service logs for details, try restarting the service, or investigate dependencies."
    },
    r"authentication.*fail|login.*fail|invalid.*credentials": {
        "explanation": "An authentication attempt failed due to incorrect credentials or account issues.",
        "recommendation": "Verify credentials, check for account lockouts, review security logs for brute force attempts."
    },
}


class LogAnalyzer:
    def _parse_log_line(self, line: str, line_num: int) -> LogEntry:
        level = "info"
        level_patterns = [
            (r'\b(ERROR|FATAL|CRITICAL)\b', "error"),
            (r'\b(WARN|WARNING)\b', "warning"),
            (r'\b(DEBUG|TRACE)\b', "debug"),
            (r'\b(INFO)\b', "info"),
        ]
        for pattern, lvl in level_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                level = lvl
                break

        # Try to extract timestamp
        ts_match = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2}[\sT]\d{2}:\d{2}:\d{2})', line)
        timestamp = ts_match.group(1) if ts_match else None

        return LogEntry(timestamp=timestamp, level=level, source="log", message=line.strip(), line_number=line_num)

    def analyze_log_content(self, content: str) -> LogAnalysis:
        lines = content.strip().split('\n')
        entries = [self._parse_log_line(line, i + 1) for i, line in enumerate(lines) if line.strip()]

        error_count = sum(1 for e in entries if e.level == "error")
        warning_count = sum(1 for e in entries if e.level == "warning")
        info_count = sum(1 for e in entries if e.level == "info")

        # Pattern detection
        patterns = []
        full_text = content.lower()
        for pattern, info in ERROR_PATTERNS.items():
            matches = re.findall(pattern, full_text)
            if matches:
                patterns.append({
                    "pattern": pattern,
                    "count": len(matches),
                    "explanation": info["explanation"],
                    "recommendation": info["recommendation"]
                })

        # Generate AI summary
        summary_parts = [f"Analyzed {len(entries)} log entries."]
        if error_count:
            summary_parts.append(f"Found {error_count} errors that need attention.")
        if warning_count:
            summary_parts.append(f"Found {warning_count} warnings to review.")
        if patterns:
            summary_parts.append(f"Detected {len(patterns)} known issue pattern(s).")
        if not error_count and not warning_count:
            summary_parts.append("No critical issues detected — system appears healthy.")

        recommendations = [p["recommendation"] for p in patterns]
        if error_count > 10:
            recommendations.append("High error rate detected — investigate root cause urgently.")

        return LogAnalysis(
            total_entries=len(entries), error_count=error_count,
            warning_count=warning_count, info_count=info_count,
            entries=entries[:200], ai_summary=" ".join(summary_parts),
            patterns=patterns, recommendations=recommendations or ["No specific recommendations — logs look clean."]
        )

    def get_system_logs(self, max_lines: int = 100) -> LogAnalysis:
        """Read system logs based on OS."""
        content = ""
        if platform.system() == "Windows":
            try:
                import subprocess
                result = subprocess.run(
                    ['powershell', '-Command',
                     f'Get-EventLog -LogName System -Newest {max_lines} | Format-List TimeGenerated,EntryType,Source,Message'],
                    capture_output=True, text=True, timeout=15
                )
                content = result.stdout if result.stdout else "No system log entries found."
            except Exception as e:
                content = f"ERROR: Could not read system logs: {str(e)}"
        else:
            log_paths = ['/var/log/syslog', '/var/log/messages', '/var/log/system.log']
            for lp in log_paths:
                if os.path.exists(lp):
                    try:
                        with open(lp, 'r', errors='ignore') as f:
                            lines = f.readlines()
                            content = ''.join(lines[-max_lines:])
                            break
                    except PermissionError:
                        content = f"ERROR: Permission denied reading {lp}"
            if not content:
                content = "INFO: No system log files found at standard locations."

        return self.analyze_log_content(content)

log_analyzer = LogAnalyzer()
