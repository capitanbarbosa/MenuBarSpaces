import AppKit
import ApplicationServices

final class AppDelegate: NSObject, NSApplicationDelegate {
    private var statusItemController: StatusItemController?

    func applicationDidFinishLaunching(_ notification: Notification) {
        // Do not force the system prompt on every launch — it fights with an
        // already-enabled toggle after rebuilds. DesktopSwitcher prompts on use.
        statusItemController = StatusItemController()

        if !AXIsProcessTrusted() {
            print("ActiveMenuBar: Accessibility OFF for \(Bundle.main.bundlePath)")
            print("Enable that exact app in System Settings → Privacy & Security → Accessibility")
        } else {
            print("ActiveMenuBar: Accessibility ON")
        }
    }

    func applicationWillTerminate(_ notification: Notification) {
        statusItemController = nil
    }
}
