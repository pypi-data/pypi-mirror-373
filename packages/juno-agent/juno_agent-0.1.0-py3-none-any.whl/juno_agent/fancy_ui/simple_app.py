"""Simple chat app using Textual for juno-agent."""

import asyncio
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer

from .widgets.chat_area import ChatArea
from .widgets.input_area import ChatInput
from ..config import ConfigManager
from ..tiny_agent import TinyCodeAgentChat


class SimpleChatApp(App):
    """Modern chat interface using Textual."""
    
    CSS_PATH = Path(__file__).parent / "styles" / "chat.tcss"
    
    BINDINGS = [
        ("ctrl+c", "clear", "Clear Chat"),
        ("ctrl+q", "quit", "Quit"),
        ("escape", "quit", "Quit"),
    ]
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__()
        
        self.config_manager = config_manager
        # Set dynamic title based on current working directory
        self.title = self._generate_dynamic_title()
        self.tiny_code_agent = None
        self.chat_area = None
        self.chat_input = None
        
    def _generate_dynamic_title(self) -> str:
        """Generate a dynamic title showing last two path parts, branding, and model name."""
        try:
            workdir_path = Path(self.config_manager.workdir)
            if len(workdir_path.parts) > 2:
                # Show last two parts: "parent_dir/current_dir"
                path_display = f"{workdir_path.parts[-2]}/{workdir_path.parts[-1]}"
            else:
                # Show full path if less than 2 parts
                path_display = str(workdir_path.name) if workdir_path.name else str(workdir_path)
            
            # Add model name if available
            config = self.config_manager.load_config()
            base_title = f"{path_display} - JUNO AI CLI - AI Coding Assistant"
            
            if config.agent_config.model_name and config.agent_config.model_name != "Not set":
                # Extract the last part after "/" for model name (e.g., "gpt-4o" from "openai/gpt-4o")
                model_display = config.agent_config.model_name.split("/")[-1]
                return f"{base_title} : {model_display.upper()}"
            else:
                return base_title
                
        except Exception:
            # Fallback to original title if something goes wrong
            return "JUNO-AI-CLI - AI Coding Assistant"
        
    def compose(self) -> ComposeResult:
        """Compose the UI."""
        yield Header()
        self.chat_area = ChatArea()
        yield self.chat_area
        self.chat_input = ChatInput()
        yield self.chat_input
        yield Footer()
    
    async def on_mount(self) -> None:
        """Initialize the app after mounting."""
        # Initialize TinyCodeAgent with no console output (Textual handles UI)
        self.tiny_code_agent = TinyCodeAgentChat(self.config_manager, console=None)
        
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
    
    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()
    
    def action_clear(self) -> None:
        """Clear the chat area."""
        if self.chat_area:
            self.chat_area.clear_messages()
            self.chat_area.add_message(
                "Chat cleared. How can I help you?",
                is_user=False
            )