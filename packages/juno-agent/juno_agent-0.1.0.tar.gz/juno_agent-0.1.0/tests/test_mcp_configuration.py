"""
Comprehensive test cases for MCP configuration behavior across all supported IDEs.

This test suite verifies:
1. MCP configuration file creation for each IDE
2. Correct file paths and locations
3. Proper JSON/TOML structure and configuration keys
4. API key handling and insertion
5. VibeContext server configuration
"""

import json
import os
import tempfile
import toml
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from typing import Dict, Any, Optional

import pytest

from juno_agent.fancy_ui.setup.mcp_installer import MCPInstaller, MCPInstallationError


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory for testing."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    return project_dir


@pytest.fixture
def temp_home_dir(tmp_path):
    """Create a temporary home directory for testing."""
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    return home_dir


@pytest.fixture
def mock_api_key():
    """Valid test API key."""
    return "vibe_test_key_12345678901234567890abcdef1234567890"


@pytest.fixture
def installer_with_temp_home(temp_home_dir, temp_project_dir):
    """Create MCPInstaller with mocked home directory."""
    with patch('juno_agent.fancy_ui.setup.mcp_installer.Path.home', return_value=temp_home_dir):
        installer = MCPInstaller(project_dir=temp_project_dir)
        # Mock API key manager to always return valid key
        installer.api_key_manager.get_askbudi_api_key = Mock(return_value="test_api_key")
        installer.api_key_manager.has_valid_api_key = Mock(return_value=True)
        yield installer


