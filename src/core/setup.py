import flet as ft
from typing import Optional, TypeAlias, Callable

OptionalCallableKeyboardEvent: TypeAlias = Optional[Callable[[ft.KeyboardEvent], None]]

WINDOW_WIDTH: Optional[ft.Number] = 600
WINDOW_HEIGHT: Optional[ft.Number] = 400

def setup_page(page: ft.Page, title: str = "The Overseer", *, add_debug_hooks: bool = True):
    """Use for the `before_main` in `run()`."""
    page.title = title
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.decoration = ft.BoxDecoration(border=ft.Border.all(2, ft.Colors.SURFACE_CONTAINER_HIGHEST))
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(ft.Colors.DEEP_PURPLE_900)
    page.padding = 4
    
    page.window.width = WINDOW_WIDTH
    page.window.height = WINDOW_HEIGHT
    page.window.min_width = WINDOW_WIDTH
    page.window.min_height = WINDOW_HEIGHT
    page.window.title_bar_hidden = True
    page.window.prevent_close = False
    page.window.maximized = False
    
    if add_debug_hooks:
        page.on_close = lambda e: print(e)
        page.on_resize = lambda e: print(e)
        page.window.on_event = lambda e: print(e)
    page.update()
    