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

            Text("Space names (\(nameStore.names.count))")
                .font(.subheadline.bold())

            nameFields
                .frame(maxHeight: nameStore.names.count > 7 ? renameListHeight : nil)

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
                .lineLimit(2)
                .truncationMode(.middle)
                .frame(maxWidth: .infinity, alignment: .leading)

            Divider()

            Button("Quit") {
                NSApp.terminate(nil)
            }
            .keyboardShortcut("q")
        }
        .padding(16)
        .frame(width: 320, alignment: .topLeading)
        .fixedSize(horizontal: true, vertical: true)
        .ignoresSafeArea()
        .onAppear(perform: refreshStatus)
    }

    @ViewBuilder
    private var nameFields: some View {
        let fields = VStack(spacing: 6) {
            ForEach(nameStore.names.indices, id: \.self) { index in
                HStack {
                    Text("\(index + 1)")
                        .foregroundStyle(.secondary)
                        .frame(width: 16, alignment: .trailing)

                    TextField(
                        "Desktop \(index + 1)",
                        text: Binding(
                            get: { nameStore.editableName(for: index) },
                            set: { nameStore.setName($0, for: index) }
                        )
                    )
                    .textFieldStyle(.roundedBorder)
                }
            }
        }

        if nameStore.names.count > 7 {
            ScrollView {
                fields
            }
            .frame(height: renameListHeight)
        } else {
            fields
        }
    }

    private func refreshStatus() {
        accessibilityOn = AXIsProcessTrusted()
        spaceAPI = SpaceBridge.isAvailable
        desktopIndex = SpaceBridge.currentDesktopIndex().map(String.init) ?? "?"
        appPath = Bundle.main.bundlePath
    }

    private var renameListHeight: CGFloat {
        CGFloat(min(max(nameStore.names.count, 1), 7)) * 30
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
