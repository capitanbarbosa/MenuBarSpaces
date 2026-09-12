import AppKit
import Darwin
import Foundation

/// Read/switch Mission Control Spaces via SkyLight + a Dock-friendly key fallback.
enum SpaceBridge {
    typealias ConnectionID = Int32
    typealias SpaceID = UInt64

    private static let handle: UnsafeMutableRawPointer? = {
        dlopen("/System/Library/PrivateFrameworks/SkyLight.framework/SkyLight", RTLD_LAZY)
    }()

    private static func symbol<T>(_ name: String) -> T? {
        guard let handle, let sym = dlsym(handle, name) else { return nil }
        return unsafeBitCast(sym, to: T.self)
    }

    private static let mainConnectionID: (@convention(c) () -> ConnectionID)? =
        symbol("SLSMainConnectionID")

    private static let copyManagedDisplaySpaces: (@convention(c) (ConnectionID) -> Unmanaged<CFArray>?)? =
        symbol("CGSCopyManagedDisplaySpaces")

    private static let managedDisplayGetCurrentSpace: (@convention(c) (ConnectionID, CFString) -> SpaceID)? =
        symbol("SLSManagedDisplayGetCurrentSpace")

    private static let managedDisplaySetCurrentSpace: (@convention(c) (ConnectionID, CFString, SpaceID) -> Int32)? =
        symbol("SLSManagedDisplaySetCurrentSpace")

    private static let showSpaces: (@convention(c) (ConnectionID, CFArray) -> Void)? =
        symbol("SLSShowSpaces")

    private static let hideSpaces: (@convention(c) (ConnectionID, CFArray) -> Void)? =
        symbol("SLSHideSpaces")

    private static let getActiveSpace: (@convention(c) (ConnectionID) -> SpaceID)? =
        symbol("SLSGetActiveSpace")

    static var isAvailable: Bool {
        handle != nil
            && mainConnectionID != nil
            && copyManagedDisplaySpaces != nil
            && managedDisplaySetCurrentSpace != nil
    }

    struct DisplaySpaces {
        let displayIdentifier: String
        let spaceIDs: [SpaceID]
        let currentSpaceID: SpaceID
    }

    static func mainDisplaySpaces() -> DisplaySpaces? {
        guard let mainConnectionID,
              let copyManagedDisplaySpaces
        else { return nil }

        let cid = mainConnectionID()
        guard let raw = copyManagedDisplaySpaces(cid)?.takeRetainedValue() as? [[String: Any]],
              let display = raw.first,
              let displayIdentifier = display["Display Identifier"] as? String,
              let spaces = display["Spaces"] as? [[String: Any]]
        else { return nil }

        // Mission Control order == Spaces array order (type 0 = user desktop).
        let spaceIDs: [SpaceID] = spaces.compactMap { (space: [String: Any]) -> SpaceID? in
            let type = space["type"] as? Int ?? 0
            guard type == 0 else { return nil }
            return spaceID(from: space)
        }

        let currentFromDict = (display["Current Space"] as? [String: Any]).flatMap(spaceID(from:))
        let current = resolveCurrentSpaceID(
            cid: cid,
            displayIdentifier: displayIdentifier,
            knownIDs: spaceIDs,
            fallback: currentFromDict
        )

        return DisplaySpaces(
            displayIdentifier: displayIdentifier,
            spaceIDs: spaceIDs,
            currentSpaceID: current
        )
    }

    private static func spaceID(from space: [String: Any]) -> SpaceID? {
        if let id64 = space["id64"] as? UInt64 { return id64 }
        if let id64 = space["id64"] as? Int { return SpaceID(id64) }
        if let managed = space["ManagedSpaceID"] as? Int { return SpaceID(managed) }
        if let managed = space["ManagedSpaceID"] as? Int64 { return SpaceID(managed) }
        return nil
    }

