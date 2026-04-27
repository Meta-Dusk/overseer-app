import flet as ft
import flet_audio as fta
import asyncio, random
from typing import Optional, cast

from managers.loader import load_app_lists, reset_config, app_log, LogType
from managers.window import WindowHelperManager
from core.utilities import safe_sleep, format_time_str, try_update
from core.data_types import WindowInfo, AppType, UnusedEvent, EventsConfig
from core.assets import Assets
from core.preferences import Preferences
from components.layouts import PresetColumn, PresetWindowDragArea, DefaultContainer, CenteredColumn
from components.appbar import PresetAppBar
from components.buttons import ExitButton, MinimizeButton, PresetPopupMenuButton, \
    SimplePopupMenuItem, FullscreenButton, ThemeToggleButton
from components.text import DefaultText
from components.loading_screen import LoadingIndicator, LoadingScreen
from components.notifications import SimpleNotification, ErrorNotification
from managers.error_checking import check_app_integrity
from managers.smart_classifier import SmartClassifier
from managers.events import EventsManager
from managers.narrator import NativeNarrator
from managers.audio import AudioManager
from utilities.screen_color import ScreenColorManager
from utilities.desktop import DesktopManager
from utilities.window_effects import WindowEffectsManager

class App:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        
        # Configurations
        self.title = "The Overseer"
        self.loading_interval: float = 0.5
        self.events_config = EventsConfig()
        
        # States
        self.window_names = None
        self.stop_event = asyncio.Event()
        self.distraction_time: int = 0
        self.productive_time: int = 0
        self.idle_time: int = 0
        self.app_exiting: bool = False
        self._intensity: int = 1
        self.playing_music: bool = False
        
        # Managers
        self.classifier = None
        self.window_manager = None
        self.events = None
        self.narrator = None
        self.audio_manager = None
        self.prefs = Preferences()
        self.window_effects = None
        
        app_log("[App] App class instantiated.", LogType.GOOD)
    
    # | Properties |
    @property
    def intensity(self) -> int:
        return self._intensity
    
    @intensity.setter
    def intensity(self, value: int) -> None:
        self._intensity = value
        app_log(f"[App] Setting intensity to: {value}")
    
    # | App Main Methods |
    async def save_configs(self) -> None:
        """Pushes the current in-memory config state to persistent Preferences."""
        await self.prefs.set("idle_freq", self.events_config.idle_frequency)
        await self.prefs.set("idle_chance", self.events_config.idle_chance)
        await self.prefs.set("dist_freq", self.events_config.distracted_frequency)
        await self.prefs.set("dist_chance", self.events_config.distracted_chance)
        await self.prefs.set("prod_freq", self.events_config.productive_frequency)
        await self.prefs.set("idle_events_start", self.events_config.idle_events_start)
        await self.prefs.set("dist_events_start", self.events_config.distracted_events_start)
        
        if self.audio_manager:
            await self.prefs.set("music_volume", self.audio_manager.music_volume)
            await self.prefs.set("sfx_volume", self.audio_manager.sfx_volume)
        app_log("[App] Configs pushed to storage.")
    
    async def reset_configs(self) -> None:
        """Resets both in-memory and persistent settings to hardcoded defaults."""
        self.events_config = EventsConfig() 
        if self.audio_manager:
            self.audio_manager.music_volume = 1.0
            self.audio_manager.sfx_volume = 1.0
            
        await self.save_configs()
        self.page.show_dialog(SimpleNotification("Settings have been reset to default values!"))
    
    async def get_configs(self) -> None:
        idle_freq = await self.prefs.get("idle_freq")
        if idle_freq and isinstance(idle_freq, int): self.events_config.idle_frequency = idle_freq
        else: await self.prefs.set("idle_freq", self.events_config.idle_frequency)
        
        idle_chance = await self.prefs.get("idle_chance")
        if idle_chance and isinstance(idle_chance, float): self.events_config.idle_chance = idle_chance
        else: await self.prefs.set("idle_chance", self.events_config.idle_chance)
        
        dist_freq = await self.prefs.get("dist_freq")
        if dist_freq and isinstance(dist_freq, int): self.events_config.distracted_frequency = dist_freq
        else: await self.prefs.set("dist_freq", self.events_config.distracted_frequency)
        
        dist_chance = await self.prefs.get("dist_chance")
        if dist_chance and isinstance(dist_chance, float): self.events_config.distracted_chance = dist_chance
        else: await self.prefs.set("dist_chance", self.events_config.distracted_chance)
        
        prod_freq = await self.prefs.get("prod_freq")
        if prod_freq and isinstance(prod_freq, int): self.events_config.productive_frequency = prod_freq
        else: await self.prefs.set("prod_freq", self.events_config.productive_frequency)
        
        music_vol = await self.prefs.get("music_volume")
        if music_vol and isinstance(music_vol, float) and self.audio_manager:
            self.audio_manager.music_volume = music_vol
        else: await self.prefs.set("music_volume", 1.0)
        
        sfx_vol = await self.prefs.get("sfx_volume")
        if sfx_vol and isinstance(sfx_vol, float) and self.audio_manager:
            self.audio_manager.sfx_volume = sfx_vol
        else: await self.prefs.set("sfx_volume", 1.0)
        
        idle_events_start = await self.prefs.get("idle_events_start")
        if idle_events_start and isinstance(idle_events_start, int):
            self.events_config.idle_events_start = idle_events_start
        
        dist_events_start = await self.prefs.get("dist_events_start")
        if dist_events_start and isinstance(dist_events_start, int):
            self.events_config.distracted_events_start = dist_events_start
    
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
            
            app_log("[App] Initiating setup...")
            self.window_names = load_app_lists()
            self.classifier = SmartClassifier(self.window_names)
            self.window_manager = WindowHelperManager()
            self.events = EventsManager(self.page, app_title=self.title)
            self.narrator = NativeNarrator(self.page)
            self.audio_manager = AudioManager(self.page, music_volume=1.0, sfx_volume=1.0)
            self.window_effects = WindowEffectsManager(self.page)
            
            app_log("[App] Getting saved preferences...")
            await self.get_configs()
            
            if ScreenColorManager.initialize():
                app_log("[App] ScreenColorManager initialized!", LogType.GOOD)
            else:
                app_log("[App] ScreenColorManager failed to initialize!", LogType.WARNING)
            
            app_log("[App] Checking app integrity...")
            await check_app_integrity(
                self.page, loading_text, self.window_manager,
                progress_ring, self.loading_interval
            )
            
        except Exception as e:
            app_log(f"[App] There was an error running 'setup()': {str(e)}", LogType.WARNING)
            return False
        app_log(f"[App] Finished App.setup()", LogType.GOOD)
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
            popup_menu_btn.items.append(
                SimplePopupMenuItem(
                    text="Show Additional Settings", icon=ft.Icons.SETTINGS,
                    on_click=self.show_settings
                )
            )
            appbar = PresetAppBar(
                title = self.title,
                actions=[
                    ThemeToggleButton(), popup_menu_btn,
                    ft.Container(padding=8),
                    MinimizeButton(), FullscreenButton(on_long_press=self.on_long_press),
                    ExitButton(on_click=self.on_close)
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
                    ft.TextSpan(format_time_str(self.distraction_time))
                ],
                size=16, color=ft.Colors.ERROR
            )
            self.productive_counter_text = ft.Text(
                spans=[
                    ft.TextSpan("You Were Productive for: "),
                    ft.TextSpan(format_time_str(self.productive_time))
                ],
                size=16, color=ft.Colors.PRIMARY
            )
            self.idle_counter_text = ft.Text(
                spans=[
                    ft.TextSpan("You Were Idle for: "),
                    ft.TextSpan(format_time_str(self.idle_time))
                ],
                size=16, color=ft.Colors.SECONDARY
            )
            
            # | Layouts |
            form_controls = [
                self.distractions_counter_text,
                self.productive_counter_text,
                self.idle_counter_text,
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
        app_log(f"[App] Finished App.build()", LogType.GOOD)
        return True
    
    # | Event Handlers |
    async def on_long_press(self, _: UnusedEvent) -> None:
        def on_submit(e: ft.Event[ft.TextField]) -> None:
            if e.data is None: return
            data: str = e.data
            print(f"Entered name: {data}")
            self.show_bday_dialog(data)
            
        dlg = ft.AlertDialog(
            title="Enter a Name",
            content=ft.TextField(
                on_submit=on_submit, hint_text="Enter your name?",
                max_lines=1, max_length=12, autofocus=True
            )
        )
        self.page.show_dialog(dlg)
    
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
        
        DesktopManager.purge_created_files()
        app_log("[App] Attempted to purge all created files.")
        
        if ScreenColorManager.cleanup():
            app_log("[App] ScreenColorManager successful cleanup.", LogType.GOOD)
        else:
            app_log("[App] ScreenColorManager failed to cleanup!", LogType.WARNING)
            
        self.form.opacity = 0
        self.form.offset = ft.Offset(0, -1)
        try_update(self.form)
        await asyncio.sleep(1)
        self.page.window.prevent_close = False
        self.page.window.update()
        await self.page.window.close()
    
    async def on_event(self, e: ft.WindowEvent):
        match e.type:
            case ft.WindowEventType.CLOSE: await self.on_close(e)
            case _: pass
    
    def reset_config_btn_call(self, _: UnusedEvent):
        """Resets the config to its default values once called."""
        if reset_config():
            notif = SimpleNotification("Successful reset of config file.", duration=1500)
        else:
            notif = ErrorNotification("Failed to reset config file!", duration=1500)
        self.page.show_dialog(notif)
    
    
    # | Events |
    async def show_settings(self, _: UnusedEvent) -> None:
        sfx_volume = await self.prefs.get("sfx_volume")
        if sfx_volume is None: sfx_volume = 1.0
        sfx_volume = cast(float, sfx_volume)
        
        music_volume = await self.prefs.get("music_volume")
        if music_volume is None: music_volume = 1.0
        music_volume = cast(float, music_volume)
        
        idle_freq = await self.prefs.get("idle_freq")
        if idle_freq is None: idle_freq = 1
        idle_freq = cast(int, idle_freq)
        
        idle_chance = await self.prefs.get("idle_chance")
        if idle_chance is None: idle_chance = 0.5
        idle_chance = cast(float, idle_chance)
        
        idle_events_start = await self.prefs.get("idle_events_start")
        if idle_events_start is None: idle_events_start = 30
        idle_events_start = cast(int, idle_events_start)
        
        dist_freq = await self.prefs.get("dist_freq")
        if dist_freq is None: dist_freq = 1
        dist_freq = cast(int, dist_freq)
        
        dist_chance = await self.prefs.get("dist_chance")
        if dist_chance is None: dist_chance = 0.5
        dist_chance = cast(float, dist_chance)
        
        dist_events_start = await self.prefs.get("dist_events_start")
        if dist_events_start is None: dist_events_start = 20
        dist_events_start = cast(int, dist_events_start)
        
        prod_freq = await self.prefs.get("prod_freq")
        if prod_freq is None: prod_freq = 1
        prod_freq = cast(int, prod_freq)
        
        async def sfx_on_change(e: ft.Event[ft.Slider]) -> None:
            if not e.data: return
            data: float = e.data
            await self.prefs.set("sfx_volume", round(data, 2))
            e.control.label = f"{int(data*100)}%"
            e.control.update()
        
        async def music_on_change(e: ft.Event[ft.Slider]) -> None:
            if not e.data: return
            data: float = e.data
            await self.prefs.set("music_volume", round(data, 2))
            e.control.label = f"{int(data*100)}%"
            e.control.update()
        
        def idle_freq_on_change(e: ft.Event[ft.Slider]) -> None:
            if not e.data: return
            data: float = e.data
            e.control.label = f"Every {int(data)}s"
            e.control.update()
        
        async def idle_freq_on_change_end(e: ft.Event[ft.Slider]) -> None:
            if not e.data: return
            data: float = e.data
            await self.prefs.set("idle_freq", int(data))
        
        def idle_chance_on_change(e: ft.Event[ft.Slider]) -> None:
            if not e.data: return
            data: float = e.data
            e.control.label = f"{int(data * 100)}%"
            e.control.update()
        
        async def idle_chance_on_change_end(e: ft.Event[ft.Slider]) -> None:
            if not e.data: return
            data: float = e.data
            await self.prefs.set("idle_chance", round(data, 2))
        
        def idle_events_start_on_change(e: ft.Event[ft.Slider]) -> None:
            if not e.data: return
            data: float = e.data
            e.control.label = f"Starts after {int(data)}s"
            e.control.update()
        
        async def idle_events_start_on_change_end(e: ft.Event[ft.Slider]) -> None:
            if not e.data: return
            data: float = e.data
            await self.prefs.set("idle_events_start", int(data))
        
        def dist_freq_on_change(e: ft.Event[ft.Slider]) -> None:
            if not e.data: return
            data: float = e.data
            e.control.label = f"Every {int(data)}s"
            e.control.update()
        
        async def dist_freq_on_change_end(e: ft.Event[ft.Slider]) -> None:
            if not e.data: return
            data: float = e.data
            await self.prefs.set("dist_freq", int(data))
        
        def dist_chance_on_change(e: ft.Event[ft.Slider]) -> None:
            if not e.data: return
            data: float = e.data
            e.control.label = f"{int(data * 100)}%"
            e.control.update()
        
        async def dist_chance_on_change_end(e: ft.Event[ft.Slider]) -> None:
            if not e.data: return
            data: float = e.data
            await self.prefs.set("dist_chance", round(data, 2))
        
        def dist_events_start_on_change(e: ft.Event[ft.Slider]) -> None:
            if not e.data: return
            data: float = e.data
            e.control.label = f"Starts after {int(data)}s"
            e.control.update()
        
        async def dist_events_start_on_change_end(e: ft.Event[ft.Slider]) -> None:
            if not e.data: return
            data: float = e.data
            await self.prefs.set("dist_events_start", int(data))
        
        def prod_freq_on_change(e: ft.Event[ft.Slider]) -> None:
            if not e.data: return
            data: float = e.data
            e.control.label = f"Every {int(data)}s"
            e.control.update()
        
        async def prod_freq_on_change_end(e: ft.Event[ft.Slider]) -> None:
            if not e.data: return
            data: float = e.data
            await self.prefs.set("prod_freq", int(data))
        
        async def on_reset(_: UnusedEvent) -> None:
            self.page.pop_dialog()
            await self.reset_configs()
        
        async def clear_prefs(_: UnusedEvent) -> None:
            self.page.pop_dialog()
            if await self.prefs.clear():
                self.page.show_dialog(SimpleNotification("Cleared all preferences!"))
            else:
                self.page.show_dialog(ErrorNotification("Failed to clear preferences!"))
        
        async def on_confirm(_: UnusedEvent) -> None:
            self.page.pop_dialog()
            # await self.save_configs()
        
        sfx_slider = ft.Slider(
            value=sfx_volume, on_change=sfx_on_change,
            divisions=10, label=f"{sfx_volume}%"
        )
        music_slider = ft.Slider(
            value=music_volume, on_change=music_on_change,
            divisions=10, label=f"{music_volume}%"
        )
    
        idle_freq_slider = ft.Slider(
            value=idle_freq, on_change=idle_freq_on_change,
            on_change_end=idle_freq_on_change_end,
            divisions=59, min=1, max=60, label=f"Every {idle_freq}s"
        )
        idle_chance_slider = ft.Slider(
            value=idle_chance, on_change=idle_chance_on_change,
            on_change_end=idle_chance_on_change_end,
            divisions=100, label=f"{idle_chance}%"
        )
        idle_events_slider = ft.Slider(
            value=idle_events_start, on_change=idle_events_start_on_change,
            on_change_end=idle_events_start_on_change_end,
            divisions=59, min=1, max=60, label=f"Starts after {idle_events_start}s"
        )
    
        dist_freq_slider = ft.Slider(
            value=dist_freq, on_change=dist_freq_on_change,
            on_change_end=dist_freq_on_change_end,
            divisions=61, min=1, max=60, label=f"Every {dist_freq}s"
        )
        dist_chance_slider = ft.Slider(
            value=dist_chance, on_change=dist_chance_on_change,
            on_change_end=dist_chance_on_change_end,
            divisions=100, label=f"{dist_chance}%"
        )
        dist_events_slider = ft.Slider(
            value=dist_events_start, on_change=dist_events_start_on_change,
            on_change_end=dist_events_start_on_change_end,
            divisions=59, min=1, max=60, label=f"Starts after {dist_events_start}s"
        )
    
        prod_freq_slider = ft.Slider(
            value=prod_freq, on_change=prod_freq_on_change,
            on_change_end=prod_freq_on_change_end,
            divisions=61, min=1, max=60, label=f"Every {prod_freq}s",
        )
        
        dlg = ft.AlertDialog(
            title="Events Settings", modal=True,
            content=CenteredColumn(
                controls=[
                    ft.Divider(),
                    ft.Text("SFX Volume"),
                    sfx_slider,
                    ft.Text("Music Volume", margin=ft.Margin.only(top=8)),
                    music_slider,
                    ft.Divider(),
                    ft.Text("Idle Events Frequency", margin=ft.Margin.only(top=8)),
                    idle_freq_slider,
                    ft.Text("Idle Events Chance", margin=ft.Margin.only(top=8)),
                    idle_chance_slider,
                    ft.Text("Idle Events Start", margin=ft.Margin.only(top=8)),
                    idle_events_slider,
                    ft.Divider(),
                    ft.Text("Distraction Events Frequency", margin=ft.Margin.only(top=8)),
                    dist_freq_slider,
                    ft.Text("Distraction Events Start", margin=ft.Margin.only(top=8)),
                    dist_events_slider,
                    ft.Text("Distraction Events Chance", margin=ft.Margin.only(top=8)),
                    dist_chance_slider,
                    ft.Divider(),
                    ft.Text("Productive Events Frequency", margin=ft.Margin.only(top=8)),
                    prod_freq_slider,
                    ft.Divider(),
                ],
                scroll=ft.ScrollMode.ALWAYS
            ),
            actions=[
                ft.Button("Confirm Changes", on_click=on_confirm),
                ft.Button("Reset Values", on_click=on_reset),
                ft.Button("Clear Prefs", on_click=clear_prefs)
            ],
            expand=True
        )
        self.page.show_dialog(dlg)
    
    def show_bday_dialog(self, name: Optional[str]) -> None:
        user_name = name if name else DesktopManager.get_microsoft_display_name()
        print(f"user_name: {user_name}")
        if user_name is None or self.events is None: return
        if not self.events.is_bday(user_name): return
        
        def maximize_window(value: bool) -> None:
            if self.page.window.maximized == value: return
            self.page.window.maximized = value
            self.page.window.update()
        
        def on_click(_: UnusedEvent) -> None:
            self.page.pop_dialog()
            maximize_window(False)
        
        maximize_window(True)
        dlg = ft.AlertDialog(
            title=f"Happy Birthday, {user_name}!",
            content=CenteredColumn(
                controls=[
                    ft.Image(Assets.images.cake, fit=ft.BoxFit.COVER, width=200),
                    ft.Text(
                        "This post was made by MetaDusk", size=12, italic=True,
                        color=ft.Colors.SECONDARY
                    )
                ], tight=True
            ),
            actions=[
                ft.Button("Thanks", icon=ft.Icons.CAKE, on_click=on_click)
            ],
            on_dismiss=lambda _: maximize_window(False)
        )
        self.page.show_dialog(dlg)
    
    async def show_jumpscare(
        self, image_path: Optional[str] = None, *,
        play_sfx: bool = True,
    ) -> None:
        while self.page.pop_dialog() is not None:
            await asyncio.sleep(0.1)
        
        path = image_path if image_path else random.choice([
            Assets.images.blackwall,
            Assets.images.blackwall_2,
            Assets.images.blackwall_3,
            Assets.images.blackwall_4
        ])
        if self.page.appbar: self.page.appbar.visible = False
        self.page.padding = 0
        self.page.decoration = None
        self.page.controls.clear()
        self.page.add(
            ft.Image(
                path, fit=ft.BoxFit.FILL, expand=True, margin=0,
                repeat=ft.ImageRepeat.REPEAT, gapless_playback=True
            )
        )
        self.page.window.maximized = True
        self.page.window.always_on_top = True
        self.page.update()
        
        def on_state_change(e: fta.AudioStateChangeEvent) -> None:
            if e.state == fta.AudioState.COMPLETED:
                if self.page.appbar: self.page.appbar.visible = True
                self.page.padding = 4
                self.page.decoration = ft.BoxDecoration(
                    border=ft.Border.all(2, ft.Colors.SURFACE_CONTAINER_HIGHEST)
                )
                self.page.controls.clear()
                self.page.add(self.form)
                self.page.window.maximized = False
                self.page.window.always_on_top = False
                self.page.update()
                if self.events: self.events.applied_filter = False
                ScreenColorManager.reset()
        
        duration: float = 1
        if play_sfx and self.audio_manager:
            sfx_list: list[str] = [Assets.audio.sfx.jump]
            sfx_list.extend([Assets.audio.sfx.get_scream(i+1) for i in range(8)])
            sfx = self.audio_manager.play_sfx(random.choice(sfx_list))
            if sfx:
                sfx.on_state_change = on_state_change
                sfx_duration = await sfx.get_duration()
                if sfx_duration: duration = round(sfx_duration.in_milliseconds / 1000, 3)
        
        if self.events: await self.events.random_screen_effect_smooth(duration)
        if self.events: await self.events.trigger_z_flicker(random.randint(3, 7))
    
    async def pull_mouse_then_shake(self) -> None:
        if self.events is None: return
        if not self.events.pull_mouse_to_app(self.title): return
        if self.window_effects is None: return
        await self.window_effects.trigger_screen_shake(
            duration=(random.random() + 0.1) * 2,
            intensity=random.randint(10, 50)
        )
    
    async def flicker_flicker(self) -> None:
        """Triggers two kinds of flickers."""
        if self.events is None: return
        self.page.run_task(self.events.random_screen_flicker)
        await self.events.trigger_z_flicker(random.randint(5, 10))
    
    def match_event(self, app_type: AppType) -> None:
        if self.events is None:
            app_log("[App] Missing EventsManager!", LogType.WARNING)
            return
        
        chance = random.random()
        coro_events = [self.show_jumpscare, self.pull_mouse_then_shake, self.flicker_flicker]
        config = self.events_config

        match app_type:
            case AppType.PRODUCTIVE:
                # Check Frequency
                if self.productive_time % config.productive_frequency == 0:
                    if self.events.applied_filter:
                        ScreenColorManager.reset()
                        self.page.show_dialog(SimpleNotification("Lemme fix that for you :)"))
                    
                    if self.audio_manager and self.playing_music:
                        if self.audio_manager.music_instance:
                            self.page.run_task(self.audio_manager.music_instance.pause)
            
            case AppType.DISTRACTING:
                # Check Frequency and Start Threshold
                if (self.distraction_time % config.distracted_frequency == 0 and 
                    self.distraction_time >= config.distracted_events_start):
                    
                    # Check Chance (1.0 bypasses the RNG check)
                    if config.distracted_chance >= 1.0 or chance <= config.distracted_chance:
                        self._handle_distraction_logic(coro_events)
            
            case AppType.NEUTRAL | _:
                # Check Frequency and Start Threshold
                if (self.idle_time % config.idle_frequency == 0 and 
                    self.idle_time >= config.idle_events_start):
                    
                    # Check Chance
                    if config.idle_chance >= 1.0 or chance <= config.idle_chance:
                        self._handle_idle_logic(coro_events)

    def _handle_distraction_logic(self, coro_events):
        """Internal helper for distraction event triggers."""
        # Update Intensity
        if self.distraction_time >= 60: self.intensity = 3
        elif self.distraction_time >= 30: self.intensity = 2
        
        # Audio Management
        if self.audio_manager and not self.playing_music:
            self.audio_manager.play_music(Assets.audio.music.blackwall)
            self.playing_music = True
        
        if self.events is None: return
        time_value = format_time_str(self.distraction_time)
        app_log(f"[App] Distraction event triggered at {time_value}s")
        self.page.run_task(
            self.events.trigger_random_event, self.intensity,
            new_none_coro_events=coro_events
        )

    def _handle_idle_logic(self, coro_events):
        """Internal helper for idle/neutral event triggers."""
        if self.idle_time >= 120: self.intensity = 3
        elif self.idle_time >= 60: self.intensity = 2
            
        none_events = []
        if self.narrator:
            none_events.append(self.narrator.trigger_interrogation)
        
        if self.events is None: return
        time_value = format_time_str(self.idle_time)
        app_log(f"[App] Idle event triggered at {time_value}s")
        self.page.run_task(
            self.events.trigger_random_event, self.intensity,
            new_none_events=none_events if none_events else None,
            new_none_coro_events=coro_events
        )
    
    async def match_app_type(self, app_type: AppType) -> None:
        """Event handler for detected window type from monitor task."""
        match app_type:
            case AppType.PRODUCTIVE:
                self.productive_time += 1
                
                if self.productive_counter_text.spans and len(self.productive_counter_text.spans) > 0:
                    time_value = format_time_str(self.productive_time)
                    self.productive_counter_text.spans[1].text = time_value
                    try_update(self.productive_counter_text)
                    print(f"[App] Incremented productive_time to: {time_value}")
            
            case AppType.DISTRACTING:
                self.distraction_time += 1
                
                if self.popup_menu_item_csid.checked:
                    await self.page.window.center()
                    
                if not self.page.window.always_on_top and self.popup_menu_item_btfid.checked:
                    self.page.window.always_on_top = True
                    self.page.window.update()
                    
                if not self.page.window.maximized and self.popup_menu_item_fid.checked:
                    self.page.window.maximized = True
                    self.page.window.update()
                    
                if self.distractions_counter_text.spans and len(self.distractions_counter_text.spans) > 0:
                    time_value = format_time_str(self.distraction_time)
                    self.distractions_counter_text.spans[1].text = time_value
                    try_update(self.distractions_counter_text)
                    print(f"[App] Incremented distraction_time to: {time_value}")
                
            case AppType.NEUTRAL | _:
                self.idle_time += 1
                
                if self.page.window.always_on_top:
                    self.page.window.always_on_top = False
                    self.page.window.update()
                
                if self.idle_counter_text.spans and len(self.idle_counter_text.spans) > 0:
                    time_value = format_time_str(self.idle_time)
                    self.idle_counter_text.spans[1].text = time_value
                    try_update(self.idle_counter_text)
                    print(f"[App] Incremented idle_time to: {time_value}")
        
        self.match_event(app_type)
        await safe_sleep(1, self.stop_event)
    
    async def monitor_focus_async(self) -> None:
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
                try_update(self.category_text, self.current_app_col)
            await self.match_app_type(category)
        app_log("[App] Monitor task stopped.", LogType.GOOD)