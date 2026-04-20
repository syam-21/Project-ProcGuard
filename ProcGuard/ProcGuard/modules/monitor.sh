#!/bin/bash


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/logger.sh"
source "$SCRIPT_DIR/../config.conf"


RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' 


monitor_resources() {
    echo -e "${BOLD}${BLUE}--- 📊 System Resource Monitor 📊 ---${NC}"
    
    # CPU Usage
    if command -v top >/dev/null 2>&1; then
        CPU_IDLE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.,]*\)%* id.*/\1/" | tr ',' '.')
        CPU_USAGE=$(awk "BEGIN {print 100 - $CPU_IDLE}")
        
        COLOR=$GREEN
        [[ $(echo "$CPU_USAGE > 80" | bc -l) -eq 1 ]] && COLOR=$RED
        [[ $(echo "$CPU_USAGE > 50" | bc -l) -eq 1 && $(echo "$CPU_USAGE <= 80" | bc -l) -eq 1 ]] && COLOR=$YELLOW
        
        echo -e "${BOLD}⚡ CPU Usage: ${COLOR}${CPU_USAGE}%${NC}"
    else
        echo -e "${RED}⚡ CPU Usage: Unknown (top command missing)${NC}"
    fi
    
    # RAM Usage
    if command -v free >/dev/null 2>&1; then
        free -m | awk -v green="$GREEN" -v red="$RED" -v yellow="$YELLOW" -v nc="$NC" -v bold="$BOLD" 'NR==2{
            pct=$3*100/$2;
            color=green;
            if(pct>80) color=red; else if(pct>50) color=yellow;
            printf "%s🧠 RAM Usage: %s%s/%sMB (%.2f%%)%s\n", bold, color, $3, $2, pct, nc 
        }'
    else
        echo -e "${RED}🧠 RAM Usage: Unknown (free command missing)${NC}"
    fi
    
    # Disk Usage
    if command -v df >/dev/null 2>&1; then
        df -h | awk -v green="$GREEN" -v red="$RED" -v yellow="$YELLOW" -v nc="$NC" -v bold="$BOLD" '$NF=="/"{
            pct=substr($5, 1, length($5)-1);
            color=green;
            if(pct>80) color=red; else if(pct>50) color=yellow;
            printf "%s💾 Disk Usage: %s%s/%sGB (%s)%s\n", bold, color, $3, $2, $5, nc
        }'
    else
        echo -e "${RED}💾 Disk Usage: Unknown (df command missing)${NC}"
    fi
    
    echo -e "${BLUE}---------------------------------------${NC}"
    log_message "INFO" "Monitored system resources."
}


top_processes() {
    echo -e "${BOLD}${CYAN}--- ⚙️ Top 5 Resource-Consuming Processes ⚙️ ---${NC}"
    if command -v ps >/dev/null 2>&1; then
        echo -e "${BOLD}%-6s %-6s %-7s %-7s %-s${NC}" "PID" "PPID" "MEM%" "CPU%" "COMMAND"
        ps -eo pid,ppid,%mem,%cpu,comm --sort=-%mem | head -n 6 | awk 'NR>1 {
            cmd = $5; for (i=6; i<=NF; i++) cmd = cmd " " $i;
            printf "%-6s %-6s %-7s %-7s %-s\n", $1, $2, $3, $4, cmd
        }'
    else
        echo -e "${RED}Error: ps command missing${NC}"
    fi
    echo -e "${CYAN}-----------------------------------------------${NC}"
    log_message "INFO" "Displayed top processes."
}
