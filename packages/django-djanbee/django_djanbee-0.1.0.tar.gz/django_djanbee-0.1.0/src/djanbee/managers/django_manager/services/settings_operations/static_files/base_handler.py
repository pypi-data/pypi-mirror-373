from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Tuple, Optional

from ...settings_service import DjangoSettingsService
from .static_root_handler_display import StaticRootHandlerDisplay
from ...venv_service import DjangoEnvironmentService


class StaticFilesHandler(ABC):
    """Base class for static files handlers (WhiteNoise, Nginx, Apache, etc.)"""

    def __init__(
        self,
        settings_service: DjangoSettingsService,
        display: StaticRootHandlerDisplay,
        venv_service: DjangoEnvironmentService,
    ):
        self.settings_service = settings_service
        self.display = display
        self.venv_service = venv_service

    @abstractmethod
    def handle(self) -> bool:
        """Handle the setup of static files using the specific strategy
        
        Returns:
            bool: True if setup was successful, False otherwise
        """
        pass

    def setup_static_url(self, url: str = "/static/") -> bool:
        """Configure STATIC_URL setting
        
        Args:
            url: The URL to serve static files from
            
        Returns:
            bool: True if successful, False otherwise
        """
        static_url = self.settings_service.find_in_settings("STATIC_URL")
        if static_url != url:
            self.display.print_progress_static_url()
            result = self.settings_service.edit_settings("STATIC_URL", url)
            if not result:
                return False
        self.display.success_progress_static_url(url)
        return True

    def setup_static_root(self, path: str = "os.path.join(BASE_DIR, 'staticfiles')") -> bool:
        """Configure STATIC_ROOT setting
        
        Args:
            path: The path expression for collecting static files
            
        Returns:
            bool: True if successful, False otherwise
        """
        static_root = self.settings_service.find_in_settings("STATIC_ROOT")
        if not static_root:
            self.display.print_progress_static_root()
            has_os = self.settings_service.is_library_imported("os")
            if not has_os:
                self.settings_service.add_library_import("os")
                self.display.print_progress_static_root_add_os()
            
            result = self.settings_service.replace_settings("STATIC_ROOT", path)
            if not result[0]:
                return False
        self.display.success_progress_static_root()
        return True

    def setup_staticfiles_dirs(self,name, default_path: str = "os.path.join(BASE_DIR, 'static')") -> bool:
        """Configure STATICFILES_DIRS setting
        
        Args:
            default_path: The default path expression to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        staticfiles_dirs = self.get_raw_staticfiles_dirs()
        if not staticfiles_dirs:
            # STATICFILES_DIRS doesn't exist or is empty
            self.display.print_progress_static_file_dirs_create()
            result = self.settings_service.replace_settings(
                "STATICFILES_DIRS", f"[{default_path}]"
            )
            if not result[0]:
                return False
        else:
            # Check if our expression is already in the list
            # Look for the exact expression or similar ones (may have different spacing)
            has_path = any(
                "os.path.join(BASE_DIR" in expr and "'static'" in expr
                for expr in staticfiles_dirs
            )

            if not has_path:
                # Add our path to the list
                staticfiles_dirs.append(default_path)

                # Format the list correctly for the settings file
                formatted_list = (
                    "[\n    " + ",\n    ".join(staticfiles_dirs) + "\n]"
                )

                # Update the setting
                result = self.settings_service.replace_settings(
                    "STATICFILES_DIRS", formatted_list
                )
                if not result[0]:
                    return False
        
        self.display.success_progress_static_file_dirs_add(name)
        return True

    def get_raw_staticfiles_dirs(self) -> List[str]:
        """
        Get the raw STATICFILES_DIRS expressions from the settings file,
        correctly handling nested parentheses.

        Returns:
            list: List of raw expressions in the STATICFILES_DIRS setting,
                or empty list if the setting doesn't exist
        """
        # Use the settings service to read the file
        success, content, _ = self.settings_service._read_settings_file()
        if not success:
            return []

        try:
            # Find the STATICFILES_DIRS declaration
            import re

            pattern = r"STATICFILES_DIRS\s*=\s*\[(.*?)\]"
            match = re.search(pattern, content, re.DOTALL)

            if not match:
                return []

            # Get the content inside the brackets
            raw_content = match.group(1).strip()

            if not raw_content:
                return []

            # Split by commas, respecting nested parentheses and brackets
            expressions = []
            current_expr = ""
            paren_level = 0
            bracket_level = 0

            for char in raw_content:
                if char == "," and paren_level == 0 and bracket_level == 0:
                    # Only split on commas at the top level
                    if current_expr.strip():
                        expressions.append(current_expr.strip())
                    current_expr = ""
                else:
                    current_expr += char
                    if char == "(":
                        paren_level += 1
                    elif char == ")":
                        paren_level -= 1
                    elif char == "[":
                        bracket_level += 1
                    elif char == "]":
                        bracket_level -= 1

            # Add the last expression if there is one
            if current_expr.strip():
                expressions.append(current_expr.strip())

            return expressions

        except Exception as e:
            print(f"Error getting raw STATICFILES_DIRS: {e}")
            return []