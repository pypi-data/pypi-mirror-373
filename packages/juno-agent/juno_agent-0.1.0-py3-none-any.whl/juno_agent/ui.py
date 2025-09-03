"""User interface components for juno-agent."""

import asyncio
import getpass
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

import requests
import json

# Try to import readline, fall back gracefully on Windows
try:
    import readline
    import rlcompleter
    HAS_READLINE = True
except ImportError:
    HAS_READLINE = False

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.spinner import Spinner
from rich.text import Text
from rich.table import Table
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Header, Footer, Input, Static, ListView, ListItem, Label
from textual.events import Key

from .config import ConfigManager, Config
from .utils import SystemStatus, open_browser
from .scanner import ProjectScanner
from .editors import MCPServerInstaller
from .agent import TinyAgentChat, ProjectAnalysisAgent
from .tiny_agent import TinyCodeAgentChat, TinyCodeAgentManager


class EditorSelectorApp(App):
    """Textual app for editor selection with arrow key navigation."""
    
    CSS = """
    Screen {
        align: center middle;
    }
    
    #main_container {
        width: 80;
        height: auto;
        border: thick $primary;
        background: $surface;
    }
    
    #title {
        dock: top;
        height: 3;
        content-align: center middle;
        background: $primary;
        color: $text;
        text-style: bold;
    }
    
    #instructions {
        dock: bottom;
        height: 3;
        content-align: center middle;
        background: $accent;
        color: $text;
        text-style: dim;
    }
    
    ListView {
        height: 1fr;
        padding: 1;
    }
    
    ListItem {
        height: 3;
        padding: 0 2;
    }
    
    ListItem > Label {
        width: 1fr;
        height: 1fr;
        content-align: left middle;
    }
    
    ListItem:hover {
        background: $accent;
    }
    
    .recommended {
        color: $success;
        text-style: bold;
    }
    
    .supported {
        color: $warning;
    }
    """
    
    def __init__(self, editors: List[str]):
        super().__init__()
        self.editors = editors
        self.selected_editor = None
        self.title = "🧙‍♂️ juno-agent - Editor Selection"
    
    def compose(self) -> ComposeResult:
        """Compose the UI."""
        with Container(id="main_container"):
            yield Static("📝 Select Your Preferred Code Editor", id="title")
            
            # Create list items
            list_items = []
            for i, editor in enumerate(self.editors, 1):
                if editor in ["Claude Code", "Cursor", "Windsurf"]:
                    label_text = f"{i}. {editor} ✨ (Recommended - Full MCP support)"
                    css_class = "recommended"
                else:
                    label_text = f"{i}. {editor} ⚡ (Supported - Basic integration)"
                    css_class = "supported"
                
                list_item = ListItem(Label(label_text, classes=css_class))
                list_items.append(list_item)
            
            yield ListView(*list_items, id="editor_list")
            yield Static("↑↓ Navigate • Enter: Select • Esc: Back • q: Quit", id="instructions")
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle editor selection."""
        selected_index = event.list_view.index
        if selected_index is not None:
            self.selected_editor = self.editors[selected_index]
            self.exit(self.selected_editor)
    
    def on_key(self, event: Key) -> None:
        """Handle key presses."""
        if event.key == "q":
            self.exit(None)
        elif event.key == "escape":
            self.exit(None)
        elif event.key.isdigit():
            # Allow number selection
            try:
                num = int(event.key)
                if 1 <= num <= len(self.editors):
                    self.selected_editor = self.editors[num - 1]
                    self.exit(self.selected_editor)
            except (ValueError, IndexError):
                pass


class ModelSelectorApp(App):
    """Textual app for model selection with detailed information."""
    
    CSS = """
    Screen {
        align: center middle;
    }
    
    #main_container {
        width: 100;
        height: auto;
        border: thick $primary;
        background: $surface;
    }
    
    #title {
        dock: top;
        height: 3;
        content-align: center middle;
        background: $primary;
        color: $text;
        text-style: bold;
    }
    
    #instructions {
        dock: bottom;
        height: 3;
        content-align: center middle;
        background: $accent;
        color: $text;
        text-style: dim;
    }
    
    ListView {
        height: 1fr;
        padding: 1;
    }
    
    ListItem {
        height: 4;
        padding: 0 2;
    }
    
    ListItem > Label {
        width: 1fr;
        height: 1fr;
        content-align: left middle;
    }
    
    ListItem:hover {
        background: $accent;
    }
    
    .premium {
        color: $success;
        text-style: bold;
    }
    
    .standard {
        color: $warning;
    }
    
    .free {
        color: $text;
    }
    """
    
    def __init__(self, models: List[Dict[str, Any]]):
        super().__init__()
        self.models = models
        self.selected_model = None
        self.title = "🧙‍♂️ juno-agent - Model Selection"
    
    def compose(self) -> ComposeResult:
        """Compose the UI."""
        with Container(id="main_container"):
            yield Static("🤖 Select Your AI Model", id="title")
            
            # Create list items
            list_items = []
            for i, model in enumerate(self.models, 1):
                # Get cost tier symbol
                cost_tier = model.get("cost_tier", "standard")
                cost_symbol = {"premium": "💎", "standard": "⚡", "free": "🆓"}.get(cost_tier, "⚡")
                
                # Format the label
                label_text = f"{i}. {model['name']} ({model['provider']}) {cost_symbol}\n"
                label_text += f"    {model['model_name']} • Temp: {model['temperature']}"
                
                css_class = cost_tier
                
                list_item = ListItem(Label(label_text, classes=css_class))
                list_items.append(list_item)
            
            yield ListView(*list_items, id="model_list")
            yield Static("↑↓ Navigate • Enter: Select • Esc: Back • q: Quit", id="instructions")
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle model selection."""
        selected_index = event.list_view.index
        if selected_index is not None:
            self.selected_model = self.models[selected_index]
            self.exit(self.selected_model)
    
    def on_key(self, event: Key) -> None:
        """Handle key presses."""
        if event.key == "q":
            self.exit(None)
        elif event.key == "escape":
            self.exit(None)
        elif event.key.isdigit():
            # Allow number selection
            try:
                num = int(event.key)
                if 1 <= num <= len(self.models):
                    self.selected_model = self.models[num - 1]
                    self.exit(self.selected_model)
            except (ValueError, IndexError):
                pass


class CommandCompleter:
    """Enhanced tab completer for chat commands with inline completion."""
    
    def __init__(self, commands: List[str]):
        self.commands = commands
        self.current_candidates = []
        self.last_text = ""
        self.completion_index = 0
    
    def complete(self, text: str, state: int) -> Optional[str]:
        """Complete function for readline with inline completion."""
        if state == 0:
            # Reset completion state
            self.last_text = text
            self.completion_index = 0
            
            # Generate candidates for this completion
            if text.startswith('/'):
                # Complete commands
                self.current_candidates = [
                    cmd for cmd in self.commands 
                    if cmd.startswith(text)
                ]
            else:
                # No completion for non-commands
                self.current_candidates = []
        
        try:
            return self.current_candidates[state]
        except IndexError:
            return None
    
    def get_best_match(self, text: str) -> Optional[str]:
        """Get the best completion match for the given text."""
        if not text.startswith('/'):
            return None
            
        candidates = [cmd for cmd in self.commands if cmd.startswith(text)]
        
        if not candidates:
            return None
        elif len(candidates) == 1:
            return candidates[0]
        else:
            # If exact match exists in candidates, cycle to next one
            if text in candidates:
                try:
                    current_index = candidates.index(text)
                    return candidates[(current_index + 1) % len(candidates)]
                except ValueError:
                    return candidates[0]
            else:
                # Return first match
                return candidates[0]
    
    def display_matches(self, substitution: str, matches: List[str], longest_match_length: int) -> None:
        """Display available matches when there are multiple options."""
        if not matches:
            return
            
        if len(matches) == 1:
            # Single match - let it complete inline, no display needed
            return
        elif len(matches) <= 8:
            # Show all matches compactly
            matches_str = " │ ".join(matches)
            print(f"\n[{matches_str}]")
        else:
            # Show first few matches with count
            shown_matches = " │ ".join(matches[:6])
            remaining = len(matches) - 6
            print(f"\n[{shown_matches} │ ...+{remaining} more]")
        
        # Reprint the prompt
        print("🔵 You │ ", end="")
        sys.stdout.flush()


class AutoCompleteInput:
    """Enhanced input handler with inline tab completion like codex-cli."""
    
    def __init__(self, commands: List[str], console: Console, config_dir: Optional[Path] = None):
        self.commands = commands
        self.console = console
        self.has_readline = HAS_READLINE
        self.history_file = None
        
        if config_dir:
            self.history_file = config_dir / ".history"
        
        if self.has_readline:
            self.completer = CommandCompleter(commands)
            
            # Set up readline for inline completion
            readline.set_completer(self._inline_completer)
            readline.set_completer_delims(' \t\n')
            
            # Configure readline for smart completion behavior
            readline.parse_and_bind("tab: complete")
            readline.parse_and_bind("set completion-ignore-case on")
            readline.parse_and_bind("set show-all-if-ambiguous on")  # Show matches when ambiguous
            readline.parse_and_bind("set completion-query-items 0")  # Never ask before showing
            readline.parse_and_bind("set print-completions-horizontally on")
            
            # Disable automatic match display
            if hasattr(readline, 'set_completion_display_matches_hook'):
                readline.set_completion_display_matches_hook(self.completer.display_matches)
            
            # Enable history
            if self.history_file:
                try:
                    readline.read_history_file(str(self.history_file))
                    readline.set_history_length(1000)
                except FileNotFoundError:
                    pass
    
    def _inline_completer(self, text: str, state: int) -> Optional[str]:
        """Enhanced completer that provides direct inline completion for single matches."""
        # Use the standard completer - this will populate current_candidates at state=0
        result = self.completer.complete(text, state)
        
        if state == 0 and result:
            # Check if there's only one candidate
            candidates = [cmd for cmd in self.commands if cmd.startswith(text)]
            if len(candidates) == 1:
                # Single match - return it directly for inline completion
                return result
            else:
                # Multiple matches - let readline handle showing them
                return result
        
        return result
    
    def input(self, prompt: str = "") -> str:
        """Get input with enhanced inline tab completion."""
        try:
            if self.has_readline:
                # Use readline with enhanced completion
                user_input = input(prompt)
                
                # Save to history
                if user_input.strip():
                    readline.add_history(user_input.strip())
                    try:
                        if self.history_file:
                            readline.write_history_file(str(self.history_file))
                    except:
                        pass
            else:
                # Enhanced fallback with inline suggestions
                user_input = self._fallback_input_with_completion(prompt)
            
            return user_input
        except (EOFError, KeyboardInterrupt):
            raise KeyboardInterrupt()
    
    def update_commands(self, new_commands: List[str]):
        """Update the available commands for autocomplete."""
        self.commands = new_commands
        if self.has_readline:
            self.completer = CommandCompleter(new_commands)
            readline.set_completer(self._inline_completer)
    
    def _fallback_input_with_completion(self, prompt: str) -> str:
        """Fallback input method with completion hints for systems without readline."""
        self.console.print(f"[dim]Hint: Type commands starting with / and press Tab to see completions[/dim]")
        
        while True:
            try:
                user_input = input(prompt)
                
                # Check if user typed 'tab' or wants completion
                if user_input.lower() == 'tab' or user_input.endswith('\t'):
                    self.console.print("[yellow]Tab completion not available. Type / followed by letters to see available commands.[/yellow]")
                    continue
                
                # Show suggestions if user is typing a command
                if user_input.startswith('/') and len(user_input) > 1:
                    suggestions = self.get_suggestions(user_input)
                    if len(suggestions) > 1:
                        # Show available options
                        suggestions_str = " │ ".join(suggestions)
                        self.console.print(f"[cyan]Available completions: {suggestions_str}[/cyan]")
                        self.console.print("[dim]Continue typing to narrow down, or type one of the above[/dim]")
                        continue
                    elif len(suggestions) == 1 and suggestions[0] != user_input:
                        # Suggest the single match
                        self.console.print(f"[green]Did you mean: {suggestions[0]}? (y/n)[/green]")
                        confirm = input().strip().lower()
                        if confirm in ['y', 'yes', '']:
                            return suggestions[0]
                        else:
                            continue
                
                return user_input
                
            except (EOFError, KeyboardInterrupt):
                raise KeyboardInterrupt
    
    def get_suggestions(self, text: str) -> List[str]:
        """Get completion suggestions for given text."""
        if text.startswith('/'):
            return [cmd for cmd in self.commands if cmd.startswith(text)]
        return []
    
    def cleanup(self):
        """Clean up readline settings."""
        if self.has_readline:
            try:
                if self.history_file:
                    readline.write_history_file(str(self.history_file))
                else:
                    readline.write_history_file()
            except:
                pass
    
    def show_completions(self, text: str) -> List[str]:
        """Show available completions for the given text (for testing)."""
        return self.get_suggestions(text)


