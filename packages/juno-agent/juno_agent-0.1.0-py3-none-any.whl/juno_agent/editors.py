"""Editor management and MCP server installation functionality."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel

from .utils import run_command


class EditorConfig(BaseModel):
    """Configuration for a specific editor."""
    name: str
    config_file_name: str
    config_dir: Optional[str] = None
    install_command: Optional[str] = None
    rules_file: Optional[str] = None
    supported: bool = True


class MCPServerInstaller:
    """Manages MCP server installation for different editors."""
    
    def __init__(self, workdir: Path):
        self.workdir = workdir
        self.editors = self._get_supported_editors()
    
    def _get_supported_editors(self) -> Dict[str, EditorConfig]:
        """Get configuration for supported editors."""
        return {
            "claude-code": EditorConfig(
                name="Claude Code",
                config_file_name="claude_code_config.json",
                config_dir="~/.claude_code_config.json",
                rules_file="CLAUDE.md",
                supported=True,
            ),
            "claude-desktop": EditorConfig(
                name="Claude Desktop",
                config_file_name="claude_desktop_config.json",
                config_dir="~/Library/Application Support/Claude" if os.name != 'nt' else "%APPDATA%/Claude",
                rules_file="CLAUDE.md",
                supported=True,
            ),
            "cursor": EditorConfig(
                name="Cursor",
                config_file_name=".cursor/mcp.json",
                rules_file=".cursor/rules/vibe_context_mcp.mdc",
                supported=True,
            ),
            "windsurf": EditorConfig(
                name="Windsurf",
                config_file_name="settings.json",
                rules_file=".windsurfrules",
                supported=True,
            ),
            "trae": EditorConfig(
                name="Trae",
                config_file_name="mcp_config.json",
                rules_file="TRAE_RULES.md",
                supported=True,
            ),
            "vscode": EditorConfig(
                name="VS Code",
                config_file_name="settings.json",
                config_dir="~/.vscode",
                rules_file="VSCODE_RULES.md",
                supported=True,
            ),
            "visual-studio": EditorConfig(
                name="Visual Studio 2022",
                config_file_name="mcp_config.json",
                rules_file="VS_RULES.md",
                supported=True,
            ),
            "zed": EditorConfig(
                name="Zed",
                config_file_name="settings.json",
                config_dir="~/.config/zed",
                rules_file="ZED_RULES.md",
                supported=True,
            ),
            "cline": EditorConfig(
                name="Cline (VS Code Extension)",
                config_file_name="cline_config.json",
                rules_file="CLINE_RULES.md",
                supported=True,
            ),
            "boltai": EditorConfig(
                name="BoltAI",
                config_file_name="mcp_config.json",
                rules_file="BOLTAI_RULES.md",
                supported=True,
            ),
            "augment": EditorConfig(
                name="Augment Code",
                config_file_name="mcp_config.json",
                rules_file="AUGMENT_RULES.md",
                supported=True,
            ),
            "roo": EditorConfig(
                name="Roo Code",
                config_file_name="mcp_config.json",
                rules_file="ROO_RULES.md",
                supported=True,
            ),
            "gemini-cli": EditorConfig(
                name="Gemini CLI",
                config_file_name="mcp_config.json",
                rules_file="GEMINI_RULES.md",
                supported=True,
            ),
            "amazon-q": EditorConfig(
                name="Amazon Q Developer CLI",
                config_file_name="mcp_config.json",
                rules_file="AMAZON_Q_RULES.md",
                supported=True,
            ),
            "qodo-gen": EditorConfig(
                name="Qodo Gen",
                config_file_name="mcp_config.json",
                rules_file="QODO_RULES.md",
                supported=True,
            ),
            "jetbrains": EditorConfig(
                name="JetBrains AI Assistant",
                config_file_name="mcp_config.json",
                rules_file="JETBRAINS_RULES.md",
                supported=True,
            ),
            "warp": EditorConfig(
                name="Warp",
                config_file_name="mcp_config.json",
                rules_file="WARP_RULES.md",
                supported=True,
            ),
            "opencode": EditorConfig(
                name="Opencode",
                config_file_name="mcp_config.json",
                rules_file="OPENCODE_RULES.md",
                supported=True,
            ),
            "copilot-agent": EditorConfig(
                name="Copilot Coding Agent",
                config_file_name="mcp_config.json",
                rules_file="COPILOT_RULES.md",
                supported=True,
            ),
            "kiro": EditorConfig(
                name="Kiro",
                config_file_name="mcp_config.json",
                rules_file="KIRO_RULES.md",
                supported=True,
            ),
            "openai-codex": EditorConfig(
                name="OpenAI Codex",
                config_file_name="mcp_config.json",
                rules_file="CODEX_RULES.md",
                supported=True,
            ),
            "lm-studio": EditorConfig(
                name="LM Studio",
                config_file_name="mcp_config.json",
                rules_file="LM_STUDIO_RULES.md",
                supported=True,
            ),
            "zencoder": EditorConfig(
                name="Zencoder",
                config_file_name="mcp_config.json",
                rules_file="ZENCODER_RULES.md",
                supported=True,
            ),
        }
    
    def get_supported_editor_names(self) -> List[str]:
        """Get list of supported editor names."""
        return [name for name, config in self.editors.items() if config.supported]
    
    def is_editor_supported(self, editor_name: str) -> bool:
        """Check if an editor is supported."""
        # First try direct key match
        if editor_name in self.editors and self.editors[editor_name].supported:
            return True
        # Then try display name match
        return self._get_editor_key_by_name(editor_name) is not None
        
    def _get_editor_key_by_name(self, editor_name: str) -> Optional[str]:
        """Get editor key by display name or key."""
        # First try direct key match
        if editor_name in self.editors:
            return editor_name
        # Then try display name match
        for key, config in self.editors.items():
            if config.name == editor_name and config.supported:
                return key
        return None
    
    def install_mcp_server(self, editor_name: str, api_key: str) -> Tuple[bool, str]:
        """Install MCP server for the specified editor."""
        if not self.is_editor_supported(editor_name):
            return False, f"Editor '{editor_name}' is not supported"
        
        # Get the actual editor key (handles display name to key mapping)
        editor_key = self._get_editor_key_by_name(editor_name)
        if not editor_key:
            return False, f"Editor '{editor_name}' is not supported"
            
        editor_config = self.editors[editor_key]
        
        # Map editor keys to installation methods
        installation_methods = {
            "claude-code": self._install_claude_code_mcp,
            "claude-desktop": self._install_claude_desktop_mcp,
            "cursor": self._install_cursor_mcp,
            "windsurf": self._install_windsurf_mcp,
            "vscode": self._install_vscode_mcp,
            "zed": self._install_zed_mcp,
            "cline": self._install_cline_mcp,
        }
        
        install_method = installation_methods.get(editor_key)
        if install_method:
            return install_method(api_key)
        else:
            # For other editors, create a generic MCP configuration placeholder
            return self._create_mcp_placeholder(editor_key, api_key)
    
    def _install_claude_code_mcp(self, api_key: str) -> Tuple[bool, str]:
        """Install MCP server for Claude Code."""
        try:
            # Use relative path in project for Claude Code config
            config_file = self.workdir / ".claude_code_config.json"
            
            # Load existing config or create new one
            if config_file.exists():
                with open(config_file, "r") as f:
                    config = json.load(f)
            else:
                config = {"mcpServers": {}}
            
            # Ensure mcpServers exists
            if "mcpServers" not in config:
                config["mcpServers"] = {}
            
            # Add our MCP server with relative path
            config["mcpServers"]["askbudi-vibe-context"] = {
                "command": "npx",
                "args": ["-y", "askbudi-context@latest"],
                "env": {
                    "ASKBUDI_API_KEY": api_key,
                    "PLATFORM": "claude"
                }
            }
            
            # Save config
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)
            
            return True, f"MCP server installed successfully for Claude Code at {config_file}"
            
        except Exception as e:
            return False, f"Failed to install MCP server for Claude Code: {e}"
    
    def _install_claude_desktop_mcp(self, api_key: str) -> Tuple[bool, str]:
        """Install MCP server for Claude Desktop."""
        try:
            # Use system config for Claude Desktop
            if os.name == 'nt':  # Windows
                config_dir = Path.home() / "AppData" / "Roaming" / "Claude"
            else:  # macOS/Linux
                config_dir = Path.home() / "Library" / "Application Support" / "Claude"
            
            config_dir.mkdir(parents=True, exist_ok=True)
            config_file = config_dir / "claude_desktop_config.json"
            
            # Load existing config or create new one
            if config_file.exists():
                with open(config_file, "r") as f:
                    config = json.load(f)
            else:
                config = {"mcpServers": {}}
            
            # Ensure mcpServers exists
            if "mcpServers" not in config:
                config["mcpServers"] = {}
            
            # Add our MCP server
            config["mcpServers"]["askbudi"] = {
                "command": "npx",
                "args": ["-y", "askbudi-context@latest"],
                "env": {
                    "ASKBUDI_API_KEY": api_key,
                    "PLATFORM": "claude-desktop"
                }
            }
            
            # Save config
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)
            
            return True, f"MCP server installed successfully for Claude Desktop at {config_file}"
            
        except Exception as e:
            return False, f"Failed to install MCP server for Claude Desktop: {e}"
    
    def _install_cursor_mcp(self, api_key: str) -> Tuple[bool, str]:
        """Install MCP server for Cursor using the proper format according to official documentation."""
        try:
            # Import here to avoid circular imports
            from .fancy_ui.setup.mcp_installer import MCPInstaller
            
            # Use the MCPInstaller for proper Cursor integration
            installer = MCPInstaller()
            success = installer.install_mcp_servers('cursor', self.workdir, api_key)
            
            if success:
                mcp_config_file = self.workdir / ".cursor" / "mcp.json"
                rules_file = self.workdir / ".cursor" / "rules" / "vibe_context_mcp.mdc"
                return True, f"MCP server installed for Cursor at {mcp_config_file} and rules at {rules_file}"
            else:
                return False, "Failed to install MCP server for Cursor"
            
        except Exception as e:
            return False, f"Failed to install MCP server for Cursor: {e}"
    
    def _install_windsurf_mcp(self, api_key: str) -> Tuple[bool, str]:
        """Install MCP server for Windsurf."""
        try:
            # For Windsurf, we add to .windsurfrules file
            rules_file = self.workdir / ".windsurfrules"
            
            rules_content = f"""# Windsurf Rules for VibeContext MCP Server

