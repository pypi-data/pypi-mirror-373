from .display import DeployDisplay
from ...core import AppContainer


class DeployManager:
    """Manages deployment operations for Django projects."""
    
    def __init__(self, display: DeployDisplay, app: "AppContainer"):
        self.display = display
        self.app = app
    
    # Public methods
    
    def verify_packages(self) -> bool:
        """Verify and install necessary packages for deployment."""
        # First check if nginx is installed
        if not self._verify_venv():
            return False
        
        nginx_installed = self.app.server_manager.check_server_installed()
        
        if nginx_installed:
            self.display.nginx_found()
        else:
            self.display.nginx_not_found()
            # Prompt user to install nginx
            if self.display.prompt_install_nginx():
                self.display.progress_install_dep("nginx")
                res = self.app.server_manager.install_server()
                if res.success:
                    self.display.nginx_installed_success()
                else:
                    self.display.nginx_installed_failure(res.stderr)
                    return False
            else:
                self.display.nginx_required_abort()
                return False

        # Check dependencies
        dependency_results = self.app.server_manager.verify_dependencies()
        self.display.report_dependency_check(dependency_results)

        # Install missing dependencies
        installation_results = []
        for dep_name, is_installed, message in dependency_results:
            if not is_installed:
                self.display.progress_install_dep(dep_name)
                success, install_msg = self.app.server_manager.install_dependency(
                    dep_name
                )
                installation_results.append((dep_name, success, install_msg))

        # Report installation results
        if installation_results:
            self.display.report_dependency_installation(installation_results)

        self.display.success_verify_dep()
        return True
    
    def find_and_create_socket_file(self) -> bool:
        """Set up the socket file for the Django application."""
        if not self._verify_django_project():
            return False
        
        project_path = self.app.django_manager.state.current_project_path
        project_name = project_path.name
        
        # Always verify the /run/gunicorn directory exists with proper permissions
        dir_success, dir_message = self.app.socket_manager.verify_run_gunicorn_directory()
        if not dir_success:
            self.display.socket_directory_failure(dir_message)
            return False
        
        self.display.socket_directory_success(dir_message)
        
        self.display.socket_service_verifying(project_name)
        
        socket_exists, service_path, socket_message = (
            self.app.socket_manager.check_socket_service_exists(project_name)
        )
        if socket_exists:
            self.display.socket_service_exists(project_name, service_path)
            
            # Ask to override if exists
            if not self.display.prompt_override_socket(service_path, service_path.name):
                return True
        else:
            if service_path is None:
                self.display.socket_service_not_found(project_name)
            else:
                self.display.socket_service_error(socket_message)
        
        # Create socket service (either it doesn't exist or user wants to override)
        self.display.socket_service_creating(project_name, service_path)
        result, service_root, path = self.app.socket_manager.create_socket_service(
            project_path, project_name, use_sudo=True
        )
        
        if result:
            self.display.success_create_socketservice(service_root)
            return True
        else:
            self.display.socket_service_failure(path)
            return False

    def launch_socketfile(self) -> bool:
        """Launch the socket file service."""
        project_name = self.app.django_manager.state.current_project_path.name

        start_success, start_message = self.app.socket_manager.launch_socket_service(project_name)
        
        if start_success:
            self.display.socket_service_launch_success(project_name)
        else:
            self.display.socket_service_launch_failure(project_name, start_message)
            
        return start_success

    def find_and_create_server_file(self) -> bool:
        """Set up the server configuration file."""
        project_path =  self.app.django_manager.state.current_project_path
        
        project_name = project_path.name

        # Check if server configuration exists
        server_exists, config_path = self.app.server_manager.check_server_config_exists(
            project_name
        )

        if server_exists and not self.display.prompt_override_server(config_path, config_path.name):
            return True
            
        # Create server configuration (either it doesn't exist or user wants to override)
        result, path = self.app.server_manager.create_server_config(
            project_path, project_name, use_sudo=True
        )
        
        if result:
            self.display.success_create_serverconfig(path)
            return True
        else:
            self.display.server_config_failure(path)
            return False
    
    # Private methods
    
    def _verify_venv(self) -> bool:
        """Internal check for virtual environment."""
        if not self.app.django_manager.state.active_venv_path:
            if not self.app.django_manager.environment_service.get_active_venv():
                self.display.failure_verify_venv()
                return False
        return True

    def _verify_django_project(self) -> bool:
        """Internal check for Django project."""
        if not self.app.django_manager.project_service.state.current_project_path:
            if not self.app.django_manager.project_service.select_project():
                return False
        return True
    
    def manage_nginx_configuration(self) -> bool:
        """Check for default site and manage Nginx configuration."""
        # Check if default site exists
        default_exists = self.app.server_manager.check_default_site_exists()
        
        if default_exists:
            self.display.nginx_default_site_found()
            if self.display.prompt_remove_default_site():
                # Remove default site
                remove_success, remove_message = self.app.server_manager.remove_default_site()
                
                if not remove_success:
                    self.display.nginx_default_removal_failed(remove_message)
                    return False
                    
                self.display.nginx_default_removed()
            else:
                self.display.nginx_default_kept_warning()
        
        # Test Nginx configuration
        test_success, test_message = self.app.server_manager.test_configuration()
        
        if not test_success:
            self.display.nginx_config_test_failed(test_message)
            return False
            
        # Reload Nginx to apply changes
        reload_success, reload_message = self.app.server_manager.restart_server()
        
        if not reload_success:
            self.display.nginx_reload_failed(reload_message)
            return False
            
        self.display.nginx_reload_success()
        return True