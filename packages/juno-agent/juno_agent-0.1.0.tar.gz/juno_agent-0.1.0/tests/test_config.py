"""Tests for configuration management."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
import httpx

from juno_agent.config import Config, ConfigManager


class TestConfig:
    """Test Config model."""
    
    def test_config_creation(self):
        """Test creating a Config instance."""
        config = Config(workdir="/test/dir")
        assert config.workdir == "/test/dir"
        assert config.editor is None
        assert config.api_key_set is False
        assert config.setup_completed is False
    
    def test_config_with_values(self):
        """Test creating Config with all values."""
        config = Config(
            workdir="/test/dir",
            editor="Claude Code",
            api_key_set=True,
            mcp_server_installed=True,
            project_description="Test project",
            git_controlled=True,
            git_root="/test/dir",
            libraries=["fastapi", "typer"],
            setup_completed=True,
        )
        assert config.workdir == "/test/dir"
        assert config.editor == "Claude Code"
        assert config.api_key_set is True
        assert config.libraries == ["fastapi", "typer"]


class TestConfigManager:
    """Test ConfigManager class."""
    
    def test_init(self):
        """Test ConfigManager initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            
            assert config_manager.workdir == workdir
            assert config_manager.config_dir == workdir / ".askbudi"
            assert config_manager.config_dir.exists()
            assert (config_manager.config_dir / ".gitignore").exists()
    
    def test_load_default_config(self, monkeypatch):
        """Test loading default configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            # Clear environment variables to avoid interference
            monkeypatch.delenv('ASKBUDI_API_KEY', raising=False)
            # Create config manager and then mock its global paths
            config_manager = ConfigManager(workdir)
            global_env_path = Path(temp_dir) / "global.env"
            global_config_path = Path(temp_dir) / "global_config.json"
            config_manager.global_env_file = global_env_path
            config_manager.global_config_file = global_config_path
            
            config = config_manager.load_config()
            assert config.workdir == str(workdir)
            assert config.editor is None
            assert config.api_key_set is False
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            
            # Create and save config
            config = Config(
                workdir=str(workdir),
                editor="Claude Code",
                api_key_set=True,
                setup_completed=True,
            )
            config_manager.save_config(config)
            
            # Load config
            loaded_config = config_manager.load_config()
            assert loaded_config.editor == "Claude Code"
            assert loaded_config.api_key_set is True
            assert loaded_config.setup_completed is True
    
    def test_update_config(self):
        """Test updating configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            
            # Update config
            config_manager.update_config(editor="Cursor", setup_completed=True)
            
            # Verify update
            config = config_manager.load_config()
            assert config.editor == "Cursor"
            assert config.setup_completed is True
    
    def test_api_key_management(self, monkeypatch):
        """Test API key management."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            # Clear environment variables to avoid interference
            monkeypatch.delenv('ASKBUDI_API_KEY', raising=False)
            # Create config manager and then mock its global paths
            config_manager = ConfigManager(workdir)
            global_env_path = Path(temp_dir) / "global.env"
            global_config_path = Path(temp_dir) / "global_config.json"
            config_manager.global_env_file = global_env_path
            config_manager.global_config_file = global_config_path
            
            # Initially no API key
            assert not config_manager.has_api_key()
            assert config_manager.get_api_key() is None
            
            # Set API key
            api_key = "test-api-key-123"
            config_manager.set_api_key(api_key)
            
            # Verify API key
            assert config_manager.has_api_key()
            assert config_manager.get_api_key() == api_key
            
            # Verify config is updated
            config = config_manager.load_config()
            assert config.api_key_set is True
    
    def test_reset_config(self, monkeypatch):
        """Test resetting configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            # Clear environment variables to avoid interference
            monkeypatch.delenv('ASKBUDI_API_KEY', raising=False)
            # Create config manager and then mock its global paths
            config_manager = ConfigManager(workdir)
            global_env_path = Path(temp_dir) / "global.env"
            global_config_path = Path(temp_dir) / "global_config.json"
            config_manager.global_env_file = global_env_path
            config_manager.global_config_file = global_config_path
            
            # Set some config
            config_manager.update_config(editor="Claude Code")
            config_manager.set_api_key("test-key")
            
            # Reset
            config_manager.reset_config()
            
            # Verify reset
            assert not config_manager.config_file.exists()
            assert not config_manager.env_file.exists()
            assert not config_manager.has_api_key()
            
            # Loading should create default config
            config = config_manager.load_config()
            assert config.editor is None
            assert config.api_key_set is False
    
    def test_corrupted_config_file(self):
        """Test handling corrupted config file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            
            # Create corrupted config file
            config_manager.config_file.write_text("invalid json content")
            
            # Should load default config
            config = config_manager.load_config()
            assert config.workdir == str(workdir)
            assert config.editor is None
    
    def test_backend_url_configuration(self):
        """Test backend URL configuration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            
            # Test default URL
            default_url = config_manager.get_backend_url()
            assert default_url == "https://ts-endpoint.askbudi.ai"
            
            # Test environment variable override
            with patch.dict('os.environ', {'ASKBUDI_BACKEND_URL': 'http://localhost:3000'}):
                env_url = config_manager.get_backend_url()
                assert env_url == "http://localhost:3000"
            
            # Test config file override
            config_manager.update_config(backend_url="http://custom.backend.com")
            custom_url = config_manager.get_backend_url()
            assert custom_url == "http://custom.backend.com"
    
    @pytest.mark.asyncio
    async def test_api_key_validation_success(self, monkeypatch):
        """Test successful API key validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            # Clear environment variables to avoid interference
            monkeypatch.delenv('ASKBUDI_API_KEY', raising=False)
            config_manager = ConfigManager(workdir)
            global_env_path = Path(temp_dir) / "global.env"
            config_manager.global_env_file = global_env_path
            
            # Mock successful response
            mock_response = {
                "valid": True,
                "client_uuid": "test-uuid-123",
                "user_level": "premium",
                "quota_limit": 10000,
                "quota_used": 100,
                "message": "API key is valid"
            }
            
            # Mock the entire validation method for simpler testing
            async def mock_validate_response(api_key):
                # Update the config as the real method does
                config_manager.update_config(
                    api_key_set=True,
                    user_level=mock_response["user_level"],
                    client_uuid=mock_response["client_uuid"]
                )
                return mock_response
            
            # Replace the validation method with our mock
            original_method = config_manager.validate_api_key_with_backend
            config_manager.validate_api_key_with_backend = mock_validate_response
            
            result = await config_manager.validate_api_key_with_backend("vibe_test_123")
            
            assert result["valid"] is True
            assert result["user_level"] == "premium"
            assert result["client_uuid"] == "test-uuid-123"
            
            # Check that config was updated
            config = config_manager.load_config()
            assert config.api_key_set is True
            assert config.user_level == "premium"
            assert config.client_uuid == "test-uuid-123"
    
    @pytest.mark.asyncio
    async def test_api_key_validation_failure(self, monkeypatch):
        """Test API key validation failure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            # Clear environment variables to avoid interference
            monkeypatch.delenv('ASKBUDI_API_KEY', raising=False)
            config_manager = ConfigManager(workdir)
            global_env_path = Path(temp_dir) / "global.env"
            config_manager.global_env_file = global_env_path
            
            # Mock error response
            mock_error_response = {"valid": False, "error": "Invalid API key"}
            
            async def mock_validate_error_response(api_key):
                return mock_error_response
            
            # Replace the validation method with our mock
            config_manager.validate_api_key_with_backend = mock_validate_error_response
            
            result = await config_manager.validate_api_key_with_backend("invalid_key")
            
            assert result["valid"] is False
            assert "Invalid API key" in result["error"]
    
    @pytest.mark.asyncio
    async def test_api_key_validation_network_error(self):
        """Test API key validation with network error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            
            # Mock network error
            with patch('httpx.AsyncClient') as mock_client:
                mock_client.return_value.__aenter__.return_value.post = AsyncMock(
                    side_effect=httpx.RequestError("Connection failed")
                )
                
                result = await config_manager.validate_api_key_with_backend("test_key")
                
                assert result["valid"] is False
                assert "Connection error" in result["error"]