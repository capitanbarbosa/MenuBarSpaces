# Albert Setup Guide for macOS

This guide covers the necessary steps to install and run Albert Launcher on a new macOS setup, including troubleshooting common issues on Apple Silicon (M1/M2/M3) Macs.

## 1. Download and Install

1.  Download the latest DMG file from the [official Albert website](https://albertlauncher.github.io/).
2.  Open the DMG file and drag `Albert.app` into your `/Applications` folder.

## 2. Handling the "Not Opened" Security Warning

When you first try to open Albert, you will likely see a security warning from macOS Gatekeeper saying: `"Albert" Not Opened because Apple could not verify it is free of malware.`

This is expected for apps not downloaded from the App Store. To fix this:

1.  Click **Cancel** on the warning dialog.
2.  Open **System Settings** > **Privacy & Security**.
3.  Scroll down to the **Security** section.
4.  You will see a message about "Albert" being blocked. Click the **Open Anyway** button next to it.
5.  Enter your password and confirm you want to open it.

## 3. Fixing the Silent Launch Failure (The `qt` Issue)

On some systems, especially after clicking "Open Anyway," Albert might fail to launch without showing any error. This is usually because of a missing dependency that is not included in the DMG file.

### Symptom:

You try to open Albert, the icon might appear in the Dock for a second and then disappear. Nothing happens.

### The Fix: Install the Qt Dependency via Homebrew

The Albert application depends on the Qt framework, and it often expects to find it in the Homebrew installation path.

1.  **Make sure you have Homebrew installed.** If not, you can get it from [brew.sh](https://brew.sh/).

2.  **Open your Terminal and run the following command:**
    ```bash
    brew install qt
    ```
This command installs the necessary Qt libraries into `/opt/homebrew/`, which is where Albert will look for them.

Once the installation is complete, Albert should launch successfully from your `/Applications` folder. You shouldn't need to do this again. 