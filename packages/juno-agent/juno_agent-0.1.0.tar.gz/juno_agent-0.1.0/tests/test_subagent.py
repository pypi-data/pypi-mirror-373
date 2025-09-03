"""Tests for subagent functionality in TinyCodeAgentChat."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path

from juno_agent.config import ConfigManager, Config, AgentConfig
from juno_agent.tiny_agent import TinyCodeAgentChat

# Configure pytest for async tests - applied only to async test methods


@pytest.fixture
def mock_config_manager(tmp_path):
    """Create a mock config manager for testing."""
    config_manager = Mock(spec=ConfigManager)
    config_manager.workdir = tmp_path / "workdir"
    config_manager.config_dir = tmp_path / "config"
    
    # Ensure directories exist for tests
    config_manager.workdir.mkdir(parents=True, exist_ok=True)
    config_manager.config_dir.mkdir(parents=True, exist_ok=True)
    
    # Mock agent configuration
    agent_config = Mock(spec=AgentConfig)
    agent_config.model_name = "gpt-5-mini"
    agent_config.provider = "openai"
    agent_config.temperature = 0.0
    agent_config.max_tokens = None
    agent_config.custom_base_url = None
    agent_config.custom_params = {}
    agent_config.max_turns = 10
    agent_config.reuse_subagents = False  # Default to fresh subagents
    
    # Mock main configuration
    config = Mock(spec=Config)
    config.agent_config = agent_config
    config.project_description = "Test Project"
    config.libraries = ["pytest", "requests"]
    config.editor = "code"
    
    config_manager.load_config.return_value = config
    config_manager.get_model_api_key.return_value = "test-api-key"
    config_manager.create_debug_logger = Mock(return_value=Mock())
    
    return config_manager


@pytest.fixture
def tiny_agent_chat(mock_config_manager):
    """Create a TinyCodeAgentChat instance for testing."""
    return TinyCodeAgentChat(mock_config_manager)


class TestSubagentCreation:
    """Test subagent creation and configuration."""
    
    @pytest.mark.asyncio
    @patch('tinyagent.TinyCodeAgent')
    async def test_create_coding_subagent_success(self, mock_tiny_agent_class, tiny_agent_chat):
        """Test successful creation of coding subagent."""
        # Mock TinyCodeAgent instance
        mock_subagent = AsyncMock()
        mock_tiny_agent_class.return_value = mock_subagent
        
        # Create subagent
        result = await tiny_agent_chat.create_coding_subagent()
        
        # Verify subagent was created
        assert result == mock_subagent
        # In fresh mode (default), subagent should not be stored
        assert tiny_agent_chat.subagent is None
        
        # Verify TinyCodeAgent was called with correct parameters
        mock_tiny_agent_class.assert_called_once()
        call_args = mock_tiny_agent_class.call_args[1]
        
        # Check key parameters
        assert call_args["model"] == "gpt-5-mini"
        assert call_args["api_key"] == "test-api-key"
        assert call_args["enable_python_tool"] is False  # Should be disabled
        assert call_args["enable_shell_tool"] is True    # Should be enabled
        assert call_args["temperature"] == 0.0
        assert "working directory: /test/workdir" in call_args["system_prompt"].lower()
        assert "subagent" in call_args["system_prompt"].lower()
    
    @pytest.mark.asyncio
    @patch('tinyagent.TinyCodeAgent')
    async def test_create_coding_subagent_reuse_mode(self, mock_tiny_agent_class, tiny_agent_chat, mock_config_manager):
        """Test that subagent reuse works when reuse_subagents is True."""
        # Enable reuse mode
        mock_config_manager.load_config.return_value.agent_config.reuse_subagents = True
        
        # Mock subagent
        mock_subagent = AsyncMock()
        mock_tiny_agent_class.return_value = mock_subagent
        
        # Create first subagent
        result1 = await tiny_agent_chat.create_coding_subagent()
        assert result1 == mock_subagent
        assert tiny_agent_chat.subagent == mock_subagent  # Should be stored
        
        # Create second subagent - should reuse
        result2 = await tiny_agent_chat.create_coding_subagent()
        assert result2 == mock_subagent  # Same instance
        mock_tiny_agent_class.assert_called_once()  # Only called once
    
    @pytest.mark.asyncio
    @patch('tinyagent.TinyCodeAgent')
    async def test_create_coding_subagent_fresh_mode(self, mock_tiny_agent_class, tiny_agent_chat, mock_config_manager):
        """Test that fresh subagents are created each time when reuse_subagents is False."""
        # Ensure fresh mode (default)
        mock_config_manager.load_config.return_value.agent_config.reuse_subagents = False
        
        # Mock subagents
        mock_subagent1 = AsyncMock()
        mock_subagent2 = AsyncMock()
        mock_tiny_agent_class.side_effect = [mock_subagent1, mock_subagent2]
        
        # Create first subagent
        result1 = await tiny_agent_chat.create_coding_subagent()
        assert result1 == mock_subagent1
        assert tiny_agent_chat.subagent is None  # Should not be stored
        
        # Create second subagent - should be fresh
        result2 = await tiny_agent_chat.create_coding_subagent()
        assert result2 == mock_subagent2  # Different instance
        assert result2 != result1  # Should be different
        assert mock_tiny_agent_class.call_count == 2  # Called twice
    
    @pytest.mark.asyncio
    async def test_create_coding_subagent_no_api_key(self, tiny_agent_chat, mock_config_manager):
        """Test subagent creation fails gracefully when no API key is available."""
        # Remove API key
        mock_config_manager.get_model_api_key.return_value = None
        
        # Try to create subagent
        result = await tiny_agent_chat.create_coding_subagent()
        
        # Should return None and not crash
        assert result is None
        assert tiny_agent_chat.subagent is None
    
    def test_subagent_system_prompt_content(self, tiny_agent_chat):
        """Test that subagent system prompt contains appropriate content."""
        prompt = tiny_agent_chat._get_subagent_system_prompt()
        
        # Check for key subagent characteristics
        assert "subagent" in prompt.lower()
        assert "shell commands only" in prompt.lower()
        assert "no python execution" in prompt.lower()
        assert "file system operations" in prompt.lower()
        assert "git operations" in prompt.lower()
        assert "development workflow" in prompt.lower()
        
        # Check project context is included
        assert "Test Project" in prompt
        assert "pytest" in prompt
        assert "/test/workdir" in prompt


class TestSubagentIntegration:
    """Test subagent integration with main agent."""
    
    @pytest.mark.asyncio
    @patch('tinyagent.TinyCodeAgent')
    @patch('tinyagent.hooks.MessageCleanupHook')
    @patch('tinyagent.hooks.token_tracker.create_token_tracker')
    @patch('tinyagent.tools.create_coding_subagent')
    @patch('tinyagent.SubagentConfig')
    async def test_initialize_agent_with_subagent(self, mock_subagent_config, mock_create_coding_subagent, mock_create_token_tracker, mock_cleanup_hook, mock_tiny_agent_class, tiny_agent_chat):
        """Test that main agent initialization includes subagent tool."""
        # Mock main agent
        mock_main_agent = Mock()
        mock_main_agent.custom_tool_handlers = {}
        mock_main_agent.callbacks = []  # Make it iterable
        
        # Configure mocks
        mock_tiny_agent_class.return_value = mock_main_agent
        mock_cleanup_hook.return_value = Mock()
        
        # Mock token tracker
        mock_parent_tracker = Mock()
        mock_child_tracker = Mock()
        mock_create_token_tracker.side_effect = [mock_parent_tracker, mock_child_tracker]
        
        # Mock subagent config
        mock_config = Mock()
        mock_config.to_agent_kwargs.return_value = {"model": "gpt-5-mini"}
        mock_subagent_config.from_parent_agent.return_value = mock_config
        
        # Mock coding subagent tool
        mock_subagent_tool = {
            "type": "function",
            "function": {
                "name": "subAgent",
                "description": "Launch a new agent with shell commands"
            }
        }
        mock_create_coding_subagent.return_value = mock_subagent_tool
        
        # Initialize agent
        await tiny_agent_chat.initialize_agent()
        
        # Verify main agent was created
        assert tiny_agent_chat.agent == mock_main_agent
        
        # Verify tool was added to main agent
        mock_main_agent.add_tool.assert_called_once_with(mock_subagent_tool)
        
        # Verify the token tracker was created for both parent and child
        assert mock_create_token_tracker.call_count == 2
    
    @pytest.mark.asyncio
    @patch('tinyagent.TinyCodeAgent')
    @patch('tinyagent.hooks.MessageCleanupHook')
    @patch('tinyagent.hooks.TokenTracker')
    async def test_initialize_agent_subagent_failure(self, mock_token_tracker, mock_cleanup_hook, mock_tiny_agent_class, tiny_agent_chat):
        """Test that main agent initialization continues if subagent tool creation fails."""
        # Mock main agent creation success
        mock_main_agent = Mock()
        mock_main_agent.custom_tool_handlers = {}
        mock_tiny_agent_class.return_value = mock_main_agent
        mock_cleanup_hook.return_value = Mock()
        mock_token_tracker.return_value = Mock()
        
        # Mock subagent tool creation failure by making _create_subagent_tool raise
        tiny_agent_chat._create_subagent_tool = Mock(side_effect=Exception("Tool creation failed"))
        
        # Initialize agent - should not raise exception
        await tiny_agent_chat.initialize_agent()
        
        # Verify main agent was created but tool was not added
        assert tiny_agent_chat.agent == mock_main_agent
        # Verify that add_tool was not called due to the exception
        mock_main_agent.add_tool.assert_not_called()


class TestSubagentCleanup:
    """Test proper cleanup of subagent resources."""
    
    @pytest.mark.asyncio
    async def test_close_with_subagent(self, tiny_agent_chat):
        """Test that close method properly cleans up both agents."""
        # Set up mock agents
        mock_main_agent = AsyncMock()
        mock_subagent = AsyncMock()
        tiny_agent_chat.agent = mock_main_agent
        tiny_agent_chat.subagent = mock_subagent
        
        # Close
        await tiny_agent_chat.close()
        
        # Verify both agents were closed
        mock_subagent.close.assert_called_once()
        mock_main_agent.close.assert_called_once()
        
        # Verify references were cleared
        assert tiny_agent_chat.agent is None
        assert tiny_agent_chat.subagent is None
    
    @pytest.mark.asyncio
    async def test_close_with_subagent_error(self, tiny_agent_chat):
        """Test that close handles subagent cleanup errors gracefully."""
        # Set up mock agents with subagent close error
        mock_main_agent = AsyncMock()
        mock_subagent = AsyncMock()
        mock_subagent.close.side_effect = Exception("Close error")
        tiny_agent_chat.agent = mock_main_agent
        tiny_agent_chat.subagent = mock_subagent
        
        # Close should not raise exception
        await tiny_agent_chat.close()
        
        # Verify main agent was still closed despite subagent error
        mock_subagent.close.assert_called_once()
        mock_main_agent.close.assert_called_once()
        
        # Verify references were cleared
        assert tiny_agent_chat.agent is None
        assert tiny_agent_chat.subagent is None


class TestSubagentConfiguration:
    """Test subagent configuration inheritance."""
    
    @pytest.mark.asyncio
    @patch('tinyagent.TinyCodeAgent')
    async def test_subagent_inherits_main_agent_settings(self, mock_tiny_agent_class, tiny_agent_chat, mock_config_manager):
        """Test that subagent inherits the same settings as main agent."""
        # Modify config to test inheritance
        config = mock_config_manager.load_config.return_value
        config.agent_config.temperature = 0.7
        config.agent_config.max_tokens = 4000
        config.agent_config.custom_base_url = "https://custom.api.url"
        config.agent_config.custom_params = {"custom_param": "value"}
        
        # Mock platform detection for provider selection
        with patch('juno_agent.tiny_agent.platform.system', return_value='Darwin'):
            with patch.object(tiny_agent_chat, '_should_use_seatbelt', return_value=True):
                mock_subagent = AsyncMock()
                mock_tiny_agent_class.return_value = mock_subagent
                
                # Create subagent
                await tiny_agent_chat.create_coding_subagent()
                
                # Check that subagent was created with inherited settings
                call_args = mock_tiny_agent_class.call_args[1]
                assert call_args["model"] == "gpt-5-mini"
                assert call_args["api_key"] == "test-api-key"
                assert call_args["temperature"] == 0.7
                assert call_args["max_tokens"] == 4000
                assert call_args["base_url"] == "https://custom.api.url"
                assert call_args["custom_param"] == "value"
                assert call_args["provider"] == "seatbelt"
                
                # But tool settings should be different
                assert call_args["enable_python_tool"] is False
                assert call_args["enable_shell_tool"] is True


class TestCallbackPropagation:
    """Test that callbacks are properly propagated from parent to subagent."""
    
    @pytest.mark.asyncio
    @patch('tinyagent.TinyCodeAgent')
    @patch('tinyagent.hooks.MessageCleanupHook')
    @patch('tinyagent.hooks.AnthropicPromptCacheCallback')
    async def test_create_coding_subagent_propagates_callbacks(self, mock_cache_callback, mock_cleanup_hook, mock_tiny_agent_class, tiny_agent_chat):
        """Test that MessageCleanupHook and AnthropicPromptCacheCallback are properly propagated from parent to subagent."""
        # Mock callback instances
        parent_cleanup_hook = Mock()
        parent_cache_callback = Mock()
        mock_cleanup_hook.return_value = parent_cleanup_hook
        mock_cache_callback.return_value = parent_cache_callback
        
        # Set up main agent with callbacks
        mock_main_agent = Mock()
        mock_main_agent.callbacks = [parent_cleanup_hook, parent_cache_callback]
        tiny_agent_chat.agent = mock_main_agent
        
        # Mock subagent
        mock_subagent = Mock()
        mock_subagent.callbacks = []
        mock_subagent.add_callback = Mock()
        mock_tiny_agent_class.return_value = mock_subagent
        
        # Create subagent
        result = await tiny_agent_chat.create_coding_subagent()
        
        # Verify subagent was created
        assert result == mock_subagent
        
        # Verify that parent callbacks were added to subagent (not new instances)
        callback_calls = mock_subagent.add_callback.call_args_list
        added_callbacks = [call[0][0] for call in callback_calls]
        
        # Check that the EXACT same instances from parent were added to subagent
        assert parent_cleanup_hook in added_callbacks, "Parent MessageCleanupHook should be propagated to subagent"
        assert parent_cache_callback in added_callbacks, "Parent AnthropicPromptCacheCallback should be propagated to subagent"
        
        # Verify that new instances were NOT created when parent callbacks exist
        # The add_callback should have been called with parent instances, not new ones
        assert mock_subagent.add_callback.call_count >= 2  # At least cleanup + cache callbacks
    
    @pytest.mark.asyncio
    @patch('tinyagent.TinyCodeAgent')
    @patch('tinyagent.hooks.MessageCleanupHook')
    @patch('tinyagent.hooks.AnthropicPromptCacheCallback')
    async def test_create_coding_subagent_creates_new_callbacks_when_parent_missing(self, mock_cache_callback, mock_cleanup_hook, mock_tiny_agent_class, tiny_agent_chat):
        """Test that new callback instances are created when parent doesn't have them."""
        # Mock new callback instances
        new_cleanup_hook = Mock()
        new_cache_callback = Mock()
        mock_cleanup_hook.return_value = new_cleanup_hook
        mock_cache_callback.return_value = new_cache_callback
        
        # Set up main agent WITHOUT callbacks
        mock_main_agent = Mock()
        mock_main_agent.callbacks = []  # No callbacks in parent
        tiny_agent_chat.agent = mock_main_agent
        
        # Mock subagent
        mock_subagent = Mock()
        mock_subagent.callbacks = []
        mock_subagent.add_callback = Mock()
        mock_tiny_agent_class.return_value = mock_subagent
        
        # Create subagent
        result = await tiny_agent_chat.create_coding_subagent()
        
        # Verify subagent was created
        assert result == mock_subagent
        
        # Verify that NEW callback instances were created and added
        callback_calls = mock_subagent.add_callback.call_args_list
        added_callbacks = [call[0][0] for call in callback_calls]
        
        # Check that new instances were added since parent didn't have them
        assert new_cleanup_hook in added_callbacks, "New MessageCleanupHook should be created when parent missing"
        assert new_cache_callback in added_callbacks, "New AnthropicPromptCacheCallback should be created when parent missing"
        
        # Verify callbacks were actually created
        mock_cleanup_hook.assert_called_once()
        mock_cache_callback.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('tinyagent.TinyCodeAgent')
    async def test_create_coding_subagent_handles_missing_main_agent(self, mock_tiny_agent_class, tiny_agent_chat):
        """Test that subagent creation handles case when main agent is not initialized."""
        # No main agent set
        tiny_agent_chat.agent = None
        
        # Mock subagent with callback tracking
        mock_subagent = Mock()
        mock_subagent.callbacks = []
        mock_subagent.add_callback = Mock()
        mock_tiny_agent_class.return_value = mock_subagent
        
        # Create subagent
        result = await tiny_agent_chat.create_coding_subagent()
        
        # Verify subagent was created
        assert result == mock_subagent
        
        # Verify that new callback instances were added (since no parent to inherit from)
        assert mock_subagent.add_callback.call_count >= 2  # At least cleanup + cache callbacks
    
    @pytest.mark.asyncio
    @patch('tinyagent.TinyCodeAgent')
    async def test_subagent_tool_inherits_parent_callbacks(self, mock_tiny_agent_class, tiny_agent_chat):
        """Test that subagent created via tool also inherits parent callbacks."""
        # Set up parent agent with mock callbacks
        parent_cleanup_hook = Mock()
        parent_cache_callback = Mock() 
        parent_cleanup_hook.__class__.__name__ = 'MessageCleanupHook'
        parent_cache_callback.__class__.__name__ = 'AnthropicPromptCacheCallback'
        
        mock_main_agent = Mock()
        mock_main_agent.callbacks = [parent_cleanup_hook, parent_cache_callback]
        tiny_agent_chat.agent = mock_main_agent
        
        # Mock TinyAgent for the tool initialization process
        with patch('tinyagent.hooks.MessageCleanupHook'), \
             patch('tinyagent.hooks.AnthropicPromptCacheCallback'), \
             patch('tinyagent.hooks.token_tracker.create_token_tracker'), \
             patch('tinyagent.tools.create_coding_subagent') as mock_create_tool, \
             patch('tinyagent.SubagentConfig') as mock_subagent_config:
            
            # Configure mocks for successful initialization
            mock_main_agent.add_callback = Mock()
            mock_main_agent.add_tool = Mock()
            
            mock_tiny_agent_class.return_value = mock_main_agent
            
            # Mock subagent config
            mock_config = Mock()
            mock_config.to_agent_kwargs.return_value = {
                'callbacks': [parent_cleanup_hook, parent_cache_callback]  # Should include parent callbacks
            }
            mock_subagent_config.from_parent_agent.return_value = mock_config
            
            # Mock coding subagent tool creation
            mock_create_tool.return_value = {'name': 'subAgent', 'description': 'test'}
            
            # Initialize agent (which should set up the subagent tool with inherited callbacks)
            await tiny_agent_chat.initialize_agent()
            
            # Verify that create_coding_subagent was called with parent callbacks
            mock_create_tool.assert_called_once()
            call_kwargs = mock_create_tool.call_args[1]
            
            # The callbacks should include the parent callbacks
            assert 'callbacks' in call_kwargs
            callbacks = call_kwargs['callbacks']
            
            # Check that parent callbacks are included in the subagent tool configuration
            callback_types = [type(cb).__name__ for cb in callbacks]
            assert 'MessageCleanupHook' in callback_types or parent_cleanup_hook in callbacks
            assert 'AnthropicPromptCacheCallback' in callback_types or parent_cache_callback in callbacks


