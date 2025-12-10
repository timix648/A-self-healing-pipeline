#!/bin/bash

# Configuration
LOG_FILE="build.log"

echo "[INFO] Starting Sentinel (Self-Healing Watchdog)..."

while true; do
    echo "----------------------------------------"
    echo "[INFO] Running Build Check..."
    
    # 1. Run the build script
    ./run_build.sh
    
    # Check the exit code of the build script (0 = Success, anything else = Failure)
    if [ $? -ne 0 ]; then
        echo "[ERROR] BUILD FAILURE DETECTED!"
        echo "[INFO] Activating Gemini Auto-Fixer..."
        
        # 2. RUN THE PYTHON AGENT (Using the VENV)
        # This points explicitly to your virtual environment python
        ./venv/bin/python3 auto_fixer.py
        
        echo "[INFO] Waiting for repairs to take effect..."
    else
        echo "[SUCCESS] System is healthy."
    fi
    
    # Sleep for 10 seconds before checking again
    sleep 10
done