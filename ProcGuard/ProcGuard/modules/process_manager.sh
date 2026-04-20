#!/bin/bash


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/logger.sh"
source "$SCRIPT_DIR/../config.conf"


RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'


terminate_process() {
    local pid="$1"
    local process_name="$2"
    local mode="${3:-manual}" 
    
    
    if ps -p "$pid" > /dev/null; then
        
        if [[ ",$CRITICAL_PROCESSES," == *",$process_name,"* ]]; then
            echo -e "${BOLD}${RED}🛡️  Error: Cannot kill a critical system process ($process_name).${NC}"
            log_message "WARN" "Attempted to kill critical process $pid ($process_name) ($mode), but was blocked."
            return 1
        fi
        
        
        if kill -9 "$pid" 2>/dev/null; then
            echo -e "${BOLD}${GREEN}🔪 Process $pid ($process_name) terminated ($mode).${NC}"
            log_message "INFO" "Terminated process $pid ($process_name) ($mode)."
            return 0
        else
            
            echo -e "${YELLOW}🔑 Insufficient permissions. Attempting to use sudo...${NC}"
            
            if sudo -n kill -9 "$pid" 2>/dev/null; then
                echo -e "${BOLD}${GREEN}🔪 Process $pid ($process_name) terminated with sudo ($mode).${NC}"
                log_message "INFO" "Terminated process $pid ($process_name) using sudo ($mode)."
                return 0
            else
                echo -e "${BOLD}${RED}❌ Error: Failed to terminate process $pid ($process_name) ($mode). Operation not permitted.${NC}"
                log_message "ERROR" "Failed to terminate process $pid ($process_name) ($mode). Operation not permitted."
                return 1
            fi
        fi
    else
        echo -e "${BOLD}${RED}❓ Error: Process with PID $pid not found.${NC}"
        return 1
    fi
}


detect_high_usage_processes() {
    echo -e "${BOLD}${YELLOW}--- 🚨 High Resource Usage Processes 🚨 ---${NC}"
    
    echo -e "${BOLD}%-7s %-7s %-7s %-7s %-s${NC}" "PID" "PPID" "MEM%" "CPU%" "COMMAND"
    ps -eo pid,ppid,%mem,%cpu,comm --sort=-%mem | awk -v cpu_limit="$CPU_THRESHOLD" -v ram_limit="$RAM_THRESHOLD" \
    'NR>1 {
        if ($3 > ram_limit || $4 > cpu_limit) {
            cmd = $5; for (i=6; i<=NF; i++) cmd = cmd " " $i;
            printf "%-7s %-7s %-7s %-7s %-s\n", $1, $2, $3, $4, cmd
        }
    }'
    echo -e "${YELLOW}-------------------------------------------${NC}"
    log_message "INFO" "Checked for high-resource-usage processes."
}


manual_kill_process() {
    read -p "Enter the PID of the process to terminate: " pid
    if [[ ! "$pid" =~ ^[0-9]+$ ]]; then
        echo -e "${RED}Error: Invalid PID. Please enter a numeric value.${NC}"
        return 1
    fi
    if ps -p "$pid" > /dev/null; then
        local process_name=$(ps -p "$pid" -o comm=)
        terminate_process "$pid" "$process_name" "manual"
    else
        echo -e "${RED}Error: Process with PID $pid not found.${NC}"
    fi
}


auto_kill_high_usage_processes() {
    log_message "INFO" "Auto-kill sequence initiated."
    
    ps -eo pid,%mem,%cpu,comm --sort=-%mem | awk -v cpu_limit="$CPU_THRESHOLD" -v ram_limit="$RAM_THRESHOLD" \
    'NR>1 {
        if ($2 > ram_limit || $3 > cpu_limit) {
            cmd = $4; for (i=5; i<=NF; i++) cmd = cmd " " $i;
            print $1, cmd
        }
    }' | while read -r pid comm; do
        
        terminate_process "$pid" "$comm" "auto"
    done
    
    log_message "INFO" "Auto-kill sequence completed."
}
