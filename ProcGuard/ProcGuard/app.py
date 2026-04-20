from flask import Flask, render_template, jsonify, request, send_file
import psutil, os, subprocess, datetime, glob, shutil, signal, time, threading

app = Flask(__name__)

# ── Global State for Network Speed ────────────────────────────────────────────
last_net_io = psutil.net_io_counters()
last_net_time = time.time()

# ── Config ────────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
LOG_FILE      = os.path.join(BASE_DIR, "logs", "procguard.log")
REPORT_FILE   = os.path.join(BASE_DIR, "reports", "performance_summary.txt")
ARCHIVE_DIR   = os.path.join(BASE_DIR, "logs", "archive")
REP_ARCH_DIR  = os.path.join(BASE_DIR, "reports", "archive")
MAX_LOG_BYTES = 1 * 1024 * 1024          # 1 MB → rotate
CPU_THRESHOLD = 50  # Changed default to 50 as requested
MEM_THRESHOLD = 80
DISK_THRESHOLD= 90

CRITICAL = {"systemd","init","sshd","Xorg","NetworkManager","kthreadd",
             "migration","rcu_sched","watchdog","kworker","flask","python3","bash","sh"}

# Watched processes for instant detection
WATCHED_PROCESSES = {"vlc", "chrome", "firefox", "code", "spotify"}
WATCHER_EVENTS = [] # Store last 5 events

# Auto-Optimization State
AUTO_OPTIMIZE_ENABLED = True
OPTIMIZE_CPU_LIMIT = 10.0
OPTIMIZE_RAM_LIMIT = 5.0

# ── Auto Optimizer ───────────────────────────────────────────────────────────
def auto_optimizer_thread():
    """Background thread that optimizes system by cleaning up unnecessary processes."""
    global AUTO_OPTIMIZE_ENABLED
    write_log("INFO", "Auto-Optimization thread started.")
    while True:
        if AUTO_OPTIMIZE_ENABLED:
            try:
                optimized_count = 0
                for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
                    try:
                        # Skip critical processes
                        if p.info["name"] in CRITICAL:
                            continue
                            
                        # Logic: If a process is idle (sleeping) but consuming significant RAM or some CPU
                        cpu = p.info.get("cpu_percent", 0)
                        mem = p.info.get("memory_percent", 0)
                        status = p.info.get("status", "")
                        
                        if (status == "sleeping" and mem > OPTIMIZE_RAM_LIMIT) or \
                           (cpu > OPTIMIZE_CPU_LIMIT and cpu < CPU_THRESHOLD):
                            # This is an optimization target
                            p.terminate()
                            write_log("INFO", f"🧹 [OPTIMIZER] Terminated unnecessary process: {p.info['name']} (PID {p.pid}) to free resources.")
                            optimized_count += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if optimized_count > 0:
                    write_log("INFO", f"✅ Optimization complete. Cleaned up {optimized_count} processes.")
            except Exception as e:
                write_log("ERROR", f"Optimizer error: {e}")
        
        time.sleep(30) # Run every 30 seconds

# ── Process Watcher ──────────────────────────────────────────────────────────
def process_watcher_thread():
    """Background thread that monitors for all new processes."""
    global WATCHER_EVENTS
    existing_pids = set(psutil.pids())
    write_log("INFO", "Global process watcher thread started.")
    
    while True:
        try:
            current_pids = set(psutil.pids())
            new_pids = current_pids - existing_pids
            
            for pid in new_pids:
                try:
                    p = psutil.Process(pid)
                    name = p.name()
                    
                    # Log every new process detection
                    msg = f"✨ [NEW] {name} started (PID {pid})"
                    write_log("INFO", msg)
                    
                    # Add to events for UI toast
                    WATCHER_EVENTS.append({"name": name, "pid": pid, "time": datetime.datetime.now().strftime("%H:%M:%S")})
                    if len(WATCHER_EVENTS) > 10:
                        WATCHER_EVENTS.pop(0)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            existing_pids = current_pids
        except Exception:
            pass
        
        time.sleep(0.5)

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_net_speed():
    global last_net_io, last_net_time
    now_io = psutil.net_io_counters()
    now_time = time.time()
    dt = now_time - last_net_time
    
    if dt <= 0: return 0, 0
    
    upload = (now_io.bytes_sent - last_net_io.bytes_sent) / dt / 1024  # KB/s
    download = (now_io.bytes_recv - last_net_io.bytes_recv) / dt / 1024 # KB/s
    
    last_net_io = now_io
    last_net_time = now_time
    return round(upload, 2), round(download, 2)

