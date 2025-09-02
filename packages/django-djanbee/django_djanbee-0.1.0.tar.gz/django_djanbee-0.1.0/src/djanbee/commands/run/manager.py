from ...core import AppContainer
from .display import RunDisplay
from typing import Dict


class RunManager:
    def __init__(self, display: "RunDisplay", app: "AppContainer"):
        self.display = display
        self.app = app
        self.operation_results = {
            "Project Initialization": False,
            "Database Migrations": False,
            "Static Files Collection": False
        }
    
    def initialize_project(self, path: str = "") -> bool:
        """
        Initialize the Django project in the specified directory
        
        Args:
            path: Path to initialize the project (empty for current directory)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.display.show_initialize_start(path)
            # Initialize working directory
            self.app.django_manager.project_service.initialize_directory(path)
            self.display.show_initialize_complete(path)
            self.operation_results["Project Initialization"] = True
            return True
        except Exception as e:
            self.display.show_initialize_failed(path, e)
            self.operation_results["Project Initialization"] = False
            return False
    
    def migrate_database(self) -> bool:
        """
        Run database migrations
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.display.show_migration_start()
            
            # Create migration files
            makemigrations_result = self.app.os_manager.run_python_command(["manage.py", "makemigrations"])
            if makemigrations_result.success:
                self.display.show_makemigrations_complete()
            else:
                raise Exception("Failed to create migration files")
            
            # Apply migrations
            migrate_result = self.app.os_manager.run_python_command(["manage.py", "migrate"])
            if migrate_result.success:
                self.display.show_migrate_complete()
                self.operation_results["Database Migrations"] = True
                return True
            else:
                raise Exception("Failed to apply migrations")
        except Exception as e:
            self.display.show_migration_failed(e)
            self.operation_results["Database Migrations"] = False
            return False

    def collect_static_files(self) -> bool:
        """
        Collect static files
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.display.show_collect_static_start()
            result = self.app.os_manager.run_python_command(["manage.py", "collectstatic", "--noinput"])
            if result.success:
                self.display.show_collect_static_complete()
                self.operation_results["Static Files Collection"] = True
                return True
            else:
                raise Exception("Failed to collect static files")
        except Exception as e:
            self.display.show_collect_static_failed(e)
            self.operation_results["Static Files Collection"] = False
            return False
    
    def run_all_operations(self, path: str = "") -> Dict[str, bool]:
        """
        Run all operations in sequence
        
        Args:
            path: Path to initialize the project (empty for current directory)
            
        Returns:
            Dict[str, bool]: Results of all operations
        """
        # Initialize project
        if not self.initialize_project(path):
            self.display.show_warning("Project initialization failed. Subsequent steps may not work correctly.")
        
        # Migrate database
        if not self.migrate_database():
            self.display.show_warning("Database migration failed. This may cause issues with the application.")
        
        # Collect static files
        if not self.collect_static_files():
            self.display.show_warning("Static file collection failed. The application may not display correctly.")        
        
        # Show overall status
        if all(self.operation_results.values()):
            self.display.show_success("All operations completed successfully!")
        else:
            self.display.show_critical_warning("Some operations failed. Please check the logs for details.")
        
        return self.operation_results