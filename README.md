<div align="center">

# 🧠 NeuroSys OS Toolkit

### AI-Powered Operating System Utility & Monitoring Platform

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![Tailwind](https://img.shields.io/badge/Tailwind-3.0-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)

*Real-time system monitoring • AI command interpreter • Auto-optimization • File analysis • Log intelligence*

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [API Reference](#-api-reference)
- [Modules](#-modules)
- [Security](#-security)
- [Project Structure](#-project-structure)
- [Demo](#-demo)
- [Contributing](#-contributing)

---

## 🔭 Overview

**NeuroSys OS Toolkit** is a production-grade, full-stack SaaS platform for intelligent operating system management. It combines real-time system monitoring with AI-powered command interpretation, predictive resource analysis, and automated system optimization.

### Why NeuroSys?

| Traditional Tools | NeuroSys |
|---|---|
| CLI-only interfaces | Modern SaaS dashboard |
| Manual command lookup | Natural language → system commands |
| Reactive troubleshooting | Predictive resource alerts |
| Manual optimization | AI-powered auto-optimization |
| Raw log files | Intelligent log analysis with explanations |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (React + Tailwind)            │
│  ┌─────────┐ ┌──────────┐ ┌───────────┐ ┌───────────┐  │
│  │Dashboard │ │Processes │ │AI Command │ │ Optimizer │  │
│  └────┬─────┘ └────┬─────┘ └─────┬─────┘ └─────┬─────┘  │
│       │             │             │              │        │
│  ┌────┴─────────────┴─────────────┴──────────────┴───┐   │
│  │          API Client + WebSocket Hooks              │   │
│  └────────────────────────┬──────────────────────────┘   │
└───────────────────────────┼──────────────────────────────┘
                            │ HTTP / WebSocket
┌───────────────────────────┼──────────────────────────────┐
│                   Backend (FastAPI)                       │
│  ┌────────────────────────┴──────────────────────────┐   │
│  │              API Routes + WebSocket                │   │
│  └────┬──────┬──────┬──────┬──────┬──────┬───────────┘   │
│       │      │      │      │      │      │               │
│  ┌────┴─┐ ┌──┴──┐ ┌─┴──┐ ┌┴───┐ ┌┴──┐ ┌┴────┐          │
│  │System│ │Proc │ │ AI │ │Opt │ │FS │ │Logs │          │
│  │ Mon. │ │Mgr. │ │Eng.│ │    │ │   │ │     │          │
│  └──────┘ └─────┘ └────┘ └────┘ └───┘ └─────┘          │
│                                                          │
│  ┌────────────────┐  ┌───────────────────────────┐       │
│  │ Command Guard  │  │  Resource Predictor (NumPy)│       │
│  │ (Security)     │  │  (Linear Regression)       │       │
│  └────────────────┘  └───────────────────────────┘       │
│                                                          │
│  ┌────────────────────────────────────────────────┐      │
│  │              psutil (System Interface)          │      │
│  └────────────────────────────────────────────────┘      │
└──────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### 1. 📊 Real-Time Dashboard
- Live CPU, Memory, Disk, and Network metrics
- Interactive area charts with 60-second history
- System info panel (OS, hostname, uptime)
- WebSocket-powered live updates (1-second interval)

### 2. 🤖 AI Command Interpreter
- Natural language → system command translation
- Pattern-matching NLP engine (no API keys needed)
- Safe command execution with whitelist validation
- 14+ sample prompts across 6 categories
- Command history with execution results

### 3. 📈 Resource Prediction
- Linear regression-based CPU/memory forecasting
- Trend detection (increasing/decreasing/stable)
- Automatic high-usage alerts
- Confidence scoring

### 4. ⚡ Auto-Optimization Engine
- High CPU process detection
- Memory pressure analysis
- Disk space monitoring
- Zombie process cleanup (auto-fixable)
- Severity-coded recommendations

### 5. 📁 File System Analyzer
- MD5-based duplicate file detection
- Junk/temp file scanning (15+ patterns)
- Directory size breakdown by file type
- Top 10 largest files identification
- Configurable scan depth and limits

### 6. 📋 Log Analyzer
- System log reading (Windows Event Log / syslog)
- 10+ error pattern recognition
- AI-generated natural language explanations
- Custom log paste & analysis
- Severity filtering and recommendations

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 | UI framework |
| **Styling** | Tailwind CSS 3 | Utility-first CSS |
| **Charts** | Recharts | Data visualization |
| **Icons** | Lucide React | Icon library |
| **Routing** | React Router v6 | SPA navigation |
| **HTTP** | Axios | API communication |
| **Backend** | FastAPI | REST API framework |
| **Real-time** | WebSocket | Live data streaming |
| **System** | psutil | OS metrics collection |
| **Math** | NumPy | Prediction algorithms |
| **Validation** | Pydantic v2 | Data validation |

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.9+
- **Node.js** 18+
- **npm** 9+

### 1. Clone & Setup Backend

```bash
# Navigate to backend
cd neurosys-toolkit/backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Linux/Mac)
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Backend Server

```bash
# From backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **REST API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **WebSocket**: ws://localhost:8000/ws/metrics

### 3. Setup Frontend

```bash
# Navigate to frontend
cd neurosys-toolkit/frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

The dashboard will be available at: **http://localhost:5173**

### 4. Run Demo Script

```bash
# From backend directory (with server running)
pip install requests
python demo.py
```

---

## 📡 API Reference

### System Metrics
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/system/metrics` | Current CPU, RAM, disk, network |
| `GET` | `/api/system/history` | Historical metrics (last 60 points) |
| `GET` | `/api/system/info` | OS info, hostname, uptime |
| `GET` | `/api/system/predictions` | CPU/memory usage predictions |

### Process Management
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/processes/?sort_by=cpu&limit=100` | List processes |
| `GET` | `/api/processes/top?n=10&by=cpu` | Top N processes |
| `GET` | `/api/processes/search?q=chrome` | Search by name |
| `POST` | `/api/processes/{pid}/kill` | Terminate process |

### AI Commands
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/ai/interpret` | Interpret NL command |
| `POST` | `/api/ai/execute` | Interpret and execute |
| `GET` | `/api/ai/prompts` | Sample prompts list |

### Optimizer
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/optimizer/suggestions` | Get suggestions |
| `POST` | `/api/optimizer/apply/{id}` | Apply a suggestion |

### File System
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/filesystem/scan` | Scan directory |
| `GET` | `/api/filesystem/duplicates` | Duplicate files |
| `GET` | `/api/filesystem/junk` | Junk/temp files |

### Log Analyzer
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/logs/system` | System logs |
| `POST` | `/api/logs/analyze` | Analyze custom logs |

### WebSocket
| Endpoint | Description | Interval |
|----------|-------------|----------|
| `ws://localhost:8000/ws/metrics` | Real-time system metrics | 1 second |
| `ws://localhost:8000/ws/processes` | Real-time process list | 2 seconds |

---

## 🔒 Security

### Command Guard System

NeuroSys uses a **whitelist-only** security model:

- ✅ Only pre-approved read-only commands can execute
- 🚫 Dangerous patterns are blocked (rm -rf, format, shutdown, etc.)
- 🚫 Command chaining operators are stripped (`;`, `|`, `&&`)
- 🚫 System-critical processes (PID < 100) cannot be killed
- 🚫 Encoded PowerShell commands are blocked
- 🚫 Network download-to-execution pipes are blocked

### Blocked Command Categories
- File destruction (`rm -rf`, `del /f`, `format`)
- System control (`shutdown`, `reboot`, `halt`)
- Registry modification (`reg add`, `reg delete`)
- User management (`net user`, `net localgroup`)
- Permission escalation (`takeown`, `icacls`)

---

## 📂 Project Structure

```
neurosys-toolkit/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application entry
│   │   ├── config.py            # Configuration management
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── system.py    # System metrics endpoints
│   │   │   │   ├── processes.py # Process management
│   │   │   │   ├── ai_commands.py # AI interpreter
│   │   │   │   ├── optimizer.py # Auto-optimization
│   │   │   │   ├── filesystem.py # File analyzer
│   │   │   │   └── logs.py     # Log analyzer
│   │   │   └── websocket.py    # WebSocket handlers
│   │   ├── services/
│   │   │   ├── system_monitor.py  # psutil monitoring
│   │   │   ├── process_manager.py # Process CRUD
│   │   │   ├── ai_engine.py      # NL command engine
│   │   │   ├── resource_predictor.py # Predictions
│   │   │   ├── optimizer.py      # Optimization logic
│   │   │   ├── fs_analyzer.py    # File analysis
│   │   │   └── log_analyzer.py   # Log parsing
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic models
│   │   └── security/
│   │       └── command_guard.py # Command validation
│   ├── requirements.txt
│   └── demo.py                 # API demo script
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── index.css           # Tailwind + design system
│   │   ├── api/
│   │   │   └── client.js       # API client
│   │   ├── hooks/
│   │   │   └── useWebSocket.js # WebSocket hook
│   │   ├── components/
│   │   │   └── Layout/
│   │   │       ├── Sidebar.jsx
│   │   │       ├── Header.jsx
│   │   │       └── DashboardLayout.jsx
│   │   └── pages/
│   │       ├── DashboardPage.jsx
│   │       ├── ProcessesPage.jsx
│   │       ├── AICommandPage.jsx
│   │       ├── OptimizerPage.jsx
│   │       ├── FileSystemPage.jsx
│   │       └── LogsPage.jsx
│   ├── tailwind.config.js
│   └── package.json
└── README.md
```

---

## 🎮 Demo

### Sample AI Commands

```
"Show me system information"        → systeminfo
"What's using the most CPU?"        → Top processes by CPU
"How much disk space is free?"      → Disk usage report
"Show my IP address"                → ipconfig / ip addr
"Ping google.com"                   → ping -n 4 google.com
"List running services"             → Get-Service
"Who am I logged in as?"            → whoami
```

### Demo Script Output

```
╔═══════════════════════════════════════════╗
║      NeuroSys OS Toolkit — Demo           ║
║      AI-Powered System Management         ║
╚═══════════════════════════════════════════╝

▸ Server Status
  ✓ Status 200

▸ Live Metrics
  ✓ CPU: 23.5% | Memory: 67.2% | Disk: 45.1%

▸ AI Command: "What is my hostname?"
  ✓ Interpreted: hostname
  ✓ Output: DESKTOP-NEUROSYS

✓ Demo complete!
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">

**Built with ❤️ using FastAPI, React, and psutil**

[Report Bug](https://github.com/issues) · [Request Feature](https://github.com/issues) · [API Docs](http://localhost:8000/docs)

</div>
