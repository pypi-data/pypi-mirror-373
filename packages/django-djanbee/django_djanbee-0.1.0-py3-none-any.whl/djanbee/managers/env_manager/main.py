import subprocess
import sys
import os
import venv
from pathlib import Path
from typing import List, Tuple, Optional, Union

from ..console_manager import ConsoleManager
from ..os_manager import OSManager


class EnvManager:
    """
    Manager responsible for Python virtual environment operations,
    especially centralized package dependency management.
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

    def check_package_installed(
        self, venv_path: Union[str, Path], package: str
    ) -> bool:
        """
        Check if a package is installed in the virtual environment.

        Args:
            venv_path: Path to the virtual environment
            package: Name of the package to check

        Returns:
            bool: True if the package is installed, False otherwise
        """
        is_installed, _ = self.os_manager.check_python_package_installed(
            venv_path, package
        )
        return is_installed

    def get_missing_packages(
        self, venv_path: Union[str, Path], required_packages: List[str]
    ) -> List[str]:
        """
        Get a list of required packages that are not installed.

        Args:
            venv_path: Path to the virtual environment
            required_packages: List of package names to check

        Returns:
            List[str]: List of packages that are not installed
        """
        venv_path = Path(venv_path)
        missing_packages = []

        for package in required_packages:
            if not self.check_package_installed(venv_path, package):
                missing_packages.append(package)

        return missing_packages

    def install_package(
        self, venv_path: Union[str, Path], package: str
    ) -> Tuple[bool, str]:
        """
        Install a single package in the virtual environment.

        Args:
            venv_path: Path to the virtual environment
            package: Name of the package to install

        Returns:
            Tuple[bool, str]: Success flag and message
        """
        venv_path = Path(venv_path)
        pip_path = self.os_manager._manager.get_pip_path(venv_path)

        try:
            result = subprocess.run(
                [str(pip_path), "install", package],
                capture_output=True,
                text=True,
                check=True,
            )
            return True, f"Successfully installed {package}"
        except subprocess.CalledProcessError as e:
            return False, f"Failed to install {package}: {e.stderr}"
        except Exception as e:
            return False, f"Error installing {package}: {str(e)}"

    def is_using_venv(self) -> bool:
        """
        Check if currently running in a virtual environment.

        Returns:
            bool: True if running in a virtual environment, False otherwise
        """
        # Check if we're in a virtual environment
        return (
            hasattr(sys, "prefix")
            and hasattr(sys, "base_prefix")
            and sys.prefix != sys.base_prefix
        )

    def ensure_dependencies(
        self,
        venv_path: Optional[Union[str, Path]],
        required_packages: List[str],
        prompt_message: str = "Install missing package dependencies?",
    ) -> Tuple[bool, str, List[str]]:
        """
        Ensure all required packages are installed in the virtual environment.
        If packages are missing, prompt the user to install them if console_manager is available.

        Args:
            venv_path: Path to the virtual environment, or None to use system Python
            required_packages: List of package names to check and install
            prompt_message: Message to show when prompting for installation

        Returns:
            Tuple[bool, str, List[str]]: Success flag, message, and list of installed packages
        """
        # If venv_path is None, check if we can determine the active venv
        if venv_path is None:
            if self.is_using_venv():
                # We're in a virtual environment, use its path
                venv_path = sys.prefix
            else:
                # Use system Python (through regular pip commands)
                # Check dependencies using direct pip commands
                missing_packages = []
                for package in required_packages:
                    res = self.os_manager.check_pip_package_installed(package)

                    if not res.success:
                        missing_packages.append(package)

                if not missing_packages:
                    return True, "All required packages are already installed", []

                # Use system pip to install if needed
                return self._install_system_packages(missing_packages, prompt_message)

        # Handle virtual environment case
        venv_path = Path(venv_path)
        missing_packages = self.get_missing_packages(venv_path, required_packages)
        installed_packages = []

        # If all packages are installed, return early
        if not missing_packages:
            return True, "All required packages are already installed", []

        # If we don't have a console manager, install without prompting
        if not self.console_manager:
            return self._install_packages_without_prompt(venv_path, missing_packages)

        # Show missing packages
        self.console_manager.print_error(
            f"Missing packages: {', '.join(missing_packages)}"
        )

        # Prompt user to install
        from ...widgets.question_selector import QuestionSelector

        selector = QuestionSelector(prompt_message, self.console_manager)

        if selector.select():
            # User confirmed, install packages
            self.console_manager.print_progress(
                f"Installing packages: {', '.join(missing_packages)}"
            )
            for package in missing_packages:
                self.console_manager.print_progress(f"Installing {package}...")
                success, message = self.install_package(venv_path, package)

                if success:
                    self.console_manager.print_step_progress(
                        "Package", f"{package} installed successfully"
                    )
                    installed_packages.append(package)
                else:
                    self.console_manager.print_step_failure("Package", message)

            if len(installed_packages) == len(missing_packages):
                return (
                    True,
                    "All required packages were successfully installed",
                    installed_packages,
                )
            else:
                return False, "Some packages could not be installed", installed_packages
        else:
            # User declined installation
            self.console_manager.print_warning(
                "Packages not installed - operations may fail without required dependencies"
            )
            return False, "User declined to install required packages", []

    def _install_system_packages(
        self, packages: List[str], prompt_message: str
    ) -> Tuple[bool, str, List[str]]:
        """
        Install packages using system pip.

        Args:
            packages: List of packages to install
            prompt_message: Message to show when prompting for installation

        Returns:
            Tuple[bool, str, List[str]]: Success flag, message, and list of installed packages
        """
        installed_packages = []

        # If we don't have a console manager, install without prompting
        if not self.console_manager:
            for package in packages:
                success = self.os_manager.install_pip_package(package)
                if success.success:
                    installed_packages.append(package)
                else:
                    return False, f"Failed to install {package}", installed_packages

            return (
                True,
                "Required packages were successfully installed",
                installed_packages,
            )

        # With console manager, prompt for installation
        self.console_manager.print_error(f"Missing packages: {', '.join(packages)}")

        from ...widgets.question_selector import QuestionSelector

        selector = QuestionSelector(prompt_message, self.console_manager)

        if selector.select():
            # User confirmed, install packages
            self.console_manager.print_progress(
                f"Installing packages: {', '.join(packages)}"
            )
            for package in packages:
                self.console_manager.print_progress(f"Installing {package}...")
                success = self.os_manager.install_pip_package(package)

                if success.success:
                    self.console_manager.print_step_progress(
                        "Package", f"{package} installed successfully"
                    )
                    installed_packages.append(package)
                else:
                    self.console_manager.print_step_failure(
                        "Package", f"Failed to install {package}: {success.stderr}"
                    )

            if len(installed_packages) == len(packages):
                return (
                    True,
                    "All required packages were successfully installed",
                    installed_packages,
                )
            else:
                return False, "Some packages could not be installed", installed_packages
        else:
            # User declined installation
            self.console_manager.print_warning(
                "Packages not installed - operations may fail without required dependencies"
            )
            return False, "User declined to install required packages", []

    def _install_packages_without_prompt(
        self, venv_path: Path, packages: List[str]
    ) -> Tuple[bool, str, List[str]]:
        """
        Install packages without prompting the user.

        Args:
            venv_path: Path to the virtual environment
            packages: List of packages to install

        Returns:
            Tuple[bool, str, List[str]]: Success flag, message, and list of installed packages
        """
        installed_packages = []

        for package in packages:
            success, _ = self.install_package(venv_path, package)
            if success:
                installed_packages.append(package)
            else:
                return (
                    False,
                    f"Failed to install package: {package}",
                    installed_packages,
                )

        if installed_packages:
            return (
                True,
                "Required packages were successfully installed",
                installed_packages,
            )
        else:
            return False, "No packages were installed", []

    # Virtual environment management functions
    def is_venv(self, path: Union[str, Path]) -> bool:
        """
        Check if path is a virtual environment.

        Args:
            path: Path to check

        Returns:
            bool: True if path is a virtual environment
        """
        path = Path(path) if not isinstance(path, Path) else path

        # Check for common venv markers
        bin_dir = path / "bin" if sys.platform != "win32" else path / "Scripts"
        pyvenv_cfg = path / "pyvenv.cfg"

        return path.exists() and bin_dir.exists() and pyvenv_cfg.exists()

    def get_active_venv(self) -> Optional[str]:
        """
        Get path to the currently active virtual environment, if any.

        Returns:
            Optional[str]: Path to active venv or None if not in a venv
        """
        # Check VIRTUAL_ENV environment variable
        virtual_env = os.environ.get("VIRTUAL_ENV")

        # Verify with sys.prefix
        if virtual_env and self.is_using_venv():
            return virtual_env

        return None

    def find_venvs(self, path: Union[str, Path] = ".") -> List[Path]:
        """
        Find virtual environments in the specified path.

        Args:
            path: Directory to search in (default: current directory)

        Returns:
            List[Path]: List of found virtual environment paths
        """
        path = Path(path) if not isinstance(path, Path) else path
        found_venvs = []

        # Check common venv names in the current directory
        common_venv_names = [".venv", "venv", "env", ".env"]
        for venv_name in common_venv_names:
            venv_path = path / venv_name
            if venv_path.exists() and self.is_venv(venv_path):
                found_venvs.append(venv_path)

        # Search all directories (limited depth)
        if not found_venvs:
            for item in path.iterdir():
                if (
                    item.is_dir()
                    and not item.name.startswith(".")
                    and self.is_venv(item)
                ):
                    found_venvs.append(item)

        return found_venvs

    def create_venv(
        self, path: Union[str, Path] = ".venv", with_pip: bool = True
    ) -> Tuple[bool, str]:
        """
        Create a new virtual environment.

        Args:
            path: Path where to create the environment
            with_pip: Whether to include pip in the new environment

        Returns:
            Tuple[bool, str]: Success flag and message
        """
        try:
            if self.console_manager:
                self.console_manager.print_progress(
                    f"Creating virtual environment at {path}..."
                )

            venv_path = Path(path)

            # Create the virtual environment
            venv.create(venv_path, with_pip=with_pip)

            if self.console_manager:
                self.console_manager.print_success(
                    f"Virtual environment created at {venv_path}"
                )

            return True, f"Virtual environment created at {venv_path}"

        except Exception as e:
            error_msg = f"Failed to create virtual environment: {str(e)}"
            if self.console_manager:
                self.console_manager.print_error(error_msg)
            return False, error_msg

    def get_pip_path(self, venv_path: Union[str, Path]) -> Path:
        """
        Get path to pip in a virtual environment.

        Args:
            venv_path: Path to the virtual environment

        Returns:
            Path: Path to pip executable
        """
        return self.os_manager._manager.get_pip_path(Path(venv_path))

    def install_requirements(
        self, venv_path: Union[str, Path], requirements_path: Union[str, Path]
    ) -> Tuple[bool, str]:
        """
        Install requirements from a requirements file into a virtual environment.

        Args:
            venv_path: Path to the virtual environment
            requirements_path: Path to the requirements.txt file

        Returns:
            Tuple[bool, str]: Success flag and message
        """
        try:
            if self.console_manager:
                self.console_manager.print_progress(
                    f"Installing requirements from {requirements_path}..."
                )

            venv_path = Path(venv_path)
            requirements_path = Path(requirements_path)

            if not requirements_path.exists():
                return False, f"Requirements file not found: {requirements_path}"

            pip_path = self.get_pip_path(venv_path)

            result = subprocess.run(
                [str(pip_path), "install", "-r", str(requirements_path)],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                msg = "Requirements installed successfully"
                if self.console_manager:
                    self.console_manager.print_success(msg)
                return True, msg
            else:
                error = f"Failed to install requirements: {result.stderr}"
                if self.console_manager:
                    self.console_manager.print_error(error)
                return False, error

        except Exception as e:
            error_msg = f"Error installing requirements: {str(e)}"
            if self.console_manager:
                self.console_manager.print_error(error_msg)
            return False, error_msg

    def extract_requirements(
        self,
        venv_path: Union[str, Path],
        output_path: Union[str, Path] = "requirements.txt",
    ) -> Tuple[bool, str]:
        """
        Extract installed packages from a virtual environment to a requirements file.

        Args:
            venv_path: Path to the virtual environment
            output_path: Path where to save the requirements file

        Returns:
            Tuple[bool, str]: Success flag and message
        """
        try:
            if self.console_manager:
                self.console_manager.print_progress(
                    f"Extracting requirements from {venv_path}..."
                )

            venv_path = Path(venv_path)
            output_path = Path(output_path)

            pip_path = self.get_pip_path(venv_path)

            result = subprocess.run(
                [str(pip_path), "freeze"], capture_output=True, text=True
            )

            if result.returncode == 0:
                # Write requirements to file
                with open(output_path, "w") as f:
                    f.write(result.stdout)

                msg = f"Requirements extracted to {output_path}"
                if self.console_manager:
                    self.console_manager.print_success(msg)
                return True, msg
            else:
                error = f"Failed to extract requirements: {result.stderr}"
                if self.console_manager:
                    self.console_manager.print_error(error)
                return False, error

        except Exception as e:
            error_msg = f"Error extracting requirements: {str(e)}"
            if self.console_manager:
                self.console_manager.print_error(error_msg)
            return False, error_msg
