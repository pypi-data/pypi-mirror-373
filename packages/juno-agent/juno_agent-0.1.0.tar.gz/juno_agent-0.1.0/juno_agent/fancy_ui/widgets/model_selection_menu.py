"""Interactive model selection menu widget."""

import json
import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from textual import events
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, Container
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Static, Button, Input


class ModelOption(Static):
    """A single model option - compact style like command menu."""
    
    DEFAULT_CSS = """
    ModelOption {
        height: 1;
        padding: 0 1;
        margin: 0;
        background: transparent;
        color: $text;
    }
    
    ModelOption.selected {
        background: $primary;
        color: $background;
    }
    
    ModelOption:hover {
        background: $accent;
        color: $background;
    }
    """
    
    def __init__(self, model: Dict[str, Any], provider: str, **kwargs):
        """Initialize model item with compact display format.
        
        Args:
            model: Model data dictionary containing id, display_name, max_tokens, etc.
            provider: Provider name (e.g., "OpenAI", "Anthropic")
        """
        self.model = model
        self.provider = provider
        self.model_id = model.get('id', 'unknown')
        
        # Format display content in compact style
        display_text = self._format_compact_display(model, provider)
        super().__init__(display_text, **kwargs)
    
    def _format_compact_display(self, model: Dict[str, Any], provider: str) -> str:
        """Format model data for compact single-line display."""
        display_name = model.get('display_name', model.get('id', 'Unknown'))
        max_tokens = model.get('max_tokens', 0)
        supports_vision = model.get('supports_vision', False)
        supports_function_calling = model.get('supports_function_calling', False)
        
        # Format tokens in K/M notation
        if max_tokens > 1000000:
            tokens_str = f"{max_tokens // 1000000}M"
        elif max_tokens > 1000:
            tokens_str = f"{max_tokens // 1000}K"
        else:
            tokens_str = str(max_tokens) if max_tokens else "N/A"
        
        # Add capability indicators
        capabilities = []
        if supports_vision:
            capabilities.append("👁️")
        if supports_function_calling:
            capabilities.append("🔧")
        
        caps_str = " ".join(capabilities) if capabilities else ""
        
        # Compact format: "Provider: Model Name • 128K tokens • 👁️🔧"
        base = f"{provider}: {display_name} • {tokens_str} tokens"
        if caps_str:
            base += f" • {caps_str}"
        
        return base


class ProviderSection(Static):
    """A provider section header."""
    
    DEFAULT_CSS = """
    ProviderSection {
        height: 1;
        padding: 0 1;
        margin: 0;
        background: $surface-lighten-1;
        color: $text-muted;
        text-style: bold;
    }
    """
    
    def __init__(self, provider_name: str, **kwargs):
        super().__init__(f"▶ {provider_name}", **kwargs)


class ManualEntryOption(Static):
    """Manual model entry option."""
    
    DEFAULT_CSS = """
    ManualEntryOption {
        height: 1;
        padding: 0 1;
        margin: 0;
        background: transparent;
        color: $warning;
        text-style: italic;
    }
    
    ManualEntryOption.selected {
        background: $warning;
        color: $background;
    }
    
    ManualEntryOption:hover {
        background: $warning-darken-1;
        color: $background;
    }
    """
    
    def __init__(self, **kwargs):
        super().__init__("🔧 Enter custom model (any LiteLLM supported model)", **kwargs)


