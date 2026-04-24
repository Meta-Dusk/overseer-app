import flet as ft
import random, asyncio

from core.test_handler import setup_test
from core.data_types import UnusedEvent
from components.layouts import DefaultContainer, CenteredColumn, DefaultWindowDragArea
from utilities.dialogs.basic import WinTaskDialog, WinMessageBox, WinMBIcon
from utilities.dialogs.verbose import WinPositionedMessageBox
from utilities.screen_color import ScreenColorManager
from utilities.desktop import DesktopManager
from managers.events import EventsManager

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
    events = EventsManager(page, app_title=APP_TITLE)
    initialized = ScreenColorManager.initialize()
    if not initialized:
        print("Warning: Monitor color effects not supported.")
    
    async def delayed_mouse_magnet(_: UnusedEvent) -> None:
        await asyncio.sleep(1)
        events.pull_mouse_to_app()
    
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
        ft.Button("Trigger Spam Event", on_click=lambda _: page.run_task(events.trigger_spam_event)),
        ft.Button("Spawn Random MessageBox", on_click=lambda _: events.spawn_random_mb()),
        ft.Button("Trigger Z-Flicker", on_click=lambda _: page.run_task(events.trigger_z_flicker)),
        ft.Button("Start Delayed Cursor Magnet", on_click=delayed_mouse_magnet),
        ft.Button("Apply Grayscale", on_click=lambda _: ScreenColorManager.apply_grayscale()),
        ft.Button("Apply Inversion", on_click=lambda _: ScreenColorManager.apply_invert()),
        ft.Button(
            "Trigger File Manifestation",
            on_click=lambda _: page.run_task(events.trigger_file_bomb, auto_open=True)
        )
    ]
    
    form = DefaultWindowDragArea(
        content=DefaultContainer(
            content=CenteredColumn(
                controls=controls, scroll=ft.ScrollMode.ALWAYS
            ),
        ),
    )
    page.add(form)
    
    def on_close(_: UnusedEvent) -> None:
        DesktopManager.purge_created_files()
        if initialized:
            ScreenColorManager.cleanup()
    
    page.on_close = on_close

if __name__ == "__main__":
    ft.run(test, assets_dir="../assets")