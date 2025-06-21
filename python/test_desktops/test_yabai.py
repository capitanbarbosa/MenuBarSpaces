import subprocess
import json

def get_current_space_yabai():
    """Gets the current macOS Space (desktop) using yabai."""
    try:
        # Query the current space using yabai
        result = subprocess.run(
            ["yabai", "-m", "query", "--spaces", "--space"],
            capture_output=True, text=True, check=True, timeout=2
        )
        data = json.loads(result.stdout)
        return data.get("index")
    except FileNotFoundError:
        print("yabai is not installed or not in PATH.")
        return None
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError) as e:
        print(f"Error with yabai: {e}")
        return None

if __name__ == "__main__":
    print("Testing yabai method...")
    current_space = get_current_space_yabai()
    if current_space:
        print(f"SUCCESS: Current desktop is {current_space}")
    else:
        print("FAILURE: Could not get current desktop.")
