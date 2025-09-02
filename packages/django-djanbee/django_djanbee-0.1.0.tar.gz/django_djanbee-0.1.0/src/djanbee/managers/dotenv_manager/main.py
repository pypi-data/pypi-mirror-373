from pathlib import Path
from typing import Dict, List, Tuple, Optional, Union, Any
import os
from dotenv import load_dotenv, dotenv_values, set_key, unset_key, find_dotenv

from ..console_manager import ConsoleManager
from ..os_manager import OSManager


class DotenvManager:
    """
    Manager responsible for .env file operations,
    handling environment variables in .env files.
    """

    def __init__(self, os_manager: OSManager, console_manager: ConsoleManager = None):
        """
        Initialize with references to other managers.

        Args:
            os_manager: OSManager instance for OS operations
            console_manager: Optional ConsoleManager for user interaction
        """
        self.os_manager = os_manager
        self.console_manager = console_manager

    def create_env_file(self, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        Create a new .env file at the specified path.

        Args:
            file_path: Path where to create the .env file

        Returns:
            Tuple[bool, str]: Success flag and message
        """
        try:
            file_path = Path(file_path)
            if file_path.exists():
                return False, f"File already exists at {file_path}"
            
            # Create empty .env file
            file_path.touch()
            
            if self.console_manager:
                self.console_manager.print_success(f"Created .env file at {file_path}")
                
            return True, f"Created .env file at {file_path}"
        except Exception as e:
            error_msg = f"Failed to create .env file: {str(e)}"
            if self.console_manager:
                self.console_manager.print_error(error_msg)
            return False, error_msg

    def read_env_file(self, file_path: Union[str, Path]) -> Tuple[bool, str, Dict[str, str]]:
        """
        Read and parse a .env file.

        Args:
            file_path: Path to the .env file

        Returns:
            Tuple[bool, str, Dict[str, str]]: Success flag, message, and dictionary of key-value pairs
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False, f"File not found: {file_path}", {}
            
            # Use dotenv to parse the file
            env_vars = dotenv_values(file_path)
            
            return True, f"Successfully read {file_path}", env_vars
        except Exception as e:
            error_msg = f"Failed to read .env file: {str(e)}"
            if self.console_manager:
                self.console_manager.print_error(error_msg)
            return False, error_msg, {}

    def write_env_file(self, file_path: Union[str, Path], env_vars: Dict[str, str]) -> Tuple[bool, str]:
        """
        Write environment variables to a .env file.

        Args:
            file_path: Path to the .env file
            env_vars: Dictionary of environment variables to write

        Returns:
            Tuple[bool, str]: Success flag and message
        """
        try:
            file_path = Path(file_path)
            
            # Write variables to file
            with open(file_path, 'w') as f:
                for key, value in env_vars.items():
                    f.write(f"{key}={value}\n")
            
            if self.console_manager:
                self.console_manager.print_success(f"Successfully wrote to {file_path}")
                
            return True, f"Successfully wrote to {file_path}"
        except Exception as e:
            error_msg = f"Failed to write .env file: {str(e)}"
            if self.console_manager:
                self.console_manager.print_error(error_msg)
            return False, error_msg

    def update_env_variable(self, file_path: Union[str, Path], key: str, value: str) -> Tuple[bool, str]:
        """
        Update or add a single environment variable in a .env file.

        Args:
            file_path: Path to the .env file
            key: Environment variable name
            value: Environment variable value

        Returns:
            Tuple[bool, str]: Success flag and message
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False, f"File not found: {file_path}"
            
            # Use dotenv to set the key
            set_key(file_path, key, value)
            
            if self.console_manager:
                self.console_manager.print_success(f"Updated environment variable '{key}' in {file_path}")
                
            return True, f"Updated environment variable '{key}' in {file_path}"
        except Exception as e:
            error_msg = f"Failed to update environment variable: {str(e)}"
            if self.console_manager:
                self.console_manager.print_error(error_msg)
            return False, error_msg

    def delete_env_variable(self, file_path: Union[str, Path], key: str) -> Tuple[bool, str]:
        """
        Delete an environment variable from a .env file.

        Args:
            file_path: Path to the .env file
            key: Environment variable name to delete

        Returns:
            Tuple[bool, str]: Success flag and message
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False, f"File not found: {file_path}"
            
            # Check if key exists
            env_vars = dotenv_values(file_path)
            if key not in env_vars:
                return False, f"Environment variable '{key}' not found in {file_path}"
            
            # Use dotenv to unset the key
            unset_key(file_path, key)
            
            if self.console_manager:
                self.console_manager.print_success(f"Deleted environment variable '{key}' from {file_path}")
                
            return True, f"Deleted environment variable '{key}' from {file_path}"
        except Exception as e:
            error_msg = f"Failed to delete environment variable: {str(e)}"
            if self.console_manager:
                self.console_manager.print_error(error_msg)
            return False, error_msg

    def load_env_file(self, file_path: Union[str, Path]) -> Tuple[bool, str]:
        """
        Load environment variables from a .env file into the current process environment.

        Args:
            file_path: Path to the .env file

        Returns:
            Tuple[bool, str]: Success flag and message
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                return False, f"File not found: {file_path}"
            
            # Use dotenv to load the file
            load_dotenv(file_path)
            
            if self.console_manager:
                self.console_manager.print_success(f"Loaded environment variables from {file_path}")
                
            return True, f"Loaded environment variables from {file_path}"
        except Exception as e:
            error_msg = f"Failed to load environment variables: {str(e)}"
            if self.console_manager:
                self.console_manager.print_error(error_msg)
            return False, error_msg

    def find_env_files(self, directory: Union[str, Path] = '.') -> List[Path]:
        """
        Find .env files in the specified directory and its subdirectories.

        Args:
            directory: Directory to search in (default: current directory)

        Returns:
            List[Path]: List of found .env file paths
        """
        directory = Path(directory)
        env_files = []
        
        # Use dotenv's built-in find_dotenv function for the main .env file
        # Change working directory temporarily to search in the specified directory
        current_dir = os.getcwd()
        os.chdir(str(directory))
        main_env = find_dotenv(usecwd=True)
        os.chdir(current_dir)
        if main_env:
            env_files.append(Path(main_env))
        
        # Look for other common patterns
        for pattern in ['.env.local', '.env.development', '.env.production', '.env.test']:
            # find_dotenv doesn't support custom naming patterns, so we check manually
            env_file = directory / pattern
            if env_file.exists() and env_file.is_file():
                env_files.append(env_file)
        
        # Optionally search subdirectories
        for subdir in directory.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('.'):
                # Avoid venv directories and node_modules
                if subdir.name not in ['venv', '.venv', 'node_modules']:
                    # Change directory temporarily to search in subdirectory
                    current_dir = os.getcwd()
                    os.chdir(str(subdir))
                    subdir_env_path = find_dotenv(usecwd=True)
                    os.chdir(current_dir)
                    if subdir_env_path:
                        env_files.append(Path(subdir_env_path))
        
        return env_files
