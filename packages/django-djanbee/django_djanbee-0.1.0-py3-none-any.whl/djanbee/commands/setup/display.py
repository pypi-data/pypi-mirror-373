from ...widgets.question_selector import QuestionSelector
from ...managers import ConsoleManager


class SetupDisplay:
    def __init__(self, console_manager: "ConsoleManager"):
        self.console_manager = console_manager
