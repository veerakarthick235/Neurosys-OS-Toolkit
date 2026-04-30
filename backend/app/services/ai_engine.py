"""
NeuroSys OS Toolkit - AI Command Engine
Natural language to system command interpreter.
Uses pattern matching and keyword extraction (no external LLM required).
Architecture supports future LLM integration.
"""

import re
import subprocess
import time
import platform
from typing import List, Tuple, Optional

from app.config import settings
from app.models.schemas import (
    AICommandInterpretation, AICommandResult, AISamplePrompt
)
from app.security.command_guard import command_guard


class AIEngine:
    """
    Interprets natural language queries into system commands.
    Uses a rule-based approach with keyword matching and fuzzy intent detection.
    """

    def __init__(self):
        self._is_windows = platform.system() == "Windows"
        self._command_map = self._build_command_map()

    def _build_command_map(self) -> List[dict]:
        """Build the NL → command mapping rules."""
        win = self._is_windows

        return [
            # ─── System Information ───
            {
                "patterns": [r"system\s*info", r"about\s*(this|my)\s*(computer|system|machine)", r"what\s*(computer|os|system)"],
                "command": "systeminfo" if win else "uname -a",
                "description": "Display detailed system information",
                "category": "System Info",
            },
            {
                "patterns": [r"hostname", r"computer\s*name", r"what.*name.*computer", r"machine\s*name"],
                "command": "hostname",
                "description": "Show the computer's hostname",
                "category": "System Info",
            },
            {
                "patterns": [r"who\s*am\s*i", r"current\s*user", r"logged\s*in\s*as", r"username"],
                "command": "whoami",
                "description": "Show the currently logged in user",
                "category": "System Info",
            },
            {
                "patterns": [r"uptime", r"how\s*long.*running", r"system.*up.*since", r"boot\s*time"],
                "command": "powershell -Command Get-ComputerInfo | Select-Object OsUptime" if win else "uptime",
                "description": "Show system uptime",
                "category": "System Info",
            },
            # ─── CPU & Memory ───
            {
                "patterns": [r"cpu\s*(info|details|specs)", r"processor\s*info", r"what.*processor"],
                "command": "wmic cpu get name,NumberOfCores,MaxClockSpeed" if win else "cat /proc/cpuinfo",
                "description": "Display CPU information",
                "category": "Hardware",
            },
            {
                "patterns": [r"memory\s*(info|usage|details)", r"ram\s*(info|usage|details)", r"how\s*much\s*(ram|memory)"],
                "command": "powershell -Command Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object -First 10 Name,@{N='MemMB';E={[math]::Round($_.WorkingSet64/1MB,1)}}" if win else "free -h",
                "description": "Show memory usage information",
                "category": "Hardware",
            },
            # ─── Process Management ───
            {
                "patterns": [r"(list|show|display)\s*(all\s*)?(running\s*)?process", r"task\s*list", r"what.*running"],
                "command": "tasklist" if win else "ps aux",
                "description": "List all running processes",
                "category": "Process",
            },
            {
                "patterns": [r"(top|most|highest)\s*(cpu|memory|ram)", r"(heaviest|biggest)\s*process",
                             r"what.*(using|consuming).*(cpu|memory|ram)"],
                "command": "powershell -Command Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name,Id,CPU,@{N='MemMB';E={[math]::Round($_.WorkingSet64/1MB,1)}}" if win else "ps aux --sort=-%cpu | head -11",
                "description": "Show top processes by resource usage",
                "category": "Process",
            },
            {
                "patterns": [r"(show|list|get)\s*services", r"running\s*services", r"what\s*services"],
                "command": "powershell -Command Get-Service | Where-Object Status -eq Running | Select-Object -First 20 Name,DisplayName,Status" if win else "systemctl list-units --type=service --state=running",
                "description": "List running services",
                "category": "Process",
            },
            # ─── Disk & Storage ───
            {
                "patterns": [r"disk\s*(usage|space|info)", r"storage\s*(info|usage)", r"how\s*much\s*(disk|storage|space)",
                             r"free\s*space", r"drive\s*(info|space)"],
                "command": "powershell -Command Get-Volume | Select-Object DriveLetter,FileSystemLabel,@{N='SizeGB';E={[math]::Round($_.Size/1GB,2)}},@{N='FreeGB';E={[math]::Round($_.SizeRemaining/1GB,2)}}" if win else "df -h",
                "description": "Show disk usage and free space",
                "category": "Storage",
            },
            # ─── Network ───
            {
                "patterns": [r"(ip|network)\s*(address|config|info)", r"my\s*ip", r"network\s*adapter",
                             r"network\s*interface", r"inet\s*addr"],
                "command": "ipconfig" if win else "ip addr",
                "description": "Show network adapter configuration",
                "category": "Network",
            },
            {
                "patterns": [r"(network\s*)?connection", r"open\s*port", r"listening\s*port",
                             r"active\s*connection", r"netstat"],
                "command": "netstat -an" if win else "netstat -tuln",
                "description": "Show active network connections and listening ports",
                "category": "Network",
            },
            {
                "patterns": [r"ping\s+(\S+)", r"check.*connectivity\s+(\S+)", r"is\s+(\S+)\s+(up|online|reachable)"],
                "command_template": "ping -n 4 {target}" if win else "ping -c 4 {target}",
                "description": "Ping a network host to check connectivity",
                "category": "Network",
            },
            {
                "patterns": [r"dns\s*lookup\s+(\S+)", r"resolve\s+(\S+)", r"nslookup\s+(\S+)"],
                "command_template": "nslookup {target}",
                "description": "Perform DNS lookup for a hostname",
                "category": "Network",
            },
            # ─── Files ───
            {
                "patterns": [r"(list|show)\s*(files|directory|folder|dir)", r"what('s| is)\s*in\s*(this|the)\s*(directory|folder)"],
                "command": "dir" if win else "ls -la",
                "description": "List files in the current directory",
                "category": "Files",
            },
        ]

    def interpret(self, query: str) -> AICommandInterpretation:
        """Interpret a natural language query into a system command."""
        query_lower = query.lower().strip()
        best_match = None
        best_confidence = 0.0

        for rule in self._command_map:
            for pattern in rule["patterns"]:
                match = re.search(pattern, query_lower)
                if match:
                    # Calculate confidence based on match quality
                    match_ratio = len(match.group()) / len(query_lower)
                    confidence = min(0.95, 0.6 + match_ratio * 0.35)

                    if confidence > best_confidence:
                        # Handle template commands (e.g., ping <target>)
                        if "command_template" in rule:
                            groups = match.groups()
                            target = groups[-1] if groups else "localhost"
                            # Sanitize target
                            target = re.sub(r'[;&|`$><]', '', target)
                            command = rule["command_template"].format(target=target)
                        else:
                            command = rule["command"]

                        best_match = {
                            "command": command,
                            "description": rule["description"],
                            "category": rule["category"],
                            "confidence": confidence,
                        }
                        best_confidence = confidence

        if best_match and best_confidence >= settings.AI_CONFIDENCE_THRESHOLD:
            # Validate command safety
            is_safe, safety_msg = command_guard.validate_command(best_match["command"])

            return AICommandInterpretation(
                original_query=query,
                interpreted_command=best_match["command"],
                description=best_match["description"],
                category=best_match["category"],
                confidence=round(best_match["confidence"], 2),
                is_safe=is_safe,
                warning=None if is_safe else safety_msg,
            )

        # No match found
        return AICommandInterpretation(
            original_query=query,
            interpreted_command="",
            description="Could not interpret the command. Try rephrasing or use one of the sample prompts.",
            category="Unknown",
            confidence=0.0,
            is_safe=False,
            warning="No matching command pattern found",
        )

    def execute(self, interpretation: AICommandInterpretation) -> AICommandResult:
        """Execute an interpreted command if it's safe."""
        if not interpretation.is_safe or not interpretation.interpreted_command:
            return AICommandResult(
                interpretation=interpretation,
                output=None,
                error=interpretation.warning or "Command not safe to execute",
                executed=False,
            )

        # Double-check with command guard
        is_safe, msg = command_guard.validate_command(interpretation.interpreted_command)
        if not is_safe:
            return AICommandResult(
                interpretation=interpretation,
                output=None,
                error=msg,
                executed=False,
            )

        start_time = time.time()
        try:
            result = subprocess.run(
                interpretation.interpreted_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            elapsed = (time.time() - start_time) * 1000

            output = result.stdout.strip() if result.stdout else ""
            error = result.stderr.strip() if result.returncode != 0 else None

            return AICommandResult(
                interpretation=interpretation,
                output=output[:5000] if output else "Command completed with no output",
                error=error,
                executed=True,
                execution_time_ms=round(elapsed, 2),
            )
        except subprocess.TimeoutExpired:
            return AICommandResult(
                interpretation=interpretation,
                output=None,
                error="Command timed out after 30 seconds",
                executed=False,
                execution_time_ms=30000,
            )
        except Exception as e:
            return AICommandResult(
                interpretation=interpretation,
                output=None,
                error=f"Execution error: {str(e)}",
                executed=False,
            )

    def get_sample_prompts(self) -> List[AISamplePrompt]:
        """Get sample prompts for the UI."""
        return [
            AISamplePrompt(category="System Info", prompt="Show me system information", description="Displays detailed OS and hardware info"),
            AISamplePrompt(category="System Info", prompt="What is my hostname?", description="Shows the computer's network name"),
            AISamplePrompt(category="System Info", prompt="Who am I logged in as?", description="Shows the current username"),
            AISamplePrompt(category="System Info", prompt="How long has the system been running?", description="Shows system uptime"),
            AISamplePrompt(category="Hardware", prompt="Tell me about my CPU", description="Shows processor details"),
            AISamplePrompt(category="Hardware", prompt="Show memory usage", description="Lists top memory consumers"),
            AISamplePrompt(category="Process", prompt="List all running processes", description="Shows all active processes"),
            AISamplePrompt(category="Process", prompt="What's using the most CPU?", description="Top processes by CPU usage"),
            AISamplePrompt(category="Process", prompt="Show running services", description="Lists active system services"),
            AISamplePrompt(category="Storage", prompt="How much disk space is free?", description="Shows disk usage per drive"),
            AISamplePrompt(category="Network", prompt="Show my IP address", description="Network adapter configuration"),
            AISamplePrompt(category="Network", prompt="Show active connections", description="Lists open network connections"),
            AISamplePrompt(category="Network", prompt="Ping google.com", description="Tests connectivity to Google"),
            AISamplePrompt(category="Files", prompt="List files in this directory", description="Shows current directory contents"),
        ]


# Singleton instance
ai_engine = AIEngine()
