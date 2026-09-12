import AppKit
import ApplicationServices

/// Menu-bar desktop buttons 1…4. Highlight tracks Mission Control via space-change notifications.
final class DesktopSwitcher {
    private let desktopCount = 4
    /// Keyed by desktop index (1…4). macOS places newer status items to the left,
    /// so we create 4→1 to get a left-to-right visual order of 1 2 3 4.
    private var statusItemsByDesktop: [Int: NSStatusItem] = [:]
    private var currentDesktop = 1
    private var isSwitching = false
    private var spaceObserver: NSObjectProtocol?
    private var pollTimer: Timer?

    init() {
        installButtons()
        syncFromSystem()
        refreshButtonAppearance()
        startWatchingSpaceChanges()
    }

    deinit {
        if let spaceObserver {
            NSWorkspace.shared.notificationCenter.removeObserver(spaceObserver)
        }
        pollTimer?.invalidate()
    }

    private func installButtons() {
        for index in stride(from: desktopCount, through: 1, by: -1) {
            let item = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
            if let button = item.button {
                button.title = "\(index)"
                button.toolTip = "Switch to Desktop \(index)"
                button.tag = index
                button.target = self
                button.action = #selector(desktopClicked(_:))
            }
            statusItemsByDesktop[index] = item
        }
    }

    private func startWatchingSpaceChanges() {
        spaceObserver = NSWorkspace.shared.notificationCenter.addObserver(
            forName: NSWorkspace.activeSpaceDidChangeNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            self?.syncFromSystem()
            self?.refreshButtonAppearance()
        }

        // Backup: gestures / Mission Control don't always post promptly.
        pollTimer = Timer.scheduledTimer(withTimeInterval: 0.4, repeats: true) { [weak self] _ in
            guard let self, !self.isSwitching else { return }
            let before = self.currentDesktop
            self.syncFromSystem()
            if self.currentDesktop != before {
                self.refreshButtonAppearance()
            }
        }
    }

    @objc private func desktopClicked(_ sender: NSStatusBarButton) {
        switchToDesktop(sender.tag)
    }

    func switchToDesktop(_ target: Int) {
        guard (1...desktopCount).contains(target) else { return }
        guard !isSwitching else { return }

        syncFromSystem()
        guard target != currentDesktop else {
            refreshButtonAppearance()
            return
        }

        isSwitching = true
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            let ok = SpaceBridge.focusDesktop(index: target)
            DispatchQueue.main.async {
                guard let self else { return }
                self.isSwitching = false
                self.syncFromSystem()
                self.refreshButtonAppearance()
                if ok {
                    print("ActiveMenuBar: now on desktop \(self.currentDesktop) (requested \(target))")
                } else {
                    print("ActiveMenuBar: failed to reach desktop \(target); still \(self.currentDesktop)")
                    NSSound.beep()
                }
            }
        }
    }

    private func syncFromSystem() {
        if let index = SpaceBridge.currentDesktopIndex() {
            // Prefer live Mission Control count when >4 later; for now clamp to our buttons.
            if (1...desktopCount).contains(index) {
                currentDesktop = index
            } else if index > desktopCount {
                // More than 4 spaces: highlight none of 1…4 as "current" by leaving last,
                // or pin to 4 if we're past it.
                currentDesktop = min(index, desktopCount)
            }
        }
    }

    private func refreshButtonAppearance() {
        for index in 1...desktopCount {
            guard let button = statusItemsByDesktop[index]?.button else { continue }

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
