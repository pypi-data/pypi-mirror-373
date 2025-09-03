"""API Key Management for VibeContext integration."""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class APIKeyValidationError(Exception):
    """Raised when API key validation fails."""
    pass


class APIKeyNotFoundError(Exception):
    """Raised when API key is not found."""
    pass


class APIKeyManager:
    """Manages ASKBUDI API keys with hierarchical configuration."""

    def __init__(self, home_dir: Optional[Path] = None, project_dir: Optional[Path] = None):
        """
        Initialize APIKeyManager.
        
        Args:
            home_dir: Home directory path (defaults to user's home)
            project_dir: Project directory path (defaults to current directory)
        """
        self.home_dir = home_dir or Path.home()
        self.project_dir = project_dir or Path.cwd()
        
        self.global_config_path = self.home_dir / ".askbudi" / "global_config.json"
        self.project_config_path = self.project_dir / ".askbudi" / "config.json"
        self.env_file_path = self.home_dir / ".ASKBUDI" / ".env"
        
        self.console = Console()

    def get_askbudi_api_key(self) -> Optional[str]:
        """
        Get ASKBUDI API key from sources in priority order:
        1. Environment variable ASKBUDI_API_KEY
        2. ~/.ASKBUDI/.env file
        3. ~/.askbudi/global_config.json
        4. Project .askbudi/config.json
        
        Returns:
            API key string or None if not found
        """
        # 1. Check environment variable first
        env_key = os.environ.get("ASKBUDI_API_KEY")
        if env_key:
            # Auto-save to .env file if not already there
            self._save_to_env_file(env_key.strip())
            return env_key.strip()
        
        # 2. Check ~/.ASKBUDI/.env file
        env_file_key = self._load_from_env_file()
        if env_file_key:
            return env_file_key
        
        # 3. Check global config
        global_key = self._read_config_key(self.global_config_path)
        if global_key:
            return global_key
        
        # 4. Check project config
        project_key = self._read_config_key(self.project_config_path)
        if project_key:
            return project_key
        
        return None

    def _read_config_key(self, config_path: Path) -> Optional[str]:
        """
        Read API key from a config file.
        
        Args:
            config_path: Path to the config file
            
        Returns:
            API key string or None if not found/invalid
        """
        try:
            if not config_path.exists():
                return None
            
            content = config_path.read_text().strip()
            if not content:
                return None
            
            config = json.loads(content)
            api_key = config.get("askbudi_api_key")
            
            if isinstance(api_key, str) and api_key.strip():
                return api_key.strip()
            
            return None
        except (json.JSONDecodeError, PermissionError, OSError):
            return None

    def _load_from_env_file(self) -> Optional[str]:
        """
        Load API key from ~/.ASKBUDI/.env file.
        
        Returns:
            API key string or None if not found/invalid
        """
        try:
            if not self.env_file_path.exists():
                return None
            
            content = self.env_file_path.read_text().strip()
            if not content:
                return None
            
            # Parse .env format: ASKBUDI_API_KEY=value
            for line in content.split('\n'):
                line = line.strip()
                if line.startswith('ASKBUDI_API_KEY='):
                    api_key = line.split('=', 1)[1].strip()
                    # Remove quotes if present
                    if api_key.startswith('"') and api_key.endswith('"'):
                        api_key = api_key[1:-1]
                    elif api_key.startswith("'") and api_key.endswith("'"):
                        api_key = api_key[1:-1]
                    
                    if api_key:
                        return api_key
            
            return None
        except (PermissionError, OSError):
            return None

    def _save_to_env_file(self, api_key: str) -> None:
        """
        Save API key to ~/.ASKBUDI/.env file.
        
        Args:
            api_key: The API key to save
        """
        try:
            # Check if key already exists in .env file to avoid unnecessary writes
            existing_key = self._load_from_env_file()
            if existing_key == api_key:
                return
            
            # Ensure directory exists
            self._ensure_askbudi_directory()
            
            # Read existing content
            existing_content = ""
            other_lines = []
            if self.env_file_path.exists():
                content = self.env_file_path.read_text()
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('ASKBUDI_API_KEY='):
                        other_lines.append(line)
            
            # Write new content
            lines = other_lines + [f'ASKBUDI_API_KEY={api_key}']
            new_content = '\n'.join(lines)
            
            with open(self.env_file_path, 'w') as f:
                f.write(new_content)
        except (PermissionError, OSError):
            # Silently handle errors - .env file is optional
            pass

    def _ensure_askbudi_directory(self) -> None:
        """
        Create ~/.ASKBUDI directory if it doesn't exist.
        """
        try:
            self.env_file_path.parent.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError):
            # Silently handle errors - directory creation is optional
            pass

    async def validate_api_key(self, api_key: str) -> bool:
        """
        Validate API key by testing connection to ASKBUDI service.
        
        Args:
            api_key: The API key to validate
            
        Returns:
            True if key is valid, False otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                headers = {"Authorization": f"Bearer {api_key}"}
                # Use a simple endpoint to test the key
                response = await client.get(
                    "https://api.askbudi.com/v1/status",
                    headers=headers,
                    timeout=10.0
                )
                return response.status_code == 200
        except (httpx.RequestError, httpx.TimeoutException):
            return False

    def save_api_key(self, api_key: str, global_save: bool = True) -> None:
        """
        Save API key to configuration file and .env file.
        
        Args:
            api_key: The API key to save
            global_save: If True, save to global config, otherwise project config
        """
        config_path = self.global_config_path if global_save else self.project_config_path
        
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Read existing config or create new
        config = {}
        if config_path.exists():
            try:
                content = config_path.read_text().strip()
                if content:
                    config = json.loads(content)
            except (json.JSONDecodeError, OSError):
                config = {}
        
        # Update config with API key
        config["askbudi_api_key"] = api_key
        
        # Write back to file
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Also save to .env file
        self._save_to_env_file(api_key)

    def clear_api_key(self, global_clear: bool = True) -> None:
        """
        Clear API key from configuration file.
        
        Args:
            global_clear: If True, clear from global config, otherwise project config
        """
        config_path = self.global_config_path if global_clear else self.project_config_path
        
        if not config_path.exists():
            return
        
        try:
            content = config_path.read_text().strip()
            if not content:
                return
            
            config = json.loads(content)
            if "askbudi_api_key" in config:
                del config["askbudi_api_key"]
                
                with open(config_path, 'w') as f:
                    json.dump(config, f, indent=2)
        except (json.JSONDecodeError, OSError):
            pass

    def has_valid_api_key(self) -> bool:
        """
        Check if a valid API key is available.
        
        Returns:
            True if API key exists, False otherwise
        """
        return self.get_askbudi_api_key() is not None

    def get_value_proposition_message(self) -> str:
        """
        Get the value proposition message for VibeContext enhancement.
        
        Returns:
            Formatted message explaining VibeContext benefits
        """
        return """
