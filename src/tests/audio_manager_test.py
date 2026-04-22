import flet as ft

from managers.audio import AudioManager
from core.test_handler import setup_test
from core.assets import Assets
from components.layouts import CenteredColumn, DefaultWindowDragArea, DefaultContainer

@setup_test("Audio Test")
def test(page: ft.Page) -> None:
    audio_manager = AudioManager(page, debug=True)
    form = DefaultWindowDragArea(
        content=DefaultContainer(
            content=CenteredColumn(
                controls=[
                    ft.Button(
                        "Play SFX",
                        on_click=lambda _: audio_manager.play_sfx(
                            Assets.audio.sfx.lightning
                        )
                    ),
                    ft.Button("Play Music")
                ]
            ),
        ),
    )
    page.add(form)

if __name__ == "__main__":
    ft.run(test, assets_dir="../assets")