class WelcomeScreen:
    """Welcome screen display."""
    
    def __init__(self, config_manager: ConfigManager, system_status: SystemStatus):
        self.config_manager = config_manager
        self.system_status = system_status
        self.console = Console()
    
    def display(self) -> None:
        """Display welcome screen."""
        config = self.config_manager.load_config()
        status_info = self.system_status.get_status_info()
        
        # JUNO AI ASCII Art
        juno_ascii = """[bold cyan]
   ██ ██   ██ ███   ██  ██████      █████  ██ 
   ██ ██   ██ ████  ██ ██    ██    ██   ██ ██ 
   ██ ██   ██ ██ ██ ██ ██    ██    ███████ ██ 
██ ██ ██   ██ ██  ████ ██    ██    ██   ██ ██ 
 ███   █████  ██   ███  ██████     ██   ██ ██ 
[/bold cyan]"""
        
        self.console.print(juno_ascii)
        
        welcome_text = f"""[bold blue]Welcome to JUNO AI CLI![/bold blue]

[bold]Current Status:[/bold]
• [blue]Working Directory:[/blue] {status_info['workdir']}
• [blue]Git Status:[/blue] {status_info['git_status']}
• [blue]API Key:[/blue] {status_info['api_key_status']}
• [blue]Selected Editor:[/blue] {status_info['editor']}

"""
        
        if config.setup_completed:
            welcome_text += "[green]✓ Setup completed! You can use the chat interface or commands.[/green]"
        elif self.config_manager.has_api_key():
            welcome_text += "[green]🚀 Ready to chat! Setup optional - run setup wizard if you want to configure more features.[/green]"
        else:
            welcome_text += "[yellow]🔧 Set your API key with '/apikey' command to start chatting with AI assistant.[/yellow]"
        
        panel = Panel.fit(
            welcome_text,
            title="JUNO AI CLI",
            border_style="blue",
        )
        
        self.console.print(panel)


class SetupWizard:
    """Step-by-step setup wizard."""
    
    def __init__(self, config_manager: ConfigManager, system_status: SystemStatus):
        self.config_manager = config_manager
        self.system_status = system_status
        self.console = Console()
        self.mcp_installer = MCPServerInstaller(config_manager.workdir)
    
    def run(self) -> None:
        """Run the setup wizard."""
        self.console.print("\n[bold blue]Setup Wizard[/bold blue]")
        self.console.print("Let's configure juno-agent for your project.\n")
        
        config = self.config_manager.load_config()
        
        # Step 1: API Key
        if not self.config_manager.has_api_key():
            self._setup_api_key()
        
        # Step 2: Editor Selection
        if not config.editor:
            # For setup wizard, use a sync version to avoid event loop issues
            self._setup_editor_sync()
        
        # Step 3: Project Description
        if not config.project_description:
            self._setup_project_description()
        
        # Step 4: Model Configuration
        if not self.config_manager.is_model_configured():
            self._setup_model_configuration()
        
        # Step 5: Git Setup (if needed)
        if not self.system_status.is_git_controlled():
            self._suggest_git_setup()
        
        # Mark setup as completed
        self.config_manager.update_config(setup_completed=True)
        
        self.console.print("\n[green]✓ Setup completed![/green]")
        self.console.print("You can now use the chat interface or run commands.\n")
    
    def _setup_api_key(self) -> None:
        """Set up API key."""
        self.console.print("[bold]Step 1: API Key Configuration[/bold]")
        self.console.print("You need an ASKBUDI API key to use this tool.")
        
        if Confirm.ask("Do you have an ASKBUDI API key?", default=True):
            api_key = getpass.getpass("Enter your API key (***): ")
            if api_key.strip():
                # Validate API key with backend
                self.console.print("[blue]Validating API key with backend...[/blue]")
                
                try:
                    validation_result = asyncio.run(
                        self.config_manager.validate_api_key_with_backend(api_key.strip())
                    )
                    
                    if validation_result.get("valid"):
                        self.config_manager.set_api_key(api_key.strip())
                        user_level = validation_result.get("user_level", "unknown")
                        self.console.print(f"[green]✓ API key validated successfully (Level: {user_level})[/green]")
                    else:
                        error = validation_result.get("error", "Unknown error")
                        self.console.print(f"[red]✗ API key validation failed: {error}[/red]")
                        return self._setup_api_key()
                        
                except Exception as e:
                    self.console.print(f"[yellow]⚠️  Could not validate API key (network issue): {e}[/yellow]")
                    if Confirm.ask("Save API key anyway? (You can validate it later)", default=True):
                        self.config_manager.set_api_key(api_key.strip())
                        self.console.print("[yellow]API key saved (validation pending)[/yellow]")
                    else:
                        return self._setup_api_key()
            else:
                self.console.print("[red]Invalid API key[/red]")
                return self._setup_api_key()
        else:
            self.console.print("You can get an API key from: https://askbudi.ai")
            if Confirm.ask("Open askbudi.ai in your browser?", default=True):
                if open_browser("https://askbudi.ai"):
                    self.console.print("Browser opened. Get your API key and come back.")
                else:
                    self.console.print("Could not open browser. Please visit https://askbudi.ai manually.")
            
            return self._setup_api_key()
    
    def _setup_editor_sync(self) -> None:
        """Set up editor selection without Textual (sync version for setup wizard)."""
        self.console.print("\n[bold]Step 2: Editor Selection[/bold]")
        
        supported_editors = self.mcp_installer.get_supported_editor_names()
        editors = supported_editors + ["Other"]
        
        # Simple numbered selection instead of Textual
        selected_editor = self._simple_editor_selection(editors)
        
        if selected_editor == "Other":
            from rich.prompt import Prompt
            selected_editor = Prompt.ask("Enter editor name").strip()
            if not selected_editor:
                self.console.print("[red]Editor name cannot be empty[/red]")
                return self._setup_editor_sync()
        
        self.config_manager.update_config(editor=selected_editor)
        self.console.print(f"[green]✓ Editor set to: {selected_editor}[/green]")
        
        # Try to install MCP server for the selected editor
        if selected_editor != "Other":
            self._install_mcp_server_for_setup(selected_editor)
    
    def _simple_editor_selection(self, editors: List[str]) -> str:
        """Simple numbered editor selection."""
        from rich.prompt import Prompt
        from rich.table import Table
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("#", style="cyan", width=3)
        table.add_column("Editor", style="green")
        
        for i, editor in enumerate(editors, 1):
            table.add_row(str(i), editor)
        
        self.console.print("\n[bold]Available editors:[/bold]")
        self.console.print(table)
        
        while True:
            try:
                choice = Prompt.ask("\n[bold blue]Select editor by number[/bold blue]", default="1")
                if choice.isdigit():
                    index = int(choice) - 1
                    if 0 <= index < len(editors):
                        return editors[index]
                self.console.print("[red]Invalid choice. Please enter a valid number.[/red]")
            except (ValueError, KeyboardInterrupt):
                self.console.print("[red]Invalid input or cancelled.[/red]")
                return editors[0]  # Default to first editor
    
    def _install_mcp_server_for_setup(self, selected_editor: str) -> None:
        """Install MCP server for selected editor during setup."""
        supported_editors = self.mcp_installer.get_supported_editor_names()
        
        if (selected_editor in supported_editors and 
            self.config_manager.has_api_key() and
            Confirm.ask(f"Install MCP server for {selected_editor}?", default=True)):
            
            api_key = self.config_manager.get_api_key()
            success, message = self.mcp_installer.install_mcp_server(selected_editor, api_key)
            
            if success:
                self.console.print(f"[green]✓ {message}[/green]")
                self.config_manager.update_config(mcp_server_installed=True)
            else:
                self.console.print(f"[red]✗ {message}[/red]")
    
    async def _setup_editor(self) -> None:
        """Set up editor selection with arrow key navigation."""
        self.console.print("\n[bold]Step 2: Editor Selection[/bold]")
        
        supported_editors = self.mcp_installer.get_supported_editor_names()
        editors = supported_editors + ["Other"]
        
        # Use an interactive selector with arrow key navigation
        selected_editor = await self._interactive_editor_selection(editors)
        
        if selected_editor == "Other":
            selected_editor = Prompt.ask("Enter editor name").strip()
            if not selected_editor:
                self.console.print("[red]Editor name cannot be empty[/red]")
                return
        
        if selected_editor:
            self.config_manager.update_config(editor=selected_editor)
            self.console.print(f"[green]✓ Editor set to {selected_editor}[/green]")
            
            # If it's a supported editor and we have an API key, offer to install MCP server
            if (selected_editor in supported_editors and 
                self.config_manager.has_api_key() and
                Confirm.ask(f"Install MCP server for {selected_editor}?", default=True)):
                
                api_key = self.config_manager.get_api_key()
                success, message = self.mcp_installer.install_mcp_server(selected_editor, api_key)
                
                if success:
                    self.console.print(f"[green]✓ {message}[/green]")
                    self.config_manager.update_config(mcp_server_installed=True)
                else:
                    self.console.print(f"[red]✗ {message}[/red]")
    
    async def _interactive_editor_selection(self, editors: List[str]) -> str:
        """Modern editor selection with arrow key navigation using Textual and Rich fallback."""
        import os
        from rich.prompt import Prompt
        from rich.table import Table
        import time
        
        # First, try to use Textual for full arrow key navigation
        try:
            # Check if we have a proper terminal for Textual
            if os.isatty(0) and os.isatty(1) and os.environ.get('TERM'):
                self.console.print("\n[bold cyan]🎯 Launching interactive editor selector...[/bold cyan]")
                self.console.print("[dim]Use ↑↓ arrows to navigate, Enter to select, or number keys for quick selection[/dim]\n")
                
                # Small delay to let user read the message
                time.sleep(1)
                
                # Launch Textual app
                app = EditorSelectorApp(editors)
                selected_editor = await app.run_async()
                
                if selected_editor:
                    # Show confirmation
                    self.console.print(f"\n[bold green]✅ Selected: {selected_editor}[/bold green]")
                    
                    # Quick confirmation animation
                    with self.console.status(f"[bold green]Configuring {selected_editor}...[/bold green]", spinner="dots"):
                        time.sleep(0.8)
                    
                    self.console.print(f"[bold green]✅ {selected_editor} configured successfully![/bold green]\n")
                    return selected_editor
                else:
                    self.console.print("\n[yellow]Selection cancelled.[/yellow]")
                    return ""
                    
        except Exception as e:
            # Textual failed, fall back to Rich-based selection
            self.console.print(f"[dim]Note: Advanced UI unavailable ({str(e)[:50]}...), using fallback mode[/dim]\n")
        
        # Fallback: Rich-based selection (previous implementation)
        return self._rich_editor_selection(editors)
    
    def _rich_editor_selection(self, editors: List[str]) -> str:
        """Rich-based editor selection fallback."""
        from rich.prompt import Prompt
        from rich.table import Table
        import time
        
        # Create a beautiful editor selection display
        def create_editor_table(highlight_index: int = -1) -> Table:
            """Create a Rich table for editor selection."""
            table = Table(
                title="[bold cyan]📝 Select Your Preferred Code Editor[/bold cyan]",
                title_style="bold cyan",
                border_style="bright_blue",
                header_style="bold magenta",
                show_header=True,
                show_lines=True,
                expand=False,
                min_width=60
            )
            
            table.add_column("#", style="dim cyan", justify="center", width=3)
            table.add_column("Editor", style="bold white", min_width=15)
            table.add_column("Status", style="dim", min_width=15)
            table.add_column("Notes", style="dim", min_width=20)
            
            for i, editor in enumerate(editors, 1):
                # Determine styling and status
                if editor in ["Claude Code", "Cursor", "Windsurf"]:
                    status = "[green]✨ Recommended[/green]"
                    notes = "Full MCP support"
                    editor_style = "blue"
                else:
                    status = "[yellow]⚡ Supported[/yellow]"
                    notes = "Basic integration"
                    editor_style = "white"
                
                # Highlight selected row
                if i == highlight_index:
                    number_style = "bold green on bright_blue"
                    editor_display = f"[bold green on bright_blue] ▶ {editor} [/bold green on bright_blue]"
                else:
                    number_style = "dim cyan"
                    editor_display = f"[{editor_style}]{editor}[/{editor_style}]"
                
                table.add_row(
                    f"[{number_style}]{i}[/{number_style}]",
                    editor_display,
                    status,
                    notes
                )
            
            return table
        
        # Display the table first
        table = create_editor_table()
        self.console.print("\n")  # Add some space
        self.console.print(table)
        
        # Create helpful instruction panel
        instruction_panel = Panel(
            "[bold white]How to select:[/bold white]\n\n"
            "• [cyan]Type the number[/cyan] (1-{}) and press Enter\n"
            "• [cyan]Type the editor name[/cyan] directly\n"
            "• [dim]Press Enter for default (Claude Code)[/dim]\n"
            "• [dim]Type 'q' to quit[/dim]".format(len(editors)),
            title="[bold]📋 Instructions[/bold]",
            border_style="bright_green",
            padding=(0, 1),
            expand=False
        )
        self.console.print("\n")
        self.console.print(instruction_panel)
        
        # Interactive selection loop with better UX
        while True:
            try:
                self.console.print("\n[bold blue]🎯 Your choice:[/bold blue]", end=" ")
                
                # Use Rich's Prompt for cleaner input handling
                choice = Prompt.ask(
                    "",
                    default="1",
                    show_default=False,
                    console=self.console
                ).strip()
                
                # Handle quit
                if choice.lower() in ['q', 'quit', 'exit']:
                    self.console.print("[yellow]Selection cancelled.[/yellow]")
                    return ""
                
                # Try to parse as number first
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(editors):
                        selected_editor = editors[choice_num - 1]
                        
                        # Show confirmation with highlight
                        confirmation_table = create_editor_table(choice_num)
                        self.console.print("\n[bold green]✅ Selected:[/bold green]")
                        self.console.print(confirmation_table)
                        
                        # Quick confirmation animation
                        with self.console.status(f"[bold green]Configuring {selected_editor}...[/bold green]", spinner="dots"):
                            time.sleep(0.8)
                        
                        self.console.print(f"[bold green]✅ {selected_editor} configured successfully![/bold green]\n")
                        return selected_editor
                    else:
                        self.console.print(f"[red]❌ Please enter a number between 1 and {len(editors)}[/red]")
                        continue
                        
                except ValueError:
                    # Try to match editor name
                    choice_lower = choice.lower()
                    matched_editors = [
                        editor for editor in editors 
                        if editor.lower() == choice_lower or editor.lower().startswith(choice_lower)
                    ]
                    
                    if len(matched_editors) == 1:
                        selected_editor = matched_editors[0]
                        editor_index = editors.index(selected_editor) + 1
                        
                        # Show confirmation
                        confirmation_table = create_editor_table(editor_index)
                        self.console.print("\n[bold green]✅ Matched:[/bold green]")
                        self.console.print(confirmation_table)
                        
                        with self.console.status(f"[bold green]Configuring {selected_editor}...[/bold green]", spinner="dots"):
                            time.sleep(0.8)
                        
                        self.console.print(f"[bold green]✅ {selected_editor} configured successfully![/bold green]\n")
                        return selected_editor
                        
                    elif len(matched_editors) > 1:
                        matches_str = ", ".join(matched_editors)
                        self.console.print(f"[yellow]🤔 Multiple matches found: {matches_str}[/yellow]")
                        self.console.print("[dim]Please be more specific or use the number.[/dim]")
                        continue
                    else:
                        self.console.print(f"[red]❌ '{choice}' doesn't match any editor[/red]")
                        self.console.print("[dim]Available editors:[/dim] " + ", ".join(f"[cyan]{editor}[/cyan]" for editor in editors))
                        continue
                        
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Selection cancelled.[/yellow]")
                return ""
            except EOFError:
                self.console.print("\n[yellow]Selection cancelled.[/yellow]")
                return ""
    
    def _setup_project_description(self) -> None:
        """Set up project description."""
        self.console.print("\n[bold]Step 3: Project Description[/bold]")
        description = Prompt.ask("Describe your project (this helps with dependency detection)")
        
        if description.strip():
            self.config_manager.update_config(project_description=description.strip())
            self.console.print("[green]✓ Project description saved[/green]")
    
    def _setup_model_configuration(self) -> None:
        """Set up model configuration during setup wizard."""
        self.console.print("\n[bold]Step 4: AI Model Configuration[/bold]")
        self.console.print("To use AI features, you need to configure a model and API key.")
        
        # Show current status
        status = self.config_manager.validate_model_setup()
        self.console.print(f"Current model: {status['model_name']} ({status['provider']})")
        self.console.print(f"API key: {'Available' if status['has_api_key'] else 'Missing'}")
        
        if Confirm.ask("Configure AI model now?", default=True):
            # Use a simple model selection for setup wizard
            self.console.print("\n[bold]Choose a provider:[/bold]")
            providers = [
                ("1", "OpenAI (GPT-4, GPT-3.5)"),
                ("2", "Anthropic (Claude)"), 
                ("3", "Google (Gemini)"),
                ("4", "Other/Custom")
            ]
            
            for num, desc in providers:
                self.console.print(f"  {num}. {desc}")
            
            choice = Prompt.ask("Select provider", choices=["1", "2", "3", "4"], default="1")
            
            if choice == "1":
                model_name = "gpt-5-mini"
                provider = "openai"
                api_key_var = "OPENAI_API_KEY"
            elif choice == "2":
                model_name = "claude-4-sonnet-20250514"
                provider = "anthropic" 
                api_key_var = "ANTHROPIC_API_KEY"
            elif choice == "3":
                model_name = "gemini-2.5-pro"
                provider = "google"
                api_key_var = "GOOGLE_API_KEY"
            else:
                model_name = Prompt.ask("Enter model name", default="gpt-5-mini")
                provider = Prompt.ask("Enter provider", default="openai")
                api_key_var = f"{provider.upper()}_API_KEY"
            
            # Ask for scope
            scope = self.config_manager.prompt_config_scope("Model Configuration", is_model_config=True)
            
            # Update model configuration
            self.config_manager.update_agent_config_with_scope(
                scope=scope,
                model_name=model_name,
                provider=provider
            )
            
            self.console.print(f"✓ Model set to {model_name} ({provider})")
            
            # Ask for API key
            if Confirm.ask(f"Enter {provider} API key now?", default=True):
                api_key = getpass.getpass(f"Enter {api_key_var}: ")
                if api_key.strip():
                    self.config_manager.set_model_api_key_with_scope(
                        api_key.strip(), 
                        scope=scope,
                        key_name=api_key_var
                    )
                    self.console.print("✓ API key saved successfully")
                else:
                    self.console.print("[yellow]⚠ API key not set. You can set it later with '/model'[/yellow]")
            else:
                self.console.print(f"[yellow]⚠ Set {api_key_var} environment variable or use '/model' command[/yellow]")
        else:
            self.console.print("[yellow]⚠ AI features will be limited. Use '/model' to configure later.[/yellow]")
    
    def _suggest_git_setup(self) -> None:
        """Suggest git setup if not controlled."""
        self.console.print("\n[bold]Step 5: Git Setup[/bold]")
        self.console.print("[yellow]This directory is not under git control.[/yellow]")
        
        if Confirm.ask("Would you like to initialize a git repository?", default=False):
            self.console.print("Run these commands to initialize git:")
            self.console.print("  git init")
            self.console.print("  git add .")
            self.console.print('  git commit -m "Initial commit"')
            
            if Confirm.ask("Continue without git for now?", default=True):
                return
            else:
                sys.exit(0)


