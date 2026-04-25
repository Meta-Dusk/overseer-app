import ctypes
import ctypes.wintypes as wintypes

from utilities.dialogs.basic import WinMBIcon, WinMBStyleFlags

# --- Win32 API Setup ---
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# --- Missing 64-bit Type Definitions ---
# On 64-bit Windows, these must be 64-bit integers to prevent OverflowErrors
LRESULT = ctypes.c_int64
WPARAM = ctypes.c_uint64
LPARAM = ctypes.c_int64

# Constants for Hooking
WH_CBT = 5
HCBT_CREATEWND = 3
HCBT_ACTIVATE = 5
SWP_NOSIZE = 0x0001
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010

# Define the correct types for CallNextHookEx
# Using our custom 64-bit types here is the key to stability
user32.CallNextHookEx.argtypes = [
    wintypes.HHOOK, 
    ctypes.c_int, 
    WPARAM, 
    LPARAM
]
user32.CallNextHookEx.restype = LRESULT

# Define types for SetWindowsHookExW
user32.SetWindowsHookExW.argtypes = [
    ctypes.c_int, 
    ctypes.c_void_p, 
    wintypes.HINSTANCE, 
    wintypes.DWORD
]
user32.SetWindowsHookExW.restype = wintypes.HHOOK

# Define types for SetWindowPos
user32.SetWindowPos.argtypes = [
    wintypes.HWND, 
    wintypes.HWND, 
    ctypes.c_int, 
    ctypes.c_int, 
    ctypes.c_int, 
    ctypes.c_int, 
    wintypes.UINT
]
user32.SetWindowPos.restype = wintypes.BOOL

# Update the HOOKPROC definition to use our custom 64-bit types
HOOKPROC = ctypes.WINFUNCTYPE(
    LRESULT, 
    ctypes.c_int, 
    WPARAM, 
    LPARAM
)

class WinPositionedMessageBox:
    """Spawns a MessageBox at specific screen coordinates using Win32 Hooks."""
    
    def __init__(self, x: int, y: int, *, debug: bool = False):
        self.x = x
        self.y = y
        self.debug = debug
        
        self.hook_id = 0
        # Reference kept to prevent garbage collection crashing the callback
        self._callback_ptr = HOOKPROC(self._hook_callback)

    def _hook_callback(self, nCode, wParam, lParam):
        """Intercepts window activation to force the custom position."""
        # HCBT_ACTIVATE (5) is usually more reliable than CREATEWND for MessageBox
        if nCode == HCBT_ACTIVATE:
            hwnd = wParam
            
            # Set the position right as the window becomes active
            success = user32.SetWindowPos(
                hwnd, 0, self.x, self.y, 0, 0, 
                SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE
            )
            
            # Debug print to confirm the hook is firing in your terminal
            if success and self.debug:
                print(f"📌 Hook: Successfully moved window {hwnd} to {self.x}, {self.y}")
            
            # Unhook immediately to save system resources
            if self.hook_id:
                user32.UnhookWindowsHookEx(self.hook_id)
                self.hook_id = 0
                
        return user32.CallNextHookEx(self.hook_id, nCode, wParam, lParam)

    def spawn(self, title: str, message: str, icon: WinMBIcon = WinMBIcon.ERROR):
        """Returns a callable for page.run_thread()."""
        style = int(icon) | WinMBStyleFlags.SYSTEMMODAL | WinMBStyleFlags.SETFOREGROUND

        def _task() -> None:
            # Set the hook on the current thread
            self.hook_id = user32.SetWindowsHookExW(
                WH_CBT, 
                self._callback_ptr, 
                0, 
                kernel32.GetCurrentThreadId()
            )
            
            # Trigger the blocking MessageBox
            user32.MessageBoxW(0, message, title, style)
            
            # Safety unhook
            if not self.hook_id: return
            user32.UnhookWindowsHookEx(self.hook_id)
        
        return _task