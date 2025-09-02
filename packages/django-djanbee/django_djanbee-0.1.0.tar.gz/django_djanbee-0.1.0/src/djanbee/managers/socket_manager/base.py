from abc import ABC, abstractmethod
from pathlib import Path
from typing import Tuple, Optional


class BaseSocketManager(ABC):
    """
    Abstract base class for socket managers used in web server deployments
    """

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass
        
    @abstractmethod
    def verify_run_gunicorn_directory(self) -> Tuple[bool, str]:
        """
        Verifies that the socket-related directories exist and have proper permissions.
        Creates them if needed.

        Returns:
            Tuple of (success, message)
        """
        pass
        
    @abstractmethod
    def reload_daemon(self) -> Tuple[bool, str]:
        """
        Reloads the systemd daemon to recognize new or changed service files
        
        Returns:
            Tuple of (success, message)
        """
        pass
        
    @abstractmethod
    def enable_socket_service(self, project_name: str) -> Tuple[bool, str]:
        """
        Enables the socket service for the given project to start on boot
        
        Args:
            project_name: Name of the project (used to identify the service)
        
        Returns:
            Tuple of (success, message)
        """
        pass
        
    @abstractmethod
    def start_socket_service(self, project_name: str) -> Tuple[bool, str]:
        """
        Starts the socket service for the given project
        
        Args:
            project_name: Name of the project (used to identify the service)
        
        Returns:
            Tuple of (success, message)
        """
        pass
        
    @abstractmethod
    def launch_socket_service(self, project_name: str) -> Tuple[bool, str]:
        """
        Comprehensive function to launch a socket service:
        Checks if it exists, reloads daemon, enables, and starts it
        
        Args:
            project_name: Name of the project (used to identify the service)
        
        Returns:
            Tuple of (success, message)
        """
        pass