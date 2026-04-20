🛡️ ProcGuard: Advanced System Resource Monitoring and Process Control for Linux
A robust, full-stack system administration utility for real-time resource monitoring, intelligent process management, and web-based control — built for Linux (Ubuntu/Lubuntu).

1. Project Overview
ProcGuard is a dual-interface system monitoring and process control tool. It combines a high-performance Bash CLI engine with a Flask-powered Web Dashboard to provide:

Real-time CPU, RAM, Disk, and Network monitoring.
Auto-Optimization: Intelligent background resource reclamation.
Global Process Watcher: Instant detection of every new process starting on the system.
Threshold-based process termination and privileged kill escalation.
Downloadable performance reports and archived log management.
2. Key Features
🖥️ Real-Time Web Dashboard
Live Metrics: Real-time view of CPU, RAM, Disk, and Network Speed (Upload/Download KB/s).
Interactive Charts: Historical CPU and RAM usage charts (last 20 data points).
Notification System: Instant toast notifications for new process detections and kill events.
Alert Banner: Global warning banner when any resource exceeds configured thresholds.
⚙️ Intelligent Process Control
Manual Kill: Terminate any process by PID directly from the UI with a confirmation dialog.
Auto-Kill: Automatically terminates non-critical processes exceeding a user-defined threshold.
Auto-Optimization Mode: A background engine that cleans up "heavy idle" processes (sleeping but consuming high RAM or CPU) to keep the system lean.
📡 Global Process Watcher
Instant Detection: Fast-polling (0.5s) watcher that catches every new process as it starts.
Watchlist Alerts: Specific alerts for "Watched Processes" like VLC, Chrome, Firefox, VS Code, and Spotify.
Live Event Stream: The last 10 system events are shown as interactive toasts in the dashboard.
🔐 Security & Protection
Critical Process Guard: A hardcoded protection list (systemd, init, sshd, Xorg, etc.) prevents accidental termination of essential services.
Privileged Escalation: On AccessDenied, ProcGuard automatically attempts a non-interactive sudo -n kill for authorized administrators.
XSS & Traversal Protection: All outputs are HTML-escaped, and download paths are strictly sanitized.
📈 Reporting & Logs
Performance Summaries: Generates structured reports with system uptime, resource usage, and termination history.
⬇️ Downloadable Assets: Download current or archived reports as .txt files directly from the browser.
Log Management: Live viewer with level filters, automatic log rotation at 1MB, and an archive browser.
3. Project Structure
ProcGuard/
├── app.py                  # Flask Web Server, API Endpoints, & Background Threads
├── main.sh                 # Bash CLI Entry Point & Interactive Menu
├── config.conf             # Central Configuration (Thresholds, Paths, Watchlists)
├── README.md               # Project Documentation
├── modules/
│   ├── monitor.sh          # Resource metrics collection (Bash)
│   ├── process_manager.sh  # Detection and termination logic (Bash)
│   ├── process_watcher.sh  # Real-time process detection loop (Bash)
│   ├── logger.sh           # Logging, rotation, and directory management (Bash)
│   └── report.sh           # Performance report generation (Bash)
├── templates/
│   └── index.html          # Responsive Web Dashboard (6-tab UI)
├── logs/                   # Active logs and archives
└── reports/                # Performance summaries and archives
4. Installation & Setup
Prerequisites
Linux (Ubuntu / Lubuntu / Debian)
Python 3.8+
Bash 4+
psutil and flask Python libraries.
Step-by-Step Installation
Clone the repository:

git clone <repository-url>
cd ProcGuard
Set up the Python Virtual Environment:

python3 -m venv venv
source venv/bin/activate
pip install flask psutil
Set script permissions:

chmod +x main.sh modules/*.sh
5. Usage
🌐 Web Dashboard (Recommended)
Start the web server to access the full feature set:

source venv/bin/activate
python3 app.py
Open your browser at http://localhost:5000.

💻 CLI Mode (Interactive Bash)
Run the professional CLI menu for local administration:

./main.sh
⏱️ Automated Mode (Cron)
To run ProcGuard's auto-kill feature every 5 minutes:

*/5 * * * * /path/to/ProcGuard/main.sh --automate
6. API Reference
Method	Endpoint	Description
GET	/api/stats	System metrics, network speed, and threshold alerts.
GET	/api/processes	List of top processes (supports ?all=true).
POST	/api/kill	Kill a process by PID (Manual).
POST	/api/autokill	Kill all processes above a specific threshold.
POST	/api/optimize/toggle	Enable/Disable the Auto-Optimization engine.
GET	/api/report/download	Download the latest performance report as .txt.
GET	/api/report/archive/download/<file>	Download a specific archived report.
GET	/api/logs	Fetch log lines with optional level filtering.
GET	/api/critical	Status of critical system processes.
7. Configuration (config.conf)
You can tune ProcGuard by editing the config.conf file:

CPU_THRESHOLD / RAM_THRESHOLD: Default triggers for alerts and auto-kill.
AUTO_OPTIMIZE: Set to true to enable background resource reclamation by default.
WATCHED_PROCESSES: Comma-separated list of app names to monitor specifically.
LOG_MAX_SIZE: Maximum size (in bytes) before the log is archived.
8. Troubleshooting
Permission Denied: Ensure you have run chmod +x main.sh modules/*.sh.
Sudo Kill Fails: Ensure your user is in the sudoers group or configure sudo -n for non-interactive use.
Port 5000 in use: Run fuser -k 5000/tcp to clear the port.
Missing psutil: Always ensure your virtual environment is active (source venv/bin/activate).

sajiye dew
