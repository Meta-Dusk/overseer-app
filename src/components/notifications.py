import flet as ft
from typing import Optional

@ft.control
class SimpleNotification(ft.SnackBar):
    duration: ft.DurationValue = 1000
    behavior: Optional[ft.SnackBarBehavior] = ft.SnackBarBehavior.FLOATING

@ft.control
class ErrorNotification(ft.SnackBar):
    duration: ft.DurationValue = 2000
    bgcolor: Optional[ft.ColorValue] = ft.Colors.ERROR_CONTAINER
    
    def init(self):
        if isinstance(self.content, str):
            self.content = ft.Text(self.content, color=ft.Colors.ERROR)
        elif isinstance(self.content, ft.Text):
            self.content.color = ft.Colors.ERROR