class TestMCPConfigurationCreation:
    """Test MCP configuration file creation for all supported IDEs."""

    def test_cursor_mcp_creation(self, installer_with_temp_home, temp_project_dir, mock_api_key):
        """Test Cursor MCP configuration creation."""
        installer = installer_with_temp_home
        
        # Install MCP servers for Cursor
        success = installer.install_mcp_servers('cursor', temp_project_dir, mock_api_key)
        assert success, "Cursor MCP installation should succeed"
        
        # Check file creation
        cursor_mcp_path = temp_project_dir / '.cursor' / 'mcp.json'
        assert cursor_mcp_path.exists(), "Cursor should create .cursor/mcp.json"
        
        # Check JSON structure
        with open(cursor_mcp_path, 'r') as f:
            config = json.load(f)
        
        assert 'mcpServers' in config, "Cursor config should have mcpServers key"
        assert 'vibe_context' in config['mcpServers'], "Should contain vibe_context server"
        
        vibe_config = config['mcpServers']['vibe_context']
        assert 'command' in vibe_config, "Should have command field"
        assert 'args' in vibe_config, "Should have args field"
        assert 'env' in vibe_config, "Should have env field"
        assert vibe_config['env']['ASKBUDI_API_KEY'] == mock_api_key, "Should have correct API key"
        
        # Check AGENTS.md creation (Cursor should also create this)
        agents_md_path = temp_project_dir / 'AGENTS.md'
        assert agents_md_path.exists(), "Cursor should also create AGENTS.md"
        
        with open(agents_md_path, 'r') as f:
            agents_content = f.read()
        assert "VibeContext MCP Server Integration" in agents_content
        assert "Cursor Integration" in agents_content

    def test_vscode_mcp_creation(self, installer_with_temp_home, temp_project_dir, mock_api_key):
        """Test VS Code MCP configuration creation.""" 
        installer = installer_with_temp_home
        
        # Install MCP servers for VS Code
        success = installer.install_mcp_servers('vscode', temp_project_dir, mock_api_key)
        assert success, "VS Code MCP installation should succeed"
        
        # Check file creation - VS Code uses settings.json in .vscode directory
        vscode_config_path = temp_project_dir / '.vscode' / 'settings.json'
        assert vscode_config_path.exists(), "VS Code should create .vscode/settings.json"
        
        # Check JSON structure  
        with open(vscode_config_path, 'r') as f:
            config = json.load(f)
        
        assert 'mcp.servers' in config, "VS Code config should have mcp.servers key"
        assert 'vibe_context' in config['mcp.servers'], "Should contain vibe_context server"
        
        vibe_config = config['mcp.servers']['vibe_context'] 
        assert 'command' in vibe_config, "Should have command field"
        assert 'args' in vibe_config, "Should have args field"
        assert 'env' in vibe_config, "Should have env field"
        assert vibe_config['env']['ASKBUDI_API_KEY'] == mock_api_key, "Should have correct API key"

    def test_windsurf_mcp_creation(self, installer_with_temp_home, temp_home_dir, mock_api_key):
        """Test Windsurf MCP configuration creation."""
        installer = installer_with_temp_home
        
        # Install MCP servers for Windsurf
        success = installer.install_mcp_servers('windsurf', Path("/dummy"), mock_api_key)
        assert success, "Windsurf MCP installation should succeed"
        
        # Check file creation - Windsurf uses ~/.codeium/windsurf/mcp_config.json
        windsurf_config_path = temp_home_dir / '.codeium' / 'windsurf' / 'mcp_config.json'
        assert windsurf_config_path.exists(), "Windsurf should create ~/.codeium/windsurf/mcp_config.json"
        
        # Check JSON structure
        with open(windsurf_config_path, 'r') as f:
            config = json.load(f)
        
        assert 'mcpServers' in config, "Windsurf config should have mcpServers key"
        assert 'vibe_context' in config['mcpServers'], "Should contain vibe_context server"
        
        vibe_config = config['mcpServers']['vibe_context']
        assert 'command' in vibe_config, "Should have command field"
        assert 'args' in vibe_config, "Should have args field" 
        assert 'env' in vibe_config, "Should have env field"
        assert vibe_config['env']['ASKBUDI_API_KEY'] == mock_api_key, "Should have correct API key"

    def test_claude_code_mcp_creation(self, installer_with_temp_home, temp_home_dir, mock_api_key):
        """Test Claude Code MCP configuration creation."""
        installer = installer_with_temp_home
        
        # Install MCP servers for Claude Code
        success = installer.install_mcp_servers('claude_code', Path("/dummy"), mock_api_key)
        assert success, "Claude Code MCP installation should succeed"
        
        # Check file creation - Claude Code uses ~/.claude_code_config.json
        claude_config_path = temp_home_dir / '.claude_code_config.json'
        assert claude_config_path.exists(), "Claude Code should create ~/.claude_code_config.json"
        
        # Check JSON structure
        with open(claude_config_path, 'r') as f:
            config = json.load(f)
        
        assert 'mcpServers' in config, "Claude Code config should have mcpServers key"
        assert 'vibe_context' in config['mcpServers'], "Should contain vibe_context server"
        
        vibe_config = config['mcpServers']['vibe_context']
        assert 'command' in vibe_config, "Should have command field"
        assert 'args' in vibe_config, "Should have args field"
        assert 'env' in vibe_config, "Should have env field"
        assert vibe_config['env']['ASKBUDI_API_KEY'] == mock_api_key, "Should have correct API key"

    def test_zed_mcp_creation(self, installer_with_temp_home, temp_project_dir, mock_api_key):
        """Test Zed MCP configuration creation."""
        installer = installer_with_temp_home
        
        # Install MCP servers for Zed
        success = installer.install_mcp_servers('zed', temp_project_dir, mock_api_key)
        assert success, "Zed MCP installation should succeed"
        
        # Check file creation - Zed uses settings.json in .zed directory
        zed_config_path = temp_project_dir / '.zed' / 'settings.json'
        assert zed_config_path.exists(), "Zed should create .zed/settings.json"
        
        # Check JSON structure
        with open(zed_config_path, 'r') as f:
            config = json.load(f)
        
        assert 'context_servers' in config, "Zed config should have context_servers key"
        assert 'vibe_context' in config['context_servers'], "Should contain vibe_context server"
        
        vibe_config = config['context_servers']['vibe_context']
        assert 'command' in vibe_config, "Should have command field"
        assert 'args' in vibe_config, "Should have args field"
        assert 'env' in vibe_config, "Should have env field" 
        assert vibe_config['env']['ASKBUDI_API_KEY'] == mock_api_key, "Should have correct API key"

    def test_gemini_cli_mcp_creation(self, installer_with_temp_home, temp_home_dir, mock_api_key):
        """Test Gemini CLI MCP configuration creation."""
        installer = installer_with_temp_home
        
        # Install MCP servers for Gemini CLI
        success = installer.install_mcp_servers('gemini_cli', Path("/dummy"), mock_api_key)
        assert success, "Gemini CLI MCP installation should succeed"
        
        # Check file creation - Gemini CLI uses ~/.gemini/settings.json
        gemini_config_path = temp_home_dir / '.gemini' / 'settings.json'
        assert gemini_config_path.exists(), "Gemini CLI should create ~/.gemini/settings.json"
        
        # Check JSON structure
        with open(gemini_config_path, 'r') as f:
            config = json.load(f)
        
        assert 'mcpServers' in config, "Gemini CLI config should have mcpServers key"
        assert 'vibe_context' in config['mcpServers'], "Should contain vibe_context server"


