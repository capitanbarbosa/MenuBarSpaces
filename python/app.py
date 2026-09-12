import sys
import threading

try:
    from ApplicationServices import AXIsProcessTrustedWithOptions
except ImportError:
    AXIsProcessTrustedWithOptions = None

from Cocoa import (
    NSApplication,
    NSApplicationActivationPolicyAccessory,
    NSMenu,
    NSMenuItem,
    NSStatusBar,
    NSVariableStatusItemLength,
)
from PyObjCTools import AppHelper

try:
    from pynput import keyboard
except ImportError:
    keyboard = None

from desktop_switcher import DesktopSwitcher
from left_buttons import GPTButton, WizlabsButton, WhatsAppButton, GmailButton
from right_buttons import RightButtons


def check_accessibility_permissions():
    if sys.platform == "darwin" and AXIsProcessTrustedWithOptions is not None:
        if not AXIsProcessTrustedWithOptions(None):
            print("=" * 80)
            print("!! PERMISSION REQUIRED FOR HOTKEYS / DESKTOP SWITCHING !!")
            print("Grant Accessibility (and Input Monitoring for F9) to your terminal/Cursor.")
            print("System Settings > Privacy & Security > Accessibility")
            print("System Settings > Privacy & Security > Input Monitoring")
            print("=" * 80)
            return False
    return True


class MenuBarApp:
    """Native macOS menu bar extras (right side of the system menu bar)."""

    def __init__(self):
        # Keep strong refs so status items are not garbage-collected
        self._keepers = []

        # Order of creation ≈ left→right among this app's items
        self.menu_item = self._create_main_menu()
        self.wizlabs_button = WizlabsButton()
        self.gpt_button = GPTButton()
        self.whatsapp_button = WhatsAppButton()
        self.gmail_button = GmailButton()
        self.desktop_switcher = DesktopSwitcher()
        self.right_buttons = RightButtons()

        self._keepers.extend(
            [
                self.menu_item,
                self.wizlabs_button,
                self.gpt_button,
                self.whatsapp_button,
                self.gmail_button,
                self.desktop_switcher,
                self.right_buttons,
            ]
        )

        self.hotkey_listener_thread = None
        self.setup_hotkey_listener()
        print("Menu bar items ready (right side of the system menu bar).")

    def _create_main_menu(self):
        item = NSStatusBar.systemStatusBar().statusItemWithLength_(
            NSVariableStatusItemLength
        )
        item.button().setTitle_("≡")
        item.button().setToolTip_("Active Top Menu")

        menu = NSMenu.alloc().init()
        for title, action in [
            ("About", "aboutClicked:"),
            ("Quit", "quitClicked:"),
        ]:
            mi = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                title, action, ""
            )
            mi.setTarget_(self)
            menu.addItem_(mi)
        item.setMenu_(menu)
        return item

    def aboutClicked_(self, sender):
        print("Active Top Menu — native menu bar status items")

    def quitClicked_(self, sender):
        NSApplication.sharedApplication().terminate_(None)

    def setup_hotkey_listener(self):
        if not check_accessibility_permissions():
            print("\n[Warning] Permissions not granted. Shift highlight / hotkeys limited.")
            return

        if keyboard is None:
            print("[Warning] pynput not installed. Hotkeys disabled.")
            return

        self._shift_pressed = False

        def on_press(key):
            try:
                if key == keyboard.Key.shift and not self._shift_pressed:
                    self._shift_pressed = True
                    from PyObjCTools.AppHelper import callAfter

                    callAfter(self.desktop_switcher.highlightWorkspaceButtonsBlue)
            except Exception as e:
                print(f"Hotkey error: {e}")

        def on_release(key):
            try:
                if key == keyboard.Key.shift and self._shift_pressed:
                    self._shift_pressed = False
                    from PyObjCTools.AppHelper import callAfter

                    callAfter(self.desktop_switcher.unhighlightWorkspaceButtons)
            except Exception as e:
                print(f"Hotkey error: {e}")

        listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        t = threading.Thread(target=listener.start, daemon=True)
        t.start()
        self.hotkey_listener_thread = t


if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    controller = MenuBarApp()
    AppHelper.runEventLoop()
