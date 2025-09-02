from pathlib import Path
from ..settings_service import DjangoSettingsService
from .secret_key_handler_display import SecretKeyHandlerDisplay
from ....dotenv_manager import DotenvManager


class SecretKeyHandler:
    """Handler for Django secret key operations"""

    def __init__(
        self, 
        settings_service: DjangoSettingsService, 
        display: SecretKeyHandlerDisplay,
        dotenv_manager: DotenvManager = None
    ):
        self.settings_service = settings_service
        self.display = display
        self.dotenv_manager = dotenv_manager

    def create_secret_key(self):
        self.display.progress_generate_secret_key()
        secret_key = self.generate_secret_key()
        self.display.success_generate_secret_key(secret_key)
        return secret_key

    def update_secret_key(self, secret_key: str):
        """Update the secret key using dotenv if available"""
        # First check for dotenv_manager
        if not self.dotenv_manager:
            # Fall back to old behavior if dotenv_manager not available
            old_key = self.settings_service.find_in_settings("SECRET_KEY")
            self.display.progress_set_secret_key(secret_key, old_key)
            self.settings_service.edit_settings("SECRET_KEY", secret_key)
            self.display.success_set_secret_key()
            return
        
        # Look for .env file in the project root
        project_path = self.settings_service.state.current_project_path
        if not project_path:
            self.display.console_manager.print_warning("Project path not found, cannot locate .env file")
            return
            
        # Look for any existing .env files
        env_files = self.dotenv_manager.find_env_files(project_path)
        
        # If no .env file exists, create one at the project root
        env_file_path = None
        if not env_files:
            self.display.console_manager.print_warning("No .env file found in project")
            self.display.console_manager.print_progress("Creating new .env file")
            env_file_path = project_path / ".env"
            success, message = self.dotenv_manager.create_env_file(env_file_path)
            if not success:
                self.display.console_manager.print_error(f"Failed to create .env file: {message}")
                return
        else:
            # Use the first .env file found
            env_file_path = env_files[0]
            self.display.console_manager.print_info(f"Using existing .env file at {env_file_path}")
            
        # Check if SECRET_KEY already exists in .env
        success, message, env_vars = self.dotenv_manager.read_env_file(env_file_path)
        if not success:
            self.display.console_manager.print_error(f"Failed to read .env file: {message}")
            return
            
        # Update or add SECRET_KEY in .env file
        self.display.console_manager.print_progress(f"Setting SECRET_KEY in {env_file_path}")
        success, message = self.dotenv_manager.update_env_variable(env_file_path, "SECRET_KEY", secret_key)
        if not success:
            self.display.console_manager.print_error(f"Failed to update SECRET_KEY in .env file: {message}")
            return
            
        # Update settings.py to use env variable
        old_key = self.settings_service.find_in_settings("SECRET_KEY")
        self.display.progress_set_secret_key("os.environ.get('SECRET_KEY')", old_key)
        
        # Check if settings file already imports os
        if not self.settings_service.is_library_imported("os"):
            self.settings_service.add_library_import("os")
            
        # Check if settings file already imports dotenv
        if not self.settings_service.is_library_imported("dotenv"):
            self.settings_service.add_library_import("dotenv", import_from="dotenv", import_what=["load_dotenv"])
            
        # Add code to load .env file
        dotenv_code = (
            "# Load environment variables from .env file\n"
            "load_dotenv()\n\n"
        )
        
        # Get settings content to determine the best place to insert the dotenv loading code
        success, content, settings_path = self.settings_service._read_settings_file()
        if success:
            # Check if dotenv loading already exists
            if "load_dotenv()" not in content:
                # Find position after imports but before variables
                lines = content.split("\n")
                import_end_index = 0
                for i, line in enumerate(lines):
                    line = line.strip()
                    if (line and not line.startswith("#") and 
                        not line.startswith("import") and 
                        not line.startswith("from")):
                        import_end_index = i
                        break
                
                # Insert dotenv loading code after imports
                if import_end_index > 0:
                    new_lines = lines[:import_end_index] + [dotenv_code] + lines[import_end_index:]
                    new_content = "\n".join(new_lines)
                    self.settings_service._write_settings_file(settings_path, new_content)
        
        # Update SECRET_KEY in settings to use environment variable
        success = self.settings_service.replace_settings("SECRET_KEY", "os.environ.get('SECRET_KEY')")
        if success:
            self.display.success_set_secret_key()
            self.display.console_manager.print_success("SECRET_KEY now loaded from environment variable")
        else:
            self.display.console_manager.print_error("Failed to update SECRET_KEY in settings.py to use environment variable")

    def generate_secret_key(self) -> str:
        """
        Generate a new Django-compatible secret key without depending on Django

        Returns:
            str: A new secure secret key suitable for Django
        """
        import secrets
        import string

        # Characters to use in the secret key - matching Django's pattern
        chars = string.ascii_letters + string.digits + "!@#$%^&*(-_=+)"

        # Generate a 50-character random string
        secret_key = "".join(secrets.choice(chars) for _ in range(50))

        return secret_key
