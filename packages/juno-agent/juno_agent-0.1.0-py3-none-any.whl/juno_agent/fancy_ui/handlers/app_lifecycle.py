"""Application lifecycle and action methods handler.

This module contains all application lifecycle management, action methods,
UI state utilities, and footer update functionality extracted from PyWizardTUIApp.
"""

import asyncio
from pathlib import Path
from typing import Optional, Tuple

from ..utils.welcome_message_builder import WelcomeMessageBuilder
from ...debug_logger import debug_logger


class AppLifecycleHandler:
    """Handler for application lifecycle, actions, and UI state management."""
    
    def __init__(self, app, config_manager, chat_area, dynamic_footer, storage_manager):
        """Initialize the AppLifecycleHandler.
        
        Args:
            app: Main PyWizardTUIApp instance
            config_manager: Configuration manager instance
            chat_area: Chat area widget
            dynamic_footer: Dynamic footer widget
            storage_manager: Storage manager for conversations
        """
        self.app = app
        self.config_manager = config_manager
        self.chat_area = chat_area
        self.dynamic_footer = dynamic_footer
        self.storage_manager = storage_manager
        self.debug_log = config_manager.create_debug_logger(debug=True)
        
        # Get system status from app (None safe for testing)
        self.system_status = app.system_status if app else None
    
    # ============================================================================
    # APPLICATION ACTIONS
    # ============================================================================
    
    def clear_chat(self) -> None:
        """Clear the chat (formerly action_clear_chat)."""
        self.chat_area.clear_messages()
        self.chat_area.add_message("Chat cleared.", is_user=False)
    
    def quit_app(self) -> None:
        """Quit the application (formerly action_quit)."""
        self._cleanup()
        self.app.exit()
    
    async def new_chat(self) -> None:
        """Reset the chat - clear messages and restart (formerly action_new_chat)."""
        if self.chat_area:
            self.chat_area.clear_messages()
            
            # Start new session with storage if available
            if self.app.tiny_code_agent:
                try:
                    # CRITICAL FIX: start_new_session is now async to properly reinitialize agent
                    session_id = await self.app.tiny_code_agent.start_new_session()
                    if session_id != "no_storage":
                        self.chat_area.add_message(
                            f"✨ **New chat started!** Session {session_id[:8]}... created. Conversation history cleared. How can I help you?",
                            is_user=False
                        )
                    else:
                        self.chat_area.add_message(
                            "✨ **New chat started!** Conversation history cleared. How can I help you?",
                            is_user=False
                        )
                except Exception as e:
                    print(f"[ERROR] new_chat: Failed to start new session: {e}")
                    self.chat_area.add_message(
                        "✨ **New chat started!** Conversation history cleared. How can I help you?",
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
        if self.app.chat_input:
            self.app.chat_input.focus_input()
    
    def toggle_tool_expansion(self) -> None:
        """Toggle tool call expansion for all messages in the conversation (formerly action_toggle_tool_expansion)."""
        # Toggle the global state
        self.app.tool_calls_expanded = not self.app.tool_calls_expanded
        
        # Refresh all message widgets to update their tool call display
        if self.chat_area:
            self.chat_area.refresh_tool_call_display(self.app.tool_calls_expanded)
            
            # Show a brief notification about the state change
            state_text = "expanded" if self.app.tool_calls_expanded else "collapsed"
            self.app.notify(f"Tool calls {state_text}", timeout=2)
    
    def show_history(self) -> None:
        """Show conversation history (formerly action_show_history)."""
        self.app.run_worker(self.app.chat_handler.handle_history_command())
    
    def copy_selection(self) -> None:
        """Copy selected text to clipboard (formerly action_copy_selection)."""
        selected_text = self._get_selected_text()
        if selected_text:
            self._copy_to_clipboard_hybrid(selected_text)
            self.app.notify("Text copied to clipboard", timeout=1)
        else:
            self.app.notify("No text to copy", severity="warning", timeout=1)
    
    def toggle_selection_mode(self) -> None:
        """Exit ALL widgets from selection mode (formerly action_toggle_selection_mode)."""
        from ..widgets.chat_area import MessageWidget
        
        # Simple: Exit ALL selection modes
        if self.chat_area and self.chat_area.messages:
            selection_count = 0
            for msg in self.chat_area.messages:
                if isinstance(msg, MessageWidget) and msg.is_in_selection_mode:
                    msg._exit_selection_mode()
                    selection_count += 1
            
            if selection_count > 0:
                self.app.notify(f"Exited selection mode on {selection_count} message(s)", timeout=2)
                # Ensure footer is updated
                if self.dynamic_footer:
                    self.dynamic_footer.set_selection_mode(False)
            else:
                self.app.notify("No messages in selection mode", severity="information", timeout=1)
        else:
            self.app.notify("No messages available", severity="warning", timeout=1)
    
    # ============================================================================
    # LIFECYCLE MANAGEMENT
    # ============================================================================
    
    async def initialize_agent(self) -> None:
        """Initialize or reinitialize the TinyAgent with current configuration."""
        try:
            from ...tiny_agent import TinyCodeAgentChat
            
            self.debug_log.debug("Reinitializing TinyCodeAgentChat with updated configuration")
            
            # Create new TinyCodeAgentChat instance with updated config
            self.app.tiny_code_agent = TinyCodeAgentChat(
                self.config_manager, 
                debug=False,
                ui_callback=self.ui_tool_update_callback,
                storage_manager=self.storage_manager
            )
            
            # Initialize the agent
            await self.app.tiny_code_agent.initialize_agent()
            self.debug_log.info("TinyCodeAgentChat reinitialized successfully")
            
            # Update footer to show agent is running
            self._update_footer_stats()
            
        except Exception as e:
            self.debug_log.error(f"Error reinitializing agent: {str(e)}")
            # Re-raise the exception so it can be handled by the caller
            raise e
    
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
            if self.app.tiny_code_agent:
                try:
                    # Just set to None, let garbage collection handle it
                    # Async cleanup will be handled by on_unmount if needed
                    self.app.tiny_code_agent = None
                except:
                    pass
                
        except Exception as e:
            # Don't let cleanup errors prevent exit
            pass
    
    async def _async_cleanup(self):
        """Async cleanup of resources."""
        try:
            # Close TinyAgent resources asynchronously
            if hasattr(self.app, 'tiny_code_agent') and self.app.tiny_code_agent:
                try:
                    await self.app.tiny_code_agent.close()
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
    
    def exit_cleanup(self, return_code: int = 0, message: str = None):
        """Handle cleanup during exit (used by app.exit override)."""
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
    
    def exit_app_override(self, return_code: int = 0, message: str = None):
        """Override exit method to ensure cleanup before app exit."""
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
        
        # Return the parameters for the main app to call super().exit()
        return return_code, message
    
    # ============================================================================
    # UI STATE UTILITIES
    # ============================================================================
    
    def _get_selected_text(self) -> str:
        """Get currently selected text from the chat area."""
        if not self.chat_area:
            return ""
        
        try:
            # Strategy 1: Check for selected text in MessageWidgets in selection mode
            from ..widgets.chat_area import MessageWidget
            
            # Walk through all message widgets to find any with selected text
            for widget in self.app.walk_children():
                if isinstance(widget, MessageWidget):
                    if widget.is_in_selection_mode and widget.has_selection():
                        selected_text = widget.get_selected_text()
                        self.debug_log.logger.debug(f"COPY_SELECTION: found_message_selection | text_length={len(selected_text)}")
                        return selected_text
            
            # Strategy 2: Check for selected text in any TextArea widget (including input area)
            from textual.widgets import TextArea
            for widget in self.app.walk_children():
                if isinstance(widget, TextArea) and widget.selected_text:
                    self.debug_log.logger.debug(f"COPY_SELECTION: found_textarea_selection | text_length={len(widget.selected_text)}")
                    return widget.selected_text
            
            # Strategy 3: Check focused widget specifically
            focused_widget = self.app.focused
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
                if hasattr(self.app, '_screen_stack') and self.app._screen_stack:
                    self.app.copy_to_clipboard(text)
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
                self.app.notify("Install clipboard support: pip install juno-agent[clipboard]", 
                          severity="error", timeout=3)
            else:
                self.app.notify(f"Clipboard error: {'; '.join(error_messages)}", 
                          severity="error", timeout=3)
        else:
            # Also try OSC 52 as additional backup (some terminals support both)
            if success and "pyperclip_success" in str(self.debug_log.logger.handlers):
                try:
                    if hasattr(self.app, '_screen_stack') and self.app._screen_stack:
                        self.app.copy_to_clipboard(text)
                        self.debug_log.logger.debug("CLIPBOARD: osc52_backup_success")
                except:
                    pass  # Ignore OSC 52 backup failures
    
    # ============================================================================
    # WELCOME MESSAGE METHODS
    # ============================================================================
    
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
    
    # ============================================================================
    # FOOTER UPDATE METHODS
    # ============================================================================
    
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
        is_running = bool(self.app.tiny_code_agent and hasattr(self.app.tiny_code_agent, 'agent') and self.app.tiny_code_agent.agent)
        self.dynamic_footer.set_agent_running(is_running)
    
    def _get_current_usage_stats(self) -> Tuple[int, float]:
        """Get current token usage and cost from the agent.
        
        Returns:
            tuple: (total_tokens, total_cost)
        """
        if not self.app.tiny_code_agent or not hasattr(self.app.tiny_code_agent, 'agent') or not self.app.tiny_code_agent.agent:
            return 0, 0.0
        
        try:
            agent = self.app.tiny_code_agent.agent
            
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
    
    # ============================================================================
    # TOOL UPDATE CALLBACK
    # ============================================================================
    
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
                             app_id=hex(id(self.app)),
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