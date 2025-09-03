"""IDE Selection Menu widget for AI IDE preference setup."""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from .base_selection_menu import BaseSelectionMenu

logger = logging.getLogger(__name__)


class IDESelectionMenu(BaseSelectionMenu):
    """Menu for selecting AI IDE preference during setup."""
    
    # IDE icons mapping for visual consistency
    IDE_ICONS = {
        "claude_code": "🤖",
        "cursor": "🎯", 
        "windsurf": "🏄",
        "vscode": "📝",
        "jetbrains_ai": "🧠",
        "visual_studio_2022": "🏢",
        "zed": "⚡",
        "claude_desktop": "🖥️",
        "cline": "🔧",
        "lm_studio": "🎭",
        "perplexity_desktop": "🔍",
        "warp": "🌊",
        "boltai": "⚡",
        "crush": "💥",
        "other": "⚡"
    }
    
    def __init__(self, show_all_ides: bool = False, **kwargs):
        """
        Initialize IDE Selection Menu.
        
        Args:
            show_all_ides: If True, show all IDEs from JSON. If False, show only popular/priority IDEs.
            **kwargs: Additional arguments passed to BaseSelectionMenu
        """
        super().__init__(**kwargs)
        self.show_all_ides = show_all_ides
        self._ide_config = None
        
    def _load_ide_config(self) -> Optional[Dict[str, Any]]:
        """Load IDE configuration from JSON file."""
        if self._ide_config is not None:
            return self._ide_config
            
        try:
            # Get the path to the JSON configuration file
            config_path = Path(__file__).parent.parent.parent / "config" / "supported_ides.json"
            
            if not config_path.exists():
                logger.warning(f"IDE configuration file not found at {config_path}")
                return None
                
            with open(config_path, 'r', encoding='utf-8') as f:
                self._ide_config = json.load(f)
                
            logger.info(f"Loaded IDE configuration with {len(self._ide_config.get('ides', {}))} IDEs")
            return self._ide_config
            
        except Exception as e:
            logger.error(f"Failed to load IDE configuration: {e}")
            return None
    
    def get_priority_ides(self) -> List[str]:
        """Get the list of priority IDEs to show by default."""
        return [
            "claude_code",
            "cursor", 
            "windsurf",
            "vscode",
            "claude_desktop",
            "cline",
            "jetbrains_ai"
        ]
        
    def get_default_options(self) -> List[Dict[str, Any]]:
        """Get the list of available AI IDEs with descriptions from JSON configuration."""
        config = self._load_ide_config()
        
        if not config or 'ides' not in config:
            logger.warning("Using fallback IDE options due to configuration loading failure")
            return self._get_fallback_options()
        
        ides = config['ides']
        options = []
        
        # Determine which IDEs to show
        if self.show_all_ides:
            ide_keys = [key for key, ide_data in ides.items() if ide_data.get('supported', False)]
        else:
            # Show only priority IDEs that are supported
            priority_ides = self.get_priority_ides()
            ide_keys = [key for key in priority_ides if key in ides and ides[key].get('supported', False)]
        
        # Build options from JSON configuration
        for ide_key in ide_keys:
            ide_data = ides[ide_key]
            
            if not ide_data.get('supported', False):
                continue
                
            # Get icon for this IDE
            icon = self.IDE_ICONS.get(ide_key, "🔧")
            
            # Build label with icon, display name, and description
            display_name = ide_data.get('display_name', ide_key.title())
            description = ide_data.get('description', 'AI development tool')
            label = f"{icon} {display_name} - {description}"
            
            options.append({
                "label": label,
                "value": ide_key,  # Use the key for internal processing
                "display_name": display_name,
                "supported": ide_data.get('supported', False),
                "one_click_install": ide_data.get('one_click_install', False),
                "platform_support": ide_data.get('platform_support', [])
            })
        
        # Add "Show all IDEs" option if currently showing only priority ones
        if not self.show_all_ides:
            options.append({
                "label": "📋 Show all supported IDEs →",
                "value": "show_all",
                "display_name": "Show all IDEs",
                "supported": True,
                "one_click_install": False,
                "platform_support": []
            })
        
        # Always add "Other" option
        options.append({
            "label": "⚡ Other - Different AI coding assistant",
            "value": "other",
            "display_name": "Other",
            "supported": True,
            "one_click_install": False,
            "platform_support": []
        })
        
        logger.info(f"Generated {len(options)} IDE options ({'all' if self.show_all_ides else 'priority'} IDEs)")
        return options
    
    def _get_fallback_options(self) -> List[Dict[str, Any]]:
        """Get fallback options if JSON configuration fails to load."""
        return [
            {
                "label": "🤖 Claude Code - Anthropic's official CLI with advanced code understanding",
                "value": "claude_code",
                "display_name": "Claude Code",
                "supported": True,
                "one_click_install": False,
                "platform_support": ["windows", "macos", "linux"]
            },
            {
                "label": "🎯 Cursor - AI-first code editor with predictive editing", 
                "value": "cursor",
                "display_name": "Cursor",
                "supported": True,
                "one_click_install": True,
                "platform_support": ["windows", "macos", "linux"]
            },
            {
                "label": "🏄 Windsurf - AI-powered development environment",
                "value": "windsurf",
                "display_name": "Windsurf",
                "supported": True,
                "one_click_install": False,
                "platform_support": ["windows", "macos", "linux"]
            },
            {
                "label": "📝 VS Code - Microsoft's editor with AI extensions",
                "value": "vscode",
                "display_name": "VS Code",
                "supported": True,
                "one_click_install": True,
                "platform_support": ["windows", "macos", "linux"]
            },
            {
                "label": "⚡ Other - Different AI coding assistant",
                "value": "other",
                "display_name": "Other",
                "supported": True,
                "one_click_install": False,
                "platform_support": []
            }
        ]
    
    def get_header_text(self) -> str:
        """Get customized header text for IDE selection."""
        if self.message:
            return f"**{self.title}**\n\n{self.message}\n\nAvailable AI IDEs:"
        return f"**{self.title}**\n\nAvailable AI IDEs:"
    
    def get_footer_text(self) -> str:
        """Get customized footer text for IDE selection."""
        return "Use ↑↓ to navigate, Enter to select, Escape to cancel • This will be saved to your project config"