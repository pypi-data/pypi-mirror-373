from typing import Union
from rich.text import Text
from rich.panel import Panel
from rich import box
from ..managers import ConsoleManager
from .widget_icons import WidgetIcons
from .base_widget import BaseConsoleWidget
import readchar

class ConsoleWidget(BaseConsoleWidget):
    def __init__(
        self, 
        message: str, 
        instructions: str,
        console_manager: ConsoleManager,
        icon: Union[str, WidgetIcons] = "",
        color: str = "blue",
        warning: str = ""
    ) -> None:
        self.message = message
        self.instructions = instructions
        self.console_manager = console_manager
        self.icon = icon.value if isinstance(icon, WidgetIcons) else icon
        self.color = color
        self.warning = warning
        self._first_render = False
        self._panel_lines: int = 0

    def construct_panel(self, content: Union[str, Text]) -> Panel:
        instructions = self._prepare_instructions()
        message = self._prepare_message()
        warning = self._prepare_warning()

        panel_content = Text.assemble(
             '\n', message, instructions, warning, content, '\n'
        )

        return Panel(panel_content, border_style=self.color, box=box.HEAVY)

    def _prepare_message(self) -> Text:
        """Create formatted message text with icon and colored text"""
        text = Text()
        if self.icon:
            text.append(f"{self.icon} ", style="")
        text.append(self.message, style=f"bold {self.color}")
        text.append("\n\n")
        return text
    
    def _prepare_instructions(self) -> Text:
        """Create formatted instruction text"""
        instructions = Text(
            self.instructions,
            style="dim",
        )
        return instructions
    
    def _prepare_warning(self) -> Text:
        """Format warning message if present"""
        text = Text()
        if self.warning:
            text.append("!!! ", style="yellow") 
            text.append(self.warning, style="yellow")
            text.append("\n\n")
        return text

    def render(self, panel: Panel) -> None:
        # Calculate the current panel height based on content
        content_str = str(panel.renderable)
        content_lines = content_str.count('\n') + 1  # +1 for the last line
        current_panel_height = content_lines + 2  # +2 for top and bottom borders
        
        if self._first_render:
            # Not the first render, need to clear previous panel
            # Move cursor up by the number of lines in the previous panel
            print(f"\033[{self._panel_lines}A", end="")
            # Clear from cursor to end of screen
            print("\033[J", end="")
        else:
            self._first_render = True
        
        # Save the current panel height for next render
        self._panel_lines = current_panel_height
        
        # Print the panel
        self.console_manager.console.print(panel)
    
    def handle_exit(self, k):
        if k in (readchar.key.CTRL_C, 'q', 'Q'):
                return True