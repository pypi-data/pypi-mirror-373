from dataclasses import dataclass

from .display import DeployDisplay
from .manager import DeployManager
from ...core import AppContainer


@dataclass
class DeployContainer:
    """Container for deployment-related components and operations."""

    display: DeployDisplay
    manager: DeployManager

    @classmethod
    def create(cls, app: AppContainer) -> "DeployContainer":
        """Factory method to create a configured DeployContainer instance."""
        display = DeployDisplay(console_manager=app.console_manager)
        manager = DeployManager(display=display, app=app)
        return cls(display=display, manager=manager)

    def verify_packages(self) -> bool:
        """Verify required packages are installed in the virtual environment."""
        return self.manager.verify_packages()

    def set_up_socket_file(self) -> bool:
        """Set up the socket file for the Django application."""            
        if self.manager.find_and_create_socket_file():
            return self.manager.launch_socketfile()
            
        return False

    def set_up_server(self) -> bool:
        """Set up the server configuration."""
        if self.manager.find_and_create_server_file():
            return self.manager.manage_nginx_configuration()
        return False