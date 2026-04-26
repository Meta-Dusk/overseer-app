from dataclasses import dataclass

# | Images |
@dataclass
class Images:
    cake: str = "images/bday_cake.png"
    blackwall: str = "images/thing.png"
    blackwall_2: str = "images/thong.png"


# | Audio |
@dataclass
class Music:
    blackwall: str = "audio/music/ambience.mp3"

@dataclass
class SFX:
    jump: str = "audio/sfx/jump.mp3"
    screams: str = "audio/sfx/screams.mp3"
    
    def get_scream(self, index: int) -> str:
        return f"audio/sfx/scream_{index}.mp3"

@dataclass
class Audio:
    sfx = SFX()
    music = Music()


# | Base Class |
@dataclass
class Assets:
    audio = Audio()
    images = Images()