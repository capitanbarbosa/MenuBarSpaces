# Direct Distribution

# Developer ID distribution

This produces a universal (`arm64` + `x86_64`), Hardened Runtime app inside a
drag-to-Applications DMG. It is for direct distribution, not the Mac App Store.

## One-time Apple setup

1. Join the [Apple Developer Program](https://developer.apple.com/programs/).
2. Install full Xcode, sign into your Apple account, and create a
   **Developer ID Application** certificate:
   **Xcode → Settings → Accounts → Manage Certificates**.
3. Confirm the identity is installed:

   ```sh
   make release-status
   ```

4. Create an app-specific password at
   [appleid.apple.com](https://appleid.apple.com/), then store notarization
   credentials in Keychain:

   ```sh
   xcrun notarytool store-credentials "MenuBarSpaces-notary" \
     --apple-id "YOUR_APPLE_ID" \
     --team-id "YOUR_TEAM_ID" \
     --password "YOUR_APP_SPECIFIC_PASSWORD"
   ```

The password is stored in Keychain and is not written into this repository.

## Build and notarize

If exactly one Developer ID Application certificate is installed:

```sh
cd native
make release NOTARY_PROFILE="MenuBarSpaces-notary"
```

If multiple certificates are installed, specify the full identity:

```sh
make release \
  DEVELOPER_ID_APPLICATION="Developer ID Application: Your Name (TEAMID)" \
  NOTARY_PROFILE="MenuBarSpaces-notary"
```

The finished installer is:

```text
dist/MenuBarSpaces-0.1.0.dmg
```

Users open the DMG and drag `MenuBarSpaces.app` into Applications.

## Separate build/notarize commands

```sh
make release-dmg DEVELOPER_ID_APPLICATION="Developer ID Application: Your Name (TEAMID)"
make notarize NOTARY_PROFILE="MenuBarSpaces-notary"
```

The release script verifies the app signature, submits the DMG to Apple's
notary service, staples the ticket, and validates the final artifact.

## Important

- The local `ActiveMenuBar Local Development` certificate is only for this
  Mac. It is never used for public releases.
- The app uses the private SkyLight framework. Notarization may accept this,
  but Apple does not guarantee private API compatibility across macOS updates.
- This build cannot be submitted to the Mac App Store.
