from ..settings_service import DjangoSettingsService
from .debug_handler_display import DebugHandlerDisplay


class DebugHandler:
    """Handler for Django secret key operations"""

    def __init__(
        self, settings_service: DjangoSettingsService, display: DebugHandlerDisplay
    ):
        self.settings_service = settings_service
        self.display = display

    def handle_debug(self):
        # Check if DEBUG exists in settings
        current_debug = self.settings_service.find_in_settings("DEBUG", None)
        self.display.lookup_debug()

        # If DEBUG doesn't exist, create it and set to True
        if current_debug is None:
            self.display.failure_lookup_debug()
            self.display.progress_create_debug()
            self.settings_service.edit_settings("DEBUG", True)
        else:
            self.display.success_lookup_debug(current_debug)

        result = self.display.prompt_change_debug(current_debug)
        if not result:
            print("Cancelled")
            return None

        self.settings_service.edit_settings("DEBUG", not current_debug)
