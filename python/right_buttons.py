import psutil
import threading
import time
import json
import os
import subprocess
from Cocoa import (
    NSStatusBar, NSVariableStatusItemLength, NSFont, NSMenu, NSMenuItem,
    NSOpenPanel, NSModalResponseOK, NSWindow, NSWindowStyleMaskTitled,
    NSBackingStoreBuffered, NSTextView, NSScrollView, NSMakeRect, NSColor,
    NSAttributedString, NSForegroundColorAttributeName, NSFontAttributeName,
)

_DIR = os.path.dirname(os.path.abspath(__file__))
LAUNCHER_CONFIG_FILE = os.path.join(_DIR, "launcher_shortcuts.json")


class RightButtons:
    def __init__(self):
        self.shortcuts = self.load_shortcuts()
        self.launcher_items = []
        self.status_items = []
        self.note_window = None
        self.settings_window = None
        self._cpu_monitor_started = False

        self._create_static_items()
        self._create_launcher_items()

    def load_shortcuts(self):
        try:
            if os.path.exists(LAUNCHER_CONFIG_FILE):
                with open(LAUNCHER_CONFIG_FILE, "r") as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading shortcuts: {e}")
            return []

    def save_shortcuts(self):
        try:
            with open(LAUNCHER_CONFIG_FILE, "w") as f:
                json.dump(self.shortcuts, f, indent=4)
        except Exception as e:
            print(f"Error saving shortcuts: {e}")

    def _new_item(self, title, action, tooltip=None):
        item = NSStatusBar.systemStatusBar().statusItemWithLength_(
            NSVariableStatusItemLength
        )
        item.button().setTitle_(title)
        item.button().setTarget_(self)
        item.button().setAction_(action)
        if tooltip:
            item.button().setToolTip_(tooltip)
        self.status_items.append(item)
        return item

    def _create_static_items(self):
        self.add_item = self._new_item("+", "add_file_clicked:", "Add launcher (right-click to manage)")
        self._rebuild_add_menu()
        self.notes_item = self._new_item("N", "notes_clicked:", "Notes")
        self.settings_item = self._new_item("⚙", "settings_clicked:", "Settings")
        self.cpu_item = self._new_item("CPU", "cpu_info_clicked:", "CPU usage")
        self.start_cpu_monitor()

    def _rebuild_add_menu(self):
        menu = NSMenu.alloc().initWithTitle_("Launchers")
        add = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
            "Add Shortcut…", "add_file_clicked:", ""
        )
        add.setTarget_(self)
        menu.addItem_(add)
        if self.shortcuts:
            menu.addItem_(NSMenuItem.separatorItem())
            for path in self.shortcuts:
                label = f"Remove {os.path.basename(path)}"
                remove_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                    label, "remove_shortcut:", ""
                )
                remove_item.setTarget_(self)
                remove_item.setRepresentedObject_(path)
                menu.addItem_(remove_item)
        self.add_item.button().setMenu_(menu)

    def _create_launcher_items(self):
        for path in self.shortcuts:
            display_name = os.path.basename(path)[:1].upper() or "?"
            item = self._new_item(display_name, "launch_file:", path)
            item.button().setRepresentedObject_(path)
            self.launcher_items.append(item)

    def reload_buttons(self):
        bar = NSStatusBar.systemStatusBar()
        for item in self.launcher_items:
            bar.removeStatusItem_(item)
            if item in self.status_items:
                self.status_items.remove(item)
        self.launcher_items.clear()
        self._create_launcher_items()
        self._rebuild_add_menu()

    def cpu_info_clicked_(self, sender):
        print("CPU Info button clicked")

    def settings_clicked_(self, sender):
        if self.settings_window and self.settings_window.isVisible():
            self.settings_window.orderOut_(None)
            self.settings_window = None
            return

        rect = NSMakeRect(0, 0, 300, 200)
        self.settings_window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            rect, NSWindowStyleMaskTitled, NSBackingStoreBuffered, False
        )
        self.settings_window.setTitle_("Settings")
        self.settings_window.center()
        self.settings_window.orderFrontRegardless()

    def notes_clicked_(self, sender):
        if self.note_window and self.note_window.isVisible():
            self.note_window.orderOut_(None)
            self.note_window = None
            return

        rect = NSMakeRect(0, 0, 300, 400)
        self.note_window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            rect, NSWindowStyleMaskTitled, NSBackingStoreBuffered, False
        )
        self.note_window.setTitle_("Notes")
        self.note_window.center()

        scroll_view = NSScrollView.alloc().initWithFrame_(
            self.note_window.contentView().bounds()
        )
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
            subprocess.run(["open", file_path], check=True)
        except Exception as e:
            print(f"Error launching file {file_path}: {e}")

    def remove_shortcut_(self, sender):
        file_path_to_remove = sender.representedObject()
        if file_path_to_remove in self.shortcuts:
            self.shortcuts.remove(file_path_to_remove)
            self.save_shortcuts()
            self.reload_buttons()

    def start_cpu_monitor(self):
        if self._cpu_monitor_started:
            return
        self._cpu_monitor_started = True

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
                NSForegroundColorAttributeName: NSColor.labelColor(),
                NSFontAttributeName: NSFont.systemFontOfSize_(12),
            },
        )
        if hasattr(self, "cpu_item") and self.cpu_item.button():
            self.cpu_item.button().setAttributedTitle_(attr_title)
