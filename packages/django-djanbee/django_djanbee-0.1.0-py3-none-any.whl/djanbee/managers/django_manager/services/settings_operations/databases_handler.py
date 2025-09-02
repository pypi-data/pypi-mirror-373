from ..settings_service import DjangoSettingsService
from .databases_handler_display import DatabasesHandlerDisplay
from ..venv_service import DjangoEnvironmentService
from .....managers import EnvManager


class DatabasesHandler:
    def __init__(
        self,
        settings_service: DjangoSettingsService,
        display: DatabasesHandlerDisplay,
        venv_service: DjangoEnvironmentService,
    ):
        self.settings_service = settings_service
        self.venv_service = venv_service
        self.display = display
        self.postgres_dependencies = ["psycopg2-binary"]
        # The env_manager will be accessed lazily when needed

    def handle_databases(self):
        """Main entry point for database configuration handling."""
        # Update database configuration
        if not self._update_database_configuration():
            return

        # Handle database dependencies
        self._handle_database_dependencies()

    def _update_database_configuration(self):
        """Handle updating the database configuration in settings."""
        database = self.settings_service.find_in_settings("DATABASES", default=[])
        default_db = database.get("default", {})

        # Create a copy without the OPTIONS field
        db_without_options = {k: v for k, v in default_db.items() if k != "OPTIONS"}

        updated_db = self.display.prompt_postgresql_edit(db_without_options)
        if not updated_db:
            return False

        # Wrap the updated database configuration in the "default" key
        updated_database_config = {"default": updated_db}

        # Update the settings file
        self.edit_database_settings(updated_database_config)

        # Confirm to the user
        self.display.success_database_updated()
        return True

    def _handle_database_dependencies(self):
        """Handle checking and installing database dependencies."""
        self.display.print_lookup_database_dependencies()

        venv_path = self._get_active_venv_path()
        if not venv_path:
            print("No active virtual environment detected")
            return

        self._check_and_install_dependencies(venv_path)

    def _get_active_venv_path(self):
        """Get the path to the active virtual environment."""
        if not self.venv_service.state.active_venv_path:
            self.venv_service.get_active_venv()
        return self.venv_service.state.active_venv_path

    def _check_and_install_dependencies(self, venv_path):
        """Check for and install missing PostgreSQL dependencies."""
        # Access the env_manager through the django_manager when needed
        env_manager = self._get_env_manager()

        if not env_manager:
            # Fallback to old method if env_manager not available
            all_installed, missing_packages = (
                self.settings_service.os_manager.check_postgres_dependencies(venv_path)
            )
        else:
            # Use env_manager to check PostgreSQL dependencies
            missing_packages = env_manager.get_missing_packages(
                venv_path, self.postgres_dependencies
            )
            all_installed = len(missing_packages) == 0

        if not all_installed:
            self._install_missing_dependencies(venv_path, missing_packages)
        else:
            self.display.print_database_dependencies_present()

    def _install_missing_dependencies(self, venv_path, missing_packages):
        """Prompt and install missing database dependencies."""
        result = self.display.prompt_install_database_dependencies(missing_packages)
        if result:
            self.display.print_progress_database_dependencies_install()

            env_manager = self._get_env_manager()
            if env_manager:
                # Use new method with env_manager
                success, message, _ = env_manager.ensure_dependencies(
                    venv_path, self.postgres_dependencies
                )
            else:
                # Fallback to old method
                success, message = (
                    self.settings_service.os_manager.ensure_postgres_dependencies(
                        venv_path
                    )
                )

            print(message)

    def _get_env_manager(self):
        """Safely get the env_manager, handling potential circular references"""
        try:
            if (
                hasattr(self.settings_service, "django_manager")
                and self.settings_service.django_manager
                and hasattr(self.settings_service.django_manager, "env_manager")
            ):
                return self.settings_service.django_manager.env_manager
        except Exception:
            # If any error occurs, return None to use fallback method
            pass
        return None

    def edit_database_settings(self, new_databases):
        """
        Update the DATABASES setting in the Django settings file

        Args:
            new_databases (dict): The new DATABASES configuration

        Returns:
            tuple: (bool success, str message)
        """
        # Validate that a default database is present
        if "default" not in new_databases:
            return False, "Error: The 'default' database configuration is required"

        settings_path = self.settings_service.find_settings_file()
        if not settings_path or not settings_path.exists():
            return False, "Error: Settings file not found"

        # Read the current content
        content = settings_path.read_text()

        # Format the new databases dictionary with proper indentation
        from pprint import pformat

        formatted_databases = pformat(new_databases, indent=4)

        # Find the DATABASES definition in the file
        import re

        # First look for the start of the DATABASES assignment
        start_match = re.search(r"DATABASES\s*=\s*{", content)
        if not start_match:
            # DATABASES not found, append it to the end of the file
            new_content = (
                f"{content}\n\n# Added by Djanbee\nDATABASES = {formatted_databases}\n"
            )
            settings_path.write_text(new_content)
            return True, "DATABASES setting added successfully"

        # Find the entire DATABASES block by tracking braces
        start_pos = start_match.start()
        brace_count = 0
        end_pos = -1

        # Skip to the first opening brace
        first_brace_pos = content.find("{", start_pos)
        if first_brace_pos == -1:
            return False, "Error: Malformed DATABASES setting"

        # Count braces to find the matching closing brace
        for i in range(first_brace_pos, len(content)):
            char = content[i]
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i + 1
                    break

        if end_pos == -1:
            return False, "Error: Could not find the end of DATABASES definition"

        # Replace the entire DATABASES block with the new configuration
        new_content = (
            content[:start_pos]
            + f"DATABASES = {str(formatted_databases)}"
            + content[end_pos:]
        )

        # Write the updated content back to the file
        settings_path.write_text(new_content)
        return True, "DATABASES setting updated successfully"
