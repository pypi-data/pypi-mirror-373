"""Test token tracker hook functionality for subagents."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from juno_agent.tiny_agent import TinyCodeAgentChat
from juno_agent.config import ConfigManager


@pytest.fixture
def mock_config_manager(tmp_path):
    """Create a mock config manager."""
    config_manager = Mock(spec=ConfigManager)
    config_manager.workdir = tmp_path / "workdir"
    config_manager.config_dir = tmp_path / ".askbudi"
    config_manager.config_dir.mkdir(exist_ok=True)
    
    # Mock config
    mock_config = Mock()
    mock_config.agent_config.model_name = "gpt-5-mini"
    mock_config.agent_config.provider = "openai"
    mock_config.agent_config.temperature = 0.0
    mock_config.agent_config.max_turns = 10
    mock_config.agent_config.max_tokens = None
    mock_config.agent_config.custom_base_url = None
    mock_config.agent_config.custom_params = None
    mock_config.agent_config.reuse_subagents = False
    mock_config.project_description = "Test project"
    mock_config.libraries = []
    mock_config.editor = "vscode"
    
    config_manager.load_config.return_value = mock_config
    config_manager.get_model_api_key.return_value = "test-api-key"
    
    return config_manager


@pytest.mark.asyncio
@patch('tinyagent.TinyCodeAgent')
@patch('tinyagent.hooks.token_tracker.create_token_tracker')
@patch('tinyagent.tools.create_coding_subagent')
@patch('tinyagent.SubagentConfig')
async def test_token_tracker_initialization_success(
    mock_subagent_config, mock_create_coding_subagent, 
    mock_create_token_tracker, mock_tiny_code_agent, 
    mock_config_manager
):
    """Test successful token tracker initialization for both parent and child."""
    
    # Mock parent tracker
    mock_parent_tracker = Mock()
    mock_parent_tracker.name = "main_agent"
    
    # Mock child tracker
    mock_child_tracker = Mock()
    mock_child_tracker.name = "subagent"
    
    # Mock create_token_tracker calls
    mock_create_token_tracker.side_effect = [mock_parent_tracker, mock_child_tracker]
    
    # Mock TinyCodeAgent
    mock_agent = Mock()
    mock_agent.callbacks = [mock_parent_tracker]
    mock_tiny_code_agent.return_value = mock_agent
    
    # Mock SubagentConfig
    mock_config = Mock()
    mock_config.to_agent_kwargs.return_value = {"model": "gpt-5-mini"}
    mock_config.callbacks = [mock_child_tracker]  # Add callbacks list
    mock_subagent_config.from_parent_agent.return_value = mock_config
    
    # Mock coding subagent tool
    mock_subagent_tool = Mock()
    mock_create_coding_subagent.return_value = mock_subagent_tool
    
    # Create chat instance
    chat = TinyCodeAgentChat(mock_config_manager)
    
    # Initialize agent
    await chat.initialize_agent()
    
    # Verify parent tracker was created and added
    assert mock_create_token_tracker.call_count == 2
    mock_create_token_tracker.assert_any_call(
        name="main_agent",
        enable_detailed_logging=True
    )
    mock_agent.add_callback.assert_called()
    
    # Verify child tracker was created with parent reference
    mock_create_token_tracker.assert_any_call(
        name="subagent",
        parent_tracker=mock_parent_tracker,
        enable_detailed_logging=True
    )
    
    # Verify SubagentConfig was called with proper callbacks
    mock_subagent_config.from_parent_agent.assert_called_once()
    call_args = mock_subagent_config.from_parent_agent.call_args
    assert 'callbacks' in call_args.kwargs
    # Should include only the child tracker (not parent, per our recent fix)
    callbacks = call_args.kwargs['callbacks']
    assert mock_child_tracker in callbacks
    # Parent tracker should NOT be in callbacks for subagents
    assert mock_parent_tracker not in callbacks


@pytest.mark.asyncio
@patch('tinyagent.TinyCodeAgent')
@patch('tinyagent.hooks.token_tracker.create_token_tracker')
@patch('tinyagent.tools.create_coding_subagent')
@patch('tinyagent.SubagentConfig')
async def test_token_tracker_parent_failure_graceful_handling(
    mock_subagent_config, mock_create_coding_subagent, 
    mock_create_token_tracker, mock_tiny_code_agent, 
    mock_config_manager
):
    """Test graceful handling when parent tracker creation fails."""
    
    # Mock create_token_tracker to fail for parent
    mock_create_token_tracker.side_effect = Exception("Token tracker creation failed")
    
    # Mock TinyCodeAgent
    mock_agent = Mock()
    mock_agent.callbacks = []
    mock_tiny_code_agent.return_value = mock_agent
    
    # Mock SubagentConfig
    mock_config = Mock()
    mock_config.to_agent_kwargs.return_value = {"model": "gpt-5-mini"}
    mock_config.callbacks = []  # Empty callbacks when parent tracker creation fails
    mock_subagent_config.from_parent_agent.return_value = mock_config
    
    # Mock coding subagent tool
    mock_subagent_tool = Mock()
    mock_create_coding_subagent.return_value = mock_subagent_tool
    
    # Create chat instance
    chat = TinyCodeAgentChat(mock_config_manager)
    
    # Initialize agent - should not raise exception
    await chat.initialize_agent()
    
    # Verify parent tracker creation was attempted
    mock_create_token_tracker.assert_called_once_with(
        name="main_agent",
        enable_detailed_logging=True
    )
    
    # Verify SubagentConfig was still called (with empty callbacks from parent)
    mock_subagent_config.from_parent_agent.assert_called_once()
    call_args = mock_subagent_config.from_parent_agent.call_args
    callbacks = call_args.kwargs['callbacks']
    # Should only have parent callbacks (empty list) since child tracker wasn't created
    assert len(callbacks) == 0


@pytest.mark.asyncio
@patch('tinyagent.TinyCodeAgent')
@patch('tinyagent.hooks.token_tracker.create_token_tracker')
@patch('tinyagent.tools.create_coding_subagent')
@patch('tinyagent.SubagentConfig')
async def test_token_tracker_child_failure_graceful_handling(
    mock_subagent_config, mock_create_coding_subagent, 
    mock_create_token_tracker, mock_tiny_code_agent, 
    mock_config_manager
):
    """Test graceful handling when child tracker creation fails but parent succeeds."""
    
    # Mock parent tracker success, child tracker failure
    mock_parent_tracker = Mock()
    mock_parent_tracker.name = "main_agent"
    
    def token_tracker_side_effect(*args, **kwargs):
        if kwargs.get('name') == 'main_agent':
            return mock_parent_tracker
        else:  # child tracker
            raise Exception("Child tracker creation failed")
    
    mock_create_token_tracker.side_effect = token_tracker_side_effect
    
    # Mock TinyCodeAgent
    mock_agent = Mock()
    mock_agent.callbacks = [mock_parent_tracker]
    mock_tiny_code_agent.return_value = mock_agent
    
    # Mock SubagentConfig
    mock_config = Mock()
    mock_config.to_agent_kwargs.return_value = {"model": "gpt-5-mini"}
    mock_config.callbacks = []  # Empty callbacks since child tracker creation failed
    mock_subagent_config.from_parent_agent.return_value = mock_config
    
    # Mock coding subagent tool
    mock_subagent_tool = Mock()
    mock_create_coding_subagent.return_value = mock_subagent_tool
    
    # Create chat instance
    chat = TinyCodeAgentChat(mock_config_manager)
    
    # Initialize agent - should not raise exception
    await chat.initialize_agent()
    
    # Verify both tracker creations were attempted
    assert mock_create_token_tracker.call_count == 2
    
    # Verify SubagentConfig was called with empty callbacks since child tracker failed
    mock_subagent_config.from_parent_agent.assert_called_once()
    call_args = mock_subagent_config.from_parent_agent.call_args
    callbacks = call_args.kwargs['callbacks']
    # Should be empty since child tracker creation failed
    assert len(callbacks) == 0