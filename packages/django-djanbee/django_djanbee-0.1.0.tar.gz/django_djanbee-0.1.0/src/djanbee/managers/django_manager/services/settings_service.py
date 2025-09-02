from pathlib import Path
from ....managers.os_manager import OSManager
from ..state import DjangoManagerState
from collections import namedtuple
import re
from .settings_service_display import DjangoSettingsServiceDisplay

Result = namedtuple("Result", ["valid", "object"])


class DjangoSettingsService:
    """Service for managing Django settings"""

    def __init__(
        self,
        os_manager: OSManager,
        display: DjangoSettingsServiceDisplay,
        django_manager=None,
    ):
        self.os_manager = os_manager
        self.state = DjangoManagerState.get_instance()
        self.display = display
        # The django_manager attribute will be set after initialization by the DjangoManager itself
        # to avoid circular references. It's default None here but will be populated later
        self.django_manager = django_manager

    def find_settings(self):
        self.display.print_lookup_settings()
        settings_file = self.find_settings_file()
        if not settings_file:
            self.display.error_found_settings()
            return None
        self.display.success_found_settings(settings_file)
        return True, settings_file

    def get_settings_path(self):
        """
        Get the settings path, using cached value if available or finding it if not.

        Returns:
            Path: Path to the settings.py file or None if not found
        """
        if self.state.settings_path and self.state.settings_path.exists():
            return self.state.settings_path

        result, self.state.settings_path = self.find_settings()
        return self.state.settings_path

    def find_settings_file(self) -> Path:
        """Find the settings.py file in the Django project

        Returns:
            Path: Path to the settings.py file or None if not found
        """
        if not self.state.current_project_path:
            return None

        # Common patterns for settings file locations
        possible_locations = [
            # Standard Django project structure
            self.state.current_project_path
            / self.state.current_project_path.name
            / "settings.py",
            # Another common pattern (project/settings.py)
            self.state.current_project_path / "settings.py",
            # Project with config directory
            self.state.current_project_path / "config" / "settings.py",
            # Multiple settings files pattern
            self.state.current_project_path
            / self.state.current_project_path.name
            / "settings"
            / "base.py",
            self.state.current_project_path / "settings" / "base.py",
            self.state.current_project_path / "config" / "settings" / "base.py",
        ]

        # Check for settings module indicated in manage.py
        manage_path = self.state.current_project_path / "manage.py"
        if manage_path.exists():
            content = manage_path.read_text()

            # Look for DJANGO_SETTINGS_MODULE pattern
            settings_module_match = re.search(
                r'DJANGO_SETTINGS_MODULE["\']?\s*,\s*["\']([^"\']+)["\']', content
            )
            if settings_module_match:
                module_path = settings_module_match.group(1)
                # Convert module path (e.g. 'myproject.settings') to file path
                parts = module_path.split(".")
                file_path = self.state.current_project_path
                for part in parts[
                    :-1
                ]:  # All except the last part (which is the filename)
                    file_path = file_path / part
                file_path = file_path / f"{parts[-1]}.py"
                possible_locations.insert(0, file_path)  # Prioritize this path

        # Check each location
        for location in possible_locations:
            if location.exists() and location.is_file():
                self.state.settings_path = location
                return location

        # Search recursively as a fallback
        for path in self.state.current_project_path.rglob("settings.py"):
            self.state.settings_path = path
            return path

        return None

    def _read_settings_file(self):
        """Utility method to read settings file content

        Returns:
            tuple: (bool success, str content or error message, Path settings_path)
        """
        settings_path = self.get_settings_path()
        if not settings_path or not settings_path.exists():
            return False, "Settings file not found", None

        try:
            content = settings_path.read_text()
            return True, content, settings_path
        except Exception as e:
            return False, f"Error reading settings file: {str(e)}", None

    def _write_settings_file(self, settings_path, content):
        """Utility method to write settings file content

        Returns:
            tuple: (bool success, str message)
        """
        try:
            settings_path.write_text(content)
            return True, "Settings updated successfully"
        except Exception as e:
            return False, f"Error writing settings file: {str(e)}"

    def find_in_settings(self, setting_name, default=None):
        """
        Find a specific setting in the Django settings file

        Args:
            setting_name (str): The name of the setting to find (e.g., 'SECRET_KEY', 'ALLOWED_HOSTS', 'DATABASES')
            default: The default value to return if the setting is not found

        Returns:
            The value of the setting if found, or the default value if not found
        """
        settings_path = self.get_settings_path()
        if not settings_path:
            return default

        # Create a temporary module to execute the settings file
        import importlib.util
        import sys

        # Create a temporary module name
        temp_module_name = f"_temp_settings_{hash(str(settings_path))}"

        try:
            # Create a new module spec
            spec = importlib.util.spec_from_file_location(
                temp_module_name, settings_path
            )
            if spec is None:
                return default

            # Create the module
            module = importlib.util.module_from_spec(spec)

            # Add the module to sys.modules
            sys.modules[temp_module_name] = module

            # Execute the module
            spec.loader.exec_module(module)

            # Try to get the setting
            return getattr(module, setting_name, default)
        except Exception as e:
            print(f"Error loading setting {setting_name}: {e}")
            return default
        finally:
            # Clean up
            if temp_module_name in sys.modules:
                del sys.modules[temp_module_name]

    def edit_settings(self, setting_name, new_value):
        """
        Update a specific setting in the Django settings file

        Args:
            setting_name (str): The name of the setting to update (e.g., 'SECRET_KEY', 'ALLOWED_HOSTS')
            new_value: The new value to set for the setting

        Returns:
            bool or tuple: True if the setting was successfully updated or (True, "success message"),
                          False or (False, "error message") otherwise
        """
        success, content, settings_path = self._read_settings_file()
        if not success:
            return False if isinstance(content, bool) else (False, content)

        # Prepare the string representation of the new value
        if isinstance(new_value, str):
            # For strings, ensure quotes are used
            value_str = f"'{new_value}'"
        elif new_value is None:
            value_str = "None"
        else:
            # For other types, use repr to get a string representation
            value_str = repr(new_value)

        # Check for different patterns and update appropriately
        updated = False
        new_content = content

        # Pattern for simple assignments: SETTING_NAME = value
        simple_pattern = rf"({setting_name}\s*=\s*)([^#\n]+)"
        simple_match = re.search(simple_pattern, content)

        if simple_match:
            # Preserve the assignment part (SETTING_NAME =) and replace the value part
            prefix = simple_match.group(1)
            new_content = re.sub(simple_pattern, f"{prefix}{value_str}", content)
            updated = True
        else:
            # Pattern for settings inside dictionaries
            dict_pattern = rf"(['\"]?{setting_name}['\"]?\s*:\s*)([^,}}]+)"
            dict_match = re.search(dict_pattern, content)

            if dict_match:
                prefix = dict_match.group(1)
                new_content = re.sub(dict_pattern, f"{prefix}{value_str}", content)
                updated = True
            else:
                # Pattern for commented settings
                commented_pattern = rf"(#\s*{setting_name}\s*=\s*)([^#\n]+)"
                commented_match = re.search(commented_pattern, content)

                if commented_match:
                    # Uncomment the setting and update its value
                    prefix = commented_match.group(1).lstrip("#").lstrip()
                    new_content = re.sub(
                        commented_pattern, f"{prefix}{value_str}", content
                    )
                    updated = True
                else:
                    # Setting not found, append it to the end of the file
                    new_content = f"{content}\n\n# Added by Djanbee\n{setting_name} = {value_str}\n"
                    updated = True

        # Write the updated content back to the file
        if updated:
            success, message = self._write_settings_file(settings_path, new_content)
            return success if isinstance(success, bool) else (success, message)

        return False

    def replace_settings(self, setting_name, new_value_raw):
        """
        Replace a setting in the Django settings file by directly modifying the text.
        This is useful for settings that include raw Python expressions (like os.path.join).

        Args:
            setting_name (str): The name of the setting to replace (e.g., 'STATIC_ROOT')
            new_value_raw (str): The raw value to set (e.g., "os.path.join(BASE_DIR, 'staticfiles')")

        Returns:
            tuple: (bool success, str message)
        """
        success, content, settings_path = self._read_settings_file()
        if not success:
            return False, content

        try:
            # Pattern for finding the entire setting line or block
            pattern = rf"{setting_name}\s*=\s*[^\n]+"

            if re.search(pattern, content):
                # Replace existing setting
                new_content = re.sub(
                    pattern, f"{setting_name} = {new_value_raw}", content
                )
                return self._write_settings_file(settings_path, new_content)
            else:
                # Setting not found, append it to the end of the file
                new_content = f"{content}\n\n# Added by Djanbee\n{setting_name} = {new_value_raw}\n"
                return self._write_settings_file(settings_path, new_content)

        except Exception as e:
            return False, f"Error replacing setting {setting_name}: {str(e)}"

    def is_library_imported(self, library_name):
        """
        Check if a library is imported in the Django settings file.

        Args:
            library_name (str): The name of the library to check for (e.g., 'os', 'whitenoise')

        Returns:
            bool: True if the library is imported, False otherwise
        """
        success, content, _ = self._read_settings_file()
        if not success:
            return False

        try:
            # Define patterns for different import styles
            import_patterns = [
                rf"import\s+{library_name}",  # import os
                rf"from\s+{library_name}\s+import",  # from os import path
                rf"import\s+.*,\s*{library_name}",  # import sys, os
                rf"import\s+{library_name}\s+as",  # import os as operating_system
            ]

            # Check if any pattern matches
            for pattern in import_patterns:
                if re.search(pattern, content):
                    return True

            return False

        except Exception as e:
            print(f"Error checking for library import: {e}")
            return False

    def add_library_import(
        self, library_name, import_from=None, import_as=None, import_what=None
    ):
        """
        Add a library import to the Django settings file if it's not already present.

        Args:
            library_name (str): The name of the library to import (e.g., 'os', 'whitenoise')
            import_from (str, optional): For 'from X import Y' style imports, the module to import from
            import_as (str, optional): For 'import X as Y' style imports, the alias to use
            import_what (str or list, optional): For 'from X import Y' style imports, what to import

        Returns:
            tuple: (bool success, str message)
        """
        # First check if the library is already imported
        if self.is_library_imported(library_name):
            return True, f"{library_name} is already imported"

        success, content, settings_path = self._read_settings_file()
        if not success:
            return False, content

        try:
            # Construct the import statement based on the parameters
            if import_from:
                if import_what:
                    if isinstance(import_what, list):
                        import_what_str = ", ".join(import_what)
                    else:
                        import_what_str = import_what
                    import_statement = f"from {import_from} import {import_what_str}"
                else:
                    return False, "import_what must be provided when using import_from"
            else:
                import_statement = f"import {library_name}"
                if import_as:
                    import_statement += f" as {import_as}"

            # Find the position to insert the import
            # Usually best to put new imports at the top, after any existing imports
            import_section_end = 0

            # Find the end of imports section (look for the first non-import, non-blank line)
            lines = content.split("\n")
            for i, line in enumerate(lines):
                line = line.strip()
                if (
                    line
                    and not line.startswith("#")
                    and not line.startswith("import")
                    and not line.startswith("from")
                ):
                    import_section_end = i
                    break

            # Insert the import statement
            new_lines = (
                lines[:import_section_end]
                + [import_statement]
                + lines[import_section_end:]
            )
            new_content = "\n".join(new_lines)

            # Write the modified content back to the file
            return self._write_settings_file(settings_path, new_content)

        except Exception as e:
            return False, f"Error adding library import: {str(e)}"

    def edit_middleware_settings(self, new_middleware):
        """
        Update the MIDDLEWARE setting in the Django settings file

        Args:
            new_middleware (list): The new MIDDLEWARE configuration

        Returns:
            tuple: (bool success, str message)
        """
        import re
        from pprint import pformat

        # Format the middleware list with proper indentation
        formatted_middleware = pformat(new_middleware, indent=4)

        # Read the Django settings file
        success, content, settings_path = self._read_settings_file()
        if not success:
            return False, content

        # Look for the start of the MIDDLEWARE assignment
        start_match = re.search(r"MIDDLEWARE\s*=\s*\[", content)
        if not start_match:
            # MIDDLEWARE not found, append it to the end of the file
            new_content = f"{content}\n\n# Added by Djanbee\nMIDDLEWARE = {formatted_middleware}\n"
            return self._write_settings_file(settings_path, new_content)

        # Find the entire MIDDLEWARE block by tracking brackets
        start_pos = start_match.start()
        bracket_count = 0
        end_pos = -1

        # Skip to the first opening bracket
        first_bracket_pos = content.find("[", start_pos)
        if first_bracket_pos == -1:
            return False, "Error: Malformed MIDDLEWARE setting"

        # Count brackets to find the matching closing bracket
        for i in range(first_bracket_pos, len(content)):
            char = content[i]
            if char == "[":
                bracket_count += 1
            elif char == "]":
                bracket_count -= 1
                if bracket_count == 0:
                    end_pos = i + 1
                    break

        if end_pos == -1:
            return False, "Error: Could not find the end of MIDDLEWARE definition"

        # Replace the entire MIDDLEWARE block with the new configuration
        new_content = (
            content[:start_pos]
            + f"MIDDLEWARE = {formatted_middleware}"
            + content[end_pos:]
        )

        # Write the updated content back to the file
        return self._write_settings_file(settings_path, new_content)

    def delete_setting(self, setting_name):
        """
        Delete a setting from the Django settings file, including associated comments
        and empty lines.

        Args:
            setting_name (str): The name of the setting to delete

        Returns:
            tuple: (bool success, str message)
        """
        success, content, settings_path = self._read_settings_file()
        if not success:
            return False, content

        # Split content into lines for more precise handling
        lines = content.split("\n")
        new_lines = []

        # Variables to track state
        setting_found = False
        skip_next_empty = False
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check if this line contains the setting
            if re.match(rf"\s*{setting_name}\s*=", line):
                setting_found = True
                skip_next_empty = True

                # Look backward for comments and empty lines
                j = len(new_lines) - 1

                # Skip immediately preceding empty lines
                while j >= 0 and new_lines[j].strip() == "":
                    j -= 1

                # Skip immediately preceding comments (especially those added by Djanbee)
                while j >= 0 and new_lines[j].strip().startswith("#"):
                    j -= 1

                # Keep only lines up to j
                new_lines = new_lines[: j + 1]

                # Skip this line (the setting line)
                i += 1
                continue

            # Skip empty line after setting if needed
            if skip_next_empty and line.strip() == "":
                skip_next_empty = False
                i += 1
                continue

            # Keep all other lines
            new_lines.append(line)
            i += 1

        if not setting_found:
            return True, f"Setting {setting_name} not found, nothing to delete"

        try:
            # Join lines back into content and write to file
            new_content = "\n".join(new_lines)
            return self._write_settings_file(settings_path, new_content)
        except Exception as e:
            return False, f"Error deleting setting {setting_name}: {str(e)}"
