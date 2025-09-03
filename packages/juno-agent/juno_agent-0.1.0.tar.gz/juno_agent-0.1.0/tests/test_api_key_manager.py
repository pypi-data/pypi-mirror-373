"""Tests for APIKeyManager class."""

import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import pytest
import httpx

from juno_agent.fancy_ui.setup.api_key_manager import (
    APIKeyManager,
    APIKeyValidationError,
    APIKeyNotFoundError,
)


# Test fixtures for API key manager testing
@pytest.fixture
def temp_home_dir(tmp_path):
    """Create a temporary home directory for testing."""
    return tmp_path / "home"


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


@pytest.fixture
def mock_global_config_dir(temp_home_dir):
    """Mock the global config directory."""
    global_config_dir = temp_home_dir / ".askbudi"
    global_config_dir.mkdir(parents=True, exist_ok=True)
    return global_config_dir


@pytest.fixture
def mock_project_config_dir(temp_project_dir):
    """Mock the project config directory."""
    project_config_dir = temp_project_dir / ".askbudi"
    project_config_dir.mkdir(parents=True, exist_ok=True)
    return project_config_dir


@pytest.fixture
def mock_env_file_dir(temp_home_dir):
    """Mock the .ASKBUDI directory for .env file."""
    env_file_dir = temp_home_dir / ".ASKBUDI"
    env_file_dir.mkdir(parents=True, exist_ok=True)
    return env_file_dir


