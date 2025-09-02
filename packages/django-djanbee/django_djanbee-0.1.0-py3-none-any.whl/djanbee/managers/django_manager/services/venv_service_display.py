from ...console_manager import ConsoleManager
from ....widgets.question_selector import QuestionSelector


class DjangoEnvironmentServiceDisplay:

    def __init__(self, console_manager: "ConsoleManager"):
        self.console_manager = console_manager

    def lookup_venv(self):
        self.console_manager.print_lookup("Searching for virtual environment")

    def prompt_create_environment(self):
        selector = QuestionSelector(
            "Do you wish to create a virtual environment", self.console_manager
        )
        return selector.select()

    def failure_lookup_venv(self):
        self.console_manager.print_warning_critical("No active virtual environment")

    def failure_lookup_venvs(self):
        self.console_manager.print_warning_critical("No virtual environments found")

    def success_lookup_venv(self):
        self.console_manager.print_success("Virtual environment active")

    def success_locate_env(self, env_name, env_path):
        self.console_manager.print_step_progress(
            f"Found virtual environment {env_name}", env_path
        )
