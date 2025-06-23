import sys
import threading
try:
    from ApplicationServices import AXIsProcessTrustedWithOptions
except ImportError:
    AXIsProcessTrustedWithOptions = None
from Cocoa import NSApplication, NSWindow, NSWindowStyleMaskBorderless, NSBackingStoreBuffered, NSRect, NSScreen, NSColor, NSStatusWindowLevel, NSButton, NSPanel, NSView, NSMakeRect, NSFont, NSAttributedString, NSDictionary, NSForegroundColorAttributeName, NSStatusBar, NSVariableStatusItemLength, NSImage, NSAnimationContext
from PyObjCTools import AppHelper

# Add this import for global hotkey
try:
    from pynput import keyboard
except ImportError:
    keyboard = None  # Will show warning if not installed

from desktop_switcher import DesktopSwitcher


def check_accessibility_permissions():
    """Checks for macOS accessibility permissions and provides guidance if not enabled."""
    if sys.platform == 'darwin' and AXIsProcessTrustedWithOptions is not None:
        if not AXIsProcessTrustedWithOptions(None):
            print("="*80)
            print("!! PERMISSION REQUIRED FOR HOTKEYS !!")
            print("This app needs permissions to listen for global hotkeys (like F9).")
            print("Please grant 'Accessibility' and 'Input Monitoring' permissions to your terminal app.")
            print("\nTo do so:")
            print("1. Open System Settings > Privacy & Security > Accessibility")
            print("2. Open System Settings > Privacy & Security > Input Monitoring")
            print("\nIn both sections, click '+' and add your terminal application if it's not listed, then ensure the toggle is ON.")
            print("The app running this script needs to be added (e.g., Terminal, iTerm2, or VSCode's/Cursor's terminal).")
            print("You will likely need to restart the terminal or the script after granting permissions.")
            print("="*80)
            return False
    return True


