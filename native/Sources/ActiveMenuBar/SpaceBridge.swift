import AppKit
import Darwin
import Foundation

/// Read Mission Control Spaces via SkyLight; switch with Control+Arrow.
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

    private static let getActiveSpace: (@convention(c) (ConnectionID) -> SpaceID)? =
        symbol("SLSGetActiveSpace")

    static var isAvailable: Bool {
        handle != nil
            && mainConnectionID != nil
            && copyManagedDisplaySpaces != nil
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

    /// Number of regular desktops on the main display (fullscreen spaces excluded).
    static func desktopCount() -> Int {
        mainDisplaySpaces()?.spaceIDs.count ?? 0
    }

    /// Focus 1-based desktop index with the real Mission Control shortcut.
    /// Never write SkyLight spaces — SLSManagedDisplaySetCurrentSpace /
    /// SLSShowSpaces composites two desktops (stacked File/Edit + mixed windows).
    @discardableResult
    static func focusDesktop(index: Int) -> Bool {
        guard index >= 1,
              let info = mainDisplaySpaces(),
              index <= info.spaceIDs.count
        else { return false }

        let currentIndex = info.spaceIDs.firstIndex(of: info.currentSpaceID).map { $0 + 1 }
            ?? currentDesktopIndex()
        guard let currentIndex else { return false }
        if currentIndex == index { return true }

        return switchByRelativeKeys(from: currentIndex, to: index)
    }

    private static func switchByRelativeKeys(from: Int, to: Int) -> Bool {
        let steps = to - from
        guard steps != 0 else { return true }
        let goingRight = steps > 0
        let count = abs(steps)
        for i in 0..<count {
            if i > 0 { Thread.sleep(forTimeInterval: 0.12) }
            if !runOnMain({ sendSystemEventsArrow(goingRight: goingRight) }) {
                return currentDesktopIndex() == to
            }
        }
        return true
    }

    private static func runOnMain<T>(_ body: () -> T) -> T {
        if Thread.isMainThread { return body() }
        return DispatchQueue.main.sync(execute: body)
    }

    // Compiled once — building NSAppleScript on every click added noticeable lag.
    private static let leftArrowScript = NSAppleScript(source: """
        tell application "System Events"
            key code 123 using {control down}
        end tell
        """)
    private static let rightArrowScript = NSAppleScript(source: """
        tell application "System Events"
            key code 124 using {control down}
        end tell
        """)

    /// Mission Control “Move left/right a space”. Never activate Finder.
    @discardableResult
    private static func sendSystemEventsArrow(goingRight: Bool) -> Bool {
        let script = goingRight ? rightArrowScript : leftArrowScript
        var error: NSDictionary?
        script?.executeAndReturnError(&error)
        if let error {
            print("ActiveMenuBar: key switch error \(error)")
            return false
        }
        return true
    }
}
