"""File and folder autocomplete widget for @ mentions - Complete Refactor."""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from textual import events
from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Vertical


class FileOption(Static):
    """A single file option in the autocomplete dropdown - compact style matching model selection."""
    
    DEFAULT_CSS = """
    FileOption {
        height: 1;
        padding: 0 1;
        margin: 0;
        background: transparent;
        color: $text;
    }
    
    FileOption.selected {
        background: $primary;
        color: $background;
    }
    
    FileOption:hover {
        background: $accent;
        color: $background;
    }
    """
    
    def __init__(self, file_path: str, display_text: str, file_info: Dict[str, Any], **kwargs):
        """Initialize file option.
        
        Args:
            file_path: The actual file path
            display_text: The display text with icon
            file_info: Additional file information
        """
        self.file_path = file_path
        self.display_text = display_text
        self.file_info = file_info
        
        # Compact display format similar to model selection
        if file_info.get("is_dir"):
            # For directories, show simple format with trailing slash
            enhanced_display = f"{display_text}"
        else:
            # For files, try to get size info for compact display
            try:
                file_path_obj = Path(file_path) if not file_path.startswith('/') else Path(file_path)
                if not file_path_obj.is_absolute():
                    file_path_obj = Path.cwd() / file_path_obj
                if file_path_obj.exists():
                    size = file_path_obj.stat().st_size
                    if size < 1024:
                        size_str = f"{size}B"
                    elif size < 1024 * 1024:
                        size_str = f"{size // 1024}KB"
                    else:
                        size_str = f"{size // (1024 * 1024)}MB"
                    enhanced_display = f"{display_text} • {size_str}"
                else:
                    enhanced_display = display_text
            except:
                enhanced_display = display_text
        
        super().__init__(enhanced_display, **kwargs)


