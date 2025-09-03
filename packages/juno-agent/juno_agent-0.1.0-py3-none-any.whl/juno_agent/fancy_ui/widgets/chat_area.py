"""Chat message display area widget."""

import json
from datetime import datetime
from typing import Dict, Optional, List
from rich.markdown import Markdown
from rich.markup import escape
from rich.text import Text
from textual.containers import VerticalScroll
from textual.widgets import Static, TextArea
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual import events

from ...debug_logger import debug_logger


class TerminalLikeTextArea(TextArea):
    """TextArea with terminal-like mouse behavior (right-click to copy, Ctrl+C)."""
    
    def __init__(self, parent_message=None, **kwargs):
        super().__init__(**kwargs)
        self.parent_message = parent_message
        # Mouse selection is enabled by default (allow_select = True)
    
    def on_click(self, event: events.Click) -> None:
        """Handle mouse clicks - right click copies selected text."""
        # Right click (button 2 in Textual, button 3 on some systems)
        if event.button in (2, 3):  # Support both right-click button codes
            # Copy selected text to clipboard
            if self.selected_text:
                self._copy_to_clipboard(self.selected_text)
                # Notify user
                if self.parent_message and hasattr(self.parent_message, 'app'):
                    self.parent_message.app.notify("📋 Copied selected text", timeout=2)
            else:
                # No selection - copy all text
                self._copy_to_clipboard(self.text)
                if self.parent_message and hasattr(self.parent_message, 'app'):
                    self.parent_message.app.notify("📋 Copied all text", timeout=2)
            event.stop()
        # For left clicks, don't stop the event - let TextArea handle selection
    
    def on_key(self, event: events.Key) -> None:
        """Handle keyboard shortcuts."""
        # Ctrl+C copies selected text (like terminal)
        if event.key == "ctrl+c":
            if self.selected_text:
                self._copy_to_clipboard(self.selected_text)
                if self.parent_message and hasattr(self.parent_message, 'app'):
                    self.parent_message.app.notify("Copied selected text (Ctrl+C)", timeout=1)
            else:
                # No selection - copy all text
                self._copy_to_clipboard(self.text)
                if self.parent_message and hasattr(self.parent_message, 'app'):
                    self.parent_message.app.notify("Copied all text (Ctrl+C)", timeout=1)
            event.stop()
            return
        
        # Escape exits selection mode
        if event.key == "escape" and self.parent_message:
            self.parent_message._exit_selection_mode()
            event.stop()
            return
        
        # For other keys, let the event bubble up normally
        # Don't manually call parent methods as Textual handles this automatically
    
    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard using the app's copy method."""
        try:
            # Try to access the app's copy method
            app = self.app
            if app and hasattr(app, '_copy_to_clipboard_hybrid'):
                app._copy_to_clipboard_hybrid(text)
            else:
                # Fallback - try basic clipboard
                try:
                    import pyperclip
                    pyperclip.copy(text)
                except:
                    pass
        except Exception:
            # Silent fail - copying is not critical for functionality
            pass


