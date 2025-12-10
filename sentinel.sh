mkdir -p shared
LOG_FILE="build.log"
KESTRA_LOG="shared/kestra_errors.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

write_status() {
    echo -e "${2}[$(date +'%H:%M:%S')] :: ${1}${NC}"
}

clear
write_status "INITIALIZING PROJECT 1 PIPELINE..." "$CYAN"
write_status "TARGETS: Infinity Build, Wakanda Data, Captain Code" "$CYAN"
echo "---------------------------------------------------"

# Clear logs to start fresh
echo "" > $LOG_FILE
echo "" > $KESTRA_LOG

while true; do
    echo -n -e "${NC}."

    if grep -q "Error" "$LOG_FILE"; then
        
        if grep -q "layout.tsx" "$LOG_FILE"; then
            BROKEN_FILE="layout.tsx"
        elif grep -q "page.tsx" "$LOG_FILE"; then
            BROKEN_FILE="page.tsx"
        else
            BROKEN_FILE="unknown file"
        fi

        echo ""
        echo -e "${RED}---------------------------------------------------${NC}"
        write_status "CRITICAL FAILURE DETECTED IN ${BROKEN_FILE}" "$RED"

        # EXPORT LOGS FOR MCP
        tail -n 20 "$LOG_FILE" > "$KESTRA_LOG"
        write_status "LOGS EXPORTED TO SHARED/KESTRA_ERRORS.LOG" "$YELLOW"

        
        write_status "DISPATCHING CLINE AGENT..." "$YELLOW"

        BRANCH_NAME="fix/auto-repair-$(date +%s)"
        
        cline "CRITICAL ALERT: Build failed in ${BROKEN_FILE}.
        
        MISSION PROTOCOL:
        1. DIAGNOSE: Use the 'read_deployment_logs' tool (KestraBridge) to analyze the error in 'shared/kestra_errors.log'.
        2. FIX: Repair the syntax error in ${BROKEN_FILE}.
        3. VERIFY: Run './run_build.sh' to ensure the fix works.
        4. DEPLOY (Captain Code):
           - Create a new branch: git checkout -b ${BRANCH_NAME}
           - Stage and Commit: git add ${BROKEN_FILE} && git commit -m 'fix: automated repair of ${BROKEN_FILE}'
           - Push: git push origin ${BRANCH_NAME}
           
        Report status when done."
        
        echo "" > $LOG_FILE
        echo "" > $KESTRA_LOG
        write_status "WAITING FOR NEXT CYCLE..." "$GREEN"
        echo -e "${NC}---------------------------------------------------"
    fi
    
    sleep 2
done