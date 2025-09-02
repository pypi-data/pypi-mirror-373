from typing import Optional
from rich.text import Text
from ..managers import ConsoleManager
from .console_widget import ConsoleWidget
from .widget_icons import WidgetIcons
from readchar import key, readkey


class QuestionSelector(ConsoleWidget):
    def __init__(
        self, 
        message: str, 
        console_manager: ConsoleManager, 
        positive_command="yes", 
        negative_command="no", 
        warning=""
    ):
        super().__init__(
            message=message,
            instructions="Use ←→ or ↑↓ to navigate, Enter to select, Y/N for direct choice, Ctrl+C to cancel\n\n",
            console_manager=console_manager,
            icon=WidgetIcons.QUESTION,
            color="blue",
            warning=warning
        )
        
        self.selected_index = 0  # 0 for Yes, 1 for No
        self.positive_command = positive_command
        self.negative_command = negative_command

    def prepare_options(self):
        """Prepare the Yes/No selection options."""
        yes_text = f"→ {self.positive_command} ←" if self.selected_index == 0 else f"  {self.positive_command}  "
        no_text = f"→ {self.negative_command} ←" if self.selected_index == 1 else f"  {self.negative_command}  "
        
        content = Text()
        content.append(yes_text, style="reverse" if self.selected_index == 0 else "")
        content.append("    ")
        content.append(no_text, style="reverse" if self.selected_index == 1 else "")
        
        return content

    def _render_question_widget(self):
        """Render the question widget"""
        content = self.prepare_options()
        panel = self.construct_panel(content)
        self.render(panel)

    def select(self) -> Optional[bool]:
        """
        Interactive Yes/No selection with arrow key navigation.
        
        Returns:
            True for Yes, False for No, None for cancel
        """
        while True:
            self._render_question_widget()
            
            k = readkey()
            
            # Handle direct Y/N input
            if k.lower() == 'y':
                return True
            elif k.lower() == 'n':
                return False
            
            # Arrow key handling
            elif k == key.LEFT or k == key.UP:
                self.selected_index = 0
            elif k == key.RIGHT or k == key.DOWN:
                self.selected_index = 1
            
            # Enter key
            elif k == key.ENTER:
                return self.selected_index == 0
            
            # Handle exit (Ctrl+C, q, Q)
            if self.handle_exit(k):
                return None