import AppKit
import ApplicationServices
import SwiftUI

struct PlaceholderPopoverView: View {
    @ObservedObject var nameStore: SpaceNameStore

    @State private var accessibilityOn = false
    @State private var spaceAPI = false
    @State private var desktopIndex = "?"
    @State private var appPath = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Active Menu Bar")
                .font(.headline)

            Text("Space names")
                .font(.subheadline.bold())

            ForEach(0..<SpaceNameStore.desktopCount, id: \.self) { index in
                HStack {
                    Text("\(index + 1)")
                        .foregroundStyle(.secondary)
                        .frame(width: 16, alignment: .trailing)

                    TextField(
                        "Desktop \(index + 1)",
                        text: Binding(
                            get: { nameStore.names[index] },
                            set: { nameStore.setName($0, for: index) }
                        )
                    )
                    .textFieldStyle(.roundedBorder)
                }
            }

            Button("Reset names") {
                nameStore.reset()
            }
            .controlSize(.small)

            Divider()

            Text("Desktop: \(desktopIndex)")
                .font(.subheadline)

            Text("Space API: \(spaceAPI ? "ON" : "OFF")")
                .font(.subheadline)
                .foregroundStyle(spaceAPI ? Color.primary : Color.red)

            Text(accessibilityOn ? "Accessibility: ON" : "Accessibility: OFF")
                .font(.subheadline)
                .foregroundStyle(.secondary)

            if !accessibilityOn {
                Button("Enable Accessibility…") {
                    requestAccessibility()
                }
            }

            Text(appPath.isEmpty ? "…" : appPath)
                .font(.caption2)
                .foregroundStyle(.secondary)
                .lineLimit(3)

            Divider()

            Button("Quit") {
                NSApp.terminate(nil)
            }
            .keyboardShortcut("q")
        }
        .padding(16)
        .frame(width: 300, alignment: .leading)
        .onAppear(perform: refreshStatus)
    }

    private func refreshStatus() {
        accessibilityOn = AXIsProcessTrusted()
        spaceAPI = SpaceBridge.isAvailable
        desktopIndex = SpaceBridge.currentDesktopIndex().map(String.init) ?? "?"
        appPath = Bundle.main.bundlePath
    }

    private func requestAccessibility() {
        let options = [
            kAXTrustedCheckOptionPrompt.takeUnretainedValue() as String: true
        ] as CFDictionary
        _ = AXIsProcessTrustedWithOptions(options)

        if let settingsURL = URL(
            string: "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"
        ) {
            NSWorkspace.shared.open(settingsURL)
        }

        // TCC may take a moment to report a newly changed setting.
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            refreshStatus()
        }
    }
}
