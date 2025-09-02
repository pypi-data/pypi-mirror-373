from pathlib import Path
from ....managers.os_manager import OSManager
from ..state import DjangoManagerState
from typing import Optional, Tuple, List
from .project_service_display import DjangoProjectServiceDisplay
from collections import namedtuple

Result = namedtuple("Result", ["valid", "object"])


class DjangoProjectService:
    """Service for managing Django project files and structure"""

    def __init__(self, os_manager: OSManager, display: DjangoProjectServiceDisplay):
        self.os_manager = os_manager
        self.display = display
        self.state = DjangoManagerState.get_instance()

    def select_project(self):
        self.display.lookup_django_project()
        projects = self.find_django_project()
        if not projects:
            self.display.failure_lookup_django_project()
            return None
        if isinstance(projects, list):
            project = self._select_and_set_project(projects)
        else:
            project: Result = (
                projects  # if only one project no need to extract from list
            )

        if project:
            self.state.current_project_path = project.object
            self.display.success_lookup_project(project)
        return project

    def _select_and_set_project(
        self, projects: List[Tuple[str, Path]]
    ) -> Optional[Tuple[str, Path, bool]]:
        selected_project = self.display.prompt_project_selection(projects)
        if not selected_project:
            return None

        project_name, project_path = selected_project
        self.initialize_directory(project_path)
        return Result(True, project_path)

    def find_django_project(self) -> Optional[Tuple[str, Path, bool]]:
        project = self.find_django_project_in_current_dir()
        if not project:
            projects = self.find_django_projects_in_tree()
            if not projects:
                return None
            return projects
        return project

    def find_django_project_in_current_dir(self) -> bool:
        """Check if current directory contains a Django project"""
        return self.os_manager.search_folder(self.is_django_project)

    def find_django_projects_in_tree(self):
        """Search for Django projects in subdirectories"""
        return self.os_manager.search_subfolders(self.is_django_project)

    def initialize_directory(self, path: str) -> None:
        """Set up the working directory"""
        if not path:
            return_path = self.os_manager.get_dir()
        else:
            return_path = self.os_manager.set_dir(path)

    @staticmethod
    def is_django_project(path: Path) -> bool:
        """Validate if directory is a Django project

        Args:
            path (Path): Path to check

        Returns:
            bool: True if the directory contains a Django project, False otherwise
        """
        if not path.is_dir():
            return False

        has_manage_py = any(file.name == "manage.py" for file in path.iterdir())

        if not has_manage_py:
            return False

        manage_content = path.joinpath("manage.py").read_text()
        return "django" in manage_content.lower()

    def find_settings_file(self) -> Path:
        """Find the settings.py file in the Django project

        Returns:
            Path: Path to the settings.py file or None if not found
        """
        if not self.state._current_project_path:
            return None

        # Common patterns for settings file locations
        possible_locations = [
            # Standard Django project structure
            self.state._current_project_path
            / self.state._current_project_path.name
            / "settings.py",
            # Another common pattern (project/settings.py)
            self.state._current_project_path / "settings.py",
            # Project with config directory
            self.state._current_project_path / "config" / "settings.py",
            # Multiple settings files pattern
            self.state._current_project_path
            / self.state._current_project_path.name
            / "settings"
            / "base.py",
            self.state._current_project_path / "settings" / "base.py",
            self.state._current_project_path / "config" / "settings" / "base.py",
        ]

        # Check for settings module indicated in manage.py
        manage_path = self.current_project_path / "manage.py"
        if manage_path.exists():
            content = manage_path.read_text()
            # Look for DJANGO_SETTINGS_MODULE pattern
            import re

            settings_module_match = re.search(
                r'DJANGO_SETTINGS_MODULE["\']?\s*,\s*["\']([^"\']+)["\']', content
            )
            if settings_module_match:
                module_path = settings_module_match.group(1)
                # Convert module path (e.g. 'myproject.settings') to file path
                parts = module_path.split(".")
                file_path = self.current_project_path
                for part in parts[
                    :-1
                ]:  # All except the last part (which is the filename)
                    file_path = file_path / part
                file_path = file_path / f"{parts[-1]}.py"
                possible_locations.insert(0, file_path)  # Prioritize this path

        # Check each location
        for location in possible_locations:
            if location.exists() and location.is_file():
                return location

        # Search recursively as a fallback
        for path in self.current_project_path.rglob("settings.py"):
            return path

        return None
