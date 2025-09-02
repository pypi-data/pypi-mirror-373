from ..os_manager import OSManager
from ..console_manager import ConsoleManager
from ..dotenv_manager import DotenvManager
from .services.venv_service import DjangoEnvironmentService
from .services.project_service import DjangoProjectService
from .services.project_service_display import DjangoProjectServiceDisplay
from .services.requirements_service import DjangoRequirementsService
from .services.requirements_service_display import DjangoRequirementsServiceDisplay
from .services.venv_service_display import DjangoEnvironmentServiceDisplay
from .services.settings_service import DjangoSettingsService
from .services.settings_service_display import DjangoSettingsServiceDisplay
from .services.settings_operations.secret_key_handler import (
    SecretKeyHandler,
    SecretKeyHandlerDisplay,
)
from .services.settings_operations.allowed_hosts_handler import (
    AllowedHostsHandler,
    AllowedHostsHandlerDisplay,
)

from .services.settings_operations.databases_handler import (
    DatabasesHandler,
    DatabasesHandlerDisplay,
)
from .services.settings_operations.static_files import (
    StaticRootHandler,
    StaticRootHandlerDisplay,
)

from .services.settings_operations.ssl import SslHandler, SslHandlerDisplay
from .services.settings_operations.debug_handler import DebugHandler
from .services.settings_operations.debug_handler_display import DebugHandlerDisplay
from .state import DjangoManagerState


class DjangoManager:
    """Container for Django-related services with lazy loading"""

    def __init__(self, os_manager: OSManager, console_manager: ConsoleManager, env_manager=None, dotenv_manager=None):
        """Initialize the Django manager with dependencies but not services"""
        self.os_manager = os_manager
        self.console_manager = console_manager
        self.env_manager = env_manager
        self.dotenv_manager = dotenv_manager

        # Initialize service placeholders
        self._project_service = None
        self._environment_service = None
        self._requirements_service = None
        self._settings_service = None

        self._secret_key_handler = None
        self._allowed_hosts_handler = None
        self._databases_handler = None
        self._static_root_handler = None
        self._ssl_handler = None
        self._debug_handler = None

        # Cache values TODO REMOVE THIS
        self._current_project_path = None

    @property
    def state(self):
        """
        Get the current state from DjangoManagerState singleton

        Returns:
            The DjangoManagerState instance with the freshest data
        """

        return DjangoManagerState.get_instance()

    @property
    def project_service(self):
        """Lazy load the project service when first accessed"""
        if self._project_service is None:
            self._project_service = DjangoProjectService(
                self.os_manager, DjangoProjectServiceDisplay(self.console_manager)
            )
        return self._project_service

    @property
    def environment_service(self):
        """Lazy load the project service when first accessed"""
        if self._environment_service is None:
            self._environment_service = DjangoEnvironmentService(
                self.os_manager, DjangoEnvironmentServiceDisplay(self.console_manager)
            )
        return self._environment_service

    @property
    def requirements_service(self):
        """Lazy load the project service when first accessed"""
        if self._requirements_service is None:
            self._requirements_service = DjangoRequirementsService(
                self.os_manager,
                DjangoRequirementsServiceDisplay(self.console_manager),
            )
        return self._requirements_service

    @property
    def settings_service(self):
        """Lazy load the settings service when first accessed"""
        if self._settings_service is None:
            # Create the settings service
            self._settings_service = DjangoSettingsService(
                self.os_manager, DjangoSettingsServiceDisplay(self.console_manager)
            )
            # Set a reference to self to avoid circular import issues
            self._settings_service.django_manager = self
        return self._settings_service

    @property
    def secret_key_handler(self):
        """Lazy load the secret key handler"""
        if self._secret_key_handler is None:
            self._secret_key_handler = SecretKeyHandler(
                self.settings_service, 
                SecretKeyHandlerDisplay(self.console_manager),
                self.dotenv_manager
            )
        return self._secret_key_handler

    @property
    def allowed_hosts_handler(self):
        if self._allowed_hosts_handler is None:
            self._allowed_hosts_handler = AllowedHostsHandler(
                self.settings_service, AllowedHostsHandlerDisplay(self.console_manager)
            )
        return self._allowed_hosts_handler

    @property
    def databases_handler(self):
        if self._databases_handler is None:
            self._databases_handler = DatabasesHandler(
                self.settings_service,
                DatabasesHandlerDisplay(self.console_manager),
                self.environment_service,
            )
        return self._databases_handler

    @property
    def static_root_handler(self):
        if self._static_root_handler is None:
            self._static_root_handler = StaticRootHandler(
                self.settings_service,
                StaticRootHandlerDisplay(self.console_manager),
                self.environment_service,
            )
        return self._static_root_handler

    @property
    def ssl_handler(self):
        if self._ssl_handler is None:
            self._ssl_handler = SslHandler(
                self.settings_service,
                SslHandlerDisplay(self.console_manager),
            )
        return self._ssl_handler

    @property
    def debug_handler(self):
        if self._debug_handler is None:
            self._debug_handler = DebugHandler(
                self.settings_service,
                DebugHandlerDisplay(self.console_manager),
            )
        return self._debug_handler
