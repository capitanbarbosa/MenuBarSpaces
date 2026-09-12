import AppKit
import Darwin
import Foundation

/// Direct Mission Control / Spaces control via private SkyLight symbols.
/// Avoids keyboard shortcuts (which Cursor/Terminal steal).
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
              let copyManagedDisplaySpaces,
              let managedDisplayGetCurrentSpace
        else { return nil }

        let cid = mainConnectionID()
        guard let raw = copyManagedDisplaySpaces(cid)?.takeRetainedValue() as? [[String: Any]],
              let display = raw.first,
              let displayIdentifier = display["Display Identifier"] as? String,
              let spaces = display["Spaces"] as? [[String: Any]]
        else { return nil }

        // type 0 == user desktop (exclude fullscreen spaces)
        let spaceIDs: [SpaceID] = spaces.compactMap { (space: [String: Any]) -> SpaceID? in
            let type = space["type"] as? Int ?? 0
            guard type == 0 else { return nil }
            if let id64 = space["id64"] as? UInt64 { return id64 }
            if let id64 = space["id64"] as? Int { return SpaceID(id64) }
            if let managed = space["ManagedSpaceID"] as? Int { return SpaceID(managed) }
            if let managed = space["ManagedSpaceID"] as? Int64 { return SpaceID(managed) }
            return nil
        }

        let current = managedDisplayGetCurrentSpace(cid, displayIdentifier as CFString)
        return DisplaySpaces(
            displayIdentifier: displayIdentifier,
            spaceIDs: spaceIDs,
            currentSpaceID: current
        )
    }

    /// 1-based desktop index on the main display.
    static func currentDesktopIndex() -> Int? {
        guard let info = mainDisplaySpaces(),
              let idx = info.spaceIDs.firstIndex(of: info.currentSpaceID)
        else { return nil }
        return idx + 1
    }

    /// Focus 1-based desktop index on the main display.
    @discardableResult
    static func focusDesktop(index: Int) -> Bool {
        guard index >= 1,
              let mainConnectionID,
              let managedDisplaySetCurrentSpace,
              let info = mainDisplaySpaces(),
              index <= info.spaceIDs.count
        else { return false }

        let target = info.spaceIDs[index - 1]
        if target == info.currentSpaceID { return true }

        let cid = mainConnectionID()
        let display = info.displayIdentifier as CFString

        if let hideSpaces {
            hideSpaces(cid, [NSNumber(value: info.currentSpaceID)] as CFArray)
        }
        if let showSpaces {
            showSpaces(cid, [NSNumber(value: target)] as CFArray)
        }

        let rc = managedDisplaySetCurrentSpace(cid, display, target)
        return rc == 0
    }
}
