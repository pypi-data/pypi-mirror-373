from pathlib import Path
from typing import Tuple, Optional

from ..os_manager import OSManager
from ..console_manager import ConsoleManager
from ..django_manager import DjangoManager
from .socket_implementations import GunicornSocketManager
from .base import BaseSocketManager


class SocketManager:
    """
    Factory class for creating and managing different socket implementations
    """

    def __init__(
        self,
        os_manager: OSManager,
        console_manager: ConsoleManager,
        django_manager: DjangoManager,
        socket_type: str = "gunicorn",
    ):
        """
        Initialize socket manager with dependencies

        Args:
            os_manager: OS manager for platform-specific operations
            console_manager: Console manager for output display
            django_manager: Django manager for project information
            socket_type: Type of socket implementation to use
        """
        self.os_manager = os_manager
        self.console_manager = console_manager
        self.django_manager = django_manager

        # Initialize the appropriate socket manager based on type
        if socket_type.lower() == "gunicorn":
            self._manager = GunicornSocketManager(
                self.os_manager, self.console_manager, self.django_manager
            )
        else:
            raise ValueError(f"Unsupported socket type: {socket_type}")

    def check_socket_service_exists(self, project_name: str) -> Tuple[bool, Optional[Path], str]:
        """
        Check if a socket file exists for the given project

        Args:
            project_name: Name of the project (used as part of socket filename)

        Returns:
            Tuple of (exists, service_file_path, message)
            - exists: Boolean indicating if service exists
            - service_file_path: Path to service file or None if doesn't exist
            - message: Descriptive message about the service status
        """
        return self._manager.check_socket_service_exists(project_name)

    def create_socket_service(
        self, project_path: Path, project_name: str, wsgi_app: str = None, use_sudo: bool = False
    ) -> Tuple[bool, Path, str]:
        """
        Create a socket file for the given project

        Args:
            project_path: Path to the project directory
            project_name: Name of the project
            wsgi_app: WSGI application path (e.g., 'myproject.wsgi:application')
            use_sudo: Whether to use sudo for file operations

        Returns:
            Tuple of (success, service_file_path, socket_file_path)
        """
        return self._manager.create_socket_service(
            project_path, project_name, wsgi_app=wsgi_app, use_sudo=use_sudo
        )

    def reload_daemon(self) -> Tuple[bool, str]:
        """
        Reloads the systemd daemon to recognize new or changed service files
        
        Returns:
            Tuple of (success, message)
        """
        return self._manager.reload_daemon()
        
    def enable_socket_service(self, project_name: str) -> Tuple[bool, str]:
        """
        Enables the socket service for the given project to start on boot
        
        Args:
            project_name: Name of the project (used to identify the service)
        
        Returns:
            Tuple of (success, message)
        """
        return self._manager.enable_socket_service(project_name)

    def start_socket_service(self, project_name: str) -> Tuple[bool, str]:
        """
        Starts the socket service for the given project

        Args:
            project_name: Name of the project (used to identify the service)

        Returns:
            Tuple of (success, message)
        """
        return self._manager.start_socket_service(project_name)
        
    def launch_socket_service(self, project_name: str) -> Tuple[bool, str]:
        """
        Comprehensive function to launch a socket service:
        Checks if it exists, reloads daemon, enables, and starts it
        
        Args:
            project_name: Name of the project (used to identify the service)
        
        Returns:
            Tuple of (success, message)
        """
        return self._manager.launch_socket_service(project_name)
        
    def verify_run_gunicorn_directory(self) -> Tuple[bool, str]:
        """
        Verifies that the socket-related directories exist and have proper permissions.
        Creates them if needed.

        Returns:
            Tuple of (success, message)
        """
        return self._manager.verify_run_gunicorn_directory()