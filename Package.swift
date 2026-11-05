// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "MenuBarSpaces",
    platforms: [.macOS(.v13)],
    targets: [
        .executableTarget(
            name: "MenuBarSpaces",
            path: "Sources/ActiveMenuBar"
        )
    ]
)
