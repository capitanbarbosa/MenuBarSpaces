
from AppKit import NSWorkspace

def get_current_space_pyobjc():
    """Gets the current macOS Space (desktop) using PyObjC."""
    try:
        # This method is not officially documented for getting the space index,
        # and its behavior may not be what's expected. It often returns
        # a unique identifier for the space rather than a simple index.
        workspace = NSWorkspace.sharedWorkspace()
        active_space = workspace.activeSpace()
        return active_space
    except Exception as e:
        print(f"Error with PyObjC: {e}")
        return None

if __name__ == "__main__":
    print("Testing PyObjC method...")
    # Note: PyObjC is not installed, so this will fail.
    # To run, first execute: pip install pyobjc
    try:
        current_space = get_current_space_pyobjc()
        if current_space:
            print(f"SUCCESS: Current desktop is {current_space}")
        else:
            print("FAILURE: Could not get current desktop.")
    except ImportError:
        print("SKIPPED: PyObjC is not installed. Please run 'pip install pyobjc' to test.")
    except Exception as e:
        print(f"FAILURE: An unexpected error occurred: {e}")
