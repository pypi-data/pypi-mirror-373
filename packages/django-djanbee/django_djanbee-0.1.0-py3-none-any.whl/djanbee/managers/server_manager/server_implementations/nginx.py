from pathlib import Path
from typing import List, Tuple, Optional
import textwrap
from ..base import BaseServerManager
from ...os_manager import OSManager
from ...console_manager import ConsoleManager
from ...django_manager import DjangoManager
from ...os_manager.command_runner import CommandResult


class NginxServerManager(BaseServerManager):
    def __init__(
        self,
        os_manager: OSManager,
        console_manager: ConsoleManager,
        django_manager: DjangoManager,
    ):
        """Initialize with OS manager for platform-specific operations"""
        self.os_manager = os_manager
        self.console_manager = console_manager
        self.django_manager = django_manager
        self.server_name = "nginx"
        self.dependencies = ["gunicorn"]

    def check_server_installed(self) -> bool:
        """Checks if Nginx is installed"""
        return self.os_manager.check_package_installed(self.server_name).success

    def install_server(self) -> CommandResult:
        """Installs Nginx if not already installed"""
        if self.check_server_installed():
            return CommandResult(
                success=True,
                stdout="Nginx is already installed",
                stderr="",
                exit_code=0,
            )

        return self.os_manager.install_package(self.server_name)

    def start_server(self) -> CommandResult:
        """Starts the Nginx server"""
        return self.os_manager.start_service(self.server_name)

    def stop_server(self) -> CommandResult:
        """Stops the Nginx server"""
        return self.os_manager.stop_service(self.server_name)

    def restart_server(self) -> CommandResult:
        """Restarts the Nginx server"""
        return self.os_manager.restart_service(self.server_name)

    def enable_server(self) -> CommandResult:
        """Enables Nginx to start on boot"""
        return self.os_manager.enable_service(self.server_name)

    def check_server_status(self) -> CommandResult:
        """Checks if Nginx is running"""
        return self.os_manager.check_service_status(self.server_name)

    def get_server_version(self) -> str:
        """Gets the Nginx version"""
        success = self.os_manager.run_command([self.server_name, "-v"])
        if success.success:
            return success.stdout
        else:
            return "Unknown version"

    # Additional methods for dependency management
    def get_dependencies(self) -> List[str]:
        """Returns the list of dependencies required by this server"""
        return self.dependencies

    def check_gunicorn_installed(self) -> CommandResult:
        """Checks if Gunicorn is installed via pip"""
        return self.os_manager.check_pip_package_installed("gunicorn")

    def install_gunicorn(self) -> CommandResult:
        """Installs Gunicorn if not already installed."""
        check_res = self.check_gunicorn_installed()
        if check_res.success if isinstance(check_res, CommandResult) else check_res:
            return CommandResult(
                success=True,
                stdout="Gunicorn is already installed",
                stderr="",
                exit_code=0,
            )
        return self.os_manager.install_pip_package("gunicorn")

    def verify_dependencies(self) -> List[Tuple[str, bool, str]]:
        """Verifies all dependencies and returns results"""
        results = []
        for dependency in self.dependencies:
            check_method = getattr(self, f"check_{dependency}_installed", None)
            if check_method and callable(check_method):
                is_installed = check_method()
                status_msg = f"{dependency} is {'installed' if is_installed else 'not installed'}"
                results.append((dependency, is_installed, status_msg))
            else:
                results.append((dependency, False, f"Cannot check {dependency}"))
        return results

    def install_dependency(self, dependency: str) -> Tuple[bool, str]:
        """Install a specific dependency"""
        if dependency not in self.dependencies:
            return False, f"{dependency} is not a recognized dependency"

        install_method = getattr(self, f"install_{dependency}", None)
        if install_method and callable(install_method):
            return install_method()
        else:
            return False, f"No installation method for {dependency}"

    def check_server_config_exists(
        self, project_name: str
    ) -> Tuple[bool, Optional[Path]]:
        """
        Check if an Nginx server configuration exists for the given project

        Args:
            project_name: Name of the project (used to identify the config)

        Returns:
            Tuple of (exists, config_file_path)
            If config doesn't exist, path will be None
        """
        try:
            # Construct the config filename based on project name
            config_name = f"{project_name}"
            config_file_path = Path(f"/etc/nginx/sites-available/{config_name}")

            # Check if the config file exists
            config_exists = self.os_manager.check_file_exists(config_file_path)

            if config_exists:
                self.console_manager.print_info(
                    f"Nginx configuration found at {config_file_path}"
                )

                # Also check if the configuration is enabled (symlinked)
                enabled_path = Path(f"/etc/nginx/sites-enabled/{config_name}")
                config_enabled = self.os_manager.check_file_exists(enabled_path)

                if config_enabled:
                    self.console_manager.print_info(
                        f"Nginx configuration for {project_name} is enabled"
                    )
                else:
                    self.console_manager.print_error(
                        f"Nginx configuration exists for {project_name} but is not enabled"
                    )

                return config_exists, config_file_path
            else:
                self.console_manager.print_info(
                    f"No Nginx configuration found for {project_name}"
                )
                return False, None

        except Exception as e:
            self.console_manager.print_error(
                f"Error checking Nginx server configuration: {str(e)}"
            )
            return False, None

    def create_server_config(
        self,
        project_path: Path,
        project_name: str,
        server_name: str = "localhost",
        socket_path: Path = None,
        use_sudo: bool = False,
    ) -> Tuple[bool, str]:
        """
        Create an Nginx server configuration for the given project

        Args:
            project_path: Path to the project directory
            project_name: Name of the project
            server_name: Server name/domain for the Nginx config
            socket_path: Path to the Gunicorn socket file (if None, will be derived)
            use_sudo: Whether to use sudo for file operations

        Returns:
            Tuple of (success, message or config_path)
        """
        try:
            # Determine socket path if not provided
            if not socket_path:
                socket_path = f"/run/gunicorn/{project_name}.sock"

            # Determine web root path
            web_root = Path(f"/var/www/{project_name}")
            static_path = web_root / "static"
            media_path = web_root / "media"

            # Get the nginx user (typically www-data on Ubuntu/Debian or nginx on CentOS/RHEL)
            # First check if nginx user exists
            nginx_user_exists = self.os_manager.run_command(["id", "-u", "nginx"])
            if nginx_user_exists.success:
                web_user = "nginx"
            else:
                # Fall back to www-data which is common on Debian/Ubuntu
                web_user = "www-data"
            # Create necessary directories if they don't exist
            user = self.os_manager.get_username()
            for path in [web_root, static_path, media_path]:
                if not path.exists():
                    mkdir_command = ["sudo", "mkdir", "-p", str(path)]
                    self.os_manager.run_command(mkdir_command)

                    # Set proper ownership - user owns it, but nginx/www-data needs read access
                    user = self.os_manager.get_username()
                    chown_command = ["sudo", "chown", f"{user}:{web_user}", str(path)]
                    self.os_manager.run_command(chown_command)

                    # Set proper permissions (755 - user can write, others can read and execute)
                    chmod_command = ["sudo", "chmod", "755", str(path)]
                    self.os_manager.run_command(chmod_command)

            # Also ensure socket file is accessible to Nginx
            chmod_socket_command = ["sudo", "chmod", "660", str(socket_path)]
            result = self.os_manager.run_command(chmod_socket_command)
            chown_socket_command = [
                "sudo",
                "chown",
                f"{user}:{web_user}",
                str(socket_path),
            ]
            self.os_manager.run_command(chown_socket_command)

            # Create config file content
            config_content = (
                textwrap.dedent(
                    f"""
            server {{
                listen 80;
                server_name {server_name};

                location = /favicon.ico {{ access_log off; log_not_found off; }}
                
                location /static/ {{
                    alias {static_path}/;
                }}
                
                location /media/ {{
                    alias {media_path}/;
                }}
                
                location / {{
                    include proxy_params;
                    proxy_pass http://unix:{socket_path};
                }}
            }}
            """
                ).strip()
                + "\n"
            )

            # Write the config file
            config_file_path = Path(f"/etc/nginx/sites-available/{project_name}")
            success, message = self.os_manager.write_text_file(
                config_file_path, config_content, use_sudo=use_sudo
            )
            if not success:
                return False, f"Failed to create Nginx configuration: {message}"

            # Create symbolic link to enable the configuration
            enabled_path = Path(f"/etc/nginx/sites-enabled/{project_name}")
            if not self.os_manager.check_file_exists(enabled_path):
                symlink_command = [
                    "sudo",
                    "ln",
                    "-s",
                    str(config_file_path),
                    str(enabled_path),
                ]
                link_success = self.os_manager.run_command(
                    symlink_command
                )

                if not link_success.success:
                    return (
                        False,
                        f"Failed to enable Nginx configuration: {link_success.stderr}",
                    )

            # Test the Nginx configuration
            test_success = self.os_manager.run_command(
                ["sudo", "nginx", "-t"]
            )
            if not test_success.success:
                return False, f"Nginx configuration test failed: {test_success.stderr}"

            # Reload Nginx to apply changes
            reload_success, reload_message = self.restart_server()
            self.configure_django_static_settings(project_name)
            if not reload_success:
                return False, f"Failed to reload Nginx: {reload_message}"

            return True, str(config_file_path)

        except Exception as e:
            return False, f"Error creating Nginx server configuration: {str(e)}"

    def configure_django_static_settings(self, project_name: str) -> Tuple[bool, str]:
        """
        Configure Django static and media file settings for Nginx deployment

        Args:
            project_name: Name of the project
            settings_service: Instance of DjangoSettingsService

        Returns:
            Tuple of (success, message)
        """
        try:
            # Define the paths for static and media files
            web_root = f"/var/www/{project_name}"
            static_root = f"{web_root}/static"
            media_root = f"{web_root}/media"
            settings_service = self.django_manager.settings_service
            # Update STATIC_ROOT setting
            static_success, static_message = settings_service.edit_settings(
                "STATIC_ROOT", static_root
            )

            if not static_success:
                return False, f"Failed to configure STATIC_ROOT: {static_message}"

            # Update MEDIA_ROOT setting
            media_success, media_message = settings_service.edit_settings(
                "MEDIA_ROOT", media_root
            )

            if not media_success:
                return False, f"Failed to configure MEDIA_ROOT: {static_message}"

            # Make sure STATIC_URL is set correctly
            static_url_success, static_url_message = settings_service.edit_settings(
                "STATIC_URL", "/static/"
            )

            if not static_url_success:
                return False, f"Failed to configure STATIC_URL: {static_url_message}"

            # Make sure MEDIA_URL is set correctly
            media_url_success, media_url_message = settings_service.edit_settings(
                "MEDIA_URL", "/media/"
            )

            if not media_url_success:
                return False, f"Failed to configure MEDIA_URL: {media_url_message}"

            self.console_manager.print_info(
                f"Django static and media settings configured to use {web_root}"
            )

            return True, "Static and media settings successfully configured"

        except Exception as e:
            return False, f"Error configuring static file settings: {str(e)}"

    def check_default_site_exists(self) -> bool:
        """Check if default site exists in sites-enabled."""
        default_config_path = Path("/etc/nginx/sites-enabled/default")
        return self.os_manager.check_file_exists(default_config_path)

    def remove_default_site(self) -> CommandResult:
        """Remove the default site from sites-enabled."""
        default_config_path = Path("/etc/nginx/sites-enabled/default")
        return self.os_manager.run_command(["sudo", "rm", str(default_config_path)])

    def test_configuration(self) -> CommandResult:
        """Test the Nginx configuration."""
        return self.os_manager.run_command(["sudo", "nginx", "-t"])

