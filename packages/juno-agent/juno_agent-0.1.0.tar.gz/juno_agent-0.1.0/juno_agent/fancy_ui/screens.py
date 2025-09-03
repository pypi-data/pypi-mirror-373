"""Screen views for the TUI application."""

from textual.app import ComposeResult
from textual.widgets import Header, Footer, Static
from textual.binding import Binding
from textual.screen import Screen

from .widgets.chat_area import ChatArea
from .widgets.input_area import ChatInput
from ..config import ConfigManager
from ..utils import SystemStatus
from ..tiny_agent import TinyCodeAgentChat
from ..storage_manager_async import AsyncConversationStorageManager


class WelcomeScreenView(Screen):
    """Welcome screen view."""
    
    BINDINGS = [
        Binding("enter", "start_chat", "Start Chat", priority=True),
        Binding("s", "setup", "Setup"),
        Binding("q", "quit", "Quit"),
        Binding("escape", "quit", "Quit"),
        Binding("n", "new_chat", "New Chat"),
    ]
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.system_status = SystemStatus(config_manager.workdir)
        
    def compose(self) -> ComposeResult:
        """Compose the welcome screen."""
        yield Header()
        yield Static("🧙‍♂️ **juno-agent** - AI Coding Assistant\n\nPress Enter to start chatting!", classes="welcome-message")
        yield Footer()
    
    def action_start_chat(self) -> None:
        """Start the chat interface."""
        self.app.push_screen("chat")
    
    def action_setup(self) -> None:
        """Run setup wizard."""
        # TODO: Implement setup screen or call setup command
        self.app.push_screen("chat")
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()
    
    def action_new_chat(self) -> None:
        """Start a new chat (navigate to chat screen)."""
        self.app.push_screen("chat")


class ChatScreenView(Screen):
    """Chat interface screen view."""
    
    BINDINGS = [
        Binding("ctrl+w", "show_welcome", "Welcome"),
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+q", "quit", "Quit"),
        Binding("escape", "quit", "Quit"),
        Binding("ctrl+n", "new_chat", "New Chat"),
        Binding("ctrl+r", "toggle_tool_expansion", "Toggle Tool Details"),
    ]
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        self.config_manager = config_manager
        self.tiny_code_agent = None
        self.chat_area = None
        self.chat_input = None
        # Initialize storage manager
        try:
            self.storage_manager = AsyncConversationStorageManager()
        except Exception as e:
            # If storage manager fails to initialize, continue without it
            self.storage_manager = None
        
    def compose(self) -> ComposeResult:
        """Compose the chat interface."""
        yield Header()
        self.chat_area = ChatArea()
        yield self.chat_area
        self.chat_input = ChatInput()
        yield self.chat_input
        yield Footer()
    
    async def on_mount(self) -> None:
        """Initialize the chat screen after mounting."""
        # Initialize TinyCodeAgent with no console output (Textual handles UI) and storage manager
        self.tiny_code_agent = TinyCodeAgentChat(
            self.config_manager, 
            console=None,
            storage_manager=self.storage_manager
        )
        
        # Add welcome message
        self.chat_area.add_message(
            "Welcome to juno-agent! I'm your AI coding assistant. Type your questions or commands.",
            is_user=False
        )
        
        # Focus the input
        self.chat_input.focus_input()
        
        # Try to initialize the agent in the background
        self.run_worker(self._initialize_agent(), exclusive=True)
    
    async def _initialize_agent(self) -> None:
        """Initialize the TinyCodeAgent in the background."""
        try:
            await self.tiny_code_agent.initialize_agent()
            self.chat_area.add_message(
                "TinyAgent initialized successfully! Ready to help with your coding tasks.",
                is_user=False
            )
        except Exception as e:
            self.chat_area.add_message(
                f"Note: TinyAgent not available ({str(e)}). For first iteration, I'll respond with simple messages.",
                is_user=False
            )
    
    async def on_chat_input_submit(self, message: ChatInput.Submit) -> None:
        """Handle user message submission."""
        user_message = message.content
        
        # Add user message to chat
        self.chat_area.add_message(user_message, is_user=True)
        
        # Process the message in a background worker
        self.run_worker(self._process_message(user_message))
    
    async def _process_message(self, user_message: str) -> None:
        """Process user message in background."""
        # Show loading indicator
        loading_widget = self.chat_area.add_message("Processing your request...", is_user=False)
        
        try:
            if self.tiny_code_agent and self.tiny_code_agent.agent:
                # Use TinyCodeAgent for AI response
                response = await self.tiny_code_agent.process_chat_message(user_message)
            else:
                # Fallback simple response for first iteration
                response = f"You said '{user_message}'. I will work on it."
            
            # Remove loading message
            if self.chat_area.messages and self.chat_area.messages[-1]:
                self.chat_area.messages[-1].remove()
                self.chat_area.messages.pop()
            
            # Add agent response
            self.chat_area.add_message(response, is_user=False)
            
        except Exception as e:
            # Remove loading message
            if self.chat_area.messages and self.chat_area.messages[-1]:
                self.chat_area.messages[-1].remove()
                self.chat_area.messages.pop()
            
            # Show error message
            self.chat_area.add_message(
                f"Error processing your message: {str(e)}",
                is_user=False
            )
    
    def action_show_welcome(self) -> None:
        """Show the welcome screen."""
        self.app.pop_screen()
    
    def action_clear_chat(self) -> None:
        """Clear the chat area."""
        if self.chat_area:
            self.chat_area.clear_messages()
            self.chat_area.add_message(
                "Chat cleared. How can I help you?",
                is_user=False
            )
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()
    
    def action_new_chat(self) -> None:
        """Reset the chat (clear messages and restart)."""
        if self.chat_area:
            self.chat_area.clear_messages()
            
            # Start new session with storage if available
            if self.tiny_code_agent:
                session_id = self.tiny_code_agent.start_new_session()
                if session_id != "no_storage":
                    self.chat_area.add_message(
                        f"✨ **New chat started!** Session {session_id[:8]}... created. Conversation history cleared and context freed up. How can I help you?",
                        is_user=False
                    )
                else:
                    self.chat_area.add_message(
                        "✨ **New chat started!** Conversation history cleared and context freed up. How can I help you?",
                        is_user=False
                    )
            else:
                self.chat_area.add_message(
                    "✨ **New chat started!** Conversation history cleared and context freed up. How can I help you?",
                    is_user=False
                )
        # Focus the input
        if self.chat_input:
            self.chat_input.focus_input()
    
    def action_toggle_tool_expansion(self) -> None:
        """Toggle tool call expansion for all messages in the conversation."""
        # This method will be handled by the main app since screen views don't have direct access
        # to the expansion state. Pass through to main app.
        pass