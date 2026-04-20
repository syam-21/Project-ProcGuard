#!/bin/bash

# Real-time process watcher for ProcGuard
# Monitors for new processes and triggers actions/notifications

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/logger.sh"
source "$SCRIPT_DIR/../config.conf"

RED='\033[0;31m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

watch_processes_realtime() {
    log_message "INFO" "Real-time process watcher started."
    echo -e "${BOLD}${YELLOW}🚀 Real-time Process Watcher Active (Detecting ALL new processes)...${NC}"
    
    # Store current PIDs
    local existing_pids=$(ps -eo pid --no-headers | xargs)
    
    while true; do
        local current_pids=$(ps -eo pid --no-headers | xargs)
        
        # Find new PIDs
        for pid in $current_pids; do
            if [[ ! " $existing_pids " =~ " $pid " ]]; then
                # New PID detected
                if ps -p "$pid" > /dev/null 2>&1; then
                    local comm=$(ps -p "$pid" -o comm=)
                    local comm_lower=$(echo "$comm" | tr '[:upper:]' '[:lower:]')
                    
                    # Notify for EVERY new process
                    echo -e "${BOLD}${BLUE}✨ [NEW] ${comm^^} started (PID $pid)${NC}"
                    log_message "INFO" "✨ [NEW] ${comm^^} started (PID $pid)"
                    
                    # Extra alert if it's a watched process
                    IFS=',' read -ra WATCHED <<< "$WATCHED_PROCESSES"
                    for wp in "${WATCHED[@]}"; do
                        if [[ "$comm_lower" == *"$wp"* ]]; then
                            echo -e "${BOLD}${RED}🚨 [WATCHER] Critical Watchlist App: ${comm^^} detected!${NC}"
                        fi
                    done
                fi
            fi
        done
        
        existing_pids="$current_pids"
        sleep 0.5 # Fast polling
    done
}