class MessageWidget(Static):
    """Hybrid message widget that supports both Rich rendering and text selection.
    
    Modes:
    - Display Mode (default): Beautiful Rich markdown rendering
    - Selection Mode: TextArea for text selection capability
    """
    
    # Make the widget focusable so users can click and then Ctrl+S
    can_focus = True
    
    def __init__(self, content: str, is_user: bool = False, timestamp: datetime = None):
        super().__init__()
        self.content = content
        self.is_user = is_user
        self.timestamp = timestamp or datetime.now()
        self.tool_calls: List[Dict] = []  # Store tool calls for this message
        self.pending_tool_calls: Dict[str, Dict] = {}  # Store pending tool calls by ID
        self.tool_calls_expanded = False  # Local expansion state for this message
        
        # Mode switching
        self._selection_mode = False
        self._textarea_widget = None
        self._original_content = None
        
        self.update_content()
    
    def toggle_selection_mode(self):
        """Toggle between display mode and selection mode."""
        if self._selection_mode:
            self._exit_selection_mode()
        else:
            self._enter_selection_mode()
    
    def _enter_selection_mode(self):
        """Enter selection mode - replace content with TextArea."""
        if self._selection_mode:
            return
            
        self._selection_mode = True
        
        # Store current Rich content
        self._original_content = self.renderable
        
        # Create TextArea with formatted plain text
        formatted_text = self._get_formatted_text_for_selection()
        
        # Clear current content and show TextArea
        self.update("")
        
        # Create TextArea widget with terminal-like behavior
        self._textarea_widget = TerminalLikeTextArea(
            text=formatted_text,
            read_only=True,
            show_line_numbers=False,
            parent_message=self
        )
        
        # Mount the TextArea
        self.mount(self._textarea_widget)
        
        # Add visual indicator
        self.add_class("selection-mode")
        
        # Focus the TextArea for mouse interaction
        self._textarea_widget.focus()
        
        # Update footer to show selection mode shortcuts
        if hasattr(self.app, 'dynamic_footer') and self.app.dynamic_footer:
            self.app.dynamic_footer.set_selection_mode(True)
        # Don't auto-select - let users select with mouse like in terminal
    
    def _exit_selection_mode(self):
        """Exit selection mode - restore Rich content."""
        if not self._selection_mode:
            return
            
        self._selection_mode = False
        
        # Remove TextArea
        if self._textarea_widget:
            self._textarea_widget.remove()
            self._textarea_widget = None
        
        # Restore original Rich content
        if self._original_content:
            self.update(self._original_content)
        
        # Remove visual indicator
        self.remove_class("selection-mode")
        
        # Update footer to show normal shortcuts
        if hasattr(self.app, 'dynamic_footer') and self.app.dynamic_footer:
            self.app.dynamic_footer.set_selection_mode(False)
    
    def _get_formatted_text_for_selection(self) -> str:
        """Get formatted plain text version for TextArea selection."""
        if self.is_user:
            return f"> {self.content}"
        else:
            # Combine tool calls with original content if needed
            tool_calls_content = self._format_tool_calls()
            if tool_calls_content:
                full_content = tool_calls_content + "\n\n---\n\n" + self.content
            else:
                full_content = self.content
            
            # Convert to formatted plain text
            return self._convert_markdown_to_plain_text(full_content)
    
    @property
    def is_in_selection_mode(self) -> bool:
        """Check if widget is currently in selection mode."""
        return self._selection_mode
    
    def get_selected_text(self) -> str:
        """Get currently selected text if in selection mode."""
        if self._selection_mode and self._textarea_widget:
            # Access the selected_text property directly - it exists in TextArea
            selected = self._textarea_widget.selected_text
            return selected if selected else ''
        return ''
    
    def has_selection(self) -> bool:
        """Check if widget has selected text."""
        return bool(self.get_selected_text())
    
    def update_content(self):
        """Update the message content with proper Rich formatting for display mode."""
        # Skip update if in selection mode
        if self._selection_mode:
            return
            
        if self.is_user:
            # User message starts with > and is rendered as plain text to avoid markup issues
            formatted_content = f"> {self.content}"
            # Use Text object to ensure no markup interpretation
            text_obj = Text(formatted_content)
            self.add_class("user-message")
            self.update(text_obj)
        else:
            # Agent message starts with • and renders markdown
            self.add_class("agent-message")
            try:
                # For agent messages, check if content contains Rich markup or markdown
                if self.content.strip():
                    # Check if content contains Rich markup tags
                    if '[' in self.content and ']' in self.content and any(tag in self.content for tag in ['[bold', '[green', '[red', '[yellow', '[dim']):
                        # Content has Rich markup - use Text object  
                        rich_text = Text.from_markup(self.content)
                        self.update(rich_text)
                    else:
                        # Regular markdown content
                        markdown_obj = Markdown(self.content)
                        self.update(markdown_obj)
                else:
                    # Empty content fallback
                    self.update("(empty message)")
                    
            except Exception as e:
                # Fallback to plain text if rendering fails
                import sys
                print(f"Content rendering failed: {e}", file=sys.stderr)
                formatted_content = f"{self.content}"
                self.update(formatted_content)
    
    def _convert_markdown_to_plain_text(self, markdown_text: str) -> str:
        """Convert markdown to nicely formatted plain text for TextArea display."""
        import re
        
        text = markdown_text
        
        # Convert headers
        text = re.sub(r'^# (.+)$', r'═══ \1 ═══', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'─── \1 ───', text, flags=re.MULTILINE)
        text = re.sub(r'^### (.+)$', r'··· \1 ···', text, flags=re.MULTILINE)
        
        # Convert code blocks to bordered format
        def format_code_block(match):
            lang = match.group(1) or ""
            code = match.group(2)
            lines = code.strip().split('\n')
            max_len = max(len(line) for line in lines) if lines else 0
            border_len = max(max_len + 4, 20)
            
            result = f"┌{'─' * border_len}┐"
            if lang:
                result += f"\n│ {lang.upper():<{border_len-2}} │"
                result += f"\n├{'─' * border_len}┤"
            
            for line in lines:
                result += f"\n│ {line:<{border_len-2}} │"
            result += f"\n└{'─' * border_len}┘"
            return result
        
        text = re.sub(r'```(\w*)\n(.*?)\n```', format_code_block, text, flags=re.DOTALL)
        
        # Convert inline code
        text = re.sub(r'`([^`]+)`', r'｢\1｣', text)
        
        # Convert bold and italic
        text = re.sub(r'\*\*([^*]+)\*\*', r'【\1】', text)
        text = re.sub(r'\*([^*]+)\*', r'〈\1〉', text)
        
        # Convert lists
        text = re.sub(r'^- (.+)$', r'  • \1', text, flags=re.MULTILINE)
        text = re.sub(r'^\* (.+)$', r'  • \1', text, flags=re.MULTILINE)
        text = re.sub(r'^\d+\. (.+)$', r'  \1', text, flags=re.MULTILINE)
        
        return text
    
    def add_tool_call(self, tool_call_data: Dict):
        """Add a tool call to this message."""
        self.tool_calls.append(tool_call_data)
        self._update_with_tool_calls()
    
    def start_tool_call(self, tool_call_id: str, tool_name: str, arguments: Dict, hierarchy_data: Dict = None):
        """Start a new tool call for this message."""
        debug_logger.log_function_entry("MessageWidget.start_tool_call",
                                       tool_call_id=tool_call_id,
                                       tool_name=tool_name,
                                       arguments_keys=list(arguments.keys()) if arguments else [],
                                       message_id=hex(id(self)))
        
        tool_data = {
            "tool_call_id": tool_call_id,
            "tool_name": tool_name,
            "arguments": arguments,
            "status": "running",
            "start_time": datetime.now()
        }
        
        # Add hierarchy information if provided
        if hierarchy_data:
            tool_data.update({
                "agent_level": hierarchy_data.get("agent_level", 0),
                "is_subagent": hierarchy_data.get("is_subagent", False),
                "agent_id": hierarchy_data.get("agent_id"),
                "parent_id": hierarchy_data.get("parent_id"),
                "display_name": hierarchy_data.get("display_name")
            })
        
        self.pending_tool_calls[tool_call_id] = tool_data
        
        debug_logger.log_state_change("MessageWidget", "pending_tool_calls", 
                                    len(self.pending_tool_calls) - 1, 
                                    len(self.pending_tool_calls))
        
        self._update_with_tool_calls()
        debug_logger.log_function_exit("MessageWidget.start_tool_call")
    
    def complete_tool_call(self, tool_call_id: str, result: str, duration: Optional[float] = None, tool_name: Optional[str] = None):
        """Complete a tool call for this message."""
        debug_logger.log_function_entry("MessageWidget.complete_tool_call",
                                       tool_call_id=tool_call_id,
                                       result_length=len(str(result)) if result else 0,
                                       duration=duration,
                                       message_id=hex(id(self)))
        
        if tool_call_id in self.pending_tool_calls:
            tool_data = self.pending_tool_calls.pop(tool_call_id)
            tool_data.update({
                "result": result,
                "status": "completed",
                "duration": duration,
                "end_time": datetime.now()
            })
            self.tool_calls.append(tool_data)
            
            debug_logger.log_state_change("MessageWidget", "tool_calls_count", 
                                        len(self.tool_calls) - 1, 
                                        len(self.tool_calls))
            debug_logger.log_state_change("MessageWidget", "pending_tool_calls_count", 
                                        len(self.pending_tool_calls) + 1, 
                                        len(self.pending_tool_calls))
            
            self._update_with_tool_calls()
        else:
            # Handle orphaned tool_end event - create a completed tool call retroactively
            debug_logger.log_event("handling_orphaned_tool_end_event",
                                 tool_call_id=tool_call_id,
                                 pending_tool_call_ids=list(self.pending_tool_calls.keys()))
            
            # Use provided tool_name if available, otherwise try to extract from result
            if not tool_name:
                tool_name = "unknown_tool"
                if result and isinstance(result, str):
                    # Try to extract tool name from result patterns
                    if "File written to" in result or "content written" in result:
                        tool_name = "write"
                    elif "File read from" in result or "content:" in result:
                        tool_name = "read"
                    elif "Command executed" in result or "exit code" in result:
                        tool_name = "bash"
                    elif "Search results" in result or "matches found" in result:
                        tool_name = "grep"
            
            # Create a completed tool call with inferred information
            tool_data = {
                "tool_call_id": tool_call_id,
                "tool_name": tool_name,
                "arguments": {"note": "Orphaned tool - arguments unknown"},
                "status": "completed",
                "result": result,
                "duration": duration,
                "start_time": datetime.now(),  # Approximate
                "end_time": datetime.now()
            }
            
            self.tool_calls.append(tool_data)
            
            debug_logger.log_event("orphaned_tool_call_added",
                                 tool_call_id=tool_call_id,
                                 tool_name=tool_name,
                                 tool_calls_count=len(self.tool_calls))
            
            self._update_with_tool_calls()
        
        debug_logger.log_function_exit("MessageWidget.complete_tool_call")
    
    def error_tool_call(self, tool_call_id: str, error: str):
        """Mark a tool call as failed for this message."""
        if tool_call_id in self.pending_tool_calls:
            tool_data = self.pending_tool_calls.pop(tool_call_id)
            tool_data.update({
                "error": error,
                "status": "error",
                "end_time": datetime.now()
            })
            self.tool_calls.append(tool_data)
            self._update_with_tool_calls()
    
    def _format_tool_calls(self) -> str:
        """Format tool calls as markdown sections with proper hierarchy."""
        if not self.tool_calls and not self.pending_tool_calls:
            return ""
        
        # Combine all tool calls and sort by chronological order first
        all_tool_calls = list(self.tool_calls) + list(self.pending_tool_calls.values())
        
        # Add execution order index to maintain chronological order
        for i, tool_call in enumerate(all_tool_calls):
            if 'execution_order' not in tool_call:
                # Use start_time if available, otherwise use index
                start_time = tool_call.get('start_time')
                if start_time:
                    tool_call['execution_order'] = start_time.timestamp()
                else:
                    tool_call['execution_order'] = i
        
        # Sort all tools by execution order first
        all_tool_calls.sort(key=lambda x: x.get('execution_order', 0))
        
        # Group tools: maintain chronological order but group subagent children after their parent
        sorted_tools = []
        pending_subagent_children = {}  # Store children waiting for their parent
        
        for tool_call in all_tool_calls:
            agent_level = tool_call.get("agent_level", 0)
            tool_name = tool_call.get("tool_name", "")
            
            if agent_level == 0:
                # Main agent tool - add immediately
                sorted_tools.append(tool_call)
                
                # If this is a subagent tool, add any pending children after it
                if tool_name in ["subAgent", "coding_subagent", "subagent"]:
                    tool_call_id = tool_call.get('tool_call_id')
                    if tool_call_id in pending_subagent_children:
                        # Add children that were waiting for this parent
                        children = sorted(pending_subagent_children[tool_call_id], 
                                        key=lambda x: x.get('execution_order', 0))
                        sorted_tools.extend(children)
                        del pending_subagent_children[tool_call_id]
            else:
                # Subagent tool - find its parent
                parent_id = tool_call.get('parent_id')
                
                # Check if parent subagent is already in sorted_tools
                parent_found = False
                for existing_tool in reversed(sorted_tools):
                    existing_level = existing_tool.get("agent_level", 0)
                    existing_name = existing_tool.get("tool_name", "")
                    
                    if (existing_level == 0 and 
                        existing_name in ["subAgent", "coding_subagent", "subagent"]):
                        # Found the parent subagent, add this child immediately after its siblings
                        parent_found = True
                        sorted_tools.append(tool_call)
                        break
                
                if not parent_found:
                    # Parent hasn't appeared yet, store for later
                    # Use a generic key since we don't know the exact parent tool_call_id
                    pending_key = f"pending_subagent_{len(pending_subagent_children)}"
                    if pending_key not in pending_subagent_children:
                        pending_subagent_children[pending_key] = []
                    pending_subagent_children[pending_key].append(tool_call)
        
        tool_sections = []
        for i, tool_call in enumerate(sorted_tools):
            # Check if this is the last tool at its level within its group
            current_level = tool_call.get("agent_level", 0)
            is_last = True
            
            # Look ahead to see if there are more tools at the same level in this group
            for j in range(i + 1, len(sorted_tools)):
                next_tool = sorted_tools[j]
                next_level = next_tool.get("agent_level", 0)
                
                if next_level < current_level:
                    # We've moved to a higher level (back to main agent), so this is last
                    break
                elif next_level == current_level:
                    # Found another tool at the same level
                    is_last = False
                    break
            
            tool_section = self._format_single_tool_call(tool_call, is_last=is_last, index=i)
            tool_sections.append(tool_section)
        
        if tool_sections:
            # Format tool sections with header
            header = "**🔧 Tool Usage:**\n\n" if len(tool_sections) > 1 else ""
            return header + "\n\n".join(tool_sections)
        return ""
    
    def _format_single_tool_call(self, tool_call: Dict, is_last: bool = False, index: int = 0) -> str:
        """Format a single tool call as markdown with hierarchy support."""
        tool_name = tool_call.get("tool_name", "unknown")
        status = tool_call.get("status", "unknown")
        arguments = tool_call.get("arguments", {})
        
        # Extract hierarchy information
        agent_level = tool_call.get("agent_level", 0)
        is_subagent = tool_call.get("is_subagent", False)
        display_name = tool_call.get("display_name", "")
        
        # Format arguments for display in header with enhanced formatting
        args_display = self._format_arguments_for_display(arguments)
        
        # Create tree-like hierarchy
        indent = ""
        tree_prefix = ""
        
        if agent_level > 0:
            # For subagent tools, use tree connectors  
            indent = "  " * (agent_level - 1)
            if is_last:
                tree_prefix = "└─"  # Last item at this level (no trailing space)
            else:
                tree_prefix = "├─"  # Not the last item (no trailing space)
        
        # Adjust spacing around icon consistently
        if tree_prefix:
            # Space after tree connector, space before tool name
            connector_space = " "
            icon_space = " "
        else:
            # No tree connector, just space before tool name  
            connector_space = ""
            icon_space = " "
        
        # Choose appropriate icon
        if tool_name in ["subAgent", "coding_subagent", "subagent"]:
            icon = "🔧"  # Main subagent tool
        elif is_subagent:
            icon = "🔨"  # Tools inside subagent
        else:
            icon = "🔧"  # Regular tool
        
        if self.tool_calls_expanded:
            arrow = "⏷"  # Expanded arrow
        else:
            arrow = "⏵"  # Collapsed arrow
            
        # Escape tool name to prevent markdown interpretation (e.g., *bash*)
        escaped_tool_name = tool_name.replace('*', '\\*').replace('_', '\\_')
        
        # Create header with proper escaping
        header = f"{indent}{tree_prefix}{connector_space}{icon}{icon_space}{escaped_tool_name}({args_display}) {arrow}"
        
        # Prevent markdown list interpretation for tree connectors
        if tree_prefix:
            # Add zero-width space at the beginning to prevent markdown from treating
            # tree connectors as list markers (which causes the * prefix issue)
            header = "\u200b" + header
        
        # Get status info
        status_info = None
        if status == "running":
            status_info = "🔄 Running..."
        elif status == "completed":
            duration = tool_call.get("duration")
            if duration:
                status_info = f"✅ (Completed in {duration:.2f}s)"
            else:
                status_info = "✅ (Completed)"
        elif status == "error":
            status_info = "❌ (Error occurred)"
        
        # Build content based on expansion state
        if not self.tool_calls_expanded:
            # Collapsed view - use bold with properly escaped arguments
            if status_info:
                return f"**▶ {header}** {status_info}"
            else:
                return f"**▶ {header}**"
        else:
            # Expanded view - show full details with proper indentation
            # Calculate proper alignment for tree structure
            if tree_prefix:
                # For tree items, align content under the icon, not the tree connector
                # Zero-width space + tree connector + space + icon = need proper alignment
                detail_indent = "\u200b" + indent + "   "  # Include zero-width space for consistency
            else:
                # For main-level tools, use base indent
                detail_indent = indent
            
            content_parts = [f"**{header}**"]  # Use bold with escaped arguments
            
            if status_info:
                content_parts.append(f"{detail_indent}*Status: {status_info}*")
            
            # Show full arguments in expanded view
            if arguments:
                content_parts.append("")
                content_parts.append(f"{detail_indent}📋 Arguments:")
                try:
                    args_json = json.dumps(arguments, indent=2)
                    # Indent each line of the JSON
                    indented_json = "\n".join(f"{detail_indent}  {line}" for line in args_json.split("\n"))
                    content_parts.append(f"```json\n{indented_json}\n```")
                except:
                    content_parts.append(f"```\n{detail_indent}  {str(arguments)}\n```")
            
            # Show full results in expanded view
            if status == "completed" and "result" in tool_call:
                result = tool_call["result"]
                content_parts.append("")
                content_parts.append(f"{detail_indent}✅ Result:")
                # In expanded view, show more of the result
                if len(result) > 1000:
                    # Indent each line of the result
                    indented_result = "\n".join(f"{detail_indent}  {line}" for line in result[:1000].split("\n"))
                    content_parts.append(f"```\n{indented_result}...\n```")
                    content_parts.append(f"{detail_indent}*(Result truncated for display)*")
                else:
                    indented_result = "\n".join(f"{detail_indent}  {line}" for line in result.split("\n"))
                    content_parts.append(f"```\n{indented_result}\n```")
            elif status == "error" and "error" in tool_call:
                error = tool_call["error"]
                content_parts.append("")
                content_parts.append(f"{detail_indent}❌ Error:")
                indented_error = "\n".join(f"{detail_indent}  {line}" for line in error.split("\n"))
                content_parts.append(f"```\n{indented_error}\n```")
            elif status == "running":
                content_parts.append("")
                content_parts.append(f"{detail_indent}*Tool is currently running...*")
            
            # Show timing information in expanded view
            if status in ["completed", "error"]:
                start_time = tool_call.get("start_time")
                end_time = tool_call.get("end_time")
                if start_time and end_time:
                    content_parts.append("")
                    content_parts.append(f"{detail_indent}*Started: {start_time.strftime('%H:%M:%S')}*")
                    content_parts.append(f"{detail_indent}*Ended: {end_time.strftime('%H:%M:%S')}*")
                elif start_time:
                    content_parts.append("")
                    content_parts.append(f"{detail_indent}*Started: {start_time.strftime('%H:%M:%S')}*")
            
            return "\n".join(content_parts)
    
    def _update_with_tool_calls(self):
        """Update the message content including tool calls."""
        debug_logger.log_function_entry("MessageWidget._update_with_tool_calls",
                                       is_user=self.is_user,
                                       tool_calls_count=len(self.tool_calls),
                                       pending_tool_calls_count=len(self.pending_tool_calls),
                                       message_id=hex(id(self)))
        
        # Skip update if in selection mode
        if self._selection_mode:
            debug_logger.log_event("skipping_update_in_selection_mode")
            return
        
        if self.is_user:
            # User messages don't have tool calls - use escape for safety
            safe_content = escape(self.content)
            formatted_content = f"> {safe_content}"
            self.add_class("user-message")
            self.update(formatted_content)
            debug_logger.log_event("user_message_updated", content_length=len(formatted_content))
        else:
            # Agent message with potential tool calls
            try:
                # Combine tool calls with original content (tool calls first)
                tool_calls_content = self._format_tool_calls()
                if tool_calls_content:
                    # Tool calls first, then separator, then agent response
                    full_content = tool_calls_content + "\n\n---\n\n" + self.content
                else:
                    # No tool calls, just show the content
                    full_content = self.content
                
                debug_logger.log_event("agent_message_content_prepared",
                                     original_content_length=len(self.content),
                                     tool_calls_content_length=len(tool_calls_content) if tool_calls_content else 0,
                                     full_content_length=len(full_content))
                
                # Agent message starts with • and renders markdown (same as update_content)
                self.add_class("agent-message")
                try:
                    # For agent messages, check if content contains Rich markup or markdown
                    if full_content.strip():
                        # Check if content contains Rich markup tags
                        if '[' in full_content and ']' in full_content and any(tag in full_content for tag in ['[bold', '[green', '[red', '[yellow', '[dim']):
                            # Content has Rich markup - use Text object
                            from rich.text import Text
                            rich_text = Text.from_markup(full_content)
                            self.update(rich_text)
                        else:
                            # Regular markdown content
                            markdown_obj = Markdown(full_content)
                            self.update(markdown_obj)
                    else:
                        # Empty content fallback
                        self.update("(empty message)")
                        
                except Exception as e:
                    # Fallback to plain text if rendering fails
                    import sys
                    print(f"Content rendering failed: {e}", file=sys.stderr)
                    formatted_content = f"{full_content}"
                    self.update(formatted_content)
                
                debug_logger.log_event("agent_message_updated_with_rich_content")
            except Exception as e:
                debug_logger.log_error("message_update_failed", e,
                                     message_id=hex(id(self)),
                                     content_length=len(self.content))
                import sys
                print(f"Message update failed: {e}", file=sys.stderr)
                # Fallback to just the content
                self.update(self.content)
        
        debug_logger.log_function_exit("MessageWidget._update_with_tool_calls")
    
    def _format_arguments_for_display(self, arguments: Dict) -> str:
        """Format arguments for display in collapsed tool call headers.
        
        Shows actual argument names and values with smart truncation:
        - Character limit per argument value (30-50 characters)
        - Smart truncation that preserves readability
        - Show count of remaining content for long arguments
        - Handle different argument types (strings, numbers, objects)
        """
        if not arguments:
            return ""
        
        try:
            formatted_args = []
            max_total_length = 120  # Maximum total length for all arguments
            max_arg_length = 40     # Maximum length per argument value
            current_length = 0
            
            for arg_key, arg_value in arguments.items():
                # Format the argument value based on its type
                if isinstance(arg_value, str):
                    formatted_value = self._format_string_argument(arg_value, max_arg_length)
                elif isinstance(arg_value, (int, float, bool)):
                    formatted_value = str(arg_value)
                elif isinstance(arg_value, (list, dict)):
                    formatted_value = self._format_complex_argument(arg_value, max_arg_length)
                else:
                    formatted_value = str(arg_value)[:max_arg_length] + "..." if len(str(arg_value)) > max_arg_length else str(arg_value)
                
                # Create the argument string with proper escaping
                # Escape markdown characters in both key and value
                escaped_key = str(arg_key).replace('*', '\\*').replace('_', '\\_')
                escaped_value = str(formatted_value).replace('*', '\\*').replace('_', '\\_')
                arg_string = f"{escaped_key}={escaped_value}"
                
                # Check if adding this argument would exceed total length
                remaining_indicator = f"... +{len(arguments) - len(formatted_args)} more" if len(arguments) - len(formatted_args) > 1 else ""
                projected_length = current_length + len(arg_string) + len(remaining_indicator) + 4  # +4 for separators
                
                if projected_length > max_total_length and formatted_args:
                    # Add indicator for remaining arguments
                    remaining_count = len(arguments) - len(formatted_args)
                    formatted_args.append(f"... +{remaining_count} more")
                    break
                
                formatted_args.append(arg_string)
                current_length += len(arg_string) + 2  # +2 for ", "
            
            return ", ".join(formatted_args)
            
        except Exception:
            # Fallback to simple display
            return "..."
    
    def _format_string_argument(self, value: str, max_length: int) -> str:
        """Format a string argument with smart truncation and markdown escaping."""
        if len(value) <= max_length:
            # Escape markdown characters in the value
            escaped_value = value.replace('*', '\\*').replace('_', '\\_')
            return f'"{escaped_value}"'
        
        # For file paths, show filename and indicate directory
        if '/' in value or '\\' in value:
            # Likely a file path
            if value.startswith('/'):
                # Absolute path - show filename and indicate path
                filename = value.split('/')[-1]
                if len(filename) <= max_length - 10:
                    escaped_filename = filename.replace('*', '\\*').replace('_', '\\_')
                    return f'"...//{escaped_filename}"'
            else:
                # Relative path or filename
                parts = value.replace('\\', '/').split('/')
                filename = parts[-1]
                if len(filename) <= max_length - 5:
                    escaped_filename = filename.replace('*', '\\*').replace('_', '\\_')
                    if len(parts) > 1:
                        return f'".../{escaped_filename}"'
                    else:
                        return f'"{escaped_filename}"'
        
        # For long text content, show preview and indicate more content
        if '\n' in value:
            # Multi-line content
            first_line = value.split('\n')[0]
            line_count = value.count('\n') + 1
            char_count = len(value)
            
            if len(first_line) <= max_length - 20:
                escaped_line = first_line.replace('*', '\\*').replace('_', '\\_')
                return f'"{escaped_line}... [{line_count} lines, {char_count} chars]"'
            else:
                truncated = first_line[:max_length - 25]
                escaped_truncated = truncated.replace('*', '\\*').replace('_', '\\_')
                return f'"{escaped_truncated}... [{line_count} lines, {char_count} chars]"'
        else:
            # Single line - simple truncation with character count
            truncated = value[:max_length - 15]
            escaped_truncated = truncated.replace('*', '\\*').replace('_', '\\_')
            char_count = len(value)
            return f'"{escaped_truncated}... [{char_count} chars]"'
    
    def _format_complex_argument(self, value, max_length: int) -> str:
        """Format complex arguments (lists, dicts) with smart truncation."""
        if isinstance(value, list):
            if not value:
                return "[]"
            elif len(value) == 1:
                # Single item list
                item_str = str(value[0])
                if len(item_str) <= max_length - 10:
                    return f"[{item_str}]"
                else:
                    return f"[1 item]"
            else:
                return f"[{len(value)} items]"
        
        elif isinstance(value, dict):
            if not value:
                return "{}"
            elif len(value) == 1:
                # Single key dict
                key, val = list(value.items())[0]
                key_val_str = f"{key}: {val}"
                if len(key_val_str) <= max_length - 10:
                    return f"{{{key_val_str}}}"
                else:
                    return f"{{1 key}}"
            else:
                return f"{{{len(value)} keys}}"
        
        else:
            # Other complex types
            str_val = str(value)
            if len(str_val) <= max_length:
                return str_val
            else:
                return str_val[:max_length - 3] + "..."
    
    def refresh_tool_calls(self, expanded: bool):
        """Refresh tool call display with new expansion state."""
        self.tool_calls_expanded = expanded
        self._update_with_tool_calls()
    
    def get_copyable_text(self) -> str:
        """Get the text content for copying - prioritize selected text."""
        # First check if we're in selection mode and have selected text
        if self._selection_mode and self._textarea_widget:
            selected = getattr(self._textarea_widget, 'selected_text', '') or ''
            if selected:
                return selected
        
        # If no selection, return the original content (not the formatted display text)
        if self.is_user:
            # For user messages, return just the content without the > prefix
            return self.content
        else:
            # For agent messages, return the original markdown content
            return self.content
    
    def on_click(self, event) -> None:
        """Handle mouse clicks for entering selection mode."""
        # Check if this is a double-click
        # Textual's Click event uses 'chain' for consecutive clicks
        if hasattr(event, 'chain') and event.chain == 2:
            # Double-click enters selection mode (simple and intuitive)
            # Exit any other message from selection mode first
            self._ensure_only_this_message_selected()
            self._enter_selection_mode()
            event.stop()
    
    def _ensure_only_this_message_selected(self):
        """Exit selection mode on all other messages."""
        # Find parent ChatArea to access all messages
        parent = self.parent
        while parent and not hasattr(parent, 'messages'):
            parent = getattr(parent, 'parent', None)
        
        if parent and hasattr(parent, 'messages'):
            for msg in parent.messages:
                if msg != self and hasattr(msg, 'is_in_selection_mode') and msg.is_in_selection_mode:
                    msg._exit_selection_mode()
    
    def on_key(self, event) -> None:
        """Handle key events."""
        # Escape exits selection mode
        if event.key == "escape" and self._selection_mode:
            self._exit_selection_mode()
            event.stop()
        # Note: Ctrl+S is handled at the app level for global exit


