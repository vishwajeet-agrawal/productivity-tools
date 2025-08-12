# Setting up background notifications with ntfy (macOS & Linux)

**Note: Linux guide is not verified.**


This guide covers:
1. Installing ntfy
2. A subscription script
3. Running it automatically on startup
4. Testing/verification

## 1) Install ntfy

### macOS

```bash
# Homebrew (recommended)
brew install ntfy
```

### Linux (Debian/Ubuntu)

```bash
# Official APT repo (recommended)
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://archive.heckel.io/apt/pubkey.txt | sudo gpg --dearmor -o /etc/apt/keyrings/archive.heckel.io.gpg
echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/archive.heckel.io.gpg] https://archive.heckel.io/apt debian main" | sudo tee /etc/apt/sources.list.d/archive.heckel.io.list
sudo apt update
sudo apt install ntfy

# For desktop pop-ups:
sudo apt install libnotify-bin  # provides `notify-send`
```

### Other Linux distros

Use your distro's package manager if available, or download the static binary release and place it in `/usr/local/bin/ntfy` (chmod +x).

Ensure a notification tool exists (e.g., `notify-send`).

## 2) Subscription Script

The script listens on an ntfy topic and, for each incoming message, shows a desktop notification, plays a sound, and appends a line to `~/jobs.txt`.

Set your topic once:

```bash
export NTFY_TOPIC="my_job_topic"
```

### macOS — `~/bin/ntfy_subscriber.sh`

```bash
#!/usr/bin/env bash
# Logs
exec >>/tmp/ntfysub.out 2>>/tmp/ntfysub.err

# Find Homebrew tools
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

topic="${NTFY_TOPIC:-my_job_topic}"

# Show native banner with sound + append to log file
ntfy subscribe "$topic" \
'osascript -e "display notification \"$m\" with title \"$t\" sound name \"Glass\"" && \
 afplay /System/Library/Sounds/Ping.aiff && \
 printf "%s\t%s\t%s\n" "$(date +%F" "%T)" "$t" "$m" >> "$HOME/jobs.txt"'
```

```bash
mkdir -p ~/bin
chmod +x ~/bin/ntfy_subscriber.sh
```

### Linux — `~/.local/bin/ntfy_subscriber.sh`

```bash
#!/usr/bin/env bash
# Logs
exec >>/tmp/ntfysub.out 2>>/tmp/ntfysub.err

export PATH="/usr/local/bin:/usr/bin:/bin"

topic="${NTFY_TOPIC:-my_job_topic}"

# Desktop notification + optional sound + append to log file
ntfy subscribe "$topic" \
'notify-send "$t" "$m" && \
 (command -v canberra-gtk-play >/dev/null && canberra-gtk-play -i complete || true) && \
 printf "%s\t%s\t%s\n" "$(date +%F" "%T)" "$t" "$m" >> "$HOME/jobs.txt"'
```

```bash
mkdir -p ~/.local/bin
chmod +x ~/.local/bin/ntfy_subscriber.sh
```

## 3) Run Automatically on Startup

### macOS (LaunchAgent, starts at login)

Create `~/Library/LaunchAgents/com.example.ntfysub.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
 "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key>             <string>com.example.ntfysub</string>
  <key>ProgramArguments</key>  <array>
    <string>/Users/REPLACE_WITH_YOUR_USERNAME/bin/ntfy_subscriber.sh</string>
  </array>
  <key>RunAtLoad</key>         <true/>
  <key>KeepAlive</key>         <true/>
  <key>StandardInPath</key>    <string>/dev/null</string>
  <key>StandardOutPath</key>   <string>/tmp/ntfysub.out</string>
  <key>StandardErrorPath</key> <string>/tmp/ntfysub.err</string>
</dict></plist>
```

Load and persist:

```bash
launchctl load -w ~/Library/LaunchAgents/com.example.ntfysub.plist
```

**Notes:**
- Use absolute paths (no `~` or `$HOME`) in plists.
- For pre-login startup use a LaunchDaemon in `/Library/LaunchDaemons`, but GUI notifications require a user session, so prefer LaunchAgent.

### Linux (systemd user service, starts at login; "linger" to run after boot)

Create `~/.config/systemd/user/ntfy-sub.service`:

```ini
[Unit]
Description=ntfy subscriber

[Service]
ExecStart=%h/.local/bin/ntfy_subscriber.sh
Restart=always
RestartSec=2

[Install]
WantedBy=default.target
```

Enable and start:

```bash
systemctl --user daemon-reload
systemctl --user enable --now ntfy-sub.service
```

Optional (keep it running across reboots without an interactive login):

```bash
loginctl enable-linger "$USER"
```

**Notes:**
- Desktop pop-ups (`notify-send`) require a running notification daemon in your user session. With lingering before login, notifications may be deferred or dropped until the session exists; logs still capture messages.

## 4) Example and Verification

### Send test messages

```bash
# From anywhere:
curl -d "hello from curl" -H 'Title: Smoke test' "https://ntfy.sh/$NTFY_TOPIC"

# Or via CLI:
ntfy publish "$NTFY_TOPIC" "hello from CLI" --title "Smoke test"
```

### Verify subscriber is running

#### macOS

```bash
launchctl list com.example.ntfysub
# Look for a PID (running) and LastExitStatus=0
tail -f /tmp/ntfysub.out /tmp/ntfysub.err
```

#### Linux

```bash
systemctl --user status ntfy-sub
journalctl --user -u ntfy-sub -f
```

### Verify outputs

```bash
# You should see a desktop notification
# You should hear the configured sound
tail -n 5 ~/jobs.txt             # recent appended lines (timestamp, title, message)
```

## Troubleshooting

- **command not found:** ensure ntfy is installed and PATH is set inside the script.
- **No notification sound on Linux:** install libcanberra (`canberra-gtk-play`) or use `paplay` with a .wav file you have.
- **Script not starting on macOS:** confirm the plist path and use `launchctl unload` then `launchctl load -w` after edits.
- **For different topics per machine:** override `NTFY_TOPIC` in your shell profile or at the top of the scripts.