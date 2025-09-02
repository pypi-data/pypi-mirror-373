import os
import shlex
from pathlib import Path
from typing import List, Union

from ..base import BaseOSManager
from ..command_runner import CommandRunner, CommandResult


class UnixOSManager(BaseOSManager):
    def __init__(self, runner: CommandRunner):
        super().__init__(runner)

    def get_dir(self) -> Path:
        """Returns current working directory."""
        return Path.cwd().resolve()

    def get_pip_path(self, venv_path: Path) -> Path:
        """Gets pip executable path in a virtual environment."""
        return venv_path / "bin" / "pip"

    def check_pip_package_installed(self, package_name: str) -> CommandResult:
        """Checks if a Python package is installed via pip."""
        import sys
        return self._runner.run(
            [sys.executable, "-m", "pip", "show", package_name]
        )

    def install_pip_package(self, package_name: str) -> CommandResult:
        """Installs a Python package via pip."""
        import sys
        return self._runner.run(
            [sys.executable, "-m", "pip", "install", package_name]
        )

    def check_package_installed(self, package_name: str) -> CommandResult:
        """Checks if a system package is installed (by which)."""
        return self._runner.run(["which", package_name])

    def check_service_status(self, service_name: str) -> CommandResult:
        """Checks if a system service is running."""
        return self._runner.run(
            ["systemctl", "status", service_name]
        )

    def install_package(self, package_name: str) -> CommandResult:
        """Installs a system package using apt-get."""
        # Update package list first
        update_res = self._runner.run(
            ["apt-get", "update"], sudo=True
        )
        if not update_res.success:
            return update_res
        # Then install the package
        return self._runner.run(
            ["apt-get", "install", "-y", package_name], sudo=True
        )

    def start_service(self, service_name: str) -> CommandResult:
        """Starts a system service."""
        return self._runner.run(
            ["systemctl", "start", service_name], sudo=True
        )

    def stop_service(self, service_name: str) -> CommandResult:
        """Stops a system service."""
        return self._runner.run(
            ["systemctl", "stop", service_name], sudo=True
        )

    def restart_service(self, service_name: str) -> CommandResult:
        """Restarts a system service."""
        return self._runner.run(
            ["systemctl", "restart", service_name], sudo=True
        )

    def enable_service(self, service_name: str) -> CommandResult:
        """Enables a service to start on boot."""
        return self._runner.run(
            ["systemctl", "enable", service_name], sudo=True
        )

    def run_command(self, command: Union[str, List[str]]) -> CommandResult:
        """Runs a system command (string or list of args)."""
        return self._runner.run(command)

    def run_python_command(self, command_args: List[str]) -> CommandResult:
        """Runs a Python command using the system interpreter."""
        # Determine Python executable
        res = self._runner.run(["which", "python3"])
        if res.success:
            python_exec = res.stdout
        else:
            res2 = self._runner.run(["which", "python"])
            if res2.success:
                python_exec = res2.stdout
            else:
                return CommandResult(
                    success=False,
                    stdout="",
                    stderr="Could not find Python executable",
                    exit_code=res2.exit_code,
                )
        return self._runner.run([python_exec] + command_args)

    def get_username(self) -> str:
        """Gets current user's username."""
        res = self._runner.run(["whoami"])
        return res.stdout.strip() if res.success else ""

    def is_admin(self) -> bool:
        """Checks if current user has admin (root) privileges."""
        try:
            return os.geteuid() == 0
        except AttributeError:
            # os.geteuid not available on some platforms
            return False

    def is_venv_directory(self, path: Path) -> bool:
        """Checks if a directory is a Python virtual environment."""
        return (
            (path / "pyvenv.cfg").exists()
            and (path / "bin").is_dir()
            and (path / "bin" / "python").exists()
        )

    def check_directory_exists(self, dir_path: Union[str, Path]) -> bool:
        """Checks if a directory exists."""
        p = Path(dir_path)
        return p.is_dir()

    def check_file_exists(self, file_path: Path) -> bool:
        """Checks if a file exists."""
        return file_path.is_file()

    def reload_daemon(self) -> CommandResult:
        """Reloads the systemd daemon."""
        return self._runner.run(
            ["systemctl", "daemon-reload"], sudo=True
        )

    def user_exists(self, username: str) -> bool:
        """Checks if a system user exists."""
        res = self._runner.run(["id", username])
        return res.success
