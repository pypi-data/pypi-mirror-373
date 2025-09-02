from pathlib import Path
from typing import Optional, Dict, List, Union, Tuple, cast

from ...settings_service import DjangoSettingsService
from .static_root_handler_display import StaticRootHandlerDisplay
from ...venv_service import DjangoEnvironmentService
from .handler_factory import StaticFilesHandlerFactory


class StaticRootHandler:
    """Main handler for configuring static files in Django projects"""
    
    def __init__(
        self,
        settings_service: DjangoSettingsService,
        display: StaticRootHandlerDisplay,
        venv_service: DjangoEnvironmentService,
    ) -> None:
        """
        Initialize the StaticRootHandler
        
        Args:
            settings_service: Service for managing Django settings
            display: Display service for user interaction
            venv_service: Service for virtual environment operations
        """
        self.settings_service = settings_service
        self.display = display
        self.venv_service = venv_service
        
    def handle_static_root(self) -> bool:
        """
        Handle the configuration of static files based on user selection
        
        Returns:
            bool: True if setup was successful, False otherwise
        """
        # Prompt user to select which static files strategy to use
        result = self.display.prompt_static_files_solution()
        if result is None:
            return False 

        if not result:
            return False
            
        # Create appropriate handler using factory
        handler = StaticFilesHandlerFactory.create_handler(
            result,
            self.settings_service,
            self.display,
            self.venv_service
        )
        
        if not handler:
            self.display.error_unsupported_handler(result)
            return False
            
        # Handle the static files configuration
        success = handler.handle()
        
        if success is None:
            return False
        
        if success:
            self.display.success_static_files_setup(result)
        else:
            self.display.error_static_files_setup(result)
            
        return success