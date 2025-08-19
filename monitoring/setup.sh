#!/bin/bash

# Setup script for the monitoring system

echo "Setting up the Activity Monitoring System..."

# Get the current directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Update the plist file with the correct path
PLIST_FILE="$SCRIPT_DIR/com.monitoring.hourly.plist"
MONITOR_SCRIPT="$SCRIPT_DIR/monitor.py"

# Make the monitor script executable
chmod +x "$MONITOR_SCRIPT"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Copy the plist to LaunchAgents
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
mkdir -p "$LAUNCH_AGENTS_DIR"

echo "Installing launch agent..."
cp "$PLIST_FILE" "$LAUNCH_AGENTS_DIR/"

# Load the launch agent
echo "Loading the launch agent..."
launchctl load "$LAUNCH_AGENTS_DIR/com.monitoring.hourly.plist"

# Check if loaded successfully
if launchctl list | grep -q "com.monitoring.hourly"; then
    echo "✓ Monitoring system installed successfully!"
    echo ""
    echo "The system will show a popup every hour to log your activities."
    echo "Logs are stored in: ~/.monitoring_logs.jsonl"
    echo ""
    echo "To test the system now, run:"
    echo "  python3 $MONITOR_SCRIPT"
    echo ""
    echo "To uninstall, run:"
    echo "  bash $SCRIPT_DIR/uninstall.sh"
else
    echo "Error: Failed to load the launch agent."
    echo "Please check the system logs for more information."
    exit 1
fi