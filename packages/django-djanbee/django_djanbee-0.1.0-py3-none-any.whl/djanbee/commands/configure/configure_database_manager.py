from ...core import AppContainer
from .configure_database_display import ConfigureDatabaseDisplay
from pathlib import Path
from typing import Tuple, Optional


class ConfigureDatabaseManager:

    def __init__(self, display: ConfigureDatabaseDisplay, app: AppContainer):
        self.display = display
        self.app = app

    def configure_database(self, path: str) -> bool:
        """
        Main entry point for database configuration.

        Args:
            path: Project path

        Returns:
            bool: True if configuration was successful, False otherwise
        """
        self.display.show_lookup_database()

        # Ensure PostgreSQL is installed and running
        if not self._ensure_installation():
            return False

        if not self._ensure_service_running():
            return False

        self.display.success_database_running()

        # Handle user login/creation
        user = self._handle_user()
        if not user:
            return False

        self.display.success_login_user(user)

        # Handle database creation/connection
        return self._handle_database_create_or_connect()

    def _ensure_installation(self) -> bool:
        """Ensure PostgreSQL is installed, install if needed."""
        is_installed, location = self.app.database_manager.check_postgres_installation()

        if not is_installed:
            return self._handle_installation()
        self.display.success_database_installed(location)
        return True

    def _ensure_service_running(self) -> bool:
        """Ensure PostgreSQL service is running, start if needed."""
        is_running = self.app.database_manager.check_postgres_status()

        if not is_running:
            return self._handle_service_start()

        return True

    def _handle_installation(self) -> bool:
        """Handle PostgreSQL installation process."""
        self.display.error_database_installed()

        if not self.display.prompt_install_database():
            return False
        self.display.progress_install_database()
        try:
            if not self._run_installation():
                return False

            # Verify installation
            is_installed, location = (
                self.app.database_manager.check_postgres_installation()
            )
            if is_installed:
                self.display.success_database_installed(location)
                return True
            else:
                self.display.error_database_installed()
                return False

        except Exception as e:
            self.display.print_installation_failure(
                "Installation", f"Unexpected error: {e}"
            )
            return False

    def _run_installation(self) -> bool:
        """Run the actual installation process with progress reporting."""
        try:
            # Get installation generator
            installation = self.app.database_manager.install_postgres()

            # Process each installation step and show progress
            for step_name, success, message in installation:
                if success:
                    self.display.print_installation_progress(step_name, message)
                else:
                    self.display.print_installation_failure(step_name, message)
                    return False

            return True
        except Exception as e:
            self.display.print_installation_failure(
                "Installation", f"Installation error: {e}"
            )
            return False

    def _handle_service_start(self) -> bool:
        """Handle starting PostgreSQL service."""
        db_manager = self.app.database_manager

        # Show service not running error
        self.display.error_database_running()

        # Prompt to start service
        if not self.display.prompt_enable_database():
            return False

        # Try to start service
        success, message = db_manager.configure_postgres_service()
        if not success:
            self.display.error_database_running()
            self.display.console_manager.print_step_failure("Service", message)
            return False

        # Verify service is running
        is_running = db_manager.check_postgres_status()
        if not is_running:
            self.display.error_database_running()
            self.display.console_manager.print_step_failure(
                "Service", "Service enabled but not running"
            )

        return is_running

    def _handle_user(self):
        """Handle user creation or login."""
        user = self.app.os_manager.get_username()
        is_admin = self.app.os_manager.is_admin()
        db_manager = self.app.database_manager

        login = self.display.prompt_user_create_or_login(is_admin)
        if login is None:
            return False

        # Create user if requested
        if not login:
            success, message = db_manager.create_user(user)
            if not success:
                self.display.error_create_user(message)
                return False
            self.display.success_create_user(user)

        # Login with the user
        success, message = db_manager.login_user(user)
        if not success:
            self.display.error_login_user(message)
            return False

        return user

    def _handle_database_create_or_connect(self):
        """Handle database creation or connection."""
        db_manager = self.app.database_manager

        if self.display.prompt_database_create_or_connect():
            # Create new database
            db_name = self.display.input_database_name()
            success, message = db_manager.create_database(db_name)
            if not success:
                self.display.console_manager.print_step_failure(
                    "Database", f"Failed to create database: {message}"
                )
                return False
        else:
            # Connect to existing database
            success, databases = db_manager.get_all_databases()
            if not success:
                self.display.console_manager.print_step_failure(
                    "Database", f"Failed to get databases: {databases}"
                )
                return False

            database = self.display.prompt_select_database(databases)
            if not database:
                return False

            db_manager.db_name = database

        self.display.print_progress_database(db_manager.db_name)
        if self.display.prompt_set_default_config():
            
            self._update_database_configuration(db_manager.db_name)
        return True
    
    def _update_database_configuration(self, db_name):
        """Handle updating the database configuration in settings and grant permissions."""
        # Get current project path
        if not self.app.django_manager.project_service.state.current_project_path:
            project = self.app.django_manager.project_service.select_project()
        else:
            project = self.app.django_manager.project_service.state.current_project_path
        if not project:
            return False

        # Get the current user
        current_user = self.app.os_manager.get_username()
        
        # Setup permissions
        self.display.show_permissions_setup(current_user)
        
        # 1. Make user the database owner
        owner_success, _ = self.app.database_manager.execute_admin_command(
            f"ALTER DATABASE {db_name} OWNER TO {current_user};"
        )
        
        # 2. Grant schema permissions
        schema_cmd = f'sudo -u postgres psql -d {db_name} -c "GRANT ALL ON SCHEMA public TO {current_user}; ALTER SCHEMA public OWNER TO {current_user};"'
        schema_success = self.app.os_manager.run_command(schema_cmd)
        
        # Report permissions result
        if owner_success and schema_success.success:
            self.display.show_permissions_success()
        else:
            self.display.show_permissions_error()
        
        # Update configuration
        self.display.show_config_update()
        
        # Create peer authentication configuration
        db_config = {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": db_name,
            "USER": current_user,
            "PASSWORD": "",  # Empty for peer authentication
            "HOST": "",      # Empty for peer authentication
            "PORT": "",      # Empty for default port
        }
        
        # Wrap the updated database configuration
        updated_database_config = {"default": db_config}
        
        # Update the settings file
        success = self.app.django_manager.databases_handler.edit_database_settings(updated_database_config)
        
        # Report configuration result
        if success:
            self.display.show_config_success()
        else:
            self.display.show_config_error()
        
        return success