class TestAPIKeyManager:
    """Test cases for APIKeyManager class."""

    def test_init(self, temp_home_dir, temp_project_dir):
        """Test APIKeyManager initialization."""
        temp_home_dir.mkdir(parents=True, exist_ok=True)
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        
        manager = APIKeyManager(
            home_dir=temp_home_dir,
            project_dir=temp_project_dir
        )
        assert manager.home_dir == temp_home_dir
        assert manager.project_dir == temp_project_dir
        assert manager.global_config_path == temp_home_dir / ".askbudi" / "global_config.json"
        assert manager.project_config_path == temp_project_dir / ".askbudi" / "config.json"

    def test_get_askbudi_api_key_from_env(self, mock_env_vars, temp_home_dir, temp_project_dir):
        """Test getting API key from environment variable."""
        temp_home_dir.mkdir(parents=True, exist_ok=True)
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        mock_env_vars(ASKBUDI_API_KEY="env-test-key-123")
        
        manager = APIKeyManager(home_dir=temp_home_dir, project_dir=temp_project_dir)
        api_key = manager.get_askbudi_api_key()
        
        assert api_key == "env-test-key-123"

    def test_get_askbudi_api_key_from_global_config(
        self, mock_global_config_dir, temp_project_dir
    ):
        """Test getting API key from global config file."""
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        
        global_config_path = mock_global_config_dir / "global_config.json"
        config_data = {"askbudi_api_key": "global-test-key-456"}
        
        with open(global_config_path, 'w') as f:
            json.dump(config_data, f)
        
        manager = APIKeyManager(
            home_dir=mock_global_config_dir.parent,
            project_dir=temp_project_dir
        )
        api_key = manager.get_askbudi_api_key()
        
        assert api_key == "global-test-key-456"

    def test_get_askbudi_api_key_from_project_config(
        self, temp_home_dir, mock_project_config_dir
    ):
        """Test getting API key from project config file."""
        temp_home_dir.mkdir(parents=True, exist_ok=True)
        
        project_config_path = mock_project_config_dir / "config.json"
        config_data = {"askbudi_api_key": "project-test-key-789"}
        
        with open(project_config_path, 'w') as f:
            json.dump(config_data, f)
        
        manager = APIKeyManager(
            home_dir=temp_home_dir,
            project_dir=mock_project_config_dir.parent
        )
        api_key = manager.get_askbudi_api_key()
        
        assert api_key == "project-test-key-789"

    def test_get_askbudi_api_key_priority_order(
        self, mock_env_vars, mock_global_config_dir, mock_project_config_dir
    ):
        """Test that environment variable takes priority over config files."""
        # Set up all sources
        mock_env_vars(ASKBUDI_API_KEY="env-priority-key")
        
        global_config_path = mock_global_config_dir / "global_config.json"
        with open(global_config_path, 'w') as f:
            json.dump({"askbudi_api_key": "global-priority-key"}, f)
        
        project_config_path = mock_project_config_dir / "config.json"
        with open(project_config_path, 'w') as f:
            json.dump({"askbudi_api_key": "project-priority-key"}, f)
        
        manager = APIKeyManager(
            home_dir=mock_global_config_dir.parent,
            project_dir=mock_project_config_dir.parent
        )
        api_key = manager.get_askbudi_api_key()
        
        # Environment should take priority
        assert api_key == "env-priority-key"

    def test_get_askbudi_api_key_not_found(self, temp_home_dir, temp_project_dir):
        """Test when API key is not found anywhere."""
        temp_home_dir.mkdir(parents=True, exist_ok=True)
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        
        manager = APIKeyManager(home_dir=temp_home_dir, project_dir=temp_project_dir)
        api_key = manager.get_askbudi_api_key()
        
        assert api_key is None

    @pytest.mark.asyncio
    async def test_validate_api_key_valid(self, temp_home_dir, temp_project_dir):
        """Test validating a valid API key."""
        temp_home_dir.mkdir(parents=True, exist_ok=True)
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        
        manager = APIKeyManager(home_dir=temp_home_dir, project_dir=temp_project_dir)
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = mock_client_class.return_value.__aenter__.return_value
            mock_response = Mock()
            mock_response.status_code = 200
            mock_client.get.return_value = mock_response
            
            is_valid = await manager.validate_api_key("valid-key-123")
            
            assert is_valid is True
            mock_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_api_key_invalid(self, temp_home_dir, temp_project_dir):
        """Test validating an invalid API key."""
        temp_home_dir.mkdir(parents=True, exist_ok=True)
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        
        manager = APIKeyManager(home_dir=temp_home_dir, project_dir=temp_project_dir)
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = mock_client_class.return_value.__aenter__.return_value
            mock_response = Mock()
            mock_response.status_code = 401
            mock_client.get.return_value = mock_response
            
            is_valid = await manager.validate_api_key("invalid-key-123")
            
            assert is_valid is False

    @pytest.mark.asyncio
    async def test_validate_api_key_connection_error(self, temp_home_dir, temp_project_dir):
        """Test handling connection errors during validation."""
        temp_home_dir.mkdir(parents=True, exist_ok=True)
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        
        manager = APIKeyManager(home_dir=temp_home_dir, project_dir=temp_project_dir)
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = mock_client_class.return_value.__aenter__.return_value
            mock_client.get.side_effect = httpx.RequestError("Connection failed")
            
            is_valid = await manager.validate_api_key("test-key")
            
            assert is_valid is False

    def test_save_api_key_global(self, mock_global_config_dir, temp_project_dir):
        """Test saving API key to global config."""
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        
        manager = APIKeyManager(
            home_dir=mock_global_config_dir.parent,
            project_dir=temp_project_dir
        )
        
        manager.save_api_key("new-global-key", global_save=True)
        
        global_config_path = mock_global_config_dir / "global_config.json"
        assert global_config_path.exists()
        
        with open(global_config_path) as f:
            config = json.load(f)
        
        assert config["askbudi_api_key"] == "new-global-key"

    def test_save_api_key_project(self, temp_home_dir, mock_project_config_dir):
        """Test saving API key to project config."""
        temp_home_dir.mkdir(parents=True, exist_ok=True)
        
        manager = APIKeyManager(
            home_dir=temp_home_dir,
            project_dir=mock_project_config_dir.parent
        )
        
        manager.save_api_key("new-project-key", global_save=False)
        
        project_config_path = mock_project_config_dir / "config.json"
        assert project_config_path.exists()
        
        with open(project_config_path) as f:
            config = json.load(f)
        
        assert config["askbudi_api_key"] == "new-project-key"

    def test_has_valid_api_key_true(self, mock_env_vars, temp_home_dir, temp_project_dir):
        """Test has_valid_api_key returns True when key exists."""
        temp_home_dir.mkdir(parents=True, exist_ok=True)
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        mock_env_vars(ASKBUDI_API_KEY="existing-key")
        
        manager = APIKeyManager(home_dir=temp_home_dir, project_dir=temp_project_dir)
        
        assert manager.has_valid_api_key() is True

    def test_has_valid_api_key_false(self, temp_home_dir, temp_project_dir):
        """Test has_valid_api_key returns False when no key exists."""
        temp_home_dir.mkdir(parents=True, exist_ok=True)
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        
        manager = APIKeyManager(home_dir=temp_home_dir, project_dir=temp_project_dir)
        
        assert manager.has_valid_api_key() is False

    def test_get_value_proposition_message(self, temp_home_dir, temp_project_dir):
        """Test getting the value proposition message."""
        temp_home_dir.mkdir(parents=True, exist_ok=True)
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        
        manager = APIKeyManager(home_dir=temp_home_dir, project_dir=temp_project_dir)
        
        message = manager.get_value_proposition_message()
        
        assert isinstance(message, str)
        assert "VibeContext" in message
        assert "enhanced" in message.lower()
        assert len(message) > 50  # Should be a substantial message

    def test_load_from_env_file_exists(self, mock_env_file_dir, temp_project_dir):
        """Test loading API key from .env file."""
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        
        env_file_path = mock_env_file_dir / ".env"
        env_file_path.write_text("ASKBUDI_API_KEY=env-file-key-123\nOTHER_VAR=value")
        
        manager = APIKeyManager(
            home_dir=mock_env_file_dir.parent,
            project_dir=temp_project_dir
        )
        
        key = manager._load_from_env_file()
        assert key == "env-file-key-123"

    def test_load_from_env_file_with_quotes(self, mock_env_file_dir, temp_project_dir):
        """Test loading API key from .env file with quotes."""
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        
        env_file_path = mock_env_file_dir / ".env"
        env_file_path.write_text('ASKBUDI_API_KEY="quoted-key-456"\nOTHER_VAR=value')
        
        manager = APIKeyManager(
            home_dir=mock_env_file_dir.parent,
            project_dir=temp_project_dir
        )
        
        key = manager._load_from_env_file()
        assert key == "quoted-key-456"

    def test_load_from_env_file_single_quotes(self, mock_env_file_dir, temp_project_dir):
        """Test loading API key from .env file with single quotes."""
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        
        env_file_path = mock_env_file_dir / ".env"
        env_file_path.write_text("ASKBUDI_API_KEY='single-quoted-key'\nOTHER_VAR=value")
        
        manager = APIKeyManager(
            home_dir=mock_env_file_dir.parent,
            project_dir=temp_project_dir
        )
        
        key = manager._load_from_env_file()
        assert key == "single-quoted-key"

    def test_load_from_env_file_not_exists(self, temp_home_dir, temp_project_dir):
        """Test loading from non-existent .env file."""
        temp_home_dir.mkdir(parents=True, exist_ok=True)
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        
        manager = APIKeyManager(home_dir=temp_home_dir, project_dir=temp_project_dir)
        
        key = manager._load_from_env_file()
        assert key is None

    def test_load_from_env_file_empty(self, mock_env_file_dir, temp_project_dir):
        """Test loading from empty .env file."""
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        
        env_file_path = mock_env_file_dir / ".env"
        env_file_path.write_text("")
        
        manager = APIKeyManager(
            home_dir=mock_env_file_dir.parent,
            project_dir=temp_project_dir
        )
        
        key = manager._load_from_env_file()
        assert key is None

    def test_load_from_env_file_no_key(self, mock_env_file_dir, temp_project_dir):
        """Test loading from .env file without ASKBUDI_API_KEY."""
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        
        env_file_path = mock_env_file_dir / ".env"
        env_file_path.write_text("OTHER_VAR=value\nANOTHER_VAR=another")
        
        manager = APIKeyManager(
            home_dir=mock_env_file_dir.parent,
            project_dir=temp_project_dir
        )
        
        key = manager._load_from_env_file()
        assert key is None

    def test_save_to_env_file_new(self, temp_home_dir, temp_project_dir):
        """Test saving API key to new .env file."""
        temp_home_dir.mkdir(parents=True, exist_ok=True)
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        
        manager = APIKeyManager(home_dir=temp_home_dir, project_dir=temp_project_dir)
        
        manager._save_to_env_file("new-env-key-789")
        
        env_file_path = temp_home_dir / ".ASKBUDI" / ".env"
        assert env_file_path.exists()
        
        content = env_file_path.read_text()
        assert "ASKBUDI_API_KEY=new-env-key-789" in content

    def test_save_to_env_file_update_existing(self, mock_env_file_dir, temp_project_dir):
        """Test updating existing .env file with new API key."""
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        
        env_file_path = mock_env_file_dir / ".env"
        env_file_path.write_text("OTHER_VAR=value\nASKBUDI_API_KEY=old-key\nANOTHER_VAR=another")
        
        manager = APIKeyManager(
            home_dir=mock_env_file_dir.parent,
            project_dir=temp_project_dir
        )
        
        manager._save_to_env_file("updated-key-999")
        
        content = env_file_path.read_text()
        assert "ASKBUDI_API_KEY=updated-key-999" in content
        assert "OTHER_VAR=value" in content
        assert "ANOTHER_VAR=another" in content
        assert "old-key" not in content

    def test_save_to_env_file_idempotent(self, mock_env_file_dir, temp_project_dir):
        """Test that saving the same key twice doesn't change the file unnecessarily."""
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        
        env_file_path = mock_env_file_dir / ".env"
        env_file_path.write_text("ASKBUDI_API_KEY=same-key-123")
        
        manager = APIKeyManager(
            home_dir=mock_env_file_dir.parent,
            project_dir=temp_project_dir
        )
        
        # Get initial modification time
        initial_mtime = env_file_path.stat().st_mtime
        
        # Save the same key
        manager._save_to_env_file("same-key-123")
        
        # File should not have been modified
        assert env_file_path.stat().st_mtime == initial_mtime

    def test_get_askbudi_api_key_env_file_priority(
        self, mock_env_file_dir, mock_global_config_dir, mock_project_config_dir
    ):
        """Test that .env file takes priority over config files but not environment variable."""
        # Set up .env file
        env_file_path = mock_env_file_dir / ".env"
        env_file_path.write_text("ASKBUDI_API_KEY=env-file-priority-key")
        
        # Set up global config
        global_config_path = mock_global_config_dir / "global_config.json"
        with open(global_config_path, 'w') as f:
            json.dump({"askbudi_api_key": "global-priority-key"}, f)
        
        # Set up project config
        project_config_path = mock_project_config_dir / "config.json"
        with open(project_config_path, 'w') as f:
            json.dump({"askbudi_api_key": "project-priority-key"}, f)
        
        manager = APIKeyManager(
            home_dir=mock_env_file_dir.parent,
            project_dir=mock_project_config_dir.parent
        )
        api_key = manager.get_askbudi_api_key()
        
        # .env file should take priority over configs
        assert api_key == "env-file-priority-key"

    def test_get_askbudi_api_key_auto_saves_env_var(
        self, mock_env_vars, temp_home_dir, temp_project_dir
    ):
        """Test that environment variable is auto-saved to .env file."""
        temp_home_dir.mkdir(parents=True, exist_ok=True)
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        mock_env_vars(ASKBUDI_API_KEY="env-var-auto-save-key")
        
        manager = APIKeyManager(home_dir=temp_home_dir, project_dir=temp_project_dir)
        api_key = manager.get_askbudi_api_key()
        
        # Should return the environment variable
        assert api_key == "env-var-auto-save-key"
        
        # Should also save to .env file
        env_file_path = temp_home_dir / ".ASKBUDI" / ".env"
        assert env_file_path.exists()
        
        content = env_file_path.read_text()
        assert "ASKBUDI_API_KEY=env-var-auto-save-key" in content

    def test_save_api_key_also_saves_to_env_file(self, temp_home_dir, temp_project_dir):
        """Test that save_api_key also saves to .env file."""
        temp_home_dir.mkdir(parents=True, exist_ok=True)
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        
        manager = APIKeyManager(home_dir=temp_home_dir, project_dir=temp_project_dir)
        
        manager.save_api_key("save-to-both-key", global_save=True)
        
        # Should save to global config
        global_config_path = temp_home_dir / ".askbudi" / "global_config.json"
        assert global_config_path.exists()
        
        with open(global_config_path) as f:
            config = json.load(f)
        assert config["askbudi_api_key"] == "save-to-both-key"
        
        # Should also save to .env file
        env_file_path = temp_home_dir / ".ASKBUDI" / ".env"
        assert env_file_path.exists()
        
        content = env_file_path.read_text()
        assert "ASKBUDI_API_KEY=save-to-both-key" in content

    def test_ensure_askbudi_directory_creates_directory(self, temp_home_dir, temp_project_dir):
        """Test that _ensure_askbudi_directory creates the directory."""
        temp_home_dir.mkdir(parents=True, exist_ok=True)
        temp_project_dir.mkdir(parents=True, exist_ok=True)
        
        manager = APIKeyManager(home_dir=temp_home_dir, project_dir=temp_project_dir)
        
        # Directory should not exist initially
        askbudi_dir = temp_home_dir / ".ASKBUDI"
        assert not askbudi_dir.exists()
        
        # Create it
        manager._ensure_askbudi_directory()
        
        # Directory should now exist
        assert askbudi_dir.exists()
        assert askbudi_dir.is_dir()