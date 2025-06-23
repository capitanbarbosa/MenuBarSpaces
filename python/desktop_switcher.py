import subprocess
import json
import os
import threading
import time
from Cocoa import NSButton, NSMakeRect, NSColor, NSFont, NSAttributedString, NSDictionary, NSForegroundColorAttributeName, NSEdgeInsetsMake
from PyObjCTools.AppHelper import callAfter

class DesktopSwitcher:
    def __init__(self, parent_view, start_x, menu_bar_height):
        self.parent_view = parent_view
        self.start_x = start_x
        self.menu_bar_height = menu_bar_height
        
        # Workspace tracking
        self.workspace_count = 6
        self.workspace_names = ["Log", "Dev", "Biz", "Media", "Chat", "Web"]
        self.current_workspace = 1  # Start at desktop 1
        self.workspace_buttons = []

        self.create_workspace_buttons()
        self.updateWorkspaceButtons()
        
        # Start monitoring workspace changes
        self.setup_workspace_monitor()
        self.resetToFirstDesktop()

    def create_workspace_buttons(self):
        """Create individual workspace buttons directly in the menu bar."""
        workspace_button_width = 64
        workspace_button_height = self.menu_bar_height - 2
        section_gap = 0
        
        for i in range(self.workspace_count):
            workspace_x = self.start_x + i * (workspace_button_width + section_gap)
            workspace_button = NSButton.alloc().initWithFrame_(
                NSMakeRect(workspace_x, 1, workspace_button_width, workspace_button_height))
            workspace_button.setTitle_(self.workspace_names[i])
            workspace_button.setBezelStyle_(2)
            workspace_button.setAction_("switchToWorkspace:")
            workspace_button.setTarget_(self)
            workspace_button.setButtonType_(0)
            workspace_button.setBordered_(False)
            workspace_button.setWantsLayer_(True)
            workspace_button.layer().setCornerRadius_(0)
            workspace_button.setFont_(NSFont.systemFontOfSize_(14))
            workspace_button.setTag_(i + 1)
            if hasattr(workspace_button, 'setContentInsets_'):
                workspace_button.setContentInsets_(NSEdgeInsetsMake(4, 12, 4, 12))
            workspace_button.layer().setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(0.094, 0.094, 0.094, 1.0).CGColor())
            self.workspace_buttons.append(workspace_button)
            self.parent_view.addSubview_(workspace_button)

    def resetToFirstDesktop(self):
        """No-op: overlay is already running; no desktop switching or activation needed."""
        print("[Pager] Overlay app is running (no desktop switching, no activation needed).")
        callAfter(self.updateWorkspaceButtons)

    def switchToWorkspaceSimple(self, target_workspace):
        """Switch to target workspace using simple left/right navigation."""
        if target_workspace == self.current_workspace:
            print(f"[Pager] Already on workspace {target_workspace}")
            return
        
        print(f"[Pager] Switching: {self.current_workspace} → {target_workspace}")
        
        swipes_needed = target_workspace - self.current_workspace
        direction = "right" if swipes_needed > 0 else "left"
        swipes_count = abs(swipes_needed)
        key_code = "124" if direction == "right" else "123" # Right or Left arrow
        
        script = f'''
        tell application "System Events"
            repeat {swipes_count} times
                key code {key_code} using {{control down}}
                delay 0.1
            end repeat
        end tell
        '''
        
        try:
            self.current_workspace = target_workspace
            self.updateWorkspaceButtons()
            
            subprocess.run(["osascript", "-e", script], check=True, capture_output=True, text=True)
            print(f"[Pager] Successfully switched to workspace {target_workspace}")
            
        except Exception as e:
            print(f"[Pager] Error switching workspace: {e}")
            self.detectMissionControlReset()

    def detectMissionControlReset(self):
        """Detect Mission Control usage and reset tracking."""
        print("[Pager] Mission Control detected, resetting to desktop 1...")
        self.resetToFirstDesktop()

    def query_current_workspace(self):
        """Query the current active workspace (desktop/space) using yabai."""
        yabai_paths = [
            "/opt/homebrew/bin/yabai",
            "/usr/local/bin/yabai",
            "yabai"
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

    def workspace_sync_monitor(self):
        """Periodically syncs the current workspace state by querying yabai."""
        while True:
            try:
                current_space = self.query_current_workspace()
                if current_space is not None and current_space != self.current_workspace:
                    print(f"[Pager] Workspace synced: {self.current_workspace} -> {current_space}")
                    self.current_workspace = current_space
                    callAfter(self.updateWorkspaceButtons)
            except Exception as e:
                print(f"[Pager] Sync monitor encountered an error: {e}")
            time.sleep(1)

    def setup_workspace_monitor(self):
        """Set up the workspace monitoring thread to keep desktop state in sync using yabai."""
        monitor_thread = threading.Thread(target=self.workspace_sync_monitor, daemon=True)
        monitor_thread.start()

    def highlightWorkspaceButtonsBlue(self):
        """Highlight all workspace buttons blue (for Shift key state)."""
        for i, button in enumerate(self.workspace_buttons):
            workspace_name = self.workspace_names[i]
            button.layer().setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(0.20, 0.44, 0.86, 1.0).CGColor())  # blue
            text_color = NSColor.whiteColor()
            attr_title = NSAttributedString.alloc().initWithString_attributes_(
                workspace_name,
                NSDictionary.dictionaryWithObject_forKey_(text_color, NSForegroundColorAttributeName)
            )
            button.setAttributedTitle_(attr_title)

    def unhighlightWorkspaceButtons(self):
        """Restore workspace buttons to normal state (green/gray)."""
        self.updateWorkspaceButtons()

    def updateWorkspaceButtons(self):
        """Update the appearance of workspace buttons to reflect current state (section style, green active, gray inactive)."""
        for i, button in enumerate(self.workspace_buttons):
            workspace_num = i + 1
            workspace_name = self.workspace_names[i]
            if workspace_num == self.current_workspace:
                # Active workspace - #38761d
                button.layer().setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(0.219, 0.463, 0.114, 1.0).CGColor())  # #38761d
                text_color = NSColor.whiteColor()
                button.layer().setBorderWidth_(0)
            else:
                # Inactive workspace - #181818
                button.layer().setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(0.094, 0.094, 0.094, 1.0).CGColor())  # #181818
                text_color = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.7, 0.7, 0.7, 1.0)
                button.layer().setBorderWidth_(0)
            # Set button title color
            attr_title = NSAttributedString.alloc().initWithString_attributes_(
                workspace_name,
                NSDictionary.dictionaryWithObject_forKey_(text_color, NSForegroundColorAttributeName)
            )
            button.setAttributedTitle_(attr_title)

    def switchToWorkspace_(self, sender):
        """Switch to the selected workspace using simple tracking."""
        workspace_number = sender.tag()
        self.switchToWorkspaceSimple(workspace_number) 