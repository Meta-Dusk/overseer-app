import ctypes
from ctypes import wintypes

# Define the 5x5 Matrix type (25 floats)
MAGCOLORMTRX = ctypes.c_float * 25

class ScreenColorManager:
    """Uses the correct Magnification API exports for unblockable color effects."""
    
    _mag = None

    @classmethod
    def initialize(cls):
        """Must be called once at app startup to link the DLL and init the API."""
        try:
            # Explicitly load the DLL
            cls._mag = ctypes.WinDLL("magnification.dll")
            
            # 1. Define argtypes for MagSetFullscreenColorEffect (The correct function)
            cls._mag.MagSetFullscreenColorEffect.argtypes = [ctypes.POINTER(MAGCOLORMTRX)]
            cls._mag.MagSetFullscreenColorEffect.restype = wintypes.BOOL
            
            # 2. Define argtypes for Initialization/Cleanup
            cls._mag.MagInitialize.restype = wintypes.BOOL
            cls._mag.MagUninitialize.restype = wintypes.BOOL

            # 3. Actually initialize the system
            if not cls._mag.MagInitialize():
                return False
            return True
        except (AttributeError, OSError):
            # Fallback if the DLL isn't supported on this specific Windows build
            return False

    @classmethod
    def _apply_matrix(cls, matrix_values):
        """Helper to send a matrix to the GPU."""
        if not cls._mag: return
        matrix = MAGCOLORMTRX(*matrix_values)
        cls._mag.MagSetFullscreenColorEffect(ctypes.byref(matrix))

    @classmethod
    def apply_invert(cls):
        """Inverts all colors on the screen."""
        # Standard Inversion Matrix
        matrix = [
            -1.0,  0.0,  0.0,  0.0,  0.0,
             0.0, -1.0,  0.0,  0.0,  0.0,
             0.0,  0.0, -1.0,  0.0,  0.0,
             0.0,  0.0,  0.0,  1.0,  0.0,
             1.0,  1.0,  1.0,  0.0,  1.0
        ]
        cls._apply_matrix(matrix)

    @classmethod
    def apply_grayscale(cls):
        """Turns the entire screen to grayscale."""
        # Standard Grayscale Matrix
        g = 0.33
        matrix = [
            g, g, g, 0.0, 0.0,
            g, g, g, 0.0, 0.0,
            g, g, g, 0.0, 0.0,
            0.0, 0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 1.0
        ]
        cls._apply_matrix(matrix)

    @classmethod
    def reset(cls):
        """Restores identity (normal) colors."""
        identity = [
            1.0, 0.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 0.0, 1.0
        ]
        cls._apply_matrix(identity)

    @classmethod
    def cleanup(cls):
        """Resets colors and releases the API handle."""
        if cls._mag:
            cls.reset()
            cls._mag.MagUninitialize()