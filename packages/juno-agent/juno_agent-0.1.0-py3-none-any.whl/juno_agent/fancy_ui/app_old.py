"""Main TUI application with welcome screen support."""

import asyncio
import getpass
import time
from pathlib import Path
from typing import List, Dict, Any
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.binding import Binding
from textual.screen import Screen
from textual.reactive import reactive
from textual import work, events

from .widgets.chat_area import ChatArea
from .widgets.input_area import ChatInput
from .widgets.history_menu import HistoryMenu
from .widgets.history_autocomplete import HistoryAutocomplete
from .widgets.model_selection_menu import ModelSelectionMenu, APIKeyPrompt, GlobalDefaultMenu, YesNoMenu
from .widgets.ide_selection_menu import IDESelectionMenu
from .widgets.base_selection_menu import BaseSelectionMenu
from .screens import WelcomeScreenView, ChatScreenView
from .components import DynamicFooter
from ..config import ConfigManager
from ..utils import SystemStatus, open_browser
from ..tiny_agent import TinyCodeAgentChat
from ..editors import MCPServerInstaller
from ..debug_logger import debug_logger
from ..storage_manager_async import AsyncConversationStorageManager
from .setup import (
    ClaudePermissionsService,
    MCPInstaller,
    DependencyScanner,
    ExternalContextManager
)
from .utils.welcome_message_builder import WelcomeMessageBuilder


