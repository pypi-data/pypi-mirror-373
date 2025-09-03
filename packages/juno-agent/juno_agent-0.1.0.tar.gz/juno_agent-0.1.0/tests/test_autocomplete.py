"""Tests for command autocomplete functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest
from rich.console import Console

from juno_agent.ui import AutoCompleteInput, CommandCompleter


class TestCommandCompleter:
    """Test CommandCompleter class."""
    
    def test_command_completion(self):
        """Test command completion functionality."""
        commands = ["/apikey", "/agent", "/editor", "/exit", "/help"]
        completer = CommandCompleter(commands)
        
        # Test completing "/a"
        result = completer.complete("/a", 0)
        assert result == "/apikey"
        
        result = completer.complete("/a", 1)
        assert result == "/agent"
        
        result = completer.complete("/a", 2)
        assert result is None
        
        # Test completing "/e"
        result = completer.complete("/e", 0)
        assert result == "/editor"
        
        result = completer.complete("/e", 1)
        assert result == "/exit"
        
        result = completer.complete("/e", 2)
        assert result is None
        
        # Test completing non-command
        result = completer.complete("hello", 0)
        assert result is None
        
        # Test completing exact command
        result = completer.complete("/help", 0)
        assert result == "/help"
        
        result = completer.complete("/help", 1)
        assert result is None


class TestAutoCompleteInput:
    """Test AutoCompleteInput class."""
    
    def test_init_without_readline(self):
        """Test initialization when readline is not available."""
        commands = ["/test", "/help"]
        console = Console()
        
        with patch('juno_agent.ui.HAS_READLINE', False):
            autocomplete = AutoCompleteInput(commands, console)
            assert not autocomplete.has_readline
            assert autocomplete.commands == commands
    
    def test_init_with_readline(self):
        """Test initialization when readline is available."""
        commands = ["/test", "/help"]
        console = Console()
        
        with patch('juno_agent.ui.HAS_READLINE', True), \
             patch('juno_agent.ui.readline') as mock_readline:
            
            autocomplete = AutoCompleteInput(commands, console)
            assert autocomplete.has_readline
            assert autocomplete.commands == commands
            
            # Verify readline was configured
            mock_readline.set_completer.assert_called_once()
            # Check that parse_and_bind was called multiple times with different settings
            parse_and_bind_calls = mock_readline.parse_and_bind.call_args_list
            tab_complete_called = any("tab: complete" in str(call) for call in parse_and_bind_calls)
            assert tab_complete_called
    
    def test_show_completions(self):
        """Test showing available completions."""
        commands = ["/apikey", "/agent", "/editor", "/exit"]
        console = Console()
        autocomplete = AutoCompleteInput(commands, console)
        
        # Test partial command completion
        completions = autocomplete.show_completions("/a")
        assert "/apikey" in completions
        assert "/agent" in completions
        assert len(completions) == 2
        
        # Test single completion
        completions = autocomplete.show_completions("/api")
        assert completions == ["/apikey"]
        
        # Test no completions
        completions = autocomplete.show_completions("/xyz")
        assert completions == []
        
        # Test non-command text
        completions = autocomplete.show_completions("hello")
        assert completions == []
    
    def test_input_without_readline(self):
        """Test input without readline."""
        commands = ["/test"]
        console = Console()
        
        with patch('juno_agent.ui.HAS_READLINE', False), \
             patch('builtins.input', return_value="test input"):
            
            autocomplete = AutoCompleteInput(commands, console)
            result = autocomplete.input("prompt: ")
            assert result == "test input"
    
    def test_input_with_readline(self):
        """Test input with readline."""
        commands = ["/test"]
        console = Console()
        
        with patch('juno_agent.ui.HAS_READLINE', True), \
             patch('juno_agent.ui.readline') as mock_readline, \
             patch('builtins.input', return_value="test input"):
            
            autocomplete = AutoCompleteInput(commands, console)
            result = autocomplete.input("prompt: ")
            assert result == "test input"
            
            # Verify history was added
            mock_readline.add_history.assert_called_once_with("test input")
    
    def test_input_keyboard_interrupt(self):
        """Test input handling keyboard interrupt."""
        commands = ["/test"]
        console = Console()
        
        with patch('juno_agent.ui.HAS_READLINE', False), \
             patch('builtins.input', side_effect=KeyboardInterrupt()):
            
            autocomplete = AutoCompleteInput(commands, console)
            
            with pytest.raises(KeyboardInterrupt):
                autocomplete.input("prompt: ")
    
    def test_cleanup(self):
        """Test cleanup functionality."""
        commands = ["/test"]
        console = Console()
        
        with patch('juno_agent.ui.HAS_READLINE', True), \
             patch('juno_agent.ui.readline') as mock_readline:
            
            autocomplete = AutoCompleteInput(commands, console)
            autocomplete.cleanup()
            
            # Verify history was written
            mock_readline.write_history_file.assert_called_once()
    
    def test_cleanup_without_readline(self):
        """Test cleanup when readline is not available."""
        commands = ["/test"]
        console = Console()
        
        with patch('juno_agent.ui.HAS_READLINE', False):
            autocomplete = AutoCompleteInput(commands, console)
            # Should not raise any errors
            autocomplete.cleanup()
    
    def test_history_file_handling(self):
        """Test history file handling with config directory."""
        commands = ["/test"]
        console = Console()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            with patch('juno_agent.ui.HAS_READLINE', True), \
                 patch('juno_agent.ui.readline') as mock_readline:
                
                autocomplete = AutoCompleteInput(commands, console, config_dir)
                assert autocomplete.history_file == config_dir / ".history"
                
                # Test reading history file
                mock_readline.read_history_file.assert_called_once_with(str(config_dir / ".history"))
                
                # Test cleanup with history file
                autocomplete.cleanup()
                mock_readline.write_history_file.assert_called_with(str(config_dir / ".history"))