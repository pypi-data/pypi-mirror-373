"""Interactive history menu widget for conversation session selection."""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
try:
    import tzlocal
except ImportError:
    tzlocal = None
try:
    from zoneinfo import ZoneInfo
except ImportError:
    try:
        from backports.zoneinfo import ZoneInfo
    except ImportError:
        ZoneInfo = None
from textual import events
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, Container
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static, Button


class SessionOption(Static):
    """A single session option - compact style like command menu."""
    
    DEFAULT_CSS = """
    SessionOption {
        height: 1;
        padding: 0 1;
        margin: 0;
        background: transparent;
        color: $text;
    }
    
    SessionOption.selected {
        background: $primary;
        color: $background;
    }
    
    SessionOption:hover {
        background: $accent;
        color: $background;
    }
    """
    
    def __init__(self, session: Dict[str, Any], **kwargs):
        """Initialize session item with compact display format.
        
        Args:
            session: Session data dictionary containing session_id, created_at, message_count, preview, etc.
        """
        self.session = session
        self.session_id = session.get('session_id', 'unknown')
        
        # Format display content in compact style
        display_text = self._format_compact_display(session)
        super().__init__(display_text, **kwargs)
    
    def _format_date_local(self, date_string: str) -> str:
        """Format date in user's local timezone for compact display."""
        if not date_string:
            return "Unknown"
        
        try:
            # Parse the timestamp
            if 'T' in str(date_string):
                # ISO format: "2024-08-19T04:21:00Z"
                dt = datetime.fromisoformat(str(date_string).replace('Z', '+00:00'))
            else:
                # Assume it's already a datetime or try parsing as timestamp
                try:
                    dt = datetime.fromisoformat(str(date_string))
                except:
                    dt = datetime.fromtimestamp(float(date_string))
            
            # Convert to local timezone
            local_dt = dt.astimezone()
            
            # Format as compact string: "2024-08-19 04:21"
            return local_dt.strftime("%Y-%m-%d %H:%M")
            
        except Exception as e:
            print(f"[DEBUG] Date formatting error: {e}")
            return "Unknown"
    
    def _format_compact_display(self, session: Dict[str, Any]) -> str:
        """Format session data for compact single-line display."""
        session_id = session.get('session_id', 'unknown')
        message_count = session.get('message_count', 0)
        preview = session.get('preview', 'No messages')
        
        # Get formatted date in local timezone
        created_at = session.get('created_at')
        created_str = self._format_date_local(created_at)
        
        # Truncate session ID for display
        session_display = session_id[:8] if len(session_id) > 8 else session_id
        
        # Truncate preview to fit single line display
        max_preview_length = 40
        if len(preview) > max_preview_length:
            preview = preview[:max_preview_length] + "..."
        
        # Compact format: "Session 12345678... • 2024-08-19 04:21 • 29 msgs • preview..."
        return f"Session {session_display}... • {created_str} • {message_count} msgs • {preview}"


