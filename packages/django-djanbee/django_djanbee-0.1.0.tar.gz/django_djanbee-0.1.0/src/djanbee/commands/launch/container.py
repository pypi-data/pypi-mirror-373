from dataclasses import dataclass
from .display import LaunchDisplay
from .manager import LaunchManager
from ...core import AppContainer


@dataclass
class LaunchContainer:
    """Container for launch command components."""
    
    display: LaunchDisplay
    manager: LaunchManager

    @classmethod
    def create(cls, app: AppContainer) -> "LaunchContainer":
        """Factory method to create and wire launch components.
        
        Args:
            app: Application container with required dependencies
            
        Returns:
            Configured LaunchContainer instance
        """
        display = LaunchDisplay(console_manager=app.console_manager)
        manager = LaunchManager(display, app)
        return cls(display=display, manager=manager)
