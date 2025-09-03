"""History viewer widget for displaying conversation history in a selectable list format."""

from typing import List, Dict, Any, Optional
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, ListItem, ListView, Button, Label
from textual.screen import ModalScreen
from textual.binding import Binding


class HistoryViewerScreen(ModalScreen):
    """Modal screen for viewing conversation history."""
    
    BINDINGS = [
        Binding("escape", "dismiss", "Close"),
        Binding("q", "dismiss", "Close"),
        Binding("enter", "load_session", "Load Session"),
        Binding("d", "delete_session", "Delete Session"),
    ]
    
    def __init__(self, storage_manager, on_load_session=None):
        super().__init__()
        self.storage_manager = storage_manager
        self.on_load_session = on_load_session
        self.sessions = []
        self.selected_session = None
    
    def compose(self) -> ComposeResult:
        """Compose the history viewer screen."""
        with Vertical(id="history-container"):
            yield Static("📝 **Conversation History**", classes="history-title")
            
            # Sessions list
            self.sessions_list = ListView(id="sessions-list")
            yield self.sessions_list
            
            # Actions
            with Horizontal(classes="history-actions"):
                yield Button("Load Session", variant="primary", id="load-btn")
                yield Button("Delete Session", variant="error", id="delete-btn")
                yield Button("Close", id="close-btn")
            
            # Status/help text
            yield Static("Use arrow keys to navigate, Enter to load, D to delete, Escape to close", classes="help-text")
    
    async def on_mount(self) -> None:
        """Load sessions when screen mounts."""
        await self.refresh_sessions()
    
    async def refresh_sessions(self) -> None:
        """Refresh the sessions list."""
        if not self.storage_manager or not self.storage_manager.is_available():
            self.sessions_list.append(ListItem(Static("❌ Storage not available")))
            return
            
        try:
            # Show simple storage information instead of listing sessions
            info_text = f"""📝 Storage Status

Database: {self.storage_manager.db_path}
Current Session: {self.storage_manager.current_session_id[:8]}...
User ID: {self.storage_manager.user_id}

History is managed by TinyAgent automatically."""
            
            self.sessions_list.clear()
            self.sessions_list.append(ListItem(Static(info_text)))
                
        except Exception as e:
            self.sessions_list.append(ListItem(Static(f"❌ Error loading storage info: {str(e)}")))
    
    def create_session_item(self, session: Dict[str, Any], index: int) -> ListItem:
        """Create a list item for a session."""
        # This method is now simplified for storage info display
        display_text = "Storage managed by TinyAgent"
        item = ListItem(Static(display_text))
        item.session_data = session
        return item
    
    async def on_list_view_selected(self, message: ListView.Selected) -> None:
        """Handle session selection."""
        if hasattr(message.item, 'session_data'):
            self.selected_session = message.item.session_data
        
    async def on_button_pressed(self, message: Button.Pressed) -> None:
        """Handle button presses."""
        if message.button.id == "load-btn":
            await self.action_load_session()
        elif message.button.id == "delete-btn":
            await self.action_delete_session()
        elif message.button.id == "close-btn":
            self.action_dismiss()
    
    async def action_load_session(self) -> None:
        """Load the selected session."""
        if not self.selected_session:
            return
        
        if self.on_load_session:
            session_id = self.selected_session.get('session_id')
            await self.on_load_session(session_id)
        
        self.dismiss(self.selected_session)
    
    async def action_delete_session(self) -> None:
        """Delete the selected session."""
        # Session deletion is now managed by TinyAgent
        self.sessions_list.append(ListItem(Static("Session deletion is managed by TinyAgent storage system.")))
        self.selected_session = None
    
    def action_dismiss(self) -> None:
        """Close the history viewer."""
        self.dismiss()


class HistoryViewer(Static):
    """Simple history viewer widget that can be embedded in other screens."""
    
    def __init__(self, storage_manager, **kwargs):
        super().__init__(**kwargs)
        self.storage_manager = storage_manager
        self.sessions = []
    
    def compose(self) -> ComposeResult:
        """Compose the embedded history viewer."""
        yield Static("📝 **Recent Conversations**", classes="history-title")
        
        self.sessions_container = Vertical(id="sessions-container")
        yield self.sessions_container
    
    async def on_mount(self) -> None:
        """Load sessions when widget mounts."""
        await self.refresh_sessions()
    
    async def refresh_sessions(self) -> None:
        """Refresh the sessions display."""
        if not self.storage_manager or not self.storage_manager.is_available():
            self.sessions_container.mount(Static("❌ Storage not available"))
            return
            
        try:
            # Clear existing content
            await self.sessions_container.remove_children()
            
            # Show storage status instead of sessions
            storage_info = f"""Current Session: {self.storage_manager.current_session_id[:8]}...
Database: {self.storage_manager.db_path}
History managed by TinyAgent"""
            
            self.sessions_container.mount(Static(storage_info))
                
        except Exception as e:
            self.sessions_container.mount(Static(f"❌ Error loading storage info: {str(e)}"))
    
    def create_session_widget(self, session: Dict[str, Any], index: int) -> Static:
        """Create a widget for a session."""
        # Simplified for storage info display
        return Static("Storage managed by TinyAgent", classes="session-item")