class PyWizardTUIApp(App):
    """Main TUI application with integrated welcome and chat interface."""
    
    CSS_PATH = Path(__file__).parent / "styles" / "chat.tcss"
    
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+q", "quit", "Quit"),
        # Removed escape binding - Escape should only hide autocomplete, not exit app
        Binding("ctrl+n", "new_chat", "New Chat"),
        Binding("ctrl+r", "toggle_tool_expansion", "Toggle Tool Details"),
        Binding("f1", "show_history", "History"),
        Binding("ctrl+shift+h", "show_history", "History"),
        Binding("f2", "copy_selection", "Copy"),
        Binding("ctrl+s", "toggle_selection_mode", "Toggle Selection"),
    ]
    
    def __init__(self, config_manager: ConfigManager, show_welcome: bool = True, auto_start_setup: bool = False, verify_only_mode: bool = False, agentic_resolver_mode: bool = False):
        super().__init__()
        
        self.config_manager = config_manager
        # Set dynamic title based on current working directory
        self.title = self._generate_dynamic_title()
        self.debug_log = config_manager.create_debug_logger(debug=True)
        self.system_status = SystemStatus(config_manager.workdir)
        self.show_welcome_section = show_welcome  # Keep for backward compatibility, but no longer used
        self.auto_start_setup = auto_start_setup  # Flag to automatically start setup wizard on mount
        self.verify_only_mode = verify_only_mode  # Flag to run only verification, skip setup
        self.agentic_resolver_mode = agentic_resolver_mode  # Flag to run agentic dependency resolver
        self.tiny_code_agent = None
        self.chat_area = None
        self.chat_input = None
        self.dynamic_footer = None
        self.history_menu = None
        self.model_selection_menu = None
        self.api_key_prompt = None
        
        # Initialize storage manager
        try:
            
            self.storage_manager = AsyncConversationStorageManager()
        except Exception as e:
            # If storage manager fails to initialize, continue without it
            print(f"[DEBUG] PyWizardTUIApp.__init__: Failed to create storage manager: {e}")
            import traceback
            print(f"[DEBUG] PyWizardTUIApp.__init__: Storage manager error traceback: {traceback.format_exc()}")
            self.storage_manager = None
        
        # Tool expansion state management
        self.tool_calls_expanded = False  # Global state for tool call expansion
        
        # Setup state management
        self.setup_active = False
        self.setup_step = 0
        self.setup_data = {}
        self.setup_steps = []
        
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
            return "juno-agent - AI Coding Assistant"
        
    def compose(self) -> ComposeResult:
        """Compose the integrated interface."""
        yield Header()
        
        # Chat area 
        self.chat_area = ChatArea()
        yield self.chat_area
        
        # Input area at the bottom
        self.chat_input = ChatInput(storage_manager=self.storage_manager)
        yield self.chat_input
        
        # Dynamic footer with context-aware hints
        self.dynamic_footer = DynamicFooter()
        yield self.dynamic_footer
        
        # History menu (initially hidden)
        self.history_menu = HistoryMenu()
        yield self.history_menu
        
        # Model selection menu (initially hidden)
        self.model_selection_menu = ModelSelectionMenu()
        yield self.model_selection_menu
        
        # API key prompt (initially hidden)
        self.api_key_prompt = APIKeyPrompt()
        yield self.api_key_prompt
        
        # Global default menu (initially hidden)
        self.global_default_menu = GlobalDefaultMenu()
        yield self.global_default_menu
        
        # Reusable Yes/No menu (initially hidden)
        self.yes_no_menu = YesNoMenu()
        yield self.yes_no_menu
        
        # Editor selection menu (initially hidden)
        self.ide_selection_menu = IDESelectionMenu()
        yield self.ide_selection_menu
    
    async def on_mount(self) -> None:
        """Initialize the app after mounting."""
        # Add comprehensive welcome message to chat area
        welcome_message = self._create_welcome_message()
        self.chat_area.add_message(welcome_message, is_user=False)
        
        # Initialize TinyAgent if possible
        try:
            from ..tiny_agent import TinyCodeAgentChat
            # Pass the tool usage update callback and storage manager to TinyAgent
            print(f"[DEBUG] _initialize_agent: Creating TinyCodeAgentChat with storage_manager: {self.storage_manager is not None}")
            
            self.tiny_code_agent = TinyCodeAgentChat(
                self.config_manager, 
                debug=False,
                ui_callback=self.ui_tool_update_callback,
                storage_manager=self.storage_manager
            )
            
            print(f"[DEBUG] _initialize_agent: TinyCodeAgentChat created, initializing agent...")
            await self.tiny_code_agent.initialize_agent()
            print(f"[DEBUG] _initialize_agent: Agent initialized")
            
            self.chat_area.add_message("🤖 **AI Assistant ready!** Type your questions or commands.", is_user=False)
            
            # Update footer to show agent is running
            self._update_footer_stats()
        except Exception as e:
            self.chat_area.add_message(f"⚠️ AI Assistant initialization failed: {str(e)}", is_user=False)
        
        # Focus the input
        self.chat_input.focus_input()
        
        # Start periodic footer stats updates
        self.set_interval(5.0, self._periodic_footer_update)
        
        # Auto-start setup wizard or verification if requested
        if self.auto_start_setup:
            # Delay slightly to ensure UI is fully loaded
            self.debug_log.debug(f"Auto-start setup mode enabled, setting timer")
            self.set_timer(0.5, self._auto_start_setup_wizard)
        elif self.verify_only_mode:
            # Start verification only mode immediately
            self.debug_log.debug(f"Verify-only mode enabled, calling verification directly")
            self.call_after_refresh(self._auto_start_verification_only)
        elif self.agentic_resolver_mode:
            # Start agentic resolver mode (for --docs-only)
            self.debug_log.debug(f"Agentic resolver mode enabled, calling agentic dependency resolver directly")
            self.set_timer(0.5, self._auto_start_agentic_resolver)
        else:
            self.debug_log.debug(f"No auto-start mode enabled: auto_start_setup={self.auto_start_setup}, verify_only_mode={self.verify_only_mode}, agentic_resolver_mode={self.agentic_resolver_mode}")
    
    async def initialize_agent(self) -> None:
        """Initialize or reinitialize the TinyAgent with current configuration."""
        try:
            from ..tiny_agent import TinyCodeAgentChat
            
            self.debug_log.debug("Reinitializing TinyCodeAgentChat with updated configuration")
            
            # Create new TinyCodeAgentChat instance with updated config
            self.tiny_code_agent = TinyCodeAgentChat(
                self.config_manager, 
                debug=False,
                ui_callback=self.ui_tool_update_callback,
                storage_manager=self.storage_manager
            )
            
            # Initialize the agent
            await self.tiny_code_agent.initialize_agent()
            self.debug_log.info("TinyCodeAgentChat reinitialized successfully")
            
            # Update footer to show agent is running
            self._update_footer_stats()
            
        except Exception as e:
            self.debug_log.error(f"Error reinitializing agent: {str(e)}")
            # Re-raise the exception so it can be handled by the caller
            raise e
    
    async def on_history_menu_session_selected(self, message: HistoryMenu.SessionSelected) -> None:
        """Handle session selection from history menu."""
        try:
            await self._load_conversation(message.session)
        except Exception as e:
            self.chat_area.add_message(f"❌ **Error loading conversation**: {str(e)}", is_user=False)
    
    async def on_history_menu_menu_closed(self, message: HistoryMenu.MenuClosed) -> None:
        """Handle history menu being closed."""
        if self.chat_input:
            self.chat_input.focus_input()
    
    async def on_history_autocomplete_session_selected(self, message: HistoryAutocomplete.SessionSelected) -> None:
        """Handle session selection from history autocomplete dropdown."""
        try:
            await self._load_conversation(message.session)
        except Exception as e:
            self.chat_area.add_message(f"❌ **Error loading conversation**: {str(e)}", is_user=False)
    
    async def on_model_selection_menu_model_selected(self, message: ModelSelectionMenu.ModelSelected) -> None:
        """Handle model selection from the model selection menu."""
        await self._handle_model_selected(message.model, message.provider)
    
    async def on_model_selection_menu_manual_entry_requested(self, message: ModelSelectionMenu.ManualEntryRequested) -> None:
        """Handle manual model entry request."""
        await self._handle_manual_model_entry()
    
    async def on_model_selection_menu_menu_closed(self, message: ModelSelectionMenu.MenuClosed) -> None:
        """Handle model selection menu being closed."""
        self.chat_area.add_message("ℹ️ **Model selection canceled** - Current model unchanged.", is_user=False)
        if self.chat_input:
            self.chat_input.focus_input()
    
    async def on_api_key_prompt_api_key_entered(self, message: APIKeyPrompt.APIKeyEntered) -> None:
        """Handle API key being entered."""
        debug_log = self.debug_log
        debug_log.debug(f"APIKeyPrompt.APIKeyEntered message received", provider=message.provider, has_key=bool(message.api_key))
        await self._handle_api_key_entered(message.api_key, message.provider)
    
    async def on_api_key_prompt_api_key_prompt_canceled(self, message: APIKeyPrompt.APIKeyPromptCanceled) -> None:
        """Handle API key prompt being canceled."""
        self.chat_area.add_message("❌ **API key entry canceled** - Model configuration incomplete.", is_user=False)
        # Hide both prompts if they're showing
        if self.api_key_prompt:
            self.api_key_prompt.hide()
        if self.model_selection_menu:
            self.model_selection_menu.hide()
        if self.chat_input:
            self.chat_input.focus_input()
    
    async def on_global_default_menu_global_default_selected(self, message: GlobalDefaultMenu.GlobalDefaultSelected) -> None:
        """Handle global default selection from menu."""
        await self._handle_global_default_selection(message.set_global)
    
    async def on_global_default_menu_menu_closed(self, message: GlobalDefaultMenu.MenuClosed) -> None:
        """Handle global default menu being closed without selection."""
        # Default to local-only if user cancels
        await self._handle_global_default_selection(False)
    
    async def on_yes_no_menu_yes_no_selected(self, message: YesNoMenu.YesNoSelected) -> None:
        """Handle Yes/No selection from menu."""
        await self._handle_yes_no_selection(message.selected_yes, message.context)
    
    async def on_yes_no_menu_menu_closed(self, message: YesNoMenu.MenuClosed) -> None:
        """Handle Yes/No menu being closed without selection."""
        await self._handle_yes_no_selection(False, message.context)
    
    async def on_base_selection_menu_option_selected(self, message: BaseSelectionMenu.OptionSelected) -> None:
        """Handle IDE selection from IDESelectionMenu."""
        if self.setup_active and hasattr(self, 'setup_data'):
            await self._handle_editor_selection(message.value)
    
    async def on_base_selection_menu_selection_cancelled(self, message: BaseSelectionMenu.SelectionCancelled) -> None:
        """Handle IDE selection cancellation."""
        if self.setup_active:
            self.chat_area.add_message("IDE selection cancelled. Continuing with setup...", is_user=False)
            # Skip this step and continue
            self.setup_step += 1
            await self._start_enhanced_setup_step()
    
    def on_key(self, event: events.Key) -> None:
        """Handle global key events for the application."""
        # Route key events to HistoryMenu when it's visible and focused
        # History menu now handles keys automatically through BINDINGS
        # No manual forwarding needed
    
    async def _load_conversation(self, session: Dict[str, Any]) -> None:
        """Load a conversation session and reconstruct the chat area."""
        session_id = session.get('session_id')
        if not session_id:
            self.chat_area.add_message("❌ **Invalid session**: No session ID found", is_user=False)
            return
        
        try:
            # Show loading message
            loading_msg = self.chat_area.add_message(f"🔄 **Loading conversation session {session_id[:8]}...**", is_user=False)
            
            # Load full session data from storage
            session_data = await self.storage_manager.load_session(session_id)
            
            if not session_data:
                # Remove loading message
                if hasattr(self.chat_area, 'remove_last_message'):
                    self.chat_area.remove_last_message()
                self.chat_area.add_message(f"❌ **Session not found**: Could not load session {session_id[:8]}", is_user=False)
                return
            
            # Extract messages from session data
            messages = self._extract_messages_from_session(session_data)
            
            if not messages:
                # Remove loading message
                if hasattr(self.chat_area, 'remove_last_message'):
                    self.chat_area.remove_last_message()
                self.chat_area.add_message(f"📝 **Empty session**: Session {session_id[:8]} has no messages", is_user=False)
                return
            
            # Clear current chat area
            self.chat_area.clear_messages()
            
            # Add session loaded header
            created_at = session.get('created_at', 'unknown')
            message_count = len(messages)
            
            # Format creation time
            try:
                if created_at != 'unknown':
                    from datetime import datetime
                    created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    created_str = created_dt.strftime('%Y-%m-%d %H:%M')
                else:
                    created_str = 'unknown'
            except:
                created_str = str(created_at)[:16] if created_at != 'unknown' else 'unknown'
            
            header_msg = f"📝 **Conversation Loaded**\n\nSession: {session_id[:8]}...\nCreated: {created_str}\nMessages: {message_count}\n\n*You can continue this conversation from where it left off.*"
            self.chat_area.add_message(header_msg, is_user=False)
            
            # Reconstruct conversation messages
            await self._reconstruct_messages(messages)
            
            # Restore agent session if possible
            await self._restore_agent_session(session_id, session_data)
            
            # Focus input for continuation
            if self.chat_input:
                self.chat_input.focus_input()
            
        except Exception as e:
            # Remove loading message if it exists
            if hasattr(self.chat_area, 'remove_last_message'):
                self.chat_area.remove_last_message()
            self.chat_area.add_message(f"❌ **Error loading conversation**: {str(e)}", is_user=False)
    
    def _extract_messages_from_session(self, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract messages from session data structure."""
        messages = []
        
        # Try different possible locations for messages in session data
        if isinstance(session_data, dict):
            # Check for direct session_data.messages
            if 'messages' in session_data:
                messages = session_data['messages']
            # Check for session_data.session_data.messages (nested structure)
            elif 'session_data' in session_data:
                nested_data = session_data['session_data']
                if isinstance(nested_data, str):
                    # Parse JSON string
                    try:
                        import json
                        nested_data = json.loads(nested_data)
                    except json.JSONDecodeError:
                        pass
                if isinstance(nested_data, dict) and 'messages' in nested_data:
                    messages = nested_data['messages']
            # Check for session_state.messages
            elif 'session_state' in session_data and isinstance(session_data['session_state'], dict):
                session_state = session_data['session_state']
                if 'messages' in session_state:
                    messages = session_state['messages']
        
        # Ensure messages is a list
        if not isinstance(messages, list):
            messages = []
        
        return messages
    
    async def _reconstruct_messages(self, messages: List[Dict[str, Any]]) -> None:
        """Reconstruct conversation messages in the chat area using the same tool display system as live conversations."""
        tool_call_mapping = {}  # Map tool_call_id to tool calls for proper pairing
        
        for msg in messages:
            if not isinstance(msg, dict):
                continue
            
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            
            if role == 'user':
                self.chat_area.add_message(content, is_user=True)
            elif role in ['assistant', 'agent']:
                # Create agent message with content
                agent_message = self.chat_area.add_message(content or "(Assistant response)", is_user=False)
                
                # Process tool calls using the same system as live conversations
                tool_calls = msg.get('tool_calls', [])
                for tool_call in tool_calls:
                    tool_event_data = self._convert_tool_call_to_event(tool_call)
                    if tool_event_data:
                        tool_call_id = tool_event_data.get('tool_call_id', '')
                        tool_call_mapping[tool_call_id] = tool_call
                        
                        # Use the existing tool event system
                        await self.chat_area.add_tool_event("tool_start", tool_event_data)
            elif role == 'tool':
                # Process tool response using the existing system
                tool_call_id = msg.get('tool_call_id', '')
                tool_name = msg.get('name', 'unknown')
                tool_content = msg.get('content', '')
                
                # Create tool end event data
                tool_end_data = {
                    'tool_call_id': tool_call_id,
                    'tool_name': tool_name,
                    'result': tool_content
                }
                
                # Use the existing tool event system for completion
                await self.chat_area.add_tool_event("tool_end", tool_end_data)
            # Skip system messages for now as they're usually not part of the visible conversation
    
    def _convert_tool_call_to_event(self, tool_call: dict) -> dict:
        """Convert a loaded tool call to the event format used by the live tool system."""
        try:
            function_data = tool_call.get('function', {})
            tool_name = function_data.get('name', 'unknown')
            tool_args = function_data.get('arguments', '{}')
            tool_call_id = tool_call.get('id', '')
            
            # Parse arguments
            try:
                import json
                args_dict = json.loads(tool_args) if isinstance(tool_args, str) else tool_args
            except:
                args_dict = {}
            
            # Create tool event data in the same format as live tools
            return {
                'tool_call_id': tool_call_id,
                'tool_name': tool_name,
                'arguments': args_dict,
                'agent_level': 0,  # Loaded conversations are treated as main agent level
                'is_subagent': False
            }
            
        except Exception as e:
            return None
    
    
    async def _restore_agent_session(self, session_id: str, session_data: Dict[str, Any]) -> None:
        """Restore the agent session with the loaded conversation.
        
        CRITICAL FIX: This now properly recreates the agent with the loaded session's
        user_id and session_id, ensuring cross-project session loading works correctly.
        """
        try:
            # Extract session parameters from loaded data
            loaded_session_id = session_data.get('session_id', session_id)
            loaded_user_id = session_data.get('user_id')
            
            print(f"[DEBUG] _restore_agent_session: Restoring session {loaded_session_id} for user {loaded_user_id}")
            
            if not loaded_user_id:
                print(f"[DEBUG] _restore_agent_session: No user_id found in session data, falling back to old behavior")
                # Fallback to old behavior if no user_id available
                if self.tiny_code_agent and hasattr(self.tiny_code_agent, 'load_session'):
                    await self.tiny_code_agent.load_session(loaded_session_id)
                    print(f"[DEBUG] Agent session restored for {loaded_session_id} (fallback)")
                return
            
            # CRITICAL FIX: Recreate agent with correct session and user context
            if self.tiny_code_agent and hasattr(self.tiny_code_agent, 'recreate_with_session_context'):
                print(f"[DEBUG] _restore_agent_session: Recreating agent with session_id: {loaded_session_id}, user_id: {loaded_user_id}")
                
                success = await self.tiny_code_agent.recreate_with_session_context(loaded_session_id, loaded_user_id)
                
                if success:
                    print(f"[DEBUG] _restore_agent_session: Agent successfully recreated with correct context")
                    
                    # Load the session messages into the recreated agent
                    if hasattr(self.tiny_code_agent, 'load_session'):
                        await self.tiny_code_agent.load_session(loaded_session_id)
                        print(f"[DEBUG] _restore_agent_session: Session messages loaded into recreated agent")
                    
                    # Show success message to user
                    self.chat_area.add_message("✅ **Agent Context Restored**: Agent successfully recreated with the loaded session's context. You can continue the conversation seamlessly.", is_user=False)
                else:
                    print(f"[DEBUG] _restore_agent_session: Failed to recreate agent with correct context")
                    self.chat_area.add_message("⚠️ **Partial Restore**: Conversation loaded but agent context could not be fully restored. The agent may have limited memory of this session.", is_user=False)
            else:
                print(f"[DEBUG] _restore_agent_session: Agent recreation not available, falling back to old behavior")
                # Fallback to old behavior
                if self.tiny_code_agent and hasattr(self.tiny_code_agent, 'load_session'):
                    await self.tiny_code_agent.load_session(loaded_session_id)
                    print(f"[DEBUG] Agent session restored for {loaded_session_id} (fallback)")
                elif self.tiny_code_agent and self.storage_manager:
                    self.storage_manager.current_session_id = loaded_session_id
                    print(f"[DEBUG] Storage manager session updated to {loaded_session_id} (fallback)")
                    
                self.chat_area.add_message("⚠️ **Note**: Conversation loaded but agent context may not be fully restored. The agent will continue with partial context.", is_user=False)
                
        except Exception as e:
            # Log but don't fail the conversation loading
            print(f"[DEBUG] _restore_agent_session: Error restoring agent session: {e}")
            import traceback
            print(f"[DEBUG] _restore_agent_session: Traceback: {traceback.format_exc()}")
            # Add a note to the user that the session loaded but agent context might not be restored
            self.chat_area.add_message("⚠️ **Error**: Conversation loaded but there was an error restoring agent context. The agent will continue with limited memory.", is_user=False)
    
    
    async def on_chat_input_submit(self, message: ChatInput.Submit) -> None:
        """Handle chat input submission."""
        user_message = message.content.strip()
        if not user_message:
            return
            
        # Add user message to chat
        self.chat_area.add_message(user_message, is_user=True)
        
        # Check if we're in setup mode
        if self.setup_active:
            await self._handle_setup_input(user_message)
        else:
            # Process the message normally
            if user_message.startswith("/"):
                # Handle commands
                await self._handle_command(user_message)
            else:
                # Handle regular chat - @work decorator runs async but allows direct UI access
                self._handle_chat_message(user_message)
    
    async def _handle_command(self, command: str) -> None:
        """Handle slash commands."""
        # Parse command and arguments
        parts = command.split(" ", 1)
        cmd = parts[0]
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd == "/help":
            help_text = """# 🤖 juno-agent Help

## **Available Commands:**

• `/cost` - Show detailed token usage and cost breakdown for the current session
• `/new-chat` - Clear conversation history and free up context
• `/reset` - Clear conversation history and free up context  
• `/compact` - Clear conversation history but keep a summary in context
• `/history` - View and manage conversation history
• `/setup` - Run the setup wizard to configure juno-agent (API key, editor, model, etc.)
• `/model` - Configure AI model, provider, and API keys
• `/help` - Show this help
• `/clear` - Clear chat history (alias for /reset)
• `/quit` - Exit application

## **Keyboard Shortcuts:**

• **Ctrl+C** - Quit application
• **Escape** - Quit application
• **Ctrl+N** - New chat (reset conversation)
• **Ctrl+Q** - Quit application
• **Ctrl+R** - Toggle tool call details (expand/collapse all tool calls)

## **Usage:**
Just type your questions - AI assistant will help!

**Example:**
- "How do I create a Python function?"
- "Help me debug this code"
- "Explain what this code does"

*Type / to see command autocomplete!*"""
            self.chat_area.add_message(help_text, is_user=False)
        
        elif cmd == "/cost":
            # Show session cost and duration
            await self._handle_cost_command()
        
        elif cmd in ["/new-chat", "/reset", "/clear"]:
            # Clear conversation history
            self.chat_area.clear_messages()
            if cmd == "/new-chat":
                self.chat_area.add_message("✨ **New chat started!** Conversation history cleared and context freed up. How can I help you?", is_user=False)
            else:
                self.chat_area.add_message("🧹 **Chat reset!** Conversation history cleared. How can I help you?", is_user=False)
            
            # Reset footer stats since conversation is cleared
            if self.dynamic_footer:
                self.dynamic_footer.reset_usage_stats()
        
        elif cmd == "/compact":
            # Compact conversation using TinyCodeAgent
            # Pass any additional arguments as summarization instructions
            await self._handle_compact_command(args)
        
        elif cmd == "/setup":
            # Run setup wizard
            await self._handle_setup_command()
        
        elif cmd == "/history":
            # View and manage conversation history
            await self._handle_history_command()
        
        elif cmd == "/model":
            # Configure AI model
            await self._handle_model_command()
        
        elif cmd == "/quit":
            self.exit()
        
        else:
            self.chat_area.add_message(f"❓ Unknown command: `{cmd}`. Type `/help` for available commands or `/` for autocomplete.", is_user=False)
    
    @work(exclusive=False)
    async def _handle_chat_message(self, message: str) -> None:
        """Handle regular chat messages in a worker."""
        if self.tiny_code_agent:
            try:
                # Show thinking indicator
                thinking_msg = self.chat_area.add_message("🤖 Thinking...", is_user=False)
                
                # Get AI response
                response = await self.tiny_code_agent.process_chat_message(message)
                
                # Instead of removing and creating new message, update the existing one
                # The thinking message already has tool calls attached, so we just update its content
                if self.chat_area.current_agent_message == thinking_msg:
                    # Update the thinking message content to the final response
                    thinking_msg.content = response
                    thinking_msg._update_with_tool_calls()  # This includes both content and tool calls
                    debug_logger.log_event("updated_thinking_message_to_final_response",
                                         final_response_length=len(response),
                                         tool_calls_count=len(thinking_msg.tool_calls),
                                         pending_tool_calls_count=len(thinking_msg.pending_tool_calls))
                else:
                    # Fallback: remove thinking and add new message (preserve tool calls)
                    if hasattr(self.chat_area, 'remove_last_message'):
                        self.chat_area.remove_last_message()
                    agent_msg = self.chat_area.add_message(response, is_user=False)
                    debug_logger.log_event("fallback_to_remove_and_add_message")
                
                # Update footer hint based on tool calls presence and refresh stats
                self._update_footer_hint()
                
                # Note: Tool calls are handled in real-time by the ui_tool_update_callback system
                # Tool calls remain attached to the same message, now with the final response content
                
            except Exception as e:
                if hasattr(self.chat_area, 'remove_last_message'):
                    self.chat_area.remove_last_message()
                self.chat_area.add_message(f"❌ Error: {str(e)}", is_user=False)
        else:
            # Check what's missing and provide helpful guidance
            config = self.config_manager.load_config()
            if not self.config_manager.has_api_key():
                self.chat_area.add_message("🔧 **AI Assistant requires API key**\n\nPlease set your API key with `/apikey` command to start chatting.", is_user=False)
            elif not self.config_manager.is_model_configured():
                self.chat_area.add_message("🔧 **AI Assistant requires model configuration**\n\nPlease configure your AI model with `/model` command to start chatting.", is_user=False)
            else:
                self.chat_area.add_message("🔧 **AI Assistant not available**\n\nThere was an error initializing the AI assistant. Try the `/model` command to reconfigure.", is_user=False)
    
    async def _handle_cost_command(self) -> None:
        """Handle /cost command - show conversation cost and token usage."""
        if not self.tiny_code_agent or not hasattr(self.tiny_code_agent, 'agent') or not self.tiny_code_agent.agent:
            self.chat_area.add_message("❌ **No active TinyAgent session**\n\nCost tracking is only available when TinyAgent is initialized.", is_user=False)
            return
        
        try:
            # Get the agent instance
            agent = self.tiny_code_agent.agent
            
            # Look for TokenTracker in callbacks
            cost_info = None
            has_child_trackers = False
            child_tracker_count = 0
            
            if hasattr(agent, 'callbacks'):
                for callback in agent.callbacks:
                    callback_type = type(callback).__name__
                    
                    if callback_type == 'TokenTracker' or hasattr(callback, 'get_total_usage'):
                        try:
                            # TokenTracker has get_total_usage() method
                            if hasattr(callback, 'get_total_usage'):
                                stats = callback.get_total_usage()
                                
                                # Check for child trackers and aggregate their costs
                                if hasattr(callback, 'child_trackers') and callback.child_trackers:
                                    try:
                                        child_count = len(callback.child_trackers)
                                        has_child_trackers = True
                                        child_tracker_count = child_count
                                    except TypeError:
                                        # Handle Mock objects that don't support len()
                                        try:
                                            child_count = len(list(callback.child_trackers))
                                            has_child_trackers = True
                                            child_tracker_count = child_count
                                        except TypeError:
                                            pass
                                    
                                    child_tokens = 0
                                    child_cost = 0.0
                                    child_calls = 0
                                    child_prompt_tokens = 0
                                    child_completion_tokens = 0
                                    
                                    for child_tracker in callback.child_trackers:
                                        if hasattr(child_tracker, 'get_total_usage'):
                                            child_stats = child_tracker.get_total_usage()
                                            child_tokens += child_stats.total_tokens
                                            child_cost += child_stats.cost
                                            child_calls += child_stats.call_count
                                            child_prompt_tokens += getattr(child_stats, 'prompt_tokens', 0)
                                            child_completion_tokens += getattr(child_stats, 'completion_tokens', 0)
                                    
                                    # Create aggregated stats including all child tracker data
                                    from types import SimpleNamespace
                                    aggregated_stats = SimpleNamespace(
                                        prompt_tokens=stats.prompt_tokens + child_prompt_tokens,
                                        completion_tokens=stats.completion_tokens + child_completion_tokens,
                                        total_tokens=stats.total_tokens + child_tokens,
                                        cost=stats.cost + child_cost,
                                        call_count=stats.call_count + child_calls,
                                        thinking_tokens=getattr(stats, 'thinking_tokens', 0),
                                        reasoning_tokens=getattr(stats, 'reasoning_tokens', 0),
                                        cache_creation_input_tokens=getattr(stats, 'cache_creation_input_tokens', 0),
                                        cache_read_input_tokens=getattr(stats, 'cache_read_input_tokens', 0)
                                    )
                                    stats = aggregated_stats
                                
                                cost_info = stats
                                break
                        except Exception:
                            continue
                    # Fallback: check for any callback with get_usage_stats method
                    elif hasattr(callback, 'get_usage_stats'):
                        try:
                            stats = callback.get_usage_stats()
                            cost_info = stats
                            break
                        except Exception:
                            continue
            
            if cost_info:
                # Check if this includes subagent costs
                if has_child_trackers:
                    subagent_info = f"• **Includes Subagent Costs**: ✅ Yes ({child_tracker_count} subagents tracked)"
                else:
                    subagent_info = "• **Includes Subagent Costs**: ❌ No subagent usage detected"
                
                # Display detailed cost information
                cost_content = f"""**💰 Conversation Cost Analysis**

**📊 Token Usage**
• **Prompt Tokens**: {cost_info.prompt_tokens:,}
• **Completion Tokens**: {cost_info.completion_tokens:,}
• **Total Tokens**: {cost_info.total_tokens:,}

**💸 Cost Breakdown**
• **Total Cost**: ${cost_info.cost:.4f}
• **API Calls**: {cost_info.call_count}
• **Average per Call**: ${(cost_info.cost / max(cost_info.call_count, 1)):.4f}
{subagent_info}

**🧠 Advanced Tokens (if supported)**
• **Thinking Tokens**: {getattr(cost_info, 'thinking_tokens', 0):,}
• **Reasoning Tokens**: {getattr(cost_info, 'reasoning_tokens', 0):,}
• **Cache Creation**: {getattr(cost_info, 'cache_creation_input_tokens', 0):,}
• **Cache Read**: {getattr(cost_info, 'cache_read_input_tokens', 0):,}

*💡 Cost tracking includes both main agent and subagent usage when available*"""
                
                self.chat_area.add_message(cost_content, is_user=False)
            else:
                # Fallback: try to get basic token count
                if hasattr(agent, 'count_tokens'):
                    # Estimate tokens from conversation history
                    conversation_text = ""
                    if hasattr(self.tiny_code_agent, 'conversation_history'):
                        for entry in self.tiny_code_agent.conversation_history:
                            conversation_text += entry.get('content', '') + "\n"
                    
                    estimated_tokens = agent.count_tokens(conversation_text)
                    estimated_cost = estimated_tokens * 0.00001  # Rough estimate
                    
                    fallback_content = f"""**💰 Estimated Cost Analysis**

**📊 Estimated Usage**
• **Estimated Tokens**: {estimated_tokens:,}
• **Estimated Cost**: ${estimated_cost:.4f}

⚠️ **Note**: This is a rough estimate. Enable TokenTracker for accurate tracking.

*💡 Add TokenTracker hook for precise cost tracking*"""
                    
                    self.chat_area.add_message(fallback_content, is_user=False)
                else:
                    self.chat_area.add_message("📊 **Cost tracking not available**\n\nEnable TokenTracker hook for detailed cost analysis.", is_user=False)
        
        except Exception as e:
            self.chat_area.add_message(f"❌ **Error retrieving cost information**: {str(e)}", is_user=False)
    
    async def _handle_compact_command(self, summarization_instructions: str = "") -> None:
        """Handle /compact command - compact conversation using TinyCodeAgent.
        
        Uses TinyAgent's compact() method which compacts the conversation AND updates the agent's context,
        unlike summarize() which only generates a summary without updating context.
        
        Args:
            summarization_instructions: Optional instructions for how to compact the conversation
        """
        if not self.tiny_code_agent or not hasattr(self.tiny_code_agent, 'agent') or not self.tiny_code_agent.agent:
            self.chat_area.add_message("❌ **No active TinyAgent session**\n\nConversation compacting requires TinyAgent to be initialized.\nPlease wait for TinyAgent to initialize or check your configuration.", is_user=False)
            return
        
        try:
            # Show processing message with custom instructions if provided
            if summarization_instructions.strip():
                processing_msg = self.chat_area.add_message(f"🗜️ **Compacting conversation history...**\n\nGenerating summary with custom instructions: *{summarization_instructions.strip()}*\n\nThis will preserve context while reducing tokens...", is_user=False)
            else:
                processing_msg = self.chat_area.add_message("🗜️ **Compacting conversation history...**\n\nGenerating summary to preserve context while reducing tokens...", is_user=False)
            
            # Use TinyAgent's compact method (preferred) or fallback to summarize
            agent = self.tiny_code_agent.agent
            summary = None
            compact_success = False
            
            if hasattr(agent, 'compact'):
                # Call the compact method - it returns True/False, not the summary text
                # The compact() method handles the conversation replacement internally
                compact_success = await agent.compact()
                
                # If compact was successful, get the summary from the compacted conversation
                # The compact method replaces the conversation with [system, user_with_summary]
                if compact_success and len(agent.messages) >= 2:
                    # Extract the summary from the user message that compact() created
                    summary_message = agent.messages[1]  # Second message after system
                    if summary_message.get("role") == "user":
                        content = summary_message.get("content", "")
                        # Extract the summary part from the formatted content
                        if content.startswith("This session is being continued from a previous conversation"):
                            # Find the summary between the intro text and any trailing text
                            lines = content.split('\n')
                            summary_lines = []
                            capture_summary = False
                            for line in lines:
                                if line.startswith("This session is being continued"):
                                    capture_summary = True
                                    continue
                                if capture_summary and line.strip():
                                    summary_lines.append(line)
                            summary = '\n'.join(summary_lines).strip()
                
            elif hasattr(agent, 'summarize'):
                # Fallback to summarize method (doesn't update context automatically)
                summary = await agent.summarize()
                # For summarize, we need to manually clear and reset if we want compacting behavior
                if summary and not summary.startswith("Failed to generate summary:"):
                    compact_success = True
                    # Manually clear conversation and add summary (basic compacting simulation)
                    if hasattr(agent, 'clear_conversation'):
                        agent.clear_conversation()
                        # Add summary as a user message to maintain context
                        agent.messages.append({
                            "role": "user",
                            "content": f"This session is being continued from a previous conversation that ran out of context. The conversation is summarized below:\n{summary}",
                            "created_at": int(time.time()) if hasattr(time, 'time') else 0
                        })
            else:
                summary = None
            
            # Remove processing message
            if hasattr(self.chat_area, 'remove_last_message'):
                self.chat_area.remove_last_message()
            elif self.chat_area.messages and self.chat_area.messages[-1]:
                self.chat_area.messages[-1].remove()
                self.chat_area.messages.pop()
            
            if compact_success:
                # Display success message with summary preview if available
                instructions_note = f"\n**Summary Instructions Used**: *{summarization_instructions.strip()}*\n" if summarization_instructions.strip() else ""
                
                if summary:
                    # Extract first 2 paragraphs for preview
                    summary_preview = self._extract_first_two_paragraphs(summary)
                    
                    summary_content = f"""**✅ Conversation Compacted Successfully**

**Summary Preview:**
{summary_preview}
{instructions_note}
The conversation history has been compacted while preserving this context for continuity.

How can I continue helping you?"""
                else:
                    summary_content = f"""**✅ Conversation Compacted Successfully**

The conversation history has been compacted and summarized internally by TinyAgent.
{instructions_note}
Context has been preserved while reducing token usage.

How can I continue helping you?"""
                
                # Clear conversation history in the UI
                self.chat_area.clear_messages()
                
                # Add the success message
                self.chat_area.add_message(summary_content, is_user=False)
                
                # Note: Don't reset conversation in TinyAgent since compact() already handled it
                
            elif hasattr(agent, 'compact'):
                # Agent has compact method but it returned False (failed)
                self.chat_area.add_message("⚠️ **Compacting failed**\n\nThe conversation may be too short to generate a meaningful summary, or there was an error during compacting.\nYou can try again after having a longer conversation.", is_user=False)
            elif hasattr(agent, 'summarize'):
                # Agent has summarize method but no summary was generated
                self.chat_area.add_message("⚠️ **No summary generated**\n\nThe conversation may be too short to generate a meaningful summary.\nYou can try again after having a longer conversation.", is_user=False)
            else:
                # Fallback: basic compacting without summarization
                self.chat_area.clear_messages()
                fallback_msg = """🗜️ **Chat compacted (basic mode)**

Conversation history has been cleared to free up context.

**Note**: Advanced compacting not available with current TinyAgent version.
The agent will start fresh but won't retain context from previous conversation.

How can I help you?"""
                
                self.chat_area.add_message(fallback_msg, is_user=False)
                
                # Reset conversation history 
                if hasattr(self.tiny_code_agent, 'reset_conversation'):
                    self.tiny_code_agent.reset_conversation()
        
        except Exception as e:
            # Remove processing message if it exists
            if hasattr(self.chat_area, 'remove_last_message'):
                self.chat_area.remove_last_message()
            elif self.chat_area.messages and self.chat_area.messages[-1]:
                self.chat_area.messages[-1].remove()
                self.chat_area.messages.pop()
            
            self.chat_area.add_message(f"❌ **Error compacting conversation**: {str(e)}\n\nFalling back to basic history clearing...", is_user=False)
            
            # Fallback: clear messages anyway
            self.chat_area.clear_messages()
            self.chat_area.add_message("🧹 **Chat cleared** due to compacting error.\n\nHow can I help you?", is_user=False)
            
            # Update footer hint (no tool calls after clearing)
            self._update_footer_hint()
    
    async def _auto_start_setup_wizard(self) -> None:
        """Automatically start the setup wizard - called from timer when auto_start_setup is True."""
        await self._handle_setup_command()
    
    async def _auto_start_verification_only(self) -> None:
        """Automatically start verification only mode - called from timer when verify_only_mode is True."""
        try:
            self.chat_area.add_message("🔍 **Auto-starting verification-only mode...**\n", is_user=False)
            await self._handle_verification_only_command()
        except Exception as e:
            self.chat_area.add_message(f"❌ **Error in verification mode**: {str(e)}\n", is_user=False)
            self.debug_log.error(f"Error in _auto_start_verification_only: {e}")
            import traceback
            self.debug_log.error(f"Traceback: {traceback.format_exc()}")
    
    async def _auto_start_agentic_resolver(self) -> None:
        """Automatically start agentic resolver mode - called from timer when agentic_resolver_mode is True."""
        try:
            self.chat_area.add_message("🤖 **Auto-starting Agentic Dependency Resolver...**\n\nUsing intelligent agent to scan dependencies and fetch documentation.\n", is_user=False)
            await self._handle_agentic_resolver_command()
        except Exception as e:
            self.chat_area.add_message(f"❌ **Error in agentic resolver mode**: {str(e)}\n", is_user=False)
            self.debug_log.error(f"Error in _auto_start_agentic_resolver: {e}")
            import traceback
            self.debug_log.error(f"Traceback: {traceback.format_exc()}")
    
    async def _handle_agentic_resolver_command(self) -> None:
        """Handle agentic resolver mode - run full dependency analysis and documentation fetching."""
        self.debug_log.debug("=" * 80)
        self.debug_log.debug("HANDLE_AGENTIC_RESOLVER_COMMAND - START")
        
        self.chat_area.add_message("**🤖 Agentic Dependency Resolver**\n\nUsing intelligent agent to analyze your project and fetch dependency documentation...\n\nThis will:\n- Intelligently scan your project for dependencies\n- Search and select the most relevant documentation\n- Fetch and organize documentation with metadata\n- Create symlinks and external context structure\n\n*Initializing agentic resolver...*\n", is_user=False)
        
        try:
            # Initialize setup components (this creates agentic_dependency_resolver)
            self.debug_log.debug("Initializing setup components...")
            await self._initialize_setup_components()
            self.debug_log.debug("Setup components initialized")
            
            # Use the already initialized resolver from setup components
            if not hasattr(self, 'agentic_dependency_resolver') or not self.agentic_dependency_resolver:
                # Only create if not already created by _initialize_setup_components
                self.debug_log.debug("Creating AgenticDependencyResolver instance (not found in setup components)...")
                from ..agentic_dependency_resolver import AgenticDependencyResolver
                
                self.agentic_dependency_resolver = AgenticDependencyResolver(
                    project_path=str(self.config_manager.workdir),
                    config_manager=self.config_manager,
                    ui_callback=self._dependency_progress_callback,
                    storage_manager=self.storage_manager
                )
                self.debug_log.debug("AgenticDependencyResolver instance created")
            else:
                self.debug_log.debug("Using existing AgenticDependencyResolver from setup components")
            
            resolver = self.agentic_dependency_resolver
            
            self.chat_area.add_message("🔄 **Running Agentic Dependency Resolution...**\n", is_user=False)
            
            # Run the complete resolver (scan dependencies + fetch docs)
            self.debug_log.debug("Calling resolver.run()...")
            result = await resolver.run()
            self.debug_log.debug(f"resolver.run() returned. Success: {result.get('success', False)}")
            
            if result.get('success', False):
                # The resolver returns files_created, file_names, etc.
                files_created = result.get('files_created', 0)
                file_names = result.get('file_names', [])
                symlinks_created = result.get('symlinks_created', False)
                
                # Try to get dependencies from scan results if available
                dependencies = result.get('dependencies', [])
                dependencies_count = len(dependencies) if dependencies else 0
                
                # If no dependencies from scan, estimate from files created
                if dependencies_count == 0 and files_created > 0:
                    dependencies_count = files_created
                
                self.chat_area.add_message(f"✅ **Agentic Dependency Resolution Complete!**\n\n**Summary:**\n- Dependencies processed: {dependencies_count}\n- Documentation files created: {files_created}\n- External context created: {'✅' if files_created > 0 else '❌'}\n- Symlinks created: {'✅' if symlinks_created else '❌'}\n\n", is_user=False)
                
                # Show file details if any were created
                if files_created > 0 and file_names:
                    file_list = "\n".join([f"- {name}" for name in file_names[:5]])
                    if len(file_names) > 5:
                        file_list += f"\n- ... and {len(file_names) - 5} more files"
                    self.chat_area.add_message(f"**📄 Documentation Files Created:**\n\n{file_list}\n\n*Agentic resolver has successfully processed your project dependencies.*\n", is_user=False)
                else:
                    self.chat_area.add_message("*Agentic resolver completed but no documentation files were created. This may indicate no suitable dependencies were found or processed.*\n", is_user=False)
            else:
                error_msg = result.get('error', 'Unknown error occurred')
                self.chat_area.add_message(f"⚠️ **Agentic Dependency Resolution Issues**\n\nSome issues occurred during resolution:\n{error_msg}\n\nPlease check the logs for more details.\n", is_user=False)
                
        except Exception as e:
            self.chat_area.add_message(f"❌ **Error in Agentic Resolver**: {str(e)}\n\nThe agentic dependency resolver encountered an error. Please check your configuration and try again.\n", is_user=False)
            self.debug_log.error(f"Error in _handle_agentic_resolver_command: {e}")
            import traceback
            self.debug_log.error(f"Traceback: {traceback.format_exc()}")
    
    async def _handle_setup_command(self) -> None:
        """Handle /setup command - start enhanced 8-step setup wizard with TinyAgent integration."""
        self.chat_area.add_message("**🚀 Enhanced AI-Powered Setup Wizard**\n\nWelcome to the comprehensive juno-agent setup process!\n\nThis AI-powered wizard will help you:\n- Analyze your project structure and dependencies\n- Configure your AI IDE preferences\n- Install MCP servers for enhanced functionality\n- Create comprehensive project documentation (JUNO.md)\n- Set up external context for better AI assistance\n- Configure IDE-specific instruction files\n- Set up Claude permissions\n\n*This setup uses TinyAgent with advanced project analysis capabilities.*\n\nLet's get started!\n", is_user=False)
        
        # Initialize setup components
        await self._initialize_setup_components()
        
        # Define the enhanced 9-step setup process
        self.setup_steps = [
            'collect_project_description',
            'editor_selection', 
            'api_key_setup',
            'ai_project_analysis',
            'install_mcp_servers',
            'fetch_dependency_docs',
            'setup_external_context',
            'create_ide_configs',
            'verification_step',
            'completion_summary'
        ]
        
        # Start setup mode
        self.setup_active = True
        self.setup_step = 0
        self.setup_data = {
            'project_description': None,
            'selected_editor': None,
            'ai_analysis_result': None,
            'detected_dependencies': None,
            'installed_mcp_servers': [],
            'fetched_docs': {},
            'external_context_setup': False,
            'permissions_configured': False,
            'ide_configs_created': False
        }
        
        # Start the first step
        await self._start_enhanced_setup_step()
    
    async def _initialize_setup_components(self) -> None:
        """Initialize all setup components."""
        try:
            # Initialize system status
            if not hasattr(self, 'system_status') or not self.system_status:
                self.system_status = SystemStatus(self.config_manager.workdir)
            
            # Initialize setup components
            self.dependency_scanner = DependencyScanner(self.config_manager.workdir)
            self.external_context_manager = ExternalContextManager(self.config_manager.workdir) 
            self.mcp_installer_enhanced = MCPInstaller(project_dir=Path(self.config_manager.workdir))
            self.claude_permissions_service = ClaudePermissionsService()
            # Initialize AgenticDependencyResolver (replaces old dependency_docs_api)
            from ..agentic_dependency_resolver import AgenticDependencyResolver
            self.agentic_dependency_resolver = AgenticDependencyResolver(
                project_path=str(self.config_manager.workdir),
                config_manager=self.config_manager,
                ui_callback=self._dependency_progress_callback,
                storage_manager=self.storage_manager
            )
            
            # The dependency documentation functionality is now handled by AgenticDependencyResolver
            
            self.chat_area.add_message("✅ Setup components initialized successfully.\n", is_user=False)
            
        except Exception as e:
            self.chat_area.add_message(f"❌ Failed to initialize setup components: {e}\n", is_user=False)
            # Continue with setup anyway, some components might still work
    
    async def _handle_verification_only_command(self) -> None:
        """Handle verification-only mode - run comprehensive verification without setup."""
        self.chat_area.add_message("**🔍 Setup Verification Mode**\n\nRunning comprehensive verification of your current setup...\n\nThis will check:\n- MCP server configuration\n- External context setup\n- IDE configuration files\n- Dependency documentation\n- API key configuration\n- File permissions\n- Project analysis accuracy\n\n*Running verification now...*\n", is_user=False)
        
        try:
            # Run the verification directly
            await self._perform_setup_verification_standalone()
            
        except Exception as e:
            self.chat_area.add_message(f"**❌ Verification Failed**\n\nError: {e}\n\nPlease check your setup and try again.\n", is_user=False)
    
    async def _perform_setup_verification_standalone(self) -> None:
        """Run comprehensive setup verification in standalone mode."""
        try:
            from .setup.setup_verification_service import SetupVerificationService
            import os
            
            # Get project information
            project_root = str(Path(self.config_manager.workdir).resolve())
            project_name = Path(project_root).name
            
            # Initialize verification service
            verification_service = SetupVerificationService(project_root, project_name)
            
            # Run verification
            self.chat_area.add_message("🔄 Running verification checks...\n", is_user=False)
            verification_results = verification_service.verify_all_components()
            
            # Generate report using the verification agent
            report = verification_service.generate_summary_report(verification_results)
            
            # Also run AI verification agent for additional analysis (skip if not available)
            ai_verification_report = None
            try:
                ai_verification_report = await self._run_ai_verification_agent(project_root, project_name, verification_results)
            except Exception as e:
                self.chat_area.add_message(f"ℹ️ AI verification analysis skipped: {str(e)}\n", is_user=False)
            
            # Count status
            status_counts = {"PASS": 0, "FAIL": 0, "WARN": 0, "INFO": 0}
            for result in verification_results:
                status_counts[result.status] += 1
            
            # Determine overall status
            if status_counts["FAIL"] == 0:
                if status_counts["WARN"] == 0:
                    overall_status = "🎉 EXCELLENT"
                    status_msg = "All components passed verification!"
                    final_msg = "**🎉 Setup is Perfect!**\n\nYour development environment is fully configured and ready to use. All components are working correctly."
                else:
                    overall_status = "✅ GOOD"
                    status_msg = f"Functional with {status_counts['WARN']} warnings"
                    final_msg = "**✅ Setup is Good!**\n\nYour setup is functional but there are some minor warnings to address for optimal performance."
            elif status_counts["FAIL"] <= 2:
                overall_status = "⚠️ NEEDS ATTENTION"
                status_msg = f"{status_counts['FAIL']} failures need resolution"
                final_msg = "**⚠️ Setup Needs Attention**\n\nYour setup has some issues that need to be resolved. Please address the failures listed below."
            else:
                overall_status = "❌ CRITICAL ISSUES"
                status_msg = f"{status_counts['FAIL']} critical failures found"
                final_msg = "**❌ Critical Issues Found**\n\nYour setup has significant problems that will impact functionality. Please address the critical failures before proceeding."
            
            # Show verification summary
            summary_message = f"""---

**Setup Verification Complete**

**Overall Status**: {overall_status}
**Message**: {status_msg}

**Component Summary**:
- ✅ Passed: {status_counts["PASS"]}
- ❌ Failed: {status_counts["FAIL"]}
- ⚠️ Warnings: {status_counts["WARN"]}
- ℹ️ Info: {status_counts["INFO"]}

**Success Rate**: {(status_counts["PASS"] / len(verification_results) * 100):.1f}%

---"""
            
            self.chat_area.add_message(summary_message, is_user=False)
            
            # Show detailed errors and warnings if they exist
            await self._display_detailed_verification_results(verification_results, status_counts)
            
            # Show AI verification insights if available
            if ai_verification_report:
                self.chat_area.add_message("**🤖 AI Verification Analysis**\n\n" + ai_verification_report, is_user=False)
            
            # Final message with next steps
            self.chat_area.add_message(final_msg, is_user=False)
            
            if status_counts["FAIL"] > 0 or status_counts["WARN"] > 0:
                next_steps_msg = "\n**📋 Next Steps:**\n"
                if status_counts["FAIL"] > 0:
                    next_steps_msg += "1. **Address Critical Failures**: Focus on FAIL status components first\n"
                    next_steps_msg += "2. **Re-run Setup**: Consider running `juno-cli setup` for failed components\n"
                    next_steps_msg += "3. **Manual Configuration**: Some components may need manual fixes\n"
                if status_counts["WARN"] > 0:
                    next_steps_msg += "4. **Resolve Warnings**: Address warning components for optimal performance\n"
                next_steps_msg += "5. **Re-run Verification**: Use `juno-cli setup --verify-only` after fixing issues\n"
                self.chat_area.add_message(next_steps_msg, is_user=False)
            else:
                self.chat_area.add_message("**🎯 You're Ready to Go!**\n\n✨ Your development environment is properly configured.\n- Start using your AI-powered IDE\n- Test MCP server functionality  \n- Explore external documentation context\n", is_user=False)
            
        except Exception as e:
            self.chat_area.add_message(f"**❌ Verification Error**\n\nFailed to run verification: {e}\n\nThis could indicate setup issues or missing components.\n", is_user=False)
    
    async def _handle_docs_only_command(self) -> None:
        """Handle docs-only mode - fetch documentation for provided/detected dependencies."""
        self.chat_area.add_message("**📚 Documentation Fetching Mode**\n\nFetching documentation for your project dependencies...\n\nThis will:\n- Use previously detected dependencies (if available)\n- Search for dependency documentation\n- Download and organize documentation\n- Create symlinks and external context\n\n*Starting documentation fetching...*\n", is_user=False)
        
        try:
            # Initialize setup components
            await self._initialize_setup_components()
            
            # Check for previously detected dependencies
            config = self.config_manager.load_config()
            previous_scan = getattr(config, 'last_dependency_scan', None)
            
            if not previous_scan or not previous_scan.get('dependencies'):
                self.chat_area.add_message("⚠️ **No Dependencies Found**\n\nNo previously detected dependencies found. Running a quick scan first...\n", is_user=False)
                
                # Run quick dependency scan
                from ..agentic_dependency_resolver import AgenticDependencyResolver
                
                resolver = AgenticDependencyResolver(
                    project_path=str(self.config_manager.workdir),
                    config_manager=self.config_manager,
                    ui_callback=self._dependency_progress_callback,
                    storage_manager=self.storage_manager
                )
                
                scan_result = await resolver.run(dependency_only=True)
                if not scan_result.get('dependencies'):
                    self.chat_area.add_message("**❌ No Dependencies to Process**\n\nNo dependencies were found in your project. Please run dependency scanning first with `juno-cli setup --docs-only` or ensure your project has dependencies configured.\n", is_user=False)
                    return
                
                dependencies = scan_result['dependencies']
            else:
                dependencies = previous_scan['dependencies']
            
            # Proceed with documentation fetching using AgenticDependencyResolver
            from ..agentic_dependency_resolver import AgenticDependencyResolver
            
            resolver = AgenticDependencyResolver(
                project_path=str(self.config_manager.workdir),
                config_manager=self.config_manager,
                ui_callback=self._dependency_progress_callback,
                storage_manager=self.storage_manager
            )
            
            self.chat_area.add_message(f"🔄 Fetching documentation for {len(dependencies)} dependencies...\n", is_user=False)
            
            # Run docs-only mode (fetch docs for provided dependencies)
            dependency_names = [dep['name'] if isinstance(dep, dict) else dep for dep in dependencies]
            result = await resolver.run(docs_only=dependency_names)
            
            # Display results
            documentation_fetched = result.get('documentation_fetched', {})
            if documentation_fetched.get('success'):
                saved_files = documentation_fetched.get('saved_files', [])
                failed_saves = documentation_fetched.get('failed_saves', [])
                
                success_count = len(saved_files)
                failed_count = len(failed_saves)
                
                success_list = "\n".join([f"✅ {file_info['name']}" for file_info in saved_files[:5]])
                if success_count > 5:
                    success_list += f"\n... and {success_count - 5} more"
                
                self.chat_area.add_message(f"**📚 Documentation Fetching Complete**\n\n**Successfully fetched:** {success_count} dependencies\n**Failed:** {failed_count} dependencies\n\n**Recent successes:**\n{success_list}\n\n---", is_user=False)
                
                if failed_saves:
                    failed_list = "\n".join([f"❌ {fail_info['name']}: {fail_info.get('error', 'Unknown error')}" for fail_info in failed_saves[:5]])
                    if failed_count > 5:
                        failed_list += f"\n... and {failed_count - 5} more"
                    self.chat_area.add_message(f"**Failed dependencies:**\n{failed_list}\n", is_user=False)
                
                # Show next steps
                self.chat_area.add_message("**🎯 Documentation Ready!**\n\n✨ Your dependency documentation has been organized and is ready to use.\n- Check the `external_context` directory for downloaded docs\n- Documentation is available through MCP servers\n- AI assistants can now access comprehensive dependency information\n", is_user=False)
            else:
                self.chat_area.add_message("**⚠️ No Documentation Retrieved**\n\nNo documentation could be fetched for the provided dependencies. This could be due to:\n- Network connectivity issues\n- API service limitations\n- Unsupported dependency types\n", is_user=False)
            
        except Exception as e:
            self.chat_area.add_message(f"**❌ Documentation Fetching Failed**\n\nError: {e}\n\nPlease check your configuration and network connection, then try again.\n", is_user=False)
    
    def _dependency_progress_callback(self, message: str, data: Dict[str, Any]) -> None:
        """Callback to receive progress updates from dependency resolver."""
        if self.chat_area:
            self.chat_area.add_message(f"🔄 {message}\n", is_user=False)
    
    async def _start_enhanced_setup_step(self) -> None:
        """Start the current enhanced setup step with progress tracking."""
        if self.setup_step >= len(self.setup_steps):
            # Setup completed
            await self._complete_enhanced_setup()
            return
        
        current_step = self.setup_steps[self.setup_step]
        step_num = self.setup_step + 1
        total_steps = len(self.setup_steps)
        
        # Show progress
        progress_msg = f"**Step {step_num}/{total_steps}**"
        
        if current_step == 'collect_project_description':
            self.chat_area.add_message(f"{progress_msg} **📋 Project Description**\n\nPlease provide a brief description of your project. This helps AI assistants understand your project context better.\n\n*Example: \"A Python web API using FastAPI for managing user data and authentication\"*\n\n(Press Enter to skip if you prefer)", is_user=False)
        
        elif current_step == 'editor_selection':
            self.chat_area.add_message(f"{progress_msg} **📝 AI IDE Selection**\n\nSelect your preferred AI-powered development environment:", is_user=False)
            # Show the EditorSelectorMenu with proper timing
            self.call_after_refresh(self._show_ide_selection_menu)
        
        elif current_step == 'api_key_setup':
            await self._perform_api_key_setup(progress_msg)
        
        elif current_step == 'ai_project_analysis':
            self.chat_area.add_message(f"{progress_msg} **🤖 AI-Powered Project Analysis**\n\nUsing TinyAgent to analyze your project structure, dependencies, and patterns...", is_user=False)
            await self._perform_ai_project_analysis()
        
        elif current_step == 'install_mcp_servers':
            self.chat_area.add_message(f"{progress_msg} **⚙️ Installing MCP Servers**\n\nInstalling VibeContext MCP server for enhanced documentation access...", is_user=False)
            await self._perform_mcp_installation()
        
        elif current_step == 'fetch_dependency_docs':
            self.chat_area.add_message(f"{progress_msg} **📚 Fetching Dependency Documentation**\n\nRetrieving documentation for your project dependencies using AI-powered tools...", is_user=False)
            await self._perform_docs_fetching()
        
        elif current_step == 'setup_external_context':
            self.chat_area.add_message(f"{progress_msg} **📁 Setting Up External Context**\n\nCreating organized documentation structure...", is_user=False)
            await self._perform_external_context_setup()
        
        elif current_step == 'create_ide_configs':
            self.chat_area.add_message(f"{progress_msg} **📝 Creating IDE Configuration Files**\n\nGenerating JUNO.md and updating IDE-specific instruction files...", is_user=False)
            await self._perform_ide_config_creation()
        
        elif current_step == 'verification_step':
            self.chat_area.add_message(f"{progress_msg} **🔍 Setup Verification**\n\nRunning comprehensive verification of all setup components...", is_user=False)
            self._perform_setup_verification()
        
        elif current_step == 'completion_summary':
            self.chat_area.add_message(f"{progress_msg} **🎉 Setup Summary**\n\nGenerating completion summary...", is_user=False)
            await self._show_completion_summary()
    
    async def _handle_setup_input(self, user_input: str) -> None:
        """Handle user input during enhanced setup."""
        if user_input.lower() in ['/cancel', '/quit', '/exit']:
            self.setup_active = False
            self.setup_data = {}
            self.chat_area.add_message("**❌ Setup cancelled.**\n\nYou can restart the setup anytime with `/setup`.", is_user=False)
            return
        
        if not self.setup_active or not hasattr(self, 'setup_steps'):
            return
        
        current_step = self.setup_steps[self.setup_step]
        
        if current_step == 'collect_project_description':
            await self._handle_project_description_input(user_input)
        elif current_step == 'api_key_setup' and self.setup_data.get('api_key_prompt_shown'):
            await self._handle_api_key_input(user_input)
        # Note: editor_selection is handled by the EditorSelectorMenu events
        # Other steps are automated and don't require user input
    
    async def _handle_project_description_input(self, description: str) -> None:
        """Handle project description input from user."""
        try:
            if description.strip():
                self.setup_data['project_description'] = description.strip()
                self.chat_area.add_message(f"✅ Project description saved: {description.strip()}\n", is_user=False)
            else:
                self.setup_data['project_description'] = None
                self.chat_area.add_message("✅ Project description skipped.\n", is_user=False)
            
            # Save to config
            config = self.config_manager.load_config()
            if self.setup_data['project_description']:
                config.project_description = self.setup_data['project_description']
                self.config_manager.save_config(config)
            
            # Move to next step
            self.setup_step += 1
            await self._start_enhanced_setup_step()
            
        except Exception as e:
            self.chat_area.add_message(f"❌ Error saving project description: {e}\n", is_user=False)
            # Continue with setup anyway
            self.setup_step += 1
            await self._start_enhanced_setup_step()
    
    async def _handle_api_key_input(self, user_input: str) -> None:
        """Handle API key input from user during setup."""
        try:
            input_lower = user_input.lower().strip()
            
            if input_lower == 'skip':
                self.chat_area.add_message("✅ Continuing with basic features (no API key configured).\n", is_user=False)
                self.setup_data['has_api_key'] = False
                self.setup_data['api_key_prompt_shown'] = False
                
            elif input_lower == 'learn':
                self.chat_area.add_message(
                    "**Learn More About VibeContext**\n\n"
                    "Visit https://askbudi.com to:\n"
                    "• Sign up for a FREE account\n"
                    "• Get your API key instantly\n"
                    "• Access comprehensive documentation\n"
                    "• Join the developer community\n\n"
                    "VibeContext integrates seamlessly with your workflow and provides intelligent assistance.\n\n"
                    "Please choose an option:\n"
                    "1. Enter 'key:<your_api_key>' to configure\n"
                    "2. Enter 'skip' to continue with basic features\n",
                    is_user=False
                )
                return  # Stay in current step
                
            elif input_lower.startswith('key:'):
                api_key = user_input[4:].strip()
                if not api_key:
                    self.chat_area.add_message("❌ Please provide an API key after 'key:'\n", is_user=False)
                    return
                    
                # Validate and save the API key
                from .setup.api_key_manager import APIKeyManager
                api_key_manager = APIKeyManager(project_dir=Path(self.config_manager.workdir))
                
                self.chat_area.add_message("🔍 Validating API key...\n", is_user=False)
                
                is_valid = await api_key_manager.validate_api_key(api_key)
                
                if is_valid:
                    # Ask where to save (default to global)
                    api_key_manager.save_api_key(api_key, global_save=True)
                    self.chat_area.add_message("✅ API key validated and saved globally! VibeContext features enabled.\n", is_user=False)
                    self.setup_data['has_api_key'] = True
                    self.setup_data['api_key_source'] = 'Global configuration (setup)'
                    self.setup_data['api_key_prompt_shown'] = False
                else:
                    self.chat_area.add_message("❌ Invalid API key. Please check and try again, or enter 'skip' to continue.\n", is_user=False)
                    return  # Stay in current step
                    
            else:
                self.chat_area.add_message(
                    "❌ Invalid option. Please choose:\n"
                    "1. Enter 'key:<your_api_key>' to configure your API key\n"
                    "2. Enter 'skip' to continue with basic features\n"
                    "3. Enter 'learn' for more information\n",
                    is_user=False
                )
                return  # Stay in current step
            
            # Move to next step
            self.setup_step += 1
            await self._start_enhanced_setup_step()
            
        except Exception as e:
            self.chat_area.add_message(f"❌ Error handling API key input: {e}\n\nContinuing with basic features...", is_user=False)
            self.setup_data['has_api_key'] = False
            self.setup_data['api_key_prompt_shown'] = False
            self.setup_step += 1
            await self._start_enhanced_setup_step()
    
    def _show_ide_selection_menu(self) -> None:
        """Show the IDE selection menu with proper timing."""
        try:
            self.ide_selection_menu.show(
                title="AI IDE Preference",
                message="Choose the AI coding environment you use most often:"
            )
        except Exception as e:
            # Fallback: add a message indicating there was an issue
            self.chat_area.add_message(f"⚠️ IDE selection menu failed to load: {e}\n\nPlease manually specify your preferred AI IDE by typing it in the chat.", is_user=False)

    async def _handle_editor_selection(self, editor_name: str) -> None:
        """Handle editor selection from EditorSelectorMenu."""
        try:
            # Special handling for "show_all" - expand the menu to show all IDEs
            if editor_name == "show_all":
                self.chat_area.add_message("📋 **Showing all supported IDEs...**\n", is_user=False)
                
                # Recreate the IDE menu with all IDEs visible
                self.ide_selection_menu.remove()
                self.ide_selection_menu = IDESelectionMenu(show_all_ides=True)
                await self.mount(self.ide_selection_menu)
                
                # Show the expanded menu
                self._show_ide_selection_menu()
                return
            
            # Regular IDE selection handling
            self.setup_data['selected_editor'] = editor_name
            self.chat_area.add_message(f"✅ AI IDE selected: **{editor_name}**\n", is_user=False)
            
            # Save editor selection to .juno_config.json for future detection
            try:
                from .setup.setup_verification_service import SetupVerificationService
                project_name = Path(self.config_manager.workdir).name
                verifier = SetupVerificationService(
                    project_root=Path(self.config_manager.workdir), 
                    project_name=project_name
                )
                if verifier.save_editor_selection(editor_name):
                    debug_logger.log_event("editor_selection_saved", editor=editor_name)
                else:
                    debug_logger.log_event("editor_selection_save_failed", editor=editor_name)
            except Exception as e:
                debug_logger.log_event("editor_selection_save_error", editor=editor_name, error=str(e))
            
            # Save to config
            config = self.config_manager.load_config()
            config.editor = editor_name
            self.config_manager.save_config(config)
            
            # Move to next step
            self.setup_step += 1
            await self._start_enhanced_setup_step()
            
        except Exception as e:
            self.chat_area.add_message(f"❌ Error saving editor selection: {e}\n", is_user=False)
            # Continue with setup anyway
            self.setup_step += 1
            await self._start_enhanced_setup_step()
    
    async def _perform_api_key_setup(self, progress_msg: str) -> None:
        """Handle API key setup for VibeContext enhancement."""
        try:
            # Check if API key is already available
            if hasattr(self, 'mcp_installer_enhanced') and self.mcp_installer_enhanced.should_install_mcp():
                api_key_status = self.mcp_installer_enhanced.get_api_key_status()
                source = api_key_status.get('api_key_source', 'Unknown')
                self.chat_area.add_message(
                    f"{progress_msg} **🔐 API Key Setup**\n\n"
                    f"✅ ASKBUDI API Key found ({source})!\n\n"
                    f"VibeContext enhanced features will be available.\n",
                    is_user=False
                )
                self.setup_data['has_api_key'] = True
                self.setup_data['api_key_source'] = source
            else:
                # Show value proposition and prompt for API key
                from .setup.api_key_manager import APIKeyManager
                api_key_manager = APIKeyManager(project_dir=Path(self.config_manager.workdir))
                
                value_prop = api_key_manager.get_value_proposition_message()
                
                self.chat_area.add_message(
                    f"{progress_msg} **🔐 API Key Setup**\n\n"
                    f"{value_prop}\n\n"
                    f"**Options:**\n"
                    f"1. Enter 'key:<your_api_key>' to configure your API key\n"
                    f"2. Enter 'skip' to continue with basic features\n"
                    f"3. Enter 'learn' for more information\n\n"
                    f"*You can get a free API key at https://askbudi.com/signup*",
                    is_user=False
                )
                
                self.setup_data['has_api_key'] = False
                self.setup_data['api_key_prompt_shown'] = True
                return  # Wait for user input
                
        except Exception as e:
            self.chat_area.add_message(f"⚠️ Error during API key setup: {e}\n\nContinuing with basic features...", is_user=False)
            self.setup_data['has_api_key'] = False
        
        # Move to next step
        self.setup_step += 1
        await self._start_enhanced_setup_step()
    
    async def _perform_ai_project_analysis(self) -> None:
        """Perform comprehensive AI-powered project analysis using TinyAgent with setup system prompt."""
        try:
            if not self.tiny_code_agent:
                self.chat_area.add_message("---\n\n**TinyAgent Unavailable**\n\nUsing basic dependency detection...\n\n---", is_user=False)
                await self._perform_dependency_detection()
                return
            
            # Note: We include setup instructions directly in the analysis request
            # so we don't need to load a separate system prompt
                
            # Create AI analysis message with context
            import platform
            from datetime import datetime
            
            project_path = str(self.config_manager.workdir)
            project_description = self.setup_data.get('project_description', 'No description provided')
            selected_editor = self.setup_data.get('selected_editor', 'Unknown')
            
            # Create comprehensive analysis request that includes the setup instructions
            analysis_request = f"""You are now acting as an intelligent project setup assistant for juno-cli. Please perform a comprehensive setup analysis for this project using the following guidelines:

**Project Context:**
- Project Path: {project_path}
- Project Description: {project_description}  
- Selected Editor: {selected_editor}
- Platform: {platform.system()} ({platform.machine()})
- Date: {datetime.now().strftime('%Y-%m-%d')}

**Your Task:**
Please execute a comprehensive 8-step project analysis:

### Step 1: Project Analysis & IDE Detection
- Scan for existing IDE configuration files (CLAUDE.md, .cursor/, WINDSURF.md, etc.)
- Read and analyze existing configurations
- Identify project type, frameworks, and architecture
- Create comprehensive project summary

### Step 2: Dependency Extraction & Analysis  
- Scan package files systematically (requirements.txt, package.json, go.mod, Cargo.toml, etc.)
- Extract dependency names and version constraints
- Identify major versions (e.g., "fastapi>=0.68.0" → "fastapi v0.x")
- Prioritize core/framework dependencies over utilities

### Step 3-8: Planning Analysis
- Plan MCP server configuration
- Plan external documentation setup
- Plan IDE configuration enhancement  
- Plan JUNO.md creation
- Plan Claude permissions (if applicable)
- Provide validation summary

**Focus Areas:**
- Analyzing the project structure and identifying frameworks/patterns
- Extracting dependencies and their versions accurately
- Creating a comprehensive project analysis for IDE configuration files
- Understanding project architecture and development patterns

**Tools Available:**
You have access to file operations, shell commands, and project analysis tools. Please use them to thoroughly analyze this project.

Please provide detailed results for each step, focusing especially on dependency extraction and project structure analysis."""
            
            # Use the TinyCodeAgentChat interface to process the analysis request
            ai_response = await self.tiny_code_agent.process_chat_message(analysis_request)
            
            # Store the analysis result
            self.setup_data['ai_analysis_result'] = ai_response
            
            # Extract dependency information if available
            detected_deps = self._extract_dependencies_from_ai_response(ai_response)
            self.setup_data['detected_dependencies'] = detected_deps
            
            # Show consolidated results
            self.chat_area.add_message(f"---\n\n**AI Project Analysis Complete**\n\n**Project Type**: {detected_deps.get('project_type', 'Unknown')}\n**Dependencies**: {len(detected_deps.get('dependencies', []))}\n**Language**: {detected_deps.get('language', 'Unknown')}\n\n---", is_user=False)
            
            # Move to next step
            self.setup_step += 1
            await self._start_enhanced_setup_step()
            
        except Exception as e:
            self.chat_area.add_message(f"---\n\n**AI Project Analysis Failed**\n\nError: {e}\n\nUsing basic dependency detection...\n\n---", is_user=False)
            await self._perform_dependency_detection()

    async def _perform_dependency_detection(self) -> None:
        """Perform dependency detection using DependencyScanner (fallback method)."""
        try:
            # Scan for dependencies
            scan_result = self.dependency_scanner.scan_project_dependencies()
            self.setup_data['detected_dependencies'] = scan_result
            
            # Show consolidated results
            if scan_result['dependencies']:
                summary = self.dependency_scanner.get_dependency_summary()
                self.chat_area.add_message(f"---\n\n**Dependency Detection Complete**\n\n{summary}\n\n---", is_user=False)
            else:
                self.chat_area.add_message("---\n\n**Dependency Detection Complete**\n\nNo dependencies found.\n\n---", is_user=False)
            
            # Move to next step
            self.setup_step += 1
            await self._start_enhanced_setup_step()
            
        except Exception as e:
            self.chat_area.add_message(f"---\n\n**Dependency Detection Failed**\n\nError: {e}\n\n---", is_user=False)
            self.setup_data['detected_dependencies'] = {'dependencies': [], 'language': 'Unknown', 'package_files': []}
            self.setup_step += 1
            await self._start_enhanced_setup_step()
    
    async def _perform_mcp_installation(self) -> None:
        """Perform MCP server installation."""
        try:
            selected_editor = self.setup_data.get('selected_editor', 'Claude Code')
            
            # Map editor names to identifiers
            editor_mapping = {
                'Claude Code': 'claude_code',
                'Cursor': 'cursor', 
                'Windsurf': 'windsurf',
                'VS Code': 'vscode',
                'VSCode': 'vscode'
            }
            
            editor_id = editor_mapping.get(selected_editor, 'claude_code')
            
            # Get API key if available
            api_key = ""
            if self.config_manager.has_api_key():
                try:
                    api_key = self.config_manager.get_api_key()
                except:
                    api_key = ""
            
            if not api_key:
                # Try to use the global function instead
                from .setup import install_vibe_context_for_editor
                success = install_vibe_context_for_editor(editor_id, Path(self.config_manager.workdir), "")
            else:
                # Install VibeContext MCP server for the selected editor
                success = self.mcp_installer_enhanced.install_mcp_servers(editor_id, Path(self.config_manager.workdir), api_key)
            
            if success:
                self.setup_data['installed_mcp_servers'].append('vibe_context')
                self.chat_area.add_message(f"---\n\n**MCP Installation Complete**\n\nVibeContext MCP server configured for {selected_editor}.\n\n---", is_user=False)
            else:
                self.chat_area.add_message(f"---\n\n**MCP Installation Issues**\n\nVibeContext MCP server setup encountered problems for {selected_editor}.\n\n---", is_user=False)
            
            # Move to next step
            self.setup_step += 1
            await self._start_enhanced_setup_step()
            
        except Exception as e:
            self.setup_data['installed_mcp_servers'] = []
            self.chat_area.add_message(f"---\n\n**MCP Installation Failed**\n\nError: {e}\n\nSetup will continue, but MCP functionality may not be available.\n\n---", is_user=False)
            self.setup_step += 1
            await self._start_enhanced_setup_step()
    
    async def _perform_docs_fetching(self) -> None:
        """Perform dependency documentation fetching using AgenticDependencyResolver."""
        try:
            detected_deps = self.setup_data.get('detected_dependencies', {})
            dependencies = detected_deps.get('dependencies', [])
            language = detected_deps.get('language', 'Unknown')
            
            if dependencies and language != 'Unknown':
                # Use AgenticDependencyResolver for documentation fetching
                from ..agentic_dependency_resolver import AgenticDependencyResolver
                
                resolver = AgenticDependencyResolver(
                    project_path=str(self.config_manager.workdir),
                    config_manager=self.config_manager,
                    ui_callback=self._dependency_progress_callback,
                    storage_manager=self.storage_manager
                )
                
                # Convert dependencies to names list for docs_only mode
                dependency_names = [dep['name'] if isinstance(dep, dict) else dep for dep in dependencies]
                
                self.chat_area.add_message(f"🔄 Using AgenticDependencyResolver to fetch documentation for {len(dependency_names)} dependencies...\n", is_user=False)
                
                # Fetch documentation using the agentic resolver
                docs_result = await resolver.run(docs_only=dependency_names)
                
                # Convert result format to match existing setup data structure
                if docs_result.get('success'):
                    documentation_fetched = docs_result.get('documentation_fetched', {})
                    saved_files = documentation_fetched.get('saved_files', [])
                    failed_saves = documentation_fetched.get('failed_saves', [])
                    
                    fetched_docs = {
                        'docs': {},
                        'successful': [file_info['name'] for file_info in saved_files],
                        'failed': [fail_info['name'] for fail_info in failed_saves]
                    }
                    
                    # Add documentation content if available
                    for file_info in saved_files:
                        dep_name = file_info['name']
                        fetched_docs['docs'][dep_name] = {
                            'sections': {'overview': f'Documentation fetched for {dep_name}'},
                            'metadata': {
                                'fetched_via': 'AgenticDependencyResolver',
                                'file_path': file_info['path'],
                                'file_size': file_info['size']
                            }
                        }
                    
                    self.setup_data['fetched_docs'] = fetched_docs
                    
                    success_count = len(fetched_docs['successful'])
                    failed_count = len(fetched_docs['failed'])
                    
                    # Create summary message
                    summary = f"**AgenticDependencyResolver Results:**\n"
                    summary += f"- Successfully fetched: {success_count} dependencies\n"
                    summary += f"- Failed to fetch: {failed_count} dependencies\n"
                    
                    if fetched_docs['successful']:
                        summary += f"\n**Successful:**\n"
                        for dep in fetched_docs['successful'][:5]:  # Show first 5
                            summary += f"✅ {dep}\n"
                        if success_count > 5:
                            summary += f"... and {success_count - 5} more\n"
                    
                    if fetched_docs['failed']:
                        summary += f"\n**Failed:**\n"
                        for dep in fetched_docs['failed'][:3]:  # Show first 3 failures
                            summary += f"❌ {dep}\n"
                        if failed_count > 3:
                            summary += f"... and {failed_count - 3} more\n"
                    
                    self.chat_area.add_message(f"---\n\n**Documentation Fetching Complete**\n\n{summary}\n\n---", is_user=False)
                else:
                    # Handle failure case
                    error_msg = docs_result.get('error', 'Unknown error occurred')
                    self.setup_data['fetched_docs'] = {'docs': {}, 'successful': [], 'failed': dependency_names}
                    self.chat_area.add_message(f"---\n\n**Documentation Fetching Failed**\n\nAgenticDependencyResolver error: {error_msg}\n\n---", is_user=False)
            else:
                self.setup_data['fetched_docs'] = {'docs': {}, 'successful': [], 'failed': []}
                self.chat_area.add_message("---\n\n**Documentation Fetching Complete**\n\nNo dependencies found to fetch documentation for.\n\n---", is_user=False)
            
            # Move to next step
            self.setup_step += 1
            await self._start_enhanced_setup_step()
            
        except Exception as e:
            self.chat_area.add_message(f"---\n\n**Documentation Fetching Failed**\n\nAgenticDependencyResolver error: {e}\n\n---", is_user=False)
            self.setup_data['fetched_docs'] = {'docs': {}, 'successful': [], 'failed': []}
            self.setup_step += 1
            await self._start_enhanced_setup_step()
    
    async def _perform_external_context_setup(self) -> None:
        """Perform external context setup."""
        try:
            # Initialize external context structure
            success = self.external_context_manager.initialize_context_structure()
            
            if success:
                # Add fetched documentation to external context
                fetched_docs = self.setup_data.get('fetched_docs', {}).get('docs', {})
                docs_added = 0
                
                for dep_name, doc_data in fetched_docs.items():
                    if doc_data and doc_data.get('sections'):
                        # Add overview documentation
                        overview = doc_data['sections'].get('overview', f'Documentation for {dep_name}')
                        if self.external_context_manager.add_dependency_documentation(dep_name, overview, 'general'):
                            docs_added += 1
                
                # Add project description if available
                project_desc = self.setup_data.get('project_description')
                if project_desc:
                    self.external_context_manager.add_project_documentation(
                        'project_description', 
                        f"# Project Description\n\n{project_desc}",
                        'md'
                    )
                
                self.setup_data['external_context_setup'] = True
                
                self.chat_area.add_message(f"---\n\n**External Context Setup Complete**\n\n**Documentation**: {docs_added} dependency docs added\n**Location**: `external_context/`\n\n---", is_user=False)
            else:
                self.chat_area.add_message("---\n\n**External Context Setup Issues**\n\nBasic structure created with limited content.\n\n---", is_user=False)
                self.setup_data['external_context_setup'] = False
            
            # Move to next step
            self.setup_step += 1
            await self._start_enhanced_setup_step()
            
        except Exception as e:
            self.chat_area.add_message(f"---\n\n**External Context Setup Failed**\n\nError: {e}\n\n---", is_user=False)
            self.setup_data['external_context_setup'] = False
            self.setup_step += 1
            await self._start_enhanced_setup_step()
    
    async def _perform_permissions_configuration(self) -> None:
        """Perform Claude permissions configuration."""
        try:
            # Setup Claude permissions for external context
            success = self.claude_permissions_service.setup_claude_permissions(Path(self.config_manager.workdir))
            
            if success:
                self.setup_data['permissions_configured'] = True
                self.chat_area.add_message("---\n\n**Claude Permissions Configured**\n\nClaude Code access configured for external_context directory.\n\n---", is_user=False)
            else:
                self.setup_data['permissions_configured'] = False
                self.chat_area.add_message("---\n\n**Claude Permissions Setup Issues**\n\nCheck `.claude/settings.json` for manual configuration.\n\n---", is_user=False)
            
            # Move to next step
            self.setup_step += 1
            await self._start_enhanced_setup_step()
            
        except Exception as e:
            self.chat_area.add_message(f"---\n\n**Claude Permissions Setup Failed**\n\nError: {e}\n\n---", is_user=False)
            self.setup_data['permissions_configured'] = False
            self.setup_step += 1
            await self._start_enhanced_setup_step()
    
    async def _perform_ide_config_creation(self) -> None:
        """Create comprehensive IDE configuration files including JUNO.md."""
        try:
            selected_editor = self.setup_data.get('selected_editor', 'Unknown')
            ai_analysis = self.setup_data.get('ai_analysis_result', '')
            detected_deps = self.setup_data.get('detected_dependencies', {})
            fetched_docs = self.setup_data.get('fetched_docs', {})
            
            # Create JUNO.md - comprehensive guide for all AI assistants
            juno_md_path = Path(self.config_manager.workdir) / "JUNO.md"
            juno_content = self._generate_juno_md_content(ai_analysis, detected_deps, fetched_docs)
            
            with open(juno_md_path, 'w', encoding='utf-8') as f:
                f.write(juno_content)
            
            configs_created = ["JUNO.md"]
            
            # Update/create IDE-specific configuration file
            ide_config_created = False
            if selected_editor.lower() in ['claude_code', 'claude code']:
                # Claude Code gets its own specific CLAUDE.md file
                ide_config_created = await self._update_claude_md(ai_analysis, detected_deps, fetched_docs)
                if ide_config_created:
                    configs_created.append("CLAUDE.md")
            elif selected_editor.lower() == 'windsurf':
                # Windsurf gets its own specific WINDSURF.md file
                ide_config_created = await self._update_windsurf_md(ai_analysis, detected_deps, fetched_docs)
                if ide_config_created:
                    configs_created.append("WINDSURF.md")
            else:
                # All other IDEs (including Cursor) use AGENTS.md as default
                ide_config_created = await self._update_agents_md(selected_editor, ai_analysis, detected_deps, fetched_docs)
                if ide_config_created:
                    configs_created.append("AGENTS.md")
            
            self.setup_data['ide_configs_created'] = True
            
            # Show consolidated results
            configs_list = ", ".join(configs_created)
            self.chat_area.add_message(f"---\n\n**IDE Configuration Files Created**\n\n**Files**: {configs_list}\n**Editor**: {selected_editor}\n\n---", is_user=False)
            
            # Move to next step
            self.setup_step += 1
            await self._start_enhanced_setup_step()
            
        except Exception as e:
            self.chat_area.add_message(f"---\n\n**IDE Configuration Creation Failed**\n\nError: {e}\n\n---", is_user=False)
            self.setup_data['ide_configs_created'] = False
            self.setup_step += 1
            await self._start_enhanced_setup_step()
    
    @work(exclusive=False)
    async def _perform_setup_verification(self) -> None:
        """Run comprehensive setup verification using dedicated verification agent."""
        try:
            from .setup.setup_verification_service import SetupVerificationService
            import os
            
            # Get project information
            project_root = str(Path(self.config_manager.workdir).resolve())
            project_name = Path(project_root).name
            
            # Initialize verification service
            verification_service = SetupVerificationService(project_root, project_name)
            
            # Run verification
            verification_results = verification_service.verify_all_components()
            
            # Generate report using the verification agent
            report = verification_service.generate_summary_report(verification_results)
            
            # Also run AI verification agent for additional analysis
            ai_verification_report = await self._run_ai_verification_agent(project_root, project_name, verification_results)
            
            # Store results
            self.setup_data['verification_results'] = verification_results
            self.setup_data['verification_report'] = report
            self.setup_data['ai_verification'] = ai_verification_report
            
            # Count status
            status_counts = {"PASS": 0, "FAIL": 0, "WARN": 0, "INFO": 0}
            for result in verification_results:
                status_counts[result.status] += 1
            
            # Determine overall status
            if status_counts["FAIL"] == 0:
                if status_counts["WARN"] == 0:
                    overall_status = "🎉 EXCELLENT"
                    status_msg = "All components passed verification!"
                else:
                    overall_status = "✅ GOOD"
                    status_msg = f"Functional with {status_counts['WARN']} warnings"
            elif status_counts["FAIL"] <= 2:
                overall_status = "⚠️ NEEDS ATTENTION"
                status_msg = f"{status_counts['FAIL']} failures need resolution"
            else:
                overall_status = "❌ CRITICAL ISSUES"
                status_msg = f"{status_counts['FAIL']} critical failures found"
            
            # Show verification summary
            summary_message = f"""---

**Setup Verification Complete**

**Overall Status**: {overall_status}
**Message**: {status_msg}

**Component Summary**:
- ✅ Passed: {status_counts["PASS"]}
- ❌ Failed: {status_counts["FAIL"]}
- ⚠️ Warnings: {status_counts["WARN"]}
- ℹ️ Info: {status_counts["INFO"]}

**Success Rate**: {(status_counts["PASS"] / len(verification_results) * 100):.1f}%

---"""
            
            self.chat_area.add_message(summary_message, is_user=False)
            
            # Show detailed errors and warnings if they exist
            await self._display_detailed_verification_results(verification_results, status_counts)
            
            # Show AI verification insights if available
            if ai_verification_report:
                self.chat_area.add_message("**🤖 AI Verification Analysis**\n\n" + ai_verification_report, is_user=False)
            
            # Move to next step
            self.setup_step += 1
            await self._start_enhanced_setup_step()
            
        except Exception as e:
            self.chat_area.add_message(f"---\n\n**Setup Verification Failed**\n\nError: {e}\n\nProceeding to completion...\n\n---", is_user=False)
            self.setup_data['verification_failed'] = True
            self.setup_step += 1
            await self._start_enhanced_setup_step()
    
    async def _display_detailed_verification_results(self, verification_results, status_counts) -> None:
        """Display detailed breakdown of errors and warnings with actionable recommendations."""
        
        # Show critical failures first
        failed_results = [r for r in verification_results if r.status == "FAIL"]
        if failed_results:
            fail_details = "**❌ CRITICAL FAILURES** *(Must be fixed)*\n\n"
            
            for i, result in enumerate(failed_results, 1):
                fail_details += f"**{i}. {result.component}**\n"
                fail_details += f"   • **Issue**: {result.message}\n"
                
                # Add details if available
                if result.details:
                    detail_items = []
                    for key, value in result.details.items():
                        if isinstance(value, list):
                            detail_items.append(f"{key}: {', '.join(map(str, value))}")
                        else:
                            detail_items.append(f"{key}: {value}")
                    if detail_items:
                        fail_details += f"   • **Details**: {'; '.join(detail_items)}\n"
                
                # Add recommendations
                if result.recommendations:
                    fail_details += "   • **Fix Actions**:\n"
                    for rec in result.recommendations:
                        fail_details += f"     - {rec}\n"
                
                fail_details += "\n"
            
            self.chat_area.add_message(fail_details.rstrip(), is_user=False)
        
        # Show warnings next
        warn_results = [r for r in verification_results if r.status == "WARN"]
        if warn_results:
            warn_details = "**⚠️ WARNINGS** *(Should be addressed)*\n\n"
            
            for i, result in enumerate(warn_results, 1):
                warn_details += f"**{i}. {result.component}**\n"
                warn_details += f"   • **Issue**: {result.message}\n"
                
                # Add details if available
                if result.details:
                    detail_items = []
                    for key, value in result.details.items():
                        if isinstance(value, list):
                            detail_items.append(f"{key}: {', '.join(map(str, value))}")
                        else:
                            detail_items.append(f"{key}: {value}")
                    if detail_items:
                        warn_details += f"   • **Details**: {'; '.join(detail_items)}\n"
                
                # Add recommendations
                if result.recommendations:
                    warn_details += "   • **Improvement Actions**:\n"
                    for rec in result.recommendations:
                        warn_details += f"     - {rec}\n"
                
                warn_details += "\n"
            
            self.chat_area.add_message(warn_details.rstrip(), is_user=False)
        
        # Show successful components summary if there are failures/warnings
        if status_counts["FAIL"] > 0 or status_counts["WARN"] > 0:
            passed_results = [r for r in verification_results if r.status == "PASS"]
            if passed_results:
                success_details = f"**✅ WORKING COMPONENTS** *({len(passed_results)} components)*\n\n"
                
                component_names = [result.component for result in passed_results]
                # Group by similar names to make it more readable
                success_details += "✓ " + "\n✓ ".join(component_names)
                success_details += "\n"
                
                self.chat_area.add_message(success_details, is_user=False)
        
        # Show actionable next steps
        if status_counts["FAIL"] > 0 or status_counts["WARN"] > 0:
            next_steps = "**🎯 RECOMMENDED NEXT STEPS**\n\n"
            
            if status_counts["FAIL"] > 0:
                next_steps += "**Priority 1: Address Critical Failures**\n"
                next_steps += "• Fix the failures listed above - these will prevent proper functionality\n"
                next_steps += "• Re-run the setup wizard for failed components if needed\n"
                next_steps += "• Test each fix by running verification again\n\n"
            
            if status_counts["WARN"] > 0:
                priority = "Priority 2" if status_counts["FAIL"] > 0 else "Priority 1"
                next_steps += f"**{priority}: Resolve Warnings**\n"
                next_steps += "• Address warnings to improve setup quality and prevent future issues\n"
                next_steps += "• These won't block functionality but may cause problems later\n\n"
            
            next_steps += "**Final Step: Re-run Verification**\n"
            next_steps += "• After making changes, run setup verification again to confirm fixes\n"
            next_steps += "• Use command: `py-wizard setup --verify-only` (if available)\n"
            
            self.chat_area.add_message(next_steps, is_user=False)
        else:
            # Everything passed - show success message
            success_msg = "**🎉 PERFECT SETUP!**\n\n"
            success_msg += "All components verified successfully. Your development environment is ready:\n\n"
            success_msg += "• **MCP Server**: Configured and accessible\n"
            success_msg += "• **External Context**: Documentation properly organized\n"
            success_msg += "• **IDE Configuration**: Files created and populated\n"
            success_msg += "• **Dependencies**: All requirements documented\n\n"
            success_msg += "**You can now start using your AI-powered development environment!**"
            
            self.chat_area.add_message(success_msg, is_user=False)

    async def _run_ai_verification_agent(self, project_root: str, project_name: str, verification_results) -> str:
        """Run AI verification agent with dedicated system prompt."""
        try:
            # Load verification system prompt
            verification_prompt = self._load_verification_system_prompt()
            
            if not verification_prompt:
                return "AI verification unavailable (prompt not found)"
            
            # Prepare context for AI agent
            context = f"""Project Root: {project_root}
Project Name: {project_name}

Verification Results Summary:
"""
            
            for result in verification_results:
                context += f"\n- {result.status}: {result.component} - {result.message}"
                if result.details:
                    context += f"\n  Details: {result.details}"
                if result.recommendations:
                    context += f"\n  Recommendations: {', '.join(result.recommendations)}"
            
            # Create a mini verification session with TinyAgent
            user_prompt = f"""Please verify the setup completion for this project. Focus on:

1. Analyzing the verification results provided
2. Testing any additional aspects that automated checks might miss
3. Providing honest assessment of setup quality
4. Recommending next steps

Context:
{context}"""

            # Use TinyAgent with verification prompt
            # Create a temporary config manager for verification
            from ..config import ConfigManager
            temp_config = ConfigManager(project_root)
            
            tiny_agent = TinyCodeAgentChat(
                config_manager=temp_config,
                debug=False,
                enable_custom_instructions=False  # Disable custom instructions for setup agents
            )
            
            # Set the system prompt manually
            if hasattr(tiny_agent, 'agent') and hasattr(tiny_agent.agent, 'system_prompt'):
                tiny_agent.agent.system_prompt = verification_prompt
            
            # Run verification analysis
            response = await tiny_agent.process_chat_message(user_prompt)
            
            return response
            
        except Exception as e:
            return f"AI verification error: {str(e)}"
    
    def _load_verification_system_prompt(self) -> str:
        """Load the verification system prompt from prompt_garden.yaml."""
        try:
            import yaml
            from pathlib import Path
            
            # Path to prompt_garden.yaml
            prompt_file = Path(__file__).parent.parent / "prompts" / "prompt_garden.yaml"
            
            if not prompt_file.exists():
                return ""
            
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompts_data = yaml.safe_load(f)
            
            verification_prompt_data = prompts_data.get('prompts', {}).get('setup_verification', {})
            verification_prompt = verification_prompt_data.get('prompt', '')
            
            # Substitute system variables
            import platform
            from datetime import datetime
            
            substitutions = {
                'PLATFORM': platform.system(),
                'ARCHITECTURE': platform.machine(),
                'CURRENT_DATE': datetime.now().strftime('%Y-%m-%d'),
                'WORKING_DIRECTORY': self.config_manager.workdir
            }
            
            for key, value in substitutions.items():
                verification_prompt = verification_prompt.replace(f'${{{key}}}', str(value))
            
            return verification_prompt
            
        except Exception as e:
            print(f"Error loading verification prompt: {e}")
            return ""

    def _load_setup_system_prompt(self) -> str:
        """Load the setup system prompt from prompt_garden.yaml."""
        try:
            import yaml
            from pathlib import Path
            
            # Path to prompt_garden.yaml
            prompt_file = Path(__file__).parent.parent / "prompts" / "prompt_garden.yaml"
            
            if not prompt_file.exists():
                return ""
            
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompts_data = yaml.safe_load(f)
            
            setup_prompt_data = prompts_data.get('prompts', {}).get('setup_command', {})
            setup_prompt = setup_prompt_data.get('prompt', '')
            
            # Substitute system variables
            import platform
            from datetime import datetime
            
            setup_prompt = setup_prompt.replace('${PLATFORM}', platform.system())
            setup_prompt = setup_prompt.replace('${ARCHITECTURE}', platform.machine())
            setup_prompt = setup_prompt.replace('${CURRENT_DATE}', datetime.now().strftime('%Y-%m-%d'))
            setup_prompt = setup_prompt.replace('${WORKING_DIRECTORY}', str(self.config_manager.workdir))
            
            return setup_prompt
            
        except Exception as e:
            logger.error(f"Failed to load setup system prompt: {e}")
            return ""
    
    def _extract_dependencies_from_ai_response(self, ai_response: str) -> Dict[str, Any]:
        """Extract dependency information from AI analysis response."""
        try:
            # This is a simple extraction - in practice, you might want more sophisticated parsing
            dependencies = []
            language = "Unknown"
            project_type = "Unknown"
            package_files = []
            
            # Look for common patterns in the AI response
            response_lower = ai_response.lower()
            
            # Extract language
            if 'python' in response_lower:
                language = "python"
            elif 'javascript' in response_lower or 'node.js' in response_lower:
                language = "javascript"
            elif 'typescript' in response_lower:
                language = "typescript"
            elif 'go' in response_lower and 'golang' in response_lower:
                language = "go"
            elif 'rust' in response_lower:
                language = "rust"
            elif 'java' in response_lower:
                language = "java"
            
            # Extract project type
            if 'fastapi' in response_lower or 'flask' in response_lower or 'django' in response_lower:
                project_type = "Python Web API"
            elif 'react' in response_lower:
                project_type = "React Application"
            elif 'express' in response_lower:
                project_type = "Node.js API"
            elif 'cli' in response_lower or 'command' in response_lower:
                project_type = "CLI Application"
            elif 'web' in response_lower:
                project_type = "Web Application"
            
            # Try to use actual dependency scanner as fallback
            if hasattr(self, 'dependency_scanner'):
                scanner_result = self.dependency_scanner.scan_project_dependencies()
                if scanner_result.get('dependencies'):
                    dependencies = scanner_result['dependencies']
                    if scanner_result.get('language') != 'Unknown':
                        language = scanner_result['language']
                    package_files = scanner_result.get('package_files', [])
            
            return {
                'dependencies': dependencies,
                'language': language,
                'project_type': project_type,
                'package_files': package_files,
                'ai_analysis_available': True
            }
            
        except Exception as e:
            logger.error(f"Failed to extract dependencies from AI response: {e}")
            # Return empty structure
            return {
                'dependencies': [],
                'language': 'Unknown',
                'project_type': 'Unknown',
                'package_files': [],
                'ai_analysis_available': False
            }
    
    def _generate_juno_md_content(self, ai_analysis: str, detected_deps: Dict, fetched_docs: Dict) -> str:
        """Generate comprehensive JUNO.md content."""
        from datetime import datetime
        import platform
        
        project_name = Path(self.config_manager.workdir).name
        project_desc = self.setup_data.get('project_description', 'No description provided')
        selected_editor = self.setup_data.get('selected_editor', 'Unknown')
        
        content = f"""# JUNO Development Guide - {project_name}

## Project Overview
This is a comprehensive development guide generated by juno-agent to help AI assistants understand and work effectively with this project.

### Basic Information
- **Project Path**: `{self.config_manager.workdir}`
- **Project Type**: {detected_deps.get('project_type', 'Unknown')}
- **Primary Language**: {detected_deps.get('language', 'Unknown')}
- **Setup Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Platform**: {platform.system()} ({platform.machine()})
- **Selected AI IDE**: {selected_editor}

### Project Description
{project_desc}

## Architecture & Dependencies

### Detected Dependencies
"""
        
        dependencies = detected_deps.get('dependencies', [])
        if dependencies:
            content += "The following dependencies were detected in this project:\n\n"
            for dep in dependencies[:15]:  # Limit to first 15
                content += f"- `{dep}`\n"
            if len(dependencies) > 15:
                content += f"- ... and {len(dependencies) - 15} more dependencies\n"
        else:
            content += "No dependencies were automatically detected.\n"
        
        content += f"""
### Package Files
"""
        
        package_files = detected_deps.get('package_files', [])
        if package_files:
            for pfile in package_files:
                content += f"- `{pfile}`\n"
        else:
            content += "- No package files detected\n"
        
        content += """
## AI Analysis Results

"""
        
        if ai_analysis and detected_deps.get('ai_analysis_available'):
            # Include a summary of the AI analysis (truncated for readability)
            analysis_summary = ai_analysis[:1000] + "..." if len(ai_analysis) > 1000 else ai_analysis
            content += f"The following insights were generated by AI analysis:\n\n```\n{analysis_summary}\n```\n\n"
        else:
            content += "AI analysis was not available during setup.\n\n"
        
        content += """## External Documentation Context

The `external_context/` directory contains up-to-date documentation for project dependencies:

"""
        
        # Add external documentation information
        saved_files = fetched_docs.get('saved_files', [])
        if saved_files:
            for file_info in saved_files:
                dep_name = file_info.get('dependency', 'unknown')
                filename = file_info.get('filename', f"{dep_name}.md")
                content += f"- **{dep_name}**: `external_context/{filename}`\n"
        else:
            content += "- No external documentation was fetched during setup\n"
        
        content += f"""

## Development Workflows

### Recommended Development Process
1. **Analysis First**: Use AI tools to understand code structure before making changes
2. **Reference Documentation**: Check external_context/ for dependency docs
3. **Test-Driven Development**: Write tests before implementing features
4. **AI-Assisted Development**: Leverage {selected_editor} for intelligent code assistance

### AI Assistant Integration
- **Primary IDE**: {selected_editor} configured for this project
- **MCP Tools Available**: VibeContext server with documentation access
- **Preferred Documentation**: Use external_context/ over general knowledge
- **Project Context**: This JUNO.md file provides comprehensive project context

## Best Practices

### Code Development
- Follow {detected_deps.get('language', 'language')}-specific conventions
- Use dependency documentation from external_context/
- Leverage AI IDE features for code completion and analysis
- Test changes thoroughly before committing

### AI Collaboration
- Provide context about your specific task when asking for help
- Reference relevant documentation from external_context/
- Use project-specific terminology and patterns
- Validate AI-generated code against project requirements

## Troubleshooting & Maintenance

### Common Issues
1. **Dependencies**: Check package files and external_context/ for version info
2. **AI IDE Issues**: Verify MCP server configuration and API keys
3. **Documentation**: Re-run juno-agent setup to refresh external context

### Maintenance Tasks
- Update external documentation regularly with `/setup`
- Review and update this JUNO.md when project structure changes
- Keep AI IDE configurations synchronized across team members

---
*This guide was generated by juno-agent v1.0.0 on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*For updates, run `juno setup` or `juno-agent setup` in this directory*
"""
        
        return content
    
    async def _update_claude_md(self, ai_analysis: str, detected_deps: Dict, fetched_docs: Dict) -> bool:
        """Update CLAUDE.md with project-specific information."""
        try:
            claude_md_path = Path(self.config_manager.workdir) / "CLAUDE.md"
            
            # Read existing CLAUDE.md if it exists
            existing_content = ""
            if claude_md_path.exists():
                with open(claude_md_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            
            # Generate enhanced content
            enhanced_content = self._generate_ide_config_content("Claude Code", ai_analysis, detected_deps, fetched_docs)
            
            # If existing content exists, try to merge intelligently
            if existing_content and "## Project Information" not in existing_content:
                # Prepend project information to existing content
                final_content = enhanced_content + "\n\n" + existing_content
            else:
                final_content = enhanced_content
            
            # Write the enhanced file
            with open(claude_md_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update CLAUDE.md: {e}")
            return False
    
    async def _update_agents_md(self, selected_editor: str, ai_analysis: str, detected_deps: Dict, fetched_docs: Dict) -> bool:
        """Update AGENTS.md with project-specific information for the selected IDE."""
        try:
            agents_md_path = Path(self.config_manager.workdir) / "AGENTS.md"
            
            # Read existing AGENTS.md if it exists
            existing_content = ""
            if agents_md_path.exists():
                with open(agents_md_path, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            
            # Generate enhanced content for the IDE
            enhanced_content = self._generate_ide_config_content(selected_editor, ai_analysis, detected_deps, fetched_docs)
            
            # If existing content exists and doesn't contain our project section, merge intelligently
            if existing_content and "## Project Information" not in existing_content:
                # Prepend project information to existing content
                final_content = enhanced_content + "\n\n---\n\n" + existing_content
            else:
                final_content = enhanced_content
            
            # Write the enhanced file
            with open(agents_md_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update AGENTS.md: {e}")
            return False
    
    async def _update_windsurf_md(self, ai_analysis: str, detected_deps: Dict, fetched_docs: Dict) -> bool:
        """Update WINDSURF.md with project-specific information."""
        try:
            windsurf_md_path = Path(self.config_manager.workdir) / "WINDSURF.md"
            enhanced_content = self._generate_ide_config_content("Windsurf", ai_analysis, detected_deps, fetched_docs)
            
            with open(windsurf_md_path, 'w', encoding='utf-8') as f:
                f.write(enhanced_content)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update WINDSURF.md: {e}")
            return False
    
    def _generate_ide_config_content(self, ide_name: str, ai_analysis: str, detected_deps: Dict, fetched_docs: Dict) -> str:
        """Generate IDE-specific configuration file content."""
        from datetime import datetime
        
        project_name = Path(self.config_manager.workdir).name
        project_desc = self.setup_data.get('project_description', 'No description provided')
        
        content = f"""# {ide_name} Configuration for {project_name}

## Project Information
- **Project Type**: {detected_deps.get('project_type', 'Unknown')}
- **Primary Language**: {detected_deps.get('language', 'Unknown')}
- **Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Project Description
{project_desc}

## Architecture & Dependencies
"""
        
        if ai_analysis and len(ai_analysis) > 100:
            # Include key insights from AI analysis
            content += "### AI Analysis Insights\n"
            content += "The following key insights were identified during setup:\n\n"
            
            # Extract first few lines or key sections
            analysis_lines = ai_analysis.split('\n')[:10]
            for line in analysis_lines:
                if line.strip() and not line.startswith('#'):
                    content += f"- {line.strip()}\n"
            content += "\n"
        
        content += "### Key Dependencies\n"
        dependencies = detected_deps.get('dependencies', [])
        if dependencies:
            for dep in dependencies[:10]:  # First 10 dependencies
                content += f"- `{dep}`\n"
            if len(dependencies) > 10:
                content += f"- ... and {len(dependencies) - 10} more dependencies\n"
        else:
            content += "- No dependencies detected\n"
        
        content += """
## External Documentation
Access up-to-date docs for dependencies in the `external_context/` directory:
"""
        
        saved_files = fetched_docs.get('saved_files', [])
        if saved_files:
            for file_info in saved_files:
                dep_name = file_info.get('dependency', 'unknown')
                filename = file_info.get('filename', f"{dep_name}.md")
                content += f"- **{dep_name}**: `external_context/{filename}`\n"
        else:
            content += "- No external documentation available\n"
        
        # Add MCP server information if available
        if self.setup_data.get('installed_mcp_servers'):
            content += """
## MCP Server Integration
This project is configured with VibeContext MCP server for enhanced documentation access.

### Available Tools:
- `file_structure`: Analyze large files efficiently with structural overview
- `resolve_library_id`: Search for libraries by name to get correct library ID
- `get_library_docs`: Get specific documentation for libraries using library ID and prompt
- `fetch_doc_url`: Fetch and convert documentation from URLs to markdown

### Usage Guidelines:
1. Always use `resolve_library_id` first to find the correct library identifier
2. Use `get_library_docs` with specific questions about the library
3. Prefer MCP server documentation over general knowledge for accuracy
4. Use `fetch_doc_url` for external documentation when needed
5. Use `file_structure` when processing large text files or encountering token limits
"""
        
        content += f"""
## Development Guidelines

### Code Style & Standards
- Follow {detected_deps.get('language', 'language')}-specific best practices
- Use consistent naming conventions throughout the project
- Write clear, self-documenting code with appropriate comments
- Leverage {ide_name} AI features for intelligent assistance

### Testing & Quality
- Write comprehensive tests for new features
- Maintain high code quality standards
- Run tests before committing changes
- Use AI assistance for test generation and code review

### Documentation  
- Keep documentation up-to-date with code changes
- Use external_context/ for dependency documentation references
- Document complex algorithms and business logic
- Maintain this configuration file as project evolves

### AI Assistant Guidelines
- Use project context from JUNO.md for comprehensive understanding
- Reference external documentation when available
- Be specific in your questions to get better responses
- Validate AI-generated code against project requirements
- Leverage {ide_name}'s intelligent features for code completion and analysis

---
*This file was generated automatically by juno-agent setup on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Update by running `juno setup` or `juno-agent setup` in this directory*
"""
        
        return content
    
    async def _show_completion_summary(self) -> None:
        """Show the setup completion summary."""
        try:
            # Generate consolidated summary
            summary_parts = [
                "---\n\n**Setup Complete**\n"
            ]
            
            # Project info
            project_desc = self.setup_data.get('project_description')
            if project_desc:
                summary_parts.append(f"**Project**: {project_desc}")
            
            # Editor info  
            selected_editor = self.setup_data.get('selected_editor')
            if selected_editor:
                summary_parts.append(f"**Editor**: {selected_editor}")
            
            # Dependencies info
            detected_deps = self.setup_data.get('detected_dependencies', {})
            if detected_deps.get('dependencies'):
                dep_count = len(detected_deps['dependencies'])
                language = detected_deps.get('language', 'Unknown')
                summary_parts.append(f"**Dependencies**: {dep_count} {language} packages")
            
            # MCP servers info
            installed_mcp = self.setup_data.get('installed_mcp_servers', [])
            if installed_mcp:
                summary_parts.append(f"**MCP Servers**: {', '.join(installed_mcp)}")
            
            # Documentation info
            fetched_docs = self.setup_data.get('fetched_docs', {})
            successful_docs = len(fetched_docs.get('successful', []))
            if successful_docs > 0:
                summary_parts.append(f"**Documentation**: {successful_docs} docs fetched")
            
            # Status info
            status_items = []
            if self.setup_data.get('external_context_setup'):
                status_items.append("External context")
            if self.setup_data.get('ide_configs_created'):
                status_items.append("IDE configs")
            if self.setup_data.get('permissions_configured'):
                status_items.append("Permissions")
            
            if status_items:
                summary_parts.append(f"**Configured**: {', '.join(status_items)}")
            
            # Verification info
            verification_results = self.setup_data.get('verification_results')
            if verification_results:
                status_counts = {"PASS": 0, "FAIL": 0, "WARN": 0, "INFO": 0}
                for result in verification_results:
                    status_counts[result.status] += 1
                
                success_rate = (status_counts["PASS"] / len(verification_results) * 100)
                
                if status_counts["FAIL"] == 0 and status_counts["WARN"] == 0:
                    verification_status = "🎉 All components verified"
                elif status_counts["FAIL"] == 0:
                    verification_status = f"✅ Verified with {status_counts['WARN']} warnings"
                else:
                    verification_status = f"⚠️ {status_counts['FAIL']} components need attention"
                
                summary_parts.append(f"**Verification**: {verification_status} ({success_rate:.0f}% success)")
            elif self.setup_data.get('verification_failed'):
                summary_parts.append("**Verification**: ❌ Verification failed - manual check recommended")
            
            summary_parts.append("\n---")
            
            final_message = "\n".join(summary_parts)
            self.chat_area.add_message(final_message, is_user=False)
            
            # Complete setup
            await self._complete_enhanced_setup()
            
        except Exception as e:
            self.chat_area.add_message(f"---\n\n**Setup Summary Error**\n\nError: {e}\n\n---", is_user=False)
            await self._complete_enhanced_setup()
    
    async def _complete_enhanced_setup(self) -> None:
        """Complete the enhanced setup process."""
        try:
            # Mark setup as completed in config
            config = self.config_manager.load_config()
            config.setup_completed = True
            self.config_manager.save_config(config)
            
            # Clean up setup state
            self.setup_active = False
            self.setup_data = {}
            
            # Final message
            self.chat_area.add_message("Setup wizard completed. Ready for AI assistance.", is_user=False)
            
        except Exception as e:
            self.chat_area.add_message(f"Setup completion error: {e}", is_user=False)
            self.setup_active = False
            self.setup_data = {}
    
    async def _handle_history_command(self) -> None:
        """Handle /history command - show interactive session selection menu."""
        print(f"[DEBUG] _handle_history_command: Storage manager available: {self.storage_manager is not None}")
        
        if not self.storage_manager:
            self.chat_area.add_message("❌ **History not available**\n\nConversation storage is not enabled. History requires TinyAgent storage integration.", is_user=False)
            return
        
        try:
            print(f"[DEBUG] _handle_history_command: Getting list of sessions...")
            # Get list of sessions (async call)
            sessions = await self.storage_manager.list_sessions()
            print(f"[DEBUG] _handle_history_command: Found {len(sessions)} sessions")
            
            # Show the interactive history menu
            if self.history_menu:
                self.history_menu.show(sessions)
            else:
                # Fallback to text display if menu not available
                self.chat_area.add_message("❌ **History menu not available**\n\nFalling back to text display...", is_user=False)
                await self._handle_history_command_fallback(sessions)
            
        except Exception as e:
            self.chat_area.add_message(f"❌ **Error retrieving history**: {str(e)}", is_user=False)
    
    async def _handle_history_command_fallback(self, sessions: List[Dict[str, Any]]) -> None:
        """Fallback text-based history display."""
        if not sessions:
            self.chat_area.add_message("📝 **No conversation history found**\n\nThis is your first conversation or no sessions have been saved.", is_user=False)
            return
        
        # Display sessions in a formatted way
        history_content = "📝 **Conversation History**\n\n"
        
        for i, session in enumerate(sessions[:10]):  # Show last 10 sessions
            session_id = session.get('session_id', 'unknown')
            created_at = session.get('created_at', 'unknown')
            message_count = session.get('message_count', 0)
            
            # Parse datetime for display
            try:
                from datetime import datetime
                if created_at != 'unknown':
                    created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    created_str = created_dt.strftime('%Y-%m-%d %H:%M')
                else:
                    created_str = 'unknown'
            except:
                created_str = str(created_at)[:16] if created_at != 'unknown' else 'unknown'
            
            # Get a summary of the session
            summary = self.storage_manager.get_session_summary(session)
            summary_preview = summary[:80] + "..." if len(summary) > 80 else summary
            
            history_content += f"**{i+1}. Session {session_id[:8]}...**\n"
            history_content += f"• Created: {created_str}\n"
            history_content += f"• Messages: {message_count}\n"
            history_content += f"• Preview: *{summary_preview}*\n\n"
        
        if len(sessions) > 10:
            history_content += f"*...and {len(sessions) - 10} more sessions*\n\n"
        
        history_content += "**💡 Note**: Use interactive menu (update available) for better session management!"
        
        self.chat_area.add_message(history_content, is_user=False)
    
    async def _handle_model_command(self) -> None:
        """Handle /model command for configuring AI models."""
        config = self.config_manager.load_config()
        agent_config = config.agent_config
        
        # Display current configuration
        current_config_content = f"""**🤖 AI Model Configuration**

**🔧 Current Configuration**
• **Model**: {agent_config.model_name}
• **Provider**: {agent_config.provider}
• **Temperature**: {agent_config.temperature}
• **Max Tokens**: {agent_config.max_tokens or 'Auto'}
• **API Key**: {'✅ Set' if self.config_manager.get_model_api_key() else '❌ Missing'}
• **Base URL**: {agent_config.custom_base_url or 'Default'}

📋 **Select a new model from the menu below, or press Escape to cancel.**"""

        self.chat_area.add_message(current_config_content, is_user=False)
        
        # Show the model selection menu
        if self.model_selection_menu:
            self.model_selection_menu.show()
    
    async def _handle_model_config_input(self, user_input: str) -> None:
        """Handle user input during model configuration."""
        if user_input.lower() in ['/cancel', '/quit', '/exit', 'q']:
            self.setup_active = False
            self.chat_area.add_message("Model configuration cancelled.", is_user=False)
            return
        
        mode_data = self.setup_data
        sub_step = mode_data.get('sub_step', 'menu')
        
        if sub_step == 'menu':
            await self._handle_model_menu_choice(user_input)
        elif sub_step == 'change_model':
            await self._handle_change_model_input(user_input)
        elif sub_step == 'api_key':
            await self._handle_model_api_key_input(user_input)
        elif sub_step == 'temperature':
            await self._handle_temperature_input(user_input)
        elif sub_step == 'max_tokens':
            await self._handle_max_tokens_input(user_input)
        elif sub_step == 'base_url':
            await self._handle_base_url_input(user_input)
        elif sub_step == 'select_openai_model':
            await self._handle_openai_model_selection(user_input)
        elif sub_step == 'select_anthropic_model':
            await self._handle_anthropic_model_selection(user_input)
        elif sub_step == 'select_google_model':
            await self._handle_google_model_selection(user_input)
        elif sub_step == 'select_groq_model':
            await self._handle_groq_model_selection(user_input)
        elif sub_step == 'custom_model_name':
            await self._handle_custom_model_name(user_input)
        elif sub_step == 'custom_provider':
            await self._handle_custom_provider(user_input)
        elif sub_step == 'ask_api_key':
            await self._handle_ask_api_key(user_input)
    
    async def _handle_model_menu_choice(self, choice: str) -> None:
        """Handle the main model configuration menu choice."""
        choice = choice.strip()
        
        if choice == "1":
            # Change model/provider
            self.chat_area.add_message("**🎯 Change Model & Provider**\n\nAvailable options:\n1. **OpenAI** - gpt-5-mini (recommended), gpt-5, o3, o4-mini\n2. **Anthropic** - claude-4-sonnet-20250514 (recommended), claude-4-haiku\n3. **Google** - gemini-2.5-pro (recommended), gemini-2.5-flash\n4. **Groq** - moonshotai/kimi-k2-instruct (recommended), qwen-coder\n5. **Custom** - Enter custom model details\n\nEnter your choice (1-5):", is_user=False)
            self.setup_data['sub_step'] = 'change_model'
            
        elif choice == "2":
            # Set API key
            config = self.config_manager.load_config()
            agent_config = config.agent_config
            expected_env_var = self._get_expected_env_var(agent_config.provider)
            
            self.chat_area.add_message(f"**🔑 API Key Configuration**\n\nFor **{agent_config.model_name}** ({agent_config.provider})\nExpected environment variable: **{expected_env_var}**\n\nPlease enter your API key (it will be saved securely):", is_user=False)
            self.setup_data['sub_step'] = 'api_key'
            
        elif choice == "3":
            # Adjust parameters
            config = self.config_manager.load_config()
            agent_config = config.agent_config
            self.chat_area.add_message(f"**⚙️ Model Parameters Configuration**\n\nCurrent temperature: **{agent_config.temperature}**\n\nEnter new temperature (0.0-2.0), or press Enter to keep current:", is_user=False)
            self.setup_data['sub_step'] = 'temperature'
            
        elif choice == "4":
            # Set custom base URL
            config = self.config_manager.load_config()
            agent_config = config.agent_config
            current_url = agent_config.custom_base_url or "Default"
            self.chat_area.add_message(f"**🌐 Custom Base URL Configuration**\n\nCurrent base URL: **{current_url}**\n\nEnter new base URL, or press Enter to use default:", is_user=False)
            self.setup_data['sub_step'] = 'base_url'
            
        elif choice == "5":
            # Reset to defaults
            from ..config import AgentConfig
            default_config = AgentConfig()
            
            try:
                # Use global scope by default for model configurations to persist across projects
                scope = "global"
                
                self.config_manager.update_agent_config_with_scope(
                    scope=scope,
                    model_name=default_config.model_name,
                    provider=default_config.provider,
                    temperature=default_config.temperature,
                    custom_base_url=default_config.custom_base_url,
                    api_key_env_var=default_config.api_key_env_var
                )
                
                scope_text = "globally" if scope == "global" else "for this project"
                self.chat_area.add_message(f"✅ **Model configuration reset to defaults** {scope_text}\n\nModel: **{default_config.model_name}** ({default_config.provider})", is_user=False)
                self.setup_active = False
                
            except Exception as e:
                self.chat_area.add_message(f"❌ Error resetting model config: {str(e)}", is_user=False)
                self.setup_active = False
            
        else:
            self.chat_area.add_message("❓ **Invalid choice**. Please enter 1-5 or 'q' to quit.", is_user=False)
    
    async def _handle_change_model_input(self, choice: str) -> None:
        """Handle model/provider change input."""
        choice = choice.strip()
        
        if choice == "1":
            # OpenAI
            self.chat_area.add_message("**OpenAI Models**\n\n1. **gpt-5** (latest flagship model)\n2. **gpt-5-mini** (recommended - fast, cost-effective)\n3. **o3** (advanced reasoning model)\n4. **o4-mini** (lightweight reasoning model)\n\nSelect model (1-4):", is_user=False)
            self.setup_data['provider'] = 'openai'
            self.setup_data['sub_step'] = 'select_openai_model'
            
        elif choice == "2":
            # Anthropic 
            self.chat_area.add_message("**Anthropic Models**\n\n1. **claude-4-sonnet-20250514** (recommended - latest v4)\n2. **claude-4-haiku** (fast, efficient v4)\n\nSelect model (1-2):", is_user=False)
            self.setup_data['provider'] = 'anthropic'
            self.setup_data['sub_step'] = 'select_anthropic_model'
            
        elif choice == "3":
            # Google
            self.chat_area.add_message("**Google Models**\n\n1. **gemini-2.5-pro** (recommended - most capable)\n2. **gemini-2.5-flash** (fast, efficient)\n\nSelect model (1-2):", is_user=False)
            self.setup_data['provider'] = 'google'
            self.setup_data['sub_step'] = 'select_google_model'
            
        elif choice == "4":
            # Groq
            self.chat_area.add_message("**Groq Models**\n\n1. **moonshotai/kimi-k2-instruct** (recommended - high performance)\n2. **qwen-coder** (specialized for coding)\n\nSelect model (1-2):", is_user=False)
            self.setup_data['provider'] = 'groq'
            self.setup_data['sub_step'] = 'select_groq_model'
            
        elif choice == "5":
            # Custom
            self.chat_area.add_message("**Custom Model Configuration**\n\nEnter the model name (LiteLLM format, e.g., 'gpt-5' or 'claude-4-sonnet-20250514'):", is_user=False)
            self.setup_data['provider'] = 'custom'
            self.setup_data['sub_step'] = 'custom_model_name'
            
        else:
            self.chat_area.add_message("❓ **Invalid choice**. Please enter 1-5.", is_user=False)
    
    async def _handle_model_api_key_input(self, api_key: str) -> None:
        """Handle API key input."""
        if not api_key.strip():
            self.chat_area.add_message("❌ **Please enter a valid API key**.", is_user=False)
            return
        
        try:
            config = self.config_manager.load_config()
            agent_config = config.agent_config
            expected_env_var = self._get_expected_env_var(agent_config.provider)
            
            # Use global scope by default for API keys to persist across projects
            scope = "global"
            self.config_manager.set_model_api_key_with_scope(api_key.strip(), scope=scope, key_name=expected_env_var)
            
            scope_text = "globally" if scope == "global" else "locally"
            self.chat_area.add_message(f"✅ **API key saved** {scope_text} as **{expected_env_var}**\n\n🔒 Key is securely stored and will not be logged", is_user=False)
            self.setup_active = False
            
        except Exception as e:
            self.chat_area.add_message(f"❌ **Error saving API key**: {str(e)}", is_user=False)
            self.setup_active = False
    
    async def _handle_temperature_input(self, temp_str: str) -> None:
        """Handle temperature input."""
        if not temp_str.strip():
            # Keep current temperature
            self.chat_area.add_message("✅ **Temperature unchanged**", is_user=False)
            # Continue to max_tokens configuration
            config = self.config_manager.load_config()
            agent_config = config.agent_config
            self.chat_area.add_message(f"**Max Tokens Configuration**\n\nCurrent max tokens: **{agent_config.max_tokens or 'Auto'}**\n\nEnter new max tokens value, or press Enter to keep current:", is_user=False)
            self.setup_data['sub_step'] = 'max_tokens'
            return
        
        try:
            temperature = float(temp_str)
            if 0.0 <= temperature <= 2.0:
                scope = "global"  # Default to global for model configurations
                self.config_manager.update_agent_config_with_scope(scope=scope, temperature=temperature)
                scope_text = "globally" if scope == "global" else "for this project"
                self.chat_area.add_message(f"✅ **Temperature set to {temperature}** {scope_text}", is_user=False)
                
                # Continue to max_tokens configuration
                config = self.config_manager.load_config()
                agent_config = config.agent_config
                self.chat_area.add_message(f"**Max Tokens Configuration**\n\nCurrent max tokens: **{agent_config.max_tokens or 'Auto'}**\n\nEnter new max tokens value, or press Enter to keep current:", is_user=False)
                self.setup_data['sub_step'] = 'max_tokens'
            else:
                self.chat_area.add_message("❌ **Temperature must be between 0.0 and 2.0**. Please try again:", is_user=False)
        except ValueError:
            self.chat_area.add_message("❌ **Invalid temperature value**. Please enter a number between 0.0 and 2.0:", is_user=False)
    
    async def _handle_max_tokens_input(self, tokens_str: str) -> None:
        """Handle max tokens input."""
        if not tokens_str.strip():
            # Set to auto (None)
            scope = "global"  # Default to global for model configurations
            self.config_manager.update_agent_config_with_scope(scope=scope, max_tokens=None)
            scope_text = "globally" if scope == "global" else "for this project"
            self.chat_area.add_message(f"✅ **Max tokens set to auto** {scope_text}", is_user=False)
            self.setup_active = False
            return
        
        try:
            max_tokens = int(tokens_str)
            if max_tokens > 0:
                scope = "global"  # Default to global for model configurations
                self.config_manager.update_agent_config_with_scope(scope=scope, max_tokens=max_tokens)
                scope_text = "globally" if scope == "global" else "for this project"
                self.chat_area.add_message(f"✅ **Max tokens set to {max_tokens}** {scope_text}", is_user=False)
                self.setup_active = False
            else:
                self.chat_area.add_message("❌ **Max tokens must be positive**. Please try again:", is_user=False)
        except ValueError:
            self.chat_area.add_message("❌ **Invalid max tokens value**. Please enter a positive integer:", is_user=False)
    
    async def _handle_base_url_input(self, url_str: str) -> None:
        """Handle base URL input."""
        scope = "global"  # Default to global for model configurations
        
        if not url_str.strip():
            # Reset to default
            self.config_manager.update_agent_config_with_scope(scope=scope, custom_base_url=None)
            scope_text = "globally" if scope == "global" else "for this project"
            self.chat_area.add_message(f"✅ **Base URL reset to default** {scope_text}", is_user=False)
        else:
            # Set custom URL
            self.config_manager.update_agent_config_with_scope(scope=scope, custom_base_url=url_str.strip())
            scope_text = "globally" if scope == "global" else "for this project"
            self.chat_area.add_message(f"✅ **Base URL set to {url_str.strip()}** {scope_text}", is_user=False)
        
        self.setup_active = False
    
    async def _handle_openai_model_selection(self, choice: str) -> None:
        """Handle OpenAI model selection."""
        models = {
            "1": ("gpt-5", "GPT-5"),
            "2": ("gpt-5-mini", "GPT-5 Mini"),
            "3": ("o3", "O3"),
            "4": ("o4-mini", "O4 Mini")
        }
        
        if choice.strip() in models:
            model_name, display_name = models[choice.strip()]
            await self._save_model_config(model_name, "openai", 1.0, display_name)
        else:
            self.chat_area.add_message("❓ **Invalid choice**. Please enter 1-4.", is_user=False)
    
    async def _handle_anthropic_model_selection(self, choice: str) -> None:
        """Handle Anthropic model selection."""
        models = {
            "1": ("claude-4-sonnet-20250514", "Claude 4 Sonnet"),
            "2": ("claude-4-haiku", "Claude 4 Haiku")
        }
        
        if choice.strip() in models:
            model_name, display_name = models[choice.strip()]
            await self._save_model_config(model_name, "anthropic", 0.2, display_name)
        else:
            self.chat_area.add_message("❓ **Invalid choice**. Please enter 1-2.", is_user=False)
    
    async def _handle_google_model_selection(self, choice: str) -> None:
        """Handle Google model selection."""
        models = {
            "1": ("gemini-2.5-pro", "Gemini 2.5 Pro"),
            "2": ("gemini-2.5-flash", "Gemini 2.5 Flash")
        }
        
        if choice.strip() in models:
            model_name, display_name = models[choice.strip()]
            await self._save_model_config(model_name, "google", 0.7, display_name)
        else:
            self.chat_area.add_message("❓ **Invalid choice**. Please enter 1-2.", is_user=False)
    
    async def _handle_groq_model_selection(self, choice: str) -> None:
        """Handle Groq model selection."""
        models = {
            "1": ("moonshotai/kimi-k2-instruct", "Moonshot K2 Instruct"),
            "2": ("qwen-coder", "Qwen Coder")
        }
        
        if choice.strip() in models:
            model_name, display_name = models[choice.strip()]
            await self._save_model_config(model_name, "groq", 0.7, display_name)
        else:
            self.chat_area.add_message("❓ **Invalid choice**. Please enter 1-2.", is_user=False)
    
    async def _handle_custom_model_name(self, model_name: str) -> None:
        """Handle custom model name input."""
        if not model_name.strip():
            self.chat_area.add_message("❌ **Please enter a valid model name**.", is_user=False)
            return
        
        self.setup_data['custom_model'] = model_name.strip()
        self.chat_area.add_message("**Provider Configuration**\n\nEnter the provider name (e.g., 'openai', 'anthropic', 'custom'):", is_user=False)
        self.setup_data['sub_step'] = 'custom_provider'
    
    async def _handle_custom_provider(self, provider: str) -> None:
        """Handle custom provider input."""
        if not provider.strip():
            self.chat_area.add_message("❌ **Please enter a valid provider name**.", is_user=False)
            return
        
        model_name = self.setup_data.get('custom_model')
        await self._save_model_config(model_name, provider.strip(), 0.7, f"Custom: {model_name}")
    
    async def _save_model_config(self, model_name: str, provider: str, temperature: float, display_name: str) -> None:
        """Save model configuration and exit model config mode."""
        try:
            # Use global scope by default for model configurations to persist across projects
            scope = "global"
            
            # Get the correct API key environment variable for this provider
            api_key_env_var = self._get_expected_env_var(provider)
            
            self.config_manager.update_agent_config_with_scope(
                scope=scope,
                model_name=model_name,
                provider=provider,
                temperature=temperature,
                api_key_env_var=api_key_env_var
            )
            
            scope_text = "globally" if scope == "global" else "for this project"
            self.chat_area.add_message(f"✅ **Model updated to {display_name}** {scope_text}\n\nProvider: **{provider}**\nTemperature: **{temperature}**", is_user=False)
            
            # Reinitialize agent with new model configuration
            try:
                await self.initialize_agent()
                self.debug_log.info("Agent reinitialized successfully after model config save")
            except Exception as agent_error:
                self.debug_log.error(f"Agent reinitialization failed after model config save: {agent_error}")
                self.chat_area.add_message(f"⚠️ **Model saved but agent initialization failed**: {str(agent_error)}", is_user=False)
            
            # Ask about API key
            expected_env_var = self._get_expected_env_var(provider)
            current_key = self.config_manager.get_model_api_key()
            
            if not current_key:
                self.chat_area.add_message(f"**🔑 API Key Setup**\n\nWould you like to set up the API key for **{provider}** now?\nExpected environment variable: **{expected_env_var}**\n\nReply with **'yes'** to enter API key, or **'no'** to skip:", is_user=False)
                self.setup_data['sub_step'] = 'ask_api_key'
            else:
                self.chat_area.add_message("**✅ Configuration Complete!**\n\nModel configuration updated successfully. API key is already configured.", is_user=False)
                self.setup_active = False
                
        except Exception as e:
            self.chat_area.add_message(f"❌ **Error saving model config**: {str(e)}", is_user=False)
            self.setup_active = False
    
    async def _handle_ask_api_key(self, response: str) -> None:
        """Handle API key setup question response."""
        if response.lower().strip() in ['yes', 'y', '1', 'true']:
            # Switch to API key input mode
            config = self.config_manager.load_config()
            agent_config = config.agent_config
            expected_env_var = self._get_expected_env_var(agent_config.provider)
            
            self.chat_area.add_message(f"**🔑 API Key Configuration**\n\nFor **{agent_config.model_name}** ({agent_config.provider})\nExpected environment variable: **{expected_env_var}**\n\nPlease enter your API key (it will be saved securely):", is_user=False)
            self.setup_data['sub_step'] = 'api_key'
        else:
            # Skip API key setup
            self.chat_area.add_message("**✅ Configuration Complete!**\n\nModel configuration updated successfully. You can set up the API key later using `/model` command option 2.", is_user=False)
            self.setup_active = False
    
    def _extract_first_two_paragraphs(self, summary: str) -> str:
        """Extract the first 2 paragraphs from a summary for preview display.
        
        Args:
            summary: The full summary text
            
        Returns:
            A formatted string containing the first 2 paragraphs, or a fallback message
        """
        if not summary or not summary.strip():
            return "No summary content available."
        
        # Clean up the summary text
        cleaned_summary = summary.strip()
        
        # Split by double newlines (common paragraph separator)
        paragraphs = [p.strip() for p in cleaned_summary.split('\n\n') if p.strip()]
        
        # If no double newlines, try single newlines but be more conservative
        if len(paragraphs) <= 1:
            lines = [line.strip() for line in cleaned_summary.split('\n') if line.strip()]
            # Group lines into paragraphs (assume every 2-3 lines is a paragraph)
            if len(lines) > 3:
                # Try to detect paragraph breaks by finding empty lines or significant content changes
                paragraphs = []
                current_paragraph = []
                
                for line in lines:
                    if len(line) < 20 and len(current_paragraph) > 0:  # Short line might be end of paragraph
                        current_paragraph.append(line)
                        paragraphs.append(' '.join(current_paragraph))
                        current_paragraph = []
                    else:
                        current_paragraph.append(line)
                
                # Add remaining lines as final paragraph
                if current_paragraph:
                    paragraphs.append(' '.join(current_paragraph))
            else:
                # Very short summary, treat as single paragraph
                paragraphs = [' '.join(lines)]
        
        # Take first 2 paragraphs
        selected_paragraphs = paragraphs[:2]
        
        # Handle very long paragraphs by truncating if needed
        max_paragraph_length = 300  # Reasonable length for display
        truncated_paragraphs = []
        
        for para in selected_paragraphs:
            if len(para) > max_paragraph_length:
                # Find a good break point (preferably at sentence end)
                truncate_point = max_paragraph_length
                # Look for sentence endings within reasonable range
                for i in range(max_paragraph_length - 50, min(len(para), max_paragraph_length + 50)):
                    if para[i] in '.!?':
                        truncate_point = i + 1
                        break
                
                truncated_para = para[:truncate_point].strip()
                if not truncated_para.endswith(('.', '!', '?')):
                    truncated_para += "..."
                truncated_paragraphs.append(truncated_para)
            else:
                truncated_paragraphs.append(para)
        
        # Join paragraphs with double newlines
        result = '\n\n'.join(truncated_paragraphs)
        
        # Fallback for very short content
        if len(result.strip()) < 10:
            return "Brief summary generated - content preserved in context."
        
        return result

    async def ui_tool_update_callback(self, message_type: str, data: dict) -> None:
        """
        Bridge method to handle UI updates from TextualToolCallback.
        
        This method receives updates from the TextualToolCallback and integrates
        tool calls inline with chat messages.
        
        Args:
            message_type: Type of the tool update ('tool_start', 'tool_end', 'tool_error')
            data: Dictionary containing tool event data
        """
        debug_logger.log_function_entry("ui_tool_update_callback", 
                                       message_type=message_type,
                                       data_keys=list(data.keys()),
                                       chat_area_available=self.chat_area is not None,
                                       add_tool_event_available=hasattr(self.chat_area, 'add_tool_event') if self.chat_area else False)
        
        # Add critical debug log to see if this method is actually being called
        debug_logger.log_event("UI_TOOL_UPDATE_CALLBACK_INVOKED", 
                             message_type=message_type,
                             app_id=hex(id(self)),
                             chat_area_id=hex(id(self.chat_area)) if self.chat_area else None)
        
        try:
            if self.chat_area and hasattr(self.chat_area, 'add_tool_event'):
                debug_logger.log_event("calling_chat_area_add_tool_event", 
                                     message_type=message_type,
                                     chat_area_id=hex(id(self.chat_area)))
                # Send tool events directly to chat area for inline display
                await self.chat_area.add_tool_event(message_type, data)
                debug_logger.log_event("chat_area_add_tool_event_completed", message_type=message_type)
            else:
                debug_logger.log_event("chat_area_not_available_or_missing_method",
                                     chat_area_available=self.chat_area is not None,
                                     add_tool_event_available=hasattr(self.chat_area, 'add_tool_event') if self.chat_area else False)
        except Exception as e:
            debug_logger.log_error("ui_tool_update_callback_failed", e,
                                 message_type=message_type,
                                 chat_area_id=hex(id(self.chat_area)) if self.chat_area else None)
            # Log error but don't break the UI - fall back to simple messages
            if message_type == "tool_start":
                tool_name = data.get("tool_name", "unknown")
                self.chat_area.add_message(f"🔧 Using {tool_name} tool...", is_user=False)
                debug_logger.log_event("fallback_tool_start_message", tool_name=tool_name)
            elif message_type == "tool_end":
                tool_name = data.get("tool_name", "unknown")
                result = data.get("result", "")
                result_preview = result[:100] + "..." if len(result) > 100 else result
                self.chat_area.add_message(f"✅ {tool_name} completed: {result_preview}", is_user=False)
                debug_logger.log_event("fallback_tool_end_message", tool_name=tool_name)
            elif message_type == "tool_error":
                tool_name = data.get("tool_name", "unknown")
                error = data.get("error", "Unknown error")
                self.chat_area.add_message(f"❌ {tool_name} failed: {error}", is_user=False)
                debug_logger.log_event("fallback_tool_error_message", tool_name=tool_name)
        
        debug_logger.log_function_exit("ui_tool_update_callback")
        
        # Update footer hint when tool events occur
        self._update_footer_hint()

    def _get_expected_env_var(self, provider: str) -> str:
        """Get expected environment variable name for a provider."""
        provider_lower = provider.lower()
        if provider_lower == "openai":
            return "OPENAI_API_KEY"
        elif provider_lower == "anthropic":
            return "ANTHROPIC_API_KEY"
        elif provider_lower == "google":
            return "GOOGLE_API_KEY"
        elif provider_lower == "azure":
            return "AZURE_OPENAI_API_KEY"
        elif provider_lower == "cohere":
            return "COHERE_API_KEY"
        elif provider_lower == "huggingface":
            return "HUGGINGFACE_API_KEY"
        elif provider_lower == "groq":
            return "GROQ_API_KEY"
        elif provider_lower == "xai":
            return "XAI_API_KEY"
        elif provider_lower == "openrouter":
            return "OPENROUTER_API_KEY"
        elif provider_lower == "ollama":
            return "OLLAMA_API_KEY"
        elif provider_lower in ["together_ai", "togetherai"]:
            return "TOGETHER_API_KEY"
        else:
            return f"{provider.upper()}_API_KEY"
    
    async def _handle_model_selected(self, model: Dict[str, Any], provider: str) -> None:
        """Handle when a model is selected from the menu."""
        try:
            model_id = model.get('id', 'unknown')
            display_name = model.get('display_name', model_id)
            
            # Load models config to get provider info
            models_config_path = Path(__file__).parent / "models.json"
            if models_config_path.exists():
                import json
                with open(models_config_path, 'r') as f:
                    models_config = json.load(f)
                
                provider_data = models_config.get("providers", {}).get(provider, {})
                api_key_env = provider_data.get("api_key_env", f"{provider.upper()}_API_KEY")
            else:
                api_key_env = self._get_expected_env_var(provider)
            
            # Always use the unified model configuration flow
            # This will handle API key checking and user prompts consistently
            await self._configure_selected_model(model, provider)
            
        except Exception as e:
            self.chat_area.add_message(f"❌ **Error selecting model**: {str(e)}", is_user=False)
    
    async def _handle_manual_model_entry(self) -> None:
        """Handle manual model entry request."""
        self.chat_area.add_message("""**🔧 Manual Model Entry**

Please enter the model details in the format: `provider/model-name`

**Examples:**
• `openai/gpt-4`
• `anthropic/claude-3-sonnet`
• `google/gemini-pro`
• `groq/llama2-70b-chat`
• `ollama/codellama`

Enter your custom model:""", is_user=False)
        
        # Start manual entry mode
        self.setup_active = True
        self.setup_step = 0
        self.setup_data = {'mode': 'manual_model_entry'}
    
    async def _handle_api_key_entered(self, api_key: str, provider: str) -> None:
        """Handle when API key is entered."""
        try:
            # Add comprehensive debugging
            debug_log = self.debug_log
            debug_log.debug(f"API key entered", provider=provider, has_key=bool(api_key), key_length=len(api_key) if api_key else 0)
            
            # Get the environment variable name for this provider
            # Check if we have a stored API key env from pending model selection (for manual entries)
            if hasattr(self, '_pending_model_selection') and 'api_key_env' in self._pending_model_selection:
                env_var = self._pending_model_selection['api_key_env']
            else:
                # Use standard provider mapping
                env_var = self._get_expected_env_var(provider)
            
            debug_log.debug(f"Determined env var", provider=provider, env_var=env_var)
            
            # Save API key to config with global scope for consistency and cross-project persistence
            scope = "global"
            debug_log.debug(f"Calling set_model_api_key_with_scope", api_key_provided=bool(api_key), key_name=env_var, scope=scope)
            self.config_manager.set_model_api_key_with_scope(api_key, scope=scope, key_name=env_var)
            
            debug_log.info(f"API key saved successfully", provider=provider, env_var=env_var, scope=scope)
            scope_text = "globally" if scope == "global" else "locally"
            self.chat_area.add_message(f"🔑 **API Key Saved** {scope_text} for {provider.title()} (as {env_var})\n⏳ **Configuring model...**", is_user=False)
            
            # Hide the API key prompt 
            if self.api_key_prompt:
                self.api_key_prompt.hide()
            
            # Check for different types of pending operations
            if hasattr(self, '_pending_model_selection'):
                debug_log.debug(f"Processing pending model selection")
                pending = self._pending_model_selection
                await self._configure_selected_model(pending["model"], pending["provider"])
                delattr(self, '_pending_model_selection')
                debug_log.debug(f"Completed pending model selection")
            
            # Check for model setup context from API key prompt
            elif hasattr(self.api_key_prompt, 'context') and self.api_key_prompt.context.get('model_setup'):
                debug_log.debug(f"Processing model setup after API key entry")
                context = self.api_key_prompt.context
                model_id = context.get('model_id', '')
                provider = context.get('provider', '')
                display_name = context.get('display_name', model_id)
                
                # Save model configuration and continue with global default flow
                await self._save_model_with_new_api_key(model_id, provider, display_name)
                debug_log.debug(f"Completed model setup after API key entry")
            
            if self.chat_input:
                self.chat_input.focus_input()
                
        except Exception as e:
            debug_log.error(f"Error saving API key: {str(e)}", provider=provider)
            self.chat_area.add_message(f"❌ **Error saving API key**: {str(e)}", is_user=False)
    
    def _handle_api_key_entered_direct(self, api_key: str, provider: str) -> None:
        """Handle API key entered via direct callback (non-async wrapper)."""
        # Schedule the async handler to run
        self.call_after_refresh(self._schedule_api_key_handler, api_key, provider)
    
    async def _schedule_api_key_handler(self, api_key: str, provider: str) -> None:
        """Schedule the async API key handler."""
        await self._handle_api_key_entered(api_key, provider)
    
    async def _configure_selected_model(self, model: Dict[str, Any], provider: str) -> None:
        """Configure the selected model in the config."""
        try:
            debug_log = self.debug_log
            model_id = model.get('id', 'unknown')
            display_name = model.get('display_name', model_id)
            
            debug_log.debug(f"Configuring selected model", model_id=model_id, provider=provider, display_name=display_name)
            
            # First, always save to local config for this project
            debug_log.debug(f"Saving to local config first", model_id=model_id, provider=provider)
            
            # Get the correct API key environment variable for this provider
            api_key_env_var = self._get_expected_env_var(provider)
            debug_log.debug(f"Using API key env var", api_key_env_var=api_key_env_var, provider=provider)
            
            # Check if API key already exists for this provider
            existing_api_key = self.config_manager.has_api_key_for_provider(provider)
            debug_log.debug(f"Existing API key for provider {provider}", has_key=existing_api_key)
            
            if existing_api_key:
                # API key exists - ask user if they want to update it
                debug_log.debug(f"API key exists for {provider}, asking user if they want to update")
                
                self.yes_no_menu.show(
                    title="🔑 Update API Key?",
                    message=f"You already have an API key configured for {provider.title()}.\n\nWould you like to update it with a new value?",
                    yes_label="🔄 Yes, update API key",
                    no_label="✅ No, use existing key",
                    context={
                        'type': 'api_key_update',
                        'model_id': model_id,
                        'provider': provider,
                        'display_name': display_name,
                        'api_key_env_var': api_key_env_var
                    }
                )
                
                # Blur chat input and focus yes/no menu
                if self.chat_input:
                    self.chat_input.blur()
                self.call_after_refresh(self._ensure_yes_no_menu_focus)
                
            else:
                # No API key exists - show API key prompt directly
                debug_log.debug(f"No API key for {provider}, showing API key prompt")
                
                self.api_key_prompt.show(
                    title=f"Set {provider.title()} API Key",
                    provider=provider,
                    context={'model_setup': True, 'model_id': model_id, 'provider': provider, 'display_name': display_name}
                )
                # Blur chat input and focus API key prompt
                if self.chat_input:
                    self.chat_input.blur()
                self.call_after_refresh(self._ensure_api_key_prompt_focus)
            
            # Hide the model selection menu
            if self.model_selection_menu:
                self.model_selection_menu.hide()
                
        except Exception as e:
            debug_log.error(f"Error configuring model: {str(e)}", model_id=model.get('id', 'unknown'), provider=provider)
            if self.chat_area:
                self.chat_area.add_message(f"❌ **Error configuring model**: {str(e)}", is_user=False)
    
    def _show_global_default_prompt(self, display_name: str, provider: str) -> None:
        """Show prompt asking if user wants to set model as global default."""
        # Remove focus from chat input first
        if self.chat_input:
            self.chat_input.blur()
        
        # Show the global default menu widget
        if self.global_default_menu:
            self.global_default_menu.show(display_name, provider)
            # Ensure menu gets focus after a brief delay
            self.call_after_refresh(self._ensure_global_menu_focus)
    
    def _ensure_global_menu_focus(self) -> None:
        """Ensure the global default menu has focus."""
        if self.global_default_menu and self.global_default_menu.is_visible:
            self.global_default_menu.focus()
    
    def _ensure_yes_no_menu_focus(self) -> None:
        """Ensure the yes/no menu has focus."""
        if self.yes_no_menu and self.yes_no_menu.is_visible:
            self.yes_no_menu.focus()
    
    def _ensure_api_key_prompt_focus(self) -> None:
        """Ensure the API key prompt has focus."""
        if self.api_key_prompt and self.api_key_prompt.is_visible:
            self.api_key_prompt.focus()
    
    async def _handle_global_default_selection(self, set_global: bool) -> None:
        """Handle the selection from global default menu."""
        try:
            debug_log = self.debug_log
            
            if set_global and hasattr(self, '_pending_global_model'):
                pending = self._pending_global_model
                debug_log.debug(f"Saving model to global config", model_id=pending['model_id'], provider=pending['provider'])
                
                # Save to global config with correct API key env var
                self.config_manager.update_agent_config_with_scope(
                    scope="global",
                    model_name=pending['model_id'],
                    provider=pending['provider'],
                    api_key_env_var=pending['api_key_env_var']
                )
                
                debug_log.info(f"Model saved to global config", model=pending['model_id'], provider=pending['provider'])
                
                # Check agent status
                agent_status = "✅ Reinitialized and ready" if pending.get('agent_reinitialized', True) else f"❌ Failed: {pending.get('agent_error', 'Unknown error')}"
                
                success_message = f"""✅ **Model Configuration Complete**

📋 **Configuration Summary:**
• **Model**: {pending['display_name']}
• **Provider**: {pending['provider'].title()}
• **Local Config**: ✅ Saved (for this project)
• **Global Config**: ✅ Saved (default for all projects)
• **Agent**: {agent_status}

🎉 **Ready to chat!** Your new model is active."""
            else:
                if hasattr(self, '_pending_global_model'):
                    pending = self._pending_global_model
                    # Check agent status
                    agent_status = "✅ Reinitialized and ready" if pending.get('agent_reinitialized', True) else f"❌ Failed: {pending.get('agent_error', 'Unknown error')}"
                    
                    success_message = f"""✅ **Model Configuration Complete**

📋 **Configuration Summary:**
• **Model**: {pending['display_name']}
• **Provider**: {pending['provider'].title()}
• **Local Config**: ✅ Saved (for this project only)
• **Global Config**: Not changed
• **Agent**: {agent_status}

🎉 **Ready to chat!** Your new model is active for this project."""
                else:
                    success_message = "✅ **Model configuration complete**"
            
            self.chat_area.add_message(success_message, is_user=False)
            
            # Clean up pending model
            if hasattr(self, '_pending_global_model'):
                delattr(self, '_pending_global_model')
            
            # Refresh welcome screen to show updated model information
            self._refresh_welcome_message()
            
            # Update footer and focus input
            self._update_footer_stats()
            if self.chat_input:
                self.chat_input.focus_input()
                
        except Exception as e:
            debug_log.error(f"Error handling global default response: {str(e)}")
            self.chat_area.add_message(f"❌ **Error**: {str(e)}", is_user=False)
            self.setup_active = False
            self.setup_data = {}
    
    async def _handle_yes_no_selection(self, selected_yes: bool, context: dict) -> None:
        """Handle Yes/No selection from the reusable YesNoMenu."""
        try:
            debug_log = self.debug_log
            debug_log.debug(f"Handling yes/no selection", selected_yes=selected_yes, context=context)
            
            # Route to specific handlers based on context
            context_type = context.get('type', 'unknown')
            
            if context_type == 'api_key_update':
                await self._handle_api_key_update_selection(selected_yes, context)
            else:
                debug_log.warning(f"Unknown yes/no context type", context_type=context_type)
                self.chat_area.add_message(f"❌ **Error**: Unknown selection context: {context_type}", is_user=False)
            
            # Always focus input after selection
            if self.chat_input:
                self.chat_input.focus_input()
                
        except Exception as e:
            debug_log.error(f"Error handling yes/no selection: {str(e)}")
            self.chat_area.add_message(f"❌ **Error**: {str(e)}", is_user=False)
    
    async def _handle_api_key_update_selection(self, update_api_key: bool, context: dict) -> None:
        """Handle API key update selection."""
        try:
            debug_log = self.debug_log
            
            if update_api_key:
                # User wants to update API key - show API key prompt
                model_id = context.get('model_id', '')
                provider = context.get('provider', '')
                
                debug_log.debug(f"User chose to update API key", model_id=model_id, provider=provider)
                
                # Show API key prompt
                self.api_key_prompt.show(
                    title=f"Update {provider.title()} API Key",
                    provider=provider,
                    context={'model_setup': True, 'model_id': model_id, 'provider': provider}
                )
                # Blur chat input and focus API key prompt
                if self.chat_input:
                    self.chat_input.blur()
                self.call_after_refresh(self._ensure_api_key_prompt_focus)
                
            else:
                # User doesn't want to update API key - proceed with existing key
                model_id = context.get('model_id', '')
                provider = context.get('provider', '')
                display_name = context.get('display_name', model_id)
                
                debug_log.debug(f"User chose to keep existing API key", model_id=model_id, provider=provider)
                
                # Save model config without updating API key
                await self._save_model_without_api_key_update(model_id, provider, display_name)
                
        except Exception as e:
            debug_log.error(f"Error handling API key update selection: {str(e)}")
            self.chat_area.add_message(f"❌ **Error**: {str(e)}", is_user=False)
    
    async def _save_model_without_api_key_update(self, model_id: str, provider: str, display_name: str) -> None:
        """Save model configuration without updating API key."""
        try:
            debug_log = self.debug_log
            
            # Get the correct API key environment variable for this provider
            api_key_env_var = self._get_expected_env_var(provider)
            
            debug_log.debug(f"Saving model without API key update", model_id=model_id, provider=provider, api_key_env_var=api_key_env_var)
            
            # Save to local config
            self.config_manager.update_agent_config_with_scope(
                scope="local",
                model_name=model_id,
                provider=provider.lower(),
                api_key_env_var=api_key_env_var
            )
            
            # Reinitialize agent
            await self.initialize_agent()
            
            # Store pending model info for global default prompt
            self._pending_global_model = {
                'model_id': model_id,
                'provider': provider,
                'display_name': display_name,
                'api_key_env_var': api_key_env_var,
                'agent_reinitialized': True
            }
            
            # Show global default selection menu
            self.global_default_menu.show(display_name, provider)
            # Blur chat input and focus global default menu
            if self.chat_input:
                self.chat_input.blur()
            self.call_after_refresh(self._ensure_global_menu_focus)
            
        except Exception as e:
            debug_log.error(f"Error saving model without API key update: {str(e)}")
            self.chat_area.add_message(f"❌ **Error**: {str(e)}", is_user=False)
    
    async def _save_model_with_new_api_key(self, model_id: str, provider: str, display_name: str) -> None:
        """Save model configuration after new API key has been set."""
        try:
            debug_log = self.debug_log
            
            # Get the correct API key environment variable for this provider
            api_key_env_var = self._get_expected_env_var(provider)
            
            debug_log.debug(f"Saving model with new API key", model_id=model_id, provider=provider, api_key_env_var=api_key_env_var)
            
            # Save to local config
            self.config_manager.update_agent_config_with_scope(
                scope="local",
                model_name=model_id,
                provider=provider.lower(),
                api_key_env_var=api_key_env_var
            )
            
            # Reinitialize agent
            await self.initialize_agent()
            
            # Store pending model info for global default prompt
            self._pending_global_model = {
                'model_id': model_id,
                'provider': provider,
                'display_name': display_name,
                'api_key_env_var': api_key_env_var,
                'agent_reinitialized': True
            }
            
            # Show global default selection menu
            self.global_default_menu.show(display_name, provider)
            # Blur chat input and focus global default menu
            if self.chat_input:
                self.chat_input.blur()
            self.call_after_refresh(self._ensure_global_menu_focus)
            
        except Exception as e:
            debug_log.error(f"Error saving model with new API key: {str(e)}")
            self.chat_area.add_message(f"❌ **Error**: {str(e)}", is_user=False)
    
    async def _handle_manual_model_input(self, user_input: str) -> None:
        """Handle manual model input."""
        try:
            debug_log = self.debug_log
            model_input = user_input.strip()
            
            debug_log.debug(f"Processing manual model input", input=model_input)
            
            if not model_input:
                self.chat_area.add_message("❌ **Please enter a valid model name**", is_user=False)
                return
            
            # Parse provider/model format
            if '/' in model_input:
                provider, model_name = model_input.split('/', 1)
            else:
                # Assume it's an OpenAI model if no provider specified
                provider = "openai"
                model_name = model_input
            
            provider = provider.strip()
            model_name = model_name.strip()
            
            debug_log.debug(f"Parsed manual model", provider=provider, model_name=model_name)
            
            # Create a model dict for the manual entry
            manual_model = {
                'id': model_input,  # Use full input as ID (e.g., "together_ai/codellama-34b")
                'display_name': model_name,
                'max_tokens': 0,  # Unknown for manual entries
                'supports_vision': False,  # Unknown for manual entries
                'supports_function_calling': True  # Assume true for manual entries
            }
            
            debug_log.debug(f"Created manual model dict", model=manual_model)
            
            # Determine API key environment variable for this provider
            provider_lower = provider.lower()
            known_providers = ["openai", "anthropic", "google", "groq", "xai", "openrouter", "ollama", "together_ai", "togetherai"]
            
            if provider_lower in known_providers:
                api_key_env = self._get_expected_env_var(provider)
            else:
                # Use MANUAL_LLM_API_KEY for unknown providers
                api_key_env = "MANUAL_LLM_API_KEY"
            
            debug_log.debug(f"Determined API key env for manual model", provider=provider, api_key_env=api_key_env)
            
            # Check if API key is available
            import os
            if not os.getenv(api_key_env) and provider_lower != "ollama":
                # Show API key prompt
                self.chat_area.add_message(f"🔑 **API Key Required** for {provider} (will be saved as {api_key_env})", is_user=False)
                if self.api_key_prompt:
                    self.api_key_prompt.show(provider, api_key_env, self._handle_api_key_entered_direct)
                # Store manual model for after API key is entered
                self._pending_model_selection = {"model": manual_model, "provider": provider, "api_key_env": api_key_env}
                debug_log.debug(f"Showing API key prompt for manual model", api_key_env=api_key_env)
            else:
                # Configure the model directly
                await self._configure_selected_model(manual_model, provider)
                debug_log.info(f"Manual model configuration completed", provider=provider, model_name=model_name)
            
            # Exit manual entry mode
            self.setup_active = False
            self.setup_data = {}
            
        except Exception as e:
            self.chat_area.add_message(f"❌ **Error with manual model entry**: {str(e)}", is_user=False)
    
    def action_clear_chat(self) -> None:
        """Clear the chat."""
        self.chat_area.clear_messages()
        self.chat_area.add_message("Chat cleared.", is_user=False)
    
    def action_quit(self) -> None:
        """Quit the application."""
        self._cleanup()
        self.exit()
    
    def _cleanup(self):
        """Clean up resources before exiting."""
        try:
            # Close storage manager first (synchronous)
            if self.storage_manager:
                try:
                    self.storage_manager.close()
                except:
                    pass
            
            # For TinyAgent cleanup, don't try to handle async operations
            # in sync context - this causes threading issues
            if self.tiny_code_agent:
                try:
                    # Just set to None, let garbage collection handle it
                    # Async cleanup will be handled by on_unmount if needed
                    self.tiny_code_agent = None
                except:
                    pass
                
        except Exception as e:
            # Don't let cleanup errors prevent exit
            pass
    
    async def _async_cleanup(self):
        """Async cleanup of resources."""
        try:
            # Close TinyAgent resources asynchronously
            if hasattr(self, 'tiny_code_agent') and self.tiny_code_agent:
                try:
                    await self.tiny_code_agent.close()
                except Exception:
                    # Ignore cleanup errors
                    pass
            
            # Close storage manager if it exists separately
            if hasattr(self, 'storage_manager') and self.storage_manager:
                try:
                    if hasattr(self.storage_manager, 'close_async'):
                        await self.storage_manager.close_async()
                    else:
                        self.storage_manager.close()
                except Exception:
                    # Ignore cleanup errors
                    pass
                
        except Exception as e:
            # Don't let cleanup errors prevent exit
            pass
    
    async def on_unmount(self):
        """Clean up when app is unmounting."""
        await self._async_cleanup()
        # Note: App class doesn't have on_unmount method, so we don't call super()
    
    def exit(self, return_code: int = 0, message: str = None):
        """Override exit to ensure cleanup."""
        try:
            # Simple cleanup without async complications
            if hasattr(self, 'storage_manager') and self.storage_manager:
                try:
                    self.storage_manager.close()
                except:
                    pass
            # Don't try to cleanup TinyAgent synchronously - causes threading issues
        except:
            pass
        return super().exit(return_code, message)
    
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
        
        # Reset footer stats since conversation is cleared
        if self.dynamic_footer:
            self.dynamic_footer.reset_usage_stats()
        
        # Update footer hint (no tool calls after clearing)
        self._update_footer_hint()
        
        # Focus the input
        if self.chat_input:
            self.chat_input.focus_input()
    
    def action_toggle_tool_expansion(self) -> None:
        """Toggle tool call expansion for all messages in the conversation."""
        # Toggle the global state
        self.tool_calls_expanded = not self.tool_calls_expanded
        
        # Refresh all message widgets to update their tool call display
        if self.chat_area:
            self.chat_area.refresh_tool_call_display(self.tool_calls_expanded)
            
            # Show a brief notification about the state change
            state_text = "expanded" if self.tool_calls_expanded else "collapsed"
            self.notify(f"Tool calls {state_text}", timeout=2)
    
    def action_show_history(self) -> None:
        """Show conversation history (F1 or Ctrl+Shift+H)."""
        self.run_worker(self._handle_history_command())
    
    def action_copy_selection(self) -> None:
        """Copy selected text to clipboard (F2 or F3)."""
        selected_text = self._get_selected_text()
        if selected_text:
            self._copy_to_clipboard_hybrid(selected_text)
            self.notify("Text copied to clipboard", timeout=1)
        else:
            self.notify("No text to copy", severity="warning", timeout=1)
    
    def action_toggle_selection_mode(self) -> None:
        """Exit ALL widgets from selection mode (Ctrl+S = global exit)."""
        from .widgets.chat_area import MessageWidget
        
        # Simple: Exit ALL selection modes
        if self.chat_area and self.chat_area.messages:
            selection_count = 0
            for msg in self.chat_area.messages:
                if isinstance(msg, MessageWidget) and msg.is_in_selection_mode:
                    msg._exit_selection_mode()
                    selection_count += 1
            
            if selection_count > 0:
                self.notify(f"Exited selection mode on {selection_count} message(s)", timeout=2)
                # Ensure footer is updated
                if self.dynamic_footer:
                    self.dynamic_footer.set_selection_mode(False)
            else:
                self.notify("No messages in selection mode", severity="information", timeout=1)
        else:
            self.notify("No messages available", severity="warning", timeout=1)
    
    def _get_selected_text(self) -> str:
        """Get currently selected text from the chat area."""
        if not self.chat_area:
            return ""
        
        try:
            # Strategy 1: Check for selected text in MessageWidgets in selection mode
            from .widgets.chat_area import MessageWidget
            
            # Walk through all message widgets to find any with selected text
            for widget in self.walk_children():
                if isinstance(widget, MessageWidget):
                    if widget.is_in_selection_mode and widget.has_selection():
                        selected_text = widget.get_selected_text()
                        self.debug_log.logger.debug(f"COPY_SELECTION: found_message_selection | text_length={len(selected_text)}")
                        return selected_text
            
            # Strategy 2: Check for selected text in any TextArea widget (including input area)
            from textual.widgets import TextArea
            for widget in self.walk_children():
                if isinstance(widget, TextArea) and widget.selected_text:
                    self.debug_log.logger.debug(f"COPY_SELECTION: found_textarea_selection | text_length={len(widget.selected_text)}")
                    return widget.selected_text
            
            # Strategy 3: Check focused widget specifically
            focused_widget = self.focused
            if isinstance(focused_widget, MessageWidget) and focused_widget.is_in_selection_mode and focused_widget.has_selection():
                selected_text = focused_widget.get_selected_text()
                self.debug_log.logger.debug(f"COPY_SELECTION: focused_message_selection | text_length={len(selected_text)}")
                return selected_text
            elif isinstance(focused_widget, TextArea) and hasattr(focused_widget, 'selected_text') and focused_widget.selected_text:
                self.debug_log.logger.debug(f"COPY_SELECTION: focused_textarea_selection | text_length={len(focused_widget.selected_text)}")
                return focused_widget.selected_text
            
            # Strategy 4: Get latest message as fallback ONLY if no selection exists anywhere
            # This is the last resort when user presses F2 without selecting anything
            latest_text = self.chat_area.get_latest_message_text()
            if latest_text:
                self.debug_log.logger.debug(f"COPY_SELECTION: latest_message_fallback | text_length={len(latest_text)}")
                return latest_text
            
        except Exception as e:
            # Log error but don't crash
            self.debug_log.logger.debug(f"COPY_SELECTION: error | {str(e)}")
        
        return ""
    
    def _copy_to_clipboard_hybrid(self, text: str) -> None:
        """Copy text to clipboard using hybrid approach (pyperclip + OSC 52 backup)."""
        if not text:
            return
            
        success = False
        error_messages = []
        
        # Strategy 1: Try pyperclip first (more reliable across environments)
        try:
            import pyperclip
            pyperclip.copy(text)
            success = True
            self.debug_log.logger.debug(f"CLIPBOARD: pyperclip_success | text_length={len(text)}")
        except ImportError:
            error_messages.append("pyperclip not available")
            self.debug_log.logger.debug("CLIPBOARD: pyperclip_missing")
        except Exception as e:
            error_messages.append(f"pyperclip failed: {str(e)}")
            self.debug_log.logger.debug(f"CLIPBOARD: pyperclip_failed | {str(e)}")
        
        # Strategy 2: Try Textual's built-in clipboard (OSC 52) as backup
        if not success:
            try:
                # Only try OSC 52 if we have proper Textual app context
                if hasattr(self, '_screen_stack') and self._screen_stack:
                    super().copy_to_clipboard(text)
                    success = True
                    self.debug_log.logger.debug(f"CLIPBOARD: osc52_success | text_length={len(text)}")
                else:
                    error_messages.append("OSC 52 unavailable (no screen context)")
                    self.debug_log.logger.debug("CLIPBOARD: osc52_skipped | no_screen_context")
            except Exception as e:
                error_messages.append(f"OSC 52 failed: {str(e)}")
                self.debug_log.logger.debug(f"CLIPBOARD: osc52_failed | {str(e)}")
        
        # Handle complete failure
        if not success:
            if "pyperclip not available" in error_messages:
                self.notify("Install clipboard support: pip install juno-agent[clipboard]", 
                          severity="error", timeout=3)
            else:
                self.notify(f"Clipboard error: {'; '.join(error_messages)}", 
                          severity="error", timeout=3)
        else:
            # Also try OSC 52 as additional backup (some terminals support both)
            if success and "pyperclip_success" in str(self.debug_log.logger.handlers):
                try:
                    if hasattr(self, '_screen_stack') and self._screen_stack:
                        super().copy_to_clipboard(text)
                        self.debug_log.logger.debug("CLIPBOARD: osc52_backup_success")
                except:
                    pass  # Ignore OSC 52 backup failures
    
    def _create_welcome_message(self) -> str:
        """Create a welcome message with proper formatting for Textual."""
        # Use the centralized welcome message builder
        welcome_builder = WelcomeMessageBuilder(self.config_manager, self.system_status)
        return welcome_builder.build_welcome_text(use_rich_formatting=True)
    
    def _refresh_welcome_message(self) -> None:
        """Refresh the welcome message in the chat area with updated model information."""
        try:
            # Generate new welcome message with current configuration
            updated_welcome = self._create_welcome_message()
            
            # Add a fresh welcome message to show updated model info
            self.chat_area.add_message("🔄 **Configuration Updated**", is_user=False)
            self.chat_area.add_message(updated_welcome, is_user=False)
            
            self.debug_log.info("Welcome screen refreshed with updated model information")
            
        except Exception as e:
            self.debug_log.error(f"Error refreshing welcome message: {str(e)}")
    
    
    def _update_footer_hint(self):
        """Update the footer hint based on whether tool calls are present."""
        if not self.dynamic_footer or not self.chat_area:
            return
        
        # Check if any messages have tool calls
        has_tool_calls = False
        for message in self.chat_area.messages:
            if not message.is_user and (message.tool_calls or message.pending_tool_calls):
                has_tool_calls = True
                break
        
        self.dynamic_footer.set_tool_calls_present(has_tool_calls)
        
        # Update token and cost information
        self._update_footer_stats()
    
    def _update_footer_stats(self):
        """Update the footer with current token usage and cost statistics."""
        if not self.dynamic_footer:
            return
        
        # Get token and cost information
        tokens, cost = self._get_current_usage_stats()
        
        # Update footer with current stats
        self.dynamic_footer.update_usage_stats(tokens, cost)
        
        # Set agent running status based on whether we have an active agent
        is_running = bool(self.tiny_code_agent and hasattr(self.tiny_code_agent, 'agent') and self.tiny_code_agent.agent)
        self.dynamic_footer.set_agent_running(is_running)
    
    def _get_current_usage_stats(self):
        """Get current token usage and cost from the agent.
        
        Returns:
            tuple: (total_tokens, total_cost)
        """
        if not self.tiny_code_agent or not hasattr(self.tiny_code_agent, 'agent') or not self.tiny_code_agent.agent:
            return 0, 0.0
        
        try:
            agent = self.tiny_code_agent.agent
            
            # Look for TokenTracker in callbacks (same logic as _handle_cost_command)
            if hasattr(agent, 'callbacks'):
                for callback in agent.callbacks:
                    callback_type = type(callback).__name__
                    
                    if callback_type == 'TokenTracker' or hasattr(callback, 'get_total_usage'):
                        try:
                            if hasattr(callback, 'get_total_usage'):
                                stats = callback.get_total_usage()
                                
                                # Check for child trackers and aggregate their costs
                                if hasattr(callback, 'child_trackers') and callback.child_trackers:
                                    child_tokens = 0
                                    child_cost = 0.0
                                    
                                    for child_tracker in callback.child_trackers:
                                        if hasattr(child_tracker, 'get_total_usage'):
                                            child_stats = child_tracker.get_total_usage()
                                            child_tokens += child_stats.total_tokens
                                            child_cost += child_stats.cost
                                    
                                    # Return aggregated stats
                                    return stats.total_tokens + child_tokens, stats.cost + child_cost
                                else:
                                    # Return main stats only
                                    return stats.total_tokens, stats.cost
                        except Exception:
                            continue
                    # Fallback: check for any callback with get_usage_stats method
                    elif hasattr(callback, 'get_usage_stats'):
                        try:
                            stats = callback.get_usage_stats()
                            return getattr(stats, 'total_tokens', 0), getattr(stats, 'cost', 0.0)
                        except Exception:
                            continue
            
            return 0, 0.0
        except Exception:
            return 0, 0.0
    
    def _periodic_footer_update(self) -> None:
        """Periodic callback to update footer stats in real-time."""
        self._update_footer_stats()


# Maintain backward compatibility with the simple app
class SimpleChatApp(PyWizardTUIApp):
    """Backward compatible simple chat app (goes directly to chat)."""
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__(config_manager, show_welcome=False)