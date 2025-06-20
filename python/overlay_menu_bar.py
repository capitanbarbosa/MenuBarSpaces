# ...existing code from overlay_menu_bar.py...
import sys
from Cocoa import NSApplication, NSWindow, NSWindowStyleMaskBorderless, NSBackingStoreBuffered, NSRect, NSScreen, NSColor, NSStatusWindowLevel, NSButton, NSPanel, NSView, NSMakeRect, NSFont, NSAttributedString, NSDictionary, NSForegroundColorAttributeName
from PyObjCTools import AppHelper


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
            NSColor.colorWithCalibratedRed_green_blue_alpha_(1.0, 0.0, 0.0, 1.0))
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
        button_width = 40
        button_height = menu_bar_height - 4
        button = NSButton.alloc().initWithFrame_(
            NSMakeRect(2, 2, button_width, button_height))
        button.setTitle_("≡")
        button.setBezelStyle_(4)  # NSBezelStyleTexturedRounded
        # Make the button respond to mouse down for instant feedback
        button.setAction_("togglePanel:")
        button.setTarget_(self)
        button.setButtonType_(0)  # NSMomentaryLightButton
        button.setBordered_(False)
        button.setWantsLayer_(True)
        button.layer().setBackgroundColor_(
            NSColor.colorWithCalibratedRed_green_blue_alpha_(0.2, 0.2, 0.2, 1.0).CGColor())
        button.layer().setCornerRadius_(8)
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

        self.window.orderFrontRegardless()

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

    def panelOptionClicked_(self, sender):
        # Placeholder: print which option was clicked
        print(f"Clicked: {sender.title()}")
        if sender.title() == "Quit":
            NSApplication.sharedApplication().terminate_(None)


if __name__ == "__main__":
    app = NSApplication.sharedApplication()
    overlay = OverlayMenuBar()
    AppHelper.runEventLoop()
