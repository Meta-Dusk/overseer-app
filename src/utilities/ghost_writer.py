import pyautogui, time, ctypes
from typing import Optional, Callable

class GhostWriter:
    """Possesses open windows to type messages."""

    @classmethod
    def possess_notepad(
        cls, filename: str, message: str, *,
        hotkeys_on_finish: Optional[list[str]] = None
    ) -> bool:
        """Finds the specific notepad file and types into it."""
        user32 = ctypes.windll.user32
        time.sleep(0.5) # Give Windows a moment to actually open the file
        
        # Find the window handle by its title (Notepad adds the filename to the title)
        # Usually: "filename - Notepad"
        hwnd = user32.FindWindowW(None, f"{filename} - Notepad")
        if not hwnd: return False
        
        # Force the window to the front so it receives the keystrokes
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.1)
        pyautogui.hotkey("end")
        time.sleep(0.1)
        pyautogui.write(message, interval=0.1)
        if hotkeys_on_finish and len(hotkeys_on_finish) > 0:
            time.sleep(0.1)
            pyautogui.hotkey(*hotkeys_on_finish)
        return True
    
    @classmethod
    def possess_blank_notepad(
        cls, message: str, *,
        on_finish: Optional[Callable[[bool], None]] = None
    ) -> bool:
        user32 = ctypes.windll.user32
        time.sleep(0.5)
        
        hwnd = user32.FindWindowW(None, "Untitled - Notepad")
        if not hwnd:
            if on_finish: on_finish(False)
            return False
        
        user32.SetForegroundWindow(hwnd)
        pyautogui.write(message, interval=0.1)
        if on_finish: on_finish(True)
        return True