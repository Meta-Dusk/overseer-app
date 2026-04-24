import ctypes
from enum import IntEnum

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
    MB_OK = 0x00000000
    
    MB_SYSTEMMODAL = 0x00001000
    """Forces the window to stay on top of everything."""
    
    MB_SETFOREGROUND = 0x00010000
    """Brings the window to the front."""
    
    MB_TOPMOST = 0x00040000
    """Forces it above even other 'Always on Top' windows."""

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
        cls, title: str, message: str, icon: WinMBIcon = WinMBIcon.ERROR,
        buttons: WinMBButtons = WinMBButtons.OK
    ):
        """Returns a callable. Run with `page.run_thread()`."""
        # Combine the icon with Modal and Foreground flags
        style = (
            icon | buttons |
            WinMBStyleFlags.MB_SYSTEMMODAL |
            WinMBStyleFlags.MB_SETFOREGROUND
        )

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

class WinTaskDialog:
    """Handles triggering modern Windows TaskDialogs without blocking the UI."""
    
    @classmethod
    def _task_dialog(
        cls, hwnd: int = 0, hinstance = None, title: str = "",
        main_instruction: str = "", content: str = "",
        buttons: int = 0x0001, icon: WinTaskIcon = WinTaskIcon.SHIELD,
        out_button_id = None
    ):
        return ctypes.windll.comctl32.TaskDialog(
            hwnd, hinstance, title, main_instruction,
            content, buttons, icon, out_button_id
        )
    
    @classmethod
    def spawn(
        cls, instruction: str, content: str,
        title: str = "Windows Security",
        icon: WinTaskIcon = WinTaskIcon.SHIELD
    ):
        """
        Returns a modern TaskDialog Callable. Run with `page.run_thread()`.
        
        Args:
            instruction (str): The large, bold heading text.
            content (str): The smaller body text below.
            title (str): The window title bar text.
            icon (WinTaskIcon): The system icon to display.
        """
        def _task():
            cls._task_dialog(
                main_instruction=instruction,
                content=content, title=title, icon=icon
            )
        
        return _task