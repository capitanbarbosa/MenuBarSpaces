// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "ActiveMenuBar",
    platforms: [.macOS(.v13)],
    targets: [
        .executableTarget(
            name: "ActiveMenuBar",
            path: "Sources/ActiveMenuBar"
        )
    ]
)
