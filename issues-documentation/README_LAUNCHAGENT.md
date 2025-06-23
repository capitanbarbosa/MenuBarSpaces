# Overlay Menu Bar - LaunchAgent Setup

This document explains how to set up the Overlay Menu Bar application to run automatically at boot using macOS LaunchAgent.

## Overview

The Overlay Menu Bar is a Python application that creates a custom menu bar overlay with desktop workspace switching functionality. It uses:
- **yabai** for detecting the current desktop/space
- **AppleScript** for switching between desktops
- **PyObjC** for the macOS GUI interface

## LaunchAgent Configuration

The application runs as a LaunchAgent using the configuration file:
`/Users/wiz/Library/LaunchAgents/com.overlay.menubar.plist`

### Key Configuration Elements

```xml
<key>EnvironmentVariables</key>
<dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>HOME</key>
    <string>/Users/wiz</string>
</dict>
<key>WorkingDirectory</key>
<string>/Users/wiz/coding/backburner/Active-Top-menu-bar_mac/python</string>
```

## Common Issue: Desktop Sync Not Working at Boot

### Problem Description
When the application runs from a terminal (VS Code, Terminal.app), the desktop highlighting works perfectly and stays in sync when switching desktops via gestures or Mission Control. However, when running at boot via LaunchAgent, the desktop switching works but the highlight colors don't sync with gesture-based desktop changes.

### Root Cause
LaunchAgents run with a limited environment that differs from user terminal sessions:

1. **Limited PATH**: The LaunchAgent environment doesn't include `/opt/homebrew/bin` where yabai is typically installed
2. **Missing Environment Variables**: HOME and other environment variables may not be set
3. **Different Working Directory**: The script may not run from the expected directory

### Solution

#### 1. Update LaunchAgent Plist
Add proper environment variables to the plist file:

```xml
<key>EnvironmentVariables</key>
<dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>HOME</key>
    <string>/Users/wiz</string>
</dict>
<key>WorkingDirectory</key>
<string>/Users/wiz/coding/backburner/Active-Top-menu-bar_mac/python</string>
```

#### 2. Update Python Code for Robust yabai Detection
Modify the `query_current_workspace()` function to try multiple paths:

```python
def query_current_workspace(self):
    """Query the current active workspace (desktop/space) using yabai."""
    import subprocess
    import json
    import os
    
    # Try different possible paths for yabai
    yabai_paths = [
        "/opt/homebrew/bin/yabai",
        "/usr/local/bin/yabai", 
        "yabai"  # fallback to PATH
    ]
    
    yabai_cmd = None
    for path in yabai_paths:
        if os.path.exists(path) or path == "yabai":
            yabai_cmd = path
            break
    
    if not yabai_cmd:
        print("[Pager] yabai not found in common locations")
        return None
        
    try:
        result = subprocess.run(
            [yabai_cmd, "-m", "query", "--spaces", "--space"],
            capture_output=True, text=True, check=True, timeout=2
        )
        data = json.loads(result.stdout)
        current_space = data.get("index")
        print(f"[Pager] yabai reports current space: {current_space}")
        return current_space
    except FileNotFoundError:
        print(f"[Pager] yabai command not found: {yabai_cmd}")
        return None
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        print(f"[Pager] Error with yabai: {e}")
        return None
```

## Installation Steps

1. **Place the LaunchAgent plist file:**
   ```bash
   cp com.overlay.menubar.plist ~/Library/LaunchAgents/
   ```

2. **Load the LaunchAgent:**
   ```bash
   launchctl load ~/Library/LaunchAgents/com.overlay.menubar.plist
   ```

3. **Verify it's running:**
   ```bash
   launchctl list | grep com.overlay.menubar
   ```

## Troubleshooting

### Check Logs
Monitor the application logs for errors:
```bash
tail -f /tmp/overlay_menubar.out.log
tail -f /tmp/overlay_menubar.err.log
```

### Expected Log Output (Working)
```
[Pager] yabai reports current space: 1
[Pager] yabai reports current space: 1
```

### Error Log Output (Not Working)
```
[Pager] yabai is not installed or not in PATH.
[Pager] yabai not found in common locations
```

### Restart the Service
```bash
launchctl unload ~/Library/LaunchAgents/com.overlay.menubar.plist
launchctl load ~/Library/LaunchAgents/com.overlay.menubar.plist
```

### Clear Cache and Restart
```bash
# Stop service
launchctl unload ~/Library/LaunchAgents/com.overlay.menubar.plist

# Kill any existing processes
pkill -f overlay_menu_bar.py

# Clear Python cache
find /Users/wiz/coding/backburner/Active-Top-menu-bar_mac/python -name "*.pyc" -delete
find /Users/wiz/coding/backburner/Active-Top-menu-bar_mac/python -name "__pycache__" -type d -exec rm -rf {} +

# Clear logs
rm -f /tmp/overlay_menubar.out.log /tmp/overlay_menubar.err.log

# Restart service
launchctl load ~/Library/LaunchAgents/com.overlay.menubar.plist
```

## Dependencies

- **yabai**: Window manager for macOS
  ```bash
  brew install yabai
  ```

- **Python dependencies**: See `requirements.txt`
  ```bash
  pip install -r requirements.txt
  ```

## Permissions Required

The application requires the following macOS permissions:
- **Accessibility**: For global hotkeys and desktop switching
- **Input Monitoring**: For detecting keyboard input

Grant these permissions in:
**System Settings > Privacy & Security > Accessibility**
**System Settings > Privacy & Security > Input Monitoring**

## File Structure

```
/Users/wiz/coding/backburner/Active-Top-menu-bar_mac/python/
├── overlay_menu_bar.py          # Main application
├── run_venv.sh                  # Virtual environment launcher
├── requirements.txt             # Python dependencies
└── venv/                       # Python virtual environment

/Users/wiz/Library/LaunchAgents/
└── com.overlay.menubar.plist   # LaunchAgent configuration
```

## Notes

- The application creates a floating menu bar overlay that appears on all desktops
- Desktop switching uses AppleScript (Control+Arrow keys simulation)
- Desktop detection uses yabai for real-time monitoring
- The overlay includes workspace buttons and a WhatsApp toggle feature
