from dataclasses import dataclass

# | Images |
@dataclass
class Scares:
    wo: str = "images/wo.png"
    mm: str = "images/mm.png"

@dataclass
class Images:
    scares = Scares()
    cake: str = "images/bday_cake.png"


# | Audio |
@dataclass
class Music:
    pass

@dataclass
class SFX:
    lightning: str = "audio/sfx/lightning.mp3"
    knock_left: str = "audio/sfx/knock_left.mp3"
    knock_right: str = "audio/sfx/knock_right.mp3"
    discord_ping: str = "audio/sfx/discord_ping.mp3"

@dataclass
class Audio:
    sfx = SFX()
    music = Music()


# | Base Class |
@dataclass
class Assets:
    audio = Audio()
    images = Images()