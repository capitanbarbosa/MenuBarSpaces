# Free distribution

Publish an unsigned build. Recipients open it once through macOS, and later
launches work normally. This path does not use the $99 Apple Developer Program.

## Ship it

From this folder:

```sh
make run
```

That installs the app at `/Applications/MenuBarSpaces.app`. Zip that app:

```sh
ditto -c -k --keepParent /Applications/MenuBarSpaces.app MenuBarSpaces.zip
```

Attach `MenuBarSpaces.zip` to a GitHub Release, then point the landing-page
download button at that file:

```sh
NEXT_PUBLIC_DOWNLOAD_URL="https://github.com/capitanbarbosa/MenuBarSpaces/releases/latest/download/MenuBarSpaces.zip"
```

## What each recipient does once

1. Download and unzip the app.
2. Move it to Applications.
3. Right-click it and choose **Open**, then confirm **Open**.
4. If macOS still blocks it, go to **System Settings → Privacy & Security** and click **Open Anyway**.
5. Turn on Accessibility for the app.

Each new version is treated as a different app, so Accessibility has to be turned
on again after an update. A paid Developer ID certificate is what makes that
permission survive updates. See `RELEASING.md` for that path.
