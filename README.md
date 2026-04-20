🛡️ ProcGuard
Advanced System Resource Monitoring and Process Control for Linux

A powerful full-stack system administration tool for real-time monitoring, intelligent process management, and web-based control on Linux systems.

🚀 Features
🖥️ Real-Time Monitoring
Live CPU, RAM, Disk, and Network usage
Real-time dashboard with interactive charts
Threshold-based alert system
⚙️ Process Management
Kill processes by PID (manual control)
Auto-kill high resource-consuming processes
Background auto-optimization engine
📡 Global Process Watcher
Detects every new process instantly
Watchlist alerts (Chrome, VLC, VS Code, etc.)
Live event notifications
🔐 Security
Protects critical system processes
Safe privilege escalation (sudo -n)
XSS and path traversal protection
📈 Reports & Logs
Downloadable performance reports
Log viewer with filtering
Automatic log rotation and archive system
🏗️ Project Structure
ProcGuard/
├── app.py
├── main.sh
├── config.conf
├── modules/
├── templates/
├── logs/
└── reports/
⚙️ Installation
Prerequisites
Linux (Ubuntu / Lubuntu / Debian)
Python 3.8+
Bash 4+
Setup
git clone https://github.com/your-username/ProcGuard.git
cd ProcGuard

python3 -m venv venv
source venv/bin/activate

pip install flask psutil

chmod +x main.sh modules/*.sh
▶️ Usage
🌐 Web Dashboard
source venv/bin/activate
python3 app.py

Open in browser:
👉 http://localhost:5000

💻 CLI Mode
./main.sh
⏱️ Auto Mode (Cron)
*/5 * * * * /path/to/ProcGuard/main.sh --automate
🔌 API Endpoints
Method	Endpoint	Description
GET	/api/stats	System metrics
GET	/api/processes	Process list
POST	/api/kill	Kill process
POST	/api/autokill	Auto kill
POST	/api/optimize/toggle	Toggle optimization
GET	/api/report/download	Download report
GET	/api/logs	View logs
🛠️ Configuration

Edit config.conf:

CPU_THRESHOLD=80
RAM_THRESHOLD=75
AUTO_OPTIMIZE=true
WATCHED_PROCESSES=chrome,vlc,code
LOG_MAX_SIZE=1048576
🧪 Troubleshooting

Permission issue:

chmod +x main.sh modules/*.sh

Port already in use:

fuser -k 5000/tcp

Missing dependencies:

source venv/bin/activate
📌 Future Improvements
Docker support
Authentication system (login/logout)
Remote monitoring (multi-device support)
Mobile responsive UI enhancements
👨‍💻 Author

MD. Abdullah Khan

⭐ Support

If you like this project, give it a ⭐ on GitHub!
