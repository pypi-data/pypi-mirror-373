from ...managers import ConsoleManager


class RunDisplay:
    def __init__(self, console_manager: "ConsoleManager"):
        self.console_manager = console_manager

    def show_initialize_start(self, path: str):
        """Show initialization start message"""
        display_path = path or "current directory"
        self.console_manager.print_progress(f"Initializing project in {display_path}")
        
    def show_initialize_complete(self, path: str):
        """Show initialization complete message"""
        display_path = path or "current directory"
        self.console_manager.print_step_progress("Initialize", f"Project initialized in {display_path}")
        
    def show_initialize_failed(self, path: str, error: Exception):
        """Show initialization failed message"""
        display_path = path or "current directory"
        self.console_manager.print_step_failure("Initialize", f"Failed to initialize project in {display_path}")
        self.console_manager.print_error(str(error))
        
    def show_migration_start(self):
        """Show migration start message"""
        self.console_manager.print_progress("Running database migrations")
        
    def show_makemigrations_complete(self):
        """Show makemigrations complete message"""
        self.console_manager.print_step_progress("Migrations", "Migration files created successfully")
        
    def show_migrate_complete(self):
        """Show migrate complete message"""
        self.console_manager.print_step_progress("Migrations", "Database migrated successfully")
        
    def show_migration_failed(self, error: Exception):
        """Show migration failed message"""
        self.console_manager.print_step_failure("Migrations", "Failed to migrate database")
        self.console_manager.print_error(str(error))
        
    def show_collect_static_start(self):
        """Show collectstatic start message"""
        self.console_manager.print_progress("Collecting static files")
        
    def show_collect_static_complete(self):
        """Show collectstatic complete message"""
        self.console_manager.print_step_progress("Static Files", "Static files collected successfully")
        
    def show_collect_static_failed(self, error: Exception):
        """Show collectstatic failed message"""
        self.console_manager.print_step_failure("Static Files", "Failed to collect static files")
        self.console_manager.print_error(str(error))

    def show_critical_warning(self, message: str):
        """Show critical warning message"""
        self.console_manager.print_warning_critical(message)
    
    def show_warning(self, message: str):
        """Show warning message"""
        self.console_manager.print_warning(message)
    
    def show_success(self, message: str):
        """Show success message"""
        self.console_manager.print_success(message)