## MCP Server Configuration
This project uses the VibeContext MCP server for enhanced documentation access.

### Setup Instructions:
1. Install the MCP server: `npm install -g @askbudi/vibe-context-mcp`
2. Set your API key: `export ASKBUDI_API_KEY={api_key}`
3. Configure in Windsurf:
   - Open Windsurf Settings
   - Go to MCP Servers section
   - Add: @askbudi/vibe-context-mcp

### Available Tools:
- resolve_library_id: Search for libraries by name
- get_library_docs: Get documentation for specific libraries
- fetch_doc_url: Fetch documentation from URLs

### Usage Guidelines:
- Always use the MCP server for library documentation
- Verify library information with resolve_library_id before use
- Use get_library_docs with specific prompts for targeted help

## Development Guidelines:
- Follow project coding standards
- Use MCP server for accurate, up-to-date documentation
- Prefer official docs from MCP server over general knowledge
"""
            
            # Append to existing rules or create new file
            if rules_file.exists():
                with open(rules_file, "r") as f:
                    existing_content = f.read()
                
                if "VibeContext MCP Server" not in existing_content:
                    with open(rules_file, "a") as f:
                        f.write("\n\n" + rules_content)
            else:
                with open(rules_file, "w") as f:
                    f.write(rules_content)
            
            return True, f"MCP server configuration added to {rules_file}"
            
        except Exception as e:
            return False, f"Failed to configure MCP server for Windsurf: {e}"
    
    def _install_vscode_mcp(self, api_key: str) -> Tuple[bool, str]:
        """Install MCP server for VS Code."""
        try:
            # Create .vscode directory and settings.json file (relative to project)
            vscode_dir = self.workdir / ".vscode"
            vscode_dir.mkdir(exist_ok=True)
            
            settings_file = vscode_dir / "settings.json"
            
            # Load existing settings or create new one
            if settings_file.exists():
                with open(settings_file, "r") as f:
                    settings = json.load(f)
            else:
                settings = {}
            
            # Add MCP server configuration
            if "mcp.servers" not in settings:
                settings["mcp.servers"] = {}
            
            settings["mcp.servers"]["askbudi"] = {
                "command": "npx",
                "args": ["-y", "askbudi-context@latest"],
                "env": {
                    "ASKBUDI_API_KEY": api_key,
                    "PLATFORM": "vscode"
                }
            }
            
            # Save settings
            with open(settings_file, "w") as f:
                json.dump(settings, f, indent=2)
            
            return True, f"MCP server installed for VS Code at {settings_file}"
            
        except Exception as e:
            return False, f"Failed to install MCP server for VS Code: {e}"
    
    def _install_zed_mcp(self, api_key: str) -> Tuple[bool, str]:
        """Install MCP server for Zed."""
        try:
            # For Zed, create a local settings.json file
            zed_dir = self.workdir / ".zed"
            zed_dir.mkdir(exist_ok=True)
            
            settings_file = zed_dir / "settings.json"
            
            # Load existing settings or create new one
            if settings_file.exists():
                with open(settings_file, "r") as f:
                    settings = json.load(f)
            else:
                settings = {}
            
            # Add MCP server configuration
            if "assistant" not in settings:
                settings["assistant"] = {}
            if "mcp_servers" not in settings["assistant"]:
                settings["assistant"]["mcp_servers"] = {}
            
            settings["assistant"]["mcp_servers"]["askbudi"] = {
                "command": "npx",
                "args": ["-y", "askbudi-context@latest"],
                "env": {
                    "ASKBUDI_API_KEY": api_key,
                    "PLATFORM": "zed"
                }
            }
            
            # Save settings
            with open(settings_file, "w") as f:
                json.dump(settings, f, indent=2)
            
            return True, f"MCP server installed for Zed at {settings_file}"
            
        except Exception as e:
            return False, f"Failed to install MCP server for Zed: {e}"
    
    def _install_cline_mcp(self, api_key: str) -> Tuple[bool, str]:
        """Install MCP server for Cline (VS Code Extension)."""
        try:
            # Create .vscode directory and settings.json file for Cline
            vscode_dir = self.workdir / ".vscode"
            vscode_dir.mkdir(exist_ok=True)
            
            settings_file = vscode_dir / "settings.json"
            
            # Load existing settings or create new one
            if settings_file.exists():
                with open(settings_file, "r") as f:
                    settings = json.load(f)
            else:
                settings = {}
            
            # Add Cline MCP server configuration
            if "cline.mcp.servers" not in settings:
                settings["cline.mcp.servers"] = {}
            
            settings["cline.mcp.servers"]["askbudi"] = {
                "command": "npx",
                "args": ["-y", "askbudi-context@latest"],
                "env": {
                    "ASKBUDI_API_KEY": api_key,
                    "PLATFORM": "cline"
                }
            }
            
            # Save settings
            with open(settings_file, "w") as f:
                json.dump(settings, f, indent=2)
            
            return True, f"MCP server installed for Cline at {settings_file}"
            
        except Exception as e:
            return False, f"Failed to install MCP server for Cline: {e}"
    
    def _create_mcp_placeholder(self, editor_name: str, api_key: str) -> Tuple[bool, str]:
        """Create a generic MCP configuration placeholder for unsupported editors."""
        try:
            # Create a generic MCP configuration file
            config_file = self.workdir / f".{editor_name.lower()}_mcp_config.json"
            
            config = {
                "mcp": {
                    "servers": {
                        "askbudi": {
                            "command": "npx",
                            "args": ["-y", "askbudi-context@latest"],
                            "env": {
                                "ASKBUDI_API_KEY": api_key,
                                "PLATFORM": editor_name.lower()
                            }
                        }
                    }
                }
            }
            
            with open(config_file, "w") as f:
                json.dump(config, f, indent=2)
            
            # Create instructions file
            instructions_file = self.workdir / f"{editor_name.upper()}_MCP_SETUP.md"
            instructions_content = f"""# MCP Server Setup for {editor_name}

