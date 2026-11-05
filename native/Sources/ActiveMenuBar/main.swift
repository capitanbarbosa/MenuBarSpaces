import AppKit

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.setActivationPolicy(.accessory)
ProcessInfo.processInfo.disableAutomaticTermination("menu bar extra")
ProcessInfo.processInfo.disableSuddenTermination()
app.run()
