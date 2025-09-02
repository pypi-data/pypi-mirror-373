from rich.panel import Panel
from rich.text import Text
from rich import box
from ...managers import ConsoleManager
from ...widgets.checkbox_selector import CheckboxSelector
from typing import List, Optional


class LaunchDisplay:
    """Handles display output for the launch command."""
    
    def __init__(self, console_manager: ConsoleManager) -> None:
        self.console_manager = console_manager

    def display_splash_screen(self) -> None:
        """Display welcome splash screen with service info."""
        # Display bee logo
        self.console_manager.print_logo()
        
        # Display warning about privileges
        warning = Text(
            "The setup might require root privileges",
            style="yellow",
            justify="center",
        )
        
        self.console_manager.console.print(Panel(warning, box=box.SIMPLE, style="blue"))
        
    def display_command_selection(self, pre_selected: Optional[List[str]] = None) -> List[str]:
        """
        Display checkbox selection menu for commands.
        
        Args:
            message: The prompt message to display
            options: List of options to select from
            pre_selected: List of options that should be pre-selected (optional)
            
        Returns:
            List of selected options, or empty list if none selected
        """
        
        options = [
            "setup - Install virtual environment and project dependencies",
            "configure - Modify Django settings and database connections",
            "deploy - Set up Gunicorn service and Nginx web server",
            "run - Apply migrations and collect static files"
        ]
        
        message = "Select commands to execute:"

        selector = CheckboxSelector(
            message=message,
            options=options,
            console_manager=self.console_manager,
            pre_selected=pre_selected
        )
        
        selected_options = selector.select()
        
        # Return empty list if cancelled
        if selected_options is None:
            return []
            
        return selected_options
    
    def display_confirmation(self, selected_options: List[str]) -> bool:
        """
        Display confirmation message for selected options.
        
        Args:
            selected_options: List of options that were selected
            
        Returns:
            True if confirmed, False otherwise
        """
        if not selected_options:
            self.console_manager.console.print("No options selected.", style="yellow")
            return False
        
        # Format selected options for display
        options_text = Text()
        for i, option in enumerate(selected_options):
            options_text.append(f"• {option}")
            if i < len(selected_options) - 1:
                options_text.append("\n")
        
        # Create confirmation panel
        content = Text.assemble(
            Text("The following options will be executed:", style="blue"), 
            "\n\n",
            options_text,
            "\n\n",
            Text("Press Enter to confirm or Ctrl+C to cancel", style="dim")
        )
        
        panel = Panel(content, title="Confirmation", border_style="blue")
        self.console_manager.console.print(panel)
        
        # Wait for confirmation
        try:
            input()
            return True
        except KeyboardInterrupt:
            self.console_manager.console.print("Operation cancelled.", style="yellow")
            return False
