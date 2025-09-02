from typing import Dict, Type, Optional, List, Union, cast

from ...settings_service import DjangoSettingsService
from .static_root_handler_display import StaticRootHandlerDisplay
from ...venv_service import DjangoEnvironmentService
from .base_handler import StaticFilesHandler
from .whitenoise_handler import WhiteNoiseHandler
from .nginx_handler import NginxHandler


class StaticFilesHandlerFactory:
    """Factory for creating static files handlers based on the user's selection"""
    
    # Map handler types to their respective classes
    HANDLERS: Dict[str, Type[StaticFilesHandler]] = {
        "whitenoise": WhiteNoiseHandler,
        "nginx": NginxHandler,
    }
    
    @classmethod
    def create_handler(
        cls,
        handler_type: str,
        settings_service: DjangoSettingsService,
        display: StaticRootHandlerDisplay,
        venv_service: DjangoEnvironmentService,
    ) -> Optional[StaticFilesHandler]:
        """
        Create a static files handler based on the user's selection
        
        Args:
            handler_type: The type of handler to create (whitenoise, nginx)
            settings_service: DjangoSettingsService instance
            display: StaticRootHandlerDisplay instance
            venv_service: DjangoEnvironmentService instance
            
        Returns:
            StaticFilesHandler: The appropriate handler instance or None if type not found
        """
        handler_type = handler_type.lower().strip()
        if handler_type not in cls.HANDLERS:
            return None
        
        handler_class = cls.HANDLERS[handler_type]
        return handler_class(settings_service, display, venv_service)
    
    @classmethod
    def get_supported_handlers(cls) -> List[str]:
        """
        Get a list of supported handler types
        
        Returns:
            List[str]: List of supported handler type names
        """
        return list(cls.HANDLERS.keys())
    
    @classmethod
    def register_handler(cls, handler_type: str, handler_class: Type[StaticFilesHandler]) -> None:
        """
        Register a new handler type
        
        Args:
            handler_type: The type/name of the handler
            handler_class: The handler class to register
        """
        cls.HANDLERS[handler_type.lower()] = handler_class