class FileAutocomplete(Widget):
    """File autocomplete dropdown - following model selection widget patterns."""
    
    BINDINGS = [
        ("up", "navigate_up", "Previous"),
        ("down", "navigate_down", "Next"),
        ("enter", "select_current", "Select"),
        ("escape", "close_menu", "Cancel"),
    ]
    
    DEFAULT_CSS = """
    FileAutocomplete {
        display: none;
        height: auto;
        max-height: 20;
        background: $surface;
        border: round $primary;
        margin-top: 0;
        margin-bottom: 0; 
        margin-left: 1;
        margin-right: 1;
        overflow-y: auto;
    }
    
    FileAutocomplete.visible {
        display: block;
    }
    
    #file-container {
        height: auto;
        max-height: 18;
        scrollbar-gutter: stable;
        scrollbar-size: 1 1;
        padding: 0;
        background: transparent;
        overflow-y: auto;
        scrollbar-size-vertical: 1;
    }
    
    .file-header {
        height: 1;
        padding: 0 1;
        color: $text-muted;
        text-style: italic;
        background: transparent;
    }
    
    .file-footer {
        height: 1;
        padding: 0 1;
        color: $text-muted;
        text-style: italic;
        background: transparent;
    }
    """
    
    class FileSelected(Message):
        """Message sent when a file is selected."""
        
        def __init__(self, file_path: str):
            super().__init__()
            self.path = file_path
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.files: List[Dict[str, Any]] = []
        self.selected_index = 0
        self.is_visible = False
        self.base_path = Path.cwd()
        self.gitignore_patterns: Set[str] = set()
        self._load_gitignore()
    
    @property
    def can_focus(self) -> bool:
        """This widget can receive focus when visible."""
        return self.is_visible
    
    def compose(self) -> ComposeResult:
        """Compose the file autocomplete menu."""
        self.container = Vertical(id="file-container")
        yield self.container
    
    def _load_gitignore(self) -> None:
        """Load .gitignore patterns."""
        gitignore_path = self.base_path / ".gitignore"
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            self.gitignore_patterns.add(line)
            except Exception:
                pass
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if a path should be ignored based on .gitignore patterns."""
        # Common directories to always ignore
        always_ignore = {
            '.git', '__pycache__', '.pytest_cache', 'node_modules',
            '.venv', 'venv', 'env', '.env', '.DS_Store', '.idea',
            '.vscode', '*.pyc', '*.pyo', '*.egg-info', 'dist', 'build'
        }
        
        name = path.name
        
        # Check against always ignore list
        for pattern in always_ignore:
            if pattern.startswith('*'):
                if name.endswith(pattern[1:]):
                    return True
            elif name == pattern:
                return True
        
        return False
    
    def _get_file_icon(self, suffix: str) -> str:
        """Get an icon for a file based on its extension."""
        icon_map = {
            '.py': '🐍', '.js': '📜', '.ts': '📘', '.jsx': '⚛️', '.tsx': '⚛️',
            '.md': '📝', '.txt': '📄', '.json': '📋', '.yaml': '📋', '.yml': '📋',
            '.toml': '📋', '.ini': '⚙️', '.cfg': '⚙️', '.conf': '⚙️',
            '.sh': '🖥️', '.bash': '🖥️', '.css': '🎨', '.html': '🌐',
            '.png': '🖼️', '.jpg': '🖼️', '.jpeg': '🖼️', '.gif': '🖼️',
            '.pdf': '📚', '.zip': '📦', '.go': '🐹', '.rs': '🦀', '.java': '☕',
        }
        return icon_map.get(suffix.lower(), '📄')
    
    def _get_files_and_folders(self, search_query: str = "") -> List[Dict[str, Any]]:
        """Get files and folders matching the search query."""
        results = []
        max_results = 100  # Increase to allow more thorough file discovery
        
        # Determine search scope
        if search_query.startswith('/'):
            # Absolute path search
            search_path = Path(search_query)
            search_term = ""
        elif '/' in search_query:
            # Relative path with directory
            parts = search_query.rsplit('/', 1)
            search_path = self.base_path / parts[0]
            search_term = parts[1].lower() if len(parts) > 1 else ""
        else:
            # Search in current directory
            search_path = self.base_path
            search_term = search_query.lower()
        
        # If search path doesn't exist, search from base
        if not search_path.exists():
            search_path = self.base_path
            search_term = search_query.lower()
        
        try:
            # First, add directories
            for item in sorted(search_path.iterdir()):
                if len(results) >= max_results:
                    break
                
                if self._should_ignore(item):
                    continue
                
                # Filter by search term
                if search_term and search_term not in item.name.lower():
                    continue
                
                if item.is_dir():
                    rel_path = str(item.relative_to(self.base_path))
                    results.append({
                        "file_path": f"{rel_path}/",
                        "display_text": f"📁 {item.name}/",
                        "is_dir": True,
                        "name": item.name
                    })
            
            # Then add files
            for item in sorted(search_path.iterdir()):
                if len(results) >= max_results:
                    break
                
                if self._should_ignore(item):
                    continue
                
                # Filter by search term
                if search_term and search_term not in item.name.lower():
                    continue
                
                if item.is_file():
                    rel_path = str(item.relative_to(self.base_path))
                    icon = self._get_file_icon(item.suffix)
                    results.append({
                        "file_path": rel_path,
                        "display_text": f"{icon} {item.name}",
                        "is_dir": False,
                        "name": item.name
                    })
        
        except (PermissionError, OSError):
            pass
        
        return results
    
    def show_for_query(self, query: str) -> None:
        """Show autocomplete for a specific query after @."""
        self.files = self._get_files_and_folders(query)
        
        if not self.files:
            self._show_empty_state()
        else:
            self.selected_index = 0
            self._clear_options()
            self._update_options()
        
        self.is_visible = True
        self.add_class("visible")
        self.focus()
    
    def hide(self) -> None:
        """Hide the file autocomplete menu."""
        self.remove_class("visible")
        self.is_visible = False
        self.selected_index = 0
        self.files = []
        self._clear_options()
    
    def _show_empty_state(self) -> None:
        """Show empty state when no files are found."""
        self._clear_options()
        
        try:
            container = getattr(self, 'container', None)
            if container is None:
                container = self.query_one("#file-container", Vertical)
            if container:
                header = Static("📁 No files found", classes="file-header")
                container.mount(header)
                
                empty_message = Static("No files or folders match your search.", classes="file-footer")
                container.mount(empty_message)
        except Exception:
            pass
    
    def _clear_options(self) -> None:
        """Clear all option widgets from the container."""
        try:
            container = getattr(self, 'container', None)
            if container is None:
                try:
                    container = self.query_one("#file-container", Vertical)
                except:
                    return
            
            if container:
                for child in list(container.children):
                    child.remove()
        except Exception:
            pass
    
    def _update_options(self) -> None:
        """Update the displayed file options."""
        try:
            container = getattr(self, 'container', None)
            if container is None:
                try:
                    container = self.query_one("#file-container", Vertical)
                except:
                    return
            
            if container and self.files:
                # Add header
                file_count = len(self.files)
                header = Static(f"📁 Files & Folders ({file_count} found) - Use ↑↓ to navigate, Enter to select", classes="file-header")
                container.mount(header)
                
                # Add file options (limit display to prevent overwhelming)
                display_count = min(40, len(self.files))
                for i in range(display_count):
                    file_info = self.files[i]
                    option = FileOption(
                        file_path=file_info["file_path"],
                        display_text=file_info["display_text"],
                        file_info=file_info
                    )
                    if i == self.selected_index:
                        option.add_class("selected")
                    container.mount(option)
                
                # Add footer
                footer_text = "Press Escape to cancel"
                if display_count < len(self.files):
                    footer_text = f"Showing {display_count} of {len(self.files)} files • Press Escape to cancel"
                footer = Static(footer_text, classes="file-footer")
                container.mount(footer)
                    
        except Exception:
            pass
    
    def navigate_up(self) -> None:
        """Navigate to previous option."""
        if not self.is_visible or not self.files:
            return
        
        display_count = min(40, len(self.files))
        self.selected_index = (self.selected_index - 1) % display_count
        self._update_selection()
    
    def navigate_down(self) -> None:
        """Navigate to next option."""
        if not self.is_visible or not self.files:
            return
        
        display_count = min(40, len(self.files))
        self.selected_index = (self.selected_index + 1) % display_count
        self._update_selection()
    
    def _update_selection(self) -> None:
        """Update the visual selection of options - matching model selection behavior."""
        try:
            # Find all file options (matching model selection pattern)
            file_options = self.query(FileOption)
            all_selectable = list(file_options)
            
            # Clear all selections first
            for option in all_selectable:
                option.remove_class("selected")
            
            # Set selection on the current index
            if 0 <= self.selected_index < len(all_selectable):
                all_selectable[self.selected_index].add_class("selected")
                
                # Scroll to selected item - exactly like model selection widget
                container = getattr(self, 'container', None)
                if container is None:
                    try:
                        container = self.query_one("#file-container", Vertical)
                    except:
                        return
                if container:
                    container.scroll_to_widget(all_selectable[self.selected_index])
                    
        except Exception:
            pass
    
    def select_current(self) -> None:
        """Select the currently highlighted file."""
        if not self.is_visible or not self.files or self.selected_index >= len(self.files):
            return
        
        selected_file = self.files[self.selected_index]
        file_path = selected_file["file_path"]
        
        # Post message with selected file
        self.post_message(self.FileSelected(file_path))
        self.hide()
    
    def get_selected_file(self) -> Optional[str]:
        """Get the currently selected file path."""
        if not self.is_visible or not self.files:
            return None
        
        return self.files[self.selected_index]["file_path"]
    
    def action_navigate_up(self) -> None:
        """Action for navigating up."""
        if self.is_visible:
            self.navigate_up()
    
    def action_navigate_down(self) -> None:
        """Action for navigating down."""
        if self.is_visible:
            self.navigate_down()
    
    def action_select_current(self) -> None:
        """Action for selecting current item."""
        if self.is_visible:
            self.select_current()
    
    def action_close_menu(self) -> None:
        """Action for closing the menu."""
        if self.is_visible:
            self.hide()
    
    def on_click(self, event: events.Click) -> None:
        """Handle click events on file options."""
        if not self.is_visible:
            return
        
        try:
            options = self.query(FileOption)
            for i, option in enumerate(options):
                if option.region.contains(event.screen_offset):
                    self.selected_index = i
                    self._update_selection()
                    # Double-click to select
                    if event.count == 2:
                        self.select_current()
                    break
        except Exception:
            pass
    
