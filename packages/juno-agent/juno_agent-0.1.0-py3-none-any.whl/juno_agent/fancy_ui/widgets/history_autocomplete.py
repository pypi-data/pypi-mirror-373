"""History autocomplete dropdown widget."""

from typing import List, Optional, Tuple, Dict, Any
from textual import events
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static
from datetime import datetime


class HistoryOption(Static):
    """A single history option in the autocomplete dropdown."""
    
    DEFAULT_CSS = """
    HistoryOption {
        height: 2;
        padding: 0 1;
        margin: 0;
        background: transparent;
        color: $text;
    }
    
    HistoryOption.selected {
        background: $primary;
        color: $background;
    }
    
    HistoryOption:hover {
        background: $accent;
        color: $background;
    }
    """
    
    def __init__(self, session: Dict[str, Any], index: int, **kwargs):
        """Initialize history option.
        
        Args:
            session: The session data from storage
            index: The display index (1-based)
        """
        self.session = session
        self.index = index
        
        # Format session info for display
        session_id = session.get('session_id', 'unknown')
        created_at = session.get('created_at', 'unknown')
        message_count = session.get('message_count', 0)
        preview = session.get('preview', 'No preview available')
        
        # Parse datetime for display
        try:
            if created_at != 'unknown':
                created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                created_str = created_dt.strftime('%m/%d %H:%M')
            else:
                created_str = 'unknown'
        except:
            created_str = str(created_at)[:10] if created_at != 'unknown' else 'unknown'
        
        # Truncate preview for display
        preview_display = preview[:50] + "..." if len(preview) > 50 else preview
        
        # Format: "1. 12/25 14:30 (5 msgs) - Preview text..."
        display_text = f"{index:2d}. {created_str} ({message_count:2d} msgs) - {preview_display}"
        
        super().__init__(display_text, **kwargs)


