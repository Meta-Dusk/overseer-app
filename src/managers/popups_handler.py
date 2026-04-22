import flet as ft
import random, asyncio, ctypes

from managers.verbose_dialogs import WinPositionedMessageBox
from managers.error_factory import ErrorFactory
from managers.monitor import MonitorManager

# Win32 Constants for Z-Order
HWND_NOTOPMOST = -2
HWND_TOPMOST = -1
HWND_BOTTOM = 1
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_SHOWWINDOW = 0x0040

class HorrorEventsHandler:
    def __init__(self, page: ft.Page, *, app_title: str = "The Overseer"):
        self.page = page
        self.app_title = app_title
        self.user32 = ctypes.windll.user32
    
    async def trigger_z_flicker(self, count: int = 5, speed: float = 0.05) -> None:
        """
        Rapidly sends the window to the back and front.
        """
        hwnd = self.user32.FindWindowW(None, self.app_title)
        if not hwnd: return

        for _ in range(count):
            # Send to the very bottom of the window stack
            self.user32.SetWindowPos(
                hwnd, HWND_BOTTOM, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE
            )
            await asyncio.sleep(speed)

            # Force it back to the absolute top
            self.user32.SetWindowPos(
                hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
            )
            
            await asyncio.sleep(speed)
        
        self.user32.SetWindowPos(
            hwnd, HWND_TOPMOST, 0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
        )
        
        self.page.window.always_on_top = False
        self.page.window.update()

    def spawn_random_mb(self, intensity: int = 1) -> None:
        """Spawns a popup ONLY on the monitor where the app is currently located."""
        left, top, right, bottom = MonitorManager.get_current_monitor_rect(self.app_title)
        title, message, icon = ErrorFactory.get_random(intensity)
        
        # We use the monitor's 'left' and 'top' as the starting point
        # A 400x200 buffer ensures the box isn't clipped off the edge
        x = random.randint(left, max(left, right - 400))
        y = random.randint(top, max(top, bottom - 200))
        
        # Spawn
        pos_box = WinPositionedMessageBox(x=x, y=y)
        task = pos_box.spawn(title=title, message=message, icon=icon)
        self.page.run_thread(task)
    
    async def trigger_spam_event(self, intensity: int = 3) -> None:
        """
        Generates and spawns a random amount of positioned error messages.
        """
        for _ in range(random.randint(5, 10)):
            self.spawn_random_mb(intensity=intensity)
            await asyncio.sleep(0.1)