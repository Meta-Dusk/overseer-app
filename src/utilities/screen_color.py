import ctypes, asyncio
from ctypes import wintypes
from typing import Optional, TypeAlias

# Define the 5x5 Matrix type (25 floats)
MAGCOLORMTRX = ctypes.c_float * 25

ColorMatrix: TypeAlias = list[float]
"""A 5x5 matrix of floats."""

class ColorMatrices:
    """A collection of preset 5x5 color matrices for screen effects."""
    
    IDENTITY = [
        1.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 1.0
    ]
    
    INVERT = [
        -1.0,  0.0,  0.0,  0.0,  0.0,
         0.0, -1.0,  0.0,  0.0,  0.0,
         0.0,  0.0, -1.0,  0.0,  0.0,
         0.0,  0.0,  0.0,  1.0,  0.0,
         1.0,  1.0,  1.0,  0.0,  1.0
    ]
    
    GRAYSCALE = [
        0.33, 0.33, 0.33, 0.0, 0.0,
        0.33, 0.33, 0.33, 0.0, 0.0,
        0.33, 0.33, 0.33, 0.0, 0.0,
        0.0,  0.0,  0.0,  1.0, 0.0,
        0.0,  0.0,  0.0,  0.0, 1.0
    ]
    
    BLOOD_MOON = [
        1.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.1, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.1, 0.0, 0.0,
        0.0, 0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 1.0
    ]
    
    ARCHIVE = [
        0.393, 0.349, 0.272, 0.0, 0.0,
        0.769, 0.686, 0.534, 0.0, 0.0,
        0.189, 0.168, 0.131, 0.0, 0.0,
        0.0,   0.0,   0.0,   1.0, 0.0,
        0.0,   0.0,   0.0,   0.0, 1.0
    ]
    
    DECAY = [
        0.0, 0.0, 1.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0, 0.0,
        1.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 1.0
    ]

    @staticmethod
    def get_dim(intensity: float = 0.1) -> list[float]:
        """Generates a matrix to dim the screen by a specific intensity (0.0 - 1.0)."""
        i = max(0.0, min(1.0, intensity))
        return [
            i,   0.0, 0.0, 0.0, 0.0,
            0.0, i,   0.0, 0.0, 0.0,
            0.0, 0.0, i,   0.0, 0.0,
            0.0, 0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 1.0
        ]

class ScreenColorManager:
    """
    Uses the Magnification API exports for unblockable color effects.
    You **MUST** call `initialize()` before using the methods.
    """
    
    _mag: Optional[ctypes.WinDLL] = None
    _current_matrix = ColorMatrices.IDENTITY.copy()

    @classmethod
    def initialize(cls) -> bool:
        """Must be called once at app startup to link the DLL and init the API."""
        try:
            # Explicitly load the DLL
            cls._mag = ctypes.WinDLL("magnification.dll")
            
            # Define argtypes for MagSetFullscreenColorEffect
            cls._mag.MagSetFullscreenColorEffect.argtypes = [ctypes.POINTER(MAGCOLORMTRX)]
            cls._mag.MagSetFullscreenColorEffect.restype = wintypes.BOOL
            
            # Define argtypes for Initialization/Cleanup
            cls._mag.MagInitialize.restype = wintypes.BOOL
            cls._mag.MagUninitialize.restype = wintypes.BOOL

            # Actually initialize the system
            if not cls._mag.MagInitialize():
                return False
            return True
        
        except (AttributeError, OSError):
            # Fallback if the DLL isn't supported on this specific Windows build
            return False

    @classmethod
    def apply_matrix(cls, matrix_values: ColorMatrix) -> bool:
        """Helper to send a matrix to the GPU."""
        if not cls._mag: return False
        cls._current_matrix = matrix_values
        matrix = MAGCOLORMTRX(*matrix_values)
        cls._mag.MagSetFullscreenColorEffect(ctypes.byref(matrix))
        return True
    
    @classmethod
    async def transition_to(
        cls, target_matrix: ColorMatrix, duration: float = 1.0
    ) -> None:
        """Smoothly fades the screen colors over the specified duration."""
        steps = 60
        interval = duration / steps
        start_matrix = cls._current_matrix.copy()
        
        for step in range(1, steps + 1):
            t = step / steps  # Progress from 0.0 to 1.0
            
            # Interpolate all 25 values
            new_matrix = [
                start_matrix[i] + (target_matrix[i] - start_matrix[i]) * t
                for i in range(25)
            ]
            
            # Use the internal _mag call directly to avoid repeated state updates
            if cls._mag:
                matrix = MAGCOLORMTRX(*new_matrix)
                cls._mag.MagSetFullscreenColorEffect(ctypes.byref(matrix))
            cls._current_matrix = new_matrix
            
            await asyncio.sleep(interval)
    
    @classmethod
    def reset(cls) -> bool:
        """Shortcut to restore default colors."""
        return cls.apply_matrix(ColorMatrices.IDENTITY)
    
    @classmethod
    def release(cls) -> bool:
        """Releases the API handle."""
        if not cls._mag: return False
        cls._mag.MagUninitialize()
        return True
    
    @classmethod
    def cleanup(cls) -> bool:
        """Resets colors and releases the API handle."""
        if not cls._mag: return False
        cls.reset()
        cls.release()
        return True