import Combine
import Foundation

final class SpaceNameStore: ObservableObject {
    static let desktopCount = 4
    static let defaultNames = ["Log", "dev", "biz", "kgp"]

    @Published private(set) var names: [String]

    private let defaults: UserDefaults
    private let defaultsKey = "desktopNames"

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults

        if let saved = defaults.stringArray(forKey: defaultsKey),
           saved.count == Self.desktopCount {
            names = saved
        } else {
            names = Self.defaultNames
        }
    }

    func name(for index: Int) -> String {
        guard names.indices.contains(index) else { return "Desktop \(index + 1)" }
        let name = names[index].trimmingCharacters(in: .whitespacesAndNewlines)
        return name.isEmpty ? "\(index + 1)" : name
    }

    func setName(_ name: String, for index: Int) {
        guard names.indices.contains(index) else { return }
        names[index] = String(name.prefix(20))
        defaults.set(names, forKey: defaultsKey)
    }

    func reset() {
        names = Self.defaultNames
        defaults.set(names, forKey: defaultsKey)
    }
}
