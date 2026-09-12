import AppKit
import SwiftUI

final class StatusItemController {
    private var spacesItem: NSStatusItem?
    private let popover: NSPopover
    private var desktopSwitcher: DesktopSwitcher?

    init() {
        popover = NSPopover()
        popover.contentSize = NSSize(width: 260, height: 160)
        popover.behavior = .transient
        popover.contentViewController = NSHostingController(
            rootView: PlaceholderPopoverView()
        )

        // Creation order ≈ left→right among this app's status items
        installSpacesButton()
        desktopSwitcher = DesktopSwitcher()
    }

    private func installSpacesButton() {
        let item = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        if let button = item.button {
            button.title = "Spaces"
            button.toolTip = "Active Menu Bar (placeholder)"
            button.action = #selector(togglePopover(_:))
            button.target = self
        }
        spacesItem = item
    }

    @objc private func togglePopover(_ sender: Any?) {
        guard let button = spacesItem?.button else { return }

        if popover.isShown {
            popover.performClose(sender)
        } else {
            popover.show(relativeTo: button.bounds, of: button, preferredEdge: .minY)
            popover.contentViewController?.view.window?.makeKey()
        }
    }
}