class ChatInterface:
    """Interactive chat interface."""
    
    def __init__(self, config_manager: ConfigManager, debug: bool = False):
        self.config_manager = config_manager
        self.debug = debug
        self.console = Console()
        self.commands = ["/apikey", "/editor", "/reset", "/setup", "/scan", "/agent", "/tiny", "/model", "/continue", "/config", "/cleanup", "/help", "/exit"]
        self.tiny_commands = ["/cost", "/compact", "/help", "exit", "quit"]
        self.mcp_installer = MCPServerInstaller(config_manager.workdir)
        self.scanner = ProjectScanner(config_manager.workdir)
        self.autocomplete_input = AutoCompleteInput(self.commands, self.console, config_manager.config_dir)
        self.tiny_agent = TinyAgentChat(config_manager)
        self.analysis_agent = ProjectAnalysisAgent(config_manager)
        self.tiny_code_agent = TinyCodeAgentChat(config_manager, debug=self.debug)
        self.tiny_manager = TinyCodeAgentManager(config_manager)
    
    async def run_with_tiny_default(self) -> None:
        """Run chat interface with TinyAgent as default for messages."""
        config = self.config_manager.load_config()
        
        # Check if we can initialize TinyAgent  
        status = self.tiny_manager.check_requirements()
        
        # Always try to use TinyAgent mode if possible, regardless of setup completion
        if status["can_initialize"]:
            await self._run_tiny_agent_mode()
        else:
            # Fall back to regular chat interface with helpful message
            await self._run_with_tiny_fallback()
    
    async def _run_with_tiny_fallback(self) -> None:
        """Run regular chat but with TinyAgent setup guidance."""
        # Show why TinyAgent isn't available and how to set it up
        status = self.tiny_manager.check_requirements()
        status_info = self.tiny_manager.get_status_info()
        
        fallback_message = f"""[bold yellow]⚠️ TinyAgent Not Available[/bold yellow]

[bold]Current Status:[/bold]
• OpenAI API Key: {status_info['openai_key']}
• TinyAgent Package: {status_info['tinyagent']}

[bold blue]To enable full AI coding assistant:[/bold blue]
1. Run [cyan]/setup[/cyan] to configure your API key
2. Restart the CLI to activate TinyAgent mode

[dim]For now, you can use basic commands like /help, /setup, /model[/dim]"""
        
        fallback_panel = Panel(
            fallback_message,
            title="[bold]🤖 AI Assistant Setup Needed[/bold]",
            border_style="yellow",
            padding=(1, 2)
        )
        self.console.print(fallback_panel)
        
        # Run regular interface
        await self.run()
    
    def _show_tiny_status(self) -> None:
        """Show TinyAgent status information."""
        status = self.tiny_manager.check_requirements()
        status_info = self.tiny_manager.get_status_info()
        
        if status["can_initialize"]:
            status_message = """[bold green]✅ TinyAgent is Active![/bold green]

[bold]Current Status:[/bold]
• OpenAI API Key: {openai_key}
• TinyAgent Package: {tinyagent}
• Model: {model}
• Provider: {provider}

[bold blue]How it works:[/bold blue]
• Just type your questions naturally
• TinyAgent processes all non-command messages
• Use [cyan]/help[/cyan] to see available commands

[dim]TinyAgent is your default AI coding assistant![/dim]""".format(**status_info)
        else:
            status_message = """[bold yellow]⚠️ TinyAgent Not Available[/bold yellow]

[bold]Current Status:[/bold]
• OpenAI API Key: {openai_key}
• TinyAgent Package: {tinyagent}

[bold blue]To activate TinyAgent:[/bold blue]
1. Run [cyan]/setup[/cyan] to configure missing requirements
2. Restart juno-agent

[dim]Once set up, TinyAgent will be your default AI assistant![/dim]""".format(**status_info)
        
        status_panel = Panel(
            status_message,
            title="[bold]🤖 TinyAgent Status[/bold]",
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(status_panel)
    
    async def _run_tiny_agent_mode(self) -> None:
        """Run chat interface with TinyAgent as default processor."""
        config = self.config_manager.load_config()
        status_indicators = []
        
        if self.config_manager.has_api_key():
            status_indicators.append("[green]🔑 API[/green]")
        else:
            status_indicators.append("[red]🔑 API[/red]")
            
        if config.editor:
            status_indicators.append(f"[blue]📝 {config.editor}[/blue]")
        else:
            status_indicators.append("[dim]📝 No Editor[/dim]")
            
        if config.mcp_server_installed:
            status_indicators.append("[green]🔗 MCP[/green]")
        else:
            status_indicators.append("[dim]🔗 MCP[/dim]")
        
        status_bar = " │ ".join(status_indicators)
        
        # Header with TinyAgent branding
        header_content = f"""[bold cyan]╭─────────────────────────────────────────────────────────╮[/bold cyan]
[bold cyan]│[/bold cyan] [bold white]🤖 juno-agent[/bold white] [dim cyan]- AI Coding Assistant (TinyAgent Active)[/dim cyan] [bold cyan]│[/bold cyan]
[bold cyan]├─────────────────────────────────────────────────────────┤[/bold cyan]
[bold cyan]│[/bold cyan] {status_bar: <55} [bold cyan]│[/bold cyan]
[bold cyan]╰─────────────────────────────────────────────────────────╯[/bold cyan]"""
        
        self.console.print(header_content)
        
        # Show capabilities and commands
        capabilities_content = """[bold green]🚀 AI Coding Assistant Ready[/bold green]
• Execute Python code securely  • Run shell commands safely
• Interactive debugging         • Code generation & testing
• Project management           • Smart command handling

[bold blue]💬 Default Mode[/bold blue]: Just type your questions - TinyAgent will help!
[bold yellow]⚡ Commands[/bold yellow]: Messages starting with [cyan]'/'[/cyan] trigger system commands
[dim]No need to type /tiny - TinyAgent is active by default![/dim]"""
        
        capabilities_panel = Panel(
            capabilities_content,
            title="[bold]🎯 Ready to Code[/bold]",
            border_style="bright_green",
            padding=(0, 1)
        )
        self.console.print(capabilities_panel)
        
        # Initialize TinyAgent
        try:
            await self.tiny_code_agent.initialize_agent()
        except Exception as e:
            self._print_ai_response(f"❌ Failed to initialize TinyAgent: {str(e)}", "error")
            return
        
        # Update autocomplete to include TinyAgent commands
        combined_commands = self.commands + ["/cost", "/compact"]
        # Remove duplicates while preserving order
        seen = set()
        unique_commands = []
        for cmd in combined_commands:
            if cmd not in seen:
                seen.add(cmd)
                unique_commands.append(cmd)
        self.autocomplete_input.update_commands(unique_commands)
        
        self.console.print("\n[dim bright_blue]━━━━━━━━━━━━━━━ JUNO AI Chat Session ━━━━━━━━━━━━━━━[/dim bright_blue]\n")
        
        conversation_history = []
        
        while True:
            try:
                current_time = self._get_current_time()
                self.console.print(f"[dim]{current_time}[/dim] [bold blue]🧙‍♂️ You[/bold blue] │ ", end="")
                user_input = self.autocomplete_input.input().strip()
                
                if not user_input:
                    continue
                
                conversation_history.append(("user", user_input))
                
                # Handle exit
                if user_input == "/exit":
                    break
                
                # Handle system commands (starting with /)
                elif user_input.startswith("/"):
                    if user_input == "/" or user_input == "/help":
                        self._handle_help_command()
                    elif user_input == "/apikey":
                        await self._handle_apikey_command()
                    elif user_input == "/editor":
                        await self._handle_editor_command()
                    elif user_input == "/reset":
                        self._handle_reset_command()
                    elif user_input == "/setup":
                        self._handle_setup_command()
                    elif user_input == "/scan":
                        self._handle_scan_command()
                    elif user_input == "/agent":
                        self._handle_agent_command()
                    elif user_input == "/tiny":
                        # Show TinyAgent status
                        self._show_tiny_status()
                    elif user_input == "/model":
                        await self._handle_model_command()
                    elif user_input == "/continue":
                        await self._handle_continue_command()
                    elif user_input == "/config":
                        self._handle_config_command()
                    elif user_input == "/cleanup":
                        self._handle_cleanup_command()
                    elif user_input == "/cost":
                        await self._handle_tiny_cost_command()
                    elif user_input == "/compact":
                        await self._handle_tiny_compact_command()
                    else:
                        # Unknown command
                        completions = self.autocomplete_input.show_completions(user_input)
                        if completions:
                            if len(completions) == 1 and completions[0] != user_input:
                                response = f"💡 Did you mean [bold cyan]'{completions[0]}'[/bold cyan]?"
                                self._print_ai_response(response, "suggestion")
                                conversation_history.append(("ai", response))
                            elif len(completions) > 1:
                                options_str = " [dim]│[/dim] ".join(f"[cyan]{cmd}[/cyan]" for cmd in completions)
                                response = f"🎯 Available options: {options_str}"
                                self._print_ai_response(response, "options")
                                conversation_history.append(("ai", response))
                            else:
                                response = f"❓ Unknown command: [red]{user_input}[/red] [dim]- Type '/help' for available commands[/dim]"
                                self._print_ai_response(response, "error")
                                conversation_history.append(("ai", response))
                        else:
                            response = f"❓ Unknown command: [red]{user_input}[/red] [dim]- Type '/help' for available commands[/dim]"
                            self._print_ai_response(response, "error")
                            conversation_history.append(("ai", response))
                
                else:
                    # Regular message - send to TinyAgent
                    try:
                        response = await self.tiny_code_agent.process_chat_message(user_input)
                        current_time = self._get_current_time()
                        self.console.print(f"[dim]{current_time}[/dim] [bold green]🤖 TinyAgent[/bold green] │ [white]{response}[/white]")
                        conversation_history.append(("ai", response))
                    except Exception as e:
                        error_response = f"🔧 TinyAgent error: {str(e)}"
                        self._print_ai_response(error_response, "error")
                        conversation_history.append(("ai", error_response))
                
                # Visual separator
                conv_count = len([h for h in conversation_history if h[0] == "user"])
                self.console.print(f"[dim bright_blue]{'─' * 45} [{conv_count} exchanges] {'─' * 10}[/dim bright_blue]")
                
            except KeyboardInterrupt:
                break
            except EOFError:
                break
        
        # Save conversation and cleanup
        try:
            self.tiny_code_agent.save_conversation()
        except Exception:
            pass
        
        # Restore original commands for autocomplete
        self.autocomplete_input.update_commands(self.commands)
        self.autocomplete_input.cleanup()
        
        goodbye_panel = Panel.fit(
            "[bold yellow]Thanks for using JUNO AI![/bold yellow]\n\n"
            "Your TinyAgent session has been saved.",
            title="Goodbye",
            border_style="yellow",
            padding=(0, 1)
        )
        self.console.print(goodbye_panel)

    async def run(self) -> None:
        """Run the sophisticated chat interface."""
        # Create an elegant header with status
        config = self.config_manager.load_config()
        status_indicators = []
        
        if self.config_manager.has_api_key():
            status_indicators.append("[green]🔑 API[/green]")
        else:
            status_indicators.append("[red]🔑 API[/red]")
            
        if config.editor:
            status_indicators.append(f"[blue]📝 {config.editor}[/blue]")
        else:
            status_indicators.append("[dim]📝 No Editor[/dim]")
            
        if config.mcp_server_installed:
            status_indicators.append("[green]🔗 MCP[/green]")
        else:
            status_indicators.append("[dim]🔗 MCP[/dim]")
        
        status_bar = " │ ".join(status_indicators)
        
        # Sophisticated header with gradient-like effect
        header_content = f"""[bold cyan]╭─────────────────────────────────────────────────────────╮[/bold cyan]
[bold cyan]│[/bold cyan] [bold white]🧙‍♂️ juno-agent[/bold white] [dim cyan]- AI-Powered Development Assistant[/dim cyan] [bold cyan]│[/bold cyan]
[bold cyan]├─────────────────────────────────────────────────────────┤[/bold cyan]
[bold cyan]│[/bold cyan] {status_bar: <55} [bold cyan]│[/bold cyan]
[bold cyan]╰─────────────────────────────────────────────────────────╯[/bold cyan]"""
        
        self.console.print(header_content)
        
        # Enhanced status display
        if self.autocomplete_input.has_readline:
            self.console.print("  [green]✨ Enhanced tab completion active[/green] [dim]- Press Tab for intelligent suggestions[/dim]")
        else:
            self.console.print("  [yellow]⚡ Basic completion mode[/yellow] [dim]- Type / for command hints[/dim]")
        
        # Sophisticated commands display with grouping
        command_groups = {
            "Setup": ["/apikey", "/editor", "/setup"],
            "AI Tools": ["/agent", "/tiny", "/model"], 
            "Project": ["/scan"],
            "System": ["/cleanup", "/reset", "/help", "/exit"]
        }
        
        commands_display = []
        colors = ['blue', 'green', 'magenta', 'yellow']
        for i, (group, cmds) in enumerate(command_groups.items()):
            color = colors[i % len(colors)]
            group_str = f"[bold {color}]{group}:[/bold {color}] {' '.join(cmds)}"
            commands_display.append(group_str)
        
        commands_panel = Panel(
            "\n".join(commands_display),
            title="[bold]🎛️  Command Palette[/bold]",
            border_style="bright_blue",
            padding=(0, 1),
            expand=False
        )
        self.console.print(commands_panel)
        
        # Interactive tips with animation
        tips = [
            "💡 Type [blue]'/help'[/blue] for detailed command information",
            "🚀 Use [green]Tab[/green] to autocomplete commands and get suggestions",
            "🔍 Commands starting with [cyan]'/'[/cyan] trigger smart actions",
            "🤖 Try [magenta]'/tiny'[/magenta] for advanced AI coding assistance",
            "💬 Regular text activates the AI chat assistant"
        ]
        
        tip_text = "\n".join(f"  {tip}" for tip in tips)
        tips_panel = Panel.fit(
            tip_text,
            title="[bold]📚 Quick Tips[/bold]",
            border_style="bright_cyan",
            padding=(0, 1)
        )
        self.console.print(tips_panel)
        
        self.console.print("\n[dim bright_blue]━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Chat Session ━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/dim bright_blue]\n")
        
        conversation_history = []
        
        while True:
            try:
                # Create sophisticated input prompt with status
                current_time = self._get_current_time()
                self.console.print(f"[dim]{current_time}[/dim] [bold blue]🧙‍♂️ You[/bold blue] │ ", end="")
                user_input = self.autocomplete_input.input().strip()
                
                if not user_input:
                    continue
                
                # Add to conversation history
                conversation_history.append(("user", user_input))
                
                if user_input == "/exit":
                    break
                elif user_input == "/" or user_input == "/help":
                    self._handle_help_command()
                elif user_input == "/apikey":
                    await self._handle_apikey_command()
                elif user_input == "/editor":
                    await self._handle_editor_command()
                elif user_input == "/reset":
                    self._handle_reset_command()
                elif user_input == "/setup":
                    self._handle_setup_command()
                elif user_input == "/scan":
                    self._handle_scan_command()
                elif user_input == "/agent":
                    self._handle_agent_command()
                elif user_input == "/tiny":
                    self._show_tiny_status()
                elif user_input == "/model":
                    await self._handle_model_command()
                elif user_input == "/continue":
                    await self._handle_continue_command()
                elif user_input == "/config":
                    self._handle_config_command()
                elif user_input == "/cleanup":
                    self._handle_cleanup_command()
                elif user_input.startswith("/"):
                    # Enhanced command suggestion with better UX
                    completions = self.autocomplete_input.show_completions(user_input)
                    if completions:
                        if len(completions) == 1 and completions[0] != user_input:
                            # Single completion suggestion with action prompt
                            response = f"💡 Did you mean [bold cyan]'{completions[0]}'[/bold cyan]? [dim](Type it or press Tab)[/dim]"
                            self._print_ai_response(response, "suggestion")
                            conversation_history.append(("ai", response))
                        elif len(completions) > 1:
                            # Multiple options with better formatting
                            options_str = " [dim]│[/dim] ".join(f"[cyan]{cmd}[/cyan]" for cmd in completions)
                            response = f"🎯 Available options: {options_str}"
                            self._print_ai_response(response, "options")
                            conversation_history.append(("ai", response))
                        else:
                            response = f"❓ Unknown command: [red]{user_input}[/red] [dim]- Type '/help' for available commands[/dim]"
                            self._print_ai_response(response, "error")
                            conversation_history.append(("ai", response))
                    else:
                        response = f"❓ Unknown command: [red]{user_input}[/red] [dim]- Type '/help' for available commands[/dim]"
                        self._print_ai_response(response, "error")
                        conversation_history.append(("ai", response))
                else:
                    # Process with AI agent
                    try:
                        # Get project context for better responses
                        project_context = {
                            "workdir": str(self.config_manager.workdir),
                            "has_api_key": self.config_manager.has_api_key(),
                            "editor": self.config_manager.load_config().editor,
                            "libraries": self.config_manager.load_config().libraries or []
                        }
                        
                        # Process with TinyAgent
                        ai_response = await self.tiny_agent.process_chat_message(user_input, project_context)
                        
                        self._print_ai_response(ai_response, "normal")
                        conversation_history.append(("ai", ai_response))
                        
                    except Exception as e:
                        error_response = f"🔧 AI processing temporarily unavailable: {str(e)}\n   [dim]Use commands starting with '/' for full functionality.[/dim]"
                        self._print_ai_response(error_response, "error")
                        conversation_history.append(("ai", error_response))
                
                # Enhanced visual separator with conversation count
                conv_count = len([h for h in conversation_history if h[0] == "user"])
                self.console.print(f"[dim bright_blue]{'─' * 45} [{conv_count} exchanges] {'─' * 10}[/dim bright_blue]")
                
            except KeyboardInterrupt:
                break
            except EOFError:
                break
        
        # Save conversation history
        try:
            self.tiny_agent.save_conversation()
        except Exception as e:
            # Don't let saving errors affect exit
            pass
        
        # Clean up autocomplete
        self.autocomplete_input.cleanup()
        
        # Show a nice goodbye message
        goodbye_panel = Panel.fit(
            "[bold yellow]Thanks for using juno-agent![/bold yellow]\n\n"
            "Your configuration has been saved and will be available next time you run the CLI.",
            title="Goodbye",
            border_style="yellow",
            padding=(0, 1)
        )
        self.console.print(goodbye_panel)
    
    def _get_current_time(self) -> str:
        """Get current time formatted for display."""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def _print_ai_response(self, response: str, response_type: str = "normal") -> None:
        """Print AI response with appropriate styling based on type."""
        current_time = self._get_current_time()
        
        # Choose emoji and color based on response type
        type_styles = {
            "suggestion": ("[bold green]💡 AI[/bold green]", "yellow"),
            "options": ("[bold blue]🎯 AI[/bold blue]", "cyan"),
            "error": ("[bold red]❌ AI[/bold red]", "red"),
            "info": ("[bold magenta]🤖 AI[/bold magenta]", "dim"),
            "success": ("[bold green]✅ AI[/bold green]", "green"),
            "normal": ("[bold green]🤖 AI[/bold green]", "white")
        }
        
        ai_prefix, color = type_styles.get(response_type, type_styles["normal"])
        self.console.print(f"[dim]{current_time}[/dim] {ai_prefix} │ [{color}]{response}[/{color}]")
    
    def _handle_help_command(self) -> None:
        """Handle /help command with enhanced formatting."""
        # Create a comprehensive help display
        help_sections = [
            {
                "title": "🎛️  Setup Commands",
                "commands": [
                    ("/apikey", "Set or update your ASKBUDI API key"),
                    ("/editor", "Select or change your preferred code editor"),
                    ("/setup", "Run the complete setup wizard")
                ],
                "color": "blue"
            },
            {
                "title": "🤖 AI Tools", 
                "commands": [
                    ("/agent", "Configure AI agent settings and project analysis"),
                    ("/tiny", "Show TinyAgent status (TinyAgent is active by default)"),
                    ("/model", "Configure AI model, provider, and API keys"),
                    ("/continue", "Resume TinyAgent session when max turns reached")
                ],
                "color": "green"
            },
            {
                "title": "🔍 Project Management", 
                "commands": [
                    ("/scan", "Scan project for dependencies and technologies")
                ],
                "color": "magenta"
            },
            {
                "title": "⚙️  System Commands",
                "commands": [
                    ("/config", "View and modify configuration settings"),
                    ("/cleanup", "Clear the screen and show current status"),
                    ("/reset", "Reset all configuration to defaults"),
                    ("/help", "Show this detailed help message"),
                    ("/exit", "Exit the application")
                ],
                "color": "yellow"
            }
        ]
        
        help_content = []
        for section in help_sections:
            section_lines = [f"[bold {section['color']}]{section['title']}[/bold {section['color']}]"]
            for cmd, desc in section["commands"]:
                section_lines.append(f"  [bold cyan]{cmd:8}[/bold cyan] │ {desc}")
            help_content.append("\n".join(section_lines))
        
        # Usage tips with better formatting
        tips_content = """[bold bright_magenta]💡 Usage Tips[/bold bright_magenta]
  [green]•[/green] [bold]Just type your questions![/bold] TinyAgent AI is active by default
  [green]•[/green] Commands starting with [bold cyan]/[/bold cyan] trigger system functions  
  [green]•[/green] Type [bold blue]/[/bold blue] and press [bold]Tab[/bold] for intelligent autocompletion
  [green]•[/green] Use [bold]↑/↓ arrows[/bold] to navigate command history
  [green]•[/green] Press [bold]Ctrl+C[/bold] anytime to exit"""
        
        # Getting started workflow
        workflow_content = """[bold bright_cyan]🚀 Quick Start Workflow[/bold bright_cyan]
  [bold]1.[/bold] Run [bold blue]/setup[/bold blue] to configure your API key and workspace
  [bold]2.[/bold] Start chatting! TinyAgent AI assistant is ready by default
  [bold]3.[/bold] Use [bold green]/scan[/bold green] to analyze your project structure  
  [bold]4.[/bold] Install MCP server integration with [bold blue]/editor[/bold blue] command"""
        
        # Combine all help content
        full_help = "\n\n".join([
            "\n".join(help_content),
            tips_content,
            workflow_content,
            "[dim]📚 Documentation: https://askbudi.ai/docs[/dim]"
        ])
        
        # Display in an elegant panel
        help_panel = Panel(
            full_help,
            title="[bold white]🧙‍♂️ juno-agent Help Guide[/bold white]",
            border_style="bright_blue",
            padding=(1, 2),
            expand=True
        )
        
        self._print_ai_response("Here's the complete help guide:", "info")
        self.console.print(help_panel)
    
    async def _handle_apikey_command(self) -> None:
        """Handle /apikey command with enhanced feedback."""
        self._print_ai_response("🔑 Managing your ASKBUDI API key...", "info")
        
        if self.config_manager.has_api_key():
            self._print_ai_response("API key is already configured.", "success")
            if Confirm.ask("🔄 Update your API key?", default=False):
                api_key = getpass.getpass("🔐 Enter new API key (input hidden): ")
                if api_key.strip():
                    # Validate with backend if possible
                    self.console.print("🔍 [blue]Validating API key...[/blue]")
                    try:
                        validation_result = await self.config_manager.validate_api_key_with_backend(api_key.strip())
                        if validation_result.get("valid"):
                            # Ask for scope
                            scope = self.config_manager.prompt_config_scope("API Key", is_model_config=True)
                            self.config_manager.set_api_key_with_scope(api_key.strip(), scope=scope)
                            user_level = validation_result.get("user_level", "unknown")
                            scope_text = "globally" if scope == "global" else "locally"
                            self._print_ai_response(f"✅ API key updated {scope_text}! (Level: {user_level})", "success")
                        else:
                            error = validation_result.get("error", "Unknown error")
                            self._print_ai_response(f"❌ API key validation failed: {error}", "error")
                    except Exception as e:
                        self._print_ai_response(f"⚠️ Could not validate API key: {e}", "error")
                        if Confirm.ask("💾 Save API key anyway?", default=True):
                            # Ask for scope
                            scope = self.config_manager.prompt_config_scope("API Key", is_model_config=True)
                            self.config_manager.set_api_key_with_scope(api_key.strip(), scope=scope)
                            scope_text = "globally" if scope == "global" else "locally"
                            self._print_ai_response(f"💾 API key saved {scope_text} (validation pending)", "info")
                else:
                    self._print_ai_response("❌ Invalid API key - operation cancelled", "error")
        else:
            self._print_ai_response("No API key found. Let's set one up!", "info")
            self.console.print("\n🌐 [dim]Get your API key from: https://askbudi.ai[/dim]")
            
            api_key = getpass.getpass("🔐 Enter your API key (input hidden): ")
            if api_key.strip():
                # Ask for scope
                scope = self.config_manager.prompt_config_scope("API Key", is_model_config=True)
                self.config_manager.set_api_key_with_scope(api_key.strip(), scope=scope)
                scope_text = "globally" if scope == "global" else "locally"
                self._print_ai_response(f"✅ API key saved {scope_text}!", "success")
            else:
                self._print_ai_response("❌ Invalid API key - operation cancelled", "error")
    
    async def _handle_editor_command(self) -> None:
        """Handle /editor command."""
        config = self.config_manager.load_config()
        current_editor = config.editor or "None"
        self.console.print(f"Current editor: {current_editor}")
        
        if Confirm.ask("Change editor?", default=False):
            wizard = SetupWizard(self.config_manager, SystemStatus(Path.cwd()))
            await wizard._setup_editor()
    
    async def _handle_model_command(self) -> None:
        """Handle /model command for configuring AI models."""
        import getpass
        
        self._print_ai_response("🤖 AI Model Configuration", "info")
        
        config = self.config_manager.load_config()
        agent_config = config.agent_config
        
        # Display current configuration
        current_config_content = f"""[bold]🔧 Current Configuration[/bold]
        
• **Model**: {agent_config.model_name}
• **Provider**: {agent_config.provider}
• **Temperature**: {agent_config.temperature}
• **Max Tokens**: {agent_config.max_tokens or 'Auto'}
• **API Key**: {'✅ Set' if self.config_manager.get_model_api_key() else '❌ Missing'}
• **Base URL**: {agent_config.custom_base_url or 'Default'}

[bold]🌟 Supported Providers[/bold]
• **OpenAI**: gpt-5, gpt-5-mini, o3, o4-mini
• **Anthropic**: claude-4-sonnet-20250514, claude-4-haiku
• **Google**: gemini-2.5-pro, gemini-2.5-flash
• **Groq**: moonshotai/kimi-k2-instruct, qwen-coder
• **Cohere**: command-r-plus, command-r, command-light
• **Hugging Face**: Any model ID (e.g., microsoft/DialoGPT-medium)
• **Local/Custom**: Any LiteLLM compatible endpoint"""
        
        config_panel = Panel(
            current_config_content,
            title="[bold]🤖 AI Model Dashboard[/bold]",
            border_style="bright_green",
            padding=(1, 2)
        )
        self.console.print(config_panel)
        
        # Interactive configuration options
        self._print_ai_response("Available actions:", "info")
        
        options = [
            ("1", "Change model/provider"),
            ("2", "Set API key for current model"),
            ("3", "Adjust parameters (temperature, max_tokens)"),
            ("4", "Set custom base URL"),
            ("5", "Reset to defaults"),
            ("q", "Back to main chat")
        ]
        
        for option, description in options:
            self.console.print(f"  [cyan]{option}[/cyan]. {description}")
        
        choice = Prompt.ask("\n[bold blue]Select an option[/bold blue]", default="1")
        
        if choice == "1":
            await self._configure_model_and_provider()
        elif choice == "2":
            self._configure_model_api_key()
        elif choice == "3":
            self._configure_model_parameters()
        elif choice == "4":
            self._configure_custom_base_url()
        elif choice == "5":
            self._reset_model_config()
        elif choice.lower() == "q":
            self._print_ai_response("Model configuration cancelled.", "info")
        else:
            self._print_ai_response("Invalid option selected.", "error")
    
    async def _configure_model_and_provider(self) -> None:
        """Configure model and provider using interactive selector."""
        self._print_ai_response("🎯 Model & Provider Configuration", "info")
        
        # Try to fetch models from backend endpoint
        models = self._fetch_models_from_backend()
        
        if not models:
            # Fallback to static presets if backend is unavailable
            self._print_ai_response("⚠️ Backend unavailable, using static presets", "warning")
            models = [
                {
                    "id": "gpt-5-mini",
                    "name": "GPT-5 Mini",
                    "model_name": "gpt-5-mini",
                    "provider": "openai",
                    "temperature": 0.7,
                    "description": "Latest fast, cost-effective GPT-5 class model",
                    "cost_tier": "standard"
                },
                {
                    "id": "claude-4-sonnet-20250514",
                    "name": "Claude 4 Sonnet",
                    "model_name": "claude-4-sonnet-20250514",
                    "provider": "anthropic",
                    "temperature": 0.2,
                    "description": "Anthropic's latest Claude 4 model",
                    "cost_tier": "premium"
                }
            ]
        
        # Add custom option
        custom_model = {
            "id": "custom",
            "name": "Custom Model",
            "model_name": "custom",
            "provider": "custom",
            "temperature": 0.7,
            "description": "Enter custom model and provider",
            "cost_tier": "standard"
        }
        display_models = models + [custom_model]
        
        # Use the new ModelSelectorApp
        try:
            app = ModelSelectorApp(display_models)
            selected_model = await app.run_async()
            
            if selected_model is None:
                self._print_ai_response("❌ Model selection cancelled", "error")
                return
                
            if selected_model["id"] == "custom":
                # Custom model entry
                self.console.print("\n[bold]📝 Custom Model Configuration[/bold]")
                model_name = Prompt.ask("[bold]Enter model name (LiteLLM format)[/bold]")
                provider = Prompt.ask("[bold]Enter provider[/bold]", default="openai")
                temperature = float(Prompt.ask("[bold]Temperature (0.0-2.0)[/bold]", default="0.7"))
            else:
                model_name = selected_model["model_name"]
                provider = selected_model["provider"]
                temperature = selected_model.get("temperature", 0.7)
            
            # Ask for configuration scope
            scope = self.config_manager.prompt_config_scope("Model Configuration", is_model_config=True)
            
            # Update configuration with scope
            self.config_manager.update_agent_config_with_scope(
                scope=scope,
                model_name=model_name,
                provider=provider,
                temperature=temperature
            )
            
            scope_text = "globally" if scope == "global" else "for this project"
            self._print_ai_response(f"✅ Model updated to {model_name} ({provider}) {scope_text}", "success")
            
            # Ask if they want to set API key
            if Confirm.ask("Set API key for this model now?", default=True):
                    self._configure_model_api_key()
                    
            else:
                self._print_ai_response("Invalid selection.", "error")
                
        except (ValueError, KeyboardInterrupt):
            self._print_ai_response("Configuration cancelled.", "info")
    
    def _fetch_models_from_backend(self) -> List[Dict[str, Any]]:
        """Fetch available models from the backend endpoint."""
        try:
            # Default backend URL - could be made configurable
            # Try localhost first (for development), then fallback to production
            backend_urls = [
                "http://localhost:3000/api/v1/wizard/models",
                "https://vibecontext-ts-endpoint.askbudi.workers.dev/api/v1/wizard/models"
            ]
            
            response = None
            for backend_url in backend_urls:
                try:
                    response = requests.get(backend_url, timeout=3)
                    if response.status_code == 200:
                        break
                except requests.exceptions.RequestException:
                    continue
            
            if not response:
                self._print_ai_response("⚠️ All backend URLs failed", "warning")
                return []
            
            data = response.json()
            models = data.get("models", [])
            self._print_ai_response(f"✅ Loaded {len(models)} models from backend", "success")
            return models
        except requests.exceptions.RequestException as e:
            self._print_ai_response(f"⚠️ Failed to connect to backend: {str(e)}", "warning")
            return []
        except Exception as e:
            self._print_ai_response(f"⚠️ Error fetching models: {str(e)}", "warning")
            return []
    
    def _configure_model_api_key(self) -> None:
        """Configure API key for the current model."""
        config = self.config_manager.load_config()
        agent_config = config.agent_config
        
        self._print_ai_response(f"🔑 API Key for {agent_config.model_name} ({agent_config.provider})", "info")
        
        # Show expected environment variable name
        expected_env_var = self._get_expected_env_var(agent_config.provider)
        
        self.console.print(f"\n[dim]Expected environment variable: [bold]{expected_env_var}[/bold][/dim]")
        self.console.print("[dim]You can either:[/dim]")
        self.console.print("  [cyan]1.[/cyan] Enter API key now (saved to .env)")
        self.console.print("  [cyan]2.[/cyan] Set it yourself in environment/shell")
        
        if Confirm.ask("\nEnter API key now?", default=True):
            api_key = getpass.getpass(f"🔐 Enter {agent_config.provider} API key (input hidden): ")
            if api_key.strip():
                # Ask for scope
                scope = self.config_manager.prompt_config_scope("API Key", is_model_config=True)
                
                # Save API key with scope
                self.config_manager.set_model_api_key_with_scope(api_key.strip(), scope=scope, key_name=expected_env_var)
                
                scope_text = "globally" if scope == "global" else "locally"
                self._print_ai_response(f"✅ API key saved {scope_text} as {expected_env_var}", "success")
                self._print_ai_response("🔒 Key is securely stored and will not be logged", "info")
            else:
                self._print_ai_response("❌ Invalid API key", "error")
        else:
            self.console.print(f"\n[yellow]💡 Set the environment variable manually:[/yellow]")
            self.console.print(f"   export {expected_env_var}=your_api_key_here")
    
    def _configure_model_parameters(self) -> None:
        """Configure model parameters like temperature and max_tokens."""
        config = self.config_manager.load_config()
        agent_config = config.agent_config
        
        self._print_ai_response("⚙️ Model Parameters Configuration", "info")
        
        # Temperature
        try:
            temp_str = Prompt.ask(
                f"[bold]Temperature[/bold] (0.0-2.0, current: {agent_config.temperature})",
                default=str(agent_config.temperature)
            )
            temperature = float(temp_str)
            if 0.0 <= temperature <= 2.0:
                # Ask for scope
                scope = self.config_manager.prompt_config_scope("Temperature Setting", is_model_config=True)
                
                self.config_manager.update_agent_config_with_scope(scope=scope, temperature=temperature)
                scope_text = "globally" if scope == "global" else "for this project"
                self._print_ai_response(f"✅ Temperature set to {temperature} {scope_text}", "success")
            else:
                self._print_ai_response("❌ Temperature must be between 0.0 and 2.0", "error")
                return
        except ValueError:
            self._print_ai_response("❌ Invalid temperature value", "error")
            return
        
        # Max tokens
        max_tokens_str = Prompt.ask(
            f"[bold]Max tokens[/bold] (leave empty for auto, current: {agent_config.max_tokens or 'Auto'})",
            default=""
        )
        
        if max_tokens_str.strip():
            try:
                max_tokens = int(max_tokens_str)
                if max_tokens > 0:
                    # Ask for scope
                    scope = self.config_manager.prompt_config_scope("Max Tokens Setting", is_model_config=True)
                    
                    self.config_manager.update_agent_config_with_scope(scope=scope, max_tokens=max_tokens)
                    scope_text = "globally" if scope == "global" else "for this project"
                    self._print_ai_response(f"✅ Max tokens set to {max_tokens} {scope_text}", "success")
                else:
                    self._print_ai_response("❌ Max tokens must be positive", "error")
            except ValueError:
                self._print_ai_response("❌ Invalid max tokens value", "error")
        else:
            # Ask for scope
            scope = self.config_manager.prompt_config_scope("Max Tokens Setting", is_model_config=True)
            
            self.config_manager.update_agent_config_with_scope(scope=scope, max_tokens=None)
            scope_text = "globally" if scope == "global" else "for this project"
            self._print_ai_response(f"✅ Max tokens set to auto {scope_text}", "success")
    
    def _configure_custom_base_url(self) -> None:
        """Configure custom base URL for API."""
        config = self.config_manager.load_config()
        agent_config = config.agent_config
        
        self._print_ai_response("🌐 Custom Base URL Configuration", "info")
        
        current_url = agent_config.custom_base_url or "Default"
        self.console.print(f"[dim]Current base URL: {current_url}[/dim]")
        
        base_url = Prompt.ask(
            "[bold]Enter custom base URL[/bold] (leave empty for default)",
            default=""
        )
        
        if base_url.strip():
            # Ask for scope
            scope = self.config_manager.prompt_config_scope("Base URL Setting", is_model_config=True)
            
            self.config_manager.update_agent_config_with_scope(scope=scope, custom_base_url=base_url.strip())
            scope_text = "globally" if scope == "global" else "for this project"
            self._print_ai_response(f"✅ Base URL set to {base_url.strip()} {scope_text}", "success")
        else:
            # Ask for scope
            scope = self.config_manager.prompt_config_scope("Base URL Setting", is_model_config=True)
            
            self.config_manager.update_agent_config_with_scope(scope=scope, custom_base_url=None)
            scope_text = "globally" if scope == "global" else "for this project"
            self._print_ai_response(f"✅ Base URL reset to default {scope_text}", "success")
    
    def _reset_model_config(self) -> None:
        """Reset model configuration to defaults."""
        if Confirm.ask("Reset model configuration to defaults?", default=False):
            from .config import AgentConfig
            default_config = AgentConfig()
            
            # Ask for scope
            scope = self.config_manager.prompt_config_scope("Reset Model Configuration", is_model_config=True)
            
            self.config_manager.update_agent_config_with_scope(
                scope=scope,
                model_name=default_config.model_name,
                provider=default_config.provider,
                temperature=default_config.temperature,
                max_tokens=default_config.max_tokens,
                custom_base_url=default_config.custom_base_url,
                api_key_env_var=default_config.api_key_env_var
            )
            
            scope_text = "globally" if scope == "global" else "for this project"
            self._print_ai_response(f"✅ Model configuration reset to defaults {scope_text}", "success")
            self._print_ai_response(f"Model: {default_config.model_name} ({default_config.provider})", "info")
    
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
        else:
            return f"{provider.upper()}_API_KEY"
    
    def _handle_cleanup_command(self) -> None:
        """Handle /cleanup command to clear the screen."""
        import os
        
        # Clear screen using system-appropriate method
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Show a nice header after clearing
        header_panel = Panel.fit(
            "[bold cyan]🧹 Screen Cleared![/bold cyan]\n\n"
            "[dim]Use /help to see available commands[/dim]",
            title="[bold]juno-agent[/bold]",
            border_style="bright_blue",
            padding=(0, 1)
        )
        self.console.print(header_panel)
        
        # Show current status quickly
        config = self.config_manager.load_config()
        status_items = []
        
        if self.config_manager.has_api_key():
            status_items.append("[green]🔑 API Key: ✓[/green]")
        else:
            status_items.append("[red]🔑 API Key: ✗[/red]")
            
        if config.editor:
            status_items.append(f"[blue]📝 Editor: {config.editor}[/blue]")
        else:
            status_items.append("[dim]📝 Editor: Not set[/dim]")
        
        # Add model info
        agent_config = config.agent_config
        model_status = f"[magenta]🤖 Model: {agent_config.model_name}[/magenta]"
        status_items.append(model_status)
        
        if status_items:
            status_line = " │ ".join(status_items)
            self.console.print(f"[dim]{status_line}[/dim]\n")
    
    def _handle_reset_command(self) -> None:
        """Handle /reset command."""
        if Confirm.ask("This will reset all configuration. Are you sure?", default=False):
            self.config_manager.reset_config()
            self.console.print("[green]✓ Configuration reset[/green]")
    
    def _handle_setup_command(self) -> None:
        """Handle /setup command."""
        wizard = SetupWizard(self.config_manager, SystemStatus(Path.cwd()))
        wizard.run()
    
    def _handle_scan_command(self) -> None:
        """Handle /scan command."""
        self.console.print("[blue]Scanning project...[/blue]")
        
        with self.console.status("[bold blue]Analyzing project structure..."):
            project_info = self.scanner.scan()
        
        # Display scan results
        self.console.print("\n[bold]Project Scan Results[/bold]")
        
        if project_info.languages:
            self.console.print(f"[blue]Languages:[/blue] {', '.join(project_info.languages)}")
        
        if project_info.frameworks:
            self.console.print(f"[blue]Frameworks:[/blue] {', '.join(project_info.frameworks)}")
        
        if project_info.package_managers:
            self.console.print(f"[blue]Package Managers:[/blue] {', '.join(project_info.package_managers)}")
        
        if project_info.dependencies:
            dep_count = len(project_info.dependencies)
            if dep_count > 10:
                shown_deps = project_info.dependencies[:10]
                self.console.print(f"[blue]Dependencies ({dep_count} total):[/blue] {', '.join(shown_deps)}, ... ({dep_count - 10} more)")
            else:
                self.console.print(f"[blue]Dependencies:[/blue] {', '.join(project_info.dependencies)}")
        
        if project_info.config_files:
            self.console.print(f"[blue]Config Files:[/blue] {', '.join(project_info.config_files)}")
        
        if project_info.technologies:
            self.console.print(f"[blue]Technologies:[/blue] {', '.join(project_info.technologies)}")
        
        # Save scan results to config
        self.config_manager.update_config(libraries=project_info.dependencies)
        
        # Offer to create/update rules file
        config = self.config_manager.load_config()
        if config.editor and self.mcp_installer.is_editor_supported(config.editor):
            if Confirm.ask(f"Update rules file for {config.editor}?", default=True):
                success, message = self.mcp_installer.create_rules_file(
                    config.editor, project_info, project_info.dependencies
                )
                if success:
                    self.console.print(f"[green]✓ {message}[/green]")
                else:
                    self.console.print(f"[red]✗ {message}[/red]")
        
        self.console.print(f"\n[green]✓ Project scan completed. Found {len(project_info.dependencies)} dependencies.[/green]")
    
    def _handle_agent_command(self) -> None:
        """Handle /agent command - AI agent configuration and status."""
        self._print_ai_response("🤖 AI Agent Configuration", "info")
        
        config = self.config_manager.load_config()
        
        # Enhanced status display with AI capabilities
        status_panel_content = []
        
        # Core setup status
        setup_items = [
            ("🔑 API Key", "✅ Configured" if self.config_manager.has_api_key() else "❌ Missing"),
            ("📝 Editor", f"✅ {config.editor}" if config.editor else "❌ Not selected"),
            ("📊 Project Scan", f"✅ {len(config.libraries or [])} dependencies" if config.libraries else "❌ Not scanned"),
            ("🔗 MCP Server", "✅ Installed" if config.mcp_server_installed else "❌ Not installed"),
        ]
        
        status_panel_content.append("[bold blue]🔧 Core Setup Status[/bold blue]")
        for item, status in setup_items:
            status_panel_content.append(f"  {item}: {status}")
        
        # AI Agent features
        status_panel_content.append("\n[bold green]🤖 AI Agent Features[/bold green]")
        agent_features = [
            "✅ Intelligent chat interface",
            "✅ Context-aware responses", 
            "✅ Project analysis and insights",
            "✅ Command suggestions and help",
            "✅ Conversation history tracking",
            "🚧 TinyAgent-py integration (coming soon)",
            "🚧 Advanced dependency analysis (coming soon)",
            "🚧 Automated documentation generation (coming soon)"
        ]
        
        for feature in agent_features:
            status_panel_content.append(f"  {feature}")
        
        # Conversation stats
        conversation_summary = self.tiny_agent.get_conversation_summary()
        if conversation_summary["total_exchanges"] > 0:
            status_panel_content.append("\n[bold cyan]💬 Current Session[/bold cyan]")
            status_panel_content.append(f"  📝 Exchanges: {conversation_summary['total_exchanges']}")
            if conversation_summary["conversation_topics"]:
                topics = ", ".join(conversation_summary["conversation_topics"])
                status_panel_content.append(f"  🏷️  Topics: {topics}")
        
        # Display comprehensive status
        status_panel = Panel(
            "\n".join(status_panel_content),
            title="[bold]🧙‍♂️ AI Agent Status Dashboard[/bold]",
            border_style="bright_blue",
            padding=(1, 2)
        )
        self.console.print(status_panel)
        
        # Interactive options
        self._print_ai_response("Available agent actions:", "info")
        
        if Confirm.ask("🔍 Run project analysis with AI insights?", default=False):
            self._run_ai_project_analysis()
        
        if conversation_summary["total_exchanges"] > 0 and Confirm.ask("💾 Export conversation history?", default=False):
            self._export_conversation_history()
        
        if Confirm.ask("⚙️ Configure advanced agent settings?", default=False):
            self._configure_agent_settings()
    
    def _run_ai_project_analysis(self) -> None:
        """Run AI-powered project analysis."""
        self._print_ai_response("🔍 Running AI project analysis...", "info")
        
        try:
            analysis = asyncio.run(
                self.analysis_agent.analyze_project_context(self.config_manager.workdir)
            )
            
            insights_report = self.analysis_agent.generate_insights_report(analysis)
            
            analysis_panel = Panel(
                insights_report,
                title="[bold]🧠 AI Project Analysis[/bold]",
                border_style="bright_green",
                padding=(1, 2)
            )
            self.console.print(analysis_panel)
            
            self._print_ai_response("✅ Analysis complete! Use these insights to improve your project.", "success")
            
        except Exception as e:
            self._print_ai_response(f"❌ Analysis failed: {str(e)}", "error")
    
    def _export_conversation_history(self) -> None:
        """Export conversation history."""
        try:
            conversation_file = self.config_manager.config_dir / "conversation_history.json"
            if conversation_file.exists():
                self._print_ai_response(f"📄 Conversation history saved to: {conversation_file}", "success")
            else:
                self._print_ai_response("❌ No conversation history found", "error")
        except Exception as e:
            self._print_ai_response(f"❌ Export failed: {str(e)}", "error")
    
    def _configure_agent_settings(self) -> None:
        """Configure advanced agent settings."""
        settings_content = """[bold]🛠️ Advanced Agent Settings[/bold]

[yellow]🚧 Advanced configuration coming in future releases:[/yellow]

• **TinyAgent-py Integration**: Deep code analysis and intelligent suggestions
• **Custom Response Templates**: Personalize AI responses for your workflow  
• **Project-Specific Context**: AI learns your project patterns and preferences
• **Advanced Analytics**: Detailed insights into development patterns
• **Automated Documentation**: Generate docs based on code analysis
• **Integration Plugins**: Connect with external tools and services

[dim]These features will be configurable through agent_config.json[/dim]
"""
        
        settings_panel = Panel(
            settings_content,
            title="[bold]⚙️ Agent Configuration[/bold]",
            border_style="bright_yellow",
            padding=(1, 2)
        )
        self.console.print(settings_panel)
        
        # Create placeholder config
        if Confirm.ask("💾 Create placeholder configuration file?", default=False):
            agent_config = {
                "version": "1.0",
                "enabled": True,
                "chat_mode": "intelligent",
                "analysis_depth": "standard",
                "auto_suggestions": True,
                "conversation_memory": True,
                "project_learning": True,
                "integrations": {
                    "tinyagent": {"enabled": False, "api_endpoint": ""},
                    "documentation": {"auto_generate": False, "format": "markdown"},
                    "analytics": {"track_usage": True, "generate_reports": False}
                }
            }
            
            config_file = self.config_manager.config_dir / "agent_config.json"
            import json
            with open(config_file, "w") as f:
                json.dump(agent_config, f, indent=2)
            
            self._print_ai_response(f"✅ Configuration template created: {config_file}", "success")
    
    async def _handle_tiny_command(self) -> None:
        """Handle /tiny command - TinyCodeAgent interactive mode."""
        self._print_ai_response("🤖 TinyCodeAgent - Advanced AI Coding Assistant", "info")
        
        # Check requirements first
        self.tiny_manager.display_setup_instructions()
        
        # Get status
        status = self.tiny_manager.check_requirements()
        status_info = self.tiny_manager.get_status_info()
        
        # Display status panel
        status_content = f"""[bold]🔧 TinyCodeAgent Status[/bold]

• **Status**: {status_info['status']}
• **OpenAI API Key**: {status_info['openai_key']}
• **TinyAgent Package**: {status_info['tinyagent']}
• **Model**: {status_info['model']}
• **Execution**: {status_info['provider']}

[bold]🚀 Capabilities[/bold]
• Execute Python code in secure sandbox
• Run shell commands safely
• Interactive debugging and analysis
• Code generation and testing
• Project management automation"""
        
        status_panel = Panel(
            status_content,
            title="[bold]🤖 TinyCodeAgent Dashboard[/bold]",
            border_style="bright_green" if status["can_initialize"] else "bright_yellow",
            padding=(1, 2)
        )
        self.console.print(status_panel)
        
        if not status["can_initialize"]:
            self._print_ai_response("⚠️ Setup required before using TinyCodeAgent.", "error")
            return
        
        # Enter TinyCodeAgent chat mode
        self._print_ai_response("🚀 Entering TinyCodeAgent interactive mode...", "info")
        self.console.print("\n[dim bright_blue]━━━━━━━━━━━━━━ TinyCodeAgent Chat Session ━━━━━━━━━━━━━━[/dim bright_blue]")
        self.console.print("[dim]Commands: /cost (usage), /compact (summarize), /help (commands), exit (return)[/dim]\n")
        
        try:
            await self.tiny_code_agent.initialize_agent()
            
            # Switch to TinyAgent-specific commands for autocomplete
            self.autocomplete_input.update_commands(self.tiny_commands)
            
            while True:
                try:
                    # Special prompt for TinyCodeAgent mode
                    current_time = self._get_current_time()
                    self.console.print(f"[dim]{current_time}[/dim] [bold cyan]🔬 Code[/bold cyan] │ ", end="")
                    user_input = self.autocomplete_input.input().strip()
                    
                    if not user_input:
                        continue
                    
                    # Check for exit commands
                    if user_input.lower() in ['exit', 'quit', '/exit']:
                        break
                    
                    # Check for TinyAgent-specific commands
                    if user_input == "/cost":
                        await self._handle_tiny_cost_command()
                        continue
                    elif user_input == "/compact":
                        await self._handle_tiny_compact_command()
                        continue
                    elif user_input == "/help":
                        self._handle_tiny_help_command()
                        continue
                    
                    # Process with TinyCodeAgent
                    response = await self.tiny_code_agent.process_chat_message(user_input)
                    
                    # Display response with special styling
                    current_time = self._get_current_time()
                    self.console.print(f"[dim]{current_time}[/dim] [bold green]🤖 TinyCode[/bold green] │ [white]{response}[/white]")
                    
                    # Visual separator
                    self.console.print(f"[dim bright_blue]{'─' * 60}[/dim bright_blue]")
                    
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
                except Exception as e:
                    self._print_ai_response(f"❌ Error in TinyCodeAgent: {str(e)}", "error")
            
            # Save conversation when exiting
            self.tiny_code_agent.save_conversation()
            
        except Exception as e:
            self._print_ai_response(f"❌ Failed to start TinyCodeAgent session: {str(e)}", "error")
        finally:
            # Restore original commands for autocomplete
            self.autocomplete_input.update_commands(self.commands)
            await self.tiny_code_agent.close()
        
        self.console.print("\n[dim bright_blue]━━━━━━━━━━━━━━ Returned to Main Chat ━━━━━━━━━━━━━━[/dim bright_blue]\n")
        self._print_ai_response("👋 Exited TinyCodeAgent mode. Back to main chat!", "info")
    
    async def _handle_continue_command(self) -> None:
        """Handle /continue command for resuming tinyagent when max turns reached."""
        self._print_ai_response("🔄 Continue TinyAgent", "info")
        
        # Check if we have an active tinyagent session
        if hasattr(self, 'tiny_code_agent') and self.tiny_code_agent:
            # Resume the agent with additional turns
            self._print_ai_response("Resuming TinyAgent session...", "info")
            # This would need to be implemented in the TinyCodeAgent class
            try:
                await self.tiny_code_agent.resume()
                self._print_ai_response("✅ TinyAgent resumed successfully", "success")
            except Exception as e:
                self._print_ai_response(f"❌ Failed to resume TinyAgent: {str(e)}", "error")
        else:
            # Start a new tinyagent session
            self._print_ai_response("No active TinyAgent session. Starting new session...", "info")
            await self._handle_tiny_command()
    
    def _handle_config_command(self) -> None:
        """Handle /config command for configuration management."""
        self._print_ai_response("⚙️ Configuration Management", "info")
        
        config = self.config_manager.load_config()
        
        # Display current configuration
        config_content = f"""[bold]🔧 Current Configuration[/bold]
        
• **Working Directory**: {config.workdir}
• **Editor**: {config.editor or 'Not set'}
• **Backend URL**: {config.backend_url or 'Default'}
• **Git Controlled**: {'✅ Yes' if config.git_controlled else '❌ No'}
• **Setup Completed**: {'✅ Yes' if config.setup_completed else '❌ No'}

[bold]🤖 Agent Configuration[/bold]
• **Model**: {config.agent_config.model_name}
• **Provider**: {config.agent_config.provider}
• **Temperature**: {config.agent_config.temperature}
• **Max Tokens**: {config.agent_config.max_tokens or 'Auto'}
• **API Key**: {'✅ Set' if self.config_manager.get_model_api_key() else '❌ Missing'}

[bold]📚 Project Libraries[/bold]
• **Count**: {len(config.libraries)}
• **Libraries**: {', '.join(config.libraries[:5]) if config.libraries else 'None detected'}
{f'• **...and {len(config.libraries) - 5} more**' if len(config.libraries) > 5 else ''}
"""
        
        config_panel = Panel(
            config_content,
            title="Configuration",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(config_panel)
        
        # Ask if they want to modify anything
        if Confirm.ask("\nModify configuration?", default=False):
            options = [
                "1. Change Model/Provider",
                "2. Set API Key", 
                "3. Change Editor",
                "4. Reset Configuration",
                "5. Back to chat"
            ]
            
            self.console.print("\n[bold]Configuration Options:[/bold]")
            for option in options:
                self.console.print(f"  {option}")
            
            try:
                choice = IntPrompt.ask("\nSelect option", default=5)
                if choice == 1:
                    self._configure_model_and_provider()
                elif choice == 2:
                    self._configure_model_api_key()
                elif choice == 3:
                    self._configure_editor()
                elif choice == 4:
                    if Confirm.ask("Are you sure you want to reset all configuration?", default=False):
                        self._handle_reset_command()
                elif choice == 5:
                    pass
                else:
                    self._print_ai_response("Invalid option selected.", "error")
            except (ValueError, KeyboardInterrupt):
                self._print_ai_response("Configuration cancelled.", "info")
    
    async def _handle_tiny_cost_command(self) -> None:
        """Handle /cost command in TinyAgent mode - show conversation cost."""
        if not hasattr(self, 'tiny_code_agent') or not self.tiny_code_agent or not self.tiny_code_agent.agent:
            self._print_ai_response("❌ No active TinyAgent session", "error")
            return
        
        try:
            # Check if TinyAgent has token tracking
            agent = self.tiny_code_agent.agent
            
            # Debug: Show agent attributes and callbacks
            self.console.print(f"[dim]🔍 Debug: Agent has callbacks: {hasattr(agent, 'callbacks')}[/dim]")
            if hasattr(agent, 'callbacks'):
                self.console.print(f"[dim]🔍 Debug: Number of callbacks: {len(agent.callbacks)}[/dim]")
                for i, callback in enumerate(agent.callbacks):
                    callback_type = type(callback).__name__
                    has_stats = hasattr(callback, 'get_usage_stats')
                    self.console.print(f"[dim]🔍 Debug: Callback {i}: {callback_type}, has_usage_stats: {has_stats}[/dim]")
            
            # Look for TokenTracker in callbacks - enhanced with debug logging
            cost_info = None
            total_tokens = 0
            total_cost = 0.0
            
            # Track child tracker info for display
            self._has_child_trackers = False
            self._child_tracker_count = 0
            
            self.console.print(f"[dim]🔍 Debug: Searching for TokenTracker in agent callbacks...[/dim]")
            
            if hasattr(agent, 'callbacks'):
                self.console.print(f"[dim]🔍 Debug: Agent has {len(agent.callbacks)} callbacks[/dim]")
                for i, callback in enumerate(agent.callbacks):
                    # Check for TokenTracker by class name or get_total_usage method
                    callback_type = type(callback).__name__
                    callback_module = type(callback).__module__
                    self.console.print(f"[dim]🔍 Debug: Callback {i}: {callback_module}.{callback_type}[/dim]")
                    
                    # Check all available methods
                    available_methods = [method for method in dir(callback) if not method.startswith('_')]
                    self.console.print(f"[dim]🔍 Debug: Available methods: {available_methods}[/dim]")
                    
                    if callback_type == 'TokenTracker' or hasattr(callback, 'get_total_usage'):
                        try:
                            # TokenTracker has get_total_usage() method
                            if hasattr(callback, 'get_total_usage'):
                                stats = callback.get_total_usage()
                                self.console.print(f"[dim]🔍 Debug: Found TokenTracker stats: {stats}[/dim]")
                                
                                # Check for child trackers and aggregate their costs
                                if hasattr(callback, 'child_trackers') and callback.child_trackers:
                                    try:
                                        child_count = len(callback.child_trackers)
                                        self.console.print(f"[dim]🔍 Debug: Found {child_count} child trackers[/dim]")
                                        self._has_child_trackers = True
                                        self._child_tracker_count = child_count
                                    except TypeError:
                                        # Handle Mock objects that don't support len()
                                        try:
                                            child_count = len(list(callback.child_trackers))
                                            self.console.print(f"[dim]🔍 Debug: Found {child_count} child trackers[/dim]")
                                            self._has_child_trackers = True
                                            self._child_tracker_count = child_count
                                        except TypeError:
                                            self.console.print(f"[dim]🔍 Debug: Could not determine child tracker count[/dim]")
                                    child_tokens = 0
                                    child_cost = 0.0
                                    child_calls = 0
                                    child_prompt_tokens = 0
                                    child_completion_tokens = 0
                                    
                                    for i, child_tracker in enumerate(callback.child_trackers):
                                        if hasattr(child_tracker, 'get_total_usage'):
                                            child_stats = child_tracker.get_total_usage()
                                            self.console.print(f"[dim]🔍 Debug: Child tracker {i} stats: {child_stats}[/dim]")
                                            child_tokens += child_stats.total_tokens
                                            child_cost += child_stats.cost
                                            child_calls += child_stats.call_count
                                            child_prompt_tokens += getattr(child_stats, 'prompt_tokens', 0)
                                            child_completion_tokens += getattr(child_stats, 'completion_tokens', 0)
                                    
                                    self.console.print(f"[dim]🔍 Debug: Total child usage - Tokens: {child_tokens}, Cost: ${child_cost:.4f}, Calls: {child_calls}[/dim]")
                                    
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
                                    self.console.print(f"[dim]🔍 Debug: Using aggregated stats including child trackers[/dim]")
                                else:
                                    self.console.print(f"[dim]🔍 Debug: No child trackers found - showing parent tracker only[/dim]")
                                
                                total_tokens = stats.total_tokens
                                total_cost = stats.cost
                                cost_info = stats
                                self.console.print(f"[dim]🔍 Debug: Successfully extracted cost info from TokenTracker[/dim]")
                                break
                        except Exception as e:
                            self.console.print(f"[dim]🔍 Debug: Error getting TokenTracker stats: {e}[/dim]")
                            import traceback
                            self.console.print(f"[dim]🔍 Debug: Traceback: {traceback.format_exc()}[/dim]")
                            continue
                    # Fallback: check for any callback with get_usage_stats method
                    elif hasattr(callback, 'get_usage_stats'):
                        try:
                            stats = callback.get_usage_stats()
                            self.console.print(f"[dim]🔍 Debug: Found stats via get_usage_stats: {stats}[/dim]")
                            total_tokens = stats.total_tokens
                            total_cost = stats.cost
                            cost_info = stats
                            break
                        except Exception as e:
                            self.console.print(f"[dim]🔍 Debug: Error getting stats: {e}[/dim]")
                            continue
                            
                if not cost_info:
                    self.console.print(f"[dim]🔍 Debug: No TokenTracker found in main agent callbacks[/dim]")
            else:
                self.console.print(f"[dim]🔍 Debug: Agent has no callbacks attribute[/dim]")
            
            if cost_info:
                # Check if this includes subagent costs (use the variables we tracked during cost extraction)
                if hasattr(self, '_has_child_trackers') and self._has_child_trackers:
                    child_count = getattr(self, '_child_tracker_count', 0)
                    subagent_info = f"• **Includes Subagent Costs**: ✅ Yes ({child_count} subagents tracked)\n"
                else:
                    subagent_info = "• **Includes Subagent Costs**: ❌ No subagent usage detected\n"
                
                # Display detailed cost information
                cost_content = f"""[bold]💰 Conversation Cost Analysis[/bold]

📊 **Token Usage**
• **Prompt Tokens**: {cost_info.prompt_tokens:,}
• **Completion Tokens**: {cost_info.completion_tokens:,}
• **Total Tokens**: {cost_info.total_tokens:,}

💸 **Cost Breakdown**
• **Total Cost**: ${cost_info.cost:.4f}
• **API Calls**: {cost_info.call_count}
• **Average per Call**: ${(cost_info.cost / max(cost_info.call_count, 1)):.4f}
{subagent_info}
🧠 **Advanced Tokens** (if supported)
• **Thinking Tokens**: {getattr(cost_info, 'thinking_tokens', 0):,}
• **Reasoning Tokens**: {getattr(cost_info, 'reasoning_tokens', 0):,}
• **Cache Creation**: {getattr(cost_info, 'cache_creation_input_tokens', 0):,}
• **Cache Read**: {getattr(cost_info, 'cache_read_input_tokens', 0):,}

[dim]💡 Cost tracking includes both main agent and subagent usage when available[/dim]"""
                
                cost_panel = Panel(
                    cost_content,
                    title="[bold bright_yellow]💰 Cost Tracker[/bold bright_yellow]",
                    border_style="bright_yellow",
                    padding=(1, 2)
                )
                self.console.print(cost_panel)
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
                    
                    fallback_content = f"""[bold]💰 Estimated Cost Analysis[/bold]

📊 **Estimated Usage**
• **Estimated Tokens**: {estimated_tokens:,}
• **Estimated Cost**: ${estimated_cost:.4f}

⚠️ **Note**: This is a rough estimate. Enable TokenTracker for accurate tracking.

[dim]💡 Add TokenTracker hook for precise cost tracking[/dim]"""
                    
                    cost_panel = Panel(
                        fallback_content,
                        title="[bold yellow]💰 Cost Estimate[/bold yellow]",
                        border_style="yellow",
                        padding=(1, 2)
                    )
                    self.console.print(cost_panel)
                else:
                    self._print_ai_response("📊 Cost tracking not available. Enable TokenTracker hook for detailed cost analysis.", "info")
        
        except Exception as e:
            self._print_ai_response(f"❌ Error retrieving cost information: {str(e)}", "error")
    
    async def _handle_tiny_compact_command(self) -> None:
        """Handle /compact command in TinyAgent mode - compact conversation.
        
        Uses TinyAgent's compact() method which compacts the conversation AND updates the agent's context,
        unlike summarize() which only generates a summary without updating context.
        """
        if not hasattr(self, 'tiny_code_agent') or not self.tiny_code_agent.agent:
            self._print_ai_response("❌ No active TinyAgent session", "error")
            return
        
        try:
            self._print_ai_response("🗜️ Compacting conversation history...", "info")
            
            # Use TinyAgent's compact method (preferred) or fallback to summarize
            agent = self.tiny_code_agent.agent
            
            if hasattr(agent, 'compact'):
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console,
                    transient=True,
                ) as progress:
                    task = progress.add_task("🗜️ Compacting conversation...", total=None)
                    
                    # Call the compact method
                    summary = await agent.compact()
            elif hasattr(agent, 'summarize'):
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console,
                    transient=True,
                ) as progress:
                    task = progress.add_task("🗜️ Generating conversation summary...", total=None)
                    
                    # Fallback: Call the summarize method (doesn't update context)
                    summary = await agent.summarize()
            else:
                summary = None
            
            if summary:
                # Display the summary
                summary_content = f"""[bold]📝 Conversation Summary[/bold]

{summary}

[dim]✅ Conversation has been compacted to preserve context while reducing tokens[/dim]"""
                
                summary_panel = Panel(
                    summary_content,
                    title="[bold bright_blue]🗜️ Conversation Compact[/bold bright_blue]",
                    border_style="bright_blue",
                    padding=(1, 2)
                )
                self.console.print(summary_panel)
                
                self._print_ai_response("✅ Conversation successfully compacted!", "success")
            elif hasattr(agent, 'compact') or hasattr(agent, 'summarize'):
                self._print_ai_response("⚠️ No summary generated - conversation may be too short", "warning")
            else:
                self._print_ai_response("❌ Compacting not supported by current TinyAgent version", "error")
        
        except Exception as e:
            self._print_ai_response(f"❌ Error compacting conversation: {str(e)}", "error")
    
    def _handle_tiny_help_command(self) -> None:
        """Handle /help command in TinyAgent mode - show TinyAgent-specific commands."""
        tiny_help_content = """[bold]🤖 TinyAgent Commands[/bold]

[bold bright_cyan]💰 Cost & Usage[/bold bright_cyan]
  [bold cyan]/cost[/bold cyan]        Show conversation cost and token usage

[bold bright_blue]🗜️ Memory Management[/bold bright_blue]  
  [bold cyan]/compact[/bold cyan]     Summarize and compact conversation history

[bold bright_green]🔄 Session Control[/bold bright_green]
  [bold cyan]/help[/bold cyan]        Show this help message
  [bold cyan]exit[/bold cyan]         Exit TinyAgent mode and return to main chat
  [bold cyan]quit[/bold cyan]         Same as exit

[bold bright_magenta]💡 Tips[/bold bright_magenta]
• Use [bold]/cost[/bold] to monitor API usage and spending
• Use [bold]/compact[/bold] when conversations get long to save tokens
• TinyAgent can execute Python code and shell commands
• All code execution happens in a secure sandbox

[dim]📚 For more information, visit the TinyAgent documentation[/dim]"""
        
        help_panel = Panel(
            tiny_help_content,
            title="[bold white]🤖 TinyAgent Help[/bold white]",
            border_style="bright_cyan",
            padding=(1, 2)
        )
        self.console.print(help_panel)


