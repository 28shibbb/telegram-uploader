#!/bin/bash

# Start_uploader.sh - Main runner script

echo "========================================="
echo "Telegram Video Uploader - Starter Script"
echo "========================================="
echo "Started at: $(date)"
echo ""

# Create necessary directories
mkdir -p downloads
mkdir -p logs

# Function to check if required files exist
check_files() {
    if [ ! -f "links.txt" ]; then
        echo "⚠️  Warning: links.txt not found!"
        echo "Please upload your links.txt file to continue"
    fi
    
    if [ ! -f ".env" ]; then
        echo "⚠️  Warning: .env file not found!"
        echo "Please create .env file with your TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID"
    fi
}

# Function to show status
show_status() {
    echo ""
    echo "📊 Current Status:"
    echo "------------------"
    echo "Downloaded videos: $(ls -1 downloads/ 2>/dev/null | wc -l) files"
    echo "Uploaded videos: $(wc -l < uploaded_videos.txt 2>/dev/null || echo 0)"
    echo "Log size: $(du -h upload_log.txt 2>/dev/null | cut -f1 || echo '0B')"
    echo ""
}

# Main loop
while true; do
    echo ""
    echo "🚀 Starting uploader iteration at $(date)"
    echo "----------------------------------------"
    
    check_files
    python telegram_uploader.py
    
    show_status
    
    echo ""
    echo "✅ Iteration completed at $(date)"
    echo "⏰ Next check in 30 minutes..."
    echo "----------------------------------------"
    
    # Wait 30 minutes before next check
    sleep 1800  # 30 minutes
done
