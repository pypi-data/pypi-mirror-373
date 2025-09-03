"""Tests for MCP installer API key integration."""

import json
import os
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

from juno_agent.fancy_ui.setup.mcp_installer import MCPInstaller


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory for testing."""
    return tmp_path / "project"


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing."""
    # Always clear ASKBUDI_API_KEY first
    monkeypatch.delenv("ASKBUDI_API_KEY", raising=False)
    
    def _mock_env(**kwargs):
        for key, value in kwargs.items():
            if value is None:
                monkeypatch.delenv(key, raising=False)
            else:
                monkeypatch.setenv(key, value)
    return _mock_env


@pytest.fixture(autouse=True)
def clean_env_vars(monkeypatch):
    """Clean environment variables before each test."""
    monkeypatch.delenv("ASKBUDI_API_KEY", raising=False)


class TestMCPInstallerAPIKeys:
    """Test cases for MCP installer API key functionality."""

    def test_init_with_api_key_manager(self, temp_project_dir):
        """Test MCPInstaller initialization includes API key manager."""
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        installer = MCPInstaller(project_dir=temp_project_dir)
        
        assert installer.api_key_manager is not None
        assert installer.api_key_manager.project_dir == temp_project_dir

    def test_should_install_mcp_with_key(self, mock_env_vars, temp_project_dir):
        """Test should_install_mcp returns True when API key exists."""
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        mock_env_vars(ASKBUDI_API_KEY="test-key")
        
        installer = MCPInstaller(project_dir=temp_project_dir)
        should_install = installer.should_install_mcp()
        
        assert should_install is True

    def test_should_install_mcp_without_key(self, temp_project_dir):
        """Test should_install_mcp returns False when no API key."""
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        installer = MCPInstaller(project_dir=temp_project_dir)
        should_install = installer.should_install_mcp()
        
        assert should_install is False

    def test_get_api_key_status_with_env_key(self, mock_env_vars, temp_project_dir):
        """Test API key status when key is in environment."""
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        mock_env_vars(ASKBUDI_API_KEY="env-test-key")
        
        installer = MCPInstaller(project_dir=temp_project_dir)
        status = installer.get_api_key_status()
        
        assert status['has_api_key'] is True
        assert status['api_key_source'] == 'Environment variable'
        assert status['can_install_mcp'] is True

    def test_get_api_key_status_without_key(self, temp_project_dir):
        """Test API key status when no key is available."""
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        installer = MCPInstaller(project_dir=temp_project_dir)
        status = installer.get_api_key_status()
        
        assert status['has_api_key'] is False
        assert status['api_key_source'] is None
        assert status['can_install_mcp'] is False

    def test_install_mcp_servers_without_key(self, temp_project_dir, capsys):
        """Test MCP server installation fails gracefully without API key."""
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        installer = MCPInstaller(project_dir=temp_project_dir)
        
        # Mock the supported editors to avoid loading complex configuration
        with patch.object(installer, 'get_supported_editors', return_value={'cursor': {'name': 'Cursor'}}):
            success = installer.install_mcp_servers('cursor', temp_project_dir)
            
            assert success is False
            
            captured = capsys.readouterr()
            assert "No valid ASKBUDI_API_KEY found" in captured.out

    def test_install_mcp_servers_uses_api_key_manager(self, mock_env_vars, temp_project_dir):
        """Test that install_mcp_servers uses the API key manager."""
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        mock_env_vars(ASKBUDI_API_KEY="manager-test-key")
        
        installer = MCPInstaller(project_dir=temp_project_dir)
        
        # Mock the required methods to avoid complex setup
        with patch.object(installer, 'get_supported_editors', return_value={'cursor': {'name': 'Cursor'}}):
            with patch.object(installer, 'get_mcp_config_path', return_value=temp_project_dir / 'test_config.json'):
                with patch.object(installer, 'create_vibe_context_config', return_value={'test': 'config'}) as mock_create:
                    with patch.object(installer, 'update_ide_config', return_value=True):
                        success = installer.install_mcp_servers('cursor', temp_project_dir)
                        
                        # Should succeed and use the API key from manager
                        mock_create.assert_called_once()
                        # Check that the effective API key was passed
                        call_args = mock_create.call_args
                        assert call_args[0][1] == "manager-test-key"  # API key argument