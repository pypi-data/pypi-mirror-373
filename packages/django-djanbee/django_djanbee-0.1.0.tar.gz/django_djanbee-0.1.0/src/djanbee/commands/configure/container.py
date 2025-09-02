from dataclasses import dataclass
from .configure_database_display import ConfigureDatabaseDisplay
from .configure_database_manager import ConfigureDatabaseManager
from .configure_settings_display import ConfigureSettingsDisplay
from .configure_settings_manager import ConfigureSettingsManager
from ...core import AppContainer
from typing import Set
from .types import ConfigStep


@dataclass
class ConfigureContainer:

    configure_database_display: ConfigureDatabaseDisplay
    configure_database_manager: ConfigureDatabaseManager
    configure_settings_display: ConfigureSettingsDisplay
    configure_settings_manager: ConfigureSettingsManager

    @classmethod
    def create(cls, app: "AppContainer") -> "ConfigureContainer":
        configure_database_display = ConfigureDatabaseDisplay(
            console_manager=app.console_manager
        )
        configure_database_manager = ConfigureDatabaseManager(
            configure_database_display, app
        )
        configure_settings_display = ConfigureSettingsDisplay(
            console_manager=app.console_manager
        )
        configure_settings_manager = ConfigureSettingsManager(
            configure_settings_display, app
        )
        return cls(
            configure_database_display=configure_database_display,
            configure_database_manager=configure_database_manager,
            configure_settings_display=configure_settings_display,
            configure_settings_manager=configure_settings_manager,
        )

    def configure_project(
        self, database: bool = False, settings: bool = False, path: str = ""
    ) -> None:
        # Convert boolean flags to steps internally
        steps = set()
        if database:
            steps.add(ConfigStep.DATABASE)
        if settings:
            steps.add(ConfigStep.SETTINGS)

        # If no specific steps selected, use ALL
        if not steps:
            steps = {ConfigStep.ALL}
        if ConfigStep.ALL in steps:
            self._configure_all(path)
        else:
            self._run_specific_steps(path, steps)

    def _run_specific_steps(self, path: str, steps: Set[ConfigStep]) -> None:
        step_handlers = {
            ConfigStep.DATABASE: self.configure_database_manager.configure_database,
            ConfigStep.SETTINGS: self.configure_settings_manager._configure_settings,
        }

        for step in steps:
            if step in step_handlers:
                step_handlers[step](path)

    def _configure_all(self, path: str) -> None:
        if not self.configure_database_manager.configure_database(path):
            return False
        self.configure_settings_manager._configure_settings(path)
