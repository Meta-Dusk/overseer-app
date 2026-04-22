import flet as ft

from core.test_handler import setup_test
from components.layouts import DefaultContainer, CenteredColumn, DefaultWindowDragArea
from managers.native_dialogs import WinTaskDialog, WinMessageBox, WinMBIcon

@setup_test("Native Dialog Test")
def test(page: ft.Page) -> None:
    controls = [
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
            "Show NativeDialog Example 1",
            on_click=lambda _: page.run_thread(
                WinMessageBox.spawn(
                    title="Security Alert",
                    message="Unauthorized process behavior detected. Monitoring active.",
                    icon=WinMBIcon.WARNING
                )
            )
        ),
        ft.Button(
            "Show NativeDialog Example 1",
            on_click=lambda _: page.run_thread(
                WinMessageBox.show_error(
                    "FATAL EXCEPTION: Page Fault in Nonpaged Area (productivity.sys)"
                )
            )
        ),
    ]
    
    form = DefaultWindowDragArea(
        content=DefaultContainer(
            content=CenteredColumn(
                controls
            ),
        ),
    )
    page.add(form)

if __name__ == "__main__":
    ft.run(test, assets_dir="../assets")