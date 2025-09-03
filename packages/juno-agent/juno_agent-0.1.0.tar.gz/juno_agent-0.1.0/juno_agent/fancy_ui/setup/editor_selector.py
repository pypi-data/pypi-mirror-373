"""Multi-editor selection widget for AI IDE preference setup."""

from typing import List, Optional
from textual import events
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static


class EditorOption(Static):
    """A single AI editor option."""
    
    DEFAULT_CSS = """
    EditorOption {
        height: 1;
        padding: 0 1;
        margin: 0;
        background: transparent;
        color: $text;
    }
    
    EditorOption.selected {
        background: $primary;
        color: $background;
    }
    
    EditorOption:hover {
        background: $accent;
        color: $background;
    }
    """
    
    def __init__(self, name: str, description: str, **kwargs):
        """Initialize editor option.
        
        Args:
            name: Editor name (e.g., "Claude Code")
            description: Brief description or tagline
        """
        self.name = name
        self.description = description
        
        # Format display text with icon and description
        display_text = self._format_display(name, description)
        super().__init__(display_text, **kwargs)
    
    def _format_display(self, name: str, description: str) -> str:
        """Format the display text for the editor option."""
        # Add icons based on editor name
        icon = self._get_editor_icon(name)
        return f"{icon} {name} - {description}"
    
    def _get_editor_icon(self, name: str) -> str:
        """Get appropriate icon for editor."""
        icons = {
            "Claude Code": "🤖",
            "Cursor": "🎯", 
            "Windsurf": "🏄",
            "VS Code": "📝",
            "GitHub Copilot": "🐙",
            "Other": "⚡"
        }
        return icons.get(name, "💻")