class HistoryAutocomplete(Widget):
    """Autocomplete dropdown for conversation history."""
    
    DEFAULT_CSS = """
    HistoryAutocomplete {
        display: none;
        height: auto;
        max-height: 25;
        overflow-y: auto;
        scrollbar-gutter: stable;
        scrollbar-size: 1 1;
        scrollbar-background: $accent 50%;
        scrollbar-color: $primary;
        scrollbar-color-hover: $warning;
        scrollbar-color-active: $error;
        background: $surface;
        border: round $primary;
        margin-top: 0;
        margin-bottom: 0;
        margin-left: 1;
        margin-right: 1;
    }
    
    HistoryAutocomplete.visible {
        display: block;
    }
    """
    
    BINDINGS = [
        ("up", "navigate_up", "Previous"),
        ("down", "navigate_down", "Next"),
        ("enter", "select_current", "Select"),
        ("escape", "escape_history", "Cancel"),
    ]
    
    class SessionSelected(Message):
        """Message sent when a session is selected."""
        
        def __init__(self, session: Dict[str, Any]):
            super().__init__()
            self.session = session
    
    class HistoryEscape(Message):
        """Message sent when history autocomplete should be dismissed."""
        pass
    
    def __init__(self, storage_manager, **kwargs):
        super().__init__(**kwargs)
        self.storage_manager = storage_manager
        self.sessions: List[Dict[str, Any]] = []
        self.selected_index = 0
        self.is_visible = False
    
    @property
    def can_focus(self) -> bool:
        """This widget can receive focus."""
        return True
    
    def compose(self) -> ComposeResult:
        """Compose the history autocomplete dropdown."""
        self.container = Vertical(id="history-autocomplete-container")
        yield self.container
    
    async def show(self) -> None:
        """Show the history autocomplete dropdown with storage info."""
        if not self.storage_manager or not self.storage_manager.is_available():
            return
        
        try:
            # Create a simple storage info session entry
            storage_info = {
                'session_id': self.storage_manager.current_session_id,
                'created_at': 'now',
                'message_count': 0,
                'preview': 'Storage managed by TinyAgent'
            }
            self.sessions = [storage_info]
            
            # Show storage info
            self.selected_index = 0
            self.is_visible = True
            # Clear any existing options first
            self._clear_options()
            # Update options with sessions
            self._update_options()
            # Make visible
            self.add_class("visible")
            # Focus this widget so it can receive key events directly
            self.focus()
        except Exception as e:
            # Hide if there's an error
            self.hide()
    
    def hide(self) -> None:
        """Hide the history autocomplete dropdown."""
        self.remove_class("visible")
        self.is_visible = False
        self.selected_index = 0
        # Clear all options
        self._clear_options()
        # Return focus to input field
        try:
            input_widget = self.app.query_one("#chat-input")
            input_widget.focus()
        except Exception:
            # If we can't find the input widget, don't crash
            pass
    
    def _deferred_cleanup(self) -> None:
        """Perform heavy DOM cleanup operations deferred from event handling."""
        try:
            self.selected_index = 0
            self._clear_options()
        except Exception:
            # Silently handle cleanup errors to prevent crashes
            pass
    
    def _clear_options(self) -> None:
        """Clear all option widgets from the container."""
        try:
            container = getattr(self, 'container', None)
            if container is None:
                try:
                    container = self.query_one("#history-autocomplete-container", Vertical)
                except:
                    return
            
            if container:
                # Use a safer approach: collect children first, then remove them
                children_to_remove = list(container.children)
                for child in children_to_remove:
                    try:
                        child.remove()
                    except Exception:
                        # Continue with other children even if one fails
                        continue
        except Exception:
            # Silently handle errors to prevent crashes during cleanup
            pass
    
    def _update_options(self) -> None:
        """Update the displayed history options."""
        try:
            # Get the container, either from instance or by querying
            container = getattr(self, 'container', None)
            if container is None:
                try:
                    container = self.query_one("#history-autocomplete-container", Vertical)
                except:
                    # Container not found, skip update
                    return
            
            # Add header
            if container and self.sessions:
                header = Static("📝 Recent Conversations (Use ↑↓ to navigate, Enter to load)")
                header.add_class("history-header")
                container.mount(header)
                
                # Add filtered options to container
                for i, session in enumerate(self.sessions[:20]):  # Show max 20 sessions
                    option = HistoryOption(session, i + 1)
                    if i == self.selected_index:
                        option.add_class("selected")
                    container.mount(option)
                    
                # Add footer
                footer = Static("Press Escape to cancel")
                footer.add_class("history-footer")
                container.mount(footer)
                
        except Exception as e:
            # If mounting fails, we should at least not crash
            # This might happen during widget lifecycle transitions
            pass
    
    def navigate_up(self) -> None:
        """Navigate to previous option."""
        if not self.is_visible or not self.sessions:
            return
        
        self.selected_index = (self.selected_index - 1) % len(self.sessions[:20])
        self._update_selection()
    
    def navigate_down(self) -> None:
        """Navigate to next option."""
        if not self.is_visible or not self.sessions:
            return
        
        self.selected_index = (self.selected_index + 1) % len(self.sessions[:20])
        self._update_selection()
    
    def _update_selection(self) -> None:
        """Update the visual selection of options."""
        try:
            options = self.query(HistoryOption)
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
        """Select the currently highlighted session."""
        # print(f"HistoryAutocomplete.select_current: {self.selected_index}")
        if not self.is_visible or not self.sessions:
            return
        
        if self.selected_index < len(self.sessions[:20]):
            selected_session = self.sessions[self.selected_index]
            
            # First, immediately hide the visual dropdown to give instant feedback
            # This prevents UI hang by avoiding DOM manipulation during event handling
            self.remove_class("visible")
            self.is_visible = False
            
            # Post the message
            self.post_message(self.SessionSelected(selected_session))
            
            # Defer the heavy DOM cleanup to avoid blocking the UI
            self.call_later(self._deferred_cleanup)
    
    def get_selected_session(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected session."""
        if not self.is_visible or not self.sessions:
            return None
        
        if self.selected_index < len(self.sessions[:20]):
            return self.sessions[self.selected_index]
        return None
    
    def on_key(self, event: events.Key) -> None:
        """Handle key events for navigation."""

        
        if not self.is_visible:
            return
        
        # Debug: log key events to help troubleshoot
        # print(f"HistoryAutocomplete.on_key: {event.key}")
        
        if event.key == "up":
            self.navigate_up()
            event.prevent_default()
        elif event.key == "down":
            self.navigate_down()
            event.prevent_default()
        elif event.key == "enter":
            self.select_current()
            event.prevent_default()
        elif event.key == "escape":
            self.post_message(self.HistoryEscape())
            self.hide()
            event.prevent_default()
