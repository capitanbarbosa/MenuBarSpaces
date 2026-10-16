# Menu Bar Spaces

Name, see, and switch macOS Desktops from the menu bar.

## Download

[MenuBarSpaces.zip](https://github.com/capitanbarbosa/MenuBarSpaces/releases/latest/download/MenuBarSpaces.zip) from the latest GitHub Release.

## First launch

The zip is unsigned. After you download it, macOS Gatekeeper shows
**“MenuBarSpaces” Not Opened** — Apple could not verify it is free of malware —
with only **Move to Trash** and **Done**. That is expected. Do not trash the app.

1. Unzip `MenuBarSpaces.zip` and move `MenuBarSpaces.app` to Applications.
2. Double-click it. When that dialog appears, click **Done**.
3. Open **System Settings → Privacy & Security** and scroll to the bottom.
4. Click **Open Anyway** next to MenuBarSpaces, then confirm **Open**.
5. If **Open Anyway** is missing, Control-click the app in Finder and choose
   **Open**, then **Open** again.
6. Turn on Accessibility for the app if you want the keyboard fallback.

Later launches from Applications open normally. Each new downloaded version
needs this once.

## Run from source

```sh
cd native
make run
```

That installs `/Applications/MenuBarSpaces.app` and opens it. Local rebuilds
use a development certificate, so they do not hit the download warning.

See `native/releasing2.md` to publish a new zip, and `native/RELEASING.md` for
Developer ID notarization (the path that removes the first-open dialog).
