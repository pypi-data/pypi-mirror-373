from ...console_manager import ConsoleManager


class DjangoSettingsServiceDisplay:

    def __init__(self, console_manager: "ConsoleManager"):
        self.console_manager = console_manager

    def print_lookup_settings(self):
        self.console_manager.print_lookup("Looking for settings.py")

    def error_found_settings(self):
        self.console_manager.print_error("Did not find settings.py")

    def success_found_settings(self, path):
        self.console_manager.print_step_progress(
            "Looking for settings.py", f"Found settings.py in {path}"
        )
