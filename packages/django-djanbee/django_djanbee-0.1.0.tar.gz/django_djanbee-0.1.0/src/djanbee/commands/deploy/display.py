from ...managers import ConsoleManager
from ...widgets.question_selector import QuestionSelector


class DeployDisplay:
    def __init__(self, console_manager: "ConsoleManager"):
        self.console_manager = console_manager

    def report_dependency_check(self, dependency_results):
        """Display initial dependency check results"""
        for dep_name, is_installed, message in dependency_results:
            if is_installed:
                self.console_manager.print_step_progress(
                    dep_name.capitalize(), f"{dep_name.capitalize()} found"
                )
            else:
                self.console_manager.print_step_failure(
                    dep_name.capitalize(), f"{dep_name.capitalize()} not found"
                )
                
    def nginx_found(self):
        """Display that Nginx is found"""
        self.console_manager.print_step_progress("Nginx", "Nginx installation found")
        
    def nginx_not_found(self):
        """Display that Nginx is not found"""
        self.console_manager.print_step_failure("Nginx", "Nginx not found")
        
    def nginx_installed_success(self):
        """Display that Nginx was installed successfully"""
        self.console_manager.print_step_progress("Nginx", "Nginx installed successfully")
        
    def nginx_installed_failure(self, error_message):
        """Display that Nginx installation failed"""
        self.console_manager.print_step_failure("Nginx", f"Failed to install Nginx: {error_message}")
        
    def nginx_required_abort(self):
        """Display warning that Nginx is required and aborting"""
        self.console_manager.print_warning_critical("Nginx is required for deployment. Aborting.")

    def report_dependency_installation(self, installation_results):
        """Display dependency installation results"""
        for dep_name, success, message in installation_results:
            if success:
                self.console_manager.print_step_progress(
                    dep_name.capitalize(),
                    f"{dep_name.capitalize()} installed successfully",
                )
            else:
                self.console_manager.print_step_failure(
                    dep_name.capitalize(), f"Failed: {message}"
                )

    def progress_install_dep(self, dep_name):
        self.console_manager.print_progress(f"Installing {dep_name.capitalize()}...")

    def success_verify_dep(self):
        self.console_manager.print_success("Server dependencies verified successfully!")

    def failure_verify_venv(self):
        self.console_manager.print_warning_critical("No venv found")

    def prompt_install_nginx(self):
        selector = QuestionSelector(
            "Nginx not found. Do you want to install it?",
            self.console_manager,
            "yes",
            "no",
            "Nginx is required for deployment",
        )
        return selector.select()

    def prompt_override_socket(self, service_path, service_name):
        selector = QuestionSelector(
            "Do you wish to override socketfile",
            self.console_manager,
            "yes",
            "no",
            f"This action will replace the current {service_name}",
        )
        return selector.select()

    def success_create_socketservice(self, path):
        self.console_manager.print_success(f"Socket service created at {path}")
        
    def socket_directory_success(self, message):
        """Display that socket directory verification succeeded"""
        self.console_manager.print_step_progress("Socket directory", message)
        
    def socket_directory_failure(self, message):
        """Display that socket directory verification failed"""
        self.console_manager.print_error(f"Failed to set up socket directory: {message}")
        
    def socket_service_failure(self, path):
        """Display that socket service creation failed"""
        self.console_manager.print_error(f"Failed to create socket service: {path}")

    def success_create_serverconfig(self, path):
        self.console_manager.print_success(f"Server config created at {path}")
        
    def server_config_failure(self, message):
        self.console_manager.print_error(f"Failed to create server configuration: {message}")

    def prompt_override_server(self, config_path, config_name):
        selector = QuestionSelector(
            "Do you wish to override server configfile",
            self.console_manager,
            "yes",
            "no",
            f"This action will replace the current {config_name}",
        )
        return selector.select()

    def socket_service_verifying(self, project_name):
        """Display that socket service verification is in progress"""
        self.console_manager.print_lookup(f"Verifying Gunicorn socket service for '{project_name}'...")
        
    def socket_service_exists(self, project_name, service_path):
        """Display that socket service exists"""
        self.console_manager.print_info(f"Gunicorn service file found at {service_path}")
        
    def socket_service_not_found(self, project_name):
        """Display that socket service was not found"""
        self.console_manager.print_warning(f"No Gunicorn service file found for '{project_name}'")
        
    def socket_service_error(self, message):
        """Display error during socket service verification"""
        self.console_manager.print_error(f"Error checking Gunicorn socket service: {message}")
        
    def socket_service_creating(self, project_name, service_path):
        """Display that socket service creation is in progress"""
        self.console_manager.print_progress(f"Creating Gunicorn socket service for '{project_name}' at {service_path}...")

    def socket_service_launch_success(self, project_name):
        """Display that socket service was successfully launched"""
        self.console_manager.print_success(f"Gunicorn socket service for '{project_name}' launched successfully")
        
    def socket_service_launch_failure(self, project_name, message):
        """Display that socket service launch failed"""
        self.console_manager.print_error(f"Failed to launch Gunicorn socket service for '{project_name}': {message}")
        

    def nginx_default_site_found(self):
        """Display that the default Nginx site is found."""
        self.console_manager.print_warning("Default Nginx site is active and may conflict with your project site.")
        
    def prompt_remove_default_site(self):
        """Ask user if they want to remove the default Nginx site."""
        selector = QuestionSelector(
            "Do you want to remove the default Nginx site?",
            self.console_manager,
            "yes",
            "no",
            "The default site can conflict with your project configuration",
        )
        return selector.select()
        
    def nginx_default_removed(self):
        """Display that the default Nginx site was removed."""
        self.console_manager.print_step_progress("Nginx", "Default site removed")
        
    def nginx_default_removal_failed(self, error_message):
        """Display that removing the default Nginx site failed."""
        self.console_manager.print_step_failure("Nginx", f"Failed to remove default site: {error_message}")
        
    def nginx_default_kept_warning(self):
        """Display warning when default site is kept."""
        self.console_manager.print_warning("Default site kept. This may cause conflicts with your project site.")
        
    def nginx_config_test_failed(self, error_message):
        """Display that Nginx configuration test failed."""
        self.console_manager.print_error(f"Nginx configuration test failed: {error_message}")
        
    def nginx_reload_failed(self, error_message):
        """Display that Nginx reload failed."""
        self.console_manager.print_error(f"Failed to reload Nginx: {error_message}")
        
    def nginx_reload_success(self):
        """Display that Nginx was successfully reloaded."""
        self.console_manager.print_success("Nginx configuration reloaded successfully")