class ModelSelectionMenu(Widget):
    """Model selection menu with compact style similar to history menu."""
    
    BINDINGS = [
        ("up", "navigate_up", "Previous"),
        ("down", "navigate_down", "Next"),
        ("enter", "select_current", "Select"),
        ("escape", "close_menu", "Cancel"),
    ]
    
    DEFAULT_CSS = """
    ModelSelectionMenu {
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
    
    ModelSelectionMenu.visible {
        display: block;
    }
    
    #model-container {
        height: auto;
        max-height: 18;
        scrollbar-gutter: stable;
        scrollbar-size: 1 1;
        padding: 0;
        background: transparent;
        overflow-y: auto;
        scrollbar-size-vertical: 1;
    }
    
    .model-header {
        height: 1;
        padding: 0 1;
        color: $text-muted;
        text-style: italic;
        background: transparent;
    }
    
    .model-footer {
        height: 1;
        padding: 0 1;
        color: $text-muted;
        text-style: italic;
        background: transparent;
    }
    """
    
    class ModelSelected(Message):
        """Message sent when a model is selected."""
        
        def __init__(self, model: Dict[str, Any], provider: str):
            super().__init__()
            self.model = model
            self.provider = provider
    
    class ManualEntryRequested(Message):
        """Message sent when manual entry is selected."""
        pass
    
    class MenuClosed(Message):
        """Message sent when menu should be closed."""
        pass
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.models_config: Dict[str, Any] = {}
        self.flat_options: List[Tuple[str, Any]] = []  # ("type", data) pairs
        self.selected_index = 0
        self.is_visible = False
        self._load_models_config()
    
    def _load_models_config(self) -> None:
        """Load models configuration from JSON file."""
        try:
            config_path = Path(__file__).parent.parent / "models.json"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.models_config = json.load(f)
            else:
                # Fallback minimal config
                self.models_config = {
                    "providers": {
                        "OpenAI": {
                            "name": "OpenAI",
                            "api_key_env": "OPENAI_API_KEY",
                            "models": [
                                {"id": "gpt-4o", "display_name": "GPT-4o", "max_tokens": 128000}
                            ]
                        }
                    },
                    "manual_entry": {"enabled": True}
                }
        except Exception as e:
            print(f"[DEBUG] Error loading models config: {e}")
            self.models_config = {"providers": {}, "manual_entry": {"enabled": True}}
    
    def _build_flat_options(self) -> None:
        """Build flat list of options for navigation."""
        self.flat_options = []
        
        # Add provider sections and their models
        for provider_name, provider_data in self.models_config.get("providers", {}).items():
            # Add provider header
            self.flat_options.append(("provider_header", provider_name))
            
            # Add models for this provider
            for model in provider_data.get("models", []):
                self.flat_options.append(("model", {"model": model, "provider": provider_name}))
        
        # Add manual entry option if enabled
        if self.models_config.get("manual_entry", {}).get("enabled", False):
            self.flat_options.append(("manual_entry", None))
    
    @property
    def can_focus(self) -> bool:
        """This widget can receive focus when visible."""
        return True
    
    def compose(self) -> ComposeResult:
        """Compose the model selection menu."""
        self.container = Vertical(id="model-container")
        yield self.container
    
    def show(self) -> None:
        """Show the model selection menu."""
        self._build_flat_options()
        
        if not self.flat_options:
            self._show_empty_state()
        else:
            self.selected_index = 0
            self._clear_options()
            self._update_options()
        
        self.is_visible = True
        self.add_class("visible")
        self.focus()
    
    def hide(self) -> None:
        """Hide the model selection menu."""
        self.remove_class("visible")
        self.is_visible = False
        self.selected_index = 0
        self._clear_options()
    
    def _show_empty_state(self) -> None:
        """Show empty state when no models are available."""
        self._clear_options()
        
        try:
            container = getattr(self, 'container', None)
            if container is None:
                container = self.query_one("#model-container", Vertical)
            if container:
                header = Static("🤖 No models configured", classes="model-header")
                container.mount(header)
                
                empty_message = Static("Please check models.json configuration file.", classes="model-footer")
                container.mount(empty_message)
        except Exception:
            pass
    
    def _clear_options(self) -> None:
        """Clear all option widgets from the container."""
        try:
            container = getattr(self, 'container', None)
            if container is None:
                try:
                    container = self.query_one("#model-container", Vertical)
                except:
                    return
            
            if container:
                for child in list(container.children):
                    child.remove()
        except Exception:
            pass
    
    def _update_options(self) -> None:
        """Update the displayed model options."""
        try:
            container = getattr(self, 'container', None)
            if container is None:
                try:
                    container = self.query_one("#model-container", Vertical)
                except:
                    return
            
            if container and self.flat_options:
                # Add header
                header = Static("🤖 Select AI Model (Use ↑↓ to navigate, Enter to select)", classes="model-header")
                container.mount(header)
                
                # Track which options are selectable (skip provider headers)
                selectable_index = 0
                
                # Add all options
                for i, (option_type, data) in enumerate(self.flat_options):
                    if option_type == "provider_header":
                        option = ProviderSection(data)
                        container.mount(option)
                    elif option_type == "model":
                        model_data = data["model"]
                        provider = data["provider"]
                        option = ModelOption(model_data, provider)
                        if selectable_index == self.selected_index:
                            option.add_class("selected")
                        container.mount(option)
                        selectable_index += 1
                    elif option_type == "manual_entry":
                        option = ManualEntryOption()
                        if selectable_index == self.selected_index:
                            option.add_class("selected")
                        container.mount(option)
                        selectable_index += 1
                
                # Add footer
                footer = Static("Press Escape to cancel", classes="model-footer")
                container.mount(footer)
                    
        except Exception as e:
            pass
    
    def _get_selectable_count(self) -> int:
        """Get count of selectable options (excluding headers)."""
        count = 0
        for option_type, _ in self.flat_options:
            if option_type in ["model", "manual_entry"]:
                count += 1
        return count
    
    def navigate_up(self) -> None:
        """Navigate to previous selectable option."""
        if not self.is_visible or not self.flat_options:
            return
        
        selectable_count = self._get_selectable_count()
        if selectable_count > 0:
            self.selected_index = (self.selected_index - 1) % selectable_count
            self._update_selection()
    
    def navigate_down(self) -> None:
        """Navigate to next selectable option."""
        if not self.is_visible or not self.flat_options:
            return
        
        selectable_count = self._get_selectable_count()
        if selectable_count > 0:
            self.selected_index = (self.selected_index + 1) % selectable_count
            self._update_selection()
    
    def _update_selection(self) -> None:
        """Update the visual selection of options."""
        try:
            # Find all selectable options (ModelOption and ManualEntryOption)
            model_options = self.query(ModelOption)
            manual_options = self.query(ManualEntryOption)
            
            # Combine and sort by their order in the container
            all_selectable = list(model_options) + list(manual_options)
            
            # Clear all selections first
            for option in all_selectable:
                option.remove_class("selected")
            
            # Set selection on the current index
            if 0 <= self.selected_index < len(all_selectable):
                all_selectable[self.selected_index].add_class("selected")
                
                # Scroll to selected item
                container = getattr(self, 'container', None)
                if container is None:
                    try:
                        container = self.query_one("#model-container", Vertical)
                    except:
                        return
                if container:
                    container.scroll_to_widget(all_selectable[self.selected_index])
                    
        except Exception:
            pass
    
    def select_current(self) -> None:
        """Select the currently highlighted option."""
        if not self.is_visible or not self.flat_options:
            return
        
        # Find the selected option
        selectable_index = 0
        selected_option = None
        
        for option_type, data in self.flat_options:
            if option_type in ["model", "manual_entry"]:
                if selectable_index == self.selected_index:
                    selected_option = (option_type, data)
                    break
                selectable_index += 1
        
        if selected_option:
            option_type, data = selected_option
            if option_type == "model":
                model = data["model"]
                provider = data["provider"]
                self.post_message(self.ModelSelected(model, provider))
            elif option_type == "manual_entry":
                self.post_message(self.ManualEntryRequested())
            
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
            self.post_message(self.MenuClosed())
            self.hide()
    
    def on_click(self, event: events.Click) -> None:
        """Handle click events on model options."""
        if not self.is_visible:
            return
        
        try:
            # Find all selectable options
            model_options = self.query(ModelOption)
            manual_options = self.query(ManualEntryOption)
            all_selectable = list(model_options) + list(manual_options)
            
            for i, option in enumerate(all_selectable):
                if option.region.contains(event.screen_offset):
                    self.selected_index = i
                    self._update_selection()
                    # Double-click to select
                    if event.count == 2:
                        self.select_current()
                    break
        except Exception:
            pass


