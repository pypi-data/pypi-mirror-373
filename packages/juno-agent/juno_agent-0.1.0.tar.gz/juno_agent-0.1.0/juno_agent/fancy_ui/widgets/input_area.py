"""Chat input area widget."""

from textual import events
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import TextArea
from .command_autocomplete import CommandAutocomplete
from .history_autocomplete import HistoryAutocomplete
from ..utils.command_history import CommandHistoryManager


class CustomTextArea(TextArea):
    """Custom TextArea that forwards key events to parent."""
    
    def __init__(self, parent_input=None, **kwargs):
        super().__init__(**kwargs)
        self.parent_input = parent_input
    

    
    async def _on_key(self, event: events.Key) -> None:
        """Handle key events with special logic for Enter, Ctrl+J, and autocomplete navigation."""
        # print(f"CustomTextArea._on_key: {event.key}")
        # Handle Ctrl+J - insert newline
        if event.key == "ctrl+j":
            event.stop()
            event.prevent_default()
            self.insert("\n")
            return
        
        # Handle autocomplete navigation keys and Enter when autocomplete is visible
        if event.key in ("up", "down", "escape", "tab", "enter") and self.parent_input:
            # Check if autocomplete is visible and should handle this key
            if self.parent_input.should_autocomplete_handle_key(event.key):
                event.stop()
                event.prevent_default()
                self.parent_input.handle_autocomplete_key(event)
                return
        
        # Handle regular Enter - check with parent first (only if autocomplete didn't handle it)
        if event.key == "enter":
            if self.parent_input and self.parent_input.should_submit_on_enter():
                event.stop()
                event.prevent_default()
                self.parent_input.on_enter_pressed()
                return
            # If parent doesn't want to submit, let TextArea handle normally (insert newline)
        
        # Forward navigation/special keys to parent input handler
        # Only handle special keys that should affect application state
        if self.parent_input and event.key in ("up", "down", "ctrl+up", "ctrl+down", "page_up", "page_down", "home", "end", "ctrl+home", "ctrl+end"):
            if self.parent_input.handle_key_event(event):
                # Parent handled the event, prevent default
                event.prevent_default()
                return
        # For all other keys, let TextArea handle normally
        await super()._on_key(event)


