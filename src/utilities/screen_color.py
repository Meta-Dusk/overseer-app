import ctypes
from ctypes import wintypes

# Define the 5x5 Matrix type (25 floats)
MAGCOLORMTRX = ctypes.c_float * 25

class ScreenColorManager:
    """
    Uses the Magnification API exports for unblockable color effects.
    You **MUST** call `initialize()` before using the methods.
    """
    
    _mag = None

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
    def _apply_matrix(cls, matrix_values) -> bool:
        """Helper to send a matrix to the GPU."""
        if not cls._mag: return False
        matrix = MAGCOLORMTRX(*matrix_values)
        cls._mag.MagSetFullscreenColorEffect(ctypes.byref(matrix))
        return True

    @classmethod
    def apply_invert(cls) -> bool:
        """Inverts all colors on the screen."""
        # Standard Inversion Matrix
        matrix = [
            -1.0,  0.0,  0.0,  0.0,  0.0,
             0.0, -1.0,  0.0,  0.0,  0.0,
             0.0,  0.0, -1.0,  0.0,  0.0,
             0.0,  0.0,  0.0,  1.0,  0.0,
             1.0,  1.0,  1.0,  0.0,  1.0
        ]
        return cls._apply_matrix(matrix)

    @classmethod
    def apply_grayscale(cls) -> bool:
        """Turns the entire screen to grayscale."""
        # Standard Grayscale Matrix
        g = 0.33
        matrix = [
            g,   g,   g,   0.0, 0.0,
            g,   g,   g,   0.0, 0.0,
            g,   g,   g,   0.0, 0.0,
            0.0, 0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 1.0
        ]
        return cls._apply_matrix(matrix)
    
    @classmethod
    def apply_blood_moon(cls) -> bool:
        """Deep red saturation with suppressed greens/blues."""
        matrix = [
            1.0, 0.0, 0.0, 0.0, 0.0,  # Red stays 100%
            0.0, 0.1, 0.0, 0.0, 0.0,  # Green dropped to 10%
            0.0, 0.0, 0.1, 0.0, 0.0,  # Blue dropped to 10%
            0.0, 0.0, 0.0, 1.0, 0.0,  # Alpha stays
            0.0, 0.0, 0.0, 0.0, 1.0   # Identity
        ]
        return cls._apply_matrix(matrix)
    
    @classmethod
    def apply_void(cls, intensity: float = 0.1):
        """Dims the entire screen significantly."""
        i = max(0.0, min(1.0, intensity))
        matrix = [
            i,   0.0, 0.0, 0.0, 0.0,
            0.0, i,   0.0, 0.0, 0.0,
            0.0, 0.0, i,   0.0, 0.0,
            0.0, 0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 1.0
        ]
        return cls._apply_matrix(matrix)
    
    @classmethod
    def apply_archive(cls) -> bool:
        """Classic high-contrast sepia tone."""
        matrix = [
            0.393, 0.349, 0.272, 0.0, 0.0,
            0.769, 0.686, 0.534, 0.0, 0.0,
            0.189, 0.168, 0.131, 0.0, 0.0,
            0.0,   0.0,   0.0,   1.0, 0.0,
            0.0,   0.0,   0.0,   0.0, 1.0
        ]
        return cls._apply_matrix(matrix)
    
    @classmethod
    def apply_decay(cls) -> bool:
        """Swaps red and blue channel intensity for a sick, cyan look."""
        matrix = [
            0.0, 0.0, 1.0, 0.0, 0.0, # Red becomes Blue
            0.0, 1.0, 0.0, 0.0, 0.0, # Green stays
            1.0, 0.0, 0.0, 0.0, 0.0, # Blue becomes Red
            0.0, 0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 1.0
        ]
        return cls._apply_matrix(matrix)
    
    @classmethod
    def reset(cls) -> bool:
        """Restores identity (normal) colors."""
        identity = [
            1.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 1.0
        ]
        return cls._apply_matrix(identity)
    
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