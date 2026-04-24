import flet as ft

from core.setup import setup_page
from app import App
from test_app import test

async def main(page: ft.Page) -> None:
    # app = App(page)
    # setup = await app.setup()
    
    # if not setup:
    #     raise Exception("App.setup() failed.")
    # if not await app.build():
    #     raise Exception("App.build() failed.")
    await test(page)
    
ft.run(main)