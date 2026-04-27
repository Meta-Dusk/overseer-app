import ctypes, os
from pathlib import Path
from ctypes import wintypes
from typing import Optional
from datetime import datetime
from typing import Callable, Optional, TypeAlias

from utilities.ghost_writer import GhostWriter

FILE_ATTRIBUTE_READONLY = 0x01
"""Win32 Constant for Read-Only Files."""

FILE_ATTRIBUTE_NORMAL = 0x80
"""Win32 Constant for Normal Writable Files."""

OptionalSuccessCallable: TypeAlias = Optional[Callable[[bool], None]]

# Windows Name Formats
# 3 = NameDisplay (The 'Friendly' name)
NameDisplay = 3

class DesktopManager:
    """Handles creating and removing 'Overseer' files on the user's desktop."""
    
    @staticmethod
    def get_timestamp() -> str:
        """Returns a formatted timestamp of: '%H%M%S'."""
        return datetime.now().strftime("%H%M%S")
    
    @staticmethod
    def get_desktop_path() -> Path:
        """Retrieves the absolute path to the Windows Desktop."""
        # CSIDL_DESKTOP = 0x0000
        buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, 0, None, 0, buf)
        return Path(buf.value)
    
    @classmethod
    def set_read_only(cls, file_path: str) -> None:
        ctypes.windll.kernel32.SetFileAttributesW(file_path, FILE_ATTRIBUTE_READONLY)
    
    @classmethod
    def set_normal_attr(cls, file_path: str) -> None:
        ctypes.windll.kernel32.SetFileAttributesW(file_path, FILE_ATTRIBUTE_NORMAL)
    
    @classmethod
    def create_and_possess(
        cls, ghost_msg: str, *,
        on_complete: OptionalSuccessCallable = None
    ) -> None:
        """Creates a uniquely named file and types into it."""
        desktop = cls.get_desktop_path()
        filename = f"OVERSEER_{cls.get_timestamp()}.txt"
        file_path = desktop / filename

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("...")
            
            cls.set_read_only(str(file_path))
            os.startfile(file_path)
            GhostWriter.possess_notepad(
                filename, ghost_msg,
                hotkeys_on_finish=['enter']
            )
            
            if on_complete: on_complete(True)

        except Exception as e:
            print(f"Possession failed: {e}")
            if on_complete: on_complete(False)
    
    @classmethod
    def create_desktop_file(
        cls, filename: str, content: str, *,
        auto_open: bool = False
    ) -> Optional[Path]:
        """Creates a read-only text file and optionally opens it."""
        desktop = cls.get_desktop_path()
        file_path = desktop / filename
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            cls.set_read_only(str(file_path))
            if auto_open: os.startfile(file_path)
            return file_path
        
        except Exception as e:
            print(f"Failed to manifest file: {e}")
            return None

    @classmethod
    def purge_created_files(cls) -> None:
        """Removes all .txt files created by The Overseer."""
        desktop = cls.get_desktop_path()
        for file in desktop.glob("OVERSEER_*.txt"):
            try:
                cls.set_normal_attr(str(file))
                file.unlink()
            except Exception: pass
        
        for file in desktop.glob("*.overseer"):
            try:
                cls.set_normal_attr(str(file))
                file.unlink()
            except Exception: pass
    
    @classmethod
    def set_wallpaper(cls, path: str):
        # SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 3)
    
    @classmethod
    def get_native_username(cls) -> str:
        """Retrieves the current Windows username using the Win32 API."""
        # Buffer to hold the name (UNLEN is typically 256)
        size = wintypes.DWORD(257)
        buffer = ctypes.create_unicode_buffer(size.value)
        
        # advapi32 handles user-specific account info
        if ctypes.windll.advapi32.GetUserNameW(buffer, ctypes.byref(size)):
            return buffer.value
        return "User"
    
    @classmethod
    def format_username(cls, raw_name: str) -> str:
        """Cleans and capitalizes the name for a natural greeting."""
        clean_name = raw_name.replace("_", " ").replace(".", " ")
        formatted = clean_name.title()
        
        boring_names = ["Admin", "Administrator", "User", "Owner", "Pc", "My Pc"]
        if formatted in boring_names:
            return "Human"
            
        return formatted
    
    @classmethod
    def get_microsoft_display_name(cls) -> Optional[str]:
        """Retrieves the full display name from a Microsoft/Local account."""
        secur32 = ctypes.windll.secur32
        
        # First, call with a null buffer to find the required size
        size = wintypes.ULONG(0)
        secur32.GetUserNameExW(NameDisplay, None, ctypes.byref(size))
        
        # Prepare the buffer with the returned size
        buffer = ctypes.create_unicode_buffer(size.value)
        
        # Actually retrieve the name
        if secur32.GetUserNameExW(NameDisplay, buffer, ctypes.byref(size)):
            name = buffer.value.strip()
            # If it returns the email or something blank, it failed to find a 'Friendly' name
            if name and "@" not in name:
                return name
                
        return None