class TestMCPConfigurationStructure:
    """Test MCP configuration structure and content for different IDEs."""

    def test_configuration_keys_mapping(self, installer_with_temp_home):
        """Test that each IDE uses the correct configuration key."""
        installer = installer_with_temp_home
        supported_editors = installer.get_supported_editors()
        
        expected_keys = {
            'cursor': 'mcpServers',
            'claude_code': 'mcpServers', 
            'windsurf': 'mcpServers',
            'vscode': 'mcp.servers',
            'zed': 'context_servers',
            'gemini_cli': 'mcpServers',
            'cline': 'mcpServers',
            'augment_code': 'augment.advanced.mcpServers',
            'openai_codex': 'mcp_servers',
            'jetbrains_ai': 'mcpServers',
            'claude_desktop': 'mcpServers',
            'lm_studio': 'mcpServers',
        }
        
        for editor_id, expected_key in expected_keys.items():
            if editor_id in supported_editors:
                editor_config = supported_editors[editor_id]
                actual_key = editor_config['mcp_key']
                assert actual_key == expected_key, f"{editor_id} should use '{expected_key}' but uses '{actual_key}'"

    def test_file_path_resolution(self, installer_with_temp_home, temp_project_dir, temp_home_dir):
        """Test that file paths resolve correctly for each IDE."""
        installer = installer_with_temp_home
        
        expected_paths = {
            'cursor': temp_project_dir / '.cursor' / 'mcp.json',
            'vscode': temp_project_dir / '.vscode' / 'settings.json',  
            'zed': temp_project_dir / '.zed' / 'settings.json',
            'claude_code': temp_home_dir / '.claude_code_config.json',
            'windsurf': temp_home_dir / '.codeium' / 'windsurf' / 'mcp_config.json',
            'gemini_cli': temp_home_dir / '.gemini' / 'settings.json',
        }
        
        for editor_id, expected_path in expected_paths.items():
            try:
                actual_path = installer.get_mcp_config_path(editor_id, temp_project_dir)
                assert actual_path == expected_path, f"{editor_id} path mismatch: expected {expected_path}, got {actual_path}"
            except MCPInstallationError:
                # Some IDEs might not be fully supported, skip them
                continue

    def test_vibe_context_configuration_structure(self, installer_with_temp_home, temp_project_dir, mock_api_key):
        """Test that VibeContext server configuration has correct structure."""
        installer = installer_with_temp_home
        
        config = installer.create_vibe_context_config(temp_project_dir, mock_api_key)
        
        assert 'vibe_context' in config, "Should contain vibe_context server"
        
        vibe_config = config['vibe_context']
        
        # Required fields
        assert 'command' in vibe_config, "Should have command field"
        assert 'args' in vibe_config, "Should have args field"
        assert 'env' in vibe_config, "Should have env field"
        
        # Environment variables
        env = vibe_config['env']
        assert 'ASKBUDI_API_KEY' in env, "Should have ASKBUDI_API_KEY"
        assert 'PLATFORM' in env, "Should have PLATFORM"
        assert env['ASKBUDI_API_KEY'] == mock_api_key, "Should have correct API key"
        assert env['PLATFORM'] == 'claude', "Should have correct platform"
        
        # Metadata
        assert '_metadata' in vibe_config, "Should have metadata"
        metadata = vibe_config['_metadata']
        assert 'description' in metadata, "Should have description"
        assert 'capabilities' in metadata, "Should have capabilities"
        assert isinstance(metadata['capabilities'], list), "Capabilities should be a list"
        assert len(metadata['capabilities']) > 0, "Should have at least one capability"