def ensure_dirs():
    for d in [os.path.join(BASE_DIR,"logs"), os.path.join(BASE_DIR,"reports"),
              ARCHIVE_DIR, REP_ARCH_DIR]:
        os.makedirs(d, exist_ok=True)

def write_log(level: str, message: str):
    ensure_dirs()
    rotate_log_if_needed()
    ts  = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level.upper():5s}] {message}\n"
    with open(LOG_FILE, "a") as f:
        f.write(line)

def rotate_log_if_needed():
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) >= MAX_LOG_BYTES:
        ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = os.path.join(ARCHIVE_DIR, f"procguard_{ts}.log")
        shutil.move(LOG_FILE, dest)
        write_log("INFO", f"Log rotated → archive/{os.path.basename(dest)}")

def read_log_lines(n=100, level_filter=None):
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE) as f:
        lines = f.readlines()
    if level_filter and level_filter != "ALL":
        lines = [l for l in lines if f"[{level_filter}]" in l or f"[{level_filter:5s}]" in l]
    return [l.rstrip() for l in lines[-n:]]

def generate_report():
    ensure_dirs()
    rotate_log_if_needed()
    now   = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    upstr = str(datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time()))
    cpu   = psutil.cpu_percent(interval=0.5)
    mem   = psutil.virtual_memory()
    disk  = psutil.disk_usage("/")

    # Count kill events from log
    manual_kills = auto_kills = sudo_kills = warn_count = 0
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE) as f:
            for l in f:
                if "[MANUAL KILL]" in l: manual_kills += 1
                if "[AUTO KILL]"   in l: auto_kills   += 1
                if "[SUDO KILL]"   in l: sudo_kills   += 1
                if "[WARN]"        in l or "[ WARN]" in l: warn_count += 1

    procs = []
    for p in psutil.process_iter(["pid","name","status","cpu_percent","memory_percent"]):
        try:
            procs.append(p.info)
        except Exception:
            pass

    lines = [
        "╔══════════════════════════════════════════════╗",
        "║        ProcGuard Performance Report          ║",
        "╚══════════════════════════════════════════════╝",
        f"  Generated   : {now}",
        f"  Uptime      : {upstr.split('.')[0]}",
        "─" * 47,
        "  SYSTEM RESOURCES",
        "─" * 47,
        f"  CPU Usage   : {cpu:.1f}%",
        f"  RAM Usage   : {mem.percent:.1f}%  ({mem.used/1e9:.2f} GB / {mem.total/1e9:.2f} GB)",
        f"  Disk Usage  : {disk.percent}%  ({disk.used/1e9:.1f} GB / {disk.total/1e9:.1f} GB)",
        "─" * 47,
        "  TOP 5 CPU PROCESSES",
        "─" * 47,
    ]
    top_cpu = sorted(procs, key=lambda x: x.get("cpu_percent") or 0, reverse=True)[:5]
    for p in top_cpu:
        lines.append(f"  PID {p['pid']:>7}  {p['name']:<25} CPU {p.get('cpu_percent',0):.1f}%")
    lines += [
        "─" * 47,
        "  TERMINATION SUMMARY",
        "─" * 47,
        f"  Manual Kills  : {manual_kills}",
        f"  Auto Kills    : {auto_kills}",
        f"  Sudo Kills    : {sudo_kills}",
        f"  Total Warnings: {warn_count}",
        "─" * 47,
    ]

    report_text = "\n".join(lines)
    with open(REPORT_FILE, "w") as f:
        f.write(report_text)

    # Archive a timestamped copy
    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(REP_ARCH_DIR, f"report_{ts}.txt")
    shutil.copy(REPORT_FILE, dest)

    write_log("INFO", "Performance report generated.")
    return report_text

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    ensure_dirs()
    write_log("INFO", "Dashboard loaded.")
    return render_template("index.html",
                           cpu_threshold=CPU_THRESHOLD,
                           mem_threshold=MEM_THRESHOLD,
                           disk_threshold=DISK_THRESHOLD)

