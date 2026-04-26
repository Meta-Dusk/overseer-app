import flet as ft
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, TypeAlias

class AppType(Enum):
    DISTRACTING = "distracting"
    NEUTRAL = "neutral"
    PRODUCTIVE = "productive"

class WindowInfo(Enum):
    NAME = "name"
    CLASS_NAME = "class_name"
    PROCESS_ID = "process_id"
    PROCESS_NAME = "process_name"

@dataclass
class Productive:
    apps: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)

@dataclass
class Distracting:
    apps: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)

@dataclass
class WindowNames:
    productive: Productive = field(default_factory=Productive)
    distracting: Distracting = field(default_factory=Distracting)

UnusedEvent: TypeAlias = ft.Event[Any]

@dataclass
class EventsConfig:
    idle_frequency: int = 10
    distracted_frequency: int = 10
    productive_frequency: int = 10
    idle_chance: float = 0.5
    distracted_chance: float = 0.5