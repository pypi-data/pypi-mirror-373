from typing import Optional, List, Set
from rich.text import Text
from ..managers import ConsoleManager
from .console_widget import ConsoleWidget
from .widget_icons import WidgetIcons
from readchar import key, readkey


class CheckboxSelector(ConsoleWidget):
    def __init__(
        self, 
        message: str, 
        options: List[str], 
        console_manager: ConsoleManager, 
        pre_selected: Optional[List[str]] = None,
        warning: str = ""
    ):
        super().__init__(
            message=message,
            instructions="Use ↑↓ to navigate, Space to toggle, Enter to confirm selection, a to toggle all, Ctrl+C to cancel\n\n",
            console_manager=console_manager,
            icon=WidgetIcons.CHECKBOX,
            color="blue",
            warning=warning
        )
        
        self.cursor_index = 0
        self.selected_indices = set()
        self.options = options
        
        if pre_selected:
            self._set_pre_selected(pre_selected)

    def _set_pre_selected(self, pre_selected: List[str]):
        """
        Set pre-selected options by matching option strings
        
        Args:
            pre_selected: List of option strings that should be pre-selected
        """
        # Find indices of pre-selected options
        for option in pre_selected:
            if option in self.options:
                self.selected_indices.add(self.options.index(option))

    def prepare_checkbox_options(self):
        """Prepare the checkbox selection options."""
        content = Text()

        for idx, option in enumerate(self.options):
            if idx > 0:
                content.append("\n")

            # Show checkbox status
            checkbox = "☑" if idx in self.selected_indices else "☐"

            if idx == self.cursor_index:
                content.append(f"→ {checkbox} {option}", style="reverse")
            else:
                content.append(f"  {checkbox} {option}", style="")
                
        return content

    def _render_checkbox_widget(self):
        """Render the checkbox widget"""
        content = self.prepare_checkbox_options()
        panel = self.construct_panel(content)
        self.render(panel)

    def select(self) -> List[str]:
        """
        Interactive checkbox selection with arrow key navigation.

        Returns:
            List of selected option strings or empty list if canceled
        """
        while True:
            self._render_checkbox_widget()
            
            k = readkey()
            
            # Handle arrow keys
            if k == key.UP:
                self.cursor_index = (self.cursor_index - 1) % len(self.options)
            elif k == key.DOWN:
                self.cursor_index = (self.cursor_index + 1) % len(self.options)
            
            # Space key to toggle selection
            elif k == key.SPACE:
                if self.cursor_index in self.selected_indices:
                    self.selected_indices.remove(self.cursor_index)
                else:
                    self.selected_indices.add(self.cursor_index)
            
            # 'a' key to select all
            elif k.lower() == "a":
                if len(self.selected_indices) == len(self.options):
                    # If all are selected, deselect all
                    self.selected_indices.clear()
                else:
                    # Otherwise select all
                    self.selected_indices = set(range(len(self.options)))
            
            # Enter key to confirm selection
            elif k == key.ENTER:
                return [self.options[i] for i in self.selected_indices]
            
            # Handle exit (Ctrl+C, q, Q)
            if self.handle_exit(k):
                return []