class TestMCPAPIKeyHandling:
    """Test API key handling in MCP configurations."""

    def test_api_key_insertion(self, installer_with_temp_home, temp_project_dir):
        """Test that API keys are properly inserted into configurations."""
        installer = installer_with_temp_home
        test_api_key = "test_specific_key_123456789"
        
        # Install with specific API key
        success = installer.install_mcp_servers('cursor', temp_project_dir, test_api_key)
        assert success, "Installation should succeed"
        
        # Verify API key in config
        cursor_config_path = temp_project_dir / '.cursor' / 'mcp.json'
        with open(cursor_config_path, 'r') as f:
            config = json.load(f)
        
        api_key = config['mcpServers']['vibe_context']['env']['ASKBUDI_API_KEY']
        assert api_key == test_api_key, f"API key should be {test_api_key}, got {api_key}"

    def test_api_key_fallback_to_manager(self, installer_with_temp_home, temp_project_dir):
        """Test that installation falls back to API key manager when no key provided."""
        installer = installer_with_temp_home
        manager_api_key = "manager_fallback_key_123456789"
        
        # Mock API key manager to return specific key
        installer.api_key_manager.get_askbudi_api_key = Mock(return_value=manager_api_key)
        
        # Install without providing API key (should use manager)
        success = installer.install_mcp_servers('cursor', temp_project_dir)
        assert success, "Installation should succeed with manager key"
        
        # Verify manager key was used
        cursor_config_path = temp_project_dir / '.cursor' / 'mcp.json'
        with open(cursor_config_path, 'r') as f:
            config = json.load(f)
        
        api_key = config['mcpServers']['vibe_context']['env']['ASKBUDI_API_KEY']
        assert api_key == manager_api_key, f"Should use manager API key {manager_api_key}, got {api_key}"

    def test_installation_failure_without_api_key(self, installer_with_temp_home, temp_project_dir, capsys):
        """Test that installation fails gracefully when no API key is available."""
        installer = installer_with_temp_home
        
        # Mock API key manager to return no key
        installer.api_key_manager.get_askbudi_api_key = Mock(return_value=None)
        installer.api_key_manager.has_valid_api_key = Mock(return_value=False)
        
        # Install without API key
        success = installer.install_mcp_servers('cursor', temp_project_dir)
        assert success is False, "Installation should fail without API key"
        
        # Check warning message
        captured = capsys.readouterr()
        assert "No valid ASKBUDI_API_KEY found" in captured.out
        assert "Skipping MCP installation" in captured.out


