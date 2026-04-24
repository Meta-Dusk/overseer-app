import pyautogui
import time, ctypes

class GhostWriter:
    """Possesses open windows to type messages."""

    @classmethod
    def possess_notepad(cls, filename: str, message: str) -> None:
        """Finds the specific notepad file and types into it."""
        user32 = ctypes.windll.user32
        time.sleep(0.5) # Give Windows a moment to actually open the file
        
        # Find the window handle by its title (Notepad adds the filename to the title)
        # Usually: "filename - Notepad"
        hwnd = user32.FindWindowW(None, f"{filename} - Notepad")
        if not hwnd: return
        
        # Force the window to the front so it receives the keystrokes
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.1)
        pyautogui.hotkey("end")
        time.sleep(0.1)
        pyautogui.write(message, interval=0.1)