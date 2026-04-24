import flet as ft

from core.assets import Assets
from core.test_handler import setup_test

APP_TITLE = "Jumpscares Test"
@setup_test(APP_TITLE)
def test(page: ft.Page) -> None:
    img = ft.Image(Assets.images.scares.wom1, fit=ft.BoxFit.COVER)
    page.add(ft.Text("Testing..."))
    page.overlay.append(img)
    page.update()

ft.run(test, assets_dir="../assets")