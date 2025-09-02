from pathlib import Path
from typing import Tuple, List, Optional, Union, cast

from djanbee.managers.env_manager import EnvManager
from .base_handler import StaticFilesHandler
from ...settings_service import DjangoSettingsService
from .static_root_handler_display import StaticRootHandlerDisplay
from ...venv_service import DjangoEnvironmentService


class WhiteNoiseHandler(StaticFilesHandler):
    """Handler for configuring WhiteNoise static files in Django"""

    def __init__(
        self,
        settings_service: DjangoSettingsService,
        display: StaticRootHandlerDisplay,
        venv_service: DjangoEnvironmentService,
        env_manager: Optional[EnvManager] = None,
    ) -> None:
        """
        Initialize the WhiteNoise handler

        Args:
            settings_service: Service for managing Django settings
            display: Display service for user interaction
            venv_service: Service for virtual environment operations
            env_manager: Optional EnvManager for dependency management
        """
        self.settings_service = settings_service
        self.display = display
        self.venv_service = venv_service
        self.env_manager = env_manager

    def handle(self) -> bool:
        """
        Configure Django settings for WhiteNoise static files handling

        Returns:
            bool: True if setup was successful, False otherwise
        """
        # Get the active virtual environment
        if not self.venv_service.state.active_venv_path:
            self.venv_service.get_active_venv()

        active_venv = self.venv_service.state.active_venv_path
        if not active_venv:
            print("No active virtual environment detected")
            return False

        venv_path = active_venv

        # Install WhiteNoise if needed
        is_installed, message = self.check_whitenoise_installed(venv_path)
        if not is_installed:
            result = self.display.prompt_install_whitenoise()
            if result:
                success, message = self.install_whitenoise(venv_path)
                if not success:
                    print(message)
                    return False
            else:
                return False

        # Configure middleware
        if not self.configure_whitenoise_middleware():
            return False

        # Configure basic static file settings using parent class methods
        if not super().setup_static_url():
            return False

        if not super().setup_static_root():
            return False

        if not super().setup_staticfiles_dirs("Whitenoise"):
            return False

        # Configure WhiteNoise storage backend
        if not self.configure_storage_backend():
            return False

        return True

    def configure_whitenoise_middleware(self) -> bool:
        """
        Configure Django middleware for WhiteNoise

        Returns:
            bool: True if successful, False otherwise
        """
        middleware = self.settings_service.find_in_settings("MIDDLEWARE", default=[])

        # Cast to ensure type checker knows this is a list
        middleware_list = cast(
            List[str], middleware if isinstance(middleware, list) else []
        )

        is_whitenoise = self.is_whitenoise_properly_configured(middleware_list)
        if not is_whitenoise:
            middleware_list = self.setup_whitenoise_middleware(middleware_list)
            self.display.print_progress_whitenoise()
            result = self.settings_service.edit_middleware_settings(middleware_list)
            if not isinstance(result, tuple) or not result[0]:
                return False
        self.display.success_progress_whitenoise()
        return True

    def configure_storage_backend(self) -> bool:
        """
        Configure WhiteNoise storage backend

        Returns:
            bool: True if successful, False otherwise
        """
        staticfiles_storage = self.settings_service.find_in_settings(
            "STATICFILES_STORAGE", default=""
        )
        if (
            staticfiles_storage
            != "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ):
            self.display.progress_staticfiles_storage_add()
            result = self.settings_service.edit_settings(
                "STATICFILES_STORAGE",
                "whitenoise.storage.CompressedManifestStaticFilesStorage",
            )
            success = result[0] if isinstance(result, tuple) else result
            if not success:
                return False
        self.display.success_staticfiles_storage_add()
        return True

    def is_whitenoise_properly_configured(self, middleware_list: List[str]) -> bool:
        """
        Check if WhiteNoise middleware is present and properly placed after
        SecurityMiddleware in the MIDDLEWARE setting.

        Args:
            middleware_list: List of middleware from settings

        Returns:
            bool: True if WhiteNoise middleware is present and properly placed, False otherwise
        """
        # Check if middleware_list is empty
        if not middleware_list:
            return False

        # The exact strings to look for
        security_middleware = "django.middleware.security.SecurityMiddleware"
        whitenoise_middleware = "whitenoise.middleware.WhiteNoiseMiddleware"

        # Check if both middlewares are in the list
        if (
            security_middleware not in middleware_list
            or whitenoise_middleware not in middleware_list
        ):
            return False

        # Check their relative positions
        security_index = middleware_list.index(security_middleware)
        whitenoise_index = middleware_list.index(whitenoise_middleware)

        # WhiteNoise should come directly after SecurityMiddleware
        return whitenoise_index == security_index + 1

    def setup_whitenoise_middleware(self, middleware_list: List[str]) -> List[str]:
        """
        Configure the middleware list to include WhiteNoise in the correct position
        (immediately after SecurityMiddleware).

        Args:
            middleware_list: List of middleware from settings

        Returns:
            list: Updated middleware list with WhiteNoise properly positioned
        """
        if not middleware_list:
            # If middleware_list is empty, create a list with the basic middlewares
            return [
                "django.middleware.security.SecurityMiddleware",
                "whitenoise.middleware.WhiteNoiseMiddleware",
                # Add other essential middlewares
                "django.contrib.sessions.middleware.SessionMiddleware",
                "django.middleware.common.CommonMiddleware",
                "django.middleware.csrf.CsrfViewMiddleware",
                "django.contrib.auth.middleware.AuthenticationMiddleware",
                "django.contrib.messages.middleware.MessageMiddleware",
                "django.middleware.clickjacking.XFrameOptionsMiddleware",
            ]

        # The middlewares we're working with
        security_middleware = "django.middleware.security.SecurityMiddleware"
        whitenoise_middleware = "whitenoise.middleware.WhiteNoiseMiddleware"

        # Create a copy to avoid modifying the original
        new_middleware_list = middleware_list.copy()

        # Remove WhiteNoise if it's already in the list (to reposition it)
        if whitenoise_middleware in new_middleware_list:
            new_middleware_list.remove(whitenoise_middleware)

        # If SecurityMiddleware exists, insert WhiteNoise after it
        if security_middleware in new_middleware_list:
            security_index = new_middleware_list.index(security_middleware)
            new_middleware_list.insert(security_index + 1, whitenoise_middleware)
        else:
            # If SecurityMiddleware doesn't exist, add both at the beginning
            new_middleware_list.insert(0, whitenoise_middleware)
            new_middleware_list.insert(0, security_middleware)

        return new_middleware_list

    def check_whitenoise_installed(
        self, venv_path: Union[str, Path]
    ) -> Tuple[bool, str]:
        """
        Check if WhiteNoise is installed in the virtual environment.

        Args:
            venv_path: Path to the virtual environment

        Returns:
            Tuple of (is_installed: bool, message: str)
        """
        is_installed, message = (
            self.settings_service.os_manager.check_python_package_installed(
                venv_path, "whitenoise"
            )
        )

        return is_installed, message

    def install_whitenoise(self, venv_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        Install WhiteNoise in the virtual environment if not already installed.
        Uses the EnvManager for dependency management when available.

        Args:
            venv_path: Path to the virtual environment

        Returns:
            Tuple of (success: bool, message: str)
        """
        # Check if already installed
        is_installed, _ = self.check_whitenoise_installed(venv_path)
        if is_installed:
            return True, "WhiteNoise is already installed"

        # Use env_manager if available
        if self.env_manager:
            # Use env_manager to handle installation with proper prompts
            success, message, _ = self.env_manager.ensure_dependencies(
                venv_path,
                ["whitenoise"],
                "Install WhiteNoise for static files handling?",
            )
            return success, message

        # Fallback to direct pip installation
        pip_path = self.settings_service.os_manager.get_pip_path(Path(venv_path))
        try:
            # Show progress message
            self.display.console_manager.print_progress("Installing WhiteNoise...")

            result = self.settings_service.os_manager.run_command(
                [str(pip_path), "install", "whitenoise"]
            )
            if result.success:
                self.display.console_manager.print_success("WhiteNoise installed successfully")
                return True, "WhiteNoise installed successfully"
            else:
                self.display.console_manager.print_error(f"Failed to install WhiteNoise: {result.stderr}")
                return False, f"Failed to install WhiteNoise: {result.stderr}"
        except Exception as e:
            error_msg = f"Error installing WhiteNoise: {str(e)}"
            self.display.console_manager.print_error(error_msg)
            return False, error_msg