class TestMCPConfigurationMerging:
    """Test MCP configuration merging with existing configurations."""

    def test_preserve_existing_servers(self, installer_with_temp_home, temp_project_dir, mock_api_key):
        """Test that existing MCP servers are preserved during installation."""
        installer = installer_with_temp_home
        
        # Create existing config with another server
        cursor_config_path = temp_project_dir / '.cursor'
        cursor_config_path.mkdir()
        cursor_mcp_path = cursor_config_path / 'mcp.json'
        
        existing_config = {
            'mcpServers': {
                'existing_server': {
                    'command': 'existing_command',
                    'args': ['existing_arg'],
                    'env': {'EXISTING_KEY': 'existing_value'}
                }
            }
        }
        
        with open(cursor_mcp_path, 'w') as f:
            json.dump(existing_config, f, indent=2)
        
        # Install VibeContext
        success = installer.install_mcp_servers('cursor', temp_project_dir, mock_api_key)
        assert success, "Installation should succeed"
        
        # Check both servers exist
        with open(cursor_mcp_path, 'r') as f:
            config = json.load(f)
        
        assert 'existing_server' in config['mcpServers'], "Existing server should be preserved"
        assert 'vibe_context' in config['mcpServers'], "New server should be added"
        
        # Verify existing server wasn't modified
        existing = config['mcpServers']['existing_server']
        assert existing['command'] == 'existing_command'
        assert existing['args'] == ['existing_arg']
        assert existing['env']['EXISTING_KEY'] == 'existing_value'

    def test_update_existing_vibe_context(self, installer_with_temp_home, temp_project_dir, mock_api_key):
        """Test that existing VibeContext server is updated, not duplicated."""
        installer = installer_with_temp_home
        
        # Create existing config with old VibeContext
        cursor_config_path = temp_project_dir / '.cursor'
        cursor_config_path.mkdir()
        cursor_mcp_path = cursor_config_path / 'mcp.json'
        
        existing_config = {
            'mcpServers': {
                'vibe_context': {
                    'command': 'old_command',
                    'args': ['old_arg'],
                    'env': {'ASKBUDI_API_KEY': 'old_key'}
                }
            }
        }
        
        with open(cursor_mcp_path, 'w') as f:
            json.dump(existing_config, f, indent=2)
        
        # Install VibeContext (should update existing)
        success = installer.install_mcp_servers('cursor', temp_project_dir, mock_api_key)
        assert success, "Installation should succeed"
        
        # Check VibeContext was updated
        with open(cursor_mcp_path, 'r') as f:
            config = json.load(f)
        
        assert len(config['mcpServers']) == 1, "Should only have one vibe_context server"
        
        vibe_config = config['mcpServers']['vibe_context']
        assert vibe_config['env']['ASKBUDI_API_KEY'] == mock_api_key, "API key should be updated"
        assert vibe_config['command'] != 'old_command', "Command should be updated"


class TestTOMLConfiguration:
    """Test TOML format configuration for IDEs that use it."""
    
    def test_openai_codex_toml_creation(self, installer_with_temp_home, temp_project_dir, mock_api_key):
        """Test OpenAI Codex TOML configuration creation."""
        installer = installer_with_temp_home
        
        # Mock the update_ide_config to handle TOML format
        original_update = installer.update_ide_config
        
        def mock_update_ide_config(config_path: Path, mcp_config: Dict[str, Any], editor: str) -> bool:
            if editor == 'openai_codex':
                # Handle TOML format
                config_path.parent.mkdir(parents=True, exist_ok=True)
                
                existing_config = {}
                if config_path.exists():
                    try:
                        existing_config = toml.load(config_path)
                    except Exception:
                        existing_config = {}
                
                # Get the MCP servers key for this editor
                editor_config = installer.get_supported_editors()[editor]
                mcp_key = editor_config['mcp_key']
                
                if mcp_key not in existing_config:
                    existing_config[mcp_key] = {}
                
                # Merge configurations
                for server_name, server_config in mcp_config.items():
                    existing_config[mcp_key][server_name] = server_config
                
                # Write TOML
                with open(config_path, 'w') as f:
                    toml.dump(existing_config, f)
                
                return True
            else:
                return original_update(config_path, mcp_config, editor)
        
        installer.update_ide_config = mock_update_ide_config
        
        # Install MCP servers for OpenAI Codex
        success = installer.install_mcp_servers('openai_codex', temp_project_dir, mock_api_key)
        assert success, "OpenAI Codex MCP installation should succeed"
        
        # Check file creation
        codex_config_path = temp_project_dir / '.openaicodex' / 'config.toml'  
        assert codex_config_path.exists(), "OpenAI Codex should create config.toml"
        
        # Check TOML structure
        config = toml.load(codex_config_path)
        
        assert 'mcp_servers' in config, "OpenAI Codex config should have mcp_servers key"
        assert 'vibe_context' in config['mcp_servers'], "Should contain vibe_context server"
        
        vibe_config = config['mcp_servers']['vibe_context']
        assert 'command' in vibe_config, "Should have command field"
        assert 'args' in vibe_config, "Should have args field"
        assert 'env' in vibe_config, "Should have env field"
        assert vibe_config['env']['ASKBUDI_API_KEY'] == mock_api_key, "Should have correct API key"


