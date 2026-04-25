import ctypes

class ScreenMetrics:
    """Retrieves real-time monitor resolution using Win32 API."""
    
    @staticmethod
    def get_resolution():
        """Returns (width, height) of the primary monitor."""
        # SM_CXSCREEN = 0, SM_CYSCREEN = 1
        width = ctypes.windll.user32.GetSystemMetrics(0)
        height = ctypes.windll.user32.GetSystemMetrics(1)
        return width, height