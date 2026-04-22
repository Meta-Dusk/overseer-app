import flet as ft
import asyncio, random

class ScreenEffectsManager:
    def __init__(self, page: ft.Page):
        self.page = page

    async def trigger_screen_shake(self, duration: float = 0.5, intensity: int = 10):
        """
        Physically jitters the Flet window.
        
        Args:
            duration (float): How long the shake lasts in seconds.
            intensity (int): The maximum pixel offset for the jitter.
        """
        # Store the original position to return to after the chaos
        orig_x = self.page.window.left
        orig_y = self.page.window.top
        
        # Calculate how many frames to shake based on a ~60fps target
        end_time = asyncio.get_event_loop().time() + duration
        
        while asyncio.get_event_loop().time() < end_time:
            # Generate random offsets
            offset_x = random.randint(-intensity, intensity)
            offset_y = random.randint(-intensity, intensity)
            
            # Apply the offset
            if orig_x:
                self.page.window.left = orig_x + offset_x
            if orig_y:
                self.page.window.top = orig_y + offset_y
            if orig_x or orig_y:
                self.page.update()
            
            # Tiny sleep to allow the OS/Flet to catch up
            await asyncio.sleep(0.01)
            
        # Reset to perfectly original coordinates
        self.page.window.left = orig_x
        self.page.window.top = orig_y
        self.page.update()