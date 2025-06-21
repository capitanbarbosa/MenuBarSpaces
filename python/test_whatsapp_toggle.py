#!/usr/bin/env python3
"""
Test script for WhatsApp Web PWA toggle functionality.
This script can be run independently to test the AppleScript approaches.
"""

import subprocess
import time

def get_whatsapp_status():
    """Get the current status of WhatsApp Web."""
    script = '''
    tell application "System Events"
        try
            set waProc to first process whose name is "WhatsApp Web"
            if waProc exists then
                set visibleWindows to windows of waProc whose visible is true
                set totalWindows to windows of waProc
                return "Running: true, Visible windows: " & (count of visibleWindows) & ", Total windows: " & (count of totalWindows) & ", Frontmost: " & (frontmost of waProc as string)
            else
                return "Running: false"
            end if
        on error errMsg
            return "Error: " & errMsg
        end try
    end tell
    '''
    
    try:
        result = subprocess.run(["osascript", "-e", script], check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Status check failed: {e}"

def test_comprehensive_toggle():
    """Test the comprehensive toggle method."""
    print("=== Testing Comprehensive WhatsApp Toggle ===")
    
    # Check initial status
    print(f"Initial status: {get_whatsapp_status()}")
    
    # Comprehensive toggle script
    script = '''
    tell application "System Events"
        try
            -- Check if WhatsApp Web is running
            set waProc to first process whose name is "WhatsApp Web"
            
            if waProc exists then
                -- App is running, check if minimized
                set visibleWindows to windows of waProc whose visible is true
                
                if (count of visibleWindows) is 0 then
                    -- App is minimized, try multiple restoration methods
                    print "App is minimized, attempting restoration..."
                    
                    -- Method 1: Direct activation
                    tell application "WhatsApp Web" to activate
                    delay 0.5
                    
                    -- Method 2: Check if restoration worked
                    set visibleWindowsAfter to windows of waProc whose visible is true
                    if (count of visibleWindowsAfter) is 0 then
                        -- Still minimized, try dock click
                        print "Still minimized, trying dock click..."
                        try
                            tell application "Dock" to click (first dock item whose name is "WhatsApp Web")
                            delay 0.3
                        on error
                            -- Dock click failed, try alternative approach
                            print "Dock click failed, trying alternative..."
                            set frontmost of waProc to true
                            delay 0.3
                            tell application "WhatsApp Web" to activate
                        end try
                    else
                        print "Restoration successful after direct activation"
                    end if
                    
                    -- Final check and frontmost setting
                    set frontmost of waProc to true
                    
                else
                    -- App has visible windows, just bring to front
                    print "App has visible windows, bringing to front"
                    set frontmost of waProc to true
                end if
                
            else
                -- App is not running, launch it
                print "App not running, launching..."
                tell application "WhatsApp Web" to activate
            end if
            
            return "Success"
            
        on error errMsg
            -- Fallback: simple activation
            print "Error occurred, trying fallback..."
            try
                tell application "WhatsApp Web" to activate
                return "Fallback success"
            on error fallbackErr
                return "All methods failed: " & errMsg & " | Fallback: " & fallbackErr
            end try
        end try
    end tell
    '''
    
    try:
        print("Running comprehensive toggle script...")
        result = subprocess.run(["osascript", "-e", script], check=True, capture_output=True, text=True)
        print(f"Result: {result.stdout.strip()}")
        
        # Wait a moment and check final status
        time.sleep(1)
        print(f"Final status: {get_whatsapp_status()}")
        
    except Exception as e:
        print(f"Exception: {e}")

def test_simple_toggle():
    """Test simple toggle method."""
    print("\n=== Testing Simple Toggle ===")
    
    script = '''
    tell application "WhatsApp Web"
        activate
    end tell
    '''
    
    try:
        result = subprocess.run(["osascript", "-e", script], check=True, capture_output=True, text=True)
        print("Simple toggle successful")
        time.sleep(1)
        print(f"Status after simple toggle: {get_whatsapp_status()}")
    except Exception as e:
        print(f"Simple toggle failed: {e}")

if __name__ == "__main__":
    print("WhatsApp Web PWA Toggle Test")
    print("=" * 50)
    
    # Test current status
    print(f"Current WhatsApp status: {get_whatsapp_status()}")
    
    # Test comprehensive toggle
    test_comprehensive_toggle()
    
    # Test simple toggle as comparison
    test_simple_toggle()
    
    print("\nTest completed. Check the results above.") 