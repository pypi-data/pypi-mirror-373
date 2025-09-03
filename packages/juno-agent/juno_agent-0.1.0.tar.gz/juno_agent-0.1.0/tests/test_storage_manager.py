"""Tests for conversation storage manager."""

import pytest
import tempfile
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from juno_agent.storage_manager import ConversationStorageManager


class TestConversationStorageManager:
    """Test suite for ConversationStorageManager."""
    
    def setup_method(self):
        """Set up test environment."""
        # Create temporary directory for testing
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Mock the home directory to use our temp dir
        self.home_patcher = patch('pathlib.Path.home')
        mock_home = self.home_patcher.start()
        mock_home.return_value = self.temp_dir
        
        # Initialize storage manager
        self.storage_manager = ConversationStorageManager()
        
    def teardown_method(self):
        """Clean up test environment."""
        # Stop patches
        self.home_patcher.stop()
        
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test storage manager initialization."""
        assert self.storage_manager.storage_dir == self.temp_dir / ".askbudi"
        assert self.storage_manager.storage_dir.exists()
        assert self.storage_manager.db_path == self.temp_dir / ".askbudi" / "conversations.db"
        assert self.storage_manager.user_id is not None
        assert self.storage_manager.current_session_id is not None
    
    def test_generate_user_id(self):
        """Test user ID generation from current working directory."""
        user_id = self.storage_manager._generate_user_id()
        assert isinstance(user_id, str)
        assert len(user_id) > 0
        # User ID should not contain path separators
        assert "/" not in user_id
        assert "\\" not in user_id
    
    def test_new_session(self):
        """Test creating new sessions."""
        original_session = self.storage_manager.current_session_id
        
        # Create new session
        new_session = self.storage_manager.new_session()
        
        assert new_session != original_session
        assert self.storage_manager.current_session_id == new_session
        assert len(new_session) > 0
    
    def test_attach_to_agent_with_storage(self):
        """Test attaching storage to agent when TinyAgent is available."""
        mock_agent = Mock()
        
        # Mock the import and SqliteStorage
        mock_storage = Mock()
        with patch.dict('sys.modules', {'tinyagent': MagicMock()}):
            with patch.dict('sys.modules', {'tinyagent.storage': MagicMock()}):
                with patch.dict('sys.modules', {'tinyagent.storage.sqlite_storage': MagicMock()}):
                    with patch('tinyagent.storage.sqlite_storage.SqliteStorage', return_value=mock_storage):
                        # Initialize storage (lazy loading)
                        self.storage_manager._initialize_storage()
                        
                        # Attach to agent
                        self.storage_manager.attach_to_agent(mock_agent)
                        
                        mock_storage.attach.assert_called_once_with(mock_agent)
    
    def test_attach_to_agent_without_tinyagent(self):
        """Test attaching storage when TinyAgent is not available."""
        mock_agent = Mock()
        
        # This should not raise an exception even if TinyAgent is not available
        self.storage_manager.attach_to_agent(mock_agent)
        
        # Storage should remain None when TinyAgent is not available
        assert self.storage_manager.storage is None
    
    @patch('tinyagent.storage.sqlite_storage.SqliteStorage')
    def test_save_session_metadata(self, mock_sqlite_storage):
        """Test saving session metadata."""
        mock_storage = Mock()
        mock_sqlite_storage.return_value = mock_storage
        
        metadata = {"test_key": "test_value", "project": "test_project"}
        
        self.storage_manager.save_session_metadata(metadata)
        
        mock_sqlite_storage.assert_called_once()
        mock_storage.save_session.assert_called_once()
        
        # Check the call arguments
        call_args = mock_storage.save_session.call_args[0]
        assert call_args[0] == self.storage_manager.current_session_id
        assert call_args[2] == self.storage_manager.user_id
        
        # Check data structure
        data = call_args[1]
        assert "metadata" in data
        assert "timestamp" in data
        assert data["metadata"] == metadata
    
    def test_save_session_metadata_without_storage(self):
        """Test saving session metadata when storage is not available."""
        metadata = {"test_key": "test_value"}
        
        # This should not raise an exception
        self.storage_manager.save_session_metadata(metadata)
    
    def test_list_sessions_empty(self):
        """Test listing sessions when no sessions exist."""
        sessions = self.storage_manager.list_sessions()
        assert sessions == []
    
    def test_list_sessions_with_data(self):
        """Test listing sessions with mock database data."""
        # Create mock database with test data
        db_path = self.storage_manager.db_path
        
        # Create the database directory
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create mock database table and data
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE tny_agent_sessions (
                session_id TEXT,
                user_id TEXT,
                data TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        test_data = {
            "metadata": {"test": "data"},
            "messages": [{"role": "user", "content": "test message"}]
        }
        
        import json
        cursor.execute("""
            INSERT INTO tny_agent_sessions (session_id, user_id, data, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "test-session-1",
            self.storage_manager.user_id,
            json.dumps(test_data),  # Proper JSON format
            "2023-01-01T12:00:00",
            "2023-01-01T12:30:00"
        ))
        
        conn.commit()
        conn.close()
        
        # Test listing sessions
        sessions = self.storage_manager.list_sessions()
        
        assert len(sessions) == 1
        assert sessions[0]["session_id"] == "test-session-1"
        assert sessions[0]["created_at"] == "2023-01-01T12:00:00"
        assert sessions[0]["updated_at"] == "2023-01-01T12:30:00"
    
    @patch('tinyagent.storage.sqlite_storage.SqliteStorage')
    def test_load_session(self, mock_sqlite_storage):
        """Test loading a specific session."""
        mock_storage = Mock()
        mock_sqlite_storage.return_value = mock_storage
        
        test_data = {"messages": [{"role": "user", "content": "test"}]}
        mock_storage.load_session.return_value = test_data
        
        session_id = "test-session-id"
        result = self.storage_manager.load_session(session_id)
        
        assert result == test_data
        assert self.storage_manager.current_session_id == session_id
        mock_storage.load_session.assert_called_once_with(session_id, self.storage_manager.user_id)
    
    def test_load_session_without_storage(self):
        """Test loading session when storage is not available."""
        result = self.storage_manager.load_session("test-session")
        assert result is None
    
    def test_delete_session(self):
        """Test deleting a session."""
        # Create mock database with test data
        db_path = self.storage_manager.db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE tny_agent_sessions (
                session_id TEXT,
                user_id TEXT,
                data TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        cursor.execute("""
            INSERT INTO tny_agent_sessions (session_id, user_id, data, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            "test-session-delete",
            self.storage_manager.user_id,
            "{}",
            "2023-01-01T12:00:00",
            "2023-01-01T12:30:00"
        ))
        
        conn.commit()
        conn.close()
        
        # Test deletion
        success = self.storage_manager.delete_session("test-session-delete")
        assert success is True
        
        # Verify deletion
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM tny_agent_sessions WHERE session_id = ?
        """, ("test-session-delete",))
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 0
    
    def test_delete_nonexistent_session(self):
        """Test deleting a session that doesn't exist."""
        # Create database first so the table exists
        db_path = self.storage_manager.db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE tny_agent_sessions (
                session_id TEXT,
                user_id TEXT,
                data TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        
        success = self.storage_manager.delete_session("nonexistent-session")
        assert success is True  # Still returns True even if no rows affected
    
    @patch('tinyagent.storage.sqlite_storage.SqliteStorage')
    def test_get_session_summary_with_messages(self, mock_sqlite_storage):
        """Test getting session summary with messages."""
        mock_storage = Mock()
        mock_sqlite_storage.return_value = mock_storage
        
        test_data = {
            "messages": [
                {"role": "user", "content": "How do I create a Python function?"},
                {"role": "assistant", "content": "To create a Python function..."}
            ]
        }
        mock_storage.load_session.return_value = test_data
        
        summary = self.storage_manager.get_session_summary("test-session")
        
        assert summary == "How do I create a Python function?"
    
    @patch('tinyagent.storage.sqlite_storage.SqliteStorage')
    def test_get_session_summary_long_message(self, mock_sqlite_storage):
        """Test getting session summary with long message (should be truncated)."""
        mock_storage = Mock()
        mock_sqlite_storage.return_value = mock_storage
        
        long_message = "A" * 150  # 150 characters
        test_data = {
            "messages": [
                {"role": "user", "content": long_message},
            ]
        }
        mock_storage.load_session.return_value = test_data
        
        summary = self.storage_manager.get_session_summary("test-session")
        
        assert len(summary) == 103  # 100 chars + "..."
        assert summary.endswith("...")
    
    @patch('tinyagent.storage.sqlite_storage.SqliteStorage')
    def test_get_session_summary_no_user_messages(self, mock_sqlite_storage):
        """Test getting session summary when no user messages exist."""
        mock_storage = Mock()
        mock_sqlite_storage.return_value = mock_storage
        
        test_data = {
            "messages": [
                {"role": "assistant", "content": "Hello!"}
            ]
        }
        mock_storage.load_session.return_value = test_data
        
        summary = self.storage_manager.get_session_summary("test-session")
        
        assert summary == "No user messages"
    
    @patch('tinyagent.storage.sqlite_storage.SqliteStorage')
    def test_get_session_summary_no_messages(self, mock_sqlite_storage):
        """Test getting session summary when no messages exist."""
        mock_storage = Mock()
        mock_sqlite_storage.return_value = mock_storage
        
        test_data = {"messages": []}
        mock_storage.load_session.return_value = test_data
        
        summary = self.storage_manager.get_session_summary("test-session")
        
        assert summary == "No messages"
    
    @patch('tinyagent.storage.sqlite_storage.SqliteStorage')
    def test_get_session_summary_empty_session(self, mock_sqlite_storage):
        """Test getting session summary when session doesn't exist."""
        mock_storage = Mock()
        mock_sqlite_storage.return_value = mock_storage
        mock_storage.load_session.return_value = None
        
        summary = self.storage_manager.get_session_summary("nonexistent-session")
        
        assert summary == "Empty session"
    
    @patch('tinyagent.storage.sqlite_storage.SqliteStorage')
    def test_lazy_storage_initialization(self, mock_sqlite):
        """Test that storage is initialized only when needed."""
        # Create new manager with patched home to avoid conflicts
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = self.temp_dir
            new_manager = ConversationStorageManager()
            
            # Storage should be None initially
            assert new_manager.storage is None
            
            # Should initialize on first use
            new_manager._initialize_storage()
            mock_sqlite.assert_called_once()
    
    def test_error_handling_in_list_sessions(self):
        """Test error handling when listing sessions fails."""
        # Create invalid database to trigger error
        db_path = self.storage_manager.db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create empty file (invalid database)
        db_path.touch()
        
        sessions = self.storage_manager.list_sessions()
        assert sessions == []  # Should return empty list on error
    
    def test_error_handling_in_delete_session(self):
        """Test error handling when session deletion fails."""
        # Try to delete from nonexistent database
        success = self.storage_manager.delete_session("test-session")
        # Should return False when deletion fails due to database error
        assert success is False