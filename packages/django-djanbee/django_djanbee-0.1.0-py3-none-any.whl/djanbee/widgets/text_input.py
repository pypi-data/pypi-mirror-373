from typing import Optional, List, Dict, Tuple
from rich.text import Text
from ..managers import ConsoleManager
from .console_widget import ConsoleWidget
from .widget_icons import WidgetIcons
from readchar import key, readkey


class TextInputWidget(ConsoleWidget):
    def __init__(
        self,
        title: str,
        fields: List[Tuple[str, str]],
        console_manager: ConsoleManager,
        create_button_text: str = "Create",
        cancel_button_text: str = "Cancel",
        warning: str = ""
    ):
        """
        Initialize a text input widget with multiple fields.

        Args:
            title: Title for the input panel
            fields: List of tuples containing (field_name, default_value)
            console_manager: Console manager for rendering
            create_button_text: Text for the create/confirm button
            cancel_button_text: Text for the cancel button
            warning: Optional warning message to display
        """
        super().__init__(
            message=title,
            instructions="Use Tab/↑↓/←→ to navigate, Enter to confirm, Ctrl+C to cancel\n\n",
            console_manager=console_manager,
            icon=WidgetIcons.TEXT_INPUT,
            color="blue",
            warning=warning
        )
        
        self.fields = fields
        self.create_button_text = create_button_text
        self.cancel_button_text = cancel_button_text

        # Current state
        self.active_index = 0  # 0 to len(fields)-1 are fields, then buttons
        self.values = [default for _, default in fields]
        self.cursor_positions = [len(default) for _, default in fields]

        # Button indices
        self.create_button_index = len(fields)
        self.cancel_button_index = len(fields) + 1

    def prepare_input_content(self):
        """Prepare the content with all fields and buttons"""
        content = Text()

        # Render fields
        for idx, (field_name, _) in enumerate(self.fields):
            if idx > 0:
                content.append("\n\n")

            # Field label
            content.append(f"{field_name}: ", style="bold")

            # Field input
            field_value = self.values[idx]
            cursor_pos = self.cursor_positions[idx]

            # Active field gets highlighted
            if idx == self.active_index:
                # Split the value at cursor position to show the cursor
                before_cursor = field_value[:cursor_pos]
                after_cursor = field_value[cursor_pos:]

                content.append(before_cursor)
                content.append("█", style="blink")  # Cursor
                content.append(after_cursor, style="")
            else:
                content.append(field_value)

        # Add spacing before buttons
        content.append("\n\n")

        # Render buttons
        create_text = (
            f"→ {self.create_button_text} ←"
            if self.active_index == self.create_button_index
            else f"  {self.create_button_text}  "
        )
        cancel_text = (
            f"→ {self.cancel_button_text} ←"
            if self.active_index == self.cancel_button_index
            else f"  {self.cancel_button_text}  "
        )

        content.append(
            Text(
                create_text,
                style=(
                    "reverse" if self.active_index == self.create_button_index else ""
                ),
            )
        )
        content.append("    ")  # Space between buttons
        content.append(
            Text(
                cancel_text,
                style=(
                    "reverse" if self.active_index == self.cancel_button_index else ""
                ),
            )
        )
        
        return content

    def _render_input_widget(self):
        """Render the text input widget"""
        content = self.prepare_input_content()
        panel = self.construct_panel(content)
        self.render(panel)

    def _handle_text_input(self, k, field_idx):
        """Handle text input for a specific field"""
        # Current state
        current_value = self.values[field_idx]
        cursor_pos = self.cursor_positions[field_idx]

        # Handle backspace
        if k == key.BACKSPACE:  # Backspace
            if cursor_pos > 0:
                # Remove the character before the cursor
                self.values[field_idx] = (
                    current_value[: cursor_pos - 1] + current_value[cursor_pos:]
                )
                self.cursor_positions[field_idx] = cursor_pos - 1
        # Handle delete
        elif k == key.DELETE:
            if cursor_pos < len(current_value):
                # Remove the character at the cursor
                self.values[field_idx] = (
                    current_value[:cursor_pos] + current_value[cursor_pos + 1:]
                )
        # Handle normal character input
        elif len(k) == 1 and k.isprintable():
            # Insert the character at cursor position
            self.values[field_idx] = (
                current_value[:cursor_pos] + k + current_value[cursor_pos:]
            )
            self.cursor_positions[field_idx] = cursor_pos + 1

        return "handled"

    def get_result(self) -> Optional[Dict[str, str]]:
        """
        Run the text input widget and return the entered values.

        Returns:
            Dict mapping field names to values, or None if canceled
        """
        while True:
            self._render_input_widget()

            k = readkey()

            # Handle exit (Ctrl+C, q, Q)
            if self.handle_exit(k):
                return None

            # Tab key to move between fields
            elif k == key.TAB:
                self.active_index = (self.active_index + 1) % (len(self.fields) + 2)

            # Enter key
            elif k == key.ENTER:
                # If on a button
                if self.active_index == self.create_button_index:
                    # Return the field values
                    return {
                        field[0]: value
                        for field, value in zip(self.fields, self.values)
                    }
                elif self.active_index == self.cancel_button_index:
                    return None
                else:
                    # Move to next field or to create button
                    self.active_index = (self.active_index + 1) % (len(self.fields) + 2)

            # Arrow key navigation
            elif k == key.UP or k == key.LEFT:
                # If we're at the Cancel button and want to go left
                if self.active_index == self.cancel_button_index and k == key.LEFT:
                    # Move to Create button
                    self.active_index = self.create_button_index
                else:
                    # Normal backward navigation
                    self.active_index = (self.active_index - 1) % (len(self.fields) + 2)

            elif k == key.DOWN or k == key.RIGHT:
                # If we're at the Create button and want to go right
                if self.active_index == self.create_button_index and k == key.RIGHT:
                    # Move to Cancel button
                    self.active_index = self.cancel_button_index
                else:
                    # Normal forward navigation
                    self.active_index = (self.active_index + 1) % (len(self.fields) + 2)

            # Handle cursor movement within text fields
            elif self.active_index < len(self.fields):
                field_idx = self.active_index
                
                if k == key.RIGHT and self.cursor_positions[field_idx] < len(
                    self.values[field_idx]
                ):
                    # Move cursor right
                    self.cursor_positions[field_idx] += 1
                elif k == key.LEFT and self.cursor_positions[field_idx] > 0:
                    # Move cursor left
                    self.cursor_positions[field_idx] -= 1
                else:
                    # Handle text input if we're on a field
                    self._handle_text_input(k, self.active_index)