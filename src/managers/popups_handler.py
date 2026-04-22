import flet as ft
import random, asyncio

from managers.verbose_dialogs import WinPositionedMessageBox
from managers.error_factory import ErrorFactory
from managers.monitor import MonitorManager

class PopupsHandler:
    def __init__(self, page: ft.Page, *, app_title: str = "The Overseer"):
        self.page = page
        self.app_title = app_title

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