class ChatArea(VerticalScroll):
    """Scrollable chat message area."""
    
    DEFAULT_CSS = """
    ChatArea {
        height: 1fr;
        border: round $primary;
        margin: 1;
        padding: 1;
    }
    
    .user-message {
        color: $text;
        text-align: left;
        margin: 0 0 1 0;
    }
    
    .agent-message {
        color: white;
        text-align: left;
        margin: 0 0 1 0;
    }
    """
    
    def __init__(self):
        super().__init__()
        self.messages = []
        self.current_agent_message: Optional[MessageWidget] = None  # Track current agent message for tool calls
        self.pending_tool_events: List[Dict] = []  # Buffer tool events that arrive before agent message
        
    def add_message(self, content: str, is_user: bool = False):
        """Add a new message to the chat area."""
        message_widget = MessageWidget(content, is_user)
        self.mount(message_widget)
        self.messages.append(message_widget)
        
        # Track current agent message for tool calls
        if not is_user:
            self.current_agent_message = message_widget
            # Apply any pending tool events to this new agent message
            self._apply_pending_tool_events()
        
        # Auto-scroll to bottom
        self.scroll_end(animate=False)
        
        return message_widget
        
    def clear_messages(self):
        """Clear all messages from the chat area."""
        for message in self.messages:
            message.remove()
        self.messages.clear()
        self.current_agent_message = None
    
    def remove_last_message(self):
        """Remove the last message from the chat area."""
        if self.messages:
            last_message = self.messages.pop()
            
            # If the message being removed has tool calls, preserve them for the next agent message
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                debug_logger.log_event("preserving_tool_calls_from_removed_message",
                                     tool_calls_count=len(last_message.tool_calls),
                                     pending_tool_calls_count=len(last_message.pending_tool_calls))
                
                # Store tool calls to be transferred to the next agent message
                for tool_call in last_message.tool_calls:
                    self.pending_tool_events.append({
                        "message_type": "tool_preserved_completed",
                        "data": {
                            "tool_name": tool_call.get("tool_name", "unknown"),
                            "tool_call_id": tool_call.get("tool_call_id", ""),
                            "arguments": tool_call.get("arguments", {}),
                            "result": tool_call.get("result", ""),
                            "duration": tool_call.get("duration"),
                            "status": tool_call.get("status", "completed")
                        }
                    })
                
                # Store pending tool calls to be transferred as well
                for tool_call_id, tool_call in last_message.pending_tool_calls.items():
                    self.pending_tool_events.append({
                        "message_type": "tool_preserved_pending",
                        "data": {
                            "tool_name": tool_call.get("tool_name", "unknown"),
                            "tool_call_id": tool_call_id,
                            "arguments": tool_call.get("arguments", {}),
                            "status": tool_call.get("status", "running")
                        }
                    })
            
            last_message.remove()
            
            # Update current agent message pointer if needed
            if last_message == self.current_agent_message:
                # Find the previous agent message
                for msg in reversed(self.messages):
                    if not msg.is_user:
                        self.current_agent_message = msg
                        break
                else:
                    self.current_agent_message = None
    
    async def add_tool_event(self, message_type: str, data: Dict):
        """Add a tool event to the current agent message."""
        debug_logger.log_function_entry("ChatArea.add_tool_event", 
                                       message_type=message_type,
                                       data_keys=list(data.keys()),
                                       current_agent_message_available=self.current_agent_message is not None,
                                       current_message_is_user=self.current_agent_message.is_user if self.current_agent_message else None)
        
        if not self.current_agent_message or self.current_agent_message.is_user:
            # No current agent message to attach tool events to
            # Create a new agent message to hold the tool events
            debug_logger.log_event("no_current_agent_message_for_tool_event",
                                 message_type=message_type,
                                 current_agent_message_available=self.current_agent_message is not None,
                                 is_user_message=self.current_agent_message.is_user if self.current_agent_message else None)
            
            # Create a placeholder agent message for tool events
            tool_name = data.get("tool_name", "unknown")
            if message_type == "tool_start":
                placeholder_content = f"🔧 Running {tool_name}..."
            else:
                placeholder_content = f"🔧 Tool activity: {tool_name}"
            
            debug_logger.log_event("creating_placeholder_agent_message", 
                                 tool_name=tool_name,
                                 message_type=message_type)
            
            # Alternative approach: buffer the tool event for later
            debug_logger.log_event("buffering_tool_event_for_later",
                                 message_type=message_type,
                                 tool_name=tool_name)
            
            self.pending_tool_events.append({
                "message_type": message_type,
                "data": data
            })
            
            # Create new agent message for tool events as fallback
            self.current_agent_message = self.add_message(placeholder_content, is_user=False)
            debug_logger.log_event("placeholder_agent_message_created", 
                                 message_id=hex(id(self.current_agent_message)))
            
            # The _apply_pending_tool_events will be called automatically by add_message
            return
        
        tool_name = data.get("tool_name", "unknown")
        tool_call_id = data.get("tool_call_id", "")
        
        debug_logger.log_event("processing_tool_event",
                             message_type=message_type,
                             tool_name=tool_name,
                             tool_call_id=tool_call_id,
                             current_message_id=hex(id(self.current_agent_message)))
        
        if message_type == "tool_start":
            arguments = data.get("arguments", {})
            # Extract hierarchy data from the tool event
            hierarchy_data = {
                "agent_level": data.get("agent_level", 0),
                "is_subagent": data.get("is_subagent", False),
                "agent_id": data.get("agent_id"),
                "parent_id": data.get("parent_id"),
                "display_name": data.get("display_name")
            }
            debug_logger.log_ui_update("MessageWidget", "start_tool_call",
                                     tool_call_id=tool_call_id,
                                     tool_name=tool_name,
                                     arguments_keys=list(arguments.keys()) if arguments else [])
            self.current_agent_message.start_tool_call(tool_call_id, tool_name, arguments, hierarchy_data)
            
        elif message_type == "tool_end":
            result = data.get("result", "")
            duration = data.get("duration")
            
            # Check if this tool_end event indicates an error was detected
            has_error = data.get("has_error", False)
            error_message = data.get("error_message", "")
            
            debug_logger.log_ui_update("MessageWidget", "complete_tool_call",
                                     tool_call_id=tool_call_id,
                                     result_length=len(str(result)) if result else 0,
                                     duration=duration,
                                     has_error=has_error,
                                     error_type=data.get("error_type", ""))
            
            if has_error and error_message:
                # Tool completed but with detected errors - mark as error
                self.current_agent_message.error_tool_call(tool_call_id, error_message)
            else:
                # Tool completed successfully - pass tool_name to help with orphaned tool handling
                self.current_agent_message.complete_tool_call(tool_call_id, result, duration, tool_name)
            
        elif message_type == "tool_error":
            # This is the new enhanced tool_error message type with comprehensive error info
            error = data.get("error_message", data.get("error", "Unknown error"))
            error_type = data.get("error_type", "unknown")
            error_confidence = data.get("error_confidence", 0.0)
            
            # Log enhanced error information
            debug_logger.log_ui_update("MessageWidget", "error_tool_call_enhanced",
                                     tool_call_id=tool_call_id,
                                     error_type=error_type,
                                     error_confidence=error_confidence,
                                     error=str(error))
            
            # For UI purposes, we can use the enhanced error message or fall back to basic error
            enhanced_error = f"{error} [{error_type}, confidence: {error_confidence:.2f}]" if error_type != "unknown" else str(error)
            self.current_agent_message.error_tool_call(tool_call_id, enhanced_error)
        
        debug_logger.log_event("scrolling_to_bottom_after_tool_update")
        # Auto-scroll to bottom to show updated tool call
        self.scroll_end(animate=False)
        
        debug_logger.log_function_exit("ChatArea.add_tool_event")
    
    def _apply_pending_tool_events(self):
        """Apply any pending tool events to the current agent message."""
        if not self.pending_tool_events or not self.current_agent_message:
            return
        
        debug_logger.log_event("applying_pending_tool_events",
                             pending_count=len(self.pending_tool_events),
                             current_message_id=hex(id(self.current_agent_message)))
        
        for event in self.pending_tool_events:
            message_type = event["message_type"]
            data = event["data"]
            
            debug_logger.log_event("applying_buffered_tool_event",
                                 message_type=message_type,
                                 tool_name=data.get("tool_name"))
            
            # Apply the tool event synchronously (we're not in async context here)
            tool_name = data.get("tool_name", "unknown")
            tool_call_id = data.get("tool_call_id", "")
            
            if message_type == "tool_start":
                arguments = data.get("arguments", {})
                # Extract hierarchy data from the buffered event
                hierarchy_data = {
                    "agent_level": data.get("agent_level", 0),
                    "is_subagent": data.get("is_subagent", False),
                    "agent_id": data.get("agent_id"),
                    "parent_id": data.get("parent_id"),
                    "display_name": data.get("display_name")
                }
                self.current_agent_message.start_tool_call(tool_call_id, tool_name, arguments, hierarchy_data)
                
            elif message_type == "tool_end":
                result = data.get("result", "")
                duration = data.get("duration")
                self.current_agent_message.complete_tool_call(tool_call_id, result, duration, tool_name)
                
            elif message_type == "tool_error":
                error = data.get("error", "Unknown error")
                self.current_agent_message.error_tool_call(tool_call_id, error)
                
            elif message_type == "tool_preserved_completed":
                # Restore a completed tool call that was preserved from a removed message
                arguments = data.get("arguments", {})
                result = data.get("result", "")
                duration = data.get("duration")
                
                # Extract hierarchy data from the preserved event
                hierarchy_data = {
                    "agent_level": data.get("agent_level", 0),
                    "is_subagent": data.get("is_subagent", False),
                    "agent_id": data.get("agent_id"),
                    "parent_id": data.get("parent_id"),
                    "display_name": data.get("display_name")
                }
                
                # Add as completed tool call
                self.current_agent_message.start_tool_call(tool_call_id, tool_name, arguments, hierarchy_data)
                self.current_agent_message.complete_tool_call(tool_call_id, result, duration, tool_name)
                
            elif message_type == "tool_preserved_pending":
                # Restore a pending tool call that was preserved from a removed message
                arguments = data.get("arguments", {})
                
                # Extract hierarchy data from the preserved event
                hierarchy_data = {
                    "agent_level": data.get("agent_level", 0),
                    "is_subagent": data.get("is_subagent", False),
                    "agent_id": data.get("agent_id"),
                    "parent_id": data.get("parent_id"),
                    "display_name": data.get("display_name")
                }
                
                self.current_agent_message.start_tool_call(tool_call_id, tool_name, arguments, hierarchy_data)
        
        # Clear pending events
        debug_logger.log_event("clearing_pending_tool_events", 
                             applied_count=len(self.pending_tool_events))
        self.pending_tool_events.clear()
    
    def refresh_tool_call_display(self, expanded: bool):
        """Refresh all messages to update tool call display based on expansion state."""
        for message in self.messages:
            if not message.is_user and (message.tool_calls or message.pending_tool_calls):
                # Update the message's tool call display with the new expansion state
                message.refresh_tool_calls(expanded)
    
    def get_focused_message_text(self) -> str:
        """Get text from the currently focused message widget."""
        try:
            # Get the currently focused widget from the app
            app = self.app
            if app and hasattr(app, 'focused'):
                focused_widget = app.focused
                
                # Check if the focused widget is a MessageWidget
                if isinstance(focused_widget, MessageWidget):
                    return focused_widget.get_copyable_text()
                
                # Check if the focused widget is within a MessageWidget
                parent = focused_widget
                while parent and parent != self:
                    if isinstance(parent, MessageWidget):
                        return parent.get_copyable_text()
                    parent = getattr(parent, 'parent', None)
                    
        except Exception:
            # Ignore focus detection errors
            pass
        
        return ""
    
    def get_latest_message_text(self) -> str:
        """Get text from the most recent message."""
        if self.messages:
            return self.messages[-1].get_copyable_text()
        return ""
    
    def get_all_messages_text(self) -> str:
        """Get text from all messages in the chat."""
        texts = []
        for message in self.messages:
            text = message.get_copyable_text()
            if text:
                prefix = "> " if message.is_user else "● "
                texts.append(f"{prefix}{text}")
        return "\n\n".join(texts)