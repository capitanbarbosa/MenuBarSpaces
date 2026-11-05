import AppKit
import ApplicationServices
import CoreGraphics
import SwiftUI

/// Tahoe’s status-item host flashes a gap then hides third-party extras.
/// This draws the desktop names in a menu-bar-level panel instead.
final class StatusItemController: NSObject {
    private var panel: NSPanel?
    private let popover = NSPopover()
    private let nameStore = SpaceNameStore(desktopCount: SpaceBridge.desktopCount())
    private var desktopSwitcher: DesktopSwitcher?
    private let strip = DesktopStripView(frame: NSRect(x: 0, y: 0, width: 160, height: 22))
    private var screenObserver: NSObjectProtocol?
    private var positionTimer: Timer?
    private var suppressPositionUntil = Date.distantPast
    private var lastStripSize: NSSize = .zero

    override init() {
        super.init()
        popover.behavior = .transient
        popover.animates = false

        desktopSwitcher = DesktopSwitcher(nameStore: nameStore)
        desktopSwitcher?.onChange = { [weak self] in
            self?.suppressPositionUntil = Date().addingTimeInterval(0.8)
            self?.refreshStrip()
        }
        strip.onSelectDesktop = { [weak self] desktop in
            self?.desktopSwitcher?.switchToDesktop(desktop)
        }
        strip.onSpaces = { [weak self] in
            self?.togglePopover()
        }

        installPanel()
        refreshStrip()

        screenObserver = NotificationCenter.default.addObserver(
            forName: NSApplication.didChangeScreenParametersNotification,
            object: nil,
            queue: .main
        ) { [weak self] _ in
            self?.positionPanel()
        }
        positionTimer = Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { [weak self] _ in
            self?.positionPanel()
        }
    }

    deinit {
        if let screenObserver {
            NotificationCenter.default.removeObserver(screenObserver)
        }
        positionTimer?.invalidate()
        panel?.orderOut(nil)
        panel = nil
    }

    private func installPanel() {
        let panel = NSPanel(
            contentRect: NSRect(x: 0, y: 0, width: 160, height: 22),
            styleMask: [.borderless, .nonactivatingPanel],
            backing: .buffered,
            defer: false
        )
        panel.isFloatingPanel = true
        panel.level = .statusBar
        panel.collectionBehavior = [
            .canJoinAllSpaces,
            .stationary,
            .fullScreenAuxiliary,
            .ignoresCycle,
        ]
        panel.isOpaque = false
        panel.backgroundColor = .clear
        panel.hasShadow = false
        panel.hidesOnDeactivate = false
        panel.isReleasedWhenClosed = false
        panel.ignoresMouseEvents = false
        panel.becomesKeyOnlyIfNeeded = true
        panel.animationBehavior = .none
        panel.contentView = strip
        self.panel = panel
        panel.orderFrontRegardless()
    }

    private func refreshStrip() {
        strip.names = nameStore.names.indices.map { nameStore.name(for: $0) }
        strip.currentDesktop = desktopSwitcher?.currentDesktop ?? 1
        strip.needsDisplay = true

        let size = strip.fittingSize()
        let sizeChanged = abs(size.width - lastStripSize.width) > 0.5
            || abs(size.height - lastStripSize.height) > 0.5
        lastStripSize = size
        if sizeChanged {
            strip.frame = NSRect(origin: .zero, size: size)
            panel?.setContentSize(size)
            positionPanel()
        }
    }

    private func positionPanel() {
        guard Date() >= suppressPositionUntil else { return }
        guard let panel, let screen = NSScreen.main else { return }
        let frame = screen.frame
        let visible = screen.visibleFrame
        let menuBarHeight = max(frame.maxY - visible.maxY, 24)
        let size = panel.frame.size
        let gap: CGFloat = 8
        let leftmostExtra = leftmostForeignMenuBarX(on: screen) ?? (visible.maxX - 220)
        var x = leftmostExtra - size.width - gap
        x = min(max(x, visible.minX + 8), visible.maxX - size.width - 8)
        let y = frame.maxY - menuBarHeight + (menuBarHeight - size.height) / 2
        let next = NSRect(x: x, y: y, width: size.width, height: size.height)
        if abs(panel.frame.origin.x - next.origin.x) > 12 || abs(panel.frame.origin.y - next.origin.y) > 2 {
            panel.setFrame(next, display: true)
        }
    }

    /// CG-window X of the leftmost on-screen extra in the menu bar, excluding us.
    private func leftmostForeignMenuBarX(on screen: NSScreen) -> CGFloat? {
        let options: CGWindowListOption = [.optionOnScreenOnly, .excludeDesktopElements]
        guard let info = CGWindowListCopyWindowInfo(options, kCGNullWindowID) as? [[String: Any]] else {
            return nil
        }
        let ourPID = ProcessInfo.processInfo.processIdentifier
        var leftmost: CGFloat?
        for window in info {
            let pid = window[kCGWindowOwnerPID as String] as? pid_t ?? 0
            if pid == ourPID { continue }
            let layer = window[kCGWindowLayer as String] as? Int ?? 0
            // 25 = status extras. 24 is the menu bar itself (app menus) — skip it
            // or the strip is pulled over File/Edit/View.
            guard layer == 25 else { continue }
            let owner = window[kCGWindowOwnerName as String] as? String ?? ""
            if owner == "Window Server" { continue }
            guard let bounds = window[kCGWindowBounds as String] as? [String: Any] else { continue }
            let x = (bounds["X"] as? CGFloat) ?? CGFloat((bounds["X"] as? NSNumber)?.doubleValue ?? 0)
            let y = (bounds["Y"] as? CGFloat) ?? CGFloat((bounds["Y"] as? NSNumber)?.doubleValue ?? 0)
            let width = (bounds["Width"] as? CGFloat) ?? CGFloat((bounds["Width"] as? NSNumber)?.doubleValue ?? 0)
            let height = (bounds["Height"] as? CGFloat) ?? CGFloat((bounds["Height"] as? NSNumber)?.doubleValue ?? 0)
            guard height > 8, height < 44, width > 8, width < 400 else { continue }
            guard y < 48 else { continue }
            guard x > screen.frame.midX - 24 else { continue }
            leftmost = min(leftmost ?? x, x)
        }
        return leftmost
    }

    private func togglePopover() {
        guard let panel else { return }
        if popover.isShown {
            popover.performClose(nil)
            return
        }

        let hosting = NSHostingController(
            rootView: PlaceholderPopoverView(nameStore: nameStore)
                .ignoresSafeArea()
        )
        hosting.sizingOptions = [.preferredContentSize]
        if #available(macOS 13.3, *) {
            hosting.safeAreaRegions = []
        }

        var size = hosting.sizeThatFits(in: NSSize(width: 320, height: 8_000))
        if size.width < 320 { size.width = 320 }
        if size.height < estimatedHeight { size.height = estimatedHeight }
        hosting.preferredContentSize = size
        popover.contentViewController = hosting
        popover.contentSize = size
        popover.show(relativeTo: strip.bounds, of: strip, preferredEdge: .minY)
        panel.orderFrontRegardless()
    }

    private var estimatedHeight: CGFloat {
        let names = CGFloat(min(max(nameStore.names.count, 1), 7))
        var height: CGFloat = 16 + 22 + 10 + 18 + 10
        height += names * 28 + max(0, names - 1) * 6
        height += 10 + 21 + 10 + 1 + 10
        height += 18 + 10 + 18 + 10 + 18
        if !AXIsProcessTrusted() {
            height += 34
        }
        height += 10 + 32 + 10 + 1 + 10 + 21 + 16
        return ceil(height)
    }
}
