#!/usr/bin/env python3
"""
View and analyze monitoring logs.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

LOG_FILE = Path.home() / ".monitoring_logs.jsonl"

def view_logs(days=7):
    """View logs from the last N days."""
    if not LOG_FILE.exists():
        print("No log file found.")
        return
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    print(f"\n=== Activity Logs (Last {days} days) ===\n")
    
    with open(LOG_FILE, 'r') as f:
        entries = []
        for line in f:
            try:
                entry = json.loads(line)
                timestamp = datetime.fromisoformat(entry['timestamp'])
                if timestamp >= cutoff_date:
                    entries.append((timestamp, entry['content']))
            except json.JSONDecodeError:
                continue
    
    if not entries:
        print(f"No entries found in the last {days} days.")
        return
    
    # Sort by timestamp
    entries.sort(key=lambda x: x[0])
    
    current_date = None
    for timestamp, content in entries:
        # Print date header if it's a new day
        date = timestamp.date()
        if date != current_date:
            print(f"\n--- {date.strftime('%A, %B %d, %Y')} ---")
            current_date = date
        
        # Print entry
        time_str = timestamp.strftime('%H:%M')
        print(f"\n[{time_str}]")
        print(content)
    
    print(f"\n\nTotal entries: {len(entries)}")

def get_stats():
    """Get statistics about logging habits."""
    if not LOG_FILE.exists():
        print("No log file found.")
        return
    
    with open(LOG_FILE, 'r') as f:
        timestamps = []
        for line in f:
            try:
                entry = json.loads(line)
                timestamps.append(datetime.fromisoformat(entry['timestamp']))
            except json.JSONDecodeError:
                continue
    
    if not timestamps:
        print("No valid entries found.")
        return
    
    print("\n=== Logging Statistics ===\n")
    print(f"Total logs: {len(timestamps)}")
    print(f"First log: {min(timestamps).strftime('%Y-%m-%d %H:%M')}")
    print(f"Last log: {max(timestamps).strftime('%Y-%m-%d %H:%M')}")
    
    # Calculate average logs per day
    days_span = (max(timestamps).date() - min(timestamps).date()).days + 1
    avg_per_day = len(timestamps) / days_span if days_span > 0 else 0
    print(f"Average logs per day: {avg_per_day:.1f}")
    
    # Most active hours
    hour_counts = {}
    for ts in timestamps:
        hour = ts.hour
        hour_counts[hour] = hour_counts.get(hour, 0) + 1
    
    sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    print("\nMost active hours:")
    for hour, count in sorted_hours:
        print(f"  {hour:02d}:00 - {count} logs")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "stats":
            get_stats()
        else:
            try:
                days = int(sys.argv[1])
                view_logs(days)
            except ValueError:
                print("Usage: python view_logs.py [days] or python view_logs.py stats")
    else:
        view_logs()  # Default to 7 days