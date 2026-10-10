import AppKit
import SwiftUI

final class StatusItemController {
    private var spacesItem: NSStatusItem?
    private let popover = NSPopover()
    private let nameStore = SpaceNameStore(desktopCount: SpaceBridge.desktopCount())
    private var desktopSwitcher: DesktopSwitcher?
    private var hostingController: NSHostingController<PlaceholderPopoverView>?

    init() {
        popover.behavior = .transient
        popover.animates = true

        let hosting = NSHostingController(rootView: PlaceholderPopoverView(nameStore: nameStore))
        hosting.sizingOptions = [.intrinsicContentSize]
        popover.contentViewController = hosting
        hostingController = hosting

        // Status items stack right→left as created. Spaces stays rightmost;
        // desktop items are created in reverse to read in Mission Control order.
        installSpacesButton()
        desktopSwitcher = DesktopSwitcher(nameStore: nameStore)
    }

    private func installSpacesButton() {
        let item = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        if let button = item.button {
            button.title = "Spaces"
            button.toolTip = "Active Menu Bar"
            button.action = #selector(togglePopover(_:))
            button.target = self
        }
        spacesItem = item
    }

    @objc private func togglePopover(_ sender: Any?) {
        guard let button = spacesItem?.button else { return }

        if popover.isShown {
            popover.performClose(sender)
            return
        }

        // Rebuild root view so status is current when opened.
        let hosting = NSHostingController(rootView: PlaceholderPopoverView(nameStore: nameStore))
        hosting.sizingOptions = [.intrinsicContentSize]
        popover.contentViewController = hosting
        hostingController = hosting

        popover.show(relativeTo: button.bounds, of: button, preferredEdge: .minY)
    }
}
