import AppKit

final class DesktopStripView: NSView {
    var names: [String] = []
    var currentDesktop = 1
    var onSelectDesktop: ((Int) -> Void)?
    var onSpaces: (() -> Void)?

    private let font = NSFont.menuBarFont(ofSize: 12)
    private let activeFont = NSFont.boldSystemFont(ofSize: 12)
    private let spacing: CGFloat = 8
    private let inset: CGFloat = 8
    private var nameRects: [Int: NSRect] = [:]
    private var spacesRect: NSRect = .zero
    private let spacesTitle = "[ ]"

    override var isFlipped: Bool { true }
    override var isOpaque: Bool { false }
    override var acceptsFirstResponder: Bool { false }

    override func acceptsFirstMouse(for event: NSEvent?) -> Bool { true }

    func fittingSize() -> NSSize {
        layoutLabels(in: NSRect(x: 0, y: 0, width: 4_000, height: 22))
        return NSSize(width: max(ceil(spacesRect.maxX + inset), 64), height: 22)
    }

    override func draw(_ dirtyRect: NSRect) {
        NSColor.clear.setFill()
        bounds.fill()
        layoutLabels(in: bounds)
        for (index, name) in names.enumerated() {
            let desktop = index + 1
            let active = desktop == currentDesktop
            let title = active ? "[\(name)]" : name
            guard let rect = nameRects[desktop] else { continue }
            let attrs: [NSAttributedString.Key: Any] = [
                .font: active ? activeFont : font,
                .foregroundColor: active ? NSColor.labelColor : NSColor.secondaryLabelColor,
            ]
            let textSize = (title as NSString).size(withAttributes: attrs)
            let drawRect = NSRect(
                x: rect.minX + (rect.width - textSize.width) / 2,
                y: rect.minY,
                width: textSize.width,
                height: rect.height
            )
            title.draw(in: drawRect, withAttributes: attrs)
        }
        spacesTitle.draw(
            in: spacesRect,
            withAttributes: [
                .font: font,
                .foregroundColor: NSColor.labelColor,
            ]
        )
    }

    override func mouseDown(with event: NSEvent) {
        let point = convert(event.locationInWindow, from: nil)
        for (desktop, rect) in nameRects where rect.insetBy(dx: -4, dy: -3).contains(point) {
            onSelectDesktop?(desktop)
            return
        }
        if spacesRect.insetBy(dx: -4, dy: -3).contains(point) {
            onSpaces?()
        }
    }

    private func slotWidth(for name: String) -> CGFloat {
        let plain = (name as NSString).size(withAttributes: [.font: font]).width
        let active = ("[\(name)]" as NSString).size(withAttributes: [.font: activeFont]).width
        return ceil(max(plain, active))
    }

    private func layoutLabels(in bounds: NSRect) {
        nameRects.removeAll()
        var x = inset
        let y = max((bounds.height - 15) / 2, 2)
        for (index, name) in names.enumerated() {
            let desktop = index + 1
            let width = slotWidth(for: name)
            nameRects[desktop] = NSRect(x: x, y: y, width: width, height: 16)
            x += width + spacing
        }
        x += 2
        let spacesWidth = ceil((spacesTitle as NSString).size(withAttributes: [.font: font]).width)
        spacesRect = NSRect(x: x, y: y, width: spacesWidth, height: 16)
    }
}