class WizardApp:
    """Main wizard application."""
    
    def __init__(self, config_manager: ConfigManager, system_status: SystemStatus, debug: bool = False, auto_start_setup: bool = False, verify_only_mode: bool = False, agentic_resolver_mode: bool = False):
        self.config_manager = config_manager
        self.system_status = system_status
        self.debug = debug
        self.auto_start_setup = auto_start_setup
        self.verify_only_mode = verify_only_mode
        self.agentic_resolver_mode = agentic_resolver_mode
        self.console = Console()
    
    def run(self) -> None:
        """Run the wizard application."""
        config = self.config_manager.load_config()
        
        # Check UI mode and launch appropriate interface
        from .config import UIMode
        if hasattr(config, 'ui_mode') and config.ui_mode == UIMode.FANCY:
            # For fancy UI, let the TUI handle welcome screen and setup
            self._launch_fancy_ui()
        else:
            # For simple UI, show welcome screen here
            welcome = WelcomeScreen(self.config_manager, self.system_status)
            welcome.display()
            
            # Offer setup wizard if not completed (but don't force it)
            if not config.setup_completed:
                if not self.config_manager.has_api_key():
                    # Only prompt for setup if no API key is configured
                    if Confirm.ask("Setup wizard recommended to configure API key. Run now?", default=True):
                        wizard = SetupWizard(self.config_manager, self.system_status)
                        wizard.run()
                    else:
                        self.console.print("[yellow]You can run setup later with '/setup' or set API key with '/apikey'.[/yellow]")
                else:
                    # API key exists, setup is optional
                    if Confirm.ask("Run optional setup wizard to configure additional features?", default=False):
                        wizard = SetupWizard(self.config_manager, self.system_status)
                        wizard.run()
                    else:
                        self.console.print("[green]Ready to chat! Use '/setup' later for additional configuration.[/green]")
            
            # Validate model configuration before starting agent
            self._validate_model_configuration()
            
            # Start default chat interface with TinyAgent
            chat = ChatInterface(self.config_manager, debug=self.debug)
            asyncio.run(chat.run_with_tiny_default())
    
    def _launch_fancy_ui(self) -> None:
        """Launch the fancy TUI with welcome screen."""
        try:
            from .fancy_ui import PyWizardTUIApp
            app = PyWizardTUIApp(self.config_manager, show_welcome=True, auto_start_setup=self.auto_start_setup, verify_only_mode=self.verify_only_mode, agentic_resolver_mode=self.agentic_resolver_mode)
            app.run()
        except ImportError as e:
            self.console.print(f"[red]Error: Could not import fancy UI components: {e}[/red]")
            self.console.print(f"[red]Import traceback: {e.__class__.__name__}: {str(e)}[/red]")
            import traceback
            self.console.print(f"[red]Full traceback:\n{traceback.format_exc()}[/red]")
            self.console.print("[yellow]Falling back to simple UI mode.[/yellow]")
            # Fall back to simple UI
            chat = ChatInterface(self.config_manager, debug=self.debug)
            asyncio.run(chat.run_with_tiny_default())
        except Exception as e:
            self.console.print(f"[red]Error launching fancy UI: {e}[/red]")
            self.console.print(f"[red]Exception type: {e.__class__.__name__}[/red]")
            self.console.print(f"[red]Exception args: {e.args}[/red]")
            import traceback
            self.console.print(f"[red]Full traceback:\n{traceback.format_exc()}[/red]")
            self.console.print("[yellow]Falling back to simple UI mode.[/yellow]")
            # Fall back to simple UI
            chat = ChatInterface(self.config_manager, debug=self.debug)
            asyncio.run(chat.run_with_tiny_default())
    
    def _validate_model_configuration(self) -> None:
        """Validate model configuration and guide user to setup if needed."""
        if not self.config_manager.is_model_configured():
            status = self.config_manager.validate_model_setup()
            
            # Show model configuration status
            status_content = f"""[bold yellow]⚠️ Model Configuration Required[/bold yellow]

**Current Settings:**
• Model: {status['model_name']}
• Provider: {status['provider']}
• API Key: {'✅ Available' if status['has_api_key'] else '❌ Missing'}

**Missing Requirements:**
{chr(10).join(f'• {req}' for req in status['missing_requirements'])}

**Next Steps:**
{chr(10).join(f'• {rec}' for rec in status['recommendations'])}

The agent requires a properly configured model and API key to function.
You can set this up now or continue with limited functionality."""
            
            status_panel = Panel(
                status_content,
                title="[bold]🤖 Model Setup Required[/bold]",
                border_style="bright_yellow",
                padding=(1, 2)
            )
            self.console.print(status_panel)
            
            # Ask if user wants to configure model now
            if Confirm.ask("\nConfigure model and API key now?", default=True):
                from .ui import ChatInterface
                chat = ChatInterface(self.config_manager, debug=self.debug)
                # Run model configuration synchronously
                import asyncio
                asyncio.run(chat._handle_model_command())
                
                # Re-validate after configuration
                if not self.config_manager.is_model_configured():
                    self.console.print("[yellow]⚠️ Model still not fully configured. Some features may not work.[/yellow]")
                else:
                    self.console.print("[green]✅ Model configuration complete![/green]")
            else:
                self.console.print("[yellow]⚠️ Continuing with limited functionality. Use '/model' command to configure later.[/yellow]")