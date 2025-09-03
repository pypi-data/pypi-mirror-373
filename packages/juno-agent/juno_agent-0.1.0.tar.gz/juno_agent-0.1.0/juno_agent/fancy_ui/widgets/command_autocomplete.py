"""Command autocomplete dropdown widget."""

from typing import List, Optional, Tuple
from textual import events
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static


class CommandOption(Static):
    """A single command option in the autocomplete dropdown."""
    
    DEFAULT_CSS = """
    CommandOption {
        height: 1;
        padding: 0 1;
        margin: 0;
        background: transparent;
        color: $text;
    }
    
    CommandOption.selected {
        background: $primary;
        color: $background;
    }
    
    CommandOption:hover {
        background: $accent;
        color: $background;
    }
    """
    
    def __init__(self, command: str, description: str, **kwargs):
        """Initialize command option.
        
        Args:
            command: The command name (e.g., "/cost")
            description: The command description
        """
        self.command = command
        self.description = description
        # Format: "/command    - description"
        display_text = f"{command:<12} - {description}"
        super().__init__(display_text, **kwargs)


class CommandAutocomplete(Widget):
    """Autocomplete dropdown for chat commands."""
    
    DEFAULT_CSS = """
    CommandAutocomplete {
        display: none;
        height: auto;
        max-height: 8;
        background: $surface;
        border: round $primary;
        margin-top: 0;
        margin-bottom: 0;
        margin-left: 1;
        margin-right: 1;
    }
    
    CommandAutocomplete.visible {
        display: block;
    }
    """
    
    # Available commands with descriptions
    COMMANDS = [
        ("/cost", "Show the total cost and duration of the current session"),
        ("/new-chat", "Clear conversation history and free up context. Optional: /compact [instructions for summarization]"),
        ("/reset", "Clear conversation history and free up context"),
        ("/compact", "Clear conversation history but keep a summary in context. Optional: /compact [instructions for summarization]"),
        ("/history", "View and manage conversation history"),
        ("/setup", "Run the setup wizard to configure juno-agent (API key, editor, model, etc.)"),
        ("/model", "Configure AI model, provider, and API keys"),
    ]
    
    class CommandSelected(Message):
        """Message sent when a command is selected."""
        
        def __init__(self, command: str):
            super().__init__()
            self.command = command
    
    class AutocompleteEscape(Message):
        """Message sent when autocomplete should be dismissed."""
        pass
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filtered_commands: List[Tuple[str, str]] = []
        self.selected_index = 0
        self.is_visible = False
    
    @property
    def can_focus(self) -> bool:
        """This widget can receive focus when visible."""
        return self.is_visible
    
    def compose(self) -> ComposeResult:
        """Compose the autocomplete dropdown."""
        self.container = Vertical(id="autocomplete-container")
        yield self.container
    
    def show(self, filter_text: str = "") -> None:
        """Show the autocomplete dropdown with filtered commands.
        
        Args:
            filter_text: Text to filter commands by (e.g., "/c" filters to commands starting with "/c")
        """
        # Filter commands based on input
        if filter_text == "/":
            # Show all commands when just "/" is typed
            self.filtered_commands = self.COMMANDS[:]
        else:
            # Filter commands that start with the filter text
            self.filtered_commands = [
                (cmd, desc) for cmd, desc in self.COMMANDS 
                if cmd.startswith(filter_text.lower())
            ]
        
        # Only show if there are matching commands
        if self.filtered_commands:
            self.selected_index = 0
            self.is_visible = True
            # Clear any existing options first
            self._clear_options()
            # Update options with new filtered commands
            self._update_options()
            # Make visible
            self.add_class("visible")
        else:
            self.hide()
    
    def hide(self) -> None:
        """Hide the autocomplete dropdown."""
        self.remove_class("visible")
        self.is_visible = False
        self.selected_index = 0
        self.filtered_commands = []
        # Clear all options
        self._clear_options()
    
    def _clear_options(self) -> None:
        """Clear all option widgets from the container."""
        try:
            container = getattr(self, 'container', None)
            if container is None:
                try:
                    container = self.query_one("#autocomplete-container", Vertical)
                except:
                    return
            
            if container:
                for child in list(container.children):
                    child.remove()
        except Exception:
            # Fallback: try to clear from widget itself
            for child in list(self.children):
                if hasattr(child, 'remove'):
                    child.remove()
    
    def _update_options(self) -> None:
        """Update the displayed command options."""
        try:
            # Get the container, either from instance or by querying
            container = getattr(self, 'container', None)
            if container is None:
                try:
                    container = self.query_one("#autocomplete-container", Vertical)
                except:
                    # Container not found, skip update
                    return
            
            # Add filtered options to container
            if container:
                for i, (command, description) in enumerate(self.filtered_commands):
                    option = CommandOption(command, description)
                    if i == self.selected_index:
                        option.add_class("selected")
                    container.mount(option)
        except Exception as e:
            # If mounting fails, we should at least not crash
            # This might happen during widget lifecycle transitions
            pass
    
    def navigate_up(self) -> None:
        """Navigate to previous option."""
        if not self.is_visible or not self.filtered_commands:
            return
        
        self.selected_index = (self.selected_index - 1) % len(self.filtered_commands)
        self._update_selection()
    
    def navigate_down(self) -> None:
        """Navigate to next option."""
        if not self.is_visible or not self.filtered_commands:
            return
        
        self.selected_index = (self.selected_index + 1) % len(self.filtered_commands)
        self._update_selection()
    
    def _update_selection(self) -> None:
        """Update the visual selection of options."""
        try:
            options = self.query(CommandOption)
            for i, option in enumerate(options):
                if i == self.selected_index:
                    option.add_class("selected")
                else:
                    option.remove_class("selected")
        except Exception:
            # If querying fails, skip the update
            # This might happen during widget lifecycle transitions
            pass
    
    def select_current(self) -> None:
        """Select the currently highlighted command."""
        if not self.is_visible or not self.filtered_commands:
            return
        
        selected_command = self.filtered_commands[self.selected_index][0]
        self.post_message(self.CommandSelected(selected_command))
        self.hide()
    
    def get_selected_command(self) -> Optional[str]:
        """Get the currently selected command."""
        if not self.is_visible or not self.filtered_commands:
            return None
        
        return self.filtered_commands[self.selected_index][0]
    
    def on_key(self, event: events.Key) -> None:
        """Handle key events for navigation."""
        if not self.is_visible:
            return
        
        if event.key == "up":
            self.navigate_up()
            event.prevent_default()
        elif event.key == "down":
            self.navigate_down()
            event.prevent_default()
        elif event.key == "enter" or event.key == "tab":
            self.select_current()
            event.prevent_default()
        elif event.key == "escape":
            self.post_message(self.AutocompleteEscape())
            self.hide()
            event.prevent_default()
    
