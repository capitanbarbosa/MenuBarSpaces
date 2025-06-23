# WhatsApp Web PWA Toggle Fix

## Problem Description
When the WhatsApp Web PWA was minimized in the macOS Dock, clicking the green button in the overlay did not restore or bring the app to the front. The original AppleScript logic only set the process as frontmost, which does not un-minimize a docked app.

## Solution Implemented

### Enhanced Toggle Method
The `toggleWhatsAppComprehensive_` method now handles multiple scenarios:

1. **App Not Running**: Launches WhatsApp Web
2. **App Running with Visible Windows**: Brings to front
3. **App Minimized**: Uses multiple restoration methods:
   - Direct activation with delay
   - Dock icon click as fallback
   - Alternative frontmost setting

### Key Improvements

1. **Status Detection**: Checks if the app has visible windows to determine if it's minimized
2. **Multiple Restoration Methods**: Tries different approaches if the first one fails
3. **Better Error Handling**: Includes fallback mechanisms
4. **Detailed Logging**: Provides debug information to help troubleshoot issues

### Code Changes

1. **Updated Button Action**: WhatsApp button now calls `toggleWhatsAppComprehensive:` instead of `toggleWhatsApp:`
2. **Added Status Check Method**: `getWhatsAppStatus_()` provides debugging information
3. **Comprehensive Toggle Logic**: Handles all edge cases for PWA behavior

## Testing the Fix

### Method 1: Use the Test Script
Run the standalone test script to verify functionality:

```bash
python3 test_whatsapp_toggle.py
```

This script will:
- Check current WhatsApp status
- Test the comprehensive toggle method
- Compare with simple toggle method
- Provide detailed output for debugging

### Method 2: Test in the Main App
1. Launch the overlay menu bar app
2. Minimize WhatsApp Web to the Dock
3. Click the green WhatsApp button
4. Verify that WhatsApp Web is restored and brought to front

### Expected Behavior
- If WhatsApp Web is not running: App launches
- If WhatsApp Web is running but not focused: App comes to front
- If WhatsApp Web is minimized: App is restored from dock and brought to front

## Debugging

If the toggle doesn't work as expected, check the console output for:
- `[WhatsApp Status]` messages showing current app state
- `[WhatsApp Toggle Comprehensive]` messages showing toggle progress
- Any error messages that might indicate permission issues

## Permissions Required

The script requires:
- **Accessibility permissions** for the terminal/IDE running the script
- **Input Monitoring permissions** for global hotkey support

To grant permissions:
1. System Settings > Privacy & Security > Accessibility
2. System Settings > Privacy & Security > Input Monitoring
3. Add your terminal application and ensure toggles are ON

## Alternative Methods

The code includes multiple toggle methods for different scenarios:
- `toggleWhatsApp_`: Original enhanced method
- `toggleWhatsAppAlternative_`: Alternative approach using dock clicks
- `toggleWhatsAppComprehensive_`: Current recommended method

## Troubleshooting

### Common Issues

1. **App doesn't restore**: Check if WhatsApp Web is actually minimized or just hidden
2. **Permission errors**: Ensure Accessibility and Input Monitoring permissions are granted
3. **Script errors**: Check console output for specific AppleScript error messages

### Manual Testing

You can manually test the AppleScript commands in Terminal:

```bash
# Check WhatsApp status
osascript -e 'tell application "System Events" to get name of every process whose name contains "WhatsApp"'

# Simple activation
osascript -e 'tell application "WhatsApp Web" to activate'
```

## Files Modified

- `overlay_menu_bar.py`: Main application with enhanced toggle logic
- `test_whatsapp_toggle.py`: Standalone test script
- `WHATSAPP_PWA_FIX.md`: This documentation file 