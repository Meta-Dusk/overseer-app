import ctypes
from enum import IntEnum
from typing import Optional

class WinMBButtons(IntEnum):
    """Button layout constants for MessageBoxW."""
    OK = 0x00000000
    OKCANCEL = 0x00000001
    ABORTRETRYIGNORE = 0x00000002
    YESNOCANCEL = 0x00000003
    YESNO = 0x00000004
    RETRYCANCEL = 0x00000005

class WinMBResponse(IntEnum):
    """Return values from MessageBoxW."""
    OK = 1
    CANCEL = 2
    ABORT = 3
    RETRY = 4
    IGNORE = 5
    YES = 6
    NO = 7
    TRYAGAIN = 10
    CONTINUE = 11

class WinMBIcon(IntEnum):
    """Windows MessageBox Icon constants."""
    
    ERROR = 0x10
    """Red 'X' circle."""
    
    QUESTION = 0x20
    """Blue '?' circle."""
    
    WARNING = 0x30
    """Yellow '!' triangle."""
    
    INFO = 0x40
    """Blue 'i' circle."""

class WinMBStyleFlags(IntEnum):
    SYSTEMMODAL = 0x00001000
    """Forces the window to stay on top of everything."""
    
    SETFOREGROUND = 0x00010000
    """Brings the window to the front."""
    
    TOPMOST = 0x00040000
    """Forces it above even other 'Always on Top' windows."""
    
    RIGHT = 0x00080000
    """Right-aligns all text."""
    
    RTLREADING = 0x00100000
    """Displays the text using right-to-left reading order."""
    
    DEFBUTTON2 = 0x00000100
    """Makes the second button the default."""
    
    HELP = 0x00004000
    """Adds a 'help' button."""
    
    SERVICE_NOTIFICATION = 0x00200000
    """Displays the message box on the active desktop even if no user is logged in."""

class WinMessageBox:
    """Handles triggering authentic Windows system dialogs without blocking the UI."""

    @classmethod
    def show_error(cls, message: str, *, title: str = "System Error"):
        """Quick shortcut for a critical system error. Run with `page.run_thread()`."""
        return cls.spawn(title, message, WinMBIcon.ERROR)

    @classmethod
    def show_warning(cls, message: str, *, title: str = "System Warning"):
        """Quick shortcut for a system warning. Run with `page.run_thread()`."""
        return cls.spawn(title, message, WinMBIcon.WARNING)

    @classmethod
    def spawn(
        cls, title: str, message: str,
        icon: WinMBIcon = WinMBIcon.ERROR,
        buttons: WinMBButtons = WinMBButtons.OK,
        *,
        style_flags: Optional[list[WinMBStyleFlags]] = None
    ):
        """Returns a callable. Run with `page.run_thread()`."""
        # Combine the icon with Modal and Foreground flags
        style = (icon | buttons)
        
        if style_flags is None:
            style_flags = [
                WinMBStyleFlags.SYSTEMMODAL,
                WinMBStyleFlags.SETFOREGROUND
            ]
        
        for flag in style_flags:
            style |= flag

        def _task():
            # 0 is for the hWnd (0 = Desktop)
            return ctypes.windll.user32.MessageBoxW(0, message, title, style)
        
        return _task


class WinTaskIcon(IntEnum):
    """Modern TaskDialog Icon Resource IDs."""
    
    WARNING = 65535
    """Yellow '!' (TD_WARNING_ICON)"""
    
    ERROR = 65534
    """Red 'X' (TD_ERROR_ICON)"""
    
    INFO = 65533
    """Blue 'i' (TD_INFORMATION_ICON)"""
    
    SHIELD = 65532
    """🛡️ UAC Shield (TD_SHIELD_ICON)"""

class WinTaskButtons(IntEnum):
    """Common button flags for TaskDialog (TDCBF)."""
    OK = 0x0001
    YES = 0x0002
    NO = 0x0004
    CANCEL = 0x0008
    RETRY = 0x0010
    CLOSE = 0x0020

class WinTaskDialog:
    """
    Modern TaskDialog with branching support.\n
    NOTE: This doesn't work in packaged builds.
    """

    @classmethod
    def spawn(
        cls, instruction: Optional[str] = None,
        content: Optional[str] = None,
        title: str = "Windows Security",
        icon: WinTaskIcon = WinTaskIcon.SHIELD,
        buttons: WinTaskButtons = WinTaskButtons.OK
    ):
        """Returns a callable that returns a WinMBResponse ID."""
        def _task():
            # We need a pointer to catch the button result
            clicked_button = ctypes.c_int()
            
            # HRESULT (0 = S_OK)
            result = ctypes.windll.comctl32.TaskDialog(
                0, None, title, instruction, content, 
                int(buttons), int(icon), ctypes.byref(clicked_button)
            )
            
            # Return the button ID (e.g., 6 for YES, 7 for NO)
            return clicked_button.value if result == 0 else 0
        
        return _task