from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Union

from .command_runner import CommandRunner, CommandResult


class BaseOSManager(ABC):
    def __init__(self, runner: CommandRunner):
        """Initialize with a shared CommandRunner."""
        self._runner = runner

    @abstractmethod
    def get_dir(self) -> Path:
        """Returns the current working directory."""
        pass

    @abstractmethod
    def get_pip_path(self, venv_path: Path) -> Path:
        """Get the platform-specific pip executable path in a virtual environment."""
        pass

    @abstractmethod
    def check_pip_package_installed(
        self, package_name: str
    ) -> CommandResult:
        """Checks if a Python package is installed via pip."""
        pass

    @abstractmethod
    def install_pip_package(
        self, package_name: str
    ) -> CommandResult:
        """Installs a Python package via pip."""
        pass

    @abstractmethod
    def check_package_installed(
        self, package_name: str
    ) -> CommandResult:
        """Checks if a system package is installed."""
        pass

    @abstractmethod
    def check_service_status(
        self, service_name: str
    ) -> CommandResult:
        """Checks if a system service is running."""
        pass

    @abstractmethod
    def install_package(
        self, package_name: str
    ) -> CommandResult:
        """Installs a system package."""
        pass

    @abstractmethod
    def start_service(
        self, service_name: str
    ) -> CommandResult:
        """Starts a system service."""
        pass

    @abstractmethod
    def stop_service(
        self, service_name: str
    ) -> CommandResult:
        """Stops a system service."""
        pass

    @abstractmethod
    def restart_service(
        self, service_name: str
    ) -> CommandResult:
        """Restarts a system service."""
        pass

    @abstractmethod
    def enable_service(
        self, service_name: str
    ) -> CommandResult:
        """Enables a service to start on boot."""
        pass

    @abstractmethod
    def run_command(
        self, command: Union[str, List[str]]
    ) -> CommandResult:
        """Runs a system command (string or list of args)."""
        pass

    @abstractmethod
    def run_python_command(
        self, command_args: List[str]
    ) -> CommandResult:
        """Runs a Python command using the system's interpreter."""
        pass

    @abstractmethod
    def get_username(self) -> str:
        """Gets the current user's username."""
        pass

    @abstractmethod
    def is_admin(self) -> bool:
        """Checks if the current user has admin privileges."""
        pass

    @abstractmethod
    def is_venv_directory(self, path: Path) -> bool:
        """Checks if a directory is a Python virtual environment."""
        pass

    @abstractmethod
    def check_directory_exists(
        self, dir_path: Union[str, Path]
    ) -> bool:
        """Checks if a directory exists at the given path."""
        pass

    @abstractmethod
    def check_file_exists(self, file_path: Path) -> bool:
        """Checks if a file exists at the given path."""
        pass

    @abstractmethod
    def reload_daemon(self) -> CommandResult:
        """Reloads the system service daemon (e.g., systemd)."""
        pass

    @abstractmethod
    def user_exists(self, username: str) -> bool:
        """Checks if a system user with the given name exists."""
        pass
