import flet as ft
import asyncio

from managers.loader import load_app_lists, reset_config, app_log, LogType
from managers.window import WindowHelperManager
from core.utilities import safe_sleep, format_time
from core.data_types import WindowInfo, AppType, UnusedEvent
from components.layouts import PresetColumn, PresetWindowDragArea, DefaultContainer
from components.appbar import PresetAppBar
from components.buttons import ExitButton, MinimizeButton, PresetPopupMenuButton, \
    SimplePopupMenuItem, FullscreenButton, ThemeToggleButton
from components.text import DefaultText
from components.loading_screen import LoadingIndicator, LoadingScreen
from components.notifications import SimpleNotification, ErrorNotification
from managers.error_checking import check_app_integrity
from managers.smart_classifier import SmartClassifier

class App:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        
        # Configurations
        self.title = "The Overseer"
        self.loading_interval: float = 0.5
        
        # States
        self.window_names = None
        self.stop_event = asyncio.Event()
        self.distraction_time: int = 0
        self.productive_time: int = 0
        self.app_exiting: bool = False
        
        # Managers
        self.classifier = None
        self.window_manager = None
        
        app_log("App class instantiated.")
    
    # | App Main Methods |
    async def setup(self) -> bool:
        try:
            # Loading Controls
            loading_text = DefaultText("Setting Up App...")
            progress_ring = LoadingIndicator()
            loading_controls = LoadingScreen(loading_text=loading_text, loading_indicator=progress_ring)
            
            self.page.add(loading_controls)
            self.page.appbar = PresetAppBar(title=self.title, actions=[ExitButton()])
            self.page.update()
            await self.page.window.center()
            
            app_log("Initiating setup...")
            self.window_names = load_app_lists()
            self.classifier = SmartClassifier(self.window_names)
            self.window_manager = WindowHelperManager()
            
            app_log("Checking app integrity...")
            await check_app_integrity(
                self.page, loading_text, self.window_manager,
                progress_ring, self.loading_interval
            )
            
        except Exception as e:
            app_log(f"[App] There was an error running 'setup()': {str(e)}", LogType.WARNING)
            return False
        app_log(f"[App] Finished App.setup()")
        return True
    
    async def build(self) -> bool:
        try:
            # | Controls |
            self.popup_menu_item_fid = SimplePopupMenuItem(
                text="Fullscreen if Distracted", color=ft.Colors.TERTIARY,
                icon=ft.Icons.FULLSCREEN, checked=False
            )
            self.popup_menu_item_csid = SimplePopupMenuItem(
                text="Center Screen if Distracted", color=ft.Colors.TERTIARY,
                icon=ft.Icons.CENTER_FOCUS_STRONG, checked=True
            )
            self.popup_menu_item_btfid = SimplePopupMenuItem(
                text="Bring to Front if Distracted", color=ft.Colors.TERTIARY,
                icon=ft.Icons.FLIP_TO_FRONT, checked=True
            )
            popup_menu_btn = PresetPopupMenuButton(
                new_menu_items=[
                    SimplePopupMenuItem(
                        text="Reset Config Contents", icon=ft.Icons.FILE_OPEN_OUTLINED,
                        on_click=self.reset_config_btn_call,
                    ),
                    self.popup_menu_item_fid,
                    self.popup_menu_item_csid,
                    self.popup_menu_item_btfid
                ]
            )
            appbar = PresetAppBar(
                title = self.title,
                actions=[
                    ThemeToggleButton(), popup_menu_btn,
                    ft.Container(padding=8),
                    MinimizeButton(), FullscreenButton(), ExitButton(on_click=self.on_close)
                ]
            )
            
            self.current_app_col = ft.Column(
                controls=[
                    ft.Text(
                        "Detecting active window...", size=16,
                        weight=ft.FontWeight.BOLD, data="editable_text"
                    )
                ],
                scroll=ft.ScrollMode.ALWAYS, expand=True
            )
            self.category_text = ft.Text("Unknown", size=24, weight=ft.FontWeight.BOLD)
            self.distractions_counter_text = ft.Text(
                spans=[
                    ft.TextSpan("You Were Distracted for: "),
                    ft.TextSpan(format_time(self.distraction_time))
                ],
                size=16, color=ft.Colors.ERROR
            )
            self.productive_counter_text = ft.Text(
                spans=[
                    ft.TextSpan("You Were Productive for: "),
                    ft.TextSpan(format_time(self.productive_time))
                ],
                size=16, color=ft.Colors.PRIMARY
            )
            
            # | Layouts |
            form_controls = [
                self.distractions_counter_text,
                self.productive_counter_text,
                ft.Divider(height=16),
                ft.Text("Current Window:", size=16),
                self.current_app_col,
                ft.Divider(height=16),
                ft.Text("Status:", size=16),
                self.category_text,
            ]
            self.form = PresetWindowDragArea(
                DefaultContainer(
                    content=PresetColumn(form_controls),
                    padding=16, border_radius=16,
                    bgcolor=ft.Colors.SURFACE_CONTAINER,
                )
            )
            
            # | Page Stuff + Animation |
            self.page.add(self.form)
            self.page.appbar = appbar
            self.page.run_task(self.monitor_focus_async)
            self.page.on_close = self.on_close
            self.page.window.on_event = self.on_event
            await asyncio.sleep(0.1)
            self.form.opacity = 1
            self.form.offset = ft.Offset(0, 0)
            self.page.update()
            
        except Exception as e:
            app_log(f"[App] Error attempting App.build(): {str(e)}", LogType.WARNING)
            return False
        app_log(f"[App] Finished App.build()")
        return True
    
    # | Event Handlers |
    async def on_close(self, _: UnusedEvent) -> None:
        """Handles window closing + animations."""
        if self.app_exiting:
            app_log("[App] App closed.")
            return
        self.app_exiting = True
        
        app_log("[App] App is closing... Waiting for monitor to stop.")
        self.page.show_dialog(SimpleNotification("Exiting the application..."))
        
        if not self.stop_event.is_set(): self.stop_event.set()
        if self.window_manager:
            self.window_manager.stop()
        else:
            app_log("[App] Missing window_manager!", LogType.WARNING)
            
        self.form.opacity = 0
        self.form.offset = ft.Offset(0, -1)
        self.form.update()
        await asyncio.sleep(1)
        self.page.window.prevent_close = False
        self.page.window.update()
        await self.page.window.close()
    
    async def on_event(self, e: ft.WindowEvent):
        match e.type:
            case ft.WindowEventType.CLOSE: await self.on_close(e)
            case _: pass
    
    def reset_config_btn_call(self, _):
        """Resets the config to its default values once called."""
        if reset_config():
            notif = SimpleNotification("Successful reset of config file.", duration=1500)
        else:
            notif = ErrorNotification("Failed to reset config file!", duration=1500)
        self.page.show_dialog(notif)
    
    
    # | Events |
    async def match_app_type(self, app_type: AppType):
        """Event handler for detected window type from monitor task."""
        match app_type:
            case AppType.PRODUCTIVE:
                self.productive_time += 1
                if self.productive_counter_text.spans and len(self.productive_counter_text.spans) > 0:
                    self.productive_counter_text.spans[1].text = format_time(self.productive_time)
                    self.productive_counter_text.update()
                app_log(f"Incremented productive_time to: {format_time(self.productive_time)}")
                await safe_sleep(1, self.stop_event)
            
            case AppType.DISTRACTING:
                if self.popup_menu_item_csid.checked:
                    await self.page.window.center()
                if not self.page.window.always_on_top and self.popup_menu_item_btfid.checked:
                    self.page.window.always_on_top = True
                    self.page.window.update()
                if not self.page.window.maximized and self.popup_menu_item_fid.checked:
                    self.page.window.maximized = True
                    self.page.window.update()
                self.distraction_time += 1
                if self.distractions_counter_text.spans and len(self.distractions_counter_text.spans) > 0:
                    self.distractions_counter_text.spans[1].text = format_time(self.distraction_time)
                    self.distractions_counter_text.update()
                app_log(f"Incremented distraction_time to: {format_time(self.distraction_time)}")
                await safe_sleep(1, self.stop_event)
                
            case AppType.NEUTRAL | _:
                if self.page.window.always_on_top:
                    self.page.window.always_on_top = False
                    self.page.window.update()
                await safe_sleep(0.5, self.stop_event)
    
    async def monitor_focus_async(self):
        """This is the main looping function for window detection and classification."""
        prev_title = ""
        while not self.stop_event.is_set():
            # Run blocking call in a background thread with COM initialized
            if self.window_manager:
                info = await asyncio.to_thread(self.window_manager.get_latest_window_info)
            else:
                app_log("[App] Missing window_manager!", LogType.WARNING)
                break
            
            if self.classifier:
                category = self.classifier.classify(info)
            else:
                app_log("[App] Missing classifier!", LogType.WARNING)
                break
                
            title = info.get(WindowInfo.NAME) or "Unknown Window"
            if title != prev_title:
                prev_title = title
                for ctrl in self.current_app_col.controls:
                    if isinstance(ctrl, ft.Text) and ctrl.data == "editable_text":
                        current_app_text: ft.Text = ctrl
                        current_app_text.value = str(title)
                self.category_text.value = category.value.title()
                self.category_text.color = (
                    ft.Colors.PRIMARY if category == AppType.PRODUCTIVE
                    else ft.Colors.ERROR if category == AppType.DISTRACTING
                    else ft.Colors.SECONDARY
                )
                self.page.update(self.category_text, self.current_app_col)
            await self.match_app_type(category)
        app_log("Monitor task stopped.")