class APIKeyPrompt(Widget):
    """Hidden input widget for API key entry."""
    
    DEFAULT_CSS = """
    APIKeyPrompt {
        display: none;
        height: auto;
        background: $surface;
        border: round $warning;
        margin-top: 1;
        margin-bottom: 1; 
        margin-left: 1;
        margin-right: 1;
        padding: 1;
    }
    
    APIKeyPrompt.visible {
        display: block;
    }
    
    #api-key-input {
        margin-top: 1;
    }
    """
    
    class APIKeyEntered(Message):
        """Message sent when API key is entered."""
        
        def __init__(self, api_key: str, provider: str):
            super().__init__()
            self.api_key = api_key
            self.provider = provider
    
    class APIKeyPromptCanceled(Message):
        """Message sent when API key prompt is canceled."""
        pass
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.provider = ""
        self.api_key_env = ""
        self.is_visible = False
        self.api_key_callback = None
    
    def compose(self) -> ComposeResult:
        """Compose the API key prompt."""
        yield Static("", id="prompt-text")
        yield Input(placeholder="Enter API key...", password=True, id="api-key-input")
        yield Static("Press Enter to save, Escape to cancel", id="prompt-footer")
    
    def show(self, provider: str, api_key_env: str, api_key_callback=None) -> None:
        """Show the API key prompt."""
        self.provider = provider
        self.api_key_env = api_key_env
        self.api_key_callback = api_key_callback
        
        # Update prompt text
        prompt_text = self.query_one("#prompt-text", Static)
        prompt_text.update(f"🔑 API Key Required for {provider}\nEnvironment variable: {api_key_env}")
        
        # Clear and focus input
        api_input = self.query_one("#api-key-input", Input)
        api_input.value = ""
        
        self.is_visible = True
        self.add_class("visible")
        api_input.focus()
    
    def hide(self) -> None:
        """Hide the API key prompt."""
        self.remove_class("visible")
        self.is_visible = False
        
        # Clear the input for security
        api_input = self.query_one("#api-key-input", Input)
        api_input.value = ""
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle API key submission."""
        if event.input.id == "api-key-input":
            api_key = event.value.strip()
            if api_key:
                # Use call_after_refresh to ensure message is posted at the right time
                self.call_after_refresh(self._post_api_key_message, api_key, self.provider)
                # Note: Hide will be called from the app after handling the message
            else:
                self.post_message(self.APIKeyPromptCanceled())
                self.hide()
    
    def _post_api_key_message(self, api_key: str, provider: str) -> None:
        """Post the API key message after refresh."""
        # Try both callback and message posting
        if self.api_key_callback:
            self.api_key_callback(api_key, provider)
        else:
            self.post_message(self.APIKeyEntered(api_key, provider))
    
    def on_key(self, event: events.Key) -> None:
        """Handle key events."""
        if event.key == "escape":
            self.post_message(self.APIKeyPromptCanceled())
            self.hide()
            event.prevent_default()


class YesNoMenu(Widget):
    """Reusable widget for Yes/No selection dialogs."""
    
    BINDINGS = [
        ("up", "navigate_up", "Previous"),
        ("down", "navigate_down", "Next"),
        ("enter", "select_current", "Select"),
        ("escape", "close_menu", "Cancel"),
    ]
    
    DEFAULT_CSS = """
    YesNoMenu {
        display: none;
        height: auto;
        max-height: 12;
        background: $surface;
        border: round $primary;
        margin-top: 0;
        margin-bottom: 0; 
        margin-left: 1;
        margin-right: 1;
        overflow-y: auto;
    }
    
    YesNoMenu.visible {
        display: block;
    }
    
    #yesno-container {
        height: auto;
        padding: 1;
        background: transparent;
    }
    
    .yesno-header {
        height: auto;
        padding: 0 1;
        margin-bottom: 1;
        color: $text;
        text-style: bold;
        background: transparent;
    }
    
    .yesno-footer {
        height: 1;
        padding: 0 1;
        margin-top: 1;
        color: $text-muted;
        text-style: italic;
        background: transparent;
    }
    """
    
    class YesNoSelected(Message):
        """Message sent when an option is selected."""
        
        def __init__(self, selected_yes: bool, context: dict = None):
            super().__init__()
            self.selected_yes = selected_yes
            self.context = context or {}
    
    class MenuClosed(Message):
        """Message sent when menu is closed without selection."""
        
        def __init__(self, context: dict = None):
            super().__init__()
            self.context = context or {}
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_index = 0
        self.is_visible = False
        self.title = ""
        self.message = ""
        self.yes_label = "✅ Yes"
        self.no_label = "❌ No"
        self.context = {}
        self.options = []
    
    @property
    def can_focus(self) -> bool:
        """This widget can receive focus when visible."""
        return self.is_visible
    
    def compose(self) -> ComposeResult:
        """Compose the yes/no menu."""
        self.container = Vertical(id="yesno-container")
        yield self.container
    
    def show(self, title: str, message: str, yes_label: str = "✅ Yes", no_label: str = "❌ No", context: dict = None) -> None:
        """Show the yes/no menu."""
        self.title = title
        self.message = message
        self.yes_label = yes_label
        self.no_label = no_label
        self.context = context or {}
        self.selected_index = 0
        
        self.options = [
            {"label": yes_label, "value": True},
            {"label": no_label, "value": False}
        ]
        
        self._update_display()
        
        self.is_visible = True
        self.add_class("visible")
        self.focus()
    
    def hide(self) -> None:
        """Hide the yes/no menu."""
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
            header_text = f"**{self.title}**\n\n{self.message}"
            header = Static(header_text, classes="yesno-header")
            container.mount(header)
            
            # Add options
            for i, option_data in enumerate(self.options):
                option = GlobalDefaultOption(  # Reuse working GlobalDefaultOption widget
                    option_data["label"],
                    option_data["value"]
                )
                if i == self.selected_index:
                    option.add_class("selected")
                container.mount(option)
            
            # Add footer
            footer = Static("Use ↑↓ to navigate, Enter to select, Escape to cancel", classes="yesno-footer")
            container.mount(footer)
            
        except Exception as e:
            pass
    
    def navigate_up(self) -> None:
        """Navigate to previous option."""
        if not self.is_visible:
            return
        
        self.selected_index = (self.selected_index - 1) % len(self.options)
        self._update_selection()
    
    def navigate_down(self) -> None:
        """Navigate to next option."""
        if not self.is_visible:
            return
        
        self.selected_index = (self.selected_index + 1) % len(self.options)
        self._update_selection()
    
    def _update_selection(self) -> None:
        """Update the visual selection."""
        try:
            options = self.query(GlobalDefaultOption)
            
            # Clear all selections
            for option in options:
                option.remove_class("selected")
            
            # Set current selection
            if 0 <= self.selected_index < len(options):
                list(options)[self.selected_index].add_class("selected")
                
        except Exception:
            pass
    
    def select_current(self) -> None:
        """Select the currently highlighted option."""
        if not self.is_visible:
            return
        
        selected_option = self.options[self.selected_index]
        self.post_message(self.YesNoSelected(selected_option["value"], self.context))
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
            self.post_message(self.MenuClosed(self.context))
            self.hide()



class GlobalDefaultOption(Static):
    """A single option in the global default menu."""
    
    DEFAULT_CSS = """
    GlobalDefaultOption {
        height: 1;
        padding: 0 1;
        margin: 0;
        background: transparent;
        color: $text;
    }
    
    GlobalDefaultOption.selected {
        background: $primary;
        color: $background;
    }
    
    GlobalDefaultOption:hover {
        background: $accent;
        color: $background;
    }
    """
    
    def __init__(self, label: str, value: bool, **kwargs):
        """Initialize option with label and value."""
        self.label = label
        self.value = value
        super().__init__(label, **kwargs)


class GlobalDefaultMenu(Widget):
    """Menu for selecting whether to set model as global default."""
    
    BINDINGS = [
        ("up", "navigate_up", "Previous"),
        ("down", "navigate_down", "Next"),
        ("enter", "select_current", "Select"),
        ("escape", "close_menu", "Cancel"),
    ]
    
    DEFAULT_CSS = """
    GlobalDefaultMenu {
        display: none;
        height: auto;
        max-height: 12;
        background: $surface;
        border: round $primary;
        margin-top: 0;
        margin-bottom: 0; 
        margin-left: 1;
        margin-right: 1;
        overflow-y: auto;
    }
    
    GlobalDefaultMenu.visible {
        display: block;
    }
    
    #global-default-container {
        height: auto;
        padding: 1;
        background: transparent;
    }
    
    .global-header {
        height: auto;
        padding: 0 1;
        margin-bottom: 1;
        color: $text;
        text-style: bold;
        background: transparent;
    }
    
    .global-footer {
        height: 1;
        padding: 0 1;
        margin-top: 1;
        color: $text-muted;
        text-style: italic;
        background: transparent;
    }
    """
    
    class GlobalDefaultSelected(Message):
        """Message sent when an option is selected."""
        
        def __init__(self, set_global: bool):
            super().__init__()
            self.set_global = set_global
    
    class MenuClosed(Message):
        """Message sent when menu is closed without selection."""
        pass
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_index = 0
        self.is_visible = False
        self.model_info = {}
        self.options = [
            {"label": "✅ Yes, set as global default for all projects", "value": True},
            {"label": "📁 No, keep for this project only", "value": False}
        ]
    
    @property
    def can_focus(self) -> bool:
        """This widget can receive focus when visible."""
        return self.is_visible
    
    def compose(self) -> ComposeResult:
        """Compose the global default menu."""
        self.container = Vertical(id="global-default-container")
        yield self.container
    
    def show(self, model_name: str, provider: str) -> None:
        """Show the global default menu."""
        self.model_info = {"model": model_name, "provider": provider}
        self.selected_index = 0
        self._update_display()
        
        self.is_visible = True
        self.add_class("visible")
        self.focus()
    
    def hide(self) -> None:
        """Hide the global default menu."""
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
            
            # Add header
            header_text = f"""🌍 **Set as Global Default?**

