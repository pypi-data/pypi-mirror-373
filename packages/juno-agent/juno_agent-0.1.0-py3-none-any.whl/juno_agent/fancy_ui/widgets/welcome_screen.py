"""Welcome screen widget for the Textual TUI application."""

from datetime import datetime
from pathlib import Path
from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Label
from textual.widget import Widget
from rich.text import Text
from rich.panel import Panel

from ...config import ConfigManager
from ...utils import SystemStatus
from ..utils.welcome_message_builder import WelcomeMessageBuilder


class WelcomeScreen(Widget):
    """Welcome screen widget that displays system information and status."""
    
    DEFAULT_CSS = """
    WelcomeScreen {
        height: auto;
        max-height: 12;
        margin: 1;
        padding: 1;
        background: $surface;
        border: round $primary;
    }
    
    .welcome-container {
        height: auto;
        align: center middle;
    }
    
    .juno-ascii {
        color: $primary;
        text-style: bold;
        text-align: center;
        margin: 0 0 2 0;
    }
    
    .welcome-title {
        color: $primary;
        text-style: bold;
        text-align: center;
        margin: 0 0 1 0;
    }
    
    .status-section {
        margin: 1 0;
        padding: 1;
        background: $boost;
        border: round $accent;
    }
    
    .status-item {
        margin: 0 0 1 0;
        color: $text;
    }
    
    .status-value {
        color: $primary;
    }
    
    .status-good {
        color: $success;
    }
    
    .status-warning {
        color: $warning;
    }
    
    .status-error {
        color: $error;
    }
    
    .setup-message {
        text-align: center;
        margin: 2 0 0 0;
        padding: 1;
        border: round;
    }
    
    .setup-complete {
        color: $success;
        background: $boost;
        border: round $success;
    }
    
    .setup-incomplete {
        color: $warning;
        background: $boost;
        border: round $warning;
    }
    """
    
    def __init__(self, config_manager: ConfigManager, system_status: SystemStatus):
        super().__init__()
        self.config_manager = config_manager
        self.system_status = system_status
        
    def compose(self):
        """Compose the welcome screen UI."""
        # Use the centralized welcome message builder
        welcome_builder = WelcomeMessageBuilder(self.config_manager, self.system_status)
        
        with Vertical(classes="welcome-container"):
            # Welcome title
            yield Static(welcome_builder.get_title_text(), classes="welcome-title")
            
            # Status section
            with Horizontal(classes="status-section"):
                status_line = welcome_builder.build_status_line(use_rich_formatting=False)
                yield Static(status_line, classes="status-item")
            
            # Setup completion message
            completion_message = welcome_builder.build_completion_message(use_rich_formatting=False)
            
            # Apply appropriate CSS class based on message content
            if "✅" in completion_message or "🚀" in completion_message:
                css_class = "setup-message setup-complete"
            else:
                css_class = "setup-message setup-incomplete"
                
            yield Static(completion_message, classes=css_class)
    
    def _get_juno_ascii(self) -> str:
        """Get the JUNO ASCII art."""
        return """  ██ ██   ██ ███   ██  ██████      █████  ██ 
  ██ ██   ██ ████  ██ ██    ██    ██   ██ ██ 
  ██ ██   ██ ██ ██ ██ ██    ██    ███████ ██ 
██ ██ ██   ██ ██  ████ ██    ██    ██   ██ ██ 
 ███   █████  ██   ███  ██████     ██   ██ ██ """
    

class StatusIndicator(Static):
    """A simple status indicator widget."""
    
    def __init__(self, label: str, status: str, status_type: str = "info"):
        super().__init__()
        self.label = label
        self.status = status
        self.status_type = status_type
        self.update_display()
    
    def update_display(self):
        """Update the status display."""
        status_colors = {
            "good": "green",
            "warning": "yellow", 
            "error": "red",
            "info": "blue"
        }
        
        color = status_colors.get(self.status_type, "white")
        content = f"[bold]{self.label}:[/bold] [{color}]{self.status}[/{color}]"
        self.update(content)


class WelcomeInfoPanel(Static):
    """Information panel for the welcome screen."""
    
    DEFAULT_CSS = """
    WelcomeInfoPanel {
        margin: 1;
        padding: 1;
        background: $boost;
        border: round $accent;
        height: auto;
    }
    """
    
    def __init__(self, title: str, content: str, status_type: str = "info"):
        super().__init__()
        self.title = title
        self.content = content
        self.status_type = status_type
        self.update_panel()
    
    def update_panel(self):
        """Update the panel content."""
        border_colors = {
            "good": "green",
            "warning": "yellow",
            "error": "red", 
            "info": "blue"
        }
        
        border_color = border_colors.get(self.status_type, "blue")
        
        # Create Rich panel
        panel = Panel(
            self.content,
            title=self.title,
            border_style=border_color,
            expand=False
        )
        
        self.update(panel)