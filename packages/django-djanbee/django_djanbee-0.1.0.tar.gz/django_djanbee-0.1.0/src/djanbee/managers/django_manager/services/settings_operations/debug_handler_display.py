from ....console_manager import ConsoleManager
from .....widgets.question_selector import QuestionSelector


class DebugHandlerDisplay:

    def __init__(self, console_manager: "ConsoleManager"):
        self.console_manager = console_manager

    def lookup_debug(self):
        self.console_manager.print_lookup("Looking for debug variable")

    def failure_lookup_debug(self):
        self.console_manager.print_warning_critical("Debug not found")

    def progress_create_debug(self):
        self.console_manager.print_progress("Creating DEBUG and setting to TRUE")

    def success_lookup_debug(self, current_value):
        self.console_manager.print_step_progress(
            "DEBUG", f"Current value {current_value}"
        )

    def prompt_change_debug(self, current_value: bool):
        warning = ""
        if current_value:
            warning = "Do this only when deploying website to production"
        selector = QuestionSelector(
            f"This action will change DEBUG to {not current_value} \n Are you sure",
            self.console_manager,
            "Yes",
            "No",
            warning,
        )
        return selector.select()

    def success_change_debug(self):
        self.console_manager.print_success("Debug successfully changed")