## Configuration Created
A MCP server configuration has been created at `{config_file.name}`.

## Manual Setup Required
Since {editor_name} is not yet fully supported by the wizard, you'll need to manually configure the MCP server:

1. Copy the configuration from `{config_file.name}` to your {editor_name} settings
2. Ensure your API key is set: `{api_key}`
3. Restart {editor_name} to load the MCP server

## Configuration Details
```json
{json.dumps(config, indent=2)}
```

## Available Tools
- `resolve_library_id`: Search for libraries by name
- `get_library_docs`: Get documentation for specific libraries  
- `fetch_doc_url`: Fetch documentation from URLs

## Need Help?
Visit https://askbudi.ai/docs for more information or contact support.
"""
            
            with open(instructions_file, "w") as f:
                f.write(instructions_content)
            
            return True, f"MCP configuration created at {config_file} with setup instructions at {instructions_file}"
            
        except Exception as e:
            return False, f"Failed to create MCP configuration for {editor_name}: {e}"
    
    def create_rules_file(self, editor_name: str, project_info, libraries: List[str]) -> Tuple[bool, str]:
        """Create or update rules file for the specified editor."""
        if not self.is_editor_supported(editor_name):
            return False, f"Editor '{editor_name}' is not supported"
        
        # Get the actual editor key (handles display name to key mapping)
        editor_key = self._get_editor_key_by_name(editor_name)
        if not editor_key:
            return False, f"Editor '{editor_name}' is not supported"
        
        editor_config = self.editors[editor_key]
        
        if not editor_config.rules_file:
            return False, f"No rules file defined for {editor_name}"
        
        rules_file = self.workdir / editor_config.rules_file
        
        try:
            # Generate rules content based on project info
            rules_content = self._generate_rules_content(editor_name, project_info, libraries)
            
            # Write to rules file
            with open(rules_file, "w") as f:
                f.write(rules_content)
            
            return True, f"Rules file created at {rules_file}"
            
        except Exception as e:
            return False, f"Failed to create rules file: {e}"
    
    def _generate_rules_content(self, editor_name: str, project_info, libraries: List[str]) -> str:
        """Generate rules file content based on project information."""
        content = f"""# {editor_name} Rules for Project