class HistoryMenu(Widget):
    """History menu with compact command-menu style."""
    
    BINDINGS = [
        ("up", "navigate_up", "Previous"),
        ("down", "navigate_down", "Next"),
        ("enter", "select_current", "Select"),
        ("escape", "close_menu", "Cancel"),
    ]
    
    DEFAULT_CSS = """
    HistoryMenu {
        display: none;
        height: auto;
        max-height: 25;
        background: $surface;
        border: round $primary;
        margin-top: 0;
        margin-bottom: 0; 
        margin-left: 1;
        margin-right: 1;
    }
    
    HistoryMenu.visible {
        display: block;
    }
    
    #history-container {
        height: auto;
        max-height: 23;
        overflow-y: auto;
        scrollbar-gutter: stable;
        scrollbar-size: 1 1;
        scrollbar-background: $accent 50%;
        scrollbar-color: $primary;
        scrollbar-color-hover: $warning;
        scrollbar-color-active: $error;
        padding: 0;
        background: transparent;
    }
    
    .history-header {
        height: 1;
        padding: 0 1;
        color: $text-muted;
        text-style: italic;
        background: transparent;
    }
    
    .history-footer {
        height: 1;
        padding: 0 1;
        color: $text-muted;
        text-style: italic;
        background: transparent;
    }
    
    .empty-state {
        text-align: center;
        color: $text-muted;
        padding: 2 1;
        text-style: italic;
        background: transparent;
    }
    """
    
    class SessionSelected(Message):
        """Message sent when a session is selected."""
        
        def __init__(self, session: Dict[str, Any]):
            super().__init__()
            self.session = session
    
    class MenuClosed(Message):
        """Message sent when menu should be closed."""
        pass
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sessions: List[Dict[str, Any]] = []
        self.selected_index = 0
        self.is_visible = False
    
    @property
    def can_focus(self) -> bool:
        """This widget can receive focus when visible."""
        return True
    
    def compose(self) -> ComposeResult:
        """Compose the history menu in compact style."""
        # Scrollable session options container (same pattern as command autocomplete)
        self.container = Vertical(id="history-container")
        yield self.container
    
    def show(self, sessions: List[Dict[str, Any]]) -> None:
        """Show the history menu with sessions.
        
        Args:
            sessions: List of session dictionaries from storage manager
        """
        self.sessions = sessions
        
        if not self.sessions:
            # Show empty state
            self._show_empty_state()
        else:
            # Reset selection and show sessions
            self.selected_index = 0
            self._clear_options()
            self._update_options()
        
        self.is_visible = True
        self.add_class("visible")
        self.focus()
    
    def hide(self) -> None:
        """Hide the history menu."""
        self.remove_class("visible")
        self.is_visible = False
        self.selected_index = 0
        self._clear_options()
    
    def _show_empty_state(self) -> None:
        """Show empty state when no sessions are available."""
        self._clear_options()
        
        try:
            container = getattr(self, 'container', None)
            if container is None:
                container = self.query_one("#history-container", Vertical)
            if container:
                # Add header
                header = Static("📝 No conversation history found", classes="history-header")
                container.mount(header)
                
                # Add empty message
                empty_message = Static("This is your first conversation or no sessions have been saved yet.", classes="empty-state")
                container.mount(empty_message)
                
                # Add footer
                footer = Static("Press Escape to cancel", classes="history-footer")
                container.mount(footer)
        except Exception:
            pass
    
    def _clear_options(self) -> None:
        """Clear all option widgets from the container."""
        try:
            container = getattr(self, 'container', None)
            if container is None:
                try:
                    container = self.query_one("#history-container", Vertical)
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
        """Update the displayed session options in compact style."""
        try:
            # Get the container, either from instance or by querying
            container = getattr(self, 'container', None)
            if container is None:
                try:
                    container = self.query_one("#history-container", Vertical)
                except:
                    # Container not found, skip update
                    return
            
            # Add session options to container
            if container and self.sessions:
                # Add header
                header = Static("📝 Recent Conversations (Use ↑↓ to navigate, Enter to load)", classes="history-header")
                container.mount(header)
                
                # Add session options (limit to 20 for scrollable display)
                for i, session in enumerate(self.sessions[:20]):
                    option = SessionOption(session)
                    if i == self.selected_index:
                        option.add_class("selected")
                    container.mount(option)
                
                # Add footer
                footer = Static("Press Escape to cancel", classes="history-footer")
                container.mount(footer)
                    
        except Exception as e:
            # If mounting fails, we should at least not crash
            # This might happen during widget lifecycle transitions
            pass
    
    def navigate_up(self) -> None:
        """Navigate to previous session."""
        if not self.is_visible or not self.sessions:
            return
        
        max_sessions = min(len(self.sessions), 20)  # Limit to 20 sessions for scrollable display
        self.selected_index = (self.selected_index - 1) % max_sessions
        self._update_selection()
    
    def navigate_down(self) -> None:
        """Navigate to next session."""
        if not self.is_visible or not self.sessions:
            return
        
        max_sessions = min(len(self.sessions), 20)  # Limit to 20 sessions for scrollable display
        self.selected_index = (self.selected_index + 1) % max_sessions
        self._update_selection()
    
    def _update_selection(self) -> None:
        """Update the visual selection of session options."""
        try:
            options = self.query(SessionOption)
            for i, option in enumerate(options):
                if i == self.selected_index:
                    option.add_class("selected")
                else:
                    option.remove_class("selected")
                    
            # Scroll to selected item
            if options and self.selected_index < len(options):
                selected_option = options[self.selected_index]
                container = getattr(self, 'container', None)
                if container is None:
                    try:
                        container = self.query_one("#history-container", Vertical)
                    except:
                        return
                if container:
                    container.scroll_to_widget(selected_option)
                    
        except Exception:
            # If querying fails, skip the update
            # This might happen during widget lifecycle transitions
            pass
    
    def select_current(self) -> None:
        """Select the currently highlighted session."""
        # print(f"[DEBUG] HistoryMenu.select_current: visible={self.is_visible}, selected_index={self.selected_index}")
        if not self.is_visible or not self.sessions:
            return
        
        max_sessions = min(len(self.sessions), 20)  # Limit to 20 sessions for scrollable display
        if 0 <= self.selected_index < max_sessions:
            selected_session = self.sessions[self.selected_index]
            # print(f"[DEBUG] HistoryMenu.select_current: Selected session {selected_session.get('session_id', 'unknown')}")
            self.post_message(self.SessionSelected(selected_session))
            self.hide()
    
    def get_selected_session(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected session."""
        if not self.is_visible or not self.sessions:
            return None
        
        max_sessions = min(len(self.sessions), 20)  # Limit to 20 sessions for scrollable display
        if 0 <= self.selected_index < max_sessions:
            return self.sessions[self.selected_index]
        return None
    
    # Key handling is now done through BINDINGS and action methods
    # The on_key method is no longer needed to avoid double handling
    
    def action_navigate_up(self) -> None:
        """Action for navigating up."""
        if self.is_visible:
            self.navigate_up()
    
    def action_navigate_down(self) -> None:
        """Action for navigating down."""
        if self.is_visible:
            self.navigate_down()
    
    def action_select_current(self) -> None:
        """Action for selecting current item."""
        if self.is_visible:
            self.select_current()
    
    def action_close_menu(self) -> None:
        """Action for closing the menu."""
        if self.is_visible:
            self.post_message(self.MenuClosed())
            self.hide()
    
    def on_click(self, event: events.Click) -> None:
        """Handle click events on session options."""
        if not self.is_visible:
            return
        
        # Find which session option was clicked
        try:
            container = getattr(self, 'container', None)
            if container is None:
                container = self.query_one("#history-container", Vertical)
                
            if container:
                for i, child in enumerate(container.children):
                    if isinstance(child, SessionOption):
                        if child.region.contains(event.screen_offset):
                            self.selected_index = i
                            self._update_selection()
                            # Double-click to select
                            if event.count == 2:
                                self.select_current()
                            break
        except Exception:
            pass