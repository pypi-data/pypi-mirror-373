from ...console_manager import ConsoleManager
from ....widgets.question_selector import QuestionSelector


class DjangoRequirementsServiceDisplay:

    def __init__(self, console_manager: "ConsoleManager"):
        self.console_manager = console_manager

    def lookup_requirements(self):
        self.console_manager.print_lookup("Looking for requirements")

    def failure_lookup_requirements(self):
        self.console_manager.print_error("No requirements file found")

    def prompt_extract_requirements(self):
        selector = QuestionSelector(
            "Do you wish to extract requirements", self.console_manager
        )
        return selector.select()

    def success_lookup_requirements(self, path):
        self.console_manager.print_step_progress("Found requirements.txt", path)

    def prompt_install_requirements(self):
        selector = QuestionSelector(
            "Do you wish to install requirements", self.console_manager
        )
        return selector.select()

    def progress_install_requirements(self):
        self.console_manager.print_progress("Installing requirements")

    def success_install_requirements(self, requirements, env):
        self.console_manager.print_success(
            f"Requirements {requirements} installed ito {env}"
        )
