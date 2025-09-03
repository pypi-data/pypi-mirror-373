"""Centralized welcome message builder for consistent UI across all components."""

from pathlib import Path
from typing import List, Dict, Any, Optional
from ...config import ConfigManager
from ...utils import SystemStatus


class WelcomeMessageBuilder:
    """Centralized builder for all welcome messages and status displays."""
    
    def __init__(self, config_manager: ConfigManager, system_status: Optional[SystemStatus] = None):
        self.config_manager = config_manager
        self.system_status = system_status or SystemStatus(config_manager.workdir)
    
    def get_title_text(self) -> str:
        """Get the main title text."""
        return "🧙‍♂️ JUNO AI CLI"
    
    def get_title_with_rich_formatting(self) -> str:
        """Get the title with Rich formatting for display."""
        return "[bold blue]🧙‍♂️ JUNO AI CLI[/bold blue]"
    
    def get_separator_line(self) -> str:
        """Get the separator line for sections."""
        return "[dim]─────────────────────────────────────────────────────────────[/dim]"
    
    def build_status_parts(self) -> List[str]:
        """Build the status parts that appear in the welcome screen."""
        status_info = self.system_status.get_status_info()
        status_parts = []
        
        # Working Directory - show last 2 parts of path to save space
        workdir_path = Path(status_info['workdir'])
        if len(workdir_path.parts) > 2:
            workdir_display = f".../{workdir_path.parts[-2]}/{workdir_path.parts[-1]}"
        else:
            workdir_display = str(workdir_path)
        status_parts.append(f"📁 {workdir_display}")
        
        # Git Status
        git_icon = "✓" if "✓" in status_info['git_status'] else "✗"
        status_parts.append(f"🔀 Git {git_icon}")
        
        # API Key Status
        api_icon = "✓" if "✓" in status_info['api_key_status'] else "✗"
        status_parts.append(f"🔑 API {api_icon}")
        
        # Editor Status
        editor_name = status_info['editor'] if status_info['editor'] not in ["Not selected", "None"] else "None"
        editor_icon = "✓" if editor_name != "None" else "⚠"
        status_parts.append(f"📝 {editor_name} {editor_icon}")
        
        # Agent Status
        agent_status = self._get_agent_status()
        agent_icon = "✓" if "✓" in agent_status else "⚠"
        status_parts.append(f"🤖 Agent {agent_icon}")
        
        # Model Status
        config = self.config_manager.load_config()
        # Use slug for display if available, otherwise fallback to model_name
        model_slug = config.agent_config.model_slug
        model_name = config.agent_config.model_name if config.agent_config.model_name else "Not set"
        display_name = model_slug if model_slug else model_name
        model_icon = "✓" if model_name != "Not set" else "✗"
        # Truncate long model names for display
        display_model = display_name if len(display_name) <= 20 else display_name[:17] + "..."
        status_parts.append(f"🧠 {display_model} {model_icon}")
        
        # AGENTS.md file check
        agents_md_path = Path(status_info['workdir']) / "AGENTS.md"
        agents_icon = "✓" if agents_md_path.exists() else "✗"
        status_parts.append(f"📋 AGENTS.md {agents_icon}")
        
        return status_parts
    
    def build_status_parts_with_rich_formatting(self) -> List[str]:
        """Build status parts with Rich formatting for colored display."""
        status_info = self.system_status.get_status_info()
        status_parts = []
        
        # Working Directory - show last 2 parts of path to save space  
        workdir_path = Path(status_info['workdir'])
        if len(workdir_path.parts) > 2:
            workdir_display = f".../{workdir_path.parts[-2]}/{workdir_path.parts[-1]}"
        else:
            workdir_display = str(workdir_path)
        status_parts.append(f"📁 {workdir_display}")
        
        # Git Status
        git_icon = "[green]✓[/green]" if "✓" in status_info['git_status'] else "[red]✗[/red]"
        status_parts.append(f"🔀 Git {git_icon}")
        
        # API Key Status
        api_icon = "[green]✓[/green]" if "✓" in status_info['api_key_status'] else "[red]✗[/red]" 
        status_parts.append(f"🔑 API {api_icon}")
        
        # Editor Status
        editor_name = status_info['editor'] if status_info['editor'] not in ["Not selected", "None"] else "None"
        editor_icon = "[green]✓[/green]" if editor_name != "None" else "[yellow]⚠[/yellow]"
        status_parts.append(f"📝 {editor_name} {editor_icon}")
        
        # Agent Status
        agent_status = self._get_agent_status()
        agent_icon = "[green]✓[/green]" if "✓" in agent_status else "[yellow]⚠[/yellow]"
        status_parts.append(f"🤖 Agent {agent_icon}")
        
        # Model Status
        config = self.config_manager.load_config()
        # Use slug for display if available, otherwise fallback to model_name
        model_slug = config.agent_config.model_slug
        model_name = config.agent_config.model_name if config.agent_config.model_name else "Not set"
        display_name = model_slug if model_slug else model_name
        model_icon = "[green]✓[/green]" if model_name != "Not set" else "[red]✗[/red]"
        # Truncate long model names for display
        display_model = display_name if len(display_name) <= 20 else display_name[:17] + "..."
        status_parts.append(f"🧠 {display_model} {model_icon}")
        
        # AGENTS.md file check
        agents_md_path = Path(status_info['workdir']) / "AGENTS.md"
        agents_icon = "[green]✓[/green]" if agents_md_path.exists() else "[red]✗[/red]"
        status_parts.append(f"📋 AGENTS.md {agents_icon}")
        
        return status_parts
    
    def build_status_line(self, use_rich_formatting: bool = False) -> str:
        """Build the complete status line."""
        if use_rich_formatting:
            status_parts = self.build_status_parts_with_rich_formatting()
            return " [dim]│[/dim] ".join(status_parts)
        else:
            status_parts = self.build_status_parts()
            return " │ ".join(status_parts)
    
    def build_completion_message(self, use_rich_formatting: bool = False) -> str:
        """Build the setup completion message."""
        config = self.config_manager.load_config()
        
        if config.setup_completed:
            message = "✅ Ready to code! Type your questions below."
            return f"[green]{message}[/green]" if use_rich_formatting else message
        elif self.config_manager.has_api_key():
            message = "🚀 Ready to chat! Setup optional with /setup"
            return f"[green]{message}[/green]" if use_rich_formatting else message
        else:
            message = "🔧 Set API key with /apikey to start"
            # The app.py version had "start chatting" but welcome_screen.py had "start" - keeping "start" for consistency
            return f"[yellow]{message}[/yellow]" if use_rich_formatting else message
    
    def build_complete_welcome_parts(self, use_rich_formatting: bool = False) -> List[str]:
        """Build the complete welcome message parts."""
        welcome_parts = []
        
        # Title section
        title = self.get_title_with_rich_formatting() if use_rich_formatting else self.get_title_text()
        separator = self.get_separator_line() if use_rich_formatting else "─────────────────────────────────────────────────────────────"
        
        welcome_parts.extend([
            title,
            separator,
            ""
        ])
        
        # Status section
        status_line = self.build_status_line(use_rich_formatting)
        welcome_parts.extend([
            status_line,
            separator if use_rich_formatting else "─────────────────────────────────────────────────────────────",
            ""
        ])
        
        # Completion message
        completion_msg = self.build_completion_message(use_rich_formatting)
        welcome_parts.append(completion_msg)
        
        return welcome_parts
    
    def build_welcome_text(self, use_rich_formatting: bool = False) -> str:
        """Build the complete welcome message as a single string."""
        parts = self.build_complete_welcome_parts(use_rich_formatting)
        return "\n".join(parts)
    
    def _get_agent_status(self) -> str:
        """Get agent configuration status."""
        config = self.config_manager.load_config()
        
        # Check if model is configured
        if not self.config_manager.is_model_configured():
            return "✗ Model not configured"
        
        # Check if we have API key for AI features
        if not self.config_manager.has_api_key():
            return "⚠️ API key needed for AI features"
        
        # Check if agent is properly configured
        if config.project_description:
            return "✓ Ready for AI assistance"
        else:
            return "⚠️ Project description recommended"