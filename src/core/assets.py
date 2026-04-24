from dataclasses import dataclass

# | Images |
@dataclass
class Scares:
    wom1: str = "assets/images/o.png"

@dataclass
class Images:
    scares = Scares()


# | Audio |
@dataclass
class Music:
    pass

@dataclass
class SFX:
    lightning: str = "audio/sfx/lightning.mp3"

@dataclass
class Audio:
    sfx = SFX()
    music = Music()


# | Base Class |
@dataclass
class Assets:
    audio = Audio()
    images = Images()