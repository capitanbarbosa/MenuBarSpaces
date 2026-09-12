import AppKit
import ApplicationServices

/// Menu-bar desktop buttons 1…4. Switches Spaces via SkyLight (not keystrokes).
final class DesktopSwitcher {
    private let desktopCount = 4
    private var statusItems: [NSStatusItem] = []
    private var currentDesktop = 1
    private var isSwitching = false

    init() {
        installButtons()
        syncFromSystem()
        refreshButtonAppearance()
    }

    private func installButtons() {
        for index in 1...desktopCount {
            let item = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
            if let button = item.button {
                button.title = "\(index)"
                button.toolTip = "Switch to Desktop \(index)"
                button.tag = index
                button.target = self
                button.action = #selector(desktopClicked(_:))
            }
            statusItems.append(item)
        }
    }

    @objc private func desktopClicked(_ sender: NSStatusBarButton) {
        switchToDesktop(sender.tag)
    }

    func switchToDesktop(_ target: Int) {
        guard (1...desktopCount).contains(target) else { return }
        guard !isSwitching else { return }

        syncFromSystem()
        guard target != currentDesktop else { return }

        isSwitching = true
        let ok = SpaceBridge.focusDesktop(index: target)
        isSwitching = false

        if ok {
            currentDesktop = target
            refreshButtonAppearance()
            print("ActiveMenuBar: switched to desktop \(target)")
        } else {
            print("ActiveMenuBar: failed to switch to desktop \(target) (SkyLight available=\(SpaceBridge.isAvailable))")
            NSSound.beep()
        }
    }

    private func syncFromSystem() {
        if let index = SpaceBridge.currentDesktopIndex(),
           (1...desktopCount).contains(index) {
            currentDesktop = index
        }
    }

    private func refreshButtonAppearance() {
        for (offset, item) in statusItems.enumerated() {
            let index = offset + 1
            guard let button = item.button else { continue }

            let isActive = index == currentDesktop
            let title = isActive ? "[\(index)]" : "\(index)"
            let color: NSColor = isActive ? .labelColor : .secondaryLabelColor

            button.attributedTitle = NSAttributedString(
                string: title,
                attributes: [
                    .foregroundColor: color,
                    .font: NSFont.systemFont(ofSize: 12),
                ]
            )
        }
    }
}
