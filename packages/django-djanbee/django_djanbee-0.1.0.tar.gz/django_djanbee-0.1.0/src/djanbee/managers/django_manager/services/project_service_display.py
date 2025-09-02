from pathlib import Path
from ...console_manager import ConsoleManager
from typing import Tuple, List
from ....widgets.list_selector import ListSelector


class DjangoProjectServiceDisplay:
    """Service for managing Django project files and structure"""

    def __init__(self, console_manager: "ConsoleManager"):
        self.console_manager = console_manager

    def lookup_django_project(self):
        self.console_manager.print_lookup("Looking for django projects")

    def failure_lookup_django_project(self):
        self.console_manager.print_warning_critical(
            "Django project not found in this folder"
        )

    def prompt_project_selection(
        self, projects: List[Tuple[str, Path]]
    ) -> Tuple[str, Path] | None:
        if not projects:
            return None

        choices = [(result.object.name, result.object) for result in projects]
        self.console_manager.console.print("\nDid you mean one of these projects?")
        selector = ListSelector("Select Django Project", choices, self.console_manager)
        return selector.select()

    def success_lookup_project(self, project) -> None:
        self.console_manager.print_success(
            f"Setting Django project as {project.object.name} in {project.object}"
        )
