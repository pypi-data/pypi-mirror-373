"""Configuration management for juno-agent."""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum
import httpx
from pydantic import BaseModel, Field


# Global flag to track if the logger has been initialized
_LOGGER_INITIALIZED = False


def get_debug_logger():
    """
    Get the shared debug logger instance.
    
    This function ensures that the logger is properly configured only once,
    preventing duplicate handlers and log entries.
    
    Returns:
        logging.Logger: The configured debug logger
    """
    global _LOGGER_INITIALIZED
    logger = logging.getLogger("py_wizard_debug")
    
    if not _LOGGER_INITIALIZED:
        # Configure the logger only once
        logger.setLevel(logging.DEBUG)
        logger.propagate = False  # Prevent propagation to avoid duplicates
        
        # Clear any existing handlers to ensure clean state
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
            handler.close()
        
        _LOGGER_INITIALIZED = True
    
    return logger


class UIMode(str, Enum):
    """UI mode selection for the application."""
    SIMPLE = "simple"
    FANCY = "fancy"


class DebugLogManager:
    """Debug log manager for troubleshooting token tracking and subagent issues."""
    
    def __init__(self, config_dir: Path, debug: bool = False):
        import os
        self.config_dir = config_dir
        self.logs_dir = config_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Use centralized app_run.log file in current working directory
        self.log_file = Path(os.getcwd()) / "app_run.log"
        
        # Get the shared logger instance (prevents duplicate configuration)
        self.logger = get_debug_logger()
        
        # Only configure handlers if not already configured
        if not self.logger.handlers:
            # File handler - append to centralized log file
            file_handler = logging.FileHandler(self.log_file, mode='a')
            file_handler.setLevel(logging.DEBUG)
            
            # Console handler - only show WARNING+ unless debug flag is enabled
            console_handler = logging.StreamHandler()
            console_level = logging.DEBUG if debug else logging.WARNING
            console_handler.setLevel(console_level)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            
            self.logger.info(f"Debug logging initialized. Log file: {self.log_file}")
        else:
            # Handlers already exist, just update console handler level if needed
            for handler in self.logger.handlers:
                if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
                    console_level = logging.DEBUG if debug else logging.WARNING
                    handler.setLevel(console_level)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional context."""
        if kwargs:
            message = f"{message} | Context: {kwargs}"
        self.logger.debug(message)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional context."""
        if kwargs:
            message = f"{message} | Context: {kwargs}"
        self.logger.info(message)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional context."""
        if kwargs:
            message = f"{message} | Context: {kwargs}"
        self.logger.warning(message)
    
    def error(self, message: str, **kwargs):
        """Log error message with optional context."""
        if kwargs:
            message = f"{message} | Context: {kwargs}"
        self.logger.error(message)
    
    def get_log_file_path(self) -> Path:
        """Get the current log file path."""
        return self.log_file


class AgentConfig(BaseModel):
    """Agent/Model configuration."""
    model_name: str = "gpt-5-mini"
    model_slug: Optional[str] = None  # Short display name for UI (e.g., "gpt-5-low")
    provider: str = "openai"
    api_key_env_var: Optional[str] = None  # Environment variable name for the API key
    temperature: float = 1.0
    max_tokens: Optional[int] = None
    max_turns: int = 100  # Maximum turns for TinyAgent sessions
    custom_base_url: Optional[str] = None
    custom_params: Dict[str, Any] = {}
    model_kwargs: Dict[str, Any] = {}  # Model-specific kwargs (e.g., reasoning_effort for gpt-5)
    reuse_subagents: bool = False  # If True, reuse same subagent; if False, create fresh subagent per call


class Config(BaseModel):
    """Configuration model."""
    workdir: str
    editor: Optional[str] = None
    api_key_set: bool = False
    mcp_server_installed: bool = False
    project_description: Optional[str] = None
    git_controlled: bool = False
    git_root: Optional[str] = None
    libraries: List[str] = []
    setup_completed: bool = False
    backend_url: Optional[str] = None
    client_uuid: Optional[str] = None
    user_level: Optional[str] = None
    agent_config: AgentConfig = AgentConfig()
    ui_mode: UIMode = UIMode.FANCY
    fancy_ui_settings: Dict[str, Any] = Field(default_factory=dict)


class ConfigManager:
    """Manages configuration for juno-agent with global config support."""
    
    def __init__(self, workdir):
        self.workdir = Path(workdir)
        self.config_dir = Path(workdir) / ".askbudi"
        self.config_file = self.config_dir / "config.json"
        self.env_file = self.config_dir / ".env"
        self._config: Optional[Config] = None
        
        # Global config paths
        self.global_config_dir = Path.home() / ".ASKBUDI"
        self.global_config_file = self.global_config_dir / "config.json"
        self.global_env_file = self.global_config_dir / ".env"
        self._global_config: Optional[Config] = None
        
        # Ensure config directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.global_config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create .gitignore for .env files
        for config_dir in [self.config_dir, self.global_config_dir]:
            gitignore_file = config_dir / ".gitignore"
            if not gitignore_file.exists():
                gitignore_file.write_text(".env\n")
    
    def create_debug_logger(self, debug: bool = False) -> DebugLogManager:
        """Create a debug log manager for troubleshooting."""
        return DebugLogManager(self.config_dir, debug=debug)
    
    def load_global_config(self) -> Optional[Config]:
        """Load global configuration from ~/.ASKBUDI/config.json."""
        if self._global_config is not None:
            return self._global_config
            
        if self.global_config_file.exists():
            try:
                with open(self.global_config_file, "r") as f:
                    data = json.load(f)
                # Create a config with global data but local workdir
                data['workdir'] = str(self.workdir)
                self._global_config = Config(**data)
            except (json.JSONDecodeError, ValueError):
                self._global_config = None
        
        return self._global_config
    
    def save_global_config(self, config: Config) -> None:
        """Save global configuration to ~/.ASKBUDI/config.json."""
        self._global_config = config
        with open(self.global_config_file, "w") as f:
            json.dump(config.dict(), f, indent=2)
    
    def load_config(self) -> Config:
        """Load configuration from file, merging global and local settings."""
        if self._config is not None:
            return self._config
        
        # Load global config first
        global_config = self.load_global_config()
        
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    local_data = json.load(f)
                
                # If we have global config, merge it with local overrides
                if global_config:
                    # Start with global config data
                    merged_data = global_config.dict()
                    
                    # Define which fields should be local-only (never inherited from global)
                    local_only_fields = {'workdir', 'setup_completed', 'libraries', 'project_description', 
                                        'git_controlled', 'git_root', 'mcp_server_installed', 'editor'}
                    
                    # Override with local settings, but be selective about agent_config
                    for key, value in local_data.items():
                        if key == 'agent_config' and 'agent_config' in merged_data:
                            # For agent_config, only override if the local value represents an explicit local override
                            # If local agent_config has defaults, prefer global values for model/provider settings
                            local_agent_config = value
                            global_agent_config = merged_data['agent_config']
                            
                            # Check if local config appears to have default/unmodified model settings
                            # by comparing with common defaults
                            default_models = {'gpt-5-mini'}  # Only the actual default from AgentConfig
                            local_has_defaults = (
                                local_agent_config.get('model_name') in default_models and
                                local_agent_config.get('provider') in {'openai', 'anthropic'}
                            )
                            
                            # If local has what looks like defaults and global has different settings,
                            # prefer global for model/provider, but keep local for other settings
                            if local_has_defaults and (
                                global_agent_config.get('model_name') != local_agent_config.get('model_name') or
                                global_agent_config.get('provider') != local_agent_config.get('provider')
                            ):
                                # Use global model/provider, but local values for other settings
                                merged_agent_config = global_agent_config.copy()
                                for agent_key, agent_value in local_agent_config.items():
                                    if agent_key not in {'model_name', 'provider'}:
                                        merged_agent_config[agent_key] = agent_value
                                merged_data['agent_config'] = merged_agent_config
                            else:
                                # Use local agent config as-is
                                merged_data['agent_config'] = local_agent_config
                        elif key in local_only_fields or key not in merged_data:
                            # Always use local values for local-only fields
                            merged_data[key] = value
                        # For other fields, keep global values (don't override)
                    
                    # Ensure workdir is always local
                    merged_data['workdir'] = str(self.workdir)
                    self._config = Config(**merged_data)
                else:
                    self._config = Config(**local_data)
            except (json.JSONDecodeError, ValueError):
                # If config is corrupted, create new one
                self._config = self._create_default_config()
        else:
            # No local config exists
            if global_config:
                # Use global config as base for local
                global_data = global_config.dict()
                global_data['workdir'] = str(self.workdir)
                # Reset project-specific settings
                global_data['setup_completed'] = False
                global_data['libraries'] = []
                global_data['project_description'] = None
                global_data['git_controlled'] = False
                global_data['git_root'] = None
                self._config = Config(**global_data)
            else:
                self._config = self._create_default_config()
        
        # After loading config, check if we have a global API key and update api_key_set accordingly
        if not self._config.api_key_set:
            # Check if we have a global API key available
            global_key = self._read_env_key(self.global_env_file, "ASKBUDI_API_KEY")
            if global_key:
                self._config.api_key_set = True
            
        return self._config
    
    def save_config(self, config: Config) -> None:
        """Save configuration to file."""
        self._config = config
        with open(self.config_file, "w") as f:
            json.dump(config.dict(), f, indent=2)
    
    def update_config(self, **kwargs: Any) -> None:
        """Update configuration fields."""
        config = self.load_config()
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        self.save_config(config)
    
    def get_api_key(self, key_name: str = "ASKBUDI_API_KEY") -> Optional[str]:
        """Get API key from system environment, local .env, or global .env."""
        # First check system environment
        system_value = os.getenv(key_name)
        if system_value:
            return system_value
        
        # Then check local .env file
        local_key = self._read_env_key(self.env_file, key_name)
        if local_key:
            return local_key
        
        # Finally check global .env file
        global_key = self._read_env_key(self.global_env_file, key_name)
        if global_key:
            return global_key
            
        return None
    
    def _read_env_key(self, env_file: Path, key_name: str) -> Optional[str]:
        """Read a specific key from an env file."""
        if not env_file.exists():
            return None
            
        try:
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{key_name}="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
        return None
    
    def set_api_key(self, api_key: str, key_name: str = "ASKBUDI_API_KEY") -> None:
        """Set API key in environment file, defaulting to global for new users."""
        # Save globally if no global config exists yet (first-time users)
        # This provides a better default experience where API keys are shared across projects
        if not self.has_global_config():
            # Save globally for first-time users
            self.set_api_key_global(api_key, key_name)
            # Also ensure the config is properly initialized with api_key_set=True
            self.update_config(api_key_set=True)
            return
        
        # Save locally (existing behavior for users with existing global config)
        self._set_api_key_local(api_key, key_name)
    
    def _set_api_key_local(self, api_key: str, key_name: str = "ASKBUDI_API_KEY") -> None:
        """Set API key in local environment file."""
        # Read existing .env content
        existing_lines = []
        if self.env_file.exists():
            try:
                with open(self.env_file, "r") as f:
                    existing_lines = f.readlines()
            except Exception:
                existing_lines = []
        
        # Remove existing line with this key name
        filtered_lines = [
            line for line in existing_lines 
            if not line.strip().startswith(f"{key_name}=")
        ]
        
        # Add the new key
        filtered_lines.append(f"{key_name}={api_key}\n")
        
        # Write back to file
        with open(self.env_file, "w") as f:
            f.writelines(filtered_lines)
        
        # Update config to reflect API key is set (for ASKBUDI_API_KEY only)
        if key_name == "ASKBUDI_API_KEY":
            self.update_config(api_key_set=True)
    
    def set_api_key_global(self, api_key: str, key_name: str = "ASKBUDI_API_KEY") -> None:
        """Set API key in global environment file."""
        # Read existing global .env content
        existing_lines = []
        if self.global_env_file.exists():
            try:
                with open(self.global_env_file, "r") as f:
                    existing_lines = f.readlines()
            except Exception:
                existing_lines = []
        
        # Remove existing line with this key name
        filtered_lines = [
            line for line in existing_lines 
            if not line.strip().startswith(f"{key_name}=")
        ]
        
        # Add the new key
        filtered_lines.append(f"{key_name}={api_key}\n")
        
        # Write back to file
        with open(self.global_env_file, "w") as f:
            f.writelines(filtered_lines)
    
    def set_api_key_with_scope(self, api_key: str, scope: str = "local", key_name: str = "ASKBUDI_API_KEY") -> None:
        """Set API key with specified scope (global or local)."""
        if scope == "global":
            self.set_api_key_global(api_key, key_name)
            # Also ensure the config is properly initialized with api_key_set=True
            self.update_config(api_key_set=True)
        else:
            self._set_api_key_local(api_key, key_name)
    
    def save_config_with_scope(self, config: Config, scope: str = "local") -> None:
        """Save configuration with specified scope (global or local)."""
        if scope == "global":
            # Save to global config, but exclude local-only fields
            global_data = config.dict()
            # Remove local-only fields
            local_only_fields = ['workdir', 'setup_completed', 'libraries', 'project_description', 
                               'git_controlled', 'git_root', 'mcp_server_installed', 'editor']
            for field in local_only_fields:
                global_data.pop(field, None)
            
            # Set workdir to a placeholder for global config
            global_data['workdir'] = str(Path.home())  # Use home as placeholder
            
            self.save_global_config(Config(**global_data))
            
            # Also update local config to inherit from global
            self._config = None  # Clear cache
            self.save_config(config)
        else:
            # Save to local config only
            self.save_config(config)
    
    def update_agent_config_with_scope(self, scope: str = "local", **kwargs: Any) -> None:
        """Update agent configuration with specified scope."""
        if scope == "global":
            # Update global config
            global_config = self.load_global_config()
            if not global_config:
                # Create new global config based on current local config
                local_config = self.load_config()
                global_config = Config(**local_config.dict())
            
            for key, value in kwargs.items():
                if hasattr(global_config.agent_config, key):
                    setattr(global_config.agent_config, key, value)
            
            self.save_global_config(global_config)
            
            # Update local cache
            self._config = None  # Clear cache
            self._global_config = None  # Clear global cache
        else:
            # Update local config only
            self.update_agent_config(**kwargs)
    
    def set_model_api_key_with_scope(self, api_key: str, scope: str = "local", key_name: Optional[str] = None) -> None:
        """Set API key for the model with specified scope."""
        if scope == "global":
            self.set_api_key_global(api_key, key_name or self._get_default_api_key_name())
        else:
            self.set_model_api_key(api_key, key_name)
    
    def _get_default_api_key_name(self) -> str:
        """Get default API key name based on current provider."""
        config = self.load_config()
        provider = config.agent_config.provider.lower()
        
        if provider == "openai":
            return "OPENAI_API_KEY"
        elif provider == "anthropic":
            return "ANTHROPIC_API_KEY"
        elif provider == "google":
            return "GOOGLE_API_KEY"
        elif provider == "azure":
            return "AZURE_OPENAI_API_KEY"
        elif provider == "cohere":
            return "COHERE_API_KEY"
        elif provider == "huggingface":
            return "HUGGINGFACE_API_KEY"
        elif provider == "groq":
            return "GROQ_API_KEY"
        else:
            return f"{provider.upper()}_API_KEY"
    
    def has_global_config(self) -> bool:
        """Check if global configuration exists (config file or env file)."""
        return self.global_config_file.exists() or self.global_env_file.exists()
    
    def prompt_config_scope(self, setting_name: str, is_model_config: bool = False) -> str:
        """Prompt user to choose between global or local configuration scope."""
        from rich.prompt import Confirm
        from rich.console import Console
        
        console = Console()
        
        if self.has_global_config():
            console.print(f"\n[bold]🌍 Configuration Scope for {setting_name}[/bold]")
            console.print("Choose where to save this setting:")
            console.print("  [green]Global[/green]: Apply to all projects on this machine")
            console.print("  [blue]Local[/blue]: Apply to current project only")
            
            if is_model_config:
                console.print("\n[dim]Note: API keys and backend URLs are typically saved globally for convenience.[/dim]")
            
            use_global = Confirm.ask("Save globally?", default=True)
            return "global" if use_global else "local"
        else:
            console.print(f"\n[bold]🌍 First-time setup for {setting_name}[/bold]")
            console.print("Since no global configuration exists, you can:")
            console.print("  [blue]Local[/blue]: Save to current project only")  
            console.print("  [green]Global[/green]: Save globally as default for all projects")
            
            if is_model_config:
                console.print("\n[dim]Recommended: Save model settings globally so they're available in all projects.[/dim]")
            
            use_global = Confirm.ask("Save as global default?", default=True)
            return "global" if use_global else "local"
    
    def has_api_key(self) -> bool:
        """Check if API key is configured (local or global)."""
        # Check both general API key and model-specific API key
        general_key = self.get_api_key()
        model_key = self.get_model_api_key()
        
        # Consider it configured if either key is available
        has_key = ((general_key is not None and len(general_key.strip()) > 0) or
                   (model_key is not None and len(model_key.strip()) > 0))
        
        if has_key:
            # Update local config to reflect that API key is available
            # This ensures consistency between key availability and config state
            config = self.load_config()
            if not config.api_key_set:
                config.api_key_set = True
                self.save_config(config)
        
        return has_key
    
    def _create_default_config(self) -> Config:
        """Create default configuration."""
        return Config(
            workdir=str(self.workdir),
            editor=None,
            api_key_set=False,  # Always start as False for new config
            mcp_server_installed=False,
            project_description=None,
            git_controlled=False,
            git_root=None,
            libraries=[],
            setup_completed=False,
        )
    
    def reset_config(self) -> None:
        """Reset configuration to defaults."""
        if self.config_file.exists():
            self.config_file.unlink()
        if self.env_file.exists():
            self.env_file.unlink()
        self._config = None
    
    def update_agent_config(self, **kwargs: Any) -> None:
        """Update agent configuration fields."""
        config = self.load_config()
        for key, value in kwargs.items():
            if hasattr(config.agent_config, key):
                setattr(config.agent_config, key, value)
        self.save_config(config)
    
    def has_api_key_for_provider(self, provider: str) -> bool:
        """Check if API key is configured for a specific provider."""
        # Map provider to expected environment variable name
        provider_env_map = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY', 
            'google': 'GOOGLE_API_KEY',
            'groq': 'GROQ_API_KEY',
            'xai': 'XAI_API_KEY'
        }
        
        provider_lower = provider.lower()
        expected_env_var = provider_env_map.get(provider_lower, f"{provider.upper()}_API_KEY")
        
        # Check for the API key using the expected environment variable name
        api_key = self.get_api_key(expected_env_var)
        
        return api_key is not None and len(api_key.strip()) > 0
    
    def get_model_api_key(self) -> Optional[str]:
        """Get the API key for the currently configured model."""
        config = self.load_config()
        agent_config = config.agent_config
        
        # If no specific env var is set, try common ones based on provider
        if not agent_config.api_key_env_var:
            if agent_config.provider.lower() == "openai":
                key_name = "OPENAI_API_KEY"
            elif agent_config.provider.lower() == "anthropic":
                key_name = "ANTHROPIC_API_KEY"
            elif agent_config.provider.lower() == "google":
                key_name = "GOOGLE_API_KEY"
            elif agent_config.provider.lower() == "azure":
                key_name = "AZURE_OPENAI_API_KEY"
            elif agent_config.provider.lower() == "cohere":
                key_name = "COHERE_API_KEY"
            elif agent_config.provider.lower() == "huggingface":
                key_name = "HUGGINGFACE_API_KEY"
            elif agent_config.provider.lower() == "groq":
                key_name = "GROQ_API_KEY"
            else:
                # Try a generic pattern
                key_name = f"{agent_config.provider.upper()}_API_KEY"
        else:
            key_name = agent_config.api_key_env_var
        
        return self.get_api_key(key_name)
    
    def set_model_api_key(self, api_key: str, key_name: Optional[str] = None) -> None:
        """Set API key for the model."""
        config = self.load_config()
        
        if not key_name:
            # Auto-detect key name based on provider
            if config.agent_config.provider.lower() == "openai":
                key_name = "OPENAI_API_KEY"
            elif config.agent_config.provider.lower() == "anthropic":
                key_name = "ANTHROPIC_API_KEY"
            elif config.agent_config.provider.lower() == "google":
                key_name = "GOOGLE_API_KEY"
            elif config.agent_config.provider.lower() == "azure":
                key_name = "AZURE_OPENAI_API_KEY"
            elif config.agent_config.provider.lower() == "cohere":
                key_name = "COHERE_API_KEY"
            elif config.agent_config.provider.lower() == "huggingface":
                key_name = "HUGGINGFACE_API_KEY"
            elif config.agent_config.provider.lower() == "groq":
                key_name = "GROQ_API_KEY"
            else:
                key_name = f"{config.agent_config.provider.upper()}_API_KEY"
        
        # Save the API key
        self.set_api_key(api_key, key_name)
        
        # Update agent config to remember the env var name
        self.update_agent_config(api_key_env_var=key_name)
    
    def get_backend_url(self) -> str:
        """Get backend URL from environment or config."""
        # Check environment variable first
        env_url = os.getenv("ASKBUDI_BACKEND_URL")
        if env_url:
            return env_url
            
        # Check config
        config = self.load_config()
        if config.backend_url:
            return config.backend_url
            
        # Default production URL
        return "https://ts-endpoint.askbudi.ai"
    
    def is_model_configured(self) -> bool:
        """Check if a model is properly configured with API key."""
        config = self.load_config()
        
        # Check if model name is set (not default)
        if config.agent_config.model_name == "gpt-5-mini":
            # Default model, check if it's intentionally set or just default
            api_key = self.get_model_api_key()
            return api_key is not None and len(api_key.strip()) > 0
        
        # Non-default model, check if API key is available
        api_key = self.get_model_api_key()
        return api_key is not None and len(api_key.strip()) > 0
    
    def validate_model_setup(self) -> Dict[str, Any]:
        """Validate model setup and return status information."""
        config = self.load_config()
        agent_config = config.agent_config
        
        status = {
            "configured": False,
            "model_name": agent_config.model_name,
            "provider": agent_config.provider,
            "has_api_key": False,
            "api_key_source": None,
            "missing_requirements": [],
            "recommendations": []
        }
        
        # Check API key
        api_key = self.get_model_api_key()
        if api_key and len(api_key.strip()) > 0:
            status["has_api_key"] = True
            
            # Determine API key source
            if os.getenv(self._get_default_api_key_name()):
                status["api_key_source"] = "system_environment"
            elif self._read_env_key(self.env_file, self._get_default_api_key_name()):
                status["api_key_source"] = "local_env"
            elif self._read_env_key(self.global_env_file, self._get_default_api_key_name()):
                status["api_key_source"] = "global_env"
        else:
            status["missing_requirements"].append(f"API key for {agent_config.provider}")
            status["recommendations"].append(f"Run '/model' to configure {agent_config.provider} API key")
        
        # Check if using default model without explicit configuration
        if agent_config.model_name == "gpt-5-mini" and not status["has_api_key"]:
            status["missing_requirements"].append("Model selection and API key")
            status["recommendations"].append("Run '/model' to select and configure your AI model")
        
        # Overall status
        status["configured"] = status["has_api_key"] and len(status["missing_requirements"]) == 0
        
        return status
    
    async def validate_api_key_with_backend(self, api_key: str) -> Dict[str, Any]:
        """Validate API key against the backend and return user info."""
        backend_url = self.get_backend_url()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{backend_url}/api/v1/wizard/register_client",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    # Update config with backend info
                    self.update_config(
                        api_key_set=True,
                        backend_url=backend_url,
                        client_uuid=data.get("client_uuid"),
                        user_level=data.get("user_level")
                    )
                    return data
                else:
                    error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                    return {
                        "valid": False,
                        "error": error_data.get("error", f"HTTP {response.status_code}")
                    }
                    
            except httpx.RequestError as e:
                return {
                    "valid": False,
                    "error": f"Connection error: {str(e)}"
                }
            except Exception as e:
                return {
                    "valid": False,
                    "error": f"Validation error: {str(e)}"
                }