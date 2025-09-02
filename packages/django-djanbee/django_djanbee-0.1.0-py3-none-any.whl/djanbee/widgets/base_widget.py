from abc import ABC, abstractmethod
from typing import Union
from rich.text import Text
from rich.panel import Panel
from ..managers import ConsoleManager
from .widget_icons import WidgetIcons

class BaseConsoleWidget(ABC):
    """Abstract base class defining the interface for console widgets."""
    
    @abstractmethod
    def __init__(
        self, 
        message: str, 
        instructions: str,
        console_manager: ConsoleManager,
        icon: Union[str, WidgetIcons] = "",
        color: str = "blue"
    ) -> None:
        """Initialize the console widget with required parameters."""
        pass
    
    @abstractmethod
    def construct_panel(self, content: Union[str, Text]) -> Panel:
        """Construct a panel with the provided content."""
        pass
    
    @abstractmethod
    def _prepare_message(self) -> Text:
        """Create formatted message text with icon and colored text."""
        pass
    
    @abstractmethod
    def _prepare_instructions(self) -> Text:
        """Create formatted instruction text."""
        pass
    
    @abstractmethod
    def render(self, panel: Panel) -> None:
        """Render the panel to the console."""
        pass