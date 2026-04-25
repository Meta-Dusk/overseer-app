import flet as ft
import random, asyncio, ctypes, os
from datetime import datetime
from typing import Optional

from core.constants import THE_WATCHER
from utilities.dialogs.verbose import WinPositionedMessageBox
from utilities.message_factory import ErrorMessagesFactory
from utilities.monitor import MonitorManager
from utilities.mouse import WinMouse
from utilities.desktop import DesktopManager
from utilities.window_effects import WindowEffectsManager
from utilities.ghost_writer import GhostWriter

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
    
    @property
    def get_def_file_name(self) -> str:
        """Returns a default file name for text files."""
        return f"{self.get_timestamp}.overseer"
    
    def is_bday(self, user_name: str) -> bool:
        now = datetime.now()
        if now.month != 4 or now.day != 26:
            print("Not yet bday")
            return False
        possible_names = {"rigel", "sam", "lumampao", "anarky", "mercenary", "anarkydmercenary"}
        if any(name.lower() in user_name.lower() for name in possible_names):
            return True
        print("Invalid name")
        return False
    
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
            
        self.page.window.always_on_top = True
        self.page.window.update()
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
        pos_box = WinPositionedMessageBox(x, y)
        task = pos_box.spawn(title=title, message=message, icon=icon)
        self.page.run_thread(task)
    
    async def trigger_spam_event(self, intensity: int = 3) -> None:
        """
        Generates and spawns a random amount of positioned error messages.
        """
        for _ in range(random.randint(5, 10)):
            self.spawn_random_mb(intensity=intensity)
            await asyncio.sleep(0.1)
    
    def pull_mouse_to_app(self, app_title: Optional[str] = None) -> bool:
        """Yanks the mouse cursor to the center of the App window."""
        coords = WinMouse.get_window_center(app_title if app_title else self.app_title)
        if coords is None: return False
        WinMouse.set_position(*coords)
        return True
    
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
            msg = random.choice(messages)
            DesktopManager.create_desktop_file(
                self.get_def_file_name, msg, auto_open=auto_open
            )
            if count > 1: await asyncio.sleep(0.2)
    
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
    
    async def trigger_ghostly_message(self) -> None:
        self.page.window.minimized = True
        self.page.window.update()
        await asyncio.sleep(1.0)
        
        os.startfile("notepad.exe")
        await asyncio.sleep(1.0)
        
        WindowEffectsManager.set_transparency("Untitled - Notepad", alpha=120)
        await asyncio.sleep(0.5)
        
        def on_finish(_: bool) -> None:
            self.page.window.minimized = False
            self.page.window.update()
          
        self.page.run_thread(lambda: GhostWriter.possess_blank_notepad(
            "I'm not even really here. I'm just a fragment of his code.",
            on_finish=on_finish
        ))
    
    def create_ascii_art(self) -> None:
        DesktopManager.create_desktop_file(
            self.get_def_file_name, THE_WATCHER, auto_open=True
        )
    
    def spawn_message_at_mouse(self, intensity: int = 1) -> None:
        title, message, icon = ErrorMessagesFactory.get_random(intensity)
        mx, my = WinMouse.get_position()
        pos_box = WinPositionedMessageBox(mx, my)
        task = pos_box.spawn(title=title, message=message, icon=icon)
        self.page.run_thread(task)