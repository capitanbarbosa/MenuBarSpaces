import AppKit
import ApplicationServices
import SwiftUI

struct PlaceholderPopoverView: View {
    private var accessibilityOn: Bool { AXIsProcessTrusted() }
    private var spaceAPI: Bool { SpaceBridge.isAvailable }
    private var appPath: String { Bundle.main.bundlePath }
    private var desktopIndex: String {
        if let i = SpaceBridge.currentDesktopIndex() { return "\(i)" }
        return "?"
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Active Menu Bar")
                .font(.headline)

            Text("Desktop: \(desktopIndex)  ·  Space API: \(spaceAPI ? "ON" : "OFF")")
                .font(.subheadline)
                .foregroundStyle(.secondary)

            Text(accessibilityOn ? "Accessibility: ON" : "Accessibility: OFF")
                .font(.subheadline)
                .foregroundStyle(accessibilityOn ? Color.secondary : Color.red)

            Text(appPath)
                .font(.caption2)
                .foregroundStyle(.secondary)
                .textSelection(.enabled)

            Divider()

            Button("Quit") {
                NSApp.terminate(nil)
            }
            .keyboardShortcut("q")
        }
        .padding(16)
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
    }
}
