
import subprocess

def get_current_space_applescript():
    """Gets the current macOS Space (desktop) using AppleScript."""
    try:
        script = 'tell application "System Events" to get index of current desktop'
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True, text=True, check=True, timeout=2
        )
        return int(result.stdout.strip())
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError) as e:
        print(f"Error with AppleScript: {e}")
        return None

if __name__ == "__main__":
    print("Testing AppleScript method...")
    current_space = get_current_space_applescript()
    if current_space:
        print(f"SUCCESS: Current desktop is {current_space}")
    else:
        print("FAILURE: Could not get current desktop.")