You've configured **{self.model_info.get('model', 'Model')}** ({self.model_info.get('provider', 'Provider')}) for this project.

Would you like to also set it as your **global default** model for all projects?"""
            
            header = Static(header_text, classes="global-header")
            container.mount(header)
            
            # Add options
            for i, option_data in enumerate(self.options):
                option = GlobalDefaultOption(
                    option_data["label"],
                    option_data["value"]
                )
                if i == self.selected_index:
                    option.add_class("selected")
                container.mount(option)
            
            # Add footer
            footer = Static("Use ↑↓ to navigate, Enter to select, Escape to cancel", classes="global-footer")
            container.mount(footer)
            
        except Exception as e:
            pass
    
    def navigate_up(self) -> None:
        """Navigate to previous option."""
        if not self.is_visible:
            return
        
        self.selected_index = (self.selected_index - 1) % len(self.options)
        self._update_selection()
    
    def navigate_down(self) -> None:
        """Navigate to next option."""
        if not self.is_visible:
            return
        
        self.selected_index = (self.selected_index + 1) % len(self.options)
        self._update_selection()
    
    def _update_selection(self) -> None:
        """Update the visual selection."""
        try:
            options = self.query(GlobalDefaultOption)
            
            # Clear all selections
            for option in options:
                option.remove_class("selected")
            
            # Set current selection
            if 0 <= self.selected_index < len(options):
                list(options)[self.selected_index].add_class("selected")
                
        except Exception:
            pass
    
    def select_current(self) -> None:
        """Select the currently highlighted option."""
        if not self.is_visible:
            return
        
        selected_option = self.options[self.selected_index]
        self.post_message(self.GlobalDefaultSelected(selected_option["value"]))
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
            self.post_message(self.MenuClosed())
            self.hide()