import os
import webbrowser
import subprocess
from Cocoa import NSStatusBar, NSVariableStatusItemLength, NSImage, NSSize

_DIR = os.path.dirname(os.path.abspath(__file__))


def _icon(filename, width, height):
    path = os.path.join(_DIR, filename)
    icon = NSImage.alloc().initWithContentsOfFile_(path)
    if icon:
        icon.setSize_(NSSize(width, height))
        icon.setTemplate_(False)
    return icon


class GPTButton:
    def __init__(self):
        self.status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(
            NSVariableStatusItemLength
        )
        self.status_item.button().setTitle_("GPT")
        self.status_item.button().setToolTip_("Open ChatGPT")
        self.status_item.button().setTarget_(self)
        self.status_item.button().setAction_("openGPT:")

    def openGPT_(self, sender):
        webbrowser.open("https://chat.openai.com")


class WizlabsButton:
    def __init__(self):
        self.status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(
            NSVariableStatusItemLength
        )
        self.status_item.button().setTitle_("wizlabs")
        self.status_item.button().setToolTip_("Open wizlabs.co")
        self.status_item.button().setTarget_(self)
        self.status_item.button().setAction_("openWizlabs:")

    def openWizlabs_(self, sender):
        webbrowser.open("https://wizlabs.co")


class WhatsAppButton:
    def __init__(self):
        self.status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(
            NSVariableStatusItemLength
        )
        icon = _icon("whatsapp.png", 18, 18)
        if icon:
            self.status_item.button().setImage_(icon)
        else:
            self.status_item.button().setTitle_("WA")
        self.status_item.button().setToolTip_("Open WhatsApp")
        self.status_item.button().setTarget_(self)
        self.status_item.button().setAction_("toggleWhatsApp:")

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
            result = subprocess.run(
                ["osascript", "-e", script_bring_to_front],
                capture_output=True,
                text=True,
                check=True,
            )
            if result.stdout.strip() == "not running":
                subprocess.run(["open", "-a", "WhatsApp"], check=True)
        except Exception as e:
            print(f"Error in toggleWhatsApp: {e}")
            try:
                subprocess.run(["open", "-a", "WhatsApp"], check=True)
            except Exception as e_open:
                print(f"Fallback launch of WhatsApp also failed: {e_open}")


class GmailButton:
    def __init__(self):
        self.status_item = NSStatusBar.systemStatusBar().statusItemWithLength_(
            NSVariableStatusItemLength
        )
        icon = _icon("gmail.png", 18, 18)
        if icon:
            self.status_item.button().setImage_(icon)
        else:
            self.status_item.button().setTitle_("Gmail")
        self.status_item.button().setToolTip_("Open Gmail")
        self.status_item.button().setTarget_(self)
        self.status_item.button().setAction_("openGmail:")

    def openGmail_(self, sender):
        webbrowser.open("https://mail.google.com")
