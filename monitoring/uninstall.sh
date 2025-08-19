#!/bin/bash

# Uninstall script for the monitoring system

echo "Uninstalling the Activity Monitoring System..."

LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_NAME="com.monitoring.hourly.plist"

# Unload the launch agent
if launchctl list | grep -q "com.monitoring.hourly"; then
    echo "Unloading launch agent..."
    launchctl unload "$LAUNCH_AGENTS_DIR/$PLIST_NAME"
fi

# Remove the plist file
if [ -f "$LAUNCH_AGENTS_DIR/$PLIST_NAME" ]; then
    echo "Removing launch agent file..."
    rm "$LAUNCH_AGENTS_DIR/$PLIST_NAME"
fi

echo "✓ Monitoring system uninstalled."
echo ""
echo "Note: Your log file (~/.monitoring_logs.jsonl) has been preserved."
echo "Delete it manually if you want to remove all data."