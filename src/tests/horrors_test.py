import flet as ft
import random

from core.test_handler import setup_test
from components.layouts import DefaultContainer, CenteredColumn, DefaultWindowDragArea
from managers.native_dialogs import WinTaskDialog, WinMessageBox, WinMBIcon
from managers.verbose_dialogs import WinPositionedMessageBox
from managers.popups_handler import HorrorEventsHandler

APP_TITLE = "Native Dialog Test"

async def trigger_pos_win_popup(page: ft.Page):
    # Randomly scatter errors across the screen
    random_x = random.randint(100, 1500)
    random_y = random.randint(100, 800)
    
    pos_box = WinPositionedMessageBox(random_x, random_y)
    task = pos_box.spawn(
        title="SYSTEM CORRUPTION",
        message="Memory error at offset 0x04F2. Data loss imminent.",
        icon=WinMBIcon.ERROR
    )
    page.run_thread(task)

@setup_test(APP_TITLE)
def test(page: ft.Page) -> None:
    horrors = HorrorEventsHandler(page, app_title=APP_TITLE)
    
    controls: list[ft.Control] = [
        ft.Button(
            "Show ModernNativeDialog Example",
            on_click=lambda _: page.run_thread(
                WinTaskDialog.spawn(
                    instruction="Instruction",
                    content="Small body text",
                    title="I am the title",
                )
            )
        ),
        ft.Button(
            "Show NativeDialog Example A",
            on_click=lambda _: page.run_thread(
                WinMessageBox.spawn(
                    title="Security Alert",
                    message="Unauthorized process behavior detected. Monitoring active.",
                    icon=WinMBIcon.WARNING
                )
            )
        ),
        ft.Button(
            "Show NativeDialog Example B",
            on_click=lambda _: page.run_thread(
                WinMessageBox.show_error(
                    "FATAL EXCEPTION: Page Fault in Nonpaged Area (productivity.sys)"
                )
            )
        ),
        ft.Button(
            "Show WinPositionedMessageBox Example",
            on_click=lambda _: page.run_task(trigger_pos_win_popup, page)
        ),
        ft.Button(
            "Trigger Spam Event",
            on_click=lambda _: page.run_task(horrors.trigger_spam_event)
        ),
        ft.Button(
            "Spawn Random MessageBox",
            on_click=lambda _: horrors.spawn_random_mb()
        ),
        ft.Button(
            "Trigger Z-Flicker",
            on_click=lambda _: page.run_task(horrors.trigger_z_flicker)
        )
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