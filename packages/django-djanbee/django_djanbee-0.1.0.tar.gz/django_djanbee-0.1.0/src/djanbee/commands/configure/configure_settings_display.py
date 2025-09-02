from ...managers import ConsoleManager
from ...widgets.checkbox_selector import CheckboxSelector


class ConfigureSettingsDisplay:
    def __init__(self, console_manager: "ConsoleManager"):
        self.console_manager = console_manager

    def prompt_configure_menu(self):
        options = [
            "Generate secret key",
            "Manage ALLOWED_HOSTS",
            "Manage databases",
            "Set up STATIC_ROOT",
            "Enable SSL settings (does not generate a certificate)",
            "Disable/Enable DEBUG",
        ]

        result = CheckboxSelector(
            "Select settings to configure:", options, self.console_manager
        )
        return result.select()

    def success_settings_configure(self):
        self.console_manager.print_success("Settings successfully configured")
