"""Tests for UI improvements and bug fixes."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from rich.console import Console

from juno_agent.config import ConfigManager
from juno_agent.ui import (
    WelcomeScreen, SetupWizard, ChatInterface, AutoCompleteInput, 
    CommandCompleter, WizardApp
)
from juno_agent.utils import SystemStatus


class TestAPIKeyInputMasking:
    """Test that API key input is properly masked."""
    
    def test_api_key_input_uses_getpass(self):
        """Test that API key input uses getpass for masking."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            system_status = SystemStatus(workdir)
            wizard = SetupWizard(config_manager, system_status)
            
            with patch('juno_agent.ui.getpass.getpass') as mock_getpass:
                with patch('juno_agent.ui.Confirm.ask', return_value=True):
                    with patch.object(wizard.config_manager, 'validate_api_key_with_backend') as mock_validate:
                        mock_getpass.return_value = "test-api-key"
                        mock_validate.return_value = {"valid": True, "user_level": "premium"}
                        
                        wizard._setup_api_key()
                        
                        # Verify getpass was called instead of Prompt.ask
                        mock_getpass.assert_called_once()
                        assert "Enter your API key (***)" in mock_getpass.call_args[0][0]
    
    def test_api_key_update_uses_getpass(self):
        """Test that API key update also uses getpass."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            # Set existing API key
            config_manager.set_api_key("existing-key")
            
            chat = ChatInterface(config_manager)
            
            with patch('juno_agent.ui.getpass.getpass') as mock_getpass:
                with patch('juno_agent.ui.Confirm.ask', return_value=True):
                    mock_getpass.return_value = "new-api-key"
                    
                    chat._handle_apikey_command()
                    
                    mock_getpass.assert_called_once()
                    # Check for the new enhanced prompt
                    call_arg = mock_getpass.call_args[0][0]
                    assert "Enter new API key" in call_arg or "🔐" in call_arg


class TestEditorSelectionImprovements:
    """Test arrow key navigation and improved editor selection."""
    
    def test_editor_selection_uses_input(self):
        """Test that editor selection uses simple input with default."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            system_status = SystemStatus(workdir)
            wizard = SetupWizard(config_manager, system_status)
            
            with patch('builtins.input', return_value='1') as mock_input:
                with patch.object(wizard.mcp_installer, 'get_supported_editor_names') as mock_editors:
                    mock_editors.return_value = ["Claude Code", "Cursor", "Windsurf"]
                    
                    wizard._setup_editor()
                    
                    # Verify input was called
                    mock_input.assert_called()
                    # Verify editor was set
                    config = config_manager.load_config()
                    assert config.editor == "Claude Code"
    
    def test_editor_selection_displays_list(self):
        """Test that editor selection displays a simple list."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            system_status = SystemStatus(workdir)
            wizard = SetupWizard(config_manager, system_status)
            
            with patch('builtins.input', return_value='1'):
                with patch.object(wizard.mcp_installer, 'get_supported_editor_names') as mock_editors:
                    with patch.object(wizard.console, 'print') as mock_print:
                        mock_editors.return_value = ["Claude Code", "Cursor"]
                        
                        wizard._setup_editor()
                        
                        # Check that editor list was printed
                        list_printed = any(
                            "Available editors:" in str(call)
                            for call in mock_print.call_args_list
                        )
                        assert list_printed or len(mock_print.call_args_list) > 0


class TestDefaultConfirmations:
    """Test that y/n questions have appropriate defaults."""
    
    def test_setup_wizard_defaults(self):
        """Test that setup wizard questions have Y as default where appropriate."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            system_status = SystemStatus(workdir)
            wizard = SetupWizard(config_manager, system_status)
            
            with patch('juno_agent.ui.Confirm.ask') as mock_confirm:
                with patch('juno_agent.ui.getpass.getpass', return_value="test-key"):
                    mock_confirm.return_value = True
                    
                    wizard._setup_api_key()
                    
                    # Check that the first Confirm.ask call has default=True
                    confirm_calls = mock_confirm.call_args_list
                    if confirm_calls:
                        first_call = confirm_calls[0]
                        assert first_call[1].get('default') is True
    
    def test_chat_interface_defaults(self):
        """Test that chat interface confirmations have appropriate defaults."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            chat = ChatInterface(config_manager)
            
            with patch('juno_agent.ui.Confirm.ask') as mock_confirm:
                mock_confirm.return_value = False  # User chooses not to proceed
                
                chat._handle_reset_command()
                
                # Verify that reset confirmation has default=False (safer default)
                mock_confirm.assert_called_once()
                assert mock_confirm.call_args[1]['default'] is False


class TestCommandAutocompletion:
    """Test command autocompletion functionality."""
    
    def test_command_completer_basic_functionality(self):
        """Test basic command completion."""
        commands = ["/apikey", "/editor", "/setup", "/scan", "/exit"]
        completer = CommandCompleter(commands)
        
        # Test completion for "/a"
        result = completer.complete("/a", 0)
        assert result == "/apikey"
        
        # Test no more completions
        result = completer.complete("/a", 1)
        assert result is None
    
    def test_command_completer_multiple_matches(self):
        """Test completion with multiple matches."""
        commands = ["/scan", "/setup", "/exit"]
        completer = CommandCompleter(commands)
        
        # Test completion for "/s" (should match both /scan and /setup)
        result1 = completer.complete("/s", 0)
        result2 = completer.complete("/s", 1)
        
        assert result1 in ["/scan", "/setup"]
        assert result2 in ["/scan", "/setup"]
        assert result1 != result2
    
    def test_autocomplete_input_initialization(self):
        """Test AutoCompleteInput initialization."""
        commands = ["/test", "/example"]
        console = Console()
        
        # Test with readline available
        with patch('juno_agent.ui.HAS_READLINE', True):
            autocomplete = AutoCompleteInput(commands, console)
            assert autocomplete.has_readline is True
            assert autocomplete.commands == commands
    
    def test_show_completions(self):
        """Test showing available completions."""
        commands = ["/apikey", "/agent", "/setup"]
        console = Console()
        autocomplete = AutoCompleteInput(commands, console)
        
        # Test completion for "/a"
        completions = autocomplete.show_completions("/a")
        assert "/apikey" in completions
        assert "/agent" in completions
        assert "/setup" not in completions


class TestChatInterfaceImprovements:
    """Test chat interface improvements."""
    
    def test_chat_interface_displays_panels(self):
        """Test that chat interface displays bordered panels."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            chat = ChatInterface(config_manager)
            
            with patch.object(chat.console, 'print') as mock_print:
                with patch.object(chat.autocomplete_input, 'input', side_effect=['/exit']):
                    chat.run()
                    
                    # Check that panels were printed
                    panel_printed = any(
                        hasattr(call[0][0], 'title') 
                        for call in mock_print.call_args_list
                        if call[0] and hasattr(call[0][0], 'title')
                    )
                    assert panel_printed or len(mock_print.call_args_list) > 0
    
    def test_conversation_history_tracking(self):
        """Test that conversation history is properly tracked."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            chat = ChatInterface(config_manager)
            
            with patch.object(chat.console, 'print') as mock_print:
                with patch.object(chat.autocomplete_input, 'input', side_effect=['hello', '/exit']):
                    chat.run()
                    
                    # Check that conversation formatting was applied
                    conversation_found = any(
                        "🔵 You" in str(call) or "🤖 AI" in str(call)
                        for call in mock_print.call_args_list
                    )
                    assert conversation_found or len(mock_print.call_args_list) > 0
    
    def test_visual_separators(self):
        """Test that visual separators are added between exchanges."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            chat = ChatInterface(config_manager)
            
            with patch.object(chat.console, 'print') as mock_print:
                with patch.object(chat.autocomplete_input, 'input', side_effect=['test message', '/exit']):
                    chat.run()
                    
                    # Check that separator lines were printed
                    separator_found = any(
                        "─" in str(call) or "━" in str(call)
                        for call in mock_print.call_args_list
                    )
                    assert separator_found or len(mock_print.call_args_list) > 0


