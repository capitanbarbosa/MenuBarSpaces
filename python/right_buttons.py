import psutil
import threading
import time
import json
import os
import subprocess
from Cocoa import (
    NSButton, NSMakeRect, NSColor, NSAttributedString, NSDictionary,
    NSForegroundColorAttributeName, NSFont, NSMenu, NSMenuItem, NSOpenPanel,
    NSApplication, NSModalResponseOK, NSWindow, NSWindowStyleMaskTitled,
    NSBackingStoreBuffered, NSTextView, NSScrollView
)

LAUNCHER_CONFIG_FILE = "launcher_shortcuts.json"

class RightButtons:
    def __init__(self, parent_view, x, y, width, height):
        self.parent_view = parent_view
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.shortcuts = self.load_shortcuts()
        self.launcher_buttons = []
        self.buttons = []
        
        self.create_buttons()
        self.note_window = None
        self.settings_window = None

    def load_shortcuts(self):
        try:
            if os.path.exists(LAUNCHER_CONFIG_FILE):
                with open(LAUNCHER_CONFIG_FILE, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading shortcuts: {e}")
            return []

    def save_shortcuts(self):
        try:
            with open(LAUNCHER_CONFIG_FILE, 'w') as f:
                json.dump(self.shortcuts, f, indent=4)
        except Exception as e:
            print(f"Error saving shortcuts: {e}")

    def create_buttons(self):
        # Define static button properties, from right to left
        static_button_defs = [
            ("CPU", "cpu_info_clicked:"),
            ("⚙", "settings_clicked:"),
            ("N", "notes_clicked:"),
        ]

        button_width = 40
        button_spacing = 5
        current_x = self.width - button_width - 5

        # Create static buttons first
        for title, action in static_button_defs:
            button = self._create_button(title, action, current_x, button_width)
            if title == "CPU":
                self.cpu_button = button
                self.start_cpu_monitor()
            self.buttons.append(button)
            self.parent_view.addSubview_(button)
            current_x -= (button_width + button_spacing)

        # Create launcher buttons from shortcuts
        for path in self.shortcuts:
            display_name = os.path.basename(path)[:1].upper()
            button = self._create_button(display_name, "launch_file:", current_x, button_width)
            button.setToolTip_(path)
            button.setRepresentedObject_(path) # Attach path to button object
            self.launcher_buttons.append(button)
            self.parent_view.addSubview_(button)
            current_x -= (button_width + button_spacing)

        # Create the "Add" button for launcher
        add_button = self._create_button("+", "add_file_clicked:", current_x, button_width)
        self.buttons.append(add_button)
        self.parent_view.addSubview_(add_button)
        
    def _create_button(self, title, action, x, width):
        button = NSButton.alloc().initWithFrame_(
            NSMakeRect(x, 0, width, self.height)
        )
        button.setTitle_(title)
        button.setBezelStyle_(0)
        button.setBordered_(False)
        button.setWantsLayer_(True)
        button.layer().setBackgroundColor_(NSColor.clearColor().CGColor())
        button.setTarget_(self)
        
        # Set action and context menu for launcher buttons
        if action == "launch_file:":
            button.setAction_(action)
            # Create a menu for right-click
            menu = NSMenu.alloc().initWithTitle_("Context Menu")
            remove_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Remove Shortcut", "remove_shortcut:", "")
            remove_item.setTarget_(self)
            remove_item.setRepresentedObject_(button) # Pass button to action
            menu.addItem_(remove_item)
            button.setMenu_(menu)
        else:
            button.setAction_(action)

        attr_title = NSAttributedString.alloc().initWithString_attributes_(
            title, {NSForegroundColorAttributeName: NSColor.whiteColor()}
        )
        button.setAttributedTitle_(attr_title)
        return button

    def cpu_info_clicked_(self, sender):
        print("CPU Info button clicked")

    def settings_clicked_(self, sender):
        if self.settings_window and self.settings_window.isVisible():
            self.settings_window.orderOut_(None)
            self.settings_window = None
            return

        rect = NSMakeRect(0, 0, 300, 200)
        style_mask = NSWindowStyleMaskTitled

        self.settings_window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            rect, style_mask, NSBackingStoreBuffered, False
        )
        self.settings_window.setTitle_("Settings")
        self.settings_window.center()
        
        # Add placeholder content for settings later
        
        self.settings_window.orderFrontRegardless()

    def notes_clicked_(self, sender):
        if self.note_window and self.note_window.isVisible():
            self.note_window.orderOut_(None)
            self.note_window = None
            return

        rect = NSMakeRect(0, 0, 300, 400)
        style_mask = NSWindowStyleMaskTitled

        self.note_window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            rect, style_mask, NSBackingStoreBuffered, False
        )
        self.note_window.setTitle_("Notes")
        self.note_window.center()

        # Add a text view
        scroll_view = NSScrollView.alloc().initWithFrame_(self.note_window.contentView().bounds())
        text_view = NSTextView.alloc().initWithFrame_(scroll_view.bounds())
        text_view.setRichText_(False)
        text_view.setFont_(NSFont.userFixedPitchFontOfSize_(14))
        text_view.setAllowsUndo_(True)
        
        scroll_view.setDocumentView_(text_view)
        scroll_view.setHasVerticalScroller_(True)
        self.note_window.setContentView_(scroll_view)

        self.note_window.orderFrontRegardless()

    def add_file_clicked_(self, sender):
        panel = NSOpenPanel.openPanel()
        panel.setCanChooseFiles_(True)
        panel.setCanChooseDirectories_(True)
        panel.setAllowsMultipleSelection_(False)

        response = panel.runModal()
        if response == NSModalResponseOK:
            path = panel.URL().path()
            if path not in self.shortcuts:
                self.shortcuts.append(path)
                self.save_shortcuts()
                self.reload_buttons()

    def launch_file_(self, sender):
        file_path = sender.representedObject()
        try:
            subprocess.run(['open', file_path], check=True)
        except Exception as e:
            print(f"Error launching file {file_path}: {e}")

    def remove_shortcut_(self, sender):
        button_to_remove = sender.representedObject()
        file_path_to_remove = button_to_remove.representedObject()
        if file_path_to_remove in self.shortcuts:
            self.shortcuts.remove(file_path_to_remove)
            self.save_shortcuts()
            self.reload_buttons()

    def reload_buttons(self):
        # Clear existing buttons
        for view in self.parent_view.subviews():
            view.removeFromSuperview()
        
        self.launcher_buttons.clear()
        self.buttons.clear()
        
        # Re-create all buttons
        self.create_buttons()

    def start_cpu_monitor(self):
        def update_loop():
            from PyObjCTools.AppHelper import callAfter
            while True:
                cpu_percent = psutil.cpu_percent(interval=1)
                callAfter(self.update_cpu_button, cpu_percent)
                time.sleep(4)

        monitor_thread = threading.Thread(target=update_loop, daemon=True)
        monitor_thread.start()

    def update_cpu_button(self, cpu_percent):
        title = f"{cpu_percent:.0f}%"
        attr_title = NSAttributedString.alloc().initWithString_attributes_(
            title,
            {
                NSForegroundColorAttributeName: NSColor.whiteColor(),
                NSFontAttributeName: NSFont.systemFontOfSize_(12)
            }
        )
        if hasattr(self, 'cpu_button'):
            self.cpu_button.setAttributedTitle_(attr_title) 