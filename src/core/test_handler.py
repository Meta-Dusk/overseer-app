import flet as ft
import inspect
from functools import wraps
from typing import Callable

from core.setup import OptionalCallableKeyboardEvent, setup_page
from components.appbar import PresetAppBar
from components.buttons import ExitButton

def setup_test(
    title: str = "Test", *,
    add_test_kb_events: bool = True,
    add_debug_hooks: bool = False
):
    """
    Wrapper that applies the expected configurations for the page during tests. The function must return
    `Callable[[ft.KeyboardEvent], None]` if you're going to attach keyboard events, only if `add_test_kb_events`
    is True; otherwise, you don't need to do this.
    
    Args:
        title (str): The title of the page.
        add_test_kb_events (bool): If True, the page will have a preset `on_keyboard_event` callback attached.
        center_page (bool): Centers page if True.
    
    Examples:
    ```
    # Simple setup example
    @test_page()
    def main(page: ft.Page):
        page.add(ft.Text("Hello"))
        
    ft.run(main)
    ```
    """
    def decorator(page_fn: Callable[[ft.Page], OptionalCallableKeyboardEvent]):
        @wraps(page_fn)
        async def wrapper_fn(page: ft.Page):
            # Page configurations and stuff
            setup_page(page, title, add_debug_hooks=add_debug_hooks)
            page.appbar = PresetAppBar(title="Test", actions=[ExitButton()])
            
            await page.window.center()
            
            # This variable will store whatever page_fn returns (if anything)
            handler = None
            
            async def on_keyboard_event(e: ft.KeyboardEvent) -> None:
                match e.key:
                    case "Escape": await page.window.close()
                    
                # Use the handler captured from the initial execution
                if handler is None: return
                
                if inspect.iscoroutinefunction(handler):
                    await handler(e)
                elif callable(handler):
                    handler(e)
            
            if add_test_kb_events:
                page.on_keyboard_event = on_keyboard_event
            
            if inspect.iscoroutinefunction(page_fn):
                handler = await page_fn(page)
            else:
                handler = page_fn(page)
                
            return handler
        return wrapper_fn
    return decorator