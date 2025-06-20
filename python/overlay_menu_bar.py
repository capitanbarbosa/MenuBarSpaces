# ...existing code from overlay_menu_bar.py...
import sys
import threading
from Cocoa import NSApplication, NSWindow, NSWindowStyleMaskBorderless, NSBackingStoreBuffered, NSRect, NSScreen, NSColor, NSStatusWindowLevel, NSButton, NSPanel, NSView, NSMakeRect, NSFont, NSAttributedString, NSDictionary, NSForegroundColorAttributeName, NSStatusBar, NSVariableStatusItemLength, NSImage, NSAnimationContext
from PyObjCTools import AppHelper

# Add this import for global hotkey
try:
    from pynput import keyboard
except ImportError:
    keyboard = None  # Will show warning if not installed


class OverlayMenuBar:
    def __init__(self):
        screen = NSScreen.mainScreen()
        frame = screen.frame()
        # Set height for your custom menu bar (e.g., 30 pixels)
        menu_bar_height = 30
        rect = NSRect((0, frame.size.height - menu_bar_height),
                      (frame.size.width, menu_bar_height))

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
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.137, 0.152, 0.184, 1.0))  # #23272F Charcoal Gray
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

        # Add your custom drawing or views here

        # Add a placeholder button to the overlay
        button_width = 48  # Wider for more left border
        button_height = menu_bar_height - 4
        button_x = 4  # Move closer to the left edge
        button_y = 4
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
        button_bg = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.137, 0.152, 0.184, 1.0)  # #23272F
        button.layer().setBackgroundColor_(button_bg.CGColor())
        button.layer().setCornerRadius_(10)
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

        # Add a right-edge toggle-off button to the overlay
        close_button_width = 32
        close_button_height = menu_bar_height - 8
        close_button_x = frame.size.width - close_button_width - 8
        close_button_y = 4
        close_button = NSButton.alloc().initWithFrame_(
            NSMakeRect(close_button_x, close_button_y, close_button_width, close_button_height))
        close_button.setTitle_("→")
        close_button.setBezelStyle_(4)
        close_button.setButtonType_(0)
        close_button.setBordered_(False)
        close_button.setWantsLayer_(True)
        close_button.layer().setBackgroundColor_(NSColor.colorWithCalibratedRed_green_blue_alpha_(0.18, 0.20, 0.24, 1.0).CGColor())
        close_button.layer().setCornerRadius_(10)
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

        # Add WhatsApp button next to the left menu button
        whatsapp_button_width = 36
        whatsapp_button_height = menu_bar_height - 4
        whatsapp_button_x = button_x + button_width + 8  # Place to the right of the menu button
        whatsapp_button_y = 4
        whatsapp_button = NSButton.alloc().initWithFrame_(
            NSMakeRect(whatsapp_button_x, whatsapp_button_y, whatsapp_button_width, whatsapp_button_height))
        whatsapp_button.setTitle_("🟢")  # Use WhatsApp emoji or set custom icon if desired
        whatsapp_button.setBezelStyle_(4)
        whatsapp_button.setAction_("toggleWhatsApp:")
        whatsapp_button.setTarget_(self)
        whatsapp_button.setButtonType_(0)
        whatsapp_button.setBordered_(False)
        whatsapp_button.setWantsLayer_(True)
        whatsapp_button.layer().setBackgroundColor_(button_bg.CGColor())
        whatsapp_button.layer().setCornerRadius_(10)
        attr_whatsapp = NSAttributedString.alloc().initWithString_attributes_(
            "🟢",
            NSDictionary.dictionaryWithObject_forKey_(
                NSColor.colorWithCalibratedRed_green_blue_alpha_(0.3, 0.9, 0.3, 1.0), NSForegroundColorAttributeName)
        )
        whatsapp_button.setAttributedTitle_(attr_whatsapp)
        self.whatsapp_button = whatsapp_button
        self.window.contentView().addSubview_(whatsapp_button)

        self.window.orderFrontRegardless()
        self.hotkey_listener_thread = None
        self.setup_hotkey_listener()

    def setup_hotkey_listener(self):
        if keyboard is None:
            print("[Warning] pynput not installed. F9 hotkey will not work.")
            return

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
            except Exception as e:
                print(f"Hotkey error: {e}")

        listener = keyboard.Listener(on_press=on_press)
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
        # Animate window sliding in from right
        frame = self.window.frame()
        screen = NSScreen.mainScreen().frame()
        start_x = screen.size.width
        end_x = 0
        self.window.setFrameOrigin_((start_x, frame.origin.y))
        self.window.orderFrontRegardless()
        NSAnimationContext.beginGrouping()
        NSAnimationContext.currentContext().setDuration_(0.25)
        self.window.animator().setFrameOrigin_((end_x, frame.origin.y))
        NSAnimationContext.endGrouping()

    def slideOutAndHide_(self, sender):
        # Animate window sliding out to right
        frame = self.window.frame()
        screen = NSScreen.mainScreen().frame()
        end_x = screen.size.width
        NSAnimationContext.beginGrouping()
        NSAnimationContext.currentContext().setDuration_(0.25)
        self.window.animator().setFrameOrigin_((end_x, frame.origin.y))
        NSAnimationContext.endGrouping()
        # Hide after animation
        import time
        from threading import Timer
        Timer(0.26, lambda: self.window.orderOut_(None)).start()

    def panelOptionClicked_(self, sender):
        # Placeholder: print which option was clicked
        print(f"Clicked: {sender.title()}")
        if sender.title() == "Quit":
            NSApplication.sharedApplication().terminate_(None)

    # Add this method to OverlayMenuBar
    def toggleWhatsApp_(self, sender):
        """
        Toggle the WhatsApp Edge PWA window visibility using AppleScript.
        If visible, minimize it. If minimized, restore and focus it.
        """
        import subprocess
        script = '''
        tell application "Microsoft Edge"
            set winList to every window
            set found to false
            repeat with w in winList
                if name of w contains "WhatsApp" then
                    set found to true
                    if miniaturized of w is true then
                        set miniaturized of w to false
                        set index of w to 1
                        set visible of w to true
                        activate
                    else
                        set miniaturized of w to true
                    end if
                    exit repeat
                end if
            end repeat
        end tell
        '''
        try:
            subprocess.run(["osascript", "-e", script], check=True)
        except Exception as e:
            print(f"[WhatsApp Toggle] AppleScript error: {e}")


if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    overlay = OverlayMenuBar()
    AppHelper.runEventLoop()
