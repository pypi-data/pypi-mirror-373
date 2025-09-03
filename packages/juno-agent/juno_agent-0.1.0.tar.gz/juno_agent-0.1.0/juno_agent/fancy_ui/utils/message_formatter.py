"""Message formatting utilities."""

from datetime import datetime
from rich.text import Text
from rich.markup import escape


def format_timestamp(dt: datetime = None) -> str:
    """Format timestamp for display."""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%H:%M:%S")


def format_user_message(content: str, timestamp: datetime = None) -> str:
    """Format user message with proper styling."""
    time_str = format_timestamp(timestamp)
    # Escape any rich markup in user content
    safe_content = escape(content)
    return f"> {safe_content}"


def format_agent_message(content: str, timestamp: datetime = None) -> str:
    """Format agent message with proper styling."""
    time_str = format_timestamp(timestamp)
    # Agent messages can contain rich markup
    return f"• {content}"


def format_system_message(content: str, timestamp: datetime = None) -> str:
    """Format system message with proper styling."""
    time_str = format_timestamp(timestamp)
    return f"[dim]ℹ {content}[/dim]"