    private static func resolveCurrentSpaceID(
        cid: ConnectionID,
        displayIdentifier: String,
        knownIDs: [SpaceID],
        fallback: SpaceID?
    ) -> SpaceID {
        if let getActiveSpace {
            let active = getActiveSpace(cid)
            if knownIDs.contains(active) { return active }
        }
        if let managedDisplayGetCurrentSpace {
            let viaUUID = managedDisplayGetCurrentSpace(cid, displayIdentifier as CFString)
            if knownIDs.contains(viaUUID) { return viaUUID }
            let viaMain = managedDisplayGetCurrentSpace(cid, "Main" as CFString)
            if knownIDs.contains(viaMain) { return viaMain }
        }
        if let fallback, knownIDs.contains(fallback) { return fallback }
        return knownIDs.first ?? 0
    }

    /// 1-based desktop index in Mission Control order.
    static func currentDesktopIndex() -> Int? {
        guard let info = mainDisplaySpaces(),
              info.currentSpaceID != 0,
              let idx = info.spaceIDs.firstIndex(of: info.currentSpaceID)
        else { return nil }
        return idx + 1
    }

    /// Focus 1-based desktop index. Prefer Dock key transition; fall back to SkyLight.
    @discardableResult
    static func focusDesktop(index: Int) -> Bool {
        guard index >= 1,
              let info = mainDisplaySpaces(),
              index <= info.spaceIDs.count,
              let currentIndex = info.spaceIDs.firstIndex(of: info.currentSpaceID).map({ $0 + 1 })
                ?? currentDesktopIndex()
        else { return false }

        if currentIndex == index { return true }

        let targetID = info.spaceIDs[index - 1]
        let currentID = info.spaceIDs[currentIndex - 1]

        // 1) Relative Control+Arrow via Finder — real Mission Control transition.
        if switchByRelativeKeys(from: currentIndex, to: index) {
            Thread.sleep(forTimeInterval: 0.25)
            if currentDesktopIndex() == index { return true }
        }

        // 2) SkyLight direct (show → hide → set), try UUID and "Main".
        if switchBySkyLight(from: currentID, to: targetID, displayIdentifier: info.displayIdentifier)
            || switchBySkyLight(from: currentID, to: targetID, displayIdentifier: "Main") {
            Thread.sleep(forTimeInterval: 0.15)
            return currentDesktopIndex() == index || getActiveSpaceID() == targetID
        }

        return false
    }

    private static func getActiveSpaceID() -> SpaceID? {
        guard let mainConnectionID, let getActiveSpace else { return nil }
        return getActiveSpace(mainConnectionID())
    }

    private static func switchBySkyLight(from: SpaceID, to: SpaceID, displayIdentifier: String) -> Bool {
        guard let mainConnectionID, let managedDisplaySetCurrentSpace else { return false }
        let cid = mainConnectionID()

        // yabai order: show destination, hide source, then set current
        if let showSpaces {
            showSpaces(cid, [NSNumber(value: to)] as CFArray)
        }
        if let hideSpaces {
            hideSpaces(cid, [NSNumber(value: from)] as CFArray)
        }

        let rc = managedDisplaySetCurrentSpace(cid, displayIdentifier as CFString, to)
        return rc == 0
    }

    private static func switchByRelativeKeys(from: Int, to: Int) -> Bool {
        let steps = to - from
        guard steps != 0 else { return true }
        let keyCode = steps > 0 ? 124 : 123 // right / left arrow
        let count = abs(steps)

        let source = """
        tell application "Finder" to activate
        delay 0.08
        tell application "System Events"
            repeat \(count) times
                key code \(keyCode) using {control down}
                delay 0.15
            end repeat
        end tell
        """

        var error: NSDictionary?
        let script = NSAppleScript(source: source)
        _ = script?.executeAndReturnError(&error)
        if let error {
            print("ActiveMenuBar: key switch error \(error)")
            return false
        }
        return true
    }
}