class ChatInput(Widget):
    """Enhanced chat input widget with multiline support."""
    
    DEFAULT_CSS = """
    ChatInput {
        dock: bottom;
        height: auto;
        min-height: 4;
        max-height: 10;
        margin: 1;
    }
    
    ChatInput TextArea {
        min-height: 3;
        max-height: 8;
        scrollbar-size: 1 1;
        border: round $primary;
    }
    
    ChatInput TextArea:focus {
        border: round $accent;
    }
    """
    
    class Submit(Message):
        """Message sent when user submits input."""
        
        def __init__(self, content: str):
            super().__init__()
            self.content = content
    
    def __init__(self, storage_manager=None, **kwargs):
        super().__init__(**kwargs)
        self.autocomplete_widget = None
        self.history_autocomplete_widget = None
        self.file_autocomplete_widget = None  # Will be set by app
        self.storage_manager = storage_manager
        self.command_history = CommandHistoryManager()
        self._is_navigating_history = False
        self._at_trigger_position = -1  # Track @ position for file autocomplete
        self._just_selected_file = False  # Track if we just selected a file to prevent re-triggering
    
    def compose(self) -> ComposeResult:
        """Compose the input area."""        
        # Autocomplete dropdowns (initially hidden)
        self.autocomplete_widget = CommandAutocomplete()
        yield self.autocomplete_widget
        
        # File autocomplete is now at app level, not here
        
        # History autocomplete dropdown (initially hidden)
        self.history_autocomplete_widget = HistoryAutocomplete(self.storage_manager) if self.storage_manager else None
        if self.history_autocomplete_widget:
            yield self.history_autocomplete_widget
        
        # Input field - Using CustomTextArea for multiline support with key forwarding
        yield CustomTextArea(
            parent_input=self,
            text="",
            id="chat-input",
            show_line_numbers=False
        )
    
    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Handle text area changes to show/hide autocomplete and manage history navigation."""
        current_value = event.text_area.text
        cursor_line, cursor_column = event.text_area.cursor_location
        
        # Get current line text up to cursor
        lines = current_value.split('\n')
        if cursor_line < len(lines):
            current_line = lines[cursor_line][:cursor_column]
        else:
            current_line = ""
        
        # Check for @ trigger in current line
        at_index = current_line.rfind('@')
        
        # Handle file autocomplete with @
        if at_index >= 0 and self.file_autocomplete_widget:
            # Check if @ is at word boundary (not part of email, etc)
            if at_index == 0 or current_line[at_index - 1] in ' \t\n':
                # Extract query after @
                query = current_line[at_index + 1:]
                # Show file autocomplete if no space after @ and not just selected a file
                if ' ' not in query and not getattr(self, '_just_selected_file', False):
                    # Also don't show if query looks like a completed path (ends with / or has extension)
                    if not (query.endswith('/') or ('.' in query.split('/')[-1] and len(query.split('/')[-1]) > 1)):
                        self._at_trigger_position = at_index
                        self.file_autocomplete_widget.show_for_query(query)
                        # Hide other autocompletes
                        if self.autocomplete_widget:
                            self.autocomplete_widget.hide()
                        if self.history_autocomplete_widget:
                            self.history_autocomplete_widget.hide()
                        return
                # Space after @ or completed path, hide file autocomplete
                self.file_autocomplete_widget.hide()
                self._at_trigger_position = -1
        else:
            # No @ trigger, hide file autocomplete
            if self.file_autocomplete_widget:
                self.file_autocomplete_widget.hide()
                self._at_trigger_position = -1
        
        # Handle command autocomplete
        if not self.autocomplete_widget:
            return
        
        # Show command autocomplete if input starts with "/" but is not "/history"
        if current_value.startswith("/") and not current_value.startswith("/history"):
            # Extract the command part (everything before first space or end of string)
            command_part = current_value.split()[0] if " " in current_value else current_value
            self.autocomplete_widget.show(command_part)
            # Hide history autocomplete
            if self.history_autocomplete_widget:
                self.history_autocomplete_widget.hide()
        else:
            # Hide command autocomplete if not typing a command (or typing /history)
            self.autocomplete_widget.hide()
    
    def submit_message(self) -> None:
        """Submit the current message."""
        input_widget = self.query_one("#chat-input", CustomTextArea)
        content = input_widget.text.strip()
        
        # If command autocomplete is visible and a command is selected, use that command
        if self.autocomplete_widget and self.autocomplete_widget.is_visible:
            selected_command = self.autocomplete_widget.get_selected_command()
            if selected_command:
                content = selected_command
                self.autocomplete_widget.hide()
        
        # If history autocomplete is visible and a session is selected, handle it
        if self.history_autocomplete_widget and self.history_autocomplete_widget.is_visible:
            selected_session = self.history_autocomplete_widget.get_selected_session()
            if selected_session:
                # Post session selection message and hide the autocomplete
                self.post_message(HistoryAutocomplete.SessionSelected(selected_session))
                self.history_autocomplete_widget.hide()
                # Clear the input
                input_widget.text = ""
                return
        
        if content:
            # Add to command history
            self.command_history.add_command(content)
            
            # Reset navigation state
            self._is_navigating_history = False
            
            # Send the message normally
            self.post_message(self.Submit(content))
            
            # Clear the input
            input_widget.text = ""
            input_widget.cursor_location = (0, 0)
            
            # Hide both autocomplete widgets if visible
            if self.autocomplete_widget and self.autocomplete_widget.is_visible:
                self.autocomplete_widget.hide()
            if self.history_autocomplete_widget and self.history_autocomplete_widget.is_visible:
                self.history_autocomplete_widget.hide()
    
    def should_submit_on_enter(self) -> bool:
        """Check if we should submit on Enter key."""
        # Don't submit if autocomplete widgets are visible
        if self.autocomplete_widget and self.autocomplete_widget.is_visible:
            return False
        if self.history_autocomplete_widget and self.history_autocomplete_widget.is_visible:
            return False
        
        # Submit on regular Enter
        return True
    
    def should_autocomplete_handle_key(self, key: str) -> bool:
        """Check if autocomplete should handle this key."""
        # Always handle navigation and action keys when autocomplete is visible
        # This ensures input field forwards keys to autocomplete widgets
        if key in ("up", "down") and self.autocomplete_widget and self.autocomplete_widget.is_visible:
            return True
        if key in ("up", "down") and self.history_autocomplete_widget and self.history_autocomplete_widget.is_visible:
            return True
        if key in ("up", "down") and self.file_autocomplete_widget and self.file_autocomplete_widget.is_visible:
            return True
        if key == "enter" and self.autocomplete_widget and self.autocomplete_widget.is_visible:
            return True
        if key == "enter" and self.history_autocomplete_widget and self.history_autocomplete_widget.is_visible:
            return True
        if key == "enter" and self.file_autocomplete_widget and self.file_autocomplete_widget.is_visible:
            return True
        if key == "escape" and (
            (self.autocomplete_widget and self.autocomplete_widget.is_visible) or
            (self.history_autocomplete_widget and self.history_autocomplete_widget.is_visible) or
            (self.file_autocomplete_widget and self.file_autocomplete_widget.is_visible)
        ):
            return True
        if key == "tab" and self.autocomplete_widget and self.autocomplete_widget.is_visible:
            return True
        return False

    def handle_autocomplete_key(self, event: events.Key) -> None:
        """Forward key event to appropriate autocomplete widget."""
        # print(f"ChatInput.handle_autocomplete_key: {event.key}")
        if self.file_autocomplete_widget and self.file_autocomplete_widget.is_visible:
            # Handle file autocomplete using action system (like model selection)
            if event.key == "up":
                self.file_autocomplete_widget.action_navigate_up()
            elif event.key == "down":
                self.file_autocomplete_widget.action_navigate_down()
            elif event.key == "enter":
                self.file_autocomplete_widget.action_select_current()
            elif event.key == "escape":
                self.file_autocomplete_widget.action_close_menu()
        elif self.autocomplete_widget and self.autocomplete_widget.is_visible:
            # Handle command autocomplete
            if event.key == "enter":
                # Handle Enter specially - select AND submit the command immediately
                selected_command = self.autocomplete_widget.get_selected_command()
                if selected_command:
                    input_widget = self.query_one("#chat-input", CustomTextArea)
                    input_widget.text = selected_command
                    self.autocomplete_widget.hide()
                    # Submit immediately instead of just selecting
                    self.submit_message()
            elif event.key == "tab":
                # Handle TAB completion for commands (complete without submitting)
                selected_command = self.autocomplete_widget.get_selected_command()
                if selected_command:
                    input_widget = self.query_one("#chat-input", CustomTextArea)
                    input_widget.text = selected_command
                    input_widget.cursor_location = (0, len(selected_command))
                    self.autocomplete_widget.hide()
            else:
                # Let command autocomplete handle other keys (up, down, escape)
                self.autocomplete_widget.on_key(event)
        elif self.history_autocomplete_widget and self.history_autocomplete_widget.is_visible:
            # Handle history autocomplete - Enter should also submit for history
            if event.key == "enter":
                # For history autocomplete, Enter should also trigger immediate action
                self.history_autocomplete_widget.on_key(event)
                # The history autocomplete will handle session selection and submission
            else:
                # Let history autocomplete handle other keys
                self.history_autocomplete_widget.on_key(event)
        
    def handle_key_event(self, event: events.Key) -> bool:
        """Handle key events for multiline support, autocomplete navigation, and history.
        
        Returns:
            True if the event was handled and should be prevented from default processing.
            False if the event should continue to be processed normally by TextArea.
        """
        input_widget = self.query_one("#chat-input", CustomTextArea)
        # Check if shift is pressed by looking for shift+ in the key name
        shift_pressed = 'shift+' in event.key if hasattr(event, 'key') else False
        # print(f"[DEBUG] ChatInput.handle_key_event: {event.key} shift={shift_pressed}")
        
        # Handle autocomplete navigation first (command autocomplete has priority)
        if self.autocomplete_widget and self.autocomplete_widget.is_visible:
            if event.key in ("up", "down", "enter", "escape", "tab"):
                if event.key == "tab":
                    # Handle TAB completion for commands
                    selected_command = self.autocomplete_widget.get_selected_command()
                    if selected_command:
                        input_widget.text = selected_command
                        input_widget.cursor_location = (0, len(selected_command))
                        self.autocomplete_widget.hide()
                    return True  # Handled
                elif event.key == "enter":
                    # Handle Enter in autocomplete - select command and submit
                    selected_command = self.autocomplete_widget.get_selected_command()
                    if selected_command:
                        input_widget.text = selected_command
                        input_widget.cursor_location = (0, len(selected_command))
                        self.autocomplete_widget.hide()
                        # Now submit the selected command
                        self.submit_message()
                    return True  # Handled
                else:
                    # Let command autocomplete handle other keys (up, down, escape)
                    self.autocomplete_widget.on_key(event)
                    return True  # Handled
        
        # Handle history autocomplete navigation
        if self.history_autocomplete_widget and self.history_autocomplete_widget.is_visible:
            if event.key in ("up", "down", "enter", "escape"):
                # print(f"[DEBUG] Forwarding {event.key} to history autocomplete")
                # Let history autocomplete handle these keys
                self.history_autocomplete_widget.on_key(event)
                return True  # Handled
        
        # Handle Enter key - submit message (unless Shift+Enter)
        if event.key == "enter" and not shift_pressed:
            self.submit_message()
            return True  # Handled - prevent TextArea from processing
        
        # Handle command history navigation
        if event.key == "up" and not (self.autocomplete_widget and self.autocomplete_widget.is_visible):
            # Only navigate history if cursor is at the very beginning of input (line 0, column 0)
            cursor_line, cursor_column = input_widget.cursor_location
            if cursor_line == 0 and cursor_column == 0:
                # Navigate up in history
                current_text = input_widget.text
                if not self._is_navigating_history:
                    self.command_history.start_navigation(current_text)
                    self._is_navigating_history = True
                
                previous_command = self.command_history.navigate_up()
                if previous_command is not None:
                    input_widget.text = previous_command
                    # Move cursor to end
                    lines = previous_command.split('\n')
                    if lines:
                        input_widget.cursor_location = (len(lines) - 1, len(lines[-1]))
                return True  # Handled
            # If not at beginning, let TextArea handle normal cursor movement
            return False
        
        if event.key == "down" and not (self.autocomplete_widget and self.autocomplete_widget.is_visible):
            # Only navigate history if cursor is at the very beginning of input (line 0, column 0)
            # This maintains consistency with up arrow behavior
            cursor_line, cursor_column = input_widget.cursor_location
            if cursor_line == 0 and cursor_column == 0:
                # Navigate down in history
                # Start navigation if we haven't already (allows down navigation from beginning)
                current_text = input_widget.text
                if not self._is_navigating_history:
                    self.command_history.start_navigation(current_text)
                    self._is_navigating_history = True
                
                next_command = self.command_history.navigate_down()
                if next_command is not None:
                    input_widget.text = next_command
                    # Move cursor to end
                    lines = next_command.split('\n')
                    if lines:
                        input_widget.cursor_location = (len(lines) - 1, len(lines[-1]))
                return True  # Handled
            # If not at beginning, let TextArea handle normal cursor movement
            return False
        
        # Reset navigation state for any other key (user is typing)
        if event.key not in ("up", "down", "enter", "shift+enter") and self._is_navigating_history:
            self._is_navigating_history = False
            self.command_history.clear_navigation()
        
        # For Shift+Enter and other keys, let TextArea handle normally
        return False  # Not handled - let TextArea process normally
    
    def should_handle_enter(self) -> bool:
        """Check if we should handle the Enter key or let TextArea handle it."""
        # Handle Enter unless it's Shift+Enter (but we can't detect shift here easily)
        # We'll let the key_enter method handle the logic
        return True
    
    def on_enter_pressed(self) -> None:
        """Called when Enter is pressed in the text area."""
        self.submit_message()
    
    def action_submit_input(self) -> None:
        """Action for submitting input."""
        self.submit_message()
    
    def action_new_line(self) -> None:
        """Action for creating new line."""
        input_widget = self.query_one("#chat-input", CustomTextArea)
        # Insert a newline at cursor position
        input_widget.insert("\n")
    
    def action_history_up(self) -> None:
        """Action for navigating history up."""
        # Only if autocomplete is not visible and cursor is at very beginning
        if not (self.autocomplete_widget and self.autocomplete_widget.is_visible):
            input_widget = self.query_one("#chat-input", CustomTextArea)
            cursor_line, cursor_column = input_widget.cursor_location
            if cursor_line == 0 and cursor_column == 0:
                current_text = input_widget.text
                if not self._is_navigating_history:
                    self.command_history.start_navigation(current_text)
                    self._is_navigating_history = True
                
                previous_command = self.command_history.navigate_up()
                if previous_command is not None:
                    input_widget.text = previous_command
                    lines = previous_command.split('\n')
                    if lines:
                        input_widget.cursor_location = (len(lines) - 1, len(lines[-1]))
    
    def action_history_down(self) -> None:
        """Action for navigating history down."""
        # Only if autocomplete is not visible and cursor is at very beginning
        if not (self.autocomplete_widget and self.autocomplete_widget.is_visible):
            input_widget = self.query_one("#chat-input", CustomTextArea)
            cursor_line, cursor_column = input_widget.cursor_location
            if cursor_line == 0 and cursor_column == 0:
                current_text = input_widget.text
                if not self._is_navigating_history:
                    self.command_history.start_navigation(current_text)
                    self._is_navigating_history = True
                
                next_command = self.command_history.navigate_down()
                if next_command is not None:
                    input_widget.text = next_command
                    lines = next_command.split('\n')
                    if lines:
                        input_widget.cursor_location = (len(lines) - 1, len(lines[-1]))
    
    def action_autocomplete(self) -> None:
        """Action for tab completion."""
        if self.autocomplete_widget and self.autocomplete_widget.is_visible:
            selected_command = self.autocomplete_widget.get_selected_command()
            if selected_command:
                input_widget = self.query_one("#chat-input", CustomTextArea)
                input_widget.text = selected_command
                input_widget.cursor_location = (0, len(selected_command))
                self.autocomplete_widget.hide()
    
    def action_escape_autocomplete(self) -> None:
        """Action for escaping autocomplete."""
        if self.autocomplete_widget and self.autocomplete_widget.is_visible:
            self.autocomplete_widget.hide()
        if self.history_autocomplete_widget and self.history_autocomplete_widget.is_visible:
            self.history_autocomplete_widget.hide()
    
    # TextArea doesn't have a Submitted event like Input
    # We handle submission entirely through on_key method
    
    def on_command_autocomplete_command_selected(self, message: CommandAutocomplete.CommandSelected) -> None:
        """Handle command selection from autocomplete."""
        input_widget = self.query_one("#chat-input", CustomTextArea)
        input_widget.text = message.command
        # Position cursor at the end
        input_widget.cursor_location = (0, len(message.command))
    
    def on_command_autocomplete_autocomplete_escape(self, message: CommandAutocomplete.AutocompleteEscape) -> None:
        """Handle autocomplete escape."""
        # Focus back to input
        self.focus_input()
    
    def on_history_autocomplete_session_selected(self, message: HistoryAutocomplete.SessionSelected) -> None:
        """Handle session selection from history autocomplete."""
        # Forward this message to the app level for handling
        self.post_message(message)
    
    def on_history_autocomplete_history_escape(self, message: HistoryAutocomplete.HistoryEscape) -> None:
        """Handle history autocomplete escape."""
        # Focus back to input
        self.focus_input()
    
    def focus_input(self):
        """Focus the input field."""
        input_widget = self.query_one("#chat-input", CustomTextArea)
        input_widget.focus()
    
    async def show_history_autocomplete(self):
        """Show the history autocomplete dropdown."""
        if self.history_autocomplete_widget and self.storage_manager:
            await self.history_autocomplete_widget.show()
    
    def on_file_autocomplete_file_selected(self, message) -> None:
        """Handle file selection from file autocomplete."""
        # Set flag to prevent re-triggering autocomplete
        self._just_selected_file = True
        
        input_widget = self.query_one("#chat-input", CustomTextArea)
        current_text = input_widget.text
        cursor_line, cursor_column = input_widget.cursor_location
        
        # Get current lines
        lines = current_text.split('\n')
        if cursor_line < len(lines):
            current_line = lines[cursor_line]
            
            # Find the @ position in current line
            at_index = current_line.rfind('@', 0, cursor_column)
            if at_index >= 0:
                # Replace from @ to cursor with the selected path
                new_line = current_line[:at_index] + '@' + message.path + current_line[cursor_column:]
                lines[cursor_line] = new_line
                
                # Update text
                input_widget.text = '\n'.join(lines)
                
                # Position cursor after the inserted path
                new_cursor_pos = at_index + 1 + len(message.path)
                input_widget.cursor_location = (cursor_line, new_cursor_pos)
        
        # Hide file autocomplete
        self.file_autocomplete_widget.hide()
        self._at_trigger_position = -1
        
        # Reset flag after a brief delay to allow normal @ triggering later
        self.call_later(self._reset_file_selection_flag)
    
    def _reset_file_selection_flag(self) -> None:
        """Reset the file selection flag."""
        self._just_selected_file = False