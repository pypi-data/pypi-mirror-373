from dataclasses import dataclass
from .display import SetupDisplay
from .manager import SetupManager
from ...core import AppContainer

@dataclass
class SetupContainer:

    display: SetupDisplay
    manager: SetupManager

    @classmethod
    def create(cls, app: 'AppContainer') -> 'SetupContainer':
        display = SetupDisplay(console_manager=app.console_manager)
        manager = SetupManager(display, app)
        return cls(
            display=display,
            manager=manager
        )