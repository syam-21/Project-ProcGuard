#!/bin/bash


ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"


if [[ -f "$ROOT_DIR/config.conf" ]]; then
    source "$ROOT_DIR/config.conf"
else
    echo "Error: Configuration file config.conf not found."
    exit 1
fi


source "$ROOT_DIR/modules/logger.sh"
source "$ROOT_DIR/modules/monitor.sh"
source "$ROOT_DIR/modules/process_manager.sh"
source "$ROOT_DIR/modules/report.sh"
source "$ROOT_DIR/modules/process_watcher.sh"


RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' 


live_monitor() {
    while true; do
        clear
        echo -e "${BOLD}${BLUE}╔══════════════════════════════════════════════╗${NC}"
        echo -e "${BOLD}${BLUE}║        🚀 Live System Dashboard 🚀           ║${NC}"
        echo -e "${BOLD}${BLUE}╚══════════════════════════════════════════════╝${NC}"
        echo -e "${YELLOW}       (Press any key to return to menu)       ${NC}"
        echo ""
        monitor_resources
        echo ""
        top_processes
        
        read -t 2 -n 1 && break
    done
}

main_menu() {
    while true; do
        clear
        echo -e "${BOLD}${CYAN}=============================================${NC}"
        echo -e "${BOLD}${CYAN}    🛡️  ProcGuard - System Monitoring Tool    ${NC}"
        echo -e "${BOLD}${CYAN}=============================================${NC}"
        echo -e "${BOLD} 1. ${NC} 📊 View System Resources"
        echo -e "${BOLD} 2. ${NC} ⚙️  View Top 5 Processes"
        echo -e "${BOLD} 3. ${NC} 🚀 Live Monitoring Dashboard (Auto-Refresh)"
        echo -e "${BOLD} 4. ${NC} 🚨 List High-Usage Processes"
        echo -e "${BOLD} 5. ${NC} 🔪 Terminate a Process Manually"
        echo -e "${BOLD} 6. ${NC} 🤖 Run Auto-Kill for High-Usage Processes"
        echo -e "${BOLD} 7. ${NC} 📡 Start Real-time Process Watcher"
        echo -e "${BOLD} 8. ${NC} 📈 Generate Performance Report"
        echo -e "${BOLD} 9. ${NC} 🚪 Exit"
        echo -e "${CYAN}---------------------------------------------${NC}"
        read -p "Enter your choice: " choice

        case $choice in
            1) monitor_resources; echo -e "\nPress Enter to continue..."; read;;
            2) top_processes; echo -e "\nPress Enter to continue..."; read;;
            3) live_monitor;;
            4) detect_high_usage_processes; echo -e "\nPress Enter to continue..."; read;;
            5) manual_kill_process; echo -e "\nPress Enter to continue..."; read;;
            6) auto_kill_high_usage_processes; echo -e "${BOLD}${GREEN}Auto-kill complete.${NC}"; echo -e "\nPress Enter to continue..."; read;;
            7) watch_processes_realtime;;
            8) generate_report; echo -e "\nPress Enter to continue..."; read;;
            9) echo -e "${BOLD}${BLUE}Goodbye! 👋${NC}"; exit 0;;
            *) echo -e "${RED}Invalid option. Please try again.${NC}"; sleep 1;;
        esac
    done
}


if [[ "$1" == "--automate" ]]; then
    
    log_message "INFO" "Running in automated mode."
    auto_kill_high_usage_processes
else
    
    main_menu
fi
