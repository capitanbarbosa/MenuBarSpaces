# obervations

- no way of natively hiding apps from mission control. blocked. 

If you want to automate “Assign to All Desktops,” that is not scriptable either—it must be done manually.

... what no way

GitHub Copilot
Yes, unfortunately, on macOS, the “Assign to All Desktops” (or “This Desktop”/“None”) feature is not exposed to AppleScript, Automator, or any public scripting/API interface. It is a system-level feature managed by Mission Control and the Dock, and Apple has not provided any way for third-party tools or scripts to automate this assignment.

Even advanced tools like yabai or Hammerspoon cannot programmatically change a window’s desktop assignment—they can only move windows between desktops by simulating user actions, not by toggling the “Assign to All Desktops” option.

Summary:

“Assign to All Desktops” must be set manually via the window’s right-click menu in the Dock or Mission Control.
There is currently no Apple-supported or reliable third-party way to automate this on macOS.
If Apple ever exposes this feature to automation, it will likely be announced in developer documentation or macOS release notes. For now, manual assignment is the only way.

On macOS, it is not possible to hide a window from Mission Control (the view you get when you slide 4 fingers up) while keeping it visible on your desktop. Mission Control always shows all visible windows, including those assigned to all desktops.


--

alright ive manually shown on all desktops. i need to hide it from mission control when i slide 4 fingers up

There is no AppleScript, automation tool, or third-party utility that can selectively hide a window from Mission Control but keep it visible in your workspace. This is a limitation of macOS’s window management system.

Summary:

If a window is visible on your desktop, it will always appear in Mission Control.
The only way to hide it from Mission Control is to minimize or close it, which also removes it from your desktop.
If you have any other workflow or automation goals, let me know and I’ll help you find the best possible solution!


--

