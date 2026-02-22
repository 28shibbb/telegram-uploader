#!/bin/bash

# Keep_alive.sh - Prevents Codespace from sleeping
# Writes a timestamp to a file every 5 minutes

echo "🔴 Keep-alive script started at $(date)"
echo "This script will run continuously to prevent Codespace from sleeping"
echo "Log file: keep_alive_log.txt"
echo ""

while true; do
    echo "$(date) - Heartbeat: Codespace is alive and running" >> keep_alive_log.txt
    echo "❤️  Heartbeat sent at $(date)"
    sleep 300  # 5 minutes
done
