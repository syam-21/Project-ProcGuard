#!/bin/bash


SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../config.conf"


if [[ -f "$CONFIG_FILE" ]]; then
    source "$CONFIG_FILE"
else
    
    LOG_FILE="$HOME/Desktop/ProcGuard/logs/procguard.log"
    LOG_MAX_SIZE=5242880
fi


ensure_log_dir() {
    local log_dir=$(dirname "$LOG_FILE")
    if [[ ! -d "$log_dir" ]]; then
        mkdir -p "$log_dir"
    fi
}


rotate_log() {
    
    if [[ -f "$LOG_FILE" && $(stat -c%s "$LOG_FILE") -gt "$LOG_MAX_SIZE" ]]; then
        local timestamp=$(date '+%Y%m%d-%H%M%S')
        local archive_file="${LOG_FILE%*.log}-${timestamp}.log.gz"
        
        
        gzip -c "$LOG_FILE" > "$archive_file"
        
        
        > "$LOG_FILE"
        
        
        log_message "INFO" "Log rotated. Archive created at $archive_file"
    fi
}


log_message() {
    local level="${1:-INFO}"
    local message="$2"
    
    
    ensure_log_dir
    
   
    rotate_log
    
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    
    local level_padded=$(printf "%-5s" "$level")
    
    echo "[$timestamp] [$level_padded] $message" >> "$LOG_FILE"
}