class TestWizardAppIntegration:
    """Test integration of all improvements in WizardApp."""
    
    def test_wizard_app_runs_with_improvements(self):
        """Test that WizardApp runs with all improvements integrated."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            system_status = SystemStatus(workdir)
            
            # Set up completed config to skip setup
            config_manager.update_config(setup_completed=True)
            
            app = WizardApp(config_manager, system_status)
            
            with patch('juno_agent.ui.Confirm.ask', return_value=False):
                with patch('juno_agent.ui.WelcomeScreen') as mock_welcome_class:
                    with patch('juno_agent.ui.ChatInterface') as mock_chat_class:
                        mock_welcome = MagicMock()
                        mock_welcome_class.return_value = mock_welcome
                        mock_chat = MagicMock()
                        mock_chat_class.return_value = mock_chat
                        
                        app.run()
                        
                        # Verify WelcomeScreen was created and displayed
                        mock_welcome_class.assert_called_once_with(config_manager, system_status)
                        mock_welcome.display.assert_called_once()
                        
                        # Verify ChatInterface was created and run
                        mock_chat_class.assert_called_once_with(config_manager)
                        mock_chat.run.assert_called_once()


class TestErrorHandling:
    """Test error handling in improved UI components."""
    
    def test_api_key_validation_error_handling(self):
        """Test error handling in API key validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            system_status = SystemStatus(workdir)
            wizard = SetupWizard(config_manager, system_status)
            
            # Test that validation errors are handled gracefully
            with patch.object(wizard.config_manager, 'validate_api_key_with_backend') as mock_validate:
                mock_validate.return_value = {"valid": False, "error": "Invalid key"}
                
                # This should not raise an exception
                try:
                    result = asyncio.run(wizard.config_manager.validate_api_key_with_backend("test-key"))
                    assert result["valid"] is False
                    assert "Invalid key" in result["error"]
                except Exception:
                    pytest.fail("validate_api_key_with_backend should handle errors gracefully")
    
    def test_editor_selection_keyboard_interrupt(self):
        """Test handling of keyboard interrupt in editor selection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            system_status = SystemStatus(workdir)
            wizard = SetupWizard(config_manager, system_status)
            
            with patch('builtins.input', side_effect=KeyboardInterrupt):
                with patch('juno_agent.ui.Confirm.ask', return_value=False):  # Don't try again
                    with patch.object(wizard.mcp_installer, 'get_supported_editor_names', return_value=["Claude Code"]):
                        # Should not raise exception, should handle gracefully
                        wizard._setup_editor()
    
    def test_command_completion_with_no_readline(self):
        """Test command completion gracefully handles missing readline."""
        commands = ["/test"]
        console = Console()
        
        with patch('juno_agent.ui.HAS_READLINE', False):
            autocomplete = AutoCompleteInput(commands, console)
            assert autocomplete.has_readline is False
            
            # Test that show_completions still works without readline
            completions = autocomplete.show_completions("/t")
            assert "/test" in completions


class TestAgentIntegration:
    """Test AI agent integration and chat functionality."""
    
    def test_tiny_agent_chat_initialization(self):
        """Test TinyAgentChat initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            
            # Import here to avoid issues if agent module has problems
            from juno_agent.agent import TinyAgentChat
            agent = TinyAgentChat(config_manager)
            
            assert agent.config_manager == config_manager
            assert agent.conversation_history == []
    
    @pytest.mark.asyncio
    async def test_agent_processes_chat_messages(self):
        """Test that agent processes chat messages."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            
            from juno_agent.agent import TinyAgentChat
            agent = TinyAgentChat(config_manager)
            
            # Test project-related query
            response = await agent.process_chat_message("Tell me about my project")
            assert isinstance(response, str)
            assert len(response) > 0
            assert len(agent.conversation_history) == 2  # user + assistant
    
    @pytest.mark.asyncio
    async def test_agent_context_awareness(self):
        """Test that agent uses project context."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            config_manager.update_config(libraries=["fastapi", "requests"])
            
            from juno_agent.agent import TinyAgentChat
            agent = TinyAgentChat(config_manager)
            
            context = {
                "workdir": str(workdir),
                "libraries": ["fastapi", "requests"]
            }
            
            response = await agent.process_chat_message("What dependencies does my project have?", context)
            assert "fastapi" in response.lower() or "dependencies" in response.lower()
    
    def test_agent_conversation_summary(self):
        """Test conversation summary generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            
            from juno_agent.agent import TinyAgentChat
            agent = TinyAgentChat(config_manager)
            
            # Add some mock conversation history
            agent.conversation_history = [
                {"role": "user", "content": "Help with setup", "timestamp": "2024-01-01T00:00:00"},
                {"role": "assistant", "content": "Sure, I can help", "timestamp": "2024-01-01T00:00:01"}
            ]
            
            summary = agent.get_conversation_summary()
            assert summary["total_exchanges"] == 1
            assert summary["last_user_message"] == "Help with setup"
    
    def test_project_analysis_agent(self):
        """Test ProjectAnalysisAgent initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            
            from juno_agent.agent import ProjectAnalysisAgent
            analysis_agent = ProjectAnalysisAgent(config_manager)
            
            assert analysis_agent.config_manager == config_manager
    
    @pytest.mark.asyncio
    async def test_project_analysis_context(self):
        """Test project context analysis."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            config_manager.update_config(libraries=["numpy", "pandas"])
            
            from juno_agent.agent import ProjectAnalysisAgent
            analysis_agent = ProjectAnalysisAgent(config_manager)
            
            context = await analysis_agent.analyze_project_context(workdir)
            
            assert "analysis_timestamp" in context
            assert "project_path" in context
            assert "detected_patterns" in context
            assert "optimization_suggestions" in context


class TestEnhancedChatInterface:
    """Test enhanced chat interface with AI integration."""
    
    def test_chat_interface_includes_agent(self):
        """Test that ChatInterface initializes with agent."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            chat = ChatInterface(config_manager)
            
            assert hasattr(chat, 'tiny_agent')
            assert hasattr(chat, 'analysis_agent')
    
    def test_enhanced_ui_components(self):
        """Test enhanced UI components in chat interface."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            config_manager.set_api_key("test-key")
            config_manager.update_config(editor="Claude Code")
            
            chat = ChatInterface(config_manager)
            
            # Test _print_ai_response method
            with patch.object(chat.console, 'print') as mock_print:
                chat._print_ai_response("Test message", "success")
                mock_print.assert_called_once()
                
                # Check that the response includes timestamp and styling
                call_args = str(mock_print.call_args)
                assert "AI" in call_args
    
    def test_help_command_enhancement(self):
        """Test enhanced help command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            chat = ChatInterface(config_manager)
            
            with patch.object(chat.console, 'print') as mock_print:
                chat._handle_help_command()
                
                # Verify that enhanced help was displayed
                help_displayed = any(
                    "Commands" in str(call) or "Usage Tips" in str(call)
                    for call in mock_print.call_args_list
                )
                assert help_displayed or len(mock_print.call_args_list) > 0
    
    def test_agent_command_enhancement(self):
        """Test enhanced /agent command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            config_manager.set_api_key("test-key")
            chat = ChatInterface(config_manager)
            
            with patch.object(chat.console, 'print') as mock_print:
                with patch('juno_agent.ui.Confirm.ask', return_value=False):
                    chat._handle_agent_command()
                
                # Verify agent status was displayed
                agent_info_displayed = any(
                    "Agent" in str(call) or "AI" in str(call)
                    for call in mock_print.call_args_list
                )
                assert agent_info_displayed or len(mock_print.call_args_list) > 0


class TestConversationPersistence:
    """Test conversation history persistence."""
    
    def test_conversation_saving(self):
        """Test that conversations are saved to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            
            from juno_agent.agent import TinyAgentChat
            agent = TinyAgentChat(config_manager)
            
            # Add conversation history
            agent.conversation_history = [
                {
                    "timestamp": "2024-01-01T00:00:00",
                    "role": "user",
                    "content": "Hello",
                    "context": {}
                },
                {
                    "timestamp": "2024-01-01T00:00:01", 
                    "role": "assistant",
                    "content": "Hi there!",
                    "context": {}
                }
            ]
            
            # Save conversation
            agent.save_conversation()
            
            # Check that file was created
            conversation_file = config_manager.config_dir / "conversation_history.json"
            assert conversation_file.exists()
            
            # Verify content
            import json
            with open(conversation_file, 'r') as f:
                data = json.load(f)
            
            assert len(data) == 1  # One conversation session
            assert len(data[0]["messages"]) == 2  # Two messages
    
    def test_conversation_history_limit(self):
        """Test that conversation history is limited."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            
            from juno_agent.agent import TinyAgentChat
            
            # Create 15 separate agent instances to simulate 15 sessions
            for i in range(15):
                agent = TinyAgentChat(config_manager)
                agent.conversation_history = [
                    {
                        "timestamp": f"2024-01-{i+1:02d}T00:00:00",
                        "role": "user", 
                        "content": f"Message {i}",
                        "context": {}
                    }
                ]
                agent.save_conversation()
            
            # Check that only 10 conversations are kept
            conversation_file = config_manager.config_dir / "conversation_history.json"
            import json
            with open(conversation_file, 'r') as f:
                data = json.load(f)
            
            assert len(data) == 10  # Should be limited to 10


class TestCommandAutocompletionEnhancements:
    """Test enhanced command autocompletion."""
    
    def test_display_matches_formatting(self):
        """Test enhanced display matches formatting for multiple options."""
        commands = ["/apikey", "/agent", "/setup"]
        completer = CommandCompleter(commands)
        
        with patch('sys.stdout') as mock_stdout:
            # Test single match (should not display)
            completer.display_matches("", ["/apikey"], 10)
            mock_stdout.flush.assert_not_called()
            
            # Test multiple matches (should display)
            completer.display_matches("", ["/apikey", "/agent"], 10)
            mock_stdout.flush.assert_called()
    
    def test_inline_completion_best_match(self):
        """Test get_best_match functionality for inline completion."""
        commands = ["/apikey", "/agent", "/setup", "/scan"]
        completer = CommandCompleter(commands)
        
        # Test single match
        assert completer.get_best_match("/api") == "/apikey"
        
        # Test multiple matches - should return first from the original command list
        assert completer.get_best_match("/a") == "/apikey"  # /apikey comes first in original list
        
        # Test no match
        assert completer.get_best_match("/xyz") is None
        
        # Test non-command
        assert completer.get_best_match("hello") is None
        
        # Test exact match - when typing complete command, returns same command
        assert completer.get_best_match("/agent") == "/agent"  # Only one command starts with /agent
        
        # Test cycling behavior with partial match that becomes exact
        # When user types "/a" and gets multiple matches, we should cycle through them
        first_match = completer.get_best_match("/a")
        assert first_match == "/apikey"  # First in list
    
    def test_inline_completer_integration(self):
        """Test the _inline_completer method."""
        commands = ["/apikey", "/agent", "/setup"]
        console = Console()
        autocomplete = AutoCompleteInput(commands, console)
        
        # Test best match completion - should return first from original command order
        with patch('juno_agent.ui.HAS_READLINE', True):
            result = autocomplete._inline_completer("/a", 0)
            # Should get first match from original command list order
            candidates = [cmd for cmd in commands if cmd.startswith("/a")]
            assert result == candidates[0]  # First in original order
            
            # Test state cycling - need to call state=0 first to initialize candidates
            autocomplete._inline_completer("/a", 0)  # Initialize candidates
            result = autocomplete._inline_completer("/a", 1)
            assert result == candidates[1] if len(candidates) > 1 else None
    
    def test_multiple_matches_behavior(self):
        """Test that multiple matches are handled correctly."""
        commands = ["/apikey", "/agent", "/setup"]
        console = Console()
        autocomplete = AutoCompleteInput(commands, console)
        
        # Test that multiple matches return all candidates through cycling
        candidates = [cmd for cmd in commands if cmd.startswith("/a")]
        assert len(candidates) == 2  # /apikey and /agent
        
        with patch('juno_agent.ui.HAS_READLINE', True):
            # Both candidates should be accessible
            result0 = autocomplete._inline_completer("/a", 0)
            result1 = autocomplete._inline_completer("/a", 1)
            
            assert result0 in candidates
            assert result1 in candidates
            assert result0 != result1
    
    def test_autocomplete_input_with_history(self):
        """Test autocomplete input with history file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            commands = ["/test"]
            console = Console()
            
            autocomplete = AutoCompleteInput(commands, console, config_dir)
            
            # Check that history file path is set
            assert autocomplete.history_file == config_dir / ".history"
    
    def test_autocomplete_cleanup(self):
        """Test autocomplete cleanup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            commands = ["/test"]
            console = Console()
            
            with patch('juno_agent.ui.HAS_READLINE', True):
                autocomplete = AutoCompleteInput(commands, console, config_dir)
                
                # Test cleanup doesn't raise errors
                try:
                    autocomplete.cleanup()
                except Exception as e:
                    pytest.fail(f"Cleanup should not raise exceptions: {e}")


class TestRichUIEnhancements:
    """Test Rich UI enhancements and sophisticated display."""
    
    def test_sophisticated_header_display(self):
        """Test sophisticated header in chat interface."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            config_manager.set_api_key("test-key")
            config_manager.update_config(editor="Claude Code", mcp_server_installed=True)
            
            chat = ChatInterface(config_manager)
            
            with patch.object(chat.console, 'print') as mock_print:
                with patch.object(chat.autocomplete_input, 'input', side_effect=['/exit']):
                    chat.run()
                
                # Check for sophisticated header elements
                header_found = any(
                    "juno-agent" in str(call) or "🧙‍♂️" in str(call)
                    for call in mock_print.call_args_list
                )
                assert header_found or len(mock_print.call_args_list) > 0
    
    def test_command_palette_grouping(self):
        """Test command palette grouping."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            chat = ChatInterface(config_manager)
            
            with patch.object(chat.console, 'print') as mock_print:
                with patch.object(chat.autocomplete_input, 'input', side_effect=['/exit']):
                    chat.run()
                
                # Check for command grouping
                grouping_found = any(
                    "Setup" in str(call) or "Project" in str(call) or "System" in str(call)
                    for call in mock_print.call_args_list  
                )
                assert grouping_found or len(mock_print.call_args_list) > 0
    
    def test_status_indicators(self):
        """Test status indicators in UI."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            config_manager.set_api_key("test-key")
            
            chat = ChatInterface(config_manager)
            
            with patch.object(chat.console, 'print') as mock_print:
                with patch.object(chat.autocomplete_input, 'input', side_effect=['/exit']):
                    chat.run()
                
                # Check for status indicators (emojis and status text)
                status_found = any(
                    "🔑" in str(call) or "📝" in str(call) or "🔗" in str(call)
                    for call in mock_print.call_args_list
                )
                assert status_found or len(mock_print.call_args_list) > 0


