from pathlib import Path
from typing import Tuple, Dict, Optional, Union, List, Any, cast

from .base_handler import StaticFilesHandler
from ...settings_service import DjangoSettingsService
from .static_root_handler_display import StaticRootHandlerDisplay
from ...venv_service import DjangoEnvironmentService


class NginxHandler(StaticFilesHandler):
    """Handler for configuring Nginx static files in Django"""

    def handle(self) -> bool:
        """
        Configure Django settings for Nginx static files handling
        
        Returns:
            bool: True if setup was successful, False otherwise
        """
        # Configure basic static file settings using parent class methods
        static_url = self.settings_service.find_in_settings("STATIC_URL", default="")
        new_url = self.display.input_static_url(static_url)
        
        if new_url is None:
            return None
        
        if not super().setup_static_url(new_url):
            return False
        
        if not super().setup_static_root():
            return False
        
        if not super().setup_staticfiles_dirs("Nginx"):
            return False
        
        # Configure media settings if needed
        if not self.setup_media_settings():
            return False
                
        return True

    def setup_media_settings(self) -> bool:
        """
        Configure MEDIA_URL and MEDIA_ROOT settings
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Configure MEDIA_URL
        media_url = self.settings_service.find_in_settings("MEDIA_URL")
        if media_url != "/media/":
            self.display.print_progress_media_url()
            result = self.settings_service.edit_settings("MEDIA_URL", "/media/")
            success = result[0] if isinstance(result, tuple) else result
            if not success:
                return False
        
        # Configure MEDIA_ROOT
        media_root = self.settings_service.find_in_settings("MEDIA_ROOT")
        if not media_root:
            self.display.print_progress_media_root()
            
            # Ensure os is imported
            has_os = self.settings_service.is_library_imported("os")
            if not has_os:
                self.settings_service.add_library_import("os")
                self.display.print_progress_media_root_add_os()
            
            # Set MEDIA_ROOT
            result = self.settings_service.replace_settings(
                "MEDIA_ROOT", "os.path.join(BASE_DIR, 'media')"
            )
            if not result[0]:
                return False
        
        self.display.success_progress_media_settings("/media/", "os.path.join(BASE_DIR, 'media')")
        return True

