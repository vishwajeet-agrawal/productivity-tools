#!/usr/bin/env python3
"""
Self-monitoring system with hourly popup for activity logging.
"""

import tkinter as tk
from tkinter import scrolledtext
import os
import json
from datetime import datetime
from pathlib import Path
import threading

# Configuration
LOG_FILE = Path.home() / ".monitoring_logs.jsonl"
DEFAULT_DISPLAY_ENTRIES = 2
DEFAULT_PREVIEW_LENGTH = 300
TIMEOUT_MINUTES = 15


class MonitoringPopup:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Activity Monitor")
        self.root.geometry("700x500")
        
        # Make window stay on top
        self.root.attributes('-topmost', True)
        self.root.lift()
        self.root.focus_force()
        
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Create UI elements
        self.create_widgets()
        
        # Load and display recent entries
        self.display_recent_entries()
        
        # Set focus to text input
        self.text_input.focus_set()
        
        # Bind keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
        # Set timeout for auto-close
        self.setup_timeout()
        
        # Center window on screen
        self.center_window()
    
    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create the UI elements."""
        # Title and time since last log
        header_frame = tk.Frame(self.root)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        
        last_log_time = self.get_last_log_time()
        if last_log_time:
            time_diff = datetime.now() - last_log_time
            hours = int(time_diff.total_seconds() / 3600)
            minutes = int((time_diff.total_seconds() % 3600) / 60)
            if hours > 0:
                time_text = f"Time since last log: {hours} hour{'s' if hours != 1 else ''} {minutes} minute{'s' if minutes != 1 else ''}"
            else:
                time_text = f"Time since last log: {minutes} minute{'s' if minutes != 1 else ''}"
        else:
            time_text = "No previous logs found"
        
        tk.Label(header_frame, text=time_text, font=("Arial", 12, "bold")).pack(anchor="w")
        
        # Recent entries display
        recent_frame = tk.LabelFrame(self.root, text="Recent Entries", padx=10, pady=5)
        recent_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        recent_frame.grid_columnconfigure(0, weight=1)
        recent_frame.grid_rowconfigure(0, weight=1)
        
        self.recent_text = scrolledtext.ScrolledText(
            recent_frame, 
            height=8, 
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg="#f5f5f5"
        )
        self.recent_text.grid(row=0, column=0, sticky="nsew")
        
        # Current log input
        input_frame = tk.LabelFrame(self.root, text="Log Current Activity", padx=10, pady=5)
        input_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        input_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_rowconfigure(0, weight=1)
        
        self.text_input = scrolledtext.ScrolledText(
            input_frame,
            height=6,
            wrap=tk.WORD,
            font=("Arial", 11)
        )
        self.text_input.grid(row=0, column=0, sticky="nsew")
        
        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=3, column=0, pady=10)
        
        tk.Button(
            button_frame, 
            text="Log", 
            command=self.submit_log,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame, 
            text="Cancel", 
            command=self.cancel,
            bg="#f44336",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        # Instructions
        instructions = tk.Label(
            self.root,
            text="Press Enter to submit | Shift+Enter for new line | ESC to cancel",
            font=("Arial", 9),
            fg="gray"
        )
        instructions.grid(row=4, column=0, pady=5)
    
    def setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts."""
        # Enter to submit (but not Shift+Enter)
        self.text_input.bind('<Return>', self.handle_enter)
        # ESC to cancel
        self.root.bind('<Escape>', lambda e: self.cancel())
    
    def handle_enter(self, event):
        """Handle Enter key press - submit unless Shift is held."""
        if not event.state & 0x0001:  # Check if Shift is not pressed
            self.submit_log()
            return 'break'  # Prevent default behavior
        # If Shift is pressed, allow default behavior (new line)
        return None
    
    def setup_timeout(self):
        """Set up auto-close timeout."""
        def timeout_close():
            self.cancel()
        
        self.timeout_timer = threading.Timer(TIMEOUT_MINUTES * 60, timeout_close)
        self.timeout_timer.daemon = True
        self.timeout_timer.start()
    
    def get_last_log_time(self):
        """Get the timestamp of the last log entry."""
        if not LOG_FILE.exists():
            return None
        
        try:
            with open(LOG_FILE, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_entry = json.loads(lines[-1])
                    return datetime.fromisoformat(last_entry['timestamp'])
        except Exception:
            pass
        
        return None
    
    def display_recent_entries(self):
        """Display recent log entries."""
        if not LOG_FILE.exists():
            self.recent_text.config(state=tk.NORMAL)
            self.recent_text.insert(tk.END, "No previous entries found.")
            self.recent_text.config(state=tk.DISABLED)
            return
        
        try:
            with open(LOG_FILE, 'r') as f:
                lines = f.readlines()
                
            # Get last N entries
            recent_entries = []
            for line in reversed(lines[-DEFAULT_DISPLAY_ENTRIES:]):
                try:
                    entry = json.loads(line)
                    recent_entries.append(entry)
                except json.JSONDecodeError:
                    continue
            
            # Display entries (reverse to show most recent last)
            self.recent_text.config(state=tk.NORMAL)
            for entry in reversed(recent_entries):
                timestamp = datetime.fromisoformat(entry['timestamp'])
                content = entry['content'][:DEFAULT_PREVIEW_LENGTH]
                if len(entry['content']) > DEFAULT_PREVIEW_LENGTH:
                    content += "..."
                
                display_text = f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}]\n{content}\n\n"
                self.recent_text.insert(tk.END, display_text)
            
            self.recent_text.config(state=tk.DISABLED)
            
        except Exception as e:
            self.recent_text.config(state=tk.NORMAL)
            self.recent_text.insert(tk.END, f"Error loading recent entries: {str(e)}")
            self.recent_text.config(state=tk.DISABLED)
    
    def submit_log(self):
        """Submit the log entry."""
        content = self.text_input.get("1.0", tk.END).strip()
        
        if not content:
            # Don't log empty entries
            self.cancel()
            return
        
        # Create log entry
        entry = {
            'timestamp': datetime.now().isoformat(),
            'content': content
        }
        
        # Append to log file
        try:
            LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(LOG_FILE, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            # Show error in a simple message box
            error_window = tk.Toplevel(self.root)
            error_window.title("Error")
            error_window.geometry("300x100")
            tk.Label(error_window, text=f"Error saving log:\n{str(e)}").pack(pady=20)
            tk.Button(error_window, text="OK", command=error_window.destroy).pack()
            return
        
        # Cancel timeout timer
        if hasattr(self, 'timeout_timer'):
            self.timeout_timer.cancel()
        
        # Close window
        self.root.destroy()
    
    def cancel(self):
        """Cancel without logging."""
        # Cancel timeout timer
        if hasattr(self, 'timeout_timer'):
            self.timeout_timer.cancel()
        
        self.root.destroy()
    
    def run(self):
        """Run the popup window."""
        self.root.mainloop()


def main():
    """Main entry point."""
    popup = MonitoringPopup()
    popup.run()


if __name__ == "__main__":
    main()
