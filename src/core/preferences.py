import flet as ft
from flet.controls.services.shared_preferences import SharedPreferencesValueType
from typing import Optional, Literal, TypeAlias

AvailablePrefKeys: TypeAlias = Literal[
    "idle_freq", "dist_freq", "prod_freq", "idle_chance", "dist_chance",
    "sfx_volume", "music_volume"
]
PrefsKeys: TypeAlias = AvailablePrefKeys | str

class Preferences:
    def __init__(self):
        self.key_prefix_str = "metadusk.overseer."
        self.prefs = ft.SharedPreferences()
    
    def _prefix_key(self, key: PrefsKeys) -> str:
        return f"{self.key_prefix_str}{key}"
    
    async def get(self, key: PrefsKeys) -> Optional[SharedPreferencesValueType]:
        print(f"Getting value: {key}")
        return await self.prefs.get(self._prefix_key(key))
    
    async def set(self, key: PrefsKeys, value: SharedPreferencesValueType) -> bool:
        print(f"Returning value for: {key} -> {value}")
        return await self.prefs.set(self._prefix_key(key), value)
    
    async def clear(self) -> bool:
        return await self.prefs.clear()