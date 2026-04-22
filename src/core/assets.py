from dataclasses import dataclass

@dataclass
class SFX:
    lightning: str = "audio/sfx/lightning.mp3"

@dataclass
class Audio:
    sfx = SFX()

@dataclass
class Assets:
    audio = Audio()