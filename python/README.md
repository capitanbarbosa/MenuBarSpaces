# Overlay Menu Bar for macOS (Python)

Native macOS **menu bar status items** (right side of the system menu bar) for quick launchers, desktop switching, CPU, notes, and more. Built with PyObjC.

## Features
- Status items in the real macOS menu bar (right side)
- Quick links: wizlabs, GPT, WhatsApp, Gmail
- Desktop / Space switcher (Log, Dev, Biz, Media, Chat, Web)
- Launcher shortcuts, notes, settings, live CPU %
- ≡ menu with Quit
- Hold **Shift** to highlight Space names (requires Accessibility)

## Requirements
- macOS
- Python 3.8+
- Dependencies in `requirements.txt` (PyObjC, pynput, psutil)

## Setup
```sh
cd python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage
```sh
cd python
source venv/bin/activate
python app.py
```

Items appear on the **right** of the menu bar. Leave the process running; quit via ≡ → Quit, or Ctrl+C in the terminal.

### Permissions
Desktop switching and Shift-highlight need **Accessibility** for your terminal (or Cursor). Optional **Input Monitoring** if you extend hotkeys.

## Uninstall
```sh
rm -rf venv
```

## License
MIT
