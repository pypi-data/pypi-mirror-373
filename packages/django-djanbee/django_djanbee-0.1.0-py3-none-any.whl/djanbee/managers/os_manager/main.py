import os
import platform
from pathlib import Path
from typing import Callable, List, Optional, Union, Tuple, Any
from collections import namedtuple

from .command_runner import CommandRunner, CommandResult
from .os_implementations import UnixOSManager, WindowsOSManager

Result = namedtuple("Result", ["valid", "object"])


class OSManager:
    def __init__(self):
        """Initializes the platform-specific OS manager with a shared CommandRunner."""
        self._runner = CommandRunner()
        system = platform.system().lower()
        if system == "windows":
            self._manager = WindowsOSManager(self._runner)
        else:
            self._manager = UnixOSManager(self._runner)

    def get_dir(self) -> Path:
        """Returns current working directory"""
        return self._manager.get_dir()

    def get_pip_path(self, venv_path: Path) -> Path:
        """Gets platform-specific pip executable path"""
        return self._manager.get_pip_path(venv_path)

    def check_pip_package_installed(self, package_name: str) -> CommandResult:
        """Checks if a Python package is installed via pip"""
        return self._manager.check_pip_package_installed(package_name)

    def install_pip_package(self, package_name: str) -> CommandResult:
        """Installs a Python package via pip"""
        return self._manager.install_pip_package(package_name)

    def check_package_installed(self, package_name: str) -> CommandResult:
        """Checks if a system package is installed"""
        return self._manager.check_package_installed(package_name)

    def install_package(self, package_name: str) -> CommandResult:
        """Installs a system package using the appropriate package manager"""
        return self._manager.install_package(package_name)

    def check_service_status(self, service_name: str) -> CommandResult:
        """Checks if a system service is running"""
        return self._manager.check_service_status(service_name)

    def start_service(self, service_name: str) -> CommandResult:
        """Starts a system service"""
        return self._manager.start_service(service_name)

    def stop_service(self, service_name: str) -> CommandResult:
        """Stops a system service"""
        return self._manager.stop_service(service_name)

    def restart_service(self, service_name: str) -> CommandResult:
        """Restarts a system service"""
        return self._manager.restart_service(service_name)

    def enable_service(self, service_name: str) -> CommandResult:
        """Enables a service to start on boot"""
        return self._manager.enable_service(service_name)

    def run_command(self, command: Union[str, List[str]]) -> CommandResult:
        """Runs a system command"""
        return self._manager.run_command(command)

    def run_python_command(self, command_args: List[str]) -> CommandResult:
        """Runs a Python command using the system's Python version"""
        return self._manager.run_python_command(command_args)

    def get_username(self) -> str:
        """Gets current user's username"""
        return self._manager.get_username()

    def is_admin(self) -> bool:
        """Checks if current user has admin privileges"""
        return self._manager.is_admin()

    def is_venv_directory(self, path: Path) -> bool:
        """Checks if a directory is a virtual environment"""
        return self._manager.is_venv_directory(path)

    def check_directory_exists(self, dir_path: Union[str, Path]) -> bool:
        """Check if a directory exists"""
        return self._manager.check_directory_exists(dir_path)

    def check_file_exists(self, path: Path) -> bool:
        """Check if a file exists"""
        return path.exists() and path.is_file()

    def reload_daemon(self) -> CommandResult:
        """Reload system daemon"""
        return self._manager.reload_daemon()

    def user_exists(self, username: str) -> bool:
        """Check if a system user exists"""
        return self._manager.user_exists(username)

    # Additional utility methods not in BaseOSManager

    def set_dir(self, dir: Union[str, Path] = "."):
        """Sets the process current working directory"""
        dir_path = Path(dir)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory does not exist: {dir_path}")
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {dir_path}")
        os.chdir(dir_path)

    def get_path_basename(self, path: Union[str, Path]) -> str:
        """Returns the final component of a path"""
        path_obj = Path(path)
        return path_obj.name

    def search_subfolders(
            self,
            validator: Callable[[Any], Optional[bool]],
            max_depth: int = 1,
            search_path: Union[str, Path] = None
    ) -> List[Result]:
        """Searches subfolders using a validator that may take a Path or a str."""
        if search_path is None:
            search_path = self.get_dir()
        root = Path(search_path)
        results: List[Result] = []

        def recurse(path: Path, depth: int):
            if depth > max_depth:
                return
            try:
                for child in path.iterdir():
                    if child.name.startswith('.'):
                        continue

                    # Try validator with Path
                    valid = validator(child)
                    # Fallback to validator with str(path)
                    if not valid:
                        valid = validator(str(child))

                    if valid:
                        results.append(Result(valid=valid, object=child))

                    if child.is_dir():
                        recurse(child, depth + 1)
            except PermissionError:
                pass

        recurse(root, 1)
        return results

    def search_folder(
            self,
            validator: Callable[[Any], Optional[bool]],
            search_path: Union[str, Path] = None
    ) -> Optional[Result]:
        """Searches the given folder using a validator that may take a Path or a str."""
        if search_path is None:
            search_path = self.get_dir()

        path = Path(search_path)
        try:
            # first try as Path
            res = validator(path)
            if res:
                return Result(valid=res, object=path)
            # then try as str, for backwards‐compatible validators
            res = validator(str(path))
            if res:
                return Result(valid=res, object=path)
        except PermissionError:
            pass

        return None

    def get_environment_variable(self, var_name: str) -> Optional[str]:
        """Retrieves an environment variable's value"""
        return os.environ.get(var_name)

    def run_pip_command(self, venv_path: Path, pip_args: List[str]) -> CommandResult:
        """Runs a pip command inside a virtual environment"""
        pip_path = self.get_pip_path(venv_path)
        return self._runner.run([str(pip_path)] + pip_args)

    def write_text_file(
        self, path: Path, content: str, use_sudo: bool = False
    ) -> CommandResult:
        """
        Writes text to a file, optionally using sudo privileges.
        """
        if not use_sudo:
            try:
                path.write_text(content)
                return CommandResult(success=True, stdout="File written successfully", stderr="", exit_code=0)
            except Exception as e:
                return CommandResult(success=False, stdout="", stderr=str(e), exit_code=1)
        # sudo path
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp.write(content)
            temp_path = tmp.name
        mv_res = self._runner.run(["mv", temp_path, str(path)], sudo=True)
        if not mv_res.success:
            return mv_res
        return self._runner.run(["chmod", "644", str(path)], sudo=True)

    def check_python_package_installed(
        self, venv_path: Union[str, Path], package_name: str
    ) -> CommandResult:
        """Checks if a package is installed in the virtual environment via pip"""
        venv_path = Path(venv_path)
        pip_path = self.get_pip_path(venv_path)
        res = self._runner.run([str(pip_path), "list"])
        if not res.success:
            return res
        installed = any(
            line.split()[0] == package_name for line in res.stdout.splitlines()
        )
        msg = f"{package_name} is {'installed' if installed else 'not installed'}"
        return CommandResult(success=installed, stdout=msg, stderr="", exit_code=res.exit_code)

    def check_postgres_dependencies(
        self, venv_path: Union[str, Path]
    ) -> Tuple[bool, List[str]]:
        """Identifies missing PostgreSQL dependencies in a virtual environment"""
        required = ["psycopg2", "psycopg2-binary"]
        missing = []
        for pkg in required:
            res = self.check_python_package_installed(venv_path, pkg)
            if not res.success:
                missing.append(pkg)
        return (len(missing) == 0, missing)

    def ensure_postgres_dependencies(
        self, venv_path: Union[str, Path]
    ) -> CommandResult:
        """Installs missing PostgreSQL dependencies in a virtual environment"""
        ok, missing = self.check_postgres_dependencies(venv_path)
        if ok:
            return CommandResult(success=True, stdout="Postgres dependencies already installed", stderr="", exit_code=0)
        for pkg in missing:
            res = self._runner.run([str(self.get_pip_path(Path(venv_path))), "install", pkg])
            if not res.success:
                return res
        return CommandResult(success=True, stdout="Postgres dependencies installed successfully", stderr="", exit_code=0)
