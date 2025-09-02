from pathlib import Path
from typing import Tuple, List, Dict, Optional
import textwrap
from ...os_manager import OSManager
from ...console_manager import ConsoleManager
from ...django_manager import DjangoManager
from ..base import BaseSocketManager


class GunicornSocketManager(BaseSocketManager):
    """
    Manages the Gunicorn socket configuration for Django deployments
    """

    def __init__(
        self,
        os_manager: OSManager,
        console_manager: ConsoleManager,
        django_manager: DjangoManager,
    ):
        """
        Initialize with OS manager for platform-specific operations

        Args:
            os_manager: OS manager for platform-specific operations
            console_manager: Console manager for output display
        """
        self.os_manager = os_manager
        self.console_manager = console_manager
        self.django_manager = django_manager
        self.service_name = "gunicorn"

    def check_socket_service_exists(
            self, project_name: str
        ) -> Tuple[bool, Optional[Path], str]:
            """
            Check if a Gunicorn socket service exists for the given project
            Also verifies that the /run/gunicorn directory exists and has proper permissions

            Args:
                project_name: Name of the project (used to identify the service)

            Returns:
                Tuple of (exists, service_file_path, message)
                - exists: Boolean indicating if service exists
                - service_file_path: Path to service file or None if doesn't exist
                - message: Descriptive message about the service and directory status
            """
            try:
                # First verify the /run/gunicorn directory exists with proper permissions
                # This is done regardless of whether the service exists
                dir_success, dir_message = self.verify_run_gunicorn_directory()
                
                if not dir_success:
                    return False, False, f"Failed to verify or create /run/gunicorn directory: {dir_message}"
                
                # Construct the service name based on project name
                service_name = f"gunicorn-{project_name}.service"
                service_file_path = Path(f"/etc/systemd/system/{service_name}")

                # Check if the service file exists
                service_exists = self.os_manager.check_file_exists(service_file_path)

                if service_exists:
                    # Also check if the service is active
                    active_service_name = f"gunicorn-{project_name}"
                    service_active = self.os_manager.check_service_status(
                        active_service_name
                    )

                    if service_active:
                        return service_exists, service_file_path, f"Gunicorn service for {project_name} is active and running"
                    else:
                        return service_exists, service_file_path, f"Gunicorn service file exists for {project_name} but service is not running"
                else:
                    return False, None, f"No Gunicorn service file found for {project_name}"

            except Exception as e:
                return False, False, f"Error checking Gunicorn socket service: {str(e)}"
        
    def create_socket_service(
        self,
        project_path: Path,
        project_name: str,
        wsgi_app: str = None,
        use_sudo: bool = False,
    ) -> Tuple[bool, Path, str]:
        """
        Create a systemd service file for Gunicorn that will create the socket

        Args:
            project_path: Path to the project directory
            project_name: Name of the project
            wsgi_app: WSGI application path (e.g., 'myproject.wsgi:application')
            use_sudo: Whether to use sudo for file operations

        Returns:
            Tuple of (success, service_file_path, socket_file_path)
        """
        try:
            dir_success, dir_message = self.verify_run_gunicorn_directory()
            if not dir_success:
                return (
                    False,
                    None,
                    f"Failed to verify or create /run/gunicorn directory: {dir_message}",
                )

            # Determine socket path
            socket_file_path = f"/run/gunicorn/{project_name}.sock"

            # Determine wsgi_app if not provided
            if not wsgi_app:
                wsgi_app = f"{project_name}.wsgi:application"

            # Get user information
            user = self.os_manager.get_username()

            # Create unique service name based on project name
            service_name = f"gunicorn-{project_name}"
            service_filename = f"{service_name}.service"

            # Create service file content with project-specific description
            service_content = (
                textwrap.dedent(
                    f"""
                [Unit]
                Description=Gunicorn daemon for {project_name}
                After=network.target

                [Service]
                User={user}
                Group={user}
                RuntimeDirectory=gunicorn
                WorkingDirectory={project_path}
                ExecStart={self.django_manager.state.active_venv_path}/bin/gunicorn \\
                        --access-logfile - \\
                        --workers 3 \\
                        --bind unix:{socket_file_path} \\
                        {wsgi_app}

                [Install]
                WantedBy=multi-user.target 
                """
                ).strip()
                + "\n"
            )

            # Write the service file with project-specific name
            service_root = "/etc/systemd/system/"
            service_file_path = Path(f"{service_root}{service_filename}")
            success, message = self.os_manager.write_text_file(
                service_file_path, service_content, use_sudo=use_sudo
            )

            if not success:
                return False, service_file_path, f"Failed to create service file: {message}"

            return True, service_file_path, str(socket_file_path)

        except Exception as e:
            return False, None, f"Error creating Gunicorn socket service: {str(e)}"

    def reload_daemon(self) -> Tuple[bool, str]:
        """
        Reloads the systemd daemon to recognize new or changed service files
        
        Returns:
            Tuple of (success, message)
        """
        try:
            reload_success = self.os_manager.reload_daemon()
            if not reload_success.success:
                self.console_manager.print_error(f"Failed to reload systemd daemon: {reload_success.stderr}")
            
            return reload_success.success, reload_success.stderr
        except Exception as e:
            error_msg = f"Error reloading systemd daemon: {str(e)}"
            self.console_manager.print_error(error_msg)
            return False, error_msg

    def enable_socket_service(self, project_name: str) -> Tuple[bool, str]:
        """
        Enables the Gunicorn socket service for the given project to start on boot
        
        Args:
            project_name: Name of the project (used to identify the service)
        
        Returns:
            Tuple of (success, message)
        """
        try:
            service_name = f"gunicorn-{project_name}"
            enable_success = self.os_manager.enable_service(service_name)
            
            if not enable_success.success:
                self.console_manager.print_error(f"Failed to enable service: {enable_success.stderr}")
                return False, f"Failed to enable service: {enable_success.stderr}"
            
            return True, f"Service '{service_name}' enabled successfully"
        except Exception as e:
            error_msg = f"Error enabling socket service: {str(e)}"
            self.console_manager.print_error(error_msg)
            return False, error_msg

    def start_socket_service(self, project_name: str) -> Tuple[bool, str]:
        """
        Starts the Gunicorn socket service for the given project
        
        Args:
            project_name: Name of the project (used to identify the service)
        
        Returns:
            Tuple of (success, message)
        """
        try:
            service_name = f"gunicorn-{project_name}"
            success = self.os_manager.start_service(service_name)
            
            if not success.success:
                self.console_manager.print_error(f"Failed to start socket service: {success.stderr}")
                return False, f"Failed to start socket service: {success.stderr}"
            
            return True, f"Socket service '{service_name}' started successfully"
        except Exception as e:
            error_msg = f"Error starting socket service: {str(e)}"
            self.console_manager.print_error(error_msg)
            return False, error_msg

    def launch_socket_service(self, project_name: str) -> Tuple[bool, str]:
        """
        Comprehensive function to launch a Gunicorn socket service:
        1. Checks if the service exists
        2. Reloads the systemd daemon
        3. Enables the service to start on boot
        4. Starts the service immediately
        
        Args:
            project_name: Name of the project (used to identify the service)
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Check if the service exists before proceeding
            exists, path, message = self.check_socket_service_exists(project_name)
            if not exists:
                self.console_manager.print_error(
                    f"Socket service for project '{project_name}' does not exist"
                )
                return False, f"Socket service for project '{project_name}' does not exist"
            
            # Reload the systemd daemon to recognize any changes
            reload_success, reload_message = self.reload_daemon()
            if not reload_success:
                return False, reload_message
            
            # Enable the service to start on boot
            enable_success, enable_message = self.enable_socket_service(project_name)
            if not enable_success:
                return False, enable_message
            
            # Start the service immediately
            start_success, start_message = self.start_socket_service(project_name)
            if not start_success:
                return False, start_message
            
            self.console_manager.print_step_progress(
                "Socket service", f"'{project_name}' launched successfully"
            )
            
            return True, f"Socket service for '{project_name}' launched successfully"
        except Exception as e:
            error_msg = f"Error launching socket service: {str(e)}"
            self.console_manager.print_error(error_msg)
            return False, error_msg

    def verify_run_gunicorn_directory(self) -> Tuple[bool, str]:
        """
        Verifies that the /run/gunicorn directory exists and the current user has access to it.
        Creates the directory if it doesn't exist.

        Returns:
            Tuple of (success, message)
        """
        try:
            # Check if /run/gunicorn directory exists
            run_gunicorn_path = "/run/gunicorn"

            # Check if directory exists using OS manager
            dir_exists = self.os_manager.check_directory_exists(run_gunicorn_path)
            if not dir_exists:
                self.console_manager.print_warning(
                    f"The {run_gunicorn_path} directory does not exist."
                )
                self.console_manager.print_progress(f"Attempting to create {run_gunicorn_path}")

                # We need to use sudo to create directory in /run
                create_result = self.os_manager.run_command(
                    ["sudo", "mkdir", "-p", run_gunicorn_path]
                )
                if not create_result.success:
                    return (
                        False,
                        f"Failed to create {run_gunicorn_path} directory: {create_result.stderr}",
                    )

                # Get current username
                username = self.os_manager.get_username()

                # Set ownership to current user
                chown_result = self.os_manager.run_command(
                    ["sudo", "chown", f"{username}:{username}", run_gunicorn_path]
                )
                if not chown_result.success:
                    return (
                        False,
                        f"Failed to set permissions on {run_gunicorn_path}: {chown_result.stderr}",
                    )
                # Set directory permissions
                chmod_result = self.os_manager.run_command(
                    ["sudo", "chmod", "755", run_gunicorn_path]
                )

                if not chmod_result.success:
                    return (
                        False,
                        f"Failed to set directory permissions: {chown_result.stderr}",
                    )

                # Return success message instead of printing
                return True, f"Created directory {run_gunicorn_path} successfully"

            # If directory exists, check if current user has write access
            username = self.os_manager.get_username()
            access_check = self.os_manager.run_command(
                ["test", "-w", run_gunicorn_path]
            )

            if not access_check.success:
                self.console_manager.print_warning(
                    f"User '{username}' does not have write access to {run_gunicorn_path}. Attempting to fix permissions..."
                )

                # Try to fix permissions
                fix_result = self.os_manager.run_command(
                    ["sudo", "chown", f"{username}:{username}", run_gunicorn_path]
                )

                if not fix_result.success:
                    return (
                        False,
                        f"Failed to set permissions on existing {run_gunicorn_path} directory: {fix_result.stderr}",
                    )

                # Return success message instead of printing
                return True, f"Directory permissions for {run_gunicorn_path} updated successfully"

            # Return success message instead of printing
            return True, f"The {run_gunicorn_path} directory exists and user '{username}' has proper access"

        except Exception as e:
            error_msg = f"Error verifying {run_gunicorn_path} directory: {str(e)}"
            self.console_manager.print_error(error_msg)
            return False, error_msg