🚀 Enhance Your Development Experience with VibeContext!

VibeContext provides powerful enhancements to your development workflow:

✨ Enhanced Code Intelligence:
   • Smart code completion and suggestions
   • Context-aware documentation lookup  
   • Intelligent error analysis and fixes

🔍 Advanced Search & Discovery:
   • Search across multiple code repositories
   • Find relevant code examples and patterns
   • Discover best practices for your tech stack

📚 Real-time Documentation:
   • Up-to-date library documentation
   • Interactive code examples
   • Integration guides and tutorials

🤖 AI-Powered Assistance:
   • Contextual help and explanations
   • Code review suggestions
   • Architecture recommendations

Get your FREE API key at: https://askbudi.com/signup
Or continue with basic features (limited functionality)
        """.strip()

    async def prompt_for_api_key(self) -> Optional[str]:
        """
        Prompt user for API key using rich console interface.
        
        This method provides a console-based prompt for API key entry.
        For full Textual UI integration, this would be implemented in the main app.
        
        Returns:
            API key if provided, None if skipped
        """
        # Display value proposition
        self.console.print(Panel(
            self.get_value_proposition_message(),
            title="🔮 VibeContext Enhanced Features",
            border_style="bright_blue"
        ))
        
        while True:
            self.console.print("\n[bold cyan]Choose an option:[/]")
            self.console.print("1. Enter ASKBUDI API Key")
            self.console.print("2. Continue with basic features")
            self.console.print("3. Learn more about VibeContext")
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                api_key = input("\nEnter your ASKBUDI API Key: ").strip()
                if api_key:
                    self.console.print("\n[yellow]Validating API key...[/]")
                    is_valid = await self.validate_api_key(api_key)
                    
                    if is_valid:
                        # Ask where to save
                        save_choice = input("\nSave globally for all projects? (y/n): ").strip().lower()
                        global_save = save_choice in ('y', 'yes', '')
                        
                        self.save_api_key(api_key, global_save=global_save)
                        
                        save_location = "globally" if global_save else "for this project"
                        self.console.print(f"\n[green]✅ API key validated and saved {save_location}![/]")
                        return api_key
                    else:
                        self.console.print("\n[red]❌ Invalid API key. Please check and try again.[/]")
                else:
                    self.console.print("\n[red]❌ API key cannot be empty.[/]")
            
            elif choice == "2":
                self.console.print("\n[yellow]Continuing with basic features...[/]")
                return None
            
            elif choice == "3":
                self.console.print(Panel(
                    """
Visit https://askbudi.com to:
• Sign up for a FREE account
• Get your API key instantly  
• Access comprehensive documentation
• Join the developer community

VibeContext integrates seamlessly with your existing workflow
and provides intelligent assistance without disrupting your process.
                    """.strip(),
                    title="Learn More About VibeContext",
                    border_style="bright_green"
                ))
            else:
                self.console.print("\n[red]Invalid choice. Please enter 1, 2, or 3.[/]")