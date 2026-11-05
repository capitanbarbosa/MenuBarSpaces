import AppKit
import ApplicationServices

final class AppDelegate: NSObject, NSApplicationDelegate {
    private var statusItemController: StatusItemController?

    func applicationDidFinishLaunching(_ notification: Notification) {
        ProcessInfo.processInfo.disableAutomaticTermination("menu bar extra")
        ProcessInfo.processInfo.disableSuddenTermination()
        NSApp.setActivationPolicy(.accessory)

        let myPID = ProcessInfo.processInfo.processIdentifier
        let bundleID = Bundle.main.bundleIdentifier ?? "com.wiz.ActiveMenuBar"
        for app in NSRunningApplication.runningApplications(withBundleIdentifier: bundleID)
        where app.processIdentifier != myPID {
            app.forceTerminate()
        }

        // Saved "not visible" flags make extras flash an empty gap then vanish.
        let defaults = UserDefaults.standard
        for key in defaults.dictionaryRepresentation().keys
        where key.hasPrefix("NSStatusItem") {
            defaults.removeObject(forKey: key)
        }

        statusItemController = StatusItemController()

        if !AXIsProcessTrusted() {
            print("ActiveMenuBar: Accessibility OFF for \(Bundle.main.bundlePath)")
            print("Enable that exact app in System Settings → Privacy & Security → Accessibility")
        } else {
            print("ActiveMenuBar: Accessibility ON")
        }
    }

    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        false
    }

    func applicationWillTerminate(_ notification: Notification) {
        statusItemController = nil
    }
}
