"""Simple tests for conversation storage manager focusing on core functionality."""

import pytest
import tempfile
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import sys

from juno_agent.storage_manager import ConversationStorageManager


class TestConversationStorageManagerSimple:
    """Simple test suite for ConversationStorageManager core functionality."""
    
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
        assert self.storage_manager.logger is not None
        assert self.storage_manager.storage is None  # Lazy initialization
    
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
        # Should be a valid UUID format
        assert len(new_session) >= 30  # UUIDs are typically longer
    
    def test_attach_to_agent_without_tinyagent(self):
        """Test attaching storage when TinyAgent is not available."""
        mock_agent = Mock()
        
        # This should not raise an exception even if TinyAgent is not available
        self.storage_manager.attach_to_agent(mock_agent)
        
        # Storage should remain None when TinyAgent is not available
        assert self.storage_manager.storage is None
    
    def test_save_session_metadata_without_storage(self):
        """Test saving session metadata when storage is not available."""
        metadata = {"test_key": "test_value"}
        
        # This should not raise an exception
        self.storage_manager.save_session_metadata(metadata)
        
        # Should complete without error
        assert True  # If we get here, no exception was raised
    
    def test_list_sessions_empty(self):
        """Test listing sessions when no sessions exist."""
        sessions = self.storage_manager.list_sessions()
        assert sessions == []
    
    def test_load_session_without_storage(self):
        """Test loading session when storage is not available."""
        result = self.storage_manager.load_session("test-session")
        assert result is None
    
    def test_delete_session_basic(self):
        """Test basic session deletion functionality."""
        # Create database first with proper structure
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
        
        # Insert test data
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
    
    def test_get_session_summary_empty_session(self):
        """Test getting session summary when session doesn't exist."""
        # This will call load_session which returns None without storage
        summary = self.storage_manager.get_session_summary("nonexistent-session")
        assert summary == "Empty session"
    
    def test_list_sessions_with_data(self):
        """Test listing sessions with actual database data."""
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
        session = sessions[0]
        assert session["session_id"] == "test-session-1"
        assert session["created_at"] == "2023-01-01T12:00:00"
        assert session["updated_at"] == "2023-01-01T12:30:00"
        assert session["message_count"] == 1
        assert "metadata" in session
    
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
    
    def test_lazy_storage_initialization_import_error(self):
        """Test that storage remains None when TinyAgent import fails."""
        # This tests the current behavior - storage stays None when import fails
        assert self.storage_manager.storage is None
        
        # Initialize storage - should handle ImportError gracefully
        self.storage_manager._initialize_storage()
        
        # Should still be None due to ImportError
        assert self.storage_manager.storage is None