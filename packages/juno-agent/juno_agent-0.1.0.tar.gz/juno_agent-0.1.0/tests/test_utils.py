"""Tests for utility functions."""

import subprocess
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
import git

from juno_agent.utils import SystemStatus, open_browser, run_command


class TestSystemStatus:
    """Test SystemStatus class."""
    
    def test_init(self):
        """Test SystemStatus initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            status = SystemStatus(workdir)
            assert status.workdir == workdir
    
    @patch('juno_agent.utils.git.Repo')
    def test_git_controlled(self, mock_repo):
        """Test git controlled detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            status = SystemStatus(workdir)
            
            # Mock git repo
            mock_repo_instance = MagicMock()
            mock_repo_instance.git_dir = str(workdir / ".git")
            mock_repo.return_value = mock_repo_instance
            
            assert status.is_git_controlled()
            assert status.get_git_root() == workdir
            assert status.is_git_root()
    
    @patch('juno_agent.utils.git.Repo')
    def test_not_git_controlled(self, mock_repo):
        """Test non-git directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            status = SystemStatus(workdir)
            
            # Mock git exception
            mock_repo.side_effect = git.exc.InvalidGitRepositoryError()
            
            assert not status.is_git_controlled()
            assert status.get_git_root() is None
            assert not status.is_git_root()
    
    @patch('juno_agent.utils.git.Repo')
    def test_git_subdirectory(self, mock_repo):
        """Test git subdirectory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir) / "subdir"
            workdir.mkdir()
            status = SystemStatus(workdir)
            
            # Mock git repo with different root
            mock_repo_instance = MagicMock()
            mock_repo_instance.git_dir = str(Path(temp_dir) / ".git")
            mock_repo.return_value = mock_repo_instance
            
            assert status.is_git_controlled()
            assert status.get_git_root() == Path(temp_dir)
            assert not status.is_git_root()
    
    def test_get_status_info(self):
        """Test getting status information."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            status = SystemStatus(workdir)
            
            with patch.object(status, '_get_git_status', return_value="✗ Not a git repository"):
                status_info = status.get_status_info()
                
                assert "workdir" in status_info
                assert "git_status" in status_info
                assert "api_key_status" in status_info
                assert "editor" in status_info
                assert status_info["workdir"] == str(workdir)
                assert status_info["git_status"] == "✗ Not a git repository"


class TestUtilityFunctions:
    """Test utility functions."""
    
    @patch('webbrowser.open')
    def test_open_browser_success(self, mock_webbrowser):
        """Test successful browser opening."""
        mock_webbrowser.return_value = True
        
        result = open_browser("https://example.com")
        assert result is True
        mock_webbrowser.assert_called_once_with("https://example.com")
    
    @patch('webbrowser.open')
    def test_open_browser_failure(self, mock_webbrowser):
        """Test browser opening failure."""
        mock_webbrowser.side_effect = Exception("Browser error")
        
        result = open_browser("https://example.com")
        assert result is False
    
    @patch('subprocess.run')
    def test_run_command_success(self, mock_run):
        """Test successful command execution."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "success output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        success, output = run_command("echo hello")
        assert success is True
        assert "success output" in output
    
    @patch('subprocess.run')
    def test_run_command_failure(self, mock_run):
        """Test failed command execution."""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error output"
        mock_run.return_value = mock_result
        
        success, output = run_command("false")
        assert success is False
        assert "error output" in output
    
    @patch('subprocess.run')
    def test_run_command_timeout(self, mock_run):
        """Test command timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("cmd", 30)
        
        success, output = run_command("sleep 60")
        assert success is False
        assert "Command timed out" in output
    
    @patch('subprocess.run')
    def test_run_command_exception(self, mock_run):
        """Test command execution exception."""
        mock_run.side_effect = Exception("Command error")
        
        success, output = run_command("invalid_command")
        assert success is False
        assert "Command error" in output