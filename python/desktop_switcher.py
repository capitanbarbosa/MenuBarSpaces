import subprocess
import json
import os
import threading
import time
from Cocoa import (
    NSStatusBar, NSVariableStatusItemLength, NSColor, NSFont,
    NSAttributedString, NSDictionary, NSForegroundColorAttributeName,
)
from PyObjCTools.AppHelper import callAfter


class DesktopSwitcher:
    def __init__(self):
        self.workspace_count = 6
        self.workspace_names = ["Log", "Dev", "Biz", "Media", "Chat", "Web"]
        self.current_workspace = 1
        self.workspace_items = []

        self.create_workspace_buttons()
        self.updateWorkspaceButtons()
        self.setup_workspace_monitor()
        self.resetToFirstDesktop()

    def create_workspace_buttons(self):
        bar = NSStatusBar.systemStatusBar()
        for i in range(self.workspace_count):
            item = bar.statusItemWithLength_(NSVariableStatusItemLength)
            button = item.button()
            button.setTitle_(self.workspace_names[i])
            button.setFont_(NSFont.systemFontOfSize_(12))
            button.setTarget_(self)
            button.setAction_("switchToWorkspace:")
            button.setTag_(i + 1)
            button.setToolTip_(f"Switch to {self.workspace_names[i]}")
            self.workspace_items.append(item)

    def resetToFirstDesktop(self):
        print("[Pager] Menu bar desktop switcher ready.")
        callAfter(self.updateWorkspaceButtons)

    def switchToWorkspaceSimple(self, target_workspace):
        if target_workspace == self.current_workspace:
            print(f"[Pager] Already on workspace {target_workspace}")
            return

        print(f"[Pager] Switching: {self.current_workspace} → {target_workspace}")

        swipes_needed = target_workspace - self.current_workspace
        direction = "right" if swipes_needed > 0 else "left"
        swipes_count = abs(swipes_needed)
        key_code = "124" if direction == "right" else "123"

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
            subprocess.run(
                ["osascript", "-e", script],
                check=True,
                capture_output=True,
                text=True,
            )
            print(f"[Pager] Successfully switched to workspace {target_workspace}")
        except Exception as e:
            print(f"[Pager] Error switching workspace: {e}")
            self.detectMissionControlReset()

    def detectMissionControlReset(self):
        print("[Pager] Mission Control detected, resetting to desktop 1...")
        self.resetToFirstDesktop()

    def query_current_workspace(self):
        yabai_paths = [
            "/opt/homebrew/bin/yabai",
            "/usr/local/bin/yabai",
            "yabai",
        ]

        yabai_cmd = None
        for path in yabai_paths:
            if os.path.exists(path) or path == "yabai":
                yabai_cmd = path
                break

        if not yabai_cmd:
            return None

        try:
            result = subprocess.run(
                [yabai_cmd, "-m", "query", "--spaces", "--space"],
                capture_output=True,
                text=True,
                check=True,
                timeout=2,
            )
            data = json.loads(result.stdout)
            return data.get("index")
        except Exception as e:
            print(f"[Pager] Error with yabai: {e}")
            return None

    def workspace_sync_monitor(self):
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
        monitor_thread = threading.Thread(target=self.workspace_sync_monitor, daemon=True)
        monitor_thread.start()

    def highlightWorkspaceButtonsBlue(self):
        for i, item in enumerate(self.workspace_items):
            button = item.button()
            if not button:
                continue
            attr_title = NSAttributedString.alloc().initWithString_attributes_(
                self.workspace_names[i],
                NSDictionary.dictionaryWithObject_forKey_(
                    NSColor.systemBlueColor(), NSForegroundColorAttributeName
                ),
            )
            button.setAttributedTitle_(attr_title)

    def unhighlightWorkspaceButtons(self):
        self.updateWorkspaceButtons()

    def updateWorkspaceButtons(self):
        for i, item in enumerate(self.workspace_items):
            button = item.button()
            if not button:
                continue
            workspace_num = i + 1
            workspace_name = self.workspace_names[i]
            if workspace_num == self.current_workspace:
                # Prefix marks the active Space without custom backgrounds
                title = f"[{workspace_name}]"
                color = NSColor.labelColor()
            else:
                title = workspace_name
                color = NSColor.secondaryLabelColor()
            attr_title = NSAttributedString.alloc().initWithString_attributes_(
                title,
                NSDictionary.dictionaryWithObject_forKey_(
                    color, NSForegroundColorAttributeName
                ),
            )
            button.setAttributedTitle_(attr_title)

    def switchToWorkspace_(self, sender):
        self.switchToWorkspaceSimple(sender.tag())