# ── Stats API ─────────────────────────────────────────────────────────────────
@app.route("/api/stats")
def api_stats():
    global WATCHER_EVENTS, AUTO_OPTIMIZE_ENABLED
    cpu  = psutil.cpu_percent(interval=None) # Use non-blocking
    mem  = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    up, down = get_net_speed()
    total_procs = len(psutil.pids())
    
    alerts = []
    if cpu  >= CPU_THRESHOLD:
        write_log("WARN", f"CPU usage ({cpu:.1f}%) exceeded threshold ({CPU_THRESHOLD}%)!")
        alerts.append(f"HIGH CPU: {cpu:.1f}%")
    if mem.percent >= MEM_THRESHOLD:
        write_log("WARN", f"RAM usage ({mem.percent:.1f}%) exceeded threshold ({MEM_THRESHOLD}%)!")
        alerts.append(f"HIGH RAM: {mem.percent:.1f}%")
    if disk.percent >= DISK_THRESHOLD:
        write_log("WARN", f"Disk usage ({disk.percent}%) exceeded threshold ({DISK_THRESHOLD}%)!")
        alerts.append(f"HIGH DISK: {disk.percent}%")
    
    return jsonify({
        "cpu":  cpu,
        "ram":  {"percent": mem.percent, "used_gb": round(mem.used/1e9,2), "total_gb": round(mem.total/1e9,2)},
        "disk": {"percent": disk.percent,"used_gb": round(disk.used/1e9,1),"total_gb": round(disk.total/1e9,1)},
        "net":  {"up": up, "down": down},
        "total_procs": total_procs,
        "alerts": alerts,
        "watcher_events": WATCHER_EVENTS,
        "auto_optimize": AUTO_OPTIMIZE_ENABLED,
        "thresholds": {"cpu": CPU_THRESHOLD, "mem": MEM_THRESHOLD, "disk": DISK_THRESHOLD}
    })

@app.route("/api/optimize/toggle", methods=["POST"])
def toggle_optimize():
    global AUTO_OPTIMIZE_ENABLED
    AUTO_OPTIMIZE_ENABLED = not AUTO_OPTIMIZE_ENABLED
    state = "ENABLED" if AUTO_OPTIMIZE_ENABLED else "DISABLED"
    write_log("INFO", f"Auto-Optimization Mode {state} by user.")
    return jsonify({"status": "ok", "enabled": AUTO_OPTIMIZE_ENABLED})

# ── Process API ───────────────────────────────────────────────────────────────
@app.route("/api/processes")
def api_processes():
    procs = []
    all_mode = request.args.get("all", "false") == "true"
    
    # We use a short interval for CPU percent if it's the first time
    for p in psutil.process_iter(["pid","name","status","cpu_percent","memory_percent","username"]):
        try:
            info = p.info
            info["protected"] = info["name"] in CRITICAL
            procs.append(info)
        except Exception:
            pass
            
    procs.sort(key=lambda x: (x.get("cpu_percent") or 0) + (x.get("memory_percent") or 0), reverse=True)
    
    total_count = len(procs)
    return jsonify({
        "processes": procs if all_mode else procs[:50],
        "total": total_count
    })

@app.route("/api/kill", methods=["POST"])
def api_kill():
    data = request.get_json()
    pid  = int(data.get("pid", 0))
    try:
        p = psutil.Process(pid)
        if p.name() in CRITICAL:
            write_log("WARN", f"Kill blocked — critical process: {p.name()} (PID {pid})")
            return jsonify({"status": "blocked", "reason": f"'{p.name()}' is a critical process."})
        p.terminate()
        write_log("INFO", f"[MANUAL KILL] PID {pid} ({p.name()}) terminated.")
        return jsonify({"status": "killed", "pid": pid, "name": p.name()})
    except psutil.NoSuchProcess:
        return jsonify({"status": "error", "reason": "Process not found."})
    except psutil.AccessDenied:
        write_log("WARN", f"[SUDO NEEDED] PID {pid} — access denied, attempting sudo kill.")
        try:
            subprocess.run(["sudo", "-n", "kill", "-15", str(pid)], check=True)
            write_log("INFO", f"[SUDO KILL] PID {pid} terminated via sudo.")
            return jsonify({"status": "sudo_killed", "pid": pid})
        except Exception as e:
            write_log("ERROR", f"Sudo kill failed for PID {pid}: {e}")
            return jsonify({"status": "error", "reason": "Access denied even with sudo."})

@app.route("/api/autokill", methods=["POST"])
def api_autokill():
    data      = request.get_json()
    threshold = float(data.get("threshold", 50))
    killed    = []
    for p in psutil.process_iter(["pid","name","cpu_percent","memory_percent"]):
        try:
            if p.info["name"] in CRITICAL:
                continue
            if (p.info.get("cpu_percent") or 0) >= threshold or \
               (p.info.get("memory_percent") or 0) >= threshold:
                p.terminate()
                write_log("INFO", f"[AUTO KILL] PID {p.pid} ({p.info['name']}) — exceeded threshold {threshold}%")
                killed.append({"pid": p.pid, "name": p.info["name"]})
        except Exception:
            pass
    return jsonify({"status": "done", "killed": killed})

# ── Logging API ───────────────────────────────────────────────────────────────
@app.route("/api/logs")
def api_logs():
    level = request.args.get("level", "ALL")
    n     = int(request.args.get("n", 100))
    lines = read_log_lines(n, level)
    return jsonify({"lines": lines, "count": len(lines)})

