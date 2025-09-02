from pathlib import Path
from typing import Optional, List, Tuple
from collections import namedtuple

from ..os_manager import OSManager
from ..console_manager import ConsoleManager
from ..django_manager import DjangoManager
from .server_implementations import NginxServerManager
from ..os_manager.command_runner import CommandResult

Result = namedtuple("Result", ["valid", "object"])


class ServerManager:
    def __init__(
        self,
        os_manager: OSManager,
        console_manager: ConsoleManager,
        django_manager: DjangoManager,
        server_type: str = "nginx",
    ):
        """Initializes server-specific manager"""
        self.os_manager = os_manager
        self.console_manager = console_manager
        self.django_manager = django_manager
        if server_type.lower() == "nginx":
            self._manager = NginxServerManager(
                self.os_manager, self.console_manager, self.django_manager
            )
        else:
            raise ValueError(f"Unsupported server type: {server_type}")

    def check_server_installed(self) -> bool:
        """Checks if the server is installed"""
        return self._manager.check_server_installed()

    def install_server(self) -> CommandResult:
        """Installs the server if not already installed"""
        return self._manager.install_server()

    def start_server(self) -> CommandResult:
        """Starts the server"""
        return self._manager.start_server()

    def stop_server(self) -> CommandResult:
        """Stops the server"""
        return self._manager.stop_server()

    def restart_server(self) -> CommandResult:
        """Restarts the server"""
        return self._manager.restart_server()

    def enable_server(self) -> CommandResult:
        """Enables the server to start on boot"""
        return self._manager.enable_server()

    def check_server_status(self) -> CommandResult:
        """Checks if the server is running"""
        return self._manager.check_server_status()

    def get_server_version(self) -> str:
        """Gets the server version"""
        return self._manager.get_server_version()

    def get_dependencies(self) -> List[str]:
        """Returns list of dependencies for the current server"""
        if hasattr(self._manager, "get_dependencies"):
            return self._manager.get_dependencies()
        return []

    def verify_dependencies(self) -> List[Tuple[str, bool, str]]:
        """Verifies all dependencies"""
        if hasattr(self._manager, "verify_dependencies"):
            return self._manager.verify_dependencies()
        return []

    def install_dependency(self, dependency: str) -> Tuple[bool, str]:
        """Installs a specific dependency"""
        if hasattr(self._manager, "install_dependency"):
            return self._manager.install_dependency(dependency)
        return False, "Server doesn't support dependency installation"

    def check_server_config_exists(
        self, project_name: str
    ) -> Tuple[bool, Optional[Path]]:
        """
        Check if a server configuration exists for the given project

        Args:
            project_name: Name of the project (used to identify the config)

        Returns:
            Tuple of (exists, config_file_path)
            If config doesn't exist, path will be None
        """
        return self._manager.check_server_config_exists(project_name)

    def create_server_config(
        self,
        project_path: Path,
        project_name: str,
        server_name: str = "localhost",
        socket_path: Path = None,
        use_sudo: bool = False,
    ) -> Tuple[bool, str]:
        """
        Create a server configuration for the given project

        Args:
            project_path: Path to the project directory
            project_name: Name of the project
            server_name: Server name/domain for the config
            socket_path: Path to the socket file (if applicable)
            use_sudo: Whether to use sudo for file operations

        Returns:
            Tuple of (success, message or config_path)
        """
        return self._manager.create_server_config(
            project_path, project_name, server_name, socket_path, use_sudo
        )


    def check_default_site_exists(self) -> bool:
        """Check if default site exists in sites-enabled."""
        return self._manager.check_default_site_exists()

    def remove_default_site(self) -> Tuple[bool, str]:
        """Remove the default site from sites-enabled."""
        return self._manager.remove_default_site()

    def test_configuration(self) -> Tuple[bool, str]:
        """Test the Nginx configuration."""
        return self._manager.test_configuration()