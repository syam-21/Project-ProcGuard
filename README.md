🛡️ ProcGuard
Advanced System Resource Monitoring and Process Control for Linux

A robust full-stack system administration tool designed for real-time resource monitoring, intelligent process management, and web-based control on Linux systems (Ubuntu/Lubuntu).

1. Project Overview

ProcGuard is a dual-interface system utility that combines:

A high-performance Bash CLI engine
A Flask-powered Web Dashboard

It provides:

Real-time CPU, RAM, Disk, and Network monitoring
Intelligent Auto-Optimization for resource cleanup
A Global Process Watcher for instant process detection
Threshold-based process termination with escalation support
Downloadable performance reports and structured logs
2. Key Features
🖥️ Real-Time Web Dashboard
Live Metrics: CPU, RAM, Disk, Network speed (Upload/Download KB/s)
Interactive Charts: Historical CPU and RAM usage (last 20 data points)
Notification System: Real-time toast alerts for process events
Alert Banner: Warning when thresholds are exceeded
⚙️ Intelligent Process Control
Manual Kill: Terminate processes via PID with confirmation
Auto-Kill: Automatically stops high-resource processes
Auto-Optimization Mode: Cleans idle but resource-heavy processes
📡 Global Process Watcher
Instant Detection: Fast polling (0.5s) for new processes
Watchlist Alerts: Monitors apps like Chrome, VLC, VS Code, etc.
Live Event Stream: Displays last 10 system events
🔐 Security & Protection
Critical Process Guard: Protects system services (systemd, sshd, etc.)
Privileged Escalation: Uses sudo -n for authorized kills
Security Protection: Prevents XSS and path traversal attacks
📈 Reporting & Logs
Performance Reports: Includes uptime, usage, and history
Downloadable Reports: Export as .txt files
Log Management:
Live viewer
Level filtering
Auto-rotation (1MB limit)
Archive browsing
3. Project Structure
ProcGuard/
├── app.py                  # Flask server & API
├── main.sh                 # CLI entry point
├── config.conf             # Configuration file
├── README.md               # Documentation
├── modules/
│   ├── monitor.sh
│   ├── process_manager.sh
│   ├── process_watcher.sh
│   ├── logger.sh
│   └── report.sh
├── templates/
│   └── index.html          # Web UI
├── logs/
└── reports/
4. Installation & Setup
Prerequisites
Linux (Ubuntu / Lubuntu / Debian)
Python 3.8+
Bash 4+
Python libraries: Flask, psutil
Installation Steps
git clone <repository-url>
cd ProcGuard

python3 -m venv venv
source venv/bin/activate
pip install flask psutil

chmod +x main.sh modules/*.sh
5. Usage
🌐 Web Dashboard (Recommended)
source venv/bin/activate
python3 app.py

Open:
http://localhost:5000

💻 CLI Mode
./main.sh
⏱️ Automated Mode (Cron)
*/5 * * * * /path/to/ProcGuard/main.sh --automate
6. API Reference
Method	Endpoint	Description
GET	/api/stats	System metrics and alerts
GET	/api/processes	Process list
POST	/api/kill	Kill process by PID
POST	/api/autokill	Kill high-resource processes
POST	/api/optimize/toggle	Toggle optimization
GET	/api/report/download	Download report
GET	/api/report/archive/download/<file>	Download archived report
GET	/api/logs	View logs
GET	/api/critical	Critical process status
7. Configuration (config.conf)

Key settings:

CPU_THRESHOLD / RAM_THRESHOLD → Trigger limits
AUTO_OPTIMIZE → Enable/disable optimization
WATCHED_PROCESSES → Monitored apps list
LOG_MAX_SIZE → Log rotation size
8. Troubleshooting

Permission Denied

chmod +x main.sh modules/*.sh
Sudo Kill Fails
Ensure user has sudo privileges

Port 5000 Busy

fuser -k 5000/tcp
Missing psutil
Activate virtual environment before running
