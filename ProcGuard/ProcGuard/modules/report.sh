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


generate_report() {
    
    local report_dir=$(dirname "$REPORT_FILE")
    [[ ! -d "$report_dir" ]] && mkdir -p "$report_dir"
    
    echo -e "${BOLD}${BLUE}--- 📈 Performance Summary Report 📈 ---${NC}"
    
    echo "╔══════════════════════════════════════════════╗" > "$REPORT_FILE"
    echo "║        ProcGuard Performance Report          ║" >> "$REPORT_FILE"
    echo "╚══════════════════════════════════════════════╝" >> "$REPORT_FILE"
    echo "Generated on: $(date)" >> "$REPORT_FILE"
    echo "------------------------------------------------" >> "$REPORT_FILE"
    
    if [[ -f "$LOG_FILE" ]]; then
        
        local total_events=$(grep -c "^\[[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}" "$LOG_FILE")
        echo "Total logged events: $total_events" >> "$REPORT_FILE"
        
        
        local manual_terminated=$(grep -c "(manual)" "$LOG_FILE" 2>/dev/null || echo 0)
        local auto_terminated=$(grep -c "(auto)" "$LOG_FILE" 2>/dev/null || echo 0)
        
        echo "Total manual terminations: $manual_terminated" >> "$REPORT_FILE"
        echo "Total automatic terminations: $auto_terminated" >> "$REPORT_FILE"
        
        
        local sudo_terminations=$(grep -c "using sudo" "$LOG_FILE")
        echo "Total sudo-privileged terminations: $sudo_terminations" >> "$REPORT_FILE"
        
        
        local warnings=$(grep -c "\[WARN" "$LOG_FILE")
        echo "Total system warnings: $warnings" >> "$REPORT_FILE"
    else
        echo "No log file found at $LOG_FILE" >> "$REPORT_FILE"
        echo "Total logged events: 0" >> "$REPORT_FILE"
        echo "Total manual terminations: 0" >> "$REPORT_FILE"
        echo "Total automatic terminations: 0" >> "$REPORT_FILE"
    fi
    
    echo "------------------------------------------------" >> "$REPORT_FILE"
    echo -e "${GREEN}✅ Report generated successfully at $REPORT_FILE${NC}"
    
    echo -e "${YELLOW}Report Preview:${NC}"
    cat "$REPORT_FILE"
    
    log_message "INFO" "Generated performance report."
}
