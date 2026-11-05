# Free distribution

Publish an unsigned build. Recipients open it once through macOS, and later
launches work normally. This path does not use the $99 Apple Developer Program.

## Ship it

From the repo root:

```sh
make run
```

That installs the app at `/Applications/MenuBarSpaces.app`. Zip that app:

```sh
ditto -c -k --keepParent /Applications/MenuBarSpaces.app MenuBarSpaces.zip
```

## Publish the zip on GitHub

The README download link points at the latest GitHub Release asset named
`MenuBarSpaces.zip`. Keep that filename.

Install the GitHub CLI once if `gh` is missing:

```sh
brew install gh
gh auth login
```

From this folder, create the release and attach the zip:

```sh
gh release create v0.1.0 MenuBarSpaces.zip \
  --repo capitanbarbosa/MenuBarSpaces \
  --title "MenuBarSpaces 0.1.0" \
  --notes "Unsigned macOS build. Right-click the app and choose Open the first time."
```

Or in the browser:

1. Open https://github.com/capitanbarbosa/MenuBarSpaces/releases/new
2. Tag `v0.1.0` (or the next version). Set the title to match.
3. Upload `MenuBarSpaces.zip` in the assets box. The name must stay exactly
   `MenuBarSpaces.zip`.
4. Publish the release.

Confirm the file is reachable:

```text
https://github.com/capitanbarbosa/MenuBarSpaces/releases/latest/download/MenuBarSpaces.zip
```

That is the URL the Next.js page uses. Later versions: bump the tag
(`v0.1.1`, `v0.2.0`), attach a new `MenuBarSpaces.zip`, and publish. `/latest/`
keeps serving whichever release GitHub marks as latest.

## What each recipient does once

The first launch after a download shows **"MenuBarSpaces" Not Opened** —
Apple could not verify it is free of malware — with only **Move to Trash**
and **Done**. That is Gatekeeper blocking an unsigned app. Do not trash it.

1. Download and unzip the app.
2. Move `MenuBarSpaces.app` to Applications.
3. Double-click it. When that dialog appears, click **Done**.
4. Open **System Settings → Privacy & Security**. Scroll to the bottom.
5. Next to the MenuBarSpaces blocked message, click **Open Anyway**, then
   confirm **Open**.
6. If **Open Anyway** is missing, Control-click the app in Finder and choose
   **Open**, then **Open** again.
7. Turn on Accessibility for the app if you want the keyboard fallback.

Later launches from Applications open normally. Each new downloaded version
is treated as a different app, so these steps (and Accessibility) have to be
done again after an update.

A paid Developer ID certificate plus notarization is what removes this
dialog. See `RELEASING.md` for that path. This free zip cannot skip it.