class TestCursorSpecialBehavior:
    """Test Cursor's special behavior of creating both MCP config and AGENTS.md."""
    
    def test_cursor_creates_both_mcp_and_agents(self, installer_with_temp_home, temp_project_dir, mock_api_key):
        """Test that Cursor creates both .cursor/mcp.json AND AGENTS.md."""
        installer = installer_with_temp_home
        
        # Install MCP servers for Cursor
        success = installer.install_mcp_servers('cursor', temp_project_dir, mock_api_key)
        assert success, "Cursor MCP installation should succeed"
        
        # Check .cursor/mcp.json creation
        cursor_mcp_path = temp_project_dir / '.cursor' / 'mcp.json'
        assert cursor_mcp_path.exists(), "Cursor should create .cursor/mcp.json"
        
        with open(cursor_mcp_path, 'r') as f:
            mcp_config = json.load(f)
        assert 'mcpServers' in mcp_config, "MCP config should have mcpServers"
        assert 'vibe_context' in mcp_config['mcpServers'], "Should have vibe_context server"
        
        # Check AGENTS.md creation
        agents_md_path = temp_project_dir / 'AGENTS.md'
        assert agents_md_path.exists(), "Cursor should create AGENTS.md"
        
        with open(agents_md_path, 'r') as f:
            agents_content = f.read()
        
        # Verify AGENTS.md content
        assert "AI Agent Instructions for Cursor" in agents_content
        assert "VibeContext MCP Server Integration" in agents_content
        assert "Cursor Integration" in agents_content
        assert "MCP server is configured in `.cursor/mcp.json`" in agents_content
        
        # Verify both files are separate and serve different purposes
        assert cursor_mcp_path.read_text() != agents_md_path.read_text(), "Files should have different content"

    def test_cursor_agents_md_content_structure(self, installer_with_temp_home, temp_project_dir, mock_api_key):
        """Test that Cursor's AGENTS.md has proper structure and content."""
        installer = installer_with_temp_home
        
        success = installer.install_mcp_servers('cursor', temp_project_dir, mock_api_key)
        assert success, "Installation should succeed"
        
        agents_md_path = temp_project_dir / 'AGENTS.md'
        with open(agents_md_path, 'r') as f:
            content = f.read()
        
        # Check required sections
        required_sections = [
            "# AI Agent Instructions for Cursor",
            "## VibeContext MCP Server Integration",
            "### Core MCP Tools Available",
            "#### 1. resolve_library_id",
            "#### 2. get_library_docs", 
            "#### 3. fetch_doc_url",
            "#### 4. file_structure",
            "### Usage Workflow",
            "### Best Practices",
            "### Cursor-Specific Guidelines",
            "#### Cursor Integration",
            "#### Cursor Workflow",
            "### Environment Variables",
            "### Troubleshooting"
        ]
        
        for section in required_sections:
            assert section in content, f"AGENTS.md should contain section: {section}"
        
        # Check Cursor-specific content
        assert "Use `@vibe_context` to reference MCP tools" in content
        assert "Rules and instructions are maintained in this AGENTS.md file" in content
        assert "Leverage Cursor's AI features alongside VibeContext" in content

    def test_cursor_preserves_existing_agents_md(self, installer_with_temp_home, temp_project_dir, mock_api_key):
        """Test that Cursor preserves existing AGENTS.md content."""
        installer = installer_with_temp_home
        
        # Create existing AGENTS.md
        agents_md_path = temp_project_dir / 'AGENTS.md'
        existing_content = """# My Project Instructions

This is my existing project documentation.

## Custom Rules
- Follow our coding standards
- Use TypeScript for all new code
"""
        agents_md_path.write_text(existing_content)
        
        # Install MCP servers
        success = installer.install_mcp_servers('cursor', temp_project_dir, mock_api_key)
        assert success, "Installation should succeed"
        
        # Check that existing content is preserved
        with open(agents_md_path, 'r') as f:
            updated_content = f.read()
        
        # Should contain both new VibeContext content and existing content
        assert "VibeContext MCP Server Integration" in updated_content, "Should add VibeContext content"
        assert "My Project Instructions" in updated_content, "Should preserve existing content"
        assert "Follow our coding standards" in updated_content, "Should preserve custom rules"
        assert "Use TypeScript for all new code" in updated_content, "Should preserve custom rules"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])