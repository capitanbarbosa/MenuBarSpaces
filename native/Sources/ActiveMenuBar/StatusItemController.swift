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

        attachPopoverContent()

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
        attachPopoverContent()
        popover.show(relativeTo: button.bounds, of: button, preferredEdge: .minY)
        syncPopoverSize()
        DispatchQueue.main.async { [weak self] in
            self?.syncPopoverSize()
        }
    }

    private func attachPopoverContent() {
        let hosting = NSHostingController(rootView: PlaceholderPopoverView(nameStore: nameStore))
        hosting.sizingOptions = [.preferredContentSize, .intrinsicContentSize]
        popover.contentViewController = hosting
        hostingController = hosting
        syncPopoverSize()
    }

    private func syncPopoverSize() {
        guard let hosting = hostingController else { return }
        hosting.view.layoutSubtreeIfNeeded()
        var size = hosting.view.fittingSize
        if size.width < 320 {
            size.width = 320
        }
        if size.height < 280 {
            size.height = hosting.view.intrinsicContentSize.height
        }
        if size.height < 280 || size.height == NSView.noIntrinsicMetric {
            size.height = 420
        }
        hosting.preferredContentSize = size
        popover.contentSize = size
    }
}
