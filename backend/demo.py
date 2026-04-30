"""
NeuroSys OS Toolkit - Demo Script
Exercises all API endpoints and displays formatted output.
Run: python demo.py (with the backend server running)
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"
DIM = "\033[2m"

def header(title):
    print(f"\n{BOLD}{CYAN}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{RESET}\n")

def subheader(title):
    print(f"  {YELLOW}▸ {title}{RESET}")

def success(msg):
    print(f"  {GREEN}✓ {msg}{RESET}")

def error(msg):
    print(f"  {RED}✗ {msg}{RESET}")

def pretty(data, indent=4):
    text = json.dumps(data, indent=2, default=str)
    for line in text.split('\n')[:15]:
        print(f"    {DIM}{line}{RESET}")
    if len(text.split('\n')) > 15:
        print(f"    {DIM}... ({len(text.split(chr(10)))} total lines){RESET}")

def test_endpoint(method, path, label, body=None):
    subheader(label)
    try:
        url = f"{BASE_URL}{path}"
        if method == "GET":
            r = requests.get(url, timeout=15)
        else:
            r = requests.post(url, json=body, timeout=30)
        if r.status_code == 200:
            success(f"Status {r.status_code}")
            pretty(r.json())
        else:
            error(f"Status {r.status_code}: {r.text[:200]}")
        return r
    except requests.ConnectionError:
        error("Connection failed — is the server running?")
        return None
    except Exception as e:
        error(f"Error: {e}")
        return None

def main():
    print(f"\n{BOLD}{CYAN}")
    print("  ╔═══════════════════════════════════════════╗")
    print("  ║      NeuroSys OS Toolkit — Demo           ║")
    print("  ║      AI-Powered System Management         ║")
    print("  ╚═══════════════════════════════════════════╝")
    print(f"{RESET}")

    # Health
    header("1. Health Check")
    r = test_endpoint("GET", "/", "Server Status")
    if r is None:
        print(f"\n  {RED}Server not reachable. Start it with:{RESET}")
        print(f"  {YELLOW}cd backend && uvicorn app.main:app --reload{RESET}\n")
        sys.exit(1)

    # System
    header("2. System Metrics")
    test_endpoint("GET", "/api/system/info", "System Info")
    test_endpoint("GET", "/api/system/metrics", "Live Metrics")
    test_endpoint("GET", "/api/system/history", "Metrics History")
    test_endpoint("GET", "/api/system/predictions", "Resource Predictions")

    # Processes
    header("3. Process Management")
    test_endpoint("GET", "/api/processes/?limit=5", "Top 5 Processes")
    test_endpoint("GET", "/api/processes/top?n=3&by=memory", "Top 3 by Memory")

    # AI Commands
    header("4. AI Command Interpreter")
    test_endpoint("GET", "/api/ai/prompts", "Sample Prompts")
    test_endpoint("POST", "/api/ai/interpret", "Interpret: 'Show me system info'",
                  {"query": "Show me system information"})
    test_endpoint("POST", "/api/ai/execute", "Execute: 'What is my hostname?'",
                  {"query": "What is my hostname?"})
    test_endpoint("POST", "/api/ai/execute", "Execute: 'Show disk space'",
                  {"query": "How much disk space is free?"})

    # Optimizer
    header("5. Auto-Optimization")
    test_endpoint("GET", "/api/optimizer/suggestions", "Optimization Suggestions")

    # File System
    header("6. File System Analyzer")
    test_endpoint("POST", "/api/filesystem/scan", "Scan Current Directory",
                  {"path": ".", "max_depth": 3})
    test_endpoint("GET", "/api/filesystem/duplicates", "Duplicate Files")
    test_endpoint("GET", "/api/filesystem/junk", "Junk Files")

    # Logs
    header("7. Log Analyzer")
    test_endpoint("GET", "/api/logs/system?max_lines=20", "System Logs")
    test_endpoint("POST", "/api/logs/analyze", "Analyze Custom Log",
                  {"content": "2024-01-15 10:23:45 ERROR: Out of memory - cannot allocate 512MB\n"
                              "2024-01-15 10:24:00 WARNING: Disk usage at 92%\n"
                              "2024-01-15 10:24:15 INFO: Service restarted successfully\n"
                              "2024-01-15 10:25:00 ERROR: Connection refused to database server\n"
                              "2024-01-15 10:25:30 ERROR: Permission denied accessing /etc/config\n"})

    print(f"\n{BOLD}{GREEN}  ✓ Demo complete!{RESET}")
    print(f"  {DIM}Visit http://localhost:8000/docs for interactive API docs{RESET}")
    print(f"  {DIM}Visit http://localhost:5173 for the frontend dashboard{RESET}\n")

if __name__ == "__main__":
    main()
