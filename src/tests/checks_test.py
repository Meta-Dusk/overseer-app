import flet as ft

from core.test_handler import setup_test
from managers.events import EventsManager

APP_TITLE = "Name Check Test"
@setup_test(APP_TITLE)
def test(page: ft.Page) -> None:
    def on_submit(e: ft.Event[ft.TextField]) -> None:
        if e.data is None: return
        data: str = e.data
        print(f"Entered value: {data}")
        text.value = "Happy Birthday!" if events.is_bday(data) else "Who?"
        text.update()
        
    events = EventsManager(page, app_title=APP_TITLE)
    text = ft.Text("Type your name")
    page.add(
        text, ft.TextField(on_submit=on_submit)
    )

ft.run(test, assets_dir="../assets")