class OverlayMenuBar:
    def __init__(self):
        screen = NSScreen.mainScreen()
        frame = screen.frame()
        # Set height for your custom menu bar (reduced to 24 pixels for maximum compactness)
        menu_bar_height = 24
        left_margin = 120  # Adjust left margin for floating effect
        rect = NSRect((left_margin, frame.size.height - menu_bar_height),
                      (frame.size.width - left_margin, menu_bar_height))

        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            rect,
            NSWindowStyleMaskBorderless,
            NSBackingStoreBuffered,
            False
        )
        self.window.setLevel_(NSStatusWindowLevel)
        self.window.setOpaque_(False)
        # Set a visible solid red background color (fully opaque)
        self.window.setBackgroundColor_(
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.094, 0.094, 0.094, 1.0))  # #181818
        self.window.setAlphaValue_(1.0)

        # Make the window appear on all Spaces (Desktops) and stay visible in Exposé/Spaces
        NSWindowCollectionBehaviorCanJoinAllSpaces = 1 << 0
        NSWindowCollectionBehaviorStationary = 1 << 4
        NSWindowCollectionBehaviorIgnoresCycle = 1 << 5
        NSWindowCollectionBehaviorFullScreenAuxiliary = 1 << 8
        behavior = (NSWindowCollectionBehaviorCanJoinAllSpaces |
                    NSWindowCollectionBehaviorStationary |
                    NSWindowCollectionBehaviorIgnoresCycle |
                    NSWindowCollectionBehaviorFullScreenAuxiliary)
        self.window.setCollectionBehavior_(behavior)

        # Initialize simple workspace tracking 
        # self.workspace_count = 6
        # self.workspace_names = ["Log", "Dev", "Biz", "Media", "Chat", "Web"]
        # self.current_workspace = 1  # We'll always start at desktop 1
        # self.workspace_buttons = []
        
        # Add your custom drawing or views here

        # Add a placeholder button to the overlay
        button_width = 48  # Wider for more left border
        button_height = menu_bar_height - 2  # Reduced padding for maximum compactness
        button_x = 4  # Move closer to the left edge
        button_y = 1  # Minimal vertical padding
        button = NSButton.alloc().initWithFrame_(
            NSMakeRect(button_x, button_y, button_width, button_height))
        button.setTitle_("≡")
        button.setBezelStyle_(4)  # NSBezelStyleTexturedRounded
        button.setAction_("togglePanel:")
        button.setTarget_(self)
        button.setButtonType_(0)  # NSMomentaryLightButton
        button.setBordered_(False)
        button.setWantsLayer_(True)
        # Set button background color to #23272F with a slightly lighter border for differentiation
        button_bg = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.133, 0.133, 0.133, 1.0)  # #222222
        button.layer().setBackgroundColor_(button_bg.CGColor())
        button.layer().setCornerRadius_(4)  # Minimal corner radius for maximum compactness
        # Add padding by increasing contentInsets (if available)
        if hasattr(button, 'setContentInsets_'):
            from Cocoa import NSEdgeInsetsMake
            button.setContentInsets_(NSEdgeInsetsMake(6, 20, 6, 12))  # More left padding
        # Add a subtle border to help differentiate from background
        button.layer().setBorderWidth_(1.5)
        button.layer().setBorderColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(0.22, 0.25, 0.32, 1.0).CGColor())
        # Set button text color to #E6EAF0 (Light Gray)
        attr_title = NSAttributedString.alloc().initWithString_attributes_(
            "≡",
            NSDictionary.dictionaryWithObject_forKey_(
                NSColor.colorWithCalibratedRed_green_blue_alpha_(0.902, 0.918, 0.941, 1.0), NSForegroundColorAttributeName)
        )
        button.setAttributedTitle_(attr_title)
        self.button = button  # Keep a reference
        self.window.contentView().addSubview_(button)

        # Create a placeholder panel (hidden by default)
        panel_width = 300
        panel_height = 400
        panel_rect = NSMakeRect(
            10, frame.size.height - menu_bar_height - panel_height, panel_width, panel_height)
        self.panel = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            panel_rect,
            NSWindowStyleMaskBorderless,
            NSBackingStoreBuffered,
            False
        )
        self.panel.setLevel_(NSStatusWindowLevel)
        self.panel.setOpaque_(True)
        # Use a dark background for the panel for better readability
        self.panel.setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(
            0.13, 0.15, 0.18, 1.0))  # dark gray
        self.panel.setAlphaValue_(1.0)
        self.panel.orderOut_(None)

        # Add placeholder options to the panel with improved styling
        option_titles = ["Launch App", "Settings", "About", "Quit"]
        option_height = 40
        button_bg_colors = [
            NSColor.colorWithCalibratedRed_green_blue_alpha_(
                0.20, 0.60, 0.86, 1.0),  # blue
            NSColor.colorWithCalibratedRed_green_blue_alpha_(
                0.18, 0.80, 0.44, 1.0),  # green
            NSColor.colorWithCalibratedRed_green_blue_alpha_(
                0.95, 0.77, 0.06, 1.0),  # yellow
            NSColor.colorWithCalibratedRed_green_blue_alpha_(
                0.91, 0.30, 0.24, 1.0),  # red
        ]
        text_colors = [
            NSColor.whiteColor(),
            NSColor.whiteColor(),
            NSColor.blackColor(),
            NSColor.whiteColor(),
        ]
        for idx, title in enumerate(option_titles):
            opt_button = NSButton.alloc().initWithFrame_(NSMakeRect(20, panel_height -
                                                                    (idx + 1) * (option_height + 10), panel_width - 40, option_height))
            opt_button.setTitle_(title)
            opt_button.setBezelStyle_(4)
            opt_button.setTarget_(self)
            opt_button.setAction_("panelOptionClicked:")
            opt_button.setFont_(NSFont.boldSystemFontOfSize_(16))
            opt_button.setWantsLayer_(True)
            opt_button.layer().setBackgroundColor_(
                button_bg_colors[idx].CGColor())
            opt_button.layer().setCornerRadius_(8)
            opt_button.setBordered_(False)
            # Set button title color using attributed string
            attr_title = NSAttributedString.alloc().initWithString_attributes_(
                title,
                NSDictionary.dictionaryWithObject_forKey_(
                    text_colors[idx], NSForegroundColorAttributeName)
            )
            opt_button.setAttributedTitle_(attr_title)
            self.panel.contentView().addSubview_(opt_button)

        # Add a status bar item (menu bar icon)
        self.status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(NSVariableStatusItemLength)
        # Set a simple icon (use a built-in or custom image)
        status_icon = NSImage.imageNamed_("NSMenuOnStateTemplate")
        if status_icon:
            self.status_item.button().setImage_(status_icon)
        else:
            self.status_item.button().setTitle_("≡")
        self.status_item.button().setTarget_(self)
        self.status_item.button().setAction_("toggleOverlay:")

        # Add WhatsApp button next to the left menu button
        whatsapp_button_width = 36
        whatsapp_button_height = menu_bar_height - 2  # Reduced padding for maximum compactness
        whatsapp_button_x = button_x + button_width + 8  # Place to the right of the menu button
        whatsapp_button_y = 1  # Minimal vertical padding
        whatsapp_button = NSButton.alloc().initWithFrame_(
            NSMakeRect(whatsapp_button_x, whatsapp_button_y, whatsapp_button_width, whatsapp_button_height))
        whatsapp_button.setTitle_("🟢")  # Use WhatsApp emoji or set custom icon if desired
        whatsapp_button.setBezelStyle_(4)
        whatsapp_button.setAction_("toggleWhatsAppComprehensive:")
        whatsapp_button.setTarget_(self)
        whatsapp_button.setButtonType_(0)
        whatsapp_button.setBordered_(False)
        whatsapp_button.setWantsLayer_(True)
        whatsapp_button.layer().setBackgroundColor_(button_bg.CGColor())
        whatsapp_button.layer().setCornerRadius_(4)  # Minimal corner radius for maximum compactness
        attr_whatsapp = NSAttributedString.alloc().initWithString_attributes_(
            "🟢",
            NSDictionary.dictionaryWithObject_forKey_(
                NSColor.colorWithCalibratedRed_green_blue_alpha_(0.3, 0.9, 0.3, 1.0), NSForegroundColorAttributeName)
        )
        whatsapp_button.setAttributedTitle_(attr_whatsapp)
        self.whatsapp_button = whatsapp_button
        self.window.contentView().addSubview_(whatsapp_button)

        # Create individual workspace buttons directly in the menu bar (section style)
        workspace_button_width = 64  # Wider for section look
        workspace_button_height = menu_bar_height - 2
        workspace_start_x = whatsapp_button_x + whatsapp_button_width + 8
        section_gap = 0  # No gap for section/segmented look
        
        self.desktop_switcher = DesktopSwitcher(self.window.contentView(), workspace_start_x, menu_bar_height)

        # Update workspace button appearances
        # self.updateWorkspaceButtons()

        # Add a right-edge toggle-off button to the overlay
        close_button_width = 32
        close_button_height = menu_bar_height - 4  # Reduced padding for maximum compactness
        close_button_x = frame.size.width - close_button_width - 8 - left_margin
        close_button_y = 1  # Minimal vertical padding
        close_button = NSButton.alloc().initWithFrame_(
            NSMakeRect(close_button_x, close_button_y, close_button_width, close_button_height))
        close_button.setTitle_("→")
        close_button.setBezelStyle_(4)
        close_button.setButtonType_(0)
        close_button.setBordered_(False)
        close_button.setWantsLayer_(True)
        close_button.layer().setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(0.18, 0.20, 0.24, 1.0).CGColor())
        close_button.layer().setCornerRadius_(4)  # Minimal corner radius for maximum compactness
        attr_close = NSAttributedString.alloc().initWithString_attributes_(
            "→",
            NSDictionary.dictionaryWithObject_forKey_(
                NSColor.colorWithCalibratedRed_green_blue_alpha_(0.902, 0.918, 0.941, 1.0), NSForegroundColorAttributeName)
        )
        close_button.setAttributedTitle_(attr_close)
        close_button.setTarget_(self)
        close_button.setAction_("slideOutAndHide:")
        self.window.contentView().addSubview_(close_button)
        self.close_button = close_button

        self.window.orderFrontRegardless()
        self.hotkey_listener_thread = None
        self.setup_hotkey_listener()
        
        # Reset to desktop 1 on startup and start monitoring
        # self.resetToFirstDesktop()
        # self.setup_workspace_monitor()

    def setup_hotkey_listener(self):
        if not check_accessibility_permissions():
            print("\n[Warning] Permissions not granted. The F9 hotkey will be disabled.")
            return

        if keyboard is None:
            print("[Warning] pynput not installed. F9 hotkey will not work.")
            return

        self._shift_pressed = False

        def on_press(key):
            try:
                if key == keyboard.Key.f9:
                    # Toggle the whole overlay menu bar window
                    if self.window.isVisible():
                        self.window.orderOut_(None)
                        # Also hide the panel if open
                        self.panel.orderOut_(None)
                    else:
                        self.window.orderFrontRegardless()
                elif key == keyboard.Key.shift and not self._shift_pressed:
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

    def togglePanel_(self, sender):
        # Always position the panel below the button and toggle reliably
        if self.panel.isVisible():
            self.panel.orderOut_(None)
        else:
            window_frame = self.window.frame()
            button_frame = self.button.frame()
            panel_frame = self.panel.frame()
            x = window_frame.origin.x + button_frame.origin.x
            y = window_frame.origin.y - panel_frame.size.height
            self.panel.setFrameOrigin_((x, y))
            self.panel.orderFrontRegardless()

    def toggleOverlay_(self, sender):
        if self.window.isVisible():
            self.slideOutAndHide_(None)
        else:
            self.slideInAndShow_()

    def slideInAndShow_(self):
        # Animate window fading in
        self.window.setAlphaValue_(0.0)
        self.window.orderFrontRegardless()
        NSAnimationContext.beginGrouping()
        NSAnimationContext.currentContext().setDuration_(0.2)
        self.window.animator().setAlphaValue_(1.0)
        NSAnimationContext.endGrouping()

    def slideOutAndHide_(self, sender):
        # Animate window fading out
        NSAnimationContext.beginGrouping()
        NSAnimationContext.currentContext().setDuration_(0.2)
        
        # Use a completion handler to safely hide the window after animation.
        # This avoids potential crashes from `performSelector_withObject_afterDelay_`
        # if the object gets garbage-collected.
        def completion_handler():
            self.window.orderOut_(None)

        NSAnimationContext.currentContext().setCompletionHandler_(completion_handler)
        
        self.window.animator().setAlphaValue_(0.0)
        NSAnimationContext.endGrouping()
        
        # Also hide panels
        self.panel.orderOut_(None)

    def panelOptionClicked_(self, sender):
        # Placeholder: print which option was clicked
        print(f"Clicked: {sender.title()}")
        if sender.title() == "Quit":
            NSApplication.sharedApplication().terminate_(None)

    def unminimize_and_focus_whatsapp(self):
        """Use yabai to unminimize and focus the WhatsApp Web window if it exists."""
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
            print("[WhatsApp/yabai] yabai not found in common locations")
            return
            
        try:
            # Query all windows
            result = subprocess.run(
                [yabai_cmd, "-m", "query", "--windows"],
                capture_output=True, text=True, check=True
            )
            windows = json.loads(result.stdout)
            # Find WhatsApp Web window
            wa_windows = [w for w in windows if w.get("app") == "WhatsApp Web"]
            if not wa_windows:
                print("[WhatsApp/yabai] WhatsApp Web window not found.")
                return
            wa_id = wa_windows[0]["id"]
            # Unminimize (if minimized)
            subprocess.run([yabai_cmd, "-m", "window", str(wa_id), "--toggle", "min"])
            # Focus the window
            subprocess.run([yabai_cmd, "-m", "window", "--focus", str(wa_id)])
            print("[WhatsApp/yabai] WhatsApp Web window should now be visible and focused.")
        except Exception as e:
            print(f"[WhatsApp/yabai] Error: {e}")

    def is_whatsapp_minimized(self):
        """Return True if WhatsApp Web window is minimized, False if not, None if not found."""
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
            print("[WhatsApp/yabai] yabai not found in common locations")
            return None
            
        try:
            result = subprocess.run(
                [yabai_cmd, "-m", "query", "--windows"],
                capture_output=True, text=True, check=True
            )
            windows = json.loads(result.stdout)
            wa_windows = [w for w in windows if w.get("app") == "WhatsApp Web"]
            if not wa_windows:
                return None
            return wa_windows[0].get("minimized", 0) == 1
        except Exception as e:
            print(f"[WhatsApp/yabai] Error checking minimized state: {e}")
            return None

    def toggleWhatsAppComprehensive_(self, sender):
        """
        Toggle WhatsApp Web window using yabai: minimize if visible, unminimize+focus if minimized.
        """
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
            print("[WhatsApp/yabai] yabai not found in common locations")
            return
            
        try:
            # Query all windows
            result = subprocess.run(
                [yabai_cmd, "-m", "query", "--windows"],
                capture_output=True, text=True, check=True
            )
            windows = json.loads(result.stdout)
            wa_windows = [w for w in windows if w.get("app") == "WhatsApp Web"]
            if not wa_windows:
                print("[WhatsApp/yabai] WhatsApp Web window not found.")
                return
            wa_id = wa_windows[0]["id"]
            is_minimized = wa_windows[0].get("minimized", 0) == 1
            if is_minimized:
                # Unminimize and focus
                subprocess.run([yabai_cmd, "-m", "window", str(wa_id), "--toggle", "min"])
                subprocess.run([yabai_cmd, "-m", "window", "--focus", str(wa_id)])
                print("[WhatsApp/yabai] WhatsApp Web window unminimized and focused.")
            else:
                # Minimize
                subprocess.run([yabai_cmd, "-m", "window", str(wa_id), "--toggle", "min"])
                print("[WhatsApp/yabai] WhatsApp Web window minimized.")
        except Exception as e:
            print(f"[WhatsApp/yabai] Error: {e}")


if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    overlay = OverlayMenuBar()
    AppHelper.runEventLoop()
