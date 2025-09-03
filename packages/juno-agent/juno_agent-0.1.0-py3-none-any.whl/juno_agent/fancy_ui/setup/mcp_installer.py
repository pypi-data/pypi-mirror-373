"""
MCP Server Installation Service

This service installs and configures MCP servers for different AI IDEs,
with a focus on the VibeContext MCP server. It provides cross-platform
compatibility and proper error handling.
"""

import json
import logging
import os
import platform
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from .api_key_manager import APIKeyManager

logger = logging.getLogger(__name__)


class MCPInstallationError(Exception):
    """Custom exception for MCP installation errors."""
    pass


class MCPInstaller:
    """Service for installing and configuring MCP servers across different AI IDEs."""
    
    def __init__(self, workdir=None, project_dir=None):
        """Initialize the MCP installer service.
        
        Args:
            workdir: Optional working directory (ignored, for compatibility).
                     This parameter is accepted to handle cases where MCPInstaller
                     might be incorrectly called with an argument.
            project_dir: Optional project directory for API key management.
        """
        # Ignore workdir parameter if provided - MCPInstaller doesn't need it
        # This is a defensive fix for cases where it might be called with an argument
        self.system = platform.system().lower()
        self.home_dir = Path.home()
        self._ide_config = None
        
        # Initialize API key manager
        self.api_key_manager = APIKeyManager(
            home_dir=self.home_dir,
            project_dir=project_dir or Path.cwd()
        )

    def should_install_mcp(self) -> bool:
        """
        Check if MCP should be installed based on API key availability.
        
        Returns:
            True if valid API key is available, False otherwise
        """
        return self.api_key_manager.has_valid_api_key()

    def get_api_key_status(self) -> Dict[str, Any]:
        """
        Get current API key status information.
        
        Returns:
            Dictionary with API key status details
        """
        has_key = self.api_key_manager.has_valid_api_key()
        api_key_source = None
        
        if has_key:
            # Determine API key source
            if os.environ.get("ASKBUDI_API_KEY"):
                api_key_source = "Environment variable"
            elif self.api_key_manager.global_config_path.exists():
                api_key_source = "Global configuration"
            elif self.api_key_manager.project_config_path.exists():
                api_key_source = "Project configuration"
        
        return {
            'has_api_key': has_key,
            'api_key_source': api_key_source,
            'can_install_mcp': has_key,
        }
        
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
    
    def get_supported_editors(self) -> Dict[str, Dict[str, Any]]:
        """Get supported editors from JSON configuration with fallback to legacy config."""
        config = self._load_ide_config()
        
        if not config or 'ides' not in config:
            logger.warning("Using fallback editor configuration")
            return self._get_legacy_supported_editors()
        
        # Convert JSON config to legacy format for compatibility
        supported_editors = {}
        
        for ide_key, ide_data in config['ides'].items():
            if not ide_data.get('supported', False):
                continue
                
            mcp_config = ide_data.get('mcp_config', {})
            
            # Map JSON config to legacy format
            supported_editors[ide_key] = {
                'name': ide_data.get('display_name', ide_key.title()),
                'config_filename': self._extract_filename(mcp_config.get('config_file_path', '')),
                'config_location': self._determine_config_location(ide_key, mcp_config.get('config_file_path', '')),
                'mcp_key': mcp_config.get('config_key', 'mcpServers'),
                'config_method': mcp_config.get('config_method', 'file'),
                'config_format': mcp_config.get('config_format', 'json'),
                'connection_types': ide_data.get('connection_types', ['local_npm']),
                'one_click_install': ide_data.get('one_click_install', False),
                'installation_method': ide_data.get('installation_method', 'JSON configuration'),
                'custom_instructions': ide_data.get('custom_instructions', {})
            }
        
        return supported_editors
    
    def _get_legacy_supported_editors(self) -> Dict[str, Dict[str, Any]]:
        """Get legacy supported editors configuration as fallback."""
        return {
            'claude_code': {
                'name': 'Claude Code',
                'config_filename': '.claude_code_config.json',
                'config_location': 'home',  # ~/.claude_code_config.json
                'mcp_key': 'mcpServers',
                'config_method': 'command',
                'config_format': 'cli',
                'connection_types': ['remote_http', 'remote_sse', 'local_npm'],
                'one_click_install': False
            },
            'cursor': {
                'name': 'Cursor',
                'config_filename': 'mcp.json',
                'config_location': 'project',  # .cursor/mcp.json
                'mcp_key': 'mcpServers',
                'config_method': 'file',
                'config_format': 'json',
                'connection_types': ['remote_http', 'local_npm'],
                'one_click_install': True
            },
            'windsurf': {
                'name': 'Windsurf',
                'config_filename': 'mcp_config.json',
                'config_location': 'windsurf_home',  # ~/.codeium/windsurf/mcp_config.json
                'mcp_key': 'mcpServers',
                'config_method': 'file',
                'config_format': 'json',
                'connection_types': ['remote_http', 'local_npm'],
                'one_click_install': False
            },
            'vscode': {
                'name': 'VS Code',
                'config_filename': 'mcp.json',
                'config_location': 'project',  # .vscode/mcp.json
                'mcp_key': 'mcp.servers',
                'config_method': 'file',
                'config_format': 'json',
                'connection_types': ['remote_http', 'local_stdio'],
                'one_click_install': True
            }
        }
    
    def _extract_filename(self, config_file_path: str) -> str:
        """Extract filename from config file path."""
        if not config_file_path:
            return 'mcp.json'
        
        if '/' in config_file_path:
            return Path(config_file_path).name
        
        return config_file_path
    
    def _determine_config_location(self, ide_key: str, config_file_path: str) -> str:
        """Determine config location type from file path."""
        if not config_file_path:
            return 'project'
        
        if config_file_path.startswith('~/'):
            if 'windsurf' in ide_key.lower() or '.codeium' in config_file_path:
                return 'windsurf_home'
            return 'home'
        
        if config_file_path.startswith('.'):
            return 'project'
        
        return 'project'  # Default to project-based
    
    @property
    def SUPPORTED_EDITORS(self) -> Dict[str, Dict[str, Any]]:
        """Property to access supported editors configuration."""
        return self.get_supported_editors()
        
    def install_mcp_servers(self, editor: str, project_path: Path, api_key: str = None) -> bool:
        """
        Install and configure MCP servers for a specific editor.
        
        Args:
            editor: Editor identifier (e.g., 'claude_code', 'cursor')
            project_path: Path to the project directory
            api_key: Optional API key for the VibeContext service. If not provided,
                    will use APIKeyManager to find valid key or skip installation.
            
        Returns:
            bool: True if installation was successful
            
        Raises:
            MCPInstallationError: If installation fails
        """
        if editor not in self.SUPPORTED_EDITORS:
            raise MCPInstallationError(
                f"Unsupported editor: {editor}. "
                f"Supported editors: {', '.join(self.SUPPORTED_EDITORS.keys())}"
            )
        
        # Determine API key to use - provided key takes precedence
        effective_api_key = api_key or self.api_key_manager.get_askbudi_api_key()
        
        if not effective_api_key:
            logger.warning(
                "No valid ASKBUDI API key found. Skipping MCP installation. "
                "VibeContext features will not be available."
            )
            print("⚠️  No valid ASKBUDI_API_KEY found. Skipping MCP installation.")
            print("   To enable VibeContext features:")
            print("   1. Get your free API key: https://askbudi.com/signup")
            print("   2. Set ASKBUDI_API_KEY environment variable, or")
            print("   3. Run setup wizard to configure API key")
            return False
        
        try:
            logger.info(f"Installing MCP servers for {self.SUPPORTED_EDITORS[editor]['name']}")
            
            # Get the configuration path for this editor
            config_path = self.get_mcp_config_path(editor, project_path)
            
            # Create the VibeContext MCP server configuration
            mcp_config = self.create_vibe_context_config(project_path, effective_api_key)
            
            # Update the IDE configuration
            success = self.update_ide_config(config_path, mcp_config, editor)
            
            # For Cursor, migrate legacy .cursorrules (but don't create new .cursor/rules/)
            if editor == 'cursor' and success:
                # Migrate legacy .cursorrules first
                migration_success = self.migrate_legacy_cursorrules(project_path)
                if not migration_success:
                    logger.warning("Failed to migrate legacy .cursorrules file")
                
                # Create AGENTS.md instead of .cursor/rules/
                agents_success = self.create_agents_md(project_path, editor)
                if not agents_success:
                    logger.warning("Failed to create AGENTS.md, but MCP configuration was successful")
            
            # For non-Claude IDEs with project-based configs, create AGENTS.md with IDE-specific instructions
            elif editor != 'claude_code' and success:
                editor_config = self.SUPPORTED_EDITORS[editor]
                location = editor_config.get('config_location', 'project')
                
                # Only create AGENTS.md for project-based configurations
                if location == 'project' and project_path and project_path != Path("/dummy"):
                    agents_success = self.create_agents_md(project_path, editor)
                    if not agents_success:
                        logger.warning("Failed to create AGENTS.md, but MCP configuration was successful")
            
            if success:
                logger.info(f"Successfully installed MCP servers for {editor}")
                return True
            else:
                raise MCPInstallationError(f"Failed to update configuration for {editor}")
                
        except Exception as e:
            logger.error(f"MCP installation failed: {str(e)}")
            raise MCPInstallationError(f"Installation failed: {str(e)}")
    
    def get_mcp_config_path(self, editor: str, project_path: Optional[Path] = None) -> Path:
        """
        Get the MCP configuration file path for a specific editor.
        
        Args:
            editor: Editor identifier
            project_path: Project directory path (required for project-based configs)
            
        Returns:
            Path: Configuration file path
            
        Raises:
            MCPInstallationError: If path cannot be determined
        """
        if editor not in self.SUPPORTED_EDITORS:
            raise MCPInstallationError(f"Unsupported editor: {editor}")
        
        editor_config = self.SUPPORTED_EDITORS[editor]
        location = editor_config['config_location']
        filename = editor_config['config_filename']
        
        try:
            # First, check if we have a full config_file_path from the JSON config
            ide_info = self.get_ide_info(editor)
            if ide_info and 'mcp_config' in ide_info:
                config_file_path = ide_info['mcp_config'].get('config_file_path', '')
                if config_file_path.startswith('~/'):
                    # Handle home directory paths like ~/.gemini/settings.json
                    relative_path = config_file_path[2:]  # Remove ~/
                    return self.home_dir / relative_path
            
            if location == 'home':
                # Home directory config (~/.claude_code_config.json)
                return self.home_dir / filename
                
            elif location == 'project':
                # Project-based config (.cursor/mcp.json, .vscode/mcp.json)
                if not project_path:
                    raise MCPInstallationError("Project path required for project-based configuration")
                
                # For Cursor, use .cursor directory, for VSCode use .vscode, etc.
                if editor == 'cursor':
                    config_dir = project_path / ".cursor"
                elif editor == 'vscode':
                    config_dir = project_path / ".vscode" 
                else:
                    config_dir = project_path / f".{editor.replace('_', '')}"
                return config_dir / filename
                
            elif location == 'windsurf_home':
                # Windsurf-specific home config (~/.codeium/windsurf/mcp_config.json)
                windsurf_dir = self.home_dir / '.codeium' / 'windsurf'
                return windsurf_dir / filename
                
            else:
                raise MCPInstallationError(f"Unknown config location: {location}")
                
        except Exception as e:
            raise MCPInstallationError(f"Failed to determine config path: {str(e)}")
    
    def create_vibe_context_config(self, project_path: Path, api_key: str) -> Dict[str, Any]:
        """
        Create the VibeContext MCP server configuration.
        
        Args:
            project_path: Path to the project directory
            api_key: API key for VibeContext service
            
        Returns:
            Dict containing MCP server configuration
        """
        # Determine the path to the VibeContext MCP server
        # Look for it in the project structure first, then fallback to npm
        vibe_context_path = self._find_vibe_context_server(project_path)
        
        if vibe_context_path and vibe_context_path.exists():
            # Use local build
            logger.info(f"Using local VibeContext server at: {vibe_context_path}")
            command = "node"
            args = [str(vibe_context_path)]
        else:
            # Use npm package
            logger.info("Using VibeContext server from npm")
            command = "npx"
            args = ["-y", "askbudi-context@latest"]
        
        mcp_config = {
            "vibe_context": {
                "command": command,
                "args": args,
                "env": {
                    "ASKBUDI_API_KEY": api_key,
                    "PLATFORM": "claude"
                }
            }
        }
        
        # Add configuration guidelines as comments in JSON (where supported)
        self._add_config_guidelines(mcp_config)
        
        return mcp_config
    
    def update_ide_config(self, config_path: Path, mcp_config: Dict[str, Any], editor: str) -> bool:
        """
        Update the IDE configuration file with MCP server settings.
        
        Args:
            config_path: Path to the configuration file
            mcp_config: MCP configuration to add
            editor: Editor identifier
            
        Returns:
            bool: True if update was successful
        """
        try:
            # Ensure the configuration directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Read existing configuration
            existing_config = {}
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        existing_config = json.load(f)
                    logger.info(f"Loaded existing configuration from {config_path}")
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON in {config_path}, creating backup: {e}")
                    self._backup_config_file(config_path)
                    existing_config = {}
            
            # Get the MCP servers key for this editor
            editor_config = self.SUPPORTED_EDITORS[editor]
            mcp_key = editor_config['mcp_key']
            
            # Ensure MCP servers section exists
            if mcp_key not in existing_config:
                existing_config[mcp_key] = {}
            
            # Merge new MCP configuration, preserving existing servers
            for server_name, server_config in mcp_config.items():
                if server_name in existing_config[mcp_key]:
                    logger.info(f"Updating existing MCP server: {server_name}")
                else:
                    logger.info(f"Adding new MCP server: {server_name}")
                
                existing_config[mcp_key][server_name] = server_config
            
            # Write updated configuration
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(existing_config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully updated configuration at {config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update IDE config: {str(e)}")
            return False
    
    def _find_vibe_context_server(self, project_path: Path) -> Optional[Path]:
        """
        Find the VibeContext MCP server build in the project structure.
        
        Args:
            project_path: Starting project path
            
        Returns:
            Optional[Path]: Path to the built MCP server or None
        """
        # Common paths to check for the VibeContext server
        possible_paths = [
            # Direct project structure
            project_path / "ts_mcp_server" / "ts_mcp_server" / "build" / "index.js",
            project_path / "ts_mcp_server" / "build" / "index.js",
            
            # Parent directory structure
            project_path.parent / "ts_mcp_server" / "ts_mcp_server" / "build" / "index.js",
            project_path.parent / "ts_mcp_server" / "build" / "index.js",
            
            # Sibling directory structure
            project_path.parent / "VibeContext" / "ts_mcp_server" / "ts_mcp_server" / "build" / "index.js",
            project_path.parent / "VibeContext" / "ts_mcp_server" / "build" / "index.js",
        ]
        
        for path in possible_paths:
            if path.exists() and path.is_file():
                logger.info(f"Found VibeContext server at: {path}")
                return path
        
        logger.info("VibeContext server not found locally, will use npm package")
        return None
    
    def _backup_config_file(self, config_path: Path) -> None:
        """Create a backup of the configuration file."""
        try:
            backup_path = config_path.with_suffix(f"{config_path.suffix}.backup")
            backup_path.write_text(config_path.read_text(encoding='utf-8'), encoding='utf-8')
            logger.info(f"Created backup at {backup_path}")
        except Exception as e:
            logger.warning(f"Failed to create backup: {e}")
    
    def _add_config_guidelines(self, mcp_config: Dict[str, Any]) -> None:
        """Add configuration guidelines to the MCP config."""
        # Add metadata about VibeContext capabilities
        if "vibe_context" in mcp_config:
            mcp_config["vibe_context"]["_metadata"] = {
                "description": "VibeContext MCP Server - Provides library documentation and code analysis",
                "capabilities": [
                    "File structure analysis using Universal Ctags",
                    "Library documentation access with search",
                    "URL fetching and markdown conversion",
                    "Code snippet extraction and analysis"
                ],
                "version": "1.0.4",
                "repository": "https://github.com/AskDevAI/awesome-context"
            }
    
    def migrate_legacy_cursorrules(self, project_path: Path) -> bool:
        """
        Migrate legacy .cursorrules file to the new .cursor/rules format.
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            bool: True if migration was successful or not needed
        """
        try:
            legacy_rules_file = project_path / ".cursorrules"
            
            if legacy_rules_file.exists():
                # Read the legacy content
                legacy_content = legacy_rules_file.read_text(encoding='utf-8')
                
                # Create backup
                backup_file = project_path / ".cursorrules.backup"
                backup_file.write_text(legacy_content, encoding='utf-8')
                
                # Remove the legacy file
                legacy_rules_file.unlink()
                
                logger.info(f"Migrated legacy .cursorrules to backup at {backup_file}")
                return True
            
            return True  # No migration needed
            
        except Exception as e:
            logger.error(f"Failed to migrate legacy .cursorrules: {e}")
            return False

    def create_agents_md(self, project_path: Path, editor: str) -> bool:
        """
        Create AGENTS.md file with appropriate content for the selected IDE.
        
        Args:
            project_path: Path to the project directory
            editor: Selected IDE identifier
            
        Returns:
            bool: True if AGENTS.md was created successfully
        """
        try:
            agents_md_path = project_path / "AGENTS.md"
            
            # Get IDE info from config
            ide_info = self.get_ide_info(editor)
            ide_display_name = ide_info.get('display_name', editor.title()) if ide_info else editor.title()
            
            # Read existing content if it exists
            existing_content = ""
            if agents_md_path.exists():
                existing_content = agents_md_path.read_text(encoding='utf-8')
            
            # Generate new content
            new_content = self._generate_agents_md_content(ide_display_name, editor)
            
            # If existing content exists and doesn't contain our section, append
            if existing_content and "## VibeContext MCP Server Integration" not in existing_content:
                final_content = new_content + "\n\n---\n\n" + existing_content
            else:
                final_content = new_content
            
            # Write the file
            with open(agents_md_path, 'w', encoding='utf-8') as f:
                f.write(final_content)
            
            logger.info(f"Successfully created/updated AGENTS.md for {ide_display_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create AGENTS.md: {e}")
            return False
    
    def _generate_agents_md_content(self, ide_display_name: str, editor: str) -> str:
        """Generate AGENTS.md content for the specified IDE."""
        from datetime import datetime
        
        content = f"""# AI Agent Instructions for {ide_display_name}

*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## VibeContext MCP Server Integration

This project uses the VibeContext MCP server for enhanced documentation access and code analysis. The MCP server provides real-time library documentation, code structure analysis, and URL content fetching.

### Core MCP Tools Available

#### 1. resolve_library_id
**Purpose**: Search for libraries by name to get correct identifiers
- **Always use this first** when working with external libraries
- Returns library IDs in format: `/org/project` or `/org/project/version`
- Example: `resolve_library_id("fastapi")` → `"/fastapi/fastapi"`

#### 2. get_library_docs
**Purpose**: Get specific documentation for libraries
- **Requires library ID** from resolve_library_id tool
- Provide specific, detailed questions for better results
- Returns code examples, API documentation, and usage patterns
- Example: `get_library_docs("/fastapi/fastapi", "How to create a REST API with authentication?")`

#### 3. fetch_doc_url
**Purpose**: Fetch and convert documentation from URLs
- Converts HTML content to clean markdown format
- Useful for official documentation pages and GitHub README files
- Automatically handles GitHub blob URLs by converting to raw format
- Example: `fetch_doc_url("https://docs.python.org/3/library/pathlib.html")`

#### 4. file_structure
**Purpose**: Analyze code structure using Universal Ctags
- Provides hierarchical YAML tree of symbols, functions, and classes
- Shows line ranges and method signatures
- Supports multiple languages: Python, JavaScript, TypeScript, Go, Java, etc.
- Example: `file_structure("/path/to/file.py")`

### Usage Workflow

1. **Library Research**: Start with `resolve_library_id` to find exact library identifiers
2. **Documentation Access**: Use `get_library_docs` with specific questions
3. **Additional Context**: Supplement with `fetch_doc_url` for official docs
4. **Code Analysis**: Use `file_structure` to understand existing codebases

### Best Practices

- **Prefer MCP server data** over general knowledge for accuracy and currency
- **Use specific questions** rather than generic requests when calling get_library_docs
- **Combine multiple tools** for comprehensive understanding
- **Reference official documentation** via fetch_doc_url when available
- **Always verify library IDs** using resolve_library_id before documentation requests

### {ide_display_name}-Specific Guidelines

"""
        
        # Add IDE-specific content based on the editor
        if editor == 'cursor':
            content += """#### Cursor Integration
- MCP server is configured in `.cursor/mcp.json`
- Use `@vibe_context` to reference MCP tools in conversations
- Leverage Cursor's AI features alongside VibeContext documentation
- Rules and instructions are maintained in this AGENTS.md file

#### Cursor Workflow
1. Use VibeContext tools to research libraries and APIs
2. Apply findings directly in Cursor's AI-assisted coding
3. Reference fetched documentation when asking Cursor for help
4. Use file_structure analysis before making architectural changes"""

        elif editor in ['claude_code', 'claude code']:
            content += """#### Claude Code Integration
- Configure MCP servers using: `claude mcp add`
- VibeContext server is available as HTTP/SSE remote connection
- Use MCP tools directly in Claude Code conversations
- Instructions are maintained in CLAUDE.md for Claude-specific usage

#### Claude Code Workflow
1. Start conversations by using VibeContext tools for context
2. Leverage Claude Code's advanced reasoning with fresh documentation
3. Use file_structure for comprehensive codebase understanding
4. Cross-reference official docs via fetch_doc_url"""

        elif editor == 'vscode':
            content += """#### VS Code Integration
- MCP server configured in workspace/user settings.json
- Use compatible AI extensions that support MCP protocol
- VibeContext tools available through MCP-enabled extensions
- Instructions centralized in this AGENTS.md file

#### VS Code Workflow
1. Configure MCP-compatible AI extensions
2. Use VibeContext tools through extension interfaces
3. Reference fetched docs in AI-assisted development
4. Maintain consistency with workspace settings"""

        elif editor == 'windsurf':
            content += """#### Windsurf Integration
- MCP server configured in `~/.codeium/windsurf/mcp_config.json`
- Rules may also be defined in `.windsurfrules` (TOML format)
- VibeContext tools available in Windsurf AI conversations
- Instructions maintained in both AGENTS.md and WINDSURF.md (if exists)

#### Windsurf Workflow
1. Use VibeContext tools for library research
2. Apply insights in Windsurf's AI-powered development environment
3. Leverage both local and remote documentation sources
4. Cross-reference with official documentation"""

        else:
            content += f"""#### {ide_display_name} Integration
- MCP server configuration varies by IDE implementation
- VibeContext tools available through MCP protocol support
- Check IDE documentation for MCP server configuration
- Instructions centralized in this AGENTS.md file

#### General Workflow
1. Ensure MCP server is properly configured in your IDE
2. Use VibeContext tools for enhanced documentation access
3. Apply fresh documentation insights in development
4. Reference official sources through fetch_doc_url"""

        content += """

### Environment Variables

- `ASKBUDI_API_KEY`: Required for VibeContext service access
- `PLATFORM`: Set appropriately for your development environment

### Troubleshooting

1. **MCP Connection Issues**: Verify API key is set correctly
2. **Tool Not Available**: Check MCP server configuration in IDE settings  
3. **Outdated Information**: Use fetch_doc_url for latest official documentation
4. **Performance**: Library documentation is cached for faster responses

### Integration Notes

- MCP server provides both local and remote documentation access
- Cached responses improve performance for repeated queries
- Cross-reference multiple sources for comprehensive understanding
- Keep instructions updated as project evolves"""

        return content

    def create_cursor_rules(self, project_path: Path) -> bool:
        """
        Create proper Cursor rules in .cursor/rules/ directory according to official documentation.
        
        Uses MDC format with proper metadata structure for rule types:
        - Always: Always included in model context (alwaysApply: true)
        - Auto Attached: Included when files matching globs are referenced
        - Agent Requested: Available to AI with description
        - Manual: Only included when explicitly mentioned using @ruleName
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            bool: True if rules were created successfully
        """
        try:
            # Create .cursor/rules directory
            rules_dir = project_path / ".cursor" / "rules"
            rules_dir.mkdir(parents=True, exist_ok=True)
            
            # Create the main VibeContext MCP rule file (Always type)
            self._create_main_vibe_context_rule(rules_dir)
            
            # Create Python-specific rule (Auto Attached type)
            self._create_python_specific_rule(rules_dir)
            
            # Create project-specific rule (Agent Requested type)
            self._create_project_specific_rule(rules_dir)
            
            logger.info(f"Successfully created Cursor rules in {rules_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Cursor rules: {e}")
            return False
    
    def _create_main_vibe_context_rule(self, rules_dir: Path) -> None:
        """Create the main VibeContext MCP rule (Always type)."""
        rule_file = rules_dir / "vibe_context_mcp.mdc"
        
        # Updated rule content following official MDC format
        rule_content = """---
description: VibeContext MCP Server integration and usage guidelines for enhanced documentation access
globs:
alwaysApply: true
---

# VibeContext MCP Server Integration

This project uses the VibeContext MCP server for enhanced documentation access and code analysis. The MCP server provides real-time library documentation, code structure analysis, and URL content fetching.

## Core MCP Tools Available

### 1. resolve_library_id
**Purpose**: Search for libraries by name to get correct identifiers
- **Always use this first** when working with external libraries
- Returns library IDs in format: `/org/project` or `/org/project/version`
- Example: `resolve_library_id("fastapi")` → `"/fastapi/fastapi"`

### 2. get_library_docs
**Purpose**: Get specific documentation for libraries
- **Requires library ID** from resolve_library_id tool
- Provide specific, detailed questions for better results
- Returns code examples, API documentation, and usage patterns
- Example: `get_library_docs("/fastapi/fastapi", "How to create a REST API with authentication?")`

### 3. fetch_doc_url
**Purpose**: Fetch and convert documentation from URLs
- Converts HTML content to clean markdown format
- Useful for official documentation pages and GitHub README files
- Automatically handles GitHub blob URLs by converting to raw format
- Example: `fetch_doc_url("https://docs.python.org/3/library/pathlib.html")`

### 4. file_structure
**Purpose**: Analyze code structure using Universal Ctags
- Provides hierarchical YAML tree of symbols, functions, and classes
- Shows line ranges and method signatures
- Supports multiple languages: Python, JavaScript, TypeScript, Go, Java, etc.
- Example: `file_structure("/path/to/file.py")`

## Usage Workflow

1. **Library Research**: Start with `resolve_library_id` to find exact library identifiers
2. **Documentation Access**: Use `get_library_docs` with specific questions
3. **Additional Context**: Supplement with `fetch_doc_url` for official docs
4. **Code Analysis**: Use `file_structure` to understand existing codebases

## Best Practices

- **Prefer MCP server data** over general knowledge for accuracy and currency
- **Use specific questions** rather than generic requests when calling get_library_docs
- **Combine multiple tools** for comprehensive understanding
- **Reference official documentation** via fetch_doc_url when available
- **Always verify library IDs** using resolve_library_id before documentation requests

## Configuration

MCP server configuration is managed automatically in `.cursor/mcp.json` with the following structure:

```json
{
  "mcpServers": {
    "vibe_context": {
      "command": "npx",
      "args": ["-y", "askbudi-context@latest"],
      "env": {
        "ASKBUDI_API_KEY": "your-api-key-here",
        "PLATFORM": "claude"
      }
    }
  }
}
```

## Environment Variables

- `ASKBUDI_API_KEY`: Required for VibeContext service access
- `PLATFORM`: Set to "claude" for optimal integration"""
        
        with open(rule_file, 'w', encoding='utf-8') as f:
            f.write(rule_content)
    
    def _create_python_specific_rule(self, rules_dir: Path) -> None:
        """Create Python-specific VibeContext rule (Auto Attached type)."""
        rule_file = rules_dir / "python_vibe_context.mdc"
        
        rule_content = """---
description: Python-specific VibeContext MCP usage patterns and best practices
globs:
  - "**/*.py"
  - "**/requirements.txt"
  - "**/pyproject.toml"
  - "**/setup.py"
alwaysApply: false
---

# Python Development with VibeContext MCP

When working with Python files, leverage the VibeContext MCP server for enhanced library documentation and code analysis.

## Python-Specific Usage Patterns

### Popular Python Libraries
Use these common library identifiers with get_library_docs:
- FastAPI: `/fastapi/fastapi`
- Django: `/django/django`
- Flask: `/pallets/flask`
- Pandas: `/pandas-dev/pandas`
- NumPy: `/numpy/numpy`
- Requests: `/psf/requests`
- SQLAlchemy: `/sqlalchemy/sqlalchemy`

### Python Code Analysis
When analyzing Python codebases:
1. Use `file_structure` to understand class hierarchies and method signatures
2. Focus on `__init__.py` files to understand package structure
3. Analyze imports to identify external dependencies

### Dependency Management
For Python dependency files:
- Use `fetch_doc_url` for PyPI package documentation
- Analyze `requirements.txt` and `pyproject.toml` for version compatibility
- Research security updates and best practices for dependencies

### Example Queries
- "How to implement async/await with FastAPI?"
- "What are the best practices for SQLAlchemy relationship definitions?"
- "How to handle environment variables in Django applications?"
- "What are the pandas performance optimization techniques?"

## Python Development Workflow

1. **Library Discovery**: `resolve_library_id("library-name")`
2. **API Documentation**: `get_library_docs("/org/project", "specific question")`
3. **Code Structure**: `file_structure("path/to/python/file.py")`
4. **Official Docs**: `fetch_doc_url("https://docs.python.org/...")`"""
        
        with open(rule_file, 'w', encoding='utf-8') as f:
            f.write(rule_content)
    
    def _create_project_specific_rule(self, rules_dir: Path) -> None:
        """Create project-specific rule (Agent Requested type)."""
        rule_file = rules_dir / "project_context.mdc"
        
        rule_content = """---
description: Project-specific context and VibeContext MCP integration guidelines for this codebase
globs:
alwaysApply: false
---

# Project Context and MCP Integration

This rule provides project-specific context and guidelines for using VibeContext MCP server effectively within this codebase.

## Project Structure Analysis

When exploring this project, use `file_structure` on key files to understand:
- Main application entry points
- Configuration file structures  
- Core business logic organization
- Testing patterns and utilities

## Library Dependencies

This project may include specific dependencies that benefit from MCP documentation:
- Check `requirements.txt`, `pyproject.toml`, or `package.json` for dependencies
- Use `resolve_library_id` followed by `get_library_docs` for unfamiliar libraries
- Focus on version-specific documentation when available

## Development Patterns

### Configuration Files
- Use `fetch_doc_url` for configuration schema documentation
- Analyze existing config patterns in the codebase
- Cross-reference with official documentation for best practices

### Testing Strategies
- Examine test file patterns using `file_structure`
- Research testing library documentation via MCP tools
- Understand mocking and fixture patterns

### Documentation Maintenance
- Use `fetch_doc_url` to stay current with library changes
- Verify code examples against latest documentation
- Update inline comments with current best practices

## Recommended MCP Queries for This Project

1. **Architecture Understanding**:
   - "What are the architectural patterns for [specific framework]?"
   - "How to structure [language] projects for maintainability?"

2. **Library Usage**:
   - "What are the latest API changes in [library version]?"
   - "How to migrate from [old version] to [new version]?"

3. **Performance Optimization**:
   - "What are the performance best practices for [technology]?"
   - "How to profile and optimize [specific operation]?"

## Integration Notes

- MCP server configuration is maintained in `.cursor/mcp.json`
- Environment variables are managed through project configuration
- Library documentation is cached for improved response times
- Cross-reference MCP responses with existing code patterns"""
        
        with open(rule_file, 'w', encoding='utf-8') as f:
            f.write(rule_content)
    
    def list_installed_servers(self, editor: str, project_path: Optional[Path] = None) -> List[Dict[str, Any]]:
        """
        List currently installed MCP servers for an editor.
        
        Args:
            editor: Editor identifier
            project_path: Project directory path (if required)
            
        Returns:
            List of installed MCP server configurations
        """
        try:
            config_path = self.get_mcp_config_path(editor, project_path)
            
            if not config_path.exists():
                return []
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            supported_editors = self.get_supported_editors()
            editor_config = supported_editors[editor]
            mcp_key = editor_config['mcp_key']
            
            servers = config.get(mcp_key, {})
            
            return [
                {
                    'name': name,
                    'command': server.get('command', ''),
                    'args': server.get('args', []),
                    'env_vars': list(server.get('env', {}).keys())
                }
                for name, server in servers.items()
            ]
            
        except Exception as e:
            logger.error(f"Failed to list installed servers: {e}")
            return []
    
    def remove_mcp_server(self, editor: str, server_name: str, project_path: Optional[Path] = None) -> bool:
        """
        Remove an MCP server from the configuration.
        
        Args:
            editor: Editor identifier
            server_name: Name of the MCP server to remove
            project_path: Project directory path (if required)
            
        Returns:
            bool: True if removal was successful
        """
        try:
            config_path = self.get_mcp_config_path(editor, project_path)
            
            if not config_path.exists():
                logger.warning(f"Configuration file not found: {config_path}")
                return False
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            supported_editors = self.get_supported_editors()
            editor_config = supported_editors[editor]
            mcp_key = editor_config['mcp_key']
            
            if mcp_key not in config or server_name not in config[mcp_key]:
                logger.warning(f"MCP server '{server_name}' not found in configuration")
                return False
            
            # Remove the server
            del config[mcp_key][server_name]
            
            # Write updated configuration
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully removed MCP server '{server_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove MCP server: {e}")
            return False
    
    def validate_api_key(self, api_key: str) -> Tuple[bool, str]:
        """
        Validate the provided API key format.
        
        Args:
            api_key: API key to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not api_key or not isinstance(api_key, str):
            return False, "API key is required and must be a string"
        
        api_key = api_key.strip()
        
        if len(api_key) < 10:
            return False, "API key appears to be too short"
        
        if not api_key.replace('_', '').replace('-', '').isalnum():
            return False, "API key contains invalid characters"
        
        # Check for common VibeContext API key patterns
        if api_key.startswith('vibe_') and len(api_key) > 60:
            return True, "Valid VibeContext API key format"
        
        return True, "API key format appears valid"
    
    def get_installation_status(self, editor: str, project_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Get the current installation status for an editor.
        
        Args:
            editor: Editor identifier
            project_path: Project directory path (if required)
            
        Returns:
            Dict containing installation status information
        """
        try:
            config_path = self.get_mcp_config_path(editor, project_path)
            
            status = {
                'editor': self.SUPPORTED_EDITORS[editor]['name'],
                'config_path': str(config_path),
                'config_exists': config_path.exists(),
                'vibe_context_installed': False,
                'total_servers': 0,
                'servers': []
            }
            
            if config_path.exists():
                installed_servers = self.list_installed_servers(editor, project_path)
                status['total_servers'] = len(installed_servers)
                status['servers'] = installed_servers
                
                # Check if VibeContext is installed
                status['vibe_context_installed'] = any(
                    server['name'] == 'vibe_context' for server in installed_servers
                )
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get installation status: {e}")
            return {
                'editor': editor,
                'error': str(e),
                'config_exists': False,
                'vibe_context_installed': False,
                'total_servers': 0,
                'servers': []
            }
    
    def get_ide_info(self, editor: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific IDE.
        
        Args:
            editor: Editor identifier
            
        Returns:
            Dict containing IDE information or None if not found
        """
        config = self._load_ide_config()
        
        if not config or 'ides' not in config or editor not in config['ides']:
            return None
        
        return config['ides'][editor]
    
    def is_platform_supported(self, editor: str, platform: Optional[str] = None) -> bool:
        """Check if an IDE is supported on the current or specified platform.
        
        Args:
            editor: Editor identifier
            platform: Platform to check (defaults to current platform)
            
        Returns:
            bool: True if platform is supported
        """
        if platform is None:
            platform = self.system
            
        # Normalize platform names
        platform_mapping = {
            'darwin': 'macos',
            'linux': 'linux', 
            'windows': 'windows',
            'win32': 'windows'
        }
        
        normalized_platform = platform_mapping.get(platform.lower(), platform.lower())
        
        ide_info = self.get_ide_info(editor)
        if not ide_info:
            return False
            
        supported_platforms = ide_info.get('platform_support', [])
        return normalized_platform in supported_platforms or len(supported_platforms) == 0
    
    def get_installation_instructions(self, editor: str) -> Optional[str]:
        """Get installation instructions for a specific IDE.
        
        Args:
            editor: Editor identifier
            
        Returns:
            Installation instructions or None if not found
        """
        ide_info = self.get_ide_info(editor)
        if not ide_info:
            return None
            
        return ide_info.get('installation_method', 'No installation instructions available')
    
    def supports_one_click_install(self, editor: str) -> bool:
        """Check if an IDE supports one-click installation.
        
        Args:
            editor: Editor identifier
            
        Returns:
            bool: True if one-click install is supported
        """
        ide_info = self.get_ide_info(editor)
        if not ide_info:
            return False
            
        return ide_info.get('one_click_install', False)
    
    def get_connection_types(self, editor: str) -> List[str]:
        """Get supported connection types for an IDE.
        
        Args:
            editor: Editor identifier
            
        Returns:
            List of supported connection types
        """
        ide_info = self.get_ide_info(editor)
        if not ide_info:
            return ['local_npm']  # Default fallback
            
        return ide_info.get('connection_types', ['local_npm'])


# Convenience functions for easy usage
def install_vibe_context_for_editor(editor: str, project_path: Path, api_key: str = None) -> bool:
    """
    Convenience function to install VibeContext MCP server for a specific editor.
    
    Args:
        editor: Editor identifier (claude_code, cursor, windsurf, vscode)
        project_path: Path to the project directory
        api_key: Optional API key for VibeContext service. If not provided,
                will use APIKeyManager to find valid key or skip installation.
        
    Returns:
        bool: True if installation was successful
    """
    installer = MCPInstaller(project_dir=project_path)
    return installer.install_mcp_servers(editor, project_path, api_key)


def get_supported_editors() -> List[str]:
    """Get a list of supported editor identifiers."""
    return list(MCPInstaller.SUPPORTED_EDITORS.keys())


def get_editor_display_names() -> Dict[str, str]:
    """Get a mapping of editor identifiers to display names."""
    return {
        editor_id: config['name']
        for editor_id, config in MCPInstaller.SUPPORTED_EDITORS.items()
    }


if __name__ == "__main__":
    # Example usage
    installer = MCPInstaller()
    
    # Test API key validation
    valid, message = installer.validate_api_key("vibe_test_key_1234567890abcdef")
    print(f"API Key Validation: {valid} - {message}")
    
    # Test configuration path generation
    try:
        config_path = installer.get_mcp_config_path("claude_code")
        print(f"Claude Code config path: {config_path}")
    except Exception as e:
        print(f"Error: {e}")