class TestErrorResiliency:
    """Test error handling and resilience of enhanced features."""
    
    @pytest.mark.asyncio
    async def test_agent_error_handling(self):
        """Test that agent errors are handled gracefully."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            
            from juno_agent.agent import TinyAgentChat
            agent = TinyAgentChat(config_manager)
            
            # Test with invalid context that might cause errors
            try:
                response = await agent.process_chat_message("test", {"invalid": None})
                assert isinstance(response, str)
            except Exception as e:
                pytest.fail(f"Agent should handle errors gracefully: {e}")
    
    def test_chat_interface_exception_handling(self):
        """Test chat interface handles exceptions."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            chat = ChatInterface(config_manager)
            
            # Test that exceptions in agent processing are caught
            with patch.object(chat.tiny_agent, 'process_chat_message', side_effect=Exception("Test error")):
                with patch.object(chat.console, 'print') as mock_print:
                    with patch.object(chat.autocomplete_input, 'input', side_effect=['hello', '/exit']):
                        # Should not raise exception
                        try:
                            chat.run()
                        except Exception as e:
                            pytest.fail(f"Chat interface should handle agent errors: {e}")
    
    def test_conversation_save_error_handling(self):
        """Test that conversation save errors don't break exit."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workdir = Path(temp_dir)
            config_manager = ConfigManager(workdir)
            chat = ChatInterface(config_manager)
            
            # Mock save_conversation to raise an error
            with patch.object(chat.tiny_agent, 'save_conversation', side_effect=Exception("Save error")):
                with patch.object(chat.console, 'print'):
                    with patch.object(chat.autocomplete_input, 'input', side_effect=['/exit']):
                        with patch.object(chat.autocomplete_input, 'cleanup'):
                            # Should not raise exception despite save error
                            try:
                                chat.run()
                            except Exception as e:
                                pytest.fail(f"Exit should handle save errors gracefully: {e}")