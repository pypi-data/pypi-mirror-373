from typing import Optional, List
from .display import LaunchDisplay
from ...core import AppContainer


class LaunchManager:
    """Manages Django project initialization, selection, and command menu."""
    
    def __init__(self, display: LaunchDisplay, app: AppContainer) -> None:
        self.display = display
        self.app = app

    def launch_project(self, path: str = "") -> Optional[object]:
        """Initialize environment and select Django project.
        
        Args:
            path: Optional path to Django project directory
            
        Returns:
            Selected project object or None if no project found
        """
        # Show splash screen
        self.display.display_splash_screen()

        # Initialize working directory
        self.app.django_manager.project_service.initialize_directory(path)

        # Find and select Django project
        return self.app.django_manager.project_service.select_project()
    
    def select_launch_options(self) -> List[str]:
        """
        Display command selection interface and return selected commands.
        
        Returns:
            List of command names (without descriptions) that were selected and confirmed
        """
        # Get selected commands
        selected_options = self.display.display_command_selection()
        
        # If nothing selected, return empty list
        if not selected_options:
            return []
        
        # Get confirmation
        confirmed = self.display.display_confirmation(selected_options)
        if not confirmed:
            return []
        
        # Extract command names (before the " - " in each option)
        return [option.split(" - ")[0].strip() for option in selected_options]