@app.route("/api/logs/rotate", methods=["POST"])
def api_rotate():
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
        ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dest = os.path.join(ARCHIVE_DIR, f"procguard_{ts}.log")
        shutil.move(LOG_FILE, dest)
        write_log("INFO", f"Manual log rotation → {os.path.basename(dest)}")
        return jsonify({"status": "rotated", "archive": os.path.basename(dest)})
    return jsonify({"status": "skipped", "reason": "Log file empty or not found."})

@app.route("/api/logs/archives")
def api_log_archives():
    files = sorted(glob.glob(os.path.join(ARCHIVE_DIR, "*.log")), reverse=True)
    return jsonify([{"name": os.path.basename(f),
                     "size_kb": round(os.path.getsize(f)/1024, 1),
                     "modified": datetime.datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M:%S")}
                    for f in files])

@app.route("/api/logs/archive/<filename>")
def api_log_archive_view(filename):
    path = os.path.join(ARCHIVE_DIR, filename)
    if not os.path.exists(path):
        return jsonify({"error": "Not found"}), 404
    with open(path) as f:
        lines = f.readlines()[-100:]
    return jsonify({"lines": [l.rstrip() for l in lines]})

# ── Report API ────────────────────────────────────────────────────────────────
@app.route("/api/report/generate", methods=["POST"])
def api_report_generate():
    text = generate_report()
    return jsonify({"status": "generated", "report": text})

@app.route("/api/report/current")
def api_report_current():
    if not os.path.exists(REPORT_FILE):
        return jsonify({"report": "No report generated yet. Click 'Generate Report'."})
    with open(REPORT_FILE) as f:
        return jsonify({"report": f.read()})

@app.route("/api/report/archives")
def api_report_archives():
    files = sorted(glob.glob(os.path.join(REP_ARCH_DIR, "*.txt")), reverse=True)
    return jsonify([{"name": os.path.basename(f),
                     "size_kb": round(os.path.getsize(f)/1024, 1),
                     "modified": datetime.datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M:%S")}
                    for f in files])

# ── ✅ NEW: Report Download API ───────────────────────────────────────────────
@app.route("/api/report/download")
def api_report_download():
    if not os.path.exists(REPORT_FILE):
        return jsonify({"error": "No report found. Generate one first."}), 404
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return send_file(
        REPORT_FILE,
        as_attachment=True,
        download_name=f"procguard_report_{ts}.txt",
        mimetype="text/plain"
    )

@app.route("/api/report/archive/download/<filename>")
def api_report_archive_download(filename):
    # Security: prevent path traversal
    filename = os.path.basename(filename)
    path = os.path.join(REP_ARCH_DIR, filename)
    if not os.path.exists(path):
        return jsonify({"error": "File not found."}), 404
    return send_file(
        path,
        as_attachment=True,
        download_name=filename,
        mimetype="text/plain"
    )

# ── Directory Status API ──────────────────────────────────────────────────────
@app.route("/api/dirs")
def api_dirs():
    def dir_info(path):
        if not os.path.exists(path):
            return {"exists": False, "files": 0, "size_kb": 0}
        files = os.listdir(path)
        total = sum(os.path.getsize(os.path.join(path,f))
                    for f in files if os.path.isfile(os.path.join(path,f)))
        return {"exists": True, "files": len(files), "size_kb": round(total/1024,1)}

    log_size = os.path.getsize(LOG_FILE) if os.path.exists(LOG_FILE) else 0
    return jsonify({
        "logs":         dir_info(os.path.join(BASE_DIR,"logs")),
        "logs_archive": dir_info(ARCHIVE_DIR),
        "reports":      dir_info(os.path.join(BASE_DIR,"reports")),
        "rep_archive":  dir_info(REP_ARCH_DIR),
        "log_size_kb":  round(log_size/1024,1),
        "log_max_kb":   round(MAX_LOG_BYTES/1024,1),
        "log_pct":      round(log_size/MAX_LOG_BYTES*100,1) if MAX_LOG_BYTES else 0
    })

# ── Critical Process List API ─────────────────────────────────────────────────
@app.route("/api/critical")
def api_critical():
    running = []
    for name in CRITICAL:
        found = any(p.info["name"] == name
                    for p in psutil.process_iter(["name"])
                    if p.info.get("name"))
        running.append({"name": name, "running": found})
    return jsonify(running)

if __name__ == "__main__":
    ensure_dirs()
    # Start the real-time process watcher thread
    threading.Thread(target=process_watcher_thread, daemon=True).start()
    write_log("INFO", "ProcGuard web server started.")
    app.run(debug=True, host="0.0.0.0", port=5000)