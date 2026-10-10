import Combine
import Foundation

final class SpaceNameStore: ObservableObject {
    static let defaultNames = ["Log", "dev", "biz", "kgp"]

    @Published private(set) var names: [String]

    private let defaults: UserDefaults
    private let defaultsKey = "desktopNames"

    init(desktopCount: Int, defaults: UserDefaults = .standard) {
        self.defaults = defaults
        let count = max(desktopCount, 1)
        let saved = defaults.stringArray(forKey: defaultsKey) ?? Self.defaultNames
        names = Self.names(saved, adjustedTo: count)
        defaults.set(names, forKey: defaultsKey)
    }

    private static func defaultName(for index: Int) -> String {
        defaultNames.indices.contains(index) ? defaultNames[index] : "\(index + 1)"
    }

    private static func names(_ existing: [String], adjustedTo count: Int) -> [String] {
        var adjusted = Array(existing.prefix(count))
        while adjusted.count < count {
            adjusted.append(defaultName(for: adjusted.count))
        }
        return adjusted
    }

    func name(for index: Int) -> String {
        guard names.indices.contains(index) else { return "Desktop \(index + 1)" }
        let name = names[index].trimmingCharacters(in: .whitespacesAndNewlines)
        return name.isEmpty ? "\(index + 1)" : name
    }

    /// Safe raw value for transient SwiftUI rows while the Spaces array shrinks.
    func editableName(for index: Int) -> String {
        guard names.indices.contains(index) else { return "" }
        return names[index]
    }

    func setName(_ name: String, for index: Int) {
        guard names.indices.contains(index) else { return }
        names[index] = String(name.prefix(20))
        defaults.set(names, forKey: defaultsKey)
    }

    func updateDesktopCount(_ desktopCount: Int) {
        let count = max(desktopCount, 1)
        guard count != names.count else { return }
        names = Self.names(names, adjustedTo: count)
        defaults.set(names, forKey: defaultsKey)
    }

    func reset() {
        names = Self.names([], adjustedTo: names.count)
        defaults.set(names, forKey: defaultsKey)
    }
}
