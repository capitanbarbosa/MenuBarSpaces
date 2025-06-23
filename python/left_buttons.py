import webbrowser
from Cocoa import NSButton, NSMakeRect, NSColor, NSAttributedString, NSDictionary, NSForegroundColorAttributeName

class GPTButton:
    def __init__(self, parent_view, x, y, width, height):
        self.button = NSButton.alloc().initWithFrame_(
            NSMakeRect(x, y, width, height)
        )
        self.button.setTitle_("GPT")
        self.button.setBezelStyle_(4)  # NSBezelStyleTexturedRounded
        self.button.setAction_("openGPT:")
        self.button.setTarget_(self)
        self.button.setButtonType_(0)  # NSMomentaryLightButton
        self.button.setBordered_(False)
        self.button.setWantsLayer_(True)

        button_bg = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.133, 0.133, 0.133, 1.0)  # #222222
        self.button.layer().setBackgroundColor_(button_bg.CGColor())
        self.button.layer().setCornerRadius_(4)

        attr_title = NSAttributedString.alloc().initWithString_attributes_(
            "GPT",
            NSDictionary.dictionaryWithObject_forKey_(
                NSColor.whiteColor(), NSForegroundColorAttributeName
            )
        )
        self.button.setAttributedTitle_(attr_title)

        parent_view.addSubview_(self.button)

    def openGPT_(self, sender):
        webbrowser.open("https://chat.openai.com")

class WizlabsButton:
    def __init__(self, parent_view, x, y, width, height):
        self.button = NSButton.alloc().initWithFrame_(
            NSMakeRect(x, y, width, height)
        )
        self.button.setTitle_("Wizlabs")
        self.button.setBezelStyle_(4)  # NSBezelStyleTexturedRounded
        self.button.setAction_("openWizlabs:")
        self.button.setTarget_(self)
        self.button.setButtonType_(0)  # NSMomentaryLightButton
        self.button.setBordered_(False)
        self.button.setWantsLayer_(True)

        button_bg = NSColor.colorWithCalibratedRed_green_blue_alpha_(0.133, 0.133, 0.133, 1.0)  # #222222
        self.button.layer().setBackgroundColor_(button_bg.CGColor())
        self.button.layer().setCornerRadius_(4)

        attr_title = NSAttributedString.alloc().initWithString_attributes_(
            "Wizlabs",
            NSDictionary.dictionaryWithObject_forKey_(
                NSColor.whiteColor(), NSForegroundColorAttributeName
            )
        )
        self.button.setAttributedTitle_(attr_title)

        parent_view.addSubview_(self.button)

    def openWizlabs_(self, sender):
        webbrowser.open("https://wizlabs.co") 