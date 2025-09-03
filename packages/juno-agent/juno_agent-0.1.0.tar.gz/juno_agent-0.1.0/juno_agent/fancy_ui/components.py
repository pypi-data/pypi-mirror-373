"""Utility components for the TUI application."""

from textual.widgets import Static


class DynamicFooter(Static):
    """Dynamic footer that shows context-aware hints, token usage, and cost."""
    
    def __init__(self):
        super().__init__()
        self.add_class("footer")
        self.has_tool_calls = False
        self.is_agent_running = False
        self.is_selection_mode = False
        self.total_tokens = 0
        self.total_cost = 0.0
        self.update_content()
    
    def update_content(self):
        """Update footer content based on current context."""
        # Build left side with keyboard shortcuts
        left_parts = []
        
        if self.is_selection_mode:
            # Show selection mode specific shortcuts
            left_parts.extend([
                "📋 Ctrl+C: Copy Selected",
                "F2: Copy All", 
                "Right-Click: Copy",
                "Escape: Exit Selection",
                "Ctrl+S: Exit All Selections"
            ])
        else:
            # Normal mode shortcuts
            if self.has_tool_calls:
                left_parts.append("Ctrl+R: Toggle Tool Details")
            left_parts.extend([
                "🖱️ Double-Click: Select Mode",
                "F2: Copy",
                "Ctrl+N: New Chat", 
                "F1: History",
                "Ctrl+Q: Quit"
            ])
            if not self.has_tool_calls:
                left_parts.extend(["Type / for commands", "Ctrl+J: New Line"])
        
        left_content = " | ".join(left_parts)
        
        # Build right side with token/cost info when agent is active
        if self.is_agent_running and (self.total_tokens > 0 or self.total_cost > 0):
            # Format tokens with commas for readability
            tokens_str = f"{self.total_tokens:,}" if self.total_tokens > 0 else "0"
            cost_str = f"${self.total_cost:.4f}" if self.total_cost > 0 else "$0.0000"
            right_content = f"Tokens: {tokens_str} | Cost: {cost_str}"
            
            # Combine left and right with padding
            content = f"{left_content} | {right_content}"
        else:
            content = left_content
        
        self.update(content)
    
    def set_tool_calls_present(self, present: bool):
        """Update whether tool calls are present in the conversation."""
        if self.has_tool_calls != present:
            self.has_tool_calls = present
            self.update_content()
    
    def set_agent_running(self, running: bool):
        """Update whether the agent is currently running."""
        if self.is_agent_running != running:
            self.is_agent_running = running
            self.update_content()
    
    def set_selection_mode(self, active: bool):
        """Update whether selection mode is active."""
        if self.is_selection_mode != active:
            self.is_selection_mode = active
            self.update_content()
    
    def update_usage_stats(self, tokens: int, cost: float):
        """Update token usage and cost statistics."""
        if self.total_tokens != tokens or self.total_cost != cost:
            self.total_tokens = tokens
            self.total_cost = cost
            self.update_content()
    
    def reset_usage_stats(self):
        """Reset token usage and cost statistics."""
        self.total_tokens = 0
        self.total_cost = 0.0
        self.update_content()