## Project Information
- **Languages**: {', '.join(project_info.languages) if project_info.languages else 'Not detected'}
- **Frameworks**: {', '.join(project_info.frameworks) if project_info.frameworks else 'Not detected'}
- **Package Managers**: {', '.join(project_info.package_managers) if project_info.package_managers else 'Not detected'}

## Dependencies
The following libraries are used in this project:
"""
        
        if libraries:
            for lib in libraries:
                content += f"- {lib}\n"
        else:
            content += "- No libraries detected\n"
        
        content += f"""
## MCP Server Integration
This project is configured to use the VibeContext MCP server for enhanced documentation access.

### Available Tools:
- `resolve_library_id`: Search for libraries by name to get the correct library ID
- `get_library_docs`: Get documentation for specific libraries using library ID and prompt
- `fetch_doc_url`: Fetch and convert documentation from URLs to markdown

### Usage Guidelines:
1. Always use `resolve_library_id` first to find the correct library identifier
2. Use `get_library_docs` with specific questions about the library
3. Prefer MCP server documentation over general knowledge for accuracy
4. Use `fetch_doc_url` for external documentation when needed

## Coding Guidelines:
- Follow the existing code patterns and conventions in this project
- Use the detected frameworks and libraries appropriately
- Always test your changes thoroughly
- Keep code clean and well-documented

## Library-Specific Notes:
"""
        
        # Add framework-specific guidelines
        if "FastAPI" in project_info.frameworks:
            content += """
### FastAPI Guidelines:
- Use type hints for all endpoints
- Follow REST conventions for API design
- Use dependency injection for shared logic
- Document endpoints with proper docstrings
"""
        
        if "React" in project_info.frameworks:
            content += """
### React Guidelines:
- Use functional components with hooks
- Follow component composition patterns
- Use TypeScript for type safety
- Keep components small and focused
"""
        
        if "Django" in project_info.frameworks:
            content += """
### Django Guidelines:
- Follow Django conventions and patterns
- Use Django ORM properly
- Implement proper error handling
- Follow security best practices
"""
        
        return content