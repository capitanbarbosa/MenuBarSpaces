import webbrowser
import subprocess
from Cocoa import NSButton, NSMakeRect, NSColor, NSAttributedString, NSDictionary, NSForegroundColorAttributeName, NSImage, NSSize

class GPTButton:
    def __init__(self, parent_view, x, y, width, height):
        self.button = NSButton.alloc().initWithFrame_(
            NSMakeRect(x, y, width, height)
        )
        self.button.setTitle_("GPT")
        self.button.setBezelStyle_(0)
        self.button.setBordered_(False)
        self.button.setWantsLayer_(True)
        self.button.layer().setBackgroundColor_(NSColor.clearColor().CGColor())
        self.button.setAction_("openGPT:")
        self.button.setTarget_(self)
        self.button.setButtonType_(0)

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
        self.button.setBezelStyle_(0)
        self.button.setBordered_(False)
        self.button.setWantsLayer_(True)
        self.button.layer().setBackgroundColor_(NSColor.clearColor().CGColor())
        self.button.setAction_("openWizlabs:")
        self.button.setTarget_(self)
        self.button.setButtonType_(0)

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

class WhatsAppButton:
    def __init__(self, parent_view, x, y, width, height):
        self.button = NSButton.alloc().initWithFrame_(
            NSMakeRect(x, y, width, height)
        )
        self.button.setBezelStyle_(0)
        self.button.setBordered_(False)
        self.button.setWantsLayer_(True)
        self.button.layer().setBackgroundColor_(NSColor.clearColor().CGColor())
        self.button.setAction_("toggleWhatsApp:")
        self.button.setTarget_(self)
        
        icon = NSImage.alloc().initWithContentsOfFile_("whatsapp.png")
        if icon:
            icon.setSize_(NSSize(27, 20))
            self.button.setImage_(icon)
            
        parent_view.addSubview_(self.button)

    def toggleWhatsApp_(self, sender):
        script_bring_to_front = '''
        tell application "System Events"
            set process_list to name of every process
            if "WhatsApp" is in process_list then
                tell application "WhatsApp"
                    activate
                end tell
                return "activated"
            else
                return "not running"
            end if
        end tell
        '''
        try:
            result = subprocess.run(['osascript', '-e', script_bring_to_front], capture_output=True, text=True, check=True)
            if result.stdout.strip() == "not running":
                subprocess.run(['open', '-a', 'WhatsApp'], check=True)
        except Exception as e:
            print(f"Error in toggleWhatsApp: {e}")
            try:
                subprocess.run(['open', '-a', 'WhatsApp'], check=True)
            except Exception as e_open:
                print(f"Fallback launch of WhatsApp also failed: {e_open}")

class GmailButton:
    def __init__(self, parent_view, x, y, width, height):
        self.button = NSButton.alloc().initWithFrame_(
            NSMakeRect(x, y, width, height)
        )
        self.button.setBezelStyle_(0)
        self.button.setBordered_(False)
        self.button.setWantsLayer_(True)
        self.button.layer().setBackgroundColor_(NSColor.clearColor().CGColor())
        self.button.setAction_("openGmail:")
        self.button.setTarget_(self)
        
        icon = NSImage.alloc().initWithContentsOfFile_("gmail.png")
        if icon:
            icon.setSize_(NSSize(20, 20))
            self.button.setImage_(icon)

        parent_view.addSubview_(self.button)

    def openGmail_(self, sender):
        webbrowser.open("https://mail.google.com") 