import flet as ft

from core.test_handler import setup_test
from components.layouts import DefaultContainer, CenteredColumn, DefaultWindowDragArea
from utilities.window_effects import WindowEffectsManager

APP_TITLE = "Native Dialog Test"

@setup_test(APP_TITLE)
def test(page: ft.Page) -> None:
    screen_effects = WindowEffectsManager(page)
    
    controls: list[ft.Control] = [
        ft.Button(
            "Trigger Screen Shake",
            on_click=lambda _: page.run_task(screen_effects.trigger_screen_shake)
        ),
    ]
    
    form = DefaultWindowDragArea(
        content=DefaultContainer(
            content=CenteredColumn(
                controls=controls
            ),
        ),
    )
    page.add(form)

if __name__ == "__main__":
    ft.run(test, assets_dir="../assets")