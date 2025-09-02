from typing import Optional, List
from rich.text import Text
from ..managers import ConsoleManager
from .console_widget import ConsoleWidget
from .widget_icons import WidgetIcons
from readchar import key, readkey


class ListSelector(ConsoleWidget):
    def __init__(
        self, 
        message: str, 
        options: List[str], 
        console_manager: ConsoleManager,
        warning: str = ""
    ):
        super().__init__(
            message=message,
            instructions="Use ↑↓ to navigate, Enter to select, number keys for direct choice, Ctrl+C to cancel\n\n",
            console_manager=console_manager,
            icon=WidgetIcons.LIST,
            color="blue",
            warning=warning
        )

        self.selected_index = 0
        self.options = options
        
    def prepare_list_options(self):
        list_options = Text()

        for idx, option in enumerate(self.options):
            if idx > 0:
                list_options.append("\n")

            if idx == self.selected_index:
                list_options.append(f"→ {option} ←", style="reverse")
            else:
                list_options.append(f"  {option}  ", style="")
        
        return list_options

    def _render_list_widget(self):
        """Render the list """
        content = self.prepare_list_options()
        panel = self.construct_panel(content)
        self.render(panel)

    def select(self) -> Optional[str]:
        """
        Interactive list selection with arrow key navigation.

        Returns:
            Selected option string or None for cancel
        """
        while True:
            self._render_list_widget()
            k = readkey()
            
            # Handle number key input for direct selection
            if k.isdigit():
                num = int(k)
                if 1 <= num <= len(self.options):
                    return self.options[num - 1]

            # Handle arrow keys using readchar's constants
            elif k == key.UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif k == key.DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            
            # Handle Enter key
            elif k == key.ENTER:
                return self.options[self.selected_index]
            
            # Handle Escape or Ctrl+C
            if self.handle_exit(k):
                return None