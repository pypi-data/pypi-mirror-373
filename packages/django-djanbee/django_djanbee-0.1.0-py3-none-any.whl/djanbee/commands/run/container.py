from dataclasses import dataclass
from .display import RunDisplay
from .manager import RunManager
from ...core import AppContainer

@dataclass
class RunContainer:

    display: RunDisplay
    manager: RunManager

    @classmethod
    def create(cls, app: 'AppContainer') -> 'RunContainer':
        display = RunDisplay(console_manager=app.console_manager)
        manager = RunManager(display, app)
        return cls(
            display=display,
            manager=manager
        )
    
    def run_django_setup(self, path):
        self.manager.initialize_project(path)
        self.manager.migrate_database()
        self.manager.collect_static_files()