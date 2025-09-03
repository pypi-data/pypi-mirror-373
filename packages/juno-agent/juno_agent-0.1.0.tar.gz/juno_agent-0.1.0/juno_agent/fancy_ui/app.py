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
from .widgets.file_autocomplete import FileAutocomplete
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
from .handlers.setup_handler import SetupHandler
from .handlers.model_handler import ModelHandler
from .handlers.chat_handler import ChatHandler
from .handlers.app_lifecycle import AppLifecycleHandler


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
        self.file_autocomplete_widget = None
        
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
        
        # Setup state management (shared between handlers)
        self.setup_active = False
        self.setup_data = {}
        
        # Initialize handlers
        self.setup_handler = None
        self.model_handler = None
        self.chat_handler = None
        self.app_lifecycle_handler = None
        
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
                # Use slug for display if available, otherwise fallback to model_name
                if config.agent_config.model_slug:
                    model_display = config.agent_config.model_slug
                else:
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
        
        # File autocomplete widget (initially hidden) - at app level like model selection
        self.file_autocomplete_widget = FileAutocomplete()
        yield self.file_autocomplete_widget
    
    async def on_mount(self) -> None:
        """Initialize the app after mounting."""
        # Initialize all handlers first so we can create the welcome message
        
        # Initialize setup handler
        self.setup_handler = SetupHandler(
            app=self,
            config_manager=self.config_manager,
            chat_area=self.chat_area,
            storage_manager=self.storage_manager
        )
        
        # Initialize model handler
        self.model_handler = ModelHandler(
            app=self,
            config_manager=self.config_manager,
            chat_area=self.chat_area,
            model_selection_menu=self.model_selection_menu,
            api_key_prompt=self.api_key_prompt,
            global_default_menu=self.global_default_menu,
            yes_no_menu=self.yes_no_menu,
            chat_input=self.chat_input
        )
        
        # Initialize chat handler
        self.chat_handler = ChatHandler(
            app=self,
            config_manager=self.config_manager,
            chat_area=self.chat_area,
            storage_manager=self.storage_manager,
            setup_handler=self.setup_handler,
            model_handler=self.model_handler
        )
        
        # Initialize app lifecycle handler
        self.app_lifecycle_handler = AppLifecycleHandler(
            app=self,
            config_manager=self.config_manager,
            chat_area=self.chat_area,
            dynamic_footer=self.dynamic_footer,
            storage_manager=self.storage_manager
        )
        
        # Connect file autocomplete widget to chat input
        if self.chat_input and self.file_autocomplete_widget:
            self.chat_input.file_autocomplete_widget = self.file_autocomplete_widget
        
        # Add comprehensive JUNO AI CLI welcome message FIRST (after handlers are initialized)
        welcome_message = self.app_lifecycle_handler._create_welcome_message()
        self.chat_area.add_message(welcome_message, is_user=False)
        
        # Initialize TinyAgent after welcome message
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
            
            # Add AI Assistant ready message SECOND (after JUNO AI CLI welcome)
            self.chat_area.add_message("🤖 **AI Assistant ready!** Type your questions or commands.", is_user=False)
            
            # Update footer to show agent is running
            if self.app_lifecycle_handler:
                self.app_lifecycle_handler._update_footer_stats()
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
            self.set_timer(0.5, self.setup_handler.auto_start_setup_wizard)
        elif self.verify_only_mode:
            # Start verification only mode immediately
            self.debug_log.debug(f"Verify-only mode enabled, calling verification directly")
            self.call_after_refresh(self.setup_handler.auto_start_verification_only)
        elif self.agentic_resolver_mode:
            # Start agentic resolver mode (for --docs-only)
            self.debug_log.debug(f"Agentic resolver mode enabled, calling agentic dependency resolver directly")
            self.set_timer(0.5, self.setup_handler.auto_start_agentic_resolver)
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
            if self.app_lifecycle_handler:
                self.app_lifecycle_handler._update_footer_stats()
            
        except Exception as e:
            self.debug_log.error(f"Error reinitializing agent: {str(e)}")
            # Re-raise the exception so it can be handled by the caller
            raise e
    
    async def on_history_menu_session_selected(self, message: HistoryMenu.SessionSelected) -> None:
        """Handle session selection from history menu."""
        await self.chat_handler.handle_history_menu_session_selected(message.session)
    
    async def on_history_menu_menu_closed(self, message: HistoryMenu.MenuClosed) -> None:
        """Handle history menu being closed."""
        await self.chat_handler.handle_history_menu_menu_closed()
    
    async def on_history_autocomplete_session_selected(self, message: HistoryAutocomplete.SessionSelected) -> None:
        """Handle session selection from history autocomplete dropdown."""
        await self.chat_handler.handle_history_autocomplete_session_selected(message.session)
    
    async def on_model_selection_menu_model_selected(self, message: ModelSelectionMenu.ModelSelected) -> None:
        """Handle model selection from the model selection menu."""
        await self.model_handler.handle_model_selected(message.model, message.provider)
    
    async def on_model_selection_menu_manual_entry_requested(self, message: ModelSelectionMenu.ManualEntryRequested) -> None:
        """Handle manual model entry request."""
        await self.model_handler.handle_manual_model_entry()
    
    async def on_model_selection_menu_menu_closed(self, message: ModelSelectionMenu.MenuClosed) -> None:
        """Handle model selection menu being closed."""
        self.chat_area.add_message("ℹ️ **Model selection canceled** - Current model unchanged.", is_user=False)
        if self.chat_input:
            self.chat_input.focus_input()
    
    async def on_api_key_prompt_api_key_entered(self, message: APIKeyPrompt.APIKeyEntered) -> None:
        """Handle API key being entered."""
        debug_log = self.debug_log
        debug_log.debug(f"APIKeyPrompt.APIKeyEntered message received", provider=message.provider, has_key=bool(message.api_key))
        await self.model_handler.handle_api_key_entered(message.api_key, message.provider)
    
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
        await self.model_handler.handle_global_default_selection(message.set_global)
    
    async def on_global_default_menu_menu_closed(self, message: GlobalDefaultMenu.MenuClosed) -> None:
        """Handle global default menu being closed without selection."""
        # Default to local-only if user cancels
        await self.model_handler.handle_global_default_selection(False)
    
    async def on_yes_no_menu_yes_no_selected(self, message: YesNoMenu.YesNoSelected) -> None:
        """Handle Yes/No selection from menu."""
        await self.model_handler.handle_yes_no_selection(message.selected_yes, message.context)
    
    async def on_yes_no_menu_menu_closed(self, message: YesNoMenu.MenuClosed) -> None:
        """Handle Yes/No menu being closed without selection."""
        await self.model_handler.handle_yes_no_selection(False, message.context)
    
    async def on_base_selection_menu_option_selected(self, message: BaseSelectionMenu.OptionSelected) -> None:
        """Handle IDE selection from IDESelectionMenu."""
        await self.chat_handler.handle_base_selection_menu_option_selected(message.value)
    
    async def on_base_selection_menu_selection_cancelled(self, message: BaseSelectionMenu.SelectionCancelled) -> None:
        """Handle IDE selection cancellation."""
        await self.chat_handler.handle_base_selection_menu_selection_cancelled()
    
    def on_file_autocomplete_file_selected(self, message) -> None:
        """Handle file selection from file autocomplete - forward to chat input."""
        if self.chat_input:
            # Forward the message to chat input for handling
            self.chat_input.on_file_autocomplete_file_selected(message)
    
    def on_key(self, event: events.Key) -> None:
        """Handle global key events for the application."""
        # Handle Escape key for agent cancellation
        if event.key == "escape":
            # Safety check: ensure chat_handler is initialized
            if hasattr(self, 'chat_handler') and self.chat_handler and hasattr(self.chat_handler, 'agent_processing') and self.chat_handler.agent_processing:
                # Cancel agent processing if running
                if self.chat_handler.cancel_agent_processing():
                    debug_logger.log_event("escape_key_cancelled_agent")
                    return
                    
        # Route key events to HistoryMenu when it's visible and focused
        # History menu now handles keys automatically through BINDINGS
        # No manual forwarding needed
    
    
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
        if self.app_lifecycle_handler:
            self.app_lifecycle_handler._update_footer_hint()
    
    async def on_chat_input_submit(self, message: ChatInput.Submit) -> None:
        """Handle chat input submission."""
        user_message = message.content.strip()
        if not user_message:
            return
            
        # Add user message to chat
        self.chat_area.add_message(user_message, is_user=True)
        
        # Check if we're in setup mode
        if self.setup_handler and self.setup_handler.setup_active:
            await self.setup_handler.handle_setup_input(user_message)
        elif self.setup_active and hasattr(self, 'setup_data') and self.setup_data.get('mode') == 'manual_model_entry':
            # Handle model manual entry input
            await self.model_handler.handle_manual_model_input(user_message)
        elif self.setup_active and hasattr(self, 'setup_data'):
            # Handle other model configuration inputs
            await self.model_handler.handle_model_config_input(user_message)
        else:
            # Process the message normally
            if user_message.startswith("/"):
                # Handle commands via chat handler
                await self.chat_handler.handle_command(user_message)
            else:
                # Handle regular chat via chat handler
                await self.chat_handler.handle_chat_message(user_message)
    
    
    
    
    
    
    
    
    def action_clear_chat(self) -> None:
        """Clear the chat."""
        if self.app_lifecycle_handler:
            self.app_lifecycle_handler.clear_chat()
    
    def action_quit(self) -> None:
        """Quit the application."""
        if self.app_lifecycle_handler:
            self.app_lifecycle_handler.quit_app()
        else:
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
        if self.app_lifecycle_handler:
            # Run the async new_chat method using a worker to avoid blocking the UI
            self.run_worker(self.app_lifecycle_handler.new_chat())
    
    def action_toggle_tool_expansion(self) -> None:
        """Toggle tool call expansion for all messages in the conversation."""
        if self.app_lifecycle_handler:
            self.app_lifecycle_handler.toggle_tool_expansion()
    
    def action_show_history(self) -> None:
        """Show conversation history (F1 or Ctrl+Shift+H)."""
        if self.app_lifecycle_handler:
            self.app_lifecycle_handler.show_history()
    
    def action_copy_selection(self) -> None:
        """Copy selected text to clipboard (F2 or F3)."""
        if self.app_lifecycle_handler:
            self.app_lifecycle_handler.copy_selection()
    
    def action_toggle_selection_mode(self) -> None:
        """Exit ALL widgets from selection mode (Ctrl+S = global exit)."""
        if self.app_lifecycle_handler:
            self.app_lifecycle_handler.toggle_selection_mode()
    
    def _periodic_footer_update(self) -> None:
        """Periodic callback to update footer stats in real-time."""
        if self.app_lifecycle_handler:
            self.app_lifecycle_handler._periodic_footer_update()


# Maintain backward compatibility with the simple app
class SimpleChatApp(PyWizardTUIApp):
    """Backward compatible simple chat app (goes directly to chat)."""
    
    def __init__(self, config_manager: ConfigManager):
        super().__init__(config_manager, show_welcome=False)