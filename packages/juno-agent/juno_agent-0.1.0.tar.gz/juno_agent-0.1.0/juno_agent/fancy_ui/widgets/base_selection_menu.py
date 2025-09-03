"""Base selection menu widget template for reusable menu components."""

from typing import List, Dict, Any, Optional, Callable
from textual import events
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static


class SelectionOption(Static):
    """A single selection option widget."""
    
    DEFAULT_CSS = """
    SelectionOption {
        height: 1;
        padding: 0 1;
        margin: 0;
        background: transparent;
        color: $text;
    }
    
    SelectionOption.selected {
        background: $primary;
        color: $background;
    }
    
    SelectionOption:hover {
        background: $accent;
        color: $background;
    }
    """
    
    def __init__(self, label: str, value: Any, **kwargs):
        """Initialize selection option.
        
        Args:
            label: Display text for the option
            value: The value associated with this option
        """
        self.label = label
        self.value = value
        super().__init__(label, **kwargs)


class BaseSelectionMenu(Widget):
    """Base class for selection menus with keyboard navigation."""
    
    BINDINGS = [
        ("up", "navigate_up", "Previous"),
        ("down", "navigate_down", "Next"),
        ("enter", "select_current", "Select"),
        ("escape", "close_menu", "Cancel"),
    ]
    
    DEFAULT_CSS = """
    BaseSelectionMenu {
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
    
    BaseSelectionMenu.visible {
        display: block !important;
        height: auto;
        min-height: 5;
    }
    
    #selection-container {
        height: auto;
        max-height: 18;
        padding: 1;
        background: transparent;
        overflow-y: auto;
        scrollbar-size-vertical: 1;
    }
    
    .selection-header {
        height: auto;
        padding: 0 1;
        margin-bottom: 1;
        color: $text;
        text-style: bold;
        background: transparent;
    }
    
    .selection-footer {
        height: 1;
        padding: 0 1;
        margin-top: 1;
        color: $text-muted;
        text-style: italic;
        background: transparent;
    }
    """
    
    class OptionSelected(Message):
        """Message sent when an option is selected."""
        
        def __init__(self, value: Any, label: str = "", context: Dict[str, Any] = None):
            super().__init__()
            self.value = value
            self.label = label
            self.context = context or {}
    
    class SelectionCancelled(Message):
        """Message sent when selection is cancelled."""
        
        def __init__(self, context: Dict[str, Any] = None):
            super().__init__()
            self.context = context or {}
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_index = 0
        self.is_visible = False
        self.options: List[Dict[str, Any]] = []
        self.title = ""
        self.message = ""
        self.context = {}
    
    @property
    def can_focus(self) -> bool:
        """This widget can receive focus when visible."""
        return self.is_visible
    
    def compose(self) -> ComposeResult:
        """Compose the selection menu."""
        self.container = Vertical(id="selection-container")
        yield self.container
    
    def show(self, title: str, message: str = "", options: List[Dict[str, Any]] = None, context: Dict[str, Any] = None) -> None:
        """Show the selection menu.
        
        Args:
            title: Header title for the menu
            message: Descriptive message for the user
            options: List of option dictionaries with 'label' and 'value' keys
            context: Additional context data
        """
        self.title = title
        self.message = message
        self.options = options or self.get_default_options()
        self.context = context or {}
        self.selected_index = 0
        
        # Ensure the widget is mounted before updating display
        if not self.is_mounted:
            return
        
        self.is_visible = True
        self.add_class("visible")
        
        # Update display after making visible to ensure proper rendering
        self.call_after_refresh(self._update_display_and_focus)
    
    def hide(self) -> None:
        """Hide the selection menu."""
        self.remove_class("visible")
        self.is_visible = False
        self.selected_index = 0
        self._clear_options()
    
    def get_default_options(self) -> List[Dict[str, Any]]:
        """Get default options for this menu. Override in subclasses."""
        return []
    
    def get_header_text(self) -> str:
        """Get the header text. Override in subclasses for custom formatting."""
        if self.message:
            return f"**{self.title}**\n\n{self.message}"
        return f"**{self.title}**"
    
    def get_footer_text(self) -> str:
        """Get the footer text. Override in subclasses for custom instructions."""
        return "Use ↑↓ to navigate, Enter to select, Escape to cancel"
    
    def _clear_options(self) -> None:
        """Clear all options from the container."""
        try:
            container = getattr(self, 'container', None)
            if container:
                for child in list(container.children):
                    child.remove()
        except Exception as e:
            print(f"Error clearing options: {e}")
    
    def _update_display(self) -> None:
        """Update the menu display."""
        self._clear_options()
        
        try:
            container = self.container
            if not container:
                print("No container found for BaseSelectionMenu")
                return
            
            # Add header
            header_text = self.get_header_text()
            header = Static(header_text, classes="selection-header")
            container.mount(header)
            
            # Add options
            for i, option_data in enumerate(self.options):
                option = SelectionOption(
                    option_data.get("label", str(option_data.get("value", ""))),
                    option_data.get("value")
                )
                if i == self.selected_index:
                    option.add_class("selected")
                container.mount(option)
            
            # Add footer
            footer_text = self.get_footer_text()
            footer = Static(footer_text, classes="selection-footer")
            container.mount(footer)
            
            
        except Exception as e:
            print(f"BaseSelectionMenu._update_display error: {e}")
            import traceback
            print(traceback.format_exc())
    
    def _update_display_and_focus(self) -> None:
        """Update display and set focus after widget is fully rendered."""
        self._update_display()
        self.focus()
    
    def navigate_up(self) -> None:
        """Navigate to previous option."""
        if not self.is_visible or not self.options:
            return
        
        self.selected_index = (self.selected_index - 1) % len(self.options)
        self._update_selection()
    
    def navigate_down(self) -> None:
        """Navigate to next option."""
        if not self.is_visible or not self.options:
            return
        
        self.selected_index = (self.selected_index + 1) % len(self.options)
        self._update_selection()
    
    def _update_selection(self) -> None:
        """Update the visual selection with improved scrolling."""
        try:
            options = self.query(SelectionOption)
            
            # Clear all selections
            for option in options:
                option.remove_class("selected")
            
            # Set current selection
            if 0 <= self.selected_index < len(options):
                selected_option = list(options)[self.selected_index]
                selected_option.add_class("selected")
                
                # Enhanced scrolling to keep selected item visible
                container = getattr(self, 'container', None)
                if container:
                    # Use improved scrolling logic
                    self._scroll_to_selected_item(container, selected_option)
                
        except Exception as e:
            print(f"BaseSelectionMenu._update_selection error: {e}")
    
    def _scroll_to_selected_item(self, container, selected_option) -> None:
        """Enhanced scrolling to keep selected item in viewport."""
        try:
            # Get viewport and item dimensions
            container_region = container.region
            selected_region = selected_option.region
            
            # Calculate relative positions within the container
            viewport_height = container_region.height
            current_scroll = container.scroll_offset.y
            
            # Get the item's position relative to the container's content
            item_index = self.selected_index
            item_height = selected_region.height if selected_region.height > 0 else 1
            
            # Calculate approximate item position (accounting for header)
            header_height = 2  # Approximate header height
            item_y_position = header_height + (item_index * item_height)
            
            # Calculate visible viewport bounds
            viewport_start = current_scroll
            viewport_end = current_scroll + viewport_height - 2  # Account for footer
            
            # Check if item is outside viewport and scroll accordingly
            if item_y_position < viewport_start:
                # Item is above viewport, scroll up
                new_scroll = max(0, item_y_position - 1)
                container.scroll_to(y=new_scroll, animate=False)
            elif item_y_position + item_height > viewport_end:
                # Item is below viewport, scroll down
                new_scroll = item_y_position + item_height - viewport_height + 2
                container.scroll_to(y=max(0, new_scroll), animate=False)
            
            # Also try the built-in method as a fallback
            container.scroll_to_widget(selected_option, animate=False)
            
        except Exception as e:
            # Fallback to basic scrolling
            try:
                container.scroll_to_widget(selected_option, animate=False)
            except Exception:
                pass
    
    def select_current(self) -> None:
        """Select the currently highlighted option."""
        if not self.is_visible or self.selected_index >= len(self.options):
            return
        
        selected_option = self.options[self.selected_index]
        self.post_message(self.OptionSelected(
            value=selected_option.get("value"),
            label=selected_option.get("label", ""),
            context=self.context
        ))
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
            self.post_message(self.SelectionCancelled(self.context))
            self.hide()
    
    def on_click(self, event: events.Click) -> None:
        """Handle click events on options."""
        if not self.is_visible:
            return
        
        try:
            selection_options = self.query(SelectionOption)
            
            for i, option in enumerate(selection_options):
                if option.region.contains(event.screen_offset):
                    self.selected_index = i
                    self._update_selection()
                    # Double-click to select
                    if event.count == 2:
                        self.select_current()
                    break
        except Exception as e:
            print(f"BaseSelectionMenu.on_click error: {e}")