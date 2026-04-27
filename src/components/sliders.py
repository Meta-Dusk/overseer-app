import flet as ft

@ft.control
class SettingsSlider(ft.Slider):
    def label_formatting(self, value: float) -> str:
        """Override for custom label value formatting."""
        return str(value)
    
    def _on_change(self, e: ft.Event[ft.Slider]) -> None:
        if not e.data: return
        data: float = e.data
        formatted_label = self.label_formatting(data)
        e.control.label = formatted_label
        e.control.update()
    
    def init(self):
        self.on_change = self._on_change


if __name__ == "__main__":
    from core.test_handler import setup_test
    
    APP_TITLE = "Settings Test"
    @setup_test(APP_TITLE)
    def test(page: ft.Page) -> None:
        def format_label(value: float) -> str:
            print(f"Raw value: {value}")
            return f"{value*100}%"
        
        slider = SettingsSlider(value=0.5, divisions=10, round=1, min=0, max=1)
        # slider.label_formatting = format_label
        
        page.add(slider)
    
    ft.run(test, assets_dir="../assets")