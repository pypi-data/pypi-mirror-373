from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple, Optional


class BaseServerManager(ABC):
    @abstractmethod
    def check_server_installed(self) -> bool:
        """Checks if the server is installed"""
        pass

    @abstractmethod
    def install_server(self) -> Tuple[bool, str]:
        """Installs the server if not already installed"""
        pass

    @abstractmethod
    def start_server(self) -> Tuple[bool, str]:
        """Starts the server"""
        pass

    @abstractmethod
    def stop_server(self) -> Tuple[bool, str]:
        """Stops the server"""
        pass

    @abstractmethod
    def restart_server(self) -> Tuple[bool, str]:
        """Restarts the server"""
        pass

    @abstractmethod
    def enable_server(self) -> Tuple[bool, str]:
        """Enables the server to start on boot"""
        pass

    @abstractmethod
    def check_server_status(self) -> bool:
        """Checks if the server is running"""
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass
    @abstractmethod
    def check_default_site_exists(self) -> bool:
        """Check if default site exists in sites-enabled."""
        pass
    
    @abstractmethod
    def remove_default_site(self) -> Tuple[bool, str]:
        """Remove the default site from sites-enabled."""
        pass
    
    @abstractmethod
    def test_configuration(self) -> Tuple[bool, str]:
        """Test the Nginx configuration."""
        pass