class TestSubagentToolExecution:
    """Test the new subagent tool execution functionality."""
    
    @pytest.mark.asyncio
    @patch('tinyagent.create_coding_subagent')
    async def test_coding_subagent_tool_success(self, mock_create, tiny_agent_chat):
        """Test successful execution of coding subagent tool."""
        # Mock the subagent tool function
        mock_tool_func = AsyncMock(return_value="Task completed successfully")
        mock_tool = {'function': mock_tool_func}
        mock_create.return_value = mock_tool
        
        # Create and execute the tool
        subagent_tool = tiny_agent_chat._create_subagent_tool()
        result = await subagent_tool(
            prompt="Test shell command execution",
            absolute_workdir="/test/workdir",
            description="Test shell operations"
        )
        
        assert "Task completed successfully" in result
        mock_create.assert_called_once()
        
        # Verify the configuration passed to create_coding_subagent
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs['name'] == "coding_subagent"
        assert call_kwargs['description'] == "Test shell operations"
        assert call_kwargs['enable_python_tool'] is False
        assert call_kwargs['enable_shell_tool'] is True
        assert call_kwargs['working_directory'] == "/test/workdir"
        assert "specialized coding assistant" in call_kwargs['system_prompt']
    
    @pytest.mark.asyncio
    @patch('tinyagent.create_coding_subagent')
    async def test_coding_subagent_tool_callable_directly(self, mock_create, tiny_agent_chat):
        """Test subagent tool when it's directly callable."""
        # Mock the subagent tool as directly callable
        mock_tool = AsyncMock(return_value="Direct call successful")
        mock_create.return_value = mock_tool
        
        # Create and execute the tool
        subagent_tool = tiny_agent_chat._create_subagent_tool()
        result = await subagent_tool(
            prompt="Direct execution test",
            absolute_workdir="/test/direct",
            description="Direct call test"
        )
        
        assert "Direct call successful" in result
        mock_tool.assert_called_once_with("Direct execution test")
    
    @pytest.mark.asyncio
    @patch('tinyagent.create_coding_subagent')
    async def test_coding_subagent_tool_not_callable(self, mock_create, tiny_agent_chat):
        """Test subagent tool error when tool is not callable."""
        # Mock the subagent tool as not callable
        mock_tool = "not_callable"
        mock_create.return_value = mock_tool
        
        # Create and execute the tool
        subagent_tool = tiny_agent_chat._create_subagent_tool()
        result = await subagent_tool(
            prompt="Test",
            absolute_workdir="/test",
            description="Test"
        )
        
        assert "Subagent tool is not callable" in result
    
    @pytest.mark.asyncio
    async def test_coding_subagent_tool_tracks_usage(self, tiny_agent_chat):
        """Test that subagent tool tracks usage in main agent session state."""
        with patch('tinyagent.create_coding_subagent') as mock_create:
            # Setup mock agent with session state
            tiny_agent_chat.agent = Mock()
            tiny_agent_chat.agent.session_state = {}
            
            # Mock the subagent tool
            mock_tool = AsyncMock(return_value="Success")
            mock_create.return_value = mock_tool
            
            # Create and execute the tool
            subagent_tool = tiny_agent_chat._create_subagent_tool()
            await subagent_tool(
                prompt="Long test prompt for token counting",
                absolute_workdir="/test/tracking",
                description="Usage tracking test"
            )
            
            # Verify usage was tracked
            assert 'subagent_usage' in tiny_agent_chat.agent.session_state
            usage_entries = tiny_agent_chat.agent.session_state['subagent_usage']
            assert len(usage_entries) == 1
            
            entry = usage_entries[0]
            assert entry['description'] == "Usage tracking test"
            assert entry['model'] == "gpt-5-mini"
            assert entry['prompt_length'] == len("Long test prompt for token counting")
            assert entry['working_directory'] == "/test/tracking"
            assert 'timestamp' in entry
    
    @pytest.mark.asyncio
    @patch('tinyagent.create_coding_subagent')
    async def test_coding_subagent_tool_debug_output(self, mock_create, tiny_agent_chat):
        """Test that subagent tool provides debug output."""
        # Mock the subagent tool
        mock_tool = AsyncMock(return_value="Debug test successful")
        mock_create.return_value = mock_tool
        
        # Mock console to capture debug output
        tiny_agent_chat.console = Mock()
        
        # Create and execute the tool
        subagent_tool = tiny_agent_chat._create_subagent_tool()
        await subagent_tool(
            prompt="Test prompt for debugging",
            absolute_workdir="/debug/test",
            description="Debug output test"
        )
        
        # Verify debug messages were printed
        print_calls = [call[0][0] for call in tiny_agent_chat.console.print.call_args_list]
        debug_messages = [msg for msg in print_calls if "[dim]" in msg]
        
        # Should have multiple debug messages
        assert len(debug_messages) >= 4
        
        # Check for specific debug content
        assert any("Launching coding subagent" in msg for msg in debug_messages)
        assert any("Debug output test" in msg for msg in debug_messages)
        assert any("/debug/test" in msg for msg in debug_messages)
        assert any("Prompt length: 26 chars" in msg for msg in debug_messages)
        assert any("Subagent task completed" in msg for msg in debug_messages)
    
    @pytest.mark.asyncio
    @patch('tinyagent.create_coding_subagent')
    async def test_coding_subagent_tool_exception_handling(self, mock_create, tiny_agent_chat):
        """Test that subagent tool handles exceptions gracefully."""
        # Mock create_coding_subagent to raise an exception
        mock_create.side_effect = Exception("Test exception")
        
        # Mock console to capture error output
        tiny_agent_chat.console = Mock()
        
        # Create and execute the tool
        subagent_tool = tiny_agent_chat._create_subagent_tool()
        result = await subagent_tool(
            prompt="Error test",
            absolute_workdir="/error/test",
            description="Exception test"
        )
        
        # Verify error was handled gracefully
        assert "Subagent error" in result
        assert "Test exception" in result
        
        # Verify error was printed to console with traceback
        print_calls = [call[0][0] for call in tiny_agent_chat.console.print.call_args_list]
        error_messages = [msg for msg in print_calls if "[red]" in msg]
        assert len(error_messages) >= 2  # Error message + traceback
        assert any("Test exception" in msg for msg in error_messages)
        assert any("Debug traceback" in msg for msg in error_messages)


if __name__ == "__main__":
    pytest.main([__file__])