def grant_database_permissions(self, db_name, username):
    """Grant all necessary permissions for the user on the database."""
    # 1. Make user the database owner
    owner_success, _ = self.app.database_manager.execute_admin_command(
        f"ALTER DATABASE {db_name} OWNER TO {username};"
    )
    
    # 2. Grant schema permissions
    schema_cmd = f'sudo -u postgres psql -d {db_name} -c "GRANT ALL ON SCHEMA public TO {username}; ALTER SCHEMA public OWNER TO {username};"'
    schema_success, _ = self.app.os_manager.run_command(schema_cmd)
    
    return owner_success and schema_success

    def find_settings_file(self, project_path: Path) -> Tuple[bool, Optional[Path]]:
        """
        Find the settings file for a Django project.

        Args:
            project_path: Path to the Django project directory

        Returns:
            Tuple[bool, Optional[Path]]:
                - True and the path if settings file is found
                - False and None if settings file is not found
        """
        # Save the project path
        self.current_project_path = project_path

        # Common patterns for Django settings files
        settings_patterns = [
            # Standard Django layout: project_name/settings.py
            project_path / "settings.py",
            # Project with inner module: project_name/project_name/settings.py
            *[
                project_path / inner_dir.name / "settings.py"
                for inner_dir in project_path.iterdir()
                if inner_dir.is_dir() and not inner_dir.name.startswith(".")
            ],
            # Settings in config directory: project_name/config/settings.py
            project_path / "config" / "settings.py",
            # Settings as a package: project_name/settings/__init__.py
            project_path / "settings" / "__init__.py",
            # Common Django project layout with app name matching project folder
            project_path / project_path.name / "settings.py",
        ]

        # Check each pattern using a fast path-first approach
        for settings_path in settings_patterns:
            if settings_path.exists() and settings_path.is_file():
                return True, settings_path

        # If no common pattern matches, do a more targeted search with validation
        django_markers = ["DJANGO_SETTINGS_MODULE", "SECRET_KEY", "INSTALLED_APPS"]

        try:
            # Search for settings.py files with limited results
            for settings_file in list(project_path.glob("**/settings.py"))[:5]:
                # Only read files that might be Django settings
                content = settings_file.read_text(encoding="utf-8", errors="ignore")
                if any(marker in content for marker in django_markers):
                    return True, settings_file
        except Exception:
            # Handle potential errors during file reading
            pass

        # No settings file found
        return False, None
