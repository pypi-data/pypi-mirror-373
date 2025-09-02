from pathlib import Path
from ....managers.os_manager import OSManager
from ..state import DjangoManagerState
import sys
from collections import namedtuple
import venv
from .venv_service_display import DjangoEnvironmentServiceDisplay

Result = namedtuple("Result", ["valid", "object"])


class DjangoEnvironmentService:
    """Service for managing virtual environment"""

    def __init__(self, os_manager: OSManager, display: DjangoEnvironmentServiceDisplay):
        self.os_manager = os_manager
        self.state = DjangoManagerState.get_instance()
        self.display = display

    def get_active_venv(self):
        """Detects active virtual environment"""

        # First check VIRTUAL_ENV environment variable
        virtual_env = self.os_manager.get_environment_variable("VIRTUAL_ENV")
        if not virtual_env:
            return None

        # If we have VIRTUAL_ENV, verify it with sys.prefix
        if hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        ):
            venv_name = self.os_manager.get_path_basename(virtual_env)
            self.state.active_venv_path = virtual_env
            return Result(
                True, {"virtual_env": virtual_env, "virtual_env_name": venv_name}
            )

        return None

    def is_venv(self, path="."):
        """Check if path is a virtual environment"""
        path = Path(path) if not isinstance(path, Path) else path
        return self.os_manager.is_venv_directory(path)

    def find_envs(self):
        envs = self.os_manager.search_folder(self.is_venv)
        return envs

    def create_environment(self, path: str = ".venv") -> bool:
        """
        Create a new virtual environment

        Args:
            path: Path where to create the environment (default: .venv)
        Returns:
            bool: True if environment was created successfully
        """
        try:
            self.console_manager.print_progress("Creating virtual environment...")
            venv_path = Path(path)

            # Create the virtual environment
            venv.create(venv_path, with_pip=True)

            self.console_manager.print_success(
                f"Virtual environment created at {venv_path}"
            )
            return (venv_path.name, venv_path, True)

        except Exception as e:
            self.console_manager.print_error(
                f"Failed to create virtual environment: {str(e)}"
            )
            return False

    def find_or_create_venv(self):
        """Find existing virtual environment or create a new one"""
        self.display.lookup_venv()

        active_venv = self.get_active_venv()

        if not active_venv:
            self.display.failure_lookup_venv("No active virtual environment")
            envs = self.find_envs()

            if not envs:
                self.display.failure_lookup_venvs()
                if self.display.prompt_create_environment():
                    new_env = self.create_environment()
                    if new_env:
                        _, venv_path, _ = new_env
                        env_name = self.os_manager.get_path_basename(venv_path)
                        return Result(
                            True,
                            {"virtual_env": venv_path, "virtual_env_name": env_name},
                        )
                else:
                    return None
            else:
                # If you want to handle selecting from multiple found environments
                # Add code here to select one environment from envs
                pass

        self.display.success_lookup_venv()
        is_active, venv = active_venv
        self.display.success_locate_env(venv["virtual_env_name"], venv["virtual_env"])
        return venv
