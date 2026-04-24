import ctypes, os
from pathlib import Path
from ctypes import wintypes
from typing import Optional

FILE_ATTRIBUTE_READONLY = 0x01
"""Win32 Constant for Read-Only"""

FILE_ATTRIBUTE_READWRITE = 0x80
"""Win32 Constant for Read and Write Files."""

class DesktopManager:
    """Handles creating and removing 'Overseer' files on the user's desktop."""
    
    @staticmethod
    def get_desktop_path() -> Path:
        """Retrieves the absolute path to the Windows Desktop."""
        # CSIDL_DESKTOP = 0x0000
        buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, 0, None, 0, buf)
        return Path(buf.value)

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
            
            # Set to Read-Only using kernel32
            # str(file_path) ensures compatibility with the C-string pointer
            ctypes.windll.kernel32.SetFileAttributesW(
                str(file_path), FILE_ATTRIBUTE_READONLY
            )
            
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
                #! We MUST remove the read-only attribute before we can delete it!
                ctypes.windll.kernel32.SetFileAttributesW(
                    str(file), FILE_ATTRIBUTE_READWRITE
                )
                file.unlink()
            except Exception: pass