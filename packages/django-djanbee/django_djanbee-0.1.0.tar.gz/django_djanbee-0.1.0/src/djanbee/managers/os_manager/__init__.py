from .main import OSManager
from .base import BaseOSManager
from .os_implementations import UnixOSManager, WindowsOSManager

__version__ = "1.0.0"
__all__ = ["OSManager", "BaseOSManager", "UnixOSManager", "WindowsOSManager"]
