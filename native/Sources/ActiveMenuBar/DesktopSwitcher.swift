import AppKit
import ApplicationServices
import Combine

/// One menu-bar button per regular Desktop. Tracks Mission Control additions,
/// removals, ordering, and active-space changes.
final class DesktopSwitcher {
    private let nameStore: SpaceNameStore
    private var desktopCount: Int { nameStore.names.count }
    /// Keyed by desktop index. macOS places newer status items to the left, so
    /// items are created in reverse for left-to-right Mission Control order.
    private var statusItemsByDesktop: [Int: NSStatusItem] = [:]
    private var currentDesktop = 1
    private var isSwitching = false
    private var spaceObserver: NSObjectProtocol?
    private var pollTimer: Timer?
    private var nameObserver: AnyCancellable?

    init(nameStore: SpaceNameStore) {
        self.nameStore = nameStore
        installButtons()
        syncFromSystem()
        refreshButtonAppearance()
        startWatchingSpaceChanges()
        nameObserver = nameStore.$names.sink { [weak self] names in
            guard let self else { return }
            if self.statusItemsByDesktop.count != names.count {
                self.rebuildButtons()
            } else {
                self.refreshButtonAppearance()
            }
        }
    }

    deinit {
        if let spaceObserver {
            NSWorkspace.shared.notificationCenter.removeObserver(spaceObserver)
        }
        pollTimer?.invalidate()
        statusItemsByDesktop.values.forEach(NSStatusBar.system.removeStatusItem)
    }

    private func installButtons() {
        for index in stride(from: desktopCount, through: 1, by: -1) {
            let item = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
            if let button = item.button {
                let name = nameStore.name(for: index - 1)
                button.title = name
                button.toolTip = "Switch to \(name) (Desktop \(index))"
                button.tag = index
                button.target = self
                button.action = #selector(desktopClicked(_:))
            }
            statusItemsByDesktop[index] = item
        }
    }

    private func rebuildButtons() {
        statusItemsByDesktop.values.forEach(NSStatusBar.system.removeStatusItem)
        statusItemsByDesktop.removeAll()
        installButtons()
        refreshButtonAppearance()
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
            let previousDesktop = self.currentDesktop
            let previousCount = self.desktopCount
            self.syncFromSystem()
            if self.currentDesktop != previousDesktop || self.desktopCount != previousCount {
                self.refreshButtonAppearance()
            }
        }
    }

    @objc private func desktopClicked(_ sender: NSStatusBarButton) {
        switchToDesktop(sender.tag)
    }

    func switchToDesktop(_ target: Int) {
        guard target >= 1, target <= desktopCount else { return }
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
        let systemCount = SpaceBridge.desktopCount()
        if systemCount > 0 {
            nameStore.updateDesktopCount(systemCount)
        }

        if let index = SpaceBridge.currentDesktopIndex() {
            if index >= 1, index <= desktopCount {
                currentDesktop = index
            }
        }
    }

    private func refreshButtonAppearance() {
        for offset in nameStore.names.indices {
            let index = offset + 1
            guard let button = statusItemsByDesktop[index]?.button else { continue }

            let isActive = index == currentDesktop
            let name = nameStore.name(for: index - 1)
            let title = isActive ? "[\(name)]" : name
            let color: NSColor = isActive ? .labelColor : .secondaryLabelColor

            button.toolTip = "Switch to \(name) (Desktop \(index))"
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
