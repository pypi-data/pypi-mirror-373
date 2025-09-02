from pathlib import Path
from ....managers.os_manager import OSManager
from ..state import DjangoManagerState
from collections import namedtuple
from typing import Tuple
from .requirements_service_display import DjangoRequirementsServiceDisplay

Result = namedtuple("Result", ["valid", "object"])


class DjangoRequirementsService:
    """Service for managing virtual environment"""

    def __init__(
        self, os_manager: OSManager, display: DjangoRequirementsServiceDisplay
    ):
        self.os_manager = os_manager
        self.state = DjangoManagerState.get_instance()
        self.display = display

    # High-level public methods first
    def find_or_extract_requirements(self, venv_path=None):
        """Find existing requirements or extract from virtual environment"""
        self.display.lookup_requirements()
        requirements = self.find_requirements()

        if not requirements:
            self.display.failure_lookup_requirements()
            if self.display.prompt_extract_requirements():
                # Use the provided venv_path or fall back to the one in state
                active_venv = venv_path or self.state.active_venv_path
                if not active_venv:
                    return None, "No active virtual environment found"

                requirements = self.extract_requirements(active_venv)
            else:
                return None

        if requirements:
            self.display.success_lookup_requirements(requirements.object)

        return requirements

    def install_requirements_if_confirmed(self, requirements: Result, venv_path=None):
        """Install requirements if user confirms"""
        if self.display.prompt_install_requirements():
            self.display.progress_install_requirements()

            # Use the provided venv_path or fall back to the one in state
            active_venv = venv_path or self.state.active_venv_path
            if not active_venv:
                return False, "No active virtual environment found"

            result = self.install_requirements(active_venv, requirements.object)

            if result[0]:  # If installation was successful
                self.display.success_install_requirements(
                    requirements.object, active_venv
                )
                return True, "Requirements installed successfully"
            else:
                return result
        else:
            return False, "Installation cancelled by user"

    # Mid-level methods grouped by functionality
    def find_requirements(self):
        requirements = self.os_manager.search_folder(self.has_requirements)
        if not requirements:
            requirements = self.os_manager.search_subfolders(self.has_requirements)

        if requirements:
            self.state.current_requirements_path = (
                requirements.object / "requirements.txt"
            )
            return Result(True, requirements.object / "requirements.txt")
        return None

    def extract_requirements(self, venv_path: str | Path) -> Tuple[bool, str]:
        """Extracts pip requirements from a virtual environment"""
        venv_path = Path(venv_path)

        requirements_filename = "requirements.txt"
        requirements_path = self.os_manager.get_dir() / requirements_filename

        # Run pip freeze using OS manager
        success, output = self.os_manager.run_pip_command(venv_path, ["freeze"])
        if not success:
            return False, output

        # Write requirements file using OS manager
        write_success, message = self.os_manager.write_text_file(
            requirements_path, output
        )
        if not write_success:
            return False, message

        return Result(True, requirements_path)

    def install_requirements(
        self, venv_path: str | Path, requirements_path: str | Path
    ) -> Tuple[bool, str]:
        """Installs pip requirements into a virtual environment"""

        venv_path = Path(venv_path)

        requirements_path = Path(requirements_path)

        # Check if requirements file exists
        if not self.os_manager.check_file_exists(requirements_path):
            return False, f"Requirements file not found: {requirements_path}"
        # Run pip install with requirements file
        success, output = self.os_manager.run_pip_command(
            venv_path, ["install", "-r", str(requirements_path)]
        )

        if success:
            return True, "Requirements installed successfully"
        else:
            return False, output

    # Utility/helper methods last
    def has_requirements(self, path="."):
        """
        Check if directory has requirements file by verifying:
        1. requirements.txt exists
        Or alternative requirement files like:
        2. requirements-dev.txt
        3. requirements-prod.txt
        """
        # Common requirements file patterns
        requirement_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "requirements-prod.txt",
        ]

        # Check for any of the requirements files
        for req_file in requirement_files:
            if (path / req_file).exists():
                return True

        return False
