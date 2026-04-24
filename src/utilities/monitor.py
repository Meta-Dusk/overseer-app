import ctypes
import ctypes.wintypes as wintypes

user32 = ctypes.windll.user32

# --- Win32 Structs for Monitor Info ---
class RECT(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long)
    ]

class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", wintypes.DWORD)
    ]

# Define Win32 Functions
user32.GetMonitorInfoW.argtypes = [wintypes.HMONITOR, ctypes.POINTER(MONITORINFO)]
user32.GetMonitorInfoW.restype = wintypes.BOOL

class MonitorManager:
    """Detects which monitor the app is on and returns its boundaries."""
    
    @staticmethod
    def get_current_monitor_rect(window_title: str):
        """Returns the RECT (left, top, right, bottom) of the monitor holding the app."""
        # Find our Flet Window HWND
        hwnd = user32.FindWindowW(None, window_title)
        if not hwnd:
            # Fallback to Primary Monitor metrics if window isn't found
            w = user32.GetSystemMetrics(0)
            h = user32.GetSystemMetrics(1)
            return (0, 0, w, h)

        # Get the Monitor Handle from the Window Handle
        # MONITOR_DEFAULTTONEAREST = 2
        h_monitor = user32.MonitorFromWindow(hwnd, 2)

        # Get the specific Monitor Info
        info = MONITORINFO()
        info.cbSize = ctypes.sizeof(MONITORINFO)
        if user32.GetMonitorInfoW(h_monitor, ctypes.byref(info)):
            r = info.rcMonitor
            return (r.left, r.top, r.right, r.bottom)
            
        return (0, 0, 1920, 1080) # Emergency fallback