class EditorSelectorMenu(Widget):
    """Multi-editor selection widget for AI IDE setup."""
    
    BINDINGS = [
        ("up", "navigate_up", "Previous"),
        ("down", "navigate_down", "Next"),
        ("enter", "select_current", "Select"),
        ("escape", "close_menu", "Cancel"),
    ]
    
    DEFAULT_CSS = """
    EditorSelectorMenu {
        display: none;
        height: auto;
        max-height: 20;
        background: $surface;
        border: round $primary;
        margin-top: 1;
        margin-bottom: 1; 
        margin-left: 1;
        margin-right: 1;
        overflow-y: auto;
    }
    
    EditorSelectorMenu.visible {
        display: block !important;
        height: auto;
        min-height: 10;
    }
    
    #editor-container {
        height: auto;
        max-height: 18;
        padding: 1;
        background: transparent;
        overflow-y: auto;
        scrollbar-size-vertical: 1;
    }
    
    .editor-header {
        height: auto;
        padding: 0 1;
        margin-bottom: 1;
        color: $text;
        text-style: bold;
        background: transparent;
    }
    
    .editor-footer {
        height: 1;
        padding: 0 1;
        margin-top: 1;
        color: $text-muted;
        text-style: italic;
        background: transparent;
    }
    """
    
    class EditorSelected(Message):
        """Message sent when an editor is selected."""
        
        def __init__(self, editor_name: str):
            super().__init__()
            self.editor_name = editor_name
    
    class EditorSelectionCancelled(Message):
        """Message sent when selection is cancelled."""
        pass
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_index = 0
        self.is_visible = False
        
        # Define available AI editors with descriptions
        self.editors = [
            {
                "name": "Claude Code",
                "description": "Anthropic's official CLI with advanced code understanding"
            },
            {
                "name": "Cursor", 
                "description": "AI-first code editor with predictive editing"
            },
            {
                "name": "Windsurf",
                "description": "AI-powered development environment"
            },
            {
                "name": "VS Code",
                "description": "Microsoft's editor with AI extensions"
            },
            {
                "name": "GitHub Copilot",
                "description": "AI pair programmer for any editor"
            },
            {
                "name": "Other",
                "description": "Different AI coding assistant"
            }
        ]
    
    @property
    def can_focus(self) -> bool:
        """This widget can receive focus when visible."""
        return self.is_visible
    
    def compose(self) -> ComposeResult:
        """Compose the editor selection menu."""
        self.container = Vertical(id="editor-container")
        yield self.container
    
    def show(self, title: str = "AI IDE Preference", message: str = "Select your preferred AI coding environment:") -> None:
        """Show the editor selection menu.
        
        Args:
            title: Header title for the menu
            message: Descriptive message for the user
        """
        self.title = title
        self.message = message
        self.selected_index = 0
        
        # Debug information
        print(f"EditorSelectorMenu.show() called - mounted: {self.is_mounted}, visible: {self.is_visible}")
        
        # Ensure the widget is mounted before updating display
        if not self.is_mounted:
            print("EditorSelectorMenu not mounted, cannot show")
            return
        
        self.is_visible = True
        self.add_class("visible")
        
        # Debug CSS classes
        print(f"EditorSelectorMenu classes after show: {self.classes}")
        
        # Update display after making visible to ensure proper rendering
        self.call_after_refresh(self._update_display_and_focus)
    
    def hide(self) -> None:
        """Hide the editor selection menu."""
        self.remove_class("visible")
        self.is_visible = False
        self.selected_index = 0
        self._clear_options()
    
    def _clear_options(self) -> None:
        """Clear all options from the container."""
        try:
            container = getattr(self, 'container', None)
            if container:
                for child in list(container.children):
                    child.remove()
        except Exception:
            pass
    
    def _update_display(self) -> None:
        """Update the menu display."""
        self._clear_options()
        
        try:
            container = self.container
            if not container:
                return
            
            # Add header with title and message
            header_text = f"**{getattr(self, 'title', 'AI IDE Preference')}**\n\n{getattr(self, 'message', 'Select your preferred AI coding environment:')}"
            header = Static(header_text, classes="editor-header")
            container.mount(header)
            
            # Add editor options
            for i, editor_data in enumerate(self.editors):
                option = EditorOption(
                    editor_data["name"],
                    editor_data["description"]
                )
                if i == self.selected_index:
                    option.add_class("selected")
                container.mount(option)
            
            # Add footer with instructions
            footer = Static("Use ↑↓ to navigate, Enter to select, Escape to cancel", classes="editor-footer")
            container.mount(footer)
            
        except Exception as e:
            # Log the error for debugging but don't crash the app
            import traceback
            print(f"EditorSelectorMenu._update_display error: {e}")
            print(traceback.format_exc())
    
    def _update_display_and_focus(self) -> None:
        """Update display and set focus after widget is fully rendered."""
        print(f"EditorSelectorMenu._update_display_and_focus() called - visible: {self.is_visible}, classes: {self.classes}")
        self._update_display()
        self.focus()
        print(f"EditorSelectorMenu focused - can_focus: {self.can_focus}")
    
    def navigate_up(self) -> None:
        """Navigate to previous editor option."""
        if not self.is_visible:
            return
        
        self.selected_index = (self.selected_index - 1) % len(self.editors)
        self._update_selection()
    
    def navigate_down(self) -> None:
        """Navigate to next editor option."""
        if not self.is_visible:
            return
        
        self.selected_index = (self.selected_index + 1) % len(self.editors)
        self._update_selection()
    
    def _update_selection(self) -> None:
        """Update the visual selection."""
        try:
            options = self.query(EditorOption)
            
            # Clear all selections
            for option in options:
                option.remove_class("selected")
            
            # Set current selection
            if 0 <= self.selected_index < len(options):
                list(options)[self.selected_index].add_class("selected")
                
                # Scroll to selected item if needed
                container = getattr(self, 'container', None)
                if container:
                    container.scroll_to_widget(list(options)[self.selected_index])
                
        except Exception as e:
            # Log the error for debugging
            print(f"EditorSelectorMenu._update_selection error: {e}")
    
    def select_current(self) -> None:
        """Select the currently highlighted editor."""
        if not self.is_visible or self.selected_index >= len(self.editors):
            return
        
        selected_editor = self.editors[self.selected_index]
        self.post_message(self.EditorSelected(selected_editor["name"]))
        self.hide()
    
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
            self.post_message(self.EditorSelectionCancelled())
            self.hide()
    
    def on_click(self, event: events.Click) -> None:
        """Handle click events on editor options."""
        if not self.is_visible:
            return
        
        try:
            editor_options = self.query(EditorOption)
            
            for i, option in enumerate(editor_options):
                if option.region.contains(event.screen_offset):
                    self.selected_index = i
                    self._update_selection()
                    # Double-click to select
                    if event.count == 2:
                        self.select_current()
                    break
        except Exception:
            pass