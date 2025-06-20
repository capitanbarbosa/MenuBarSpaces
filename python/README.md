# Overlay Menu Bar for macOS (Python)

A custom, always-on-top overlay menu bar for macOS, written in Python using PyObjC. Includes a hamburger menu, panel, and global hotkey support.

## Features
- Custom overlay menu bar at the top of the screen
- Hamburger toggle button with styled panel
- Global hotkey (F9 by default) to show/hide the overlay
- Modern, accessible color scheme

## Requirements
- macOS
- Python 3.8+
- [PyObjC](https://pypi.org/project/pyobjc/)
- [pynput](https://pypi.org/project/pynput/) (for global hotkey)

## Setup
1. **Clone or download this repository.**
2. **Open a terminal in the `python` directory.**
3. **Create and activate a virtual environment (recommended):**
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```
4. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   pip install pynput
   ```

## Usage
1. **Run the overlay menu bar:**
   ```sh
   python overlay_menu_bar.py
   ```
2. **Toggle the overlay:**
   - Press the hamburger button, or
   - Press `F9` (or `fn+F9` on MacBooks, unless you change keyboard settings)

## Notes
- If the F9 hotkey does not work, ensure `pynput` is installed and your app has accessibility permissions (System Settings → Privacy & Security → Accessibility).
- To use F9 without holding `fn`, enable "Use F1, F2, etc. keys as standard function keys" in System Settings → Keyboard.
- For advanced key remapping, use a tool like Karabiner-Elements.

## Uninstall
To remove the virtual environment and dependencies:
```sh
rm -rf .venv
```

## License
MIT
