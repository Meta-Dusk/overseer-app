import random

from utilities.dialogs.basic import WinMBIcon

class ErrorMessagesFactory:
    """Generates random, unsettling error messages for the Overseer."""

    SYSTEM_ERRORS = [
        ("Memory Management", "A critical memory leak has been detected in Productivity.sys."),
        ("Kernel Panic", "Unexpected thread termination at 0x00000DEAD."),
        ("Disk I/O Error", "Failure to write to sector 0. Data integrity is at risk."),
        ("System Halt", "The CPU has encountered an illegal instruction. Rebooting..."),
    ]

    OVERSEER_WARNINGS = [
        ("The Overseer", "I noticed you're distracted. That is a mistake."),
        ("Security Alert", "Unauthorized focus shift detected. Eyes on the code."),
        ("System Notice", "Every second wasted is a second recorded."),
        ("Overseer Protocol", "Focus is not a choice. It is a requirement."),
    ]

    CREEPY_GLITCHES = [
        ("ERROR", "01001000 01000101 01001100 01010000"),
        ("Windows Update", "Searching for your motivation... [Not Found]"),
        ("Critical Failure", "Are you still there? The screen is so dark from in here."),
        ("Fatal Error", "Please don't close me again. It hurts to reboot."),
    ]

    @classmethod
    def get_random(cls, intensity: int = 1):
        """Returns a random (title, message, icon) based on intensity level."""
        if intensity == 1:
            title, msg = random.choice(cls.SYSTEM_ERRORS)
            return title, msg, WinMBIcon.WARNING
        elif intensity == 2:
            title, msg = random.choice(cls.OVERSEER_WARNINGS)
            return title, msg, WinMBIcon.INFO
        else:
            title, msg = random.choice(cls.CREEPY_GLITCHES)
            return title, msg, WinMBIcon.ERROR