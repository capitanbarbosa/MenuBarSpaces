# WhatsApp PWA Window Control Limitations on macOS

## Summary
- On macOS, browser-based Progressive Web Apps (PWAs) like WhatsApp Web (installed via Edge/Chrome) do not expose their windows to AppleScript or automation in a way that allows reliable hiding, minimizing, or toggling visibility.
- AppleScript can sometimes list the window, but cannot change its state (minimize, hide, or focus) reliably. Attempts to do so may just move the window between desktops or bring it to the front.
- There is no way to hide a window from Mission Control while keeping it visible on the desktop, or to assign it to all desktops via script.
- The only reliable action is to bring the window to the front, which may cause it to jump desktops, but does not guarantee focus or a true toggle effect.
- These limitations are due to how macOS and browsers manage PWA windows, and are not present with native apps like the official WhatsApp Desktop app.

## Recommendation
- For better automation and scripting, use the official WhatsApp Desktop app for macOS.
- For browser PWAs, scripting options are limited and may not provide the desired user experience.

---

**Ticket created on:** June 20, 2025
**Author:** GitHub Copilot
