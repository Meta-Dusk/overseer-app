import ctypes
from ctypes import wintypes

class WinMouse:
    """Utilities for controlling the system cursor."""
    
    @staticmethod
    def set_position(x: int, y: int):
        """Moves the cursor to absolute screen coordinates (x, y)."""
        ctypes.windll.user32.SetCursorPos(x, y)

    @staticmethod
    def get_window_center(window_title: str):
        """Finds the center coordinates of a window by its title."""
        hwnd = ctypes.windll.user32.FindWindowW(None, window_title)
        if not hwnd: return None
            
        rect = wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
        
        center_x = (rect.left + rect.right) // 2
        center_y = (rect.top + rect.bottom) // 2
        return center_x, center_y