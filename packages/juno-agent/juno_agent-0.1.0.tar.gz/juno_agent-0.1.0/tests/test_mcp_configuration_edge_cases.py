"""
Edge case tests for MCP configuration behavior.

This test suite covers specific edge cases and regression tests.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

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
def installer_with_temp_home(temp_home_dir, temp_project_dir):
    """Create MCPInstaller with mocked home directory."""
    with patch('juno_agent.fancy_ui.setup.mcp_installer.Path.home', return_value=temp_home_dir):
        installer = MCPInstaller(project_dir=temp_project_dir)
        # Mock API key manager to always return valid key
        installer.api_key_manager.get_askbudi_api_key = Mock(return_value="test_api_key")
        installer.api_key_manager.has_valid_api_key = Mock(return_value=True)
        yield installer


class TestComplexPathResolution:
    """Test complex path resolution cases."""
    
    def test_gemini_cli_path_resolution(self, installer_with_temp_home, temp_home_dir):
        """Test that Gemini CLI uses correct subdirectory path."""
        installer = installer_with_temp_home
        
        config_path = installer.get_mcp_config_path('gemini_cli')
        expected_path = temp_home_dir / '.gemini' / 'settings.json'
        
        assert config_path == expected_path, f"Expected {expected_path}, got {config_path}"

    def test_claude_code_path_resolution(self, installer_with_temp_home, temp_home_dir):
        """Test that Claude Code uses simple home directory path."""
        installer = installer_with_temp_home
        
        config_path = installer.get_mcp_config_path('claude_code')
        expected_path = temp_home_dir / '.claude_code_config.json'
        
        assert config_path == expected_path, f"Expected {expected_path}, got {config_path}"

    def test_windsurf_path_resolution(self, installer_with_temp_home, temp_home_dir):
        """Test that Windsurf uses correct codeium subdirectory path."""
        installer = installer_with_temp_home
        
        config_path = installer.get_mcp_config_path('windsurf')
        expected_path = temp_home_dir / '.codeium' / 'windsurf' / 'mcp_config.json'
        
        assert config_path == expected_path, f"Expected {expected_path}, got {config_path}"

    def test_project_based_path_resolution(self, installer_with_temp_home, temp_project_dir):
        """Test project-based IDEs create correct subdirectory paths."""
        installer = installer_with_temp_home
        
        test_cases = [
            ('cursor', '.cursor', 'mcp.json'),
            ('vscode', '.vscode', 'settings.json'), 
            ('zed', '.zed', 'settings.json'),
        ]
        
        for editor, expected_dir, expected_file in test_cases:
            config_path = installer.get_mcp_config_path(editor, temp_project_dir)
            expected_path = temp_project_dir / expected_dir / expected_file
            
            assert config_path == expected_path, f"{editor}: Expected {expected_path}, got {config_path}"


class TestAGENTSMDCreation:
    """Test AGENTS.md creation logic."""
    
    def test_agents_md_skipped_for_home_based_configs(self, installer_with_temp_home, temp_home_dir):
        """Test that AGENTS.md is not created for home-based configurations."""
        installer = installer_with_temp_home
        
        # Install for Gemini CLI (home-based config)
        success = installer.install_mcp_servers('gemini_cli', Path("/dummy"), "test_key")
        assert success, "Installation should succeed"
        
        # Check that AGENTS.md was not attempted to be created at dummy path
        dummy_agents_path = Path("/dummy") / "AGENTS.md"
        assert not dummy_agents_path.exists(), "AGENTS.md should not be created for home-based configs"

    def test_agents_md_created_for_project_based_configs(self, installer_with_temp_home, temp_project_dir):
        """Test that AGENTS.md is created for project-based configurations."""
        installer = installer_with_temp_home
        
        # Install for Cursor (project-based config) 
        success = installer.install_mcp_servers('cursor', temp_project_dir, "test_key")
        assert success, "Installation should succeed"
        
        # Check that AGENTS.md was created
        agents_path = temp_project_dir / "AGENTS.md"
        assert agents_path.exists(), "AGENTS.md should be created for project-based configs"

    def test_agents_md_not_created_for_claude_code(self, installer_with_temp_home, temp_project_dir):
        """Test that AGENTS.md is not created for Claude Code."""
        installer = installer_with_temp_home
        
        # Install for Claude Code
        success = installer.install_mcp_servers('claude_code', temp_project_dir, "test_key")
        assert success, "Installation should succeed"
        
        # Check that AGENTS.md was not created
        agents_path = temp_project_dir / "AGENTS.md"
        assert not agents_path.exists(), "AGENTS.md should not be created for Claude Code"


class TestConfigurationKeyMapping:
    """Test that different IDEs use the correct configuration keys."""
    
    def test_ide_specific_config_keys(self, installer_with_temp_home, temp_project_dir, temp_home_dir):
        """Test that each IDE creates configs with the correct keys."""
        installer = installer_with_temp_home
        
        test_cases = [
            ('cursor', 'mcpServers', temp_project_dir / '.cursor' / 'mcp.json'),
            ('vscode', 'mcp.servers', temp_project_dir / '.vscode' / 'settings.json'),
            ('claude_code', 'mcpServers', temp_home_dir / '.claude_code_config.json'),
            ('windsurf', 'mcpServers', temp_home_dir / '.codeium' / 'windsurf' / 'mcp_config.json'),
            ('gemini_cli', 'mcpServers', temp_home_dir / '.gemini' / 'settings.json'),
            ('zed', 'context_servers', temp_project_dir / '.zed' / 'settings.json'),
        ]
        
        for editor, expected_key, expected_path in test_cases:
            # Install MCP for this editor
            project_path = temp_project_dir if not str(expected_path).startswith(str(temp_home_dir)) else Path("/dummy")
            success = installer.install_mcp_servers(editor, project_path, "test_key")
            assert success, f"Installation should succeed for {editor}"
            
            # Check the configuration file
            assert expected_path.exists(), f"Config file should exist for {editor}: {expected_path}"
            
            with open(expected_path, 'r') as f:
                config = json.load(f)
            
            assert expected_key in config, f"{editor} should have {expected_key} key"
            assert 'vibe_context' in config[expected_key], f"{editor} should have vibe_context server"


class TestInvalidConfigurations:
    """Test handling of invalid configuration scenarios."""
    
    def test_unsupported_editor_raises_error(self, installer_with_temp_home, temp_project_dir):
        """Test that unsupported editors raise appropriate errors."""
        installer = installer_with_temp_home
        
        with pytest.raises(MCPInstallationError, match="Unsupported editor"):
            installer.install_mcp_servers('nonexistent_editor', temp_project_dir, "test_key")

    def test_missing_project_path_for_project_based_config(self, installer_with_temp_home):
        """Test that missing project path raises error for project-based configs."""
        installer = installer_with_temp_home
        
        with pytest.raises(MCPInstallationError, match="Project path required"):
            installer.get_mcp_config_path('cursor', None)

    def test_invalid_json_backup_and_recovery(self, installer_with_temp_home, temp_project_dir):
        """Test that invalid JSON files are backed up and recovered."""
        installer = installer_with_temp_home
        
        # Create invalid JSON in Cursor config
        cursor_config_dir = temp_project_dir / '.cursor'
        cursor_config_dir.mkdir()
        cursor_config_path = cursor_config_dir / 'mcp.json'
        cursor_config_path.write_text("invalid json content {")
        
        # Install should succeed by backing up invalid file
        success = installer.install_mcp_servers('cursor', temp_project_dir, "test_key")
        assert success, "Installation should succeed even with invalid existing JSON"
        
        # Check backup was created
        backup_path = cursor_config_path.with_suffix('.json.backup')
        assert backup_path.exists(), "Backup should be created for invalid JSON"
        assert "invalid json content" in backup_path.read_text(), "Backup should contain original content"
        
        # Check new config is valid
        with open(cursor_config_path, 'r') as f:
            config = json.load(f)
        assert 'mcpServers' in config, "New config should be valid JSON"


class TestServerListingAndRemoval:
    """Test server listing and removal functionality."""
    
    def test_list_servers_empty_config(self, installer_with_temp_home):
        """Test listing servers when no config exists."""
        installer = installer_with_temp_home
        
        servers = installer.list_installed_servers('claude_code')
        assert servers == [], "Should return empty list for non-existent config"

    def test_list_servers_with_multiple_servers(self, installer_with_temp_home, temp_project_dir):
        """Test listing servers when multiple servers are configured."""
        installer = installer_with_temp_home
        
        # Create config with multiple servers
        cursor_config_dir = temp_project_dir / '.cursor'
        cursor_config_dir.mkdir()
        cursor_config_path = cursor_config_dir / 'mcp.json'
        
        config = {
            'mcpServers': {
                'server1': {
                    'command': 'cmd1',
                    'args': ['arg1'],
                    'env': {'KEY1': 'value1'}
                },
                'server2': {
                    'command': 'cmd2', 
                    'args': ['arg2'],
                    'env': {'KEY2': 'value2', 'KEY3': 'value3'}
                }
            }
        }
        
        with open(cursor_config_path, 'w') as f:
            json.dump(config, f)
        
        # List servers
        servers = installer.list_installed_servers('cursor', temp_project_dir)
        assert len(servers) == 2, "Should list both servers"
        
        server_names = [s['name'] for s in servers]
        assert 'server1' in server_names, "Should include server1"
        assert 'server2' in server_names, "Should include server2"

    def test_remove_server_preserves_others(self, installer_with_temp_home, temp_project_dir):
        """Test that removing one server preserves others.""" 
        installer = installer_with_temp_home
        
        # Install initial server
        success = installer.install_mcp_servers('cursor', temp_project_dir, "test_key")
        assert success, "Installation should succeed"
        
        # Manually add another server
        cursor_config_path = temp_project_dir / '.cursor' / 'mcp.json'
        with open(cursor_config_path, 'r') as f:
            config = json.load(f)
        
        config['mcpServers']['another_server'] = {
            'command': 'another_cmd',
            'args': ['another_arg']
        }
        
        with open(cursor_config_path, 'w') as f:
            json.dump(config, f)
        
        # Remove vibe_context server
        success = installer.remove_mcp_server('cursor', 'vibe_context', temp_project_dir)
        assert success, "Removal should succeed"
        
        # Check that another_server is preserved
        with open(cursor_config_path, 'r') as f:
            updated_config = json.load(f)
        
        assert 'vibe_context' not in updated_config['mcpServers'], "vibe_context should be removed"
        assert 'another_server' in updated_config['mcpServers'], "another_server should be preserved"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])