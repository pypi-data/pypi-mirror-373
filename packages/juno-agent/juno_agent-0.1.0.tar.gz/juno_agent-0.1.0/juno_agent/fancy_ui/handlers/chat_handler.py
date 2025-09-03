"""Chat and event handling functionality for PyWizardTUIApp.

This module contains all chat processing, command handling, event handling, and 
conversation management functionality extracted from the main app.py file.
"""

import time
import asyncio
from typing import List, Dict, Any, Optional

from ...debug_logger import debug_logger


class ChatHandler:
    """Handler for chat messages, commands, events, and conversation management."""
    
    def __init__(self, app, config_manager, chat_area, storage_manager, setup_handler, model_handler):
        """Initialize the chat handler.
        
        Args:
            app: Main PyWizardTUIApp instance
            config_manager: Configuration manager instance
            chat_area: ChatArea widget instance
            storage_manager: AsyncConversationStorageManager instance
            setup_handler: SetupHandler instance
            model_handler: ModelHandler instance
        """
        self.app = app
        self.config_manager = config_manager
        self.chat_area = chat_area
        self.storage_manager = storage_manager
        self.setup_handler = setup_handler
        self.model_handler = model_handler
        self.debug_log = config_manager.create_debug_logger(debug=True)
        
        # Agent execution state for UI responsiveness and cancellation
        self.agent_processing = False
        self.thinking_msg = None
        self.current_worker = None
    
    async def handle_command(self, command: str) -> None:
        """Handle slash commands.
        
        This was formerly _handle_command in the main app.
        """
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
• **Escape** - Cancel agent processing (if running) or quit application
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
            await self.handle_cost_command()
        
        elif cmd in ["/new-chat", "/reset", "/clear"]:
            # Clear conversation history
            self.chat_area.clear_messages()
            if cmd == "/new-chat":
                self.chat_area.add_message("✨ **New chat started!** Conversation history cleared and context freed up. How can I help you?", is_user=False)
            else:
                self.chat_area.add_message("🧹 **Chat reset!** Conversation history cleared. How can I help you?", is_user=False)
            
            # Reset footer stats since conversation is cleared
            if self.app.dynamic_footer:
                self.app.dynamic_footer.reset_usage_stats()
        
        elif cmd == "/compact":
            # Compact conversation using TinyCodeAgent
            # Pass any additional arguments as summarization instructions
            await self.handle_compact_command(args)
        
        elif cmd == "/setup":
            # Run setup wizard
            await self.setup_handler.handle_setup_command()
        
        elif cmd == "/history":
            # View and manage conversation history
            await self.handle_history_command()
        
        elif cmd == "/model":
            # Configure AI model
            await self.model_handler.handle_model_command()
        
        elif cmd == "/quit":
            self.app.exit()
        
        else:
            self.chat_area.add_message(f"❓ Unknown command: `{cmd}`. Type `/help` for available commands or `/` for autocomplete.", is_user=False)
    
    async def handle_chat_message(self, message: str) -> None:
        """Handle regular chat messages with non-blocking execution and cancellation support.
        
        This was formerly _handle_chat_message in the main app.
        Now uses app.run_worker for proper async handling to maintain UI responsiveness.
        """
        if self.agent_processing:
            # Agent is already processing, ignore new messages
            self.chat_area.add_message("⚠️ **Agent is busy processing**. Please wait or press **Escape** to cancel.", is_user=False)
            return
            
        if self.app.tiny_code_agent:
            # Show thinking indicator immediately
            self.thinking_msg = self.chat_area.add_message("🤖 Thinking... (Press **Escape** to cancel)", is_user=False)
            
            # Start the worker using app.run_worker
            self.current_worker = self.app.run_worker(
                self._process_agent_message(message),
                name="agent_processing",
                description="Processing AI agent message"
            )
        else:
            # Check what's missing and provide helpful guidance
            config = self.config_manager.load_config()
            if not self.config_manager.has_api_key():
                self.chat_area.add_message("🔧 **AI Assistant requires API key**\n\nPlease set your API key with `/apikey` command to start chatting.", is_user=False)
            elif not self.config_manager.is_model_configured():
                self.chat_area.add_message("🔧 **AI Assistant requires model configuration**\n\nPlease configure your AI model with `/model` command to start chatting.", is_user=False)
            else:
                self.chat_area.add_message("🔧 **AI Assistant not available**\n\nThere was an error initializing the AI assistant. Try the `/model` command to reconfigure.", is_user=False)

    async def _process_agent_message(self, message: str) -> str:
        """Async function to process agent message.
        
        This runs as a worker to maintain UI responsiveness.
        """
        try:
            self.agent_processing = True
            
            # Process the message asynchronously
            response = await self.app.tiny_code_agent.process_chat_message(message)
            
            # Update UI with response
            self._update_agent_response(response)
            
            return response
            
        except asyncio.CancelledError:
            # Handle cancellation
            self._handle_agent_cancellation()
            raise
        except Exception as e:
            # Handle errors
            self._handle_agent_error(str(e))
            raise
        finally:
            self.agent_processing = False
            self.current_worker = None
    
    def _update_agent_response(self, response: str):
        """Update the thinking message with the final response."""
        try:
            # Instead of removing and creating new message, update the existing one
            # The thinking message already has tool calls attached, so we just update its content
            if hasattr(self, 'thinking_msg') and self.thinking_msg and self.chat_area.current_agent_message == self.thinking_msg:
                # Update the thinking message content to the final response
                self.thinking_msg.content = response
                self.thinking_msg._update_with_tool_calls()  # This includes both content and tool calls
                debug_logger.log_event("updated_thinking_message_to_final_response",
                                     final_response_length=len(response),
                                     tool_calls_count=len(self.thinking_msg.tool_calls),
                                     pending_tool_calls_count=len(self.thinking_msg.pending_tool_calls))
            else:
                # Fallback: remove thinking and add new message (preserve tool calls)
                if hasattr(self.chat_area, 'remove_last_message'):
                    self.chat_area.remove_last_message()
                agent_msg = self.chat_area.add_message(response, is_user=False)
                debug_logger.log_event("fallback_to_remove_and_add_message")
            
            # Update footer hint based on tool calls presence and refresh stats
            if self.app.app_lifecycle_handler:
                self.app.app_lifecycle_handler._update_footer_hint()
            
        except Exception as e:
            debug_logger.log_event("error_updating_agent_response", error=str(e))
    
    def _handle_agent_cancellation(self):
        """Handle agent processing cancellation."""
        try:
            if hasattr(self.chat_area, 'remove_last_message'):
                self.chat_area.remove_last_message()
            self.chat_area.add_message("🛑 **Agent processing cancelled**", is_user=False)
        except Exception as e:
            debug_logger.log_event("error_handling_cancellation", error=str(e))
    
    def _handle_agent_error(self, error_msg: str):
        """Handle agent processing error."""
        try:
            if hasattr(self.chat_area, 'remove_last_message'):
                self.chat_area.remove_last_message()
            self.chat_area.add_message(f"❌ Error: {error_msg}", is_user=False)
        except Exception as e:
            debug_logger.log_event("error_handling_agent_error", error=str(e))
    
    def cancel_agent_processing(self):
        """Cancel the current agent processing if running."""
        if self.current_worker and not self.current_worker.is_finished:
            debug_logger.log_event("cancelling_agent_processing", worker_name=getattr(self.current_worker, 'name', 'unknown'))
            self.current_worker.cancel()
            return True
        return False
    
    async def handle_cost_command(self) -> None:
        """Handle /cost command - show conversation cost and token usage.
        
        This was formerly _handle_cost_command in the main app.
        """
        if not self.app.tiny_code_agent or not hasattr(self.app.tiny_code_agent, 'agent') or not self.app.tiny_code_agent.agent:
            self.chat_area.add_message("❌ **No active TinyAgent session**\n\nCost tracking is only available when TinyAgent is initialized.", is_user=False)
            return
        
        try:
            # Get the agent instance
            agent = self.app.tiny_code_agent.agent
            
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
                    if hasattr(self.app.tiny_code_agent, 'conversation_history'):
                        for entry in self.app.tiny_code_agent.conversation_history:
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
    
    async def handle_compact_command(self, summarization_instructions: str = "") -> None:
        """Handle /compact command - compact conversation using TinyCodeAgent.
        
        This was formerly _handle_compact_command in the main app.
        
        Uses TinyAgent's compact() method which compacts the conversation AND updates the agent's context,
        unlike summarize() which only generates a summary without updating context.
        
        Args:
            summarization_instructions: Optional instructions for how to compact the conversation
        """
        if not self.app.tiny_code_agent or not hasattr(self.app.tiny_code_agent, 'agent') or not self.app.tiny_code_agent.agent:
            self.chat_area.add_message("❌ **No active TinyAgent session**\n\nConversation compacting requires TinyAgent to be initialized.\nPlease wait for TinyAgent to initialize or check your configuration.", is_user=False)
            return
        
        try:
            # Show processing message with custom instructions if provided
            if summarization_instructions.strip():
                processing_msg = self.chat_area.add_message(f"🗜️ **Compacting conversation history...**\n\nGenerating summary with custom instructions: *{summarization_instructions.strip()}*\n\nThis will preserve context while reducing tokens...", is_user=False)
            else:
                processing_msg = self.chat_area.add_message("🗜️ **Compacting conversation history...**\n\nGenerating summary to preserve context while reducing tokens...", is_user=False)
            
            # Use TinyAgent's compact method (preferred) or fallback to summarize
            agent = self.app.tiny_code_agent.agent
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
                if hasattr(self.app.tiny_code_agent, 'reset_conversation'):
                    self.app.tiny_code_agent.reset_conversation()
        
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
            self.app.app_lifecycle_handler._update_footer_hint()
    
    def _extract_first_two_paragraphs(self, text: str) -> str:
        """Extract the first two paragraphs from text for preview."""
        if not text:
            return ""
        
        # Split by double newlines to get paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        if len(paragraphs) >= 2:
            return '\n\n'.join(paragraphs[:2])
        elif len(paragraphs) == 1:
            # If only one paragraph, limit to 300 characters
            if len(paragraphs[0]) > 300:
                return paragraphs[0][:300] + "..."
            return paragraphs[0]
        else:
            # Fallback: limit to 300 characters
            return text[:300] + "..." if len(text) > 300 else text
    
    async def handle_history_command(self) -> None:
        """Handle /history command - show interactive session selection menu.
        
        This was formerly _handle_history_command in the main app.
        """
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
            if self.app.history_menu:
                self.app.history_menu.show(sessions)
            else:
                # Fallback to text display if menu not available
                self.chat_area.add_message("❌ **History menu not available**\n\nFalling back to text display...", is_user=False)
                await self.handle_history_command_fallback(sessions)
            
        except Exception as e:
            self.chat_area.add_message(f"❌ **Error retrieving history**: {str(e)}", is_user=False)
    
    async def handle_history_command_fallback(self, sessions: List[Dict[str, Any]]) -> None:
        """Fallback text-based history display.
        
        This was formerly _handle_history_command_fallback in the main app.
        """
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
    
    # Event handlers (delegate from main app event handlers)
    
    async def handle_history_menu_session_selected(self, session: Dict[str, Any]) -> None:
        """Handle session selection from history menu."""
        try:
            await self.load_conversation(session)
        except Exception as e:
            self.chat_area.add_message(f"❌ **Error loading conversation**: {str(e)}", is_user=False)
    
    async def handle_history_menu_menu_closed(self) -> None:
        """Handle history menu being closed."""
        if self.app.chat_input:
            self.app.chat_input.focus_input()
    
    async def handle_history_autocomplete_session_selected(self, session: Dict[str, Any]) -> None:
        """Handle session selection from history autocomplete dropdown."""
        try:
            await self.load_conversation(session)
        except Exception as e:
            self.chat_area.add_message(f"❌ **Error loading conversation**: {str(e)}", is_user=False)
    
    async def handle_base_selection_menu_option_selected(self, value: str) -> None:
        """Handle IDE selection from IDESelectionMenu."""
        if self.setup_handler and self.setup_handler.setup_active and hasattr(self.setup_handler, 'setup_data'):
            await self.setup_handler.handle_editor_selection(value)
    
    async def handle_base_selection_menu_selection_cancelled(self) -> None:
        """Handle IDE selection cancellation."""
        if self.setup_handler and self.setup_handler.setup_active:
            self.chat_area.add_message("IDE selection cancelled. Continuing with setup...", is_user=False)
            # Skip this step and continue
            self.setup_handler.setup_step += 1
            await self.setup_handler.start_enhanced_setup_step()
    
    # Conversation management methods
    
    async def load_conversation(self, session: Dict[str, Any]) -> None:
        """Load a conversation session and reconstruct the chat area.
        
        This was formerly _load_conversation in the main app.
        """
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
            messages = self.extract_messages_from_session(session_data)
            
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
            await self.reconstruct_messages(messages)
            
            # Restore agent session if possible
            await self.restore_agent_session(session_id, session_data)
            
            # Focus input for continuation
            if self.app.chat_input:
                self.app.chat_input.focus_input()
            
        except Exception as e:
            # Remove loading message if it exists
            if hasattr(self.chat_area, 'remove_last_message'):
                self.chat_area.remove_last_message()
            self.chat_area.add_message(f"❌ **Error loading conversation**: {str(e)}", is_user=False)
    
    def extract_messages_from_session(self, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract messages from session data structure.
        
        This was formerly _extract_messages_from_session in the main app.
        """
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
    
    async def reconstruct_messages(self, messages: List[Dict[str, Any]]) -> None:
        """Reconstruct conversation messages in the chat area using the same tool display system as live conversations.
        
        This was formerly _reconstruct_messages in the main app.
        """
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
                    tool_event_data = self.convert_tool_call_to_event(tool_call)
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
    
    def convert_tool_call_to_event(self, tool_call: dict) -> dict:
        """Convert a loaded tool call to the event format used by the live tool system.
        
        This was formerly _convert_tool_call_to_event in the main app.
        """
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
    
    async def restore_agent_session(self, session_id: str, session_data: Dict[str, Any]) -> None:
        """Restore the agent session with the loaded conversation.
        
        This was formerly _restore_agent_session in the main app.
        
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
                if self.app.tiny_code_agent and hasattr(self.app.tiny_code_agent, 'load_session'):
                    await self.app.tiny_code_agent.load_session(loaded_session_id)
                    print(f"[DEBUG] Agent session restored for {loaded_session_id} (fallback)")
                return
            
            # CRITICAL FIX: Recreate agent with correct session and user context
            if self.app.tiny_code_agent and hasattr(self.app.tiny_code_agent, 'recreate_with_session_context'):
                print(f"[DEBUG] _restore_agent_session: Recreating agent with session_id: {loaded_session_id}, user_id: {loaded_user_id}")
                
                success = await self.app.tiny_code_agent.recreate_with_session_context(loaded_session_id, loaded_user_id)
                
                if success:
                    print(f"[DEBUG] _restore_agent_session: Agent successfully recreated with correct context")
                    # NOTE: No need to call load_session again - recreate_with_session_context already handles it
                    
                    # Show success message to user
                    self.chat_area.add_message("✅ **Agent Context Restored**: Agent successfully recreated with the loaded session's context. You can continue the conversation seamlessly.", is_user=False)
                else:
                    print(f"[DEBUG] _restore_agent_session: Failed to recreate agent with correct context")
                    self.chat_area.add_message("⚠️ **Partial Restore**: Conversation loaded but agent context could not be fully restored. The agent may have limited memory of this session.", is_user=False)
            else:
                print(f"[DEBUG] _restore_agent_session: Agent recreation not available, falling back to old behavior")
                # Fallback to old behavior
                if self.app.tiny_code_agent and hasattr(self.app.tiny_code_agent, 'load_session'):
                    await self.app.tiny_code_agent.load_session(loaded_session_id)
                    print(f"[DEBUG] Agent session restored for {loaded_session_id} (fallback)")
                elif self.app.tiny_code_agent and self.storage_manager:
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