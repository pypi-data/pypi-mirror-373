"""Widget for displaying subagent tool calls with proper hierarchy indentation."""

from typing import Dict, Optional, Any
from rich.text import Text
from rich.markup import escape
from textual.widgets import Static

from ...debug_logger import debug_logger


class SubagentDisplay(Static):
    """
    Widget for displaying tool calls with subagent hierarchy indentation.
    
    This widget handles:
    - Indented display of subagent tool calls
    - Different icons for main agent vs subagent tools
    - Hierarchy-aware formatting
    """
    
    DEFAULT_CSS = """
    SubagentDisplay {
        margin: 0 0 1 0;
        padding: 0;
    }
    
    .main-agent-tool {
        color: $accent;
    }
    
    .subagent-tool {
        color: $warning;
    }
    
    .tool-running {
        color: $primary;
    }
    
    .tool-completed {
        color: $success;
    }
    
    .tool-error {
        color: $error;
    }
    """
    
    # Tool icons for different agent levels
    MAIN_AGENT_ICON = "🔧"
    SUBAGENT_ICON = "↳🔧"
    INDENTATION_SIZE = 2  # 2 spaces per hierarchy level
    
    def __init__(self, tool_data: Dict[str, Any], expanded: bool = False):
        """
        Initialize the subagent display widget.
        
        Args:
            tool_data: Dictionary containing tool information including hierarchy data
            expanded: Whether to show expanded view of tool details
        """
        super().__init__()
        self.tool_data = tool_data
        self.expanded = expanded
        self.update_display()
    
    def update_display(self) -> None:
        """Update the display content based on current tool data and expansion state."""
        try:
            content = self._format_tool_display()
            self.update(content)
            
            # Apply CSS classes based on tool properties
            self._apply_css_classes()
            
        except Exception as e:
            debug_logger.log_error("subagent_display_update_failed", e,
                                 tool_data_keys=list(self.tool_data.keys()))
            # Fallback display
            self.update(f"Tool display error: {str(e)}")
    
    def _format_tool_display(self) -> Text:
        """
        Format the tool display with proper hierarchy indentation.
        
        Returns:
            Rich Text object with formatted tool display
        """
        # Extract tool information
        tool_name = self.tool_data.get("tool_name", "unknown")
        status = self.tool_data.get("status", "unknown")
        agent_level = self.tool_data.get("agent_level", 0)
        is_subagent = self.tool_data.get("is_subagent", False)
        display_name = self.tool_data.get("display_name", "")
        
        debug_logger.log_event("formatting_tool_display",
                              tool_name=tool_name,
                              status=status,
                              agent_level=agent_level,
                              is_subagent=is_subagent,
                              expanded=self.expanded)
        
        # Create indentation based on hierarchy level
        indent = " " * (agent_level * self.INDENTATION_SIZE)
        
        # Choose appropriate icon
        if is_subagent:
            icon = self.SUBAGENT_ICON
            prefix = "[Subagent] " if display_name else ""
        else:
            icon = self.MAIN_AGENT_ICON
            prefix = ""
        
        # Create the main text object
        text = Text()
        
        # Add indentation
        text.append(indent)
        
        # Add subagent prefix if needed
        if prefix:
            text.append(prefix, style="dim")
        
        # Add tool icon and name
        text.append(f"{icon} ", style=self._get_status_style(status))
        
        if self.expanded:
            content = self._format_expanded_view(tool_name, status)
        else:
            content = self._format_collapsed_view(tool_name, status)
        
        text.append(content)
        
        return text
    
    def _format_collapsed_view(self, tool_name: str, status: str) -> str:
        """Format the collapsed view of the tool call."""
        arguments = self.tool_data.get("arguments", {})
        
        # Format arguments for display
        args_display = self._format_arguments_brief(arguments)
        
        # Format status indicator
        status_indicator = self._get_status_indicator(status)
        
        # Build the collapsed display
        if args_display:
            main_text = f"{tool_name}({args_display})"
        else:
            main_text = f"{tool_name}()"
        
        if status_indicator:
            return f"{main_text} {status_indicator}"
        else:
            return main_text
    
    def _format_expanded_view(self, tool_name: str, status: str) -> str:
        """Format the expanded view of the tool call."""
        parts = [f"{tool_name}()"]
        
        # Add status information
        status_info = self._get_status_info_detailed(status)
        if status_info:
            parts.append(f"  Status: {status_info}")
        
        # Add arguments in expanded view
        arguments = self.tool_data.get("arguments", {})
        if arguments:
            parts.append("  Arguments:")
            args_text = self._format_arguments_detailed(arguments)
            parts.append(f"    {args_text}")
        
        # Add result or error in expanded view
        if status == "completed" and "result" in self.tool_data:
            result = self.tool_data["result"]
            parts.append("  Result:")
            result_text = self._format_result_brief(result)
            parts.append(f"    {result_text}")
        elif status == "error" and "error" in self.tool_data:
            error = self.tool_data["error"]
            parts.append("  Error:")
            parts.append(f"    {error}")
        
        # Add timing information
        duration = self.tool_data.get("duration")
        if duration:
            parts.append(f"  Duration: {duration:.2f}s")
        
        return "\n".join(parts)
    
    def _format_arguments_brief(self, arguments: Dict) -> str:
        """Format arguments for brief display in collapsed view."""
        if not arguments:
            return ""
        
        # Simple argument formatting for collapsed view
        if len(arguments) == 1:
            key, value = list(arguments.items())[0]
            value_str = self._format_value_brief(value)
            if len(value_str) <= 30:
                return f"{key}={value_str}"
            else:
                return f"{key}=..."
        elif len(arguments) <= 3:
            parts = []
            for key, value in list(arguments.items())[:3]:
                value_str = self._format_value_brief(value)
                if len(value_str) <= 20:
                    parts.append(f"{key}={value_str}")
                else:
                    parts.append(f"{key}=...")
            return ", ".join(parts)
        else:
            return f"{len(arguments)} args"
    
    def _format_arguments_detailed(self, arguments: Dict) -> str:
        """Format arguments for detailed display in expanded view."""
        if not arguments:
            return "None"
        
        parts = []
        for key, value in arguments.items():
            value_str = self._format_value_detailed(value)
            parts.append(f"{key}: {value_str}")
        
        return "\n    ".join(parts)
    
    def _format_value_brief(self, value: Any) -> str:
        """Format a value for brief display."""
        if isinstance(value, str):
            if len(value) <= 30:
                return f'"{value}"'
            else:
                return f'"{value[:27]}..."'
        elif isinstance(value, (int, float, bool)):
            return str(value)
        elif isinstance(value, list):
            return f"[{len(value)} items]"
        elif isinstance(value, dict):
            return f"{{{len(value)} keys}}"
        else:
            str_val = str(value)
            if len(str_val) <= 30:
                return str_val
            else:
                return f"{str_val[:27]}..."
    
    def _format_value_detailed(self, value: Any) -> str:
        """Format a value for detailed display."""
        if isinstance(value, str):
            if len(value) <= 100:
                return f'"{value}"'
            else:
                return f'"{value[:97]}..."'
        elif isinstance(value, (int, float, bool)):
            return str(value)
        elif isinstance(value, (list, dict)):
            import json
            try:
                json_str = json.dumps(value, indent=2)
                if len(json_str) <= 200:
                    return json_str
                else:
                    return f"{json_str[:197]}..."
            except:
                return str(value)
        else:
            return str(value)
    
    def _format_result_brief(self, result: str) -> str:
        """Format result for brief display."""
        if len(result) <= 100:
            return result
        else:
            return f"{result[:97]}..."
    
    def _get_status_indicator(self, status: str) -> str:
        """Get status indicator for collapsed view."""
        if status == "running":
            return "⏳"
        elif status == "completed":
            return "✅"
        elif status == "error":
            return "❌"
        else:
            return ""
    
    def _get_status_info_detailed(self, status: str) -> str:
        """Get detailed status information for expanded view."""
        if status == "running":
            return "Running..."
        elif status == "completed":
            duration = self.tool_data.get("duration")
            if duration:
                return f"Completed in {duration:.2f}s"
            else:
                return "Completed"
        elif status == "error":
            return "Error occurred"
        else:
            return status
    
    def _get_status_style(self, status: str) -> str:
        """Get the appropriate style for the tool status."""
        if status == "running":
            return "tool-running"
        elif status == "completed":
            return "tool-completed"
        elif status == "error":
            return "tool-error"
        else:
            return ""
    
    def _apply_css_classes(self) -> None:
        """Apply appropriate CSS classes based on tool properties."""
        is_subagent = self.tool_data.get("is_subagent", False)
        status = self.tool_data.get("status", "unknown")
        
        # Clear existing classes
        self.remove_class("main-agent-tool", "subagent-tool", 
                         "tool-running", "tool-completed", "tool-error")
        
        # Add agent type class
        if is_subagent:
            self.add_class("subagent-tool")
        else:
            self.add_class("main-agent-tool")
        
        # Add status class
        status_class = self._get_status_style(status)
        if status_class:
            self.add_class(status_class)
    
    def update_tool_data(self, new_tool_data: Dict[str, Any]) -> None:
        """
        Update the tool data and refresh the display.
        
        Args:
            new_tool_data: Updated tool information
        """
        self.tool_data.update(new_tool_data)
        self.update_display()
    
    def set_expanded(self, expanded: bool) -> None:
        """
        Set the expansion state and update display.
        
        Args:
            expanded: Whether to show expanded view
        """
        if self.expanded != expanded:
            self.expanded = expanded
            self.update_display()
    
    def toggle_expanded(self) -> None:
        """Toggle the expansion state."""
        self.set_expanded(not self.expanded)


def create_hierarchy_tool_display(
    tool_name: str,
    status: str = "running",
    agent_level: int = 0,
    is_subagent: bool = False,
    arguments: Optional[Dict] = None,
    result: Optional[str] = None,
    error: Optional[str] = None,
    duration: Optional[float] = None,
    display_name: Optional[str] = None,
    expanded: bool = False
) -> SubagentDisplay:
    """
    Factory function to create a SubagentDisplay widget.
    
    Args:
        tool_name: Name of the tool
        status: Tool status ("running", "completed", "error")
        agent_level: Hierarchy level (0 = main agent, 1+ = subagent)
        is_subagent: Whether this is a subagent tool
        arguments: Tool arguments
        result: Tool result (if completed)
        error: Error message (if failed)
        duration: Tool execution duration
        display_name: Display name for the agent
        expanded: Whether to show expanded view
        
    Returns:
        SubagentDisplay widget instance
    """
    tool_data = {
        "tool_name": tool_name,
        "status": status,
        "agent_level": agent_level,
        "is_subagent": is_subagent,
        "arguments": arguments or {},
        "display_name": display_name
    }
    
    if result is not None:
        tool_data["result"] = result
    if error is not None:
        tool_data["error"] = error
    if duration is not None:
        tool_data["duration"] = duration
    
    return SubagentDisplay(tool_data, expanded=expanded)