import AppKit
import ApplicationServices
import Combine

/// Tracks Mission Control desktops and switches among them.
final class DesktopSwitcher {
    private let nameStore: SpaceNameStore
    private(set) var currentDesktop = 1
    private var isSwitching = false
    private var spaceObserver: NSObjectProtocol?
    private var pollTimer: Timer?
    private var nameObserver: AnyCancellable?
    var onChange: (() -> Void)?

    init(nameStore: SpaceNameStore) {
        self.nameStore = nameStore
        syncFromSystem()
        startWatchingSpaceChanges()
        nameObserver = nameStore.$names.sink { [weak self] _ in
            self?.onChange?()
        }
    }

    deinit {
        if let spaceObserver {
            NSWorkspace.shared.notificationCenter.removeObserver(spaceObserver)
        }
        pollTimer?.invalidate()
    }

    private func startWatchingSpaceChanges() {
        spaceObserver = NSWorkspace.shared.notificationCenter.addObserver(
            forName: NSWorkspace.activeSpaceDidChangeNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            self?.syncFromSystem()
            self?.onChange?()
        }

        pollTimer = Timer.scheduledTimer(withTimeInterval: 0.4, repeats: true) { [weak self] _ in
            guard let self, !self.isSwitching else { return }
            let previousDesktop = self.currentDesktop
            let previousCount = self.nameStore.names.count
            self.syncFromSystem()
            if self.currentDesktop != previousDesktop || self.nameStore.names.count != previousCount {
                self.onChange?()
            }
        }
    }

    func switchToDesktop(_ target: Int) {
        let desktopCount = nameStore.names.count
        guard target >= 1, target <= desktopCount else { return }
        guard !isSwitching else { return }

        syncFromSystem()
        guard target != currentDesktop else {
            onChange?()
            return
        }

        isSwitching = true
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            let ok = SpaceBridge.focusDesktop(index: target)
            DispatchQueue.main.async {
                guard let self else { return }
                self.isSwitching = false
                self.syncFromSystem()
                self.onChange?()
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

        if let index = SpaceBridge.currentDesktopIndex(),
           index >= 1, index <= nameStore.names.count {
            currentDesktop = index
        }
    }
}
