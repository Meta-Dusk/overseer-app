import flet as ft
import random, asyncio, ctypes
from datetime import datetime

from utilities.dialogs.verbose import WinPositionedMessageBox
from utilities.message_factory import ErrorMessagesFactory
from utilities.monitor import MonitorManager
from utilities.mouse import WinMouse
from utilities.desktop import DesktopManager

# Win32 Constants for Z-Order
HWND_NOTOPMOST = -2
HWND_TOPMOST = -1
HWND_BOTTOM = 1
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_SHOWWINDOW = 0x0040

class EventsManager:
    def __init__(self, page: ft.Page, *, app_title: str = "The Overseer"):
        self.page = page
        self.app_title = app_title
        self.user32 = ctypes.windll.user32
    
    @property
    def get_timestamp(self) -> str:
        """Returns a formatted timestamp of: '%H%M%S'."""
        return datetime.now().strftime("%H%M%S")
    
    async def trigger_z_flicker(self, count: int = 5, speed: float = 0.05) -> None:
        """Rapidly sends the window to the back and front."""
        hwnd = self.user32.FindWindowW(None, self.app_title)
        if not hwnd: return
        
        def send_to_back() -> None:
            """Send to the very bottom of the window stack."""
            self.user32.SetWindowPos(
                hwnd, HWND_BOTTOM, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE
            )
        
        def send_to_front() -> None:
            """Send to the very top of the window stack."""
            self.user32.SetWindowPos(
                hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW
            )
        
        for _ in range(count):
            send_to_back()
            await asyncio.sleep(speed)
            send_to_front()
            await asyncio.sleep(speed)
        
        send_to_front()
        self.page.window.always_on_top = False
        self.page.window.update()

    def spawn_random_mb(self, intensity: int = 1) -> None:
        """Spawns a popup ONLY on the monitor where the app is currently located."""
        left, top, right, bottom = MonitorManager.get_current_monitor_rect(self.app_title)
        title, message, icon = ErrorMessagesFactory.get_random(intensity)
        
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
    
    def pull_mouse_to_app(self) -> None:
        """Yanks the mouse cursor to the center of the App window."""
        coords = WinMouse.get_window_center(self.app_title)
        if coords is None: return
        WinMouse.set_position(*coords)
    
    async def trigger_file_bomb(self, count: int = 1, auto_open: bool = False) -> None:
        """Manifests and opens multiple read-only files rapidly."""
        messages = [
            "FOCUS IS MANDATORY.",
            "WHY IS YOUTUBE OPEN?",
            "THE OVERSEER IS DISPLEASED.",
            "WHY ARE YOU NOT DOING YOUR ASSESSMENTS?",
            "I CAN SEE YOU."
        ]
        
        for _ in range(count):
            filename = f"{self.get_timestamp}.overseer"
            msg = random.choice(messages)
            DesktopManager.create_desktop_file(filename, msg, auto_open=auto_open)
            await asyncio.sleep(0.2)
    
    async def trigger_text_haunting(self) -> None:
        """A multi-stage event that manipulates a text file."""
        messages = [
            "Why is YouTube still open?",
            "Focus on your assessments.",
            "I'm watching you."
        ]
        msg = random.choice(messages)
        
        def on_finish(success: bool) -> None:
            if not success: return
            self.page.window.minimized = False
            self.page.window.update()
        
        # await self.trigger_z_flicker(count=3)
        self.page.window.minimized = True
        self.page.window.update()
        self.page.run_thread(
            lambda: DesktopManager.create_and_possess(
                f"\n\n{msg}", on_complete=on_finish
            )
        )