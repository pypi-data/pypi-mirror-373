"""Test cost aggregation with subagent usage."""

import pytest
from unittest.mock import Mock, patch
from types import SimpleNamespace
from juno_agent.ui import ChatInterface
from juno_agent.config import ConfigManager


@pytest.fixture
def mock_agent_with_subagent_costs():
    """Create a mock agent with parent and child token trackers."""
    
    # Mock child tracker stats
    child_stats_1 = SimpleNamespace(
        prompt_tokens=1000,
        completion_tokens=200,
        total_tokens=1200,
        cost=0.05,
        call_count=2,
        thinking_tokens=0,
        reasoning_tokens=0,
        cache_creation_input_tokens=0,
        cache_read_input_tokens=0
    )
    
    child_stats_2 = SimpleNamespace(
        prompt_tokens=800,
        completion_tokens=150,
        total_tokens=950,
        cost=0.03,
        call_count=1,
        thinking_tokens=0,
        reasoning_tokens=0,
        cache_creation_input_tokens=0,
        cache_read_input_tokens=0
    )
    
    # Mock child trackers
    child_tracker_1 = Mock()
    child_tracker_1.get_total_usage.return_value = child_stats_1
    
    child_tracker_2 = Mock()
    child_tracker_2.get_total_usage.return_value = child_stats_2
    
    # Mock parent tracker stats
    parent_stats = SimpleNamespace(
        prompt_tokens=2000,
        completion_tokens=300,
        total_tokens=2300,
        cost=0.08,
        call_count=3,
        thinking_tokens=0,
        reasoning_tokens=0,
        cache_creation_input_tokens=0,
        cache_read_input_tokens=0
    )
    
    # Mock parent tracker with child trackers
    parent_tracker = Mock()
    parent_tracker.get_total_usage.return_value = parent_stats
    parent_tracker.child_trackers = [child_tracker_1, child_tracker_2]
    
    # Mock agent
    agent = Mock()
    agent.callbacks = [Mock(), parent_tracker]  # MessageCleanupHook and TokenTracker
    
    return agent, parent_stats, [child_stats_1, child_stats_2]


@pytest.fixture
def mock_chat_interface(tmp_path):
    """Create a mock ChatInterface instance."""
    config_manager = Mock(spec=ConfigManager)
    config_manager.workdir = tmp_path
    config_manager.config_dir = tmp_path / ".askbudi"
    config_manager.config_dir.mkdir()
    
    chat = ChatInterface(config_manager)
    return chat


@pytest.mark.asyncio
async def test_cost_aggregation_with_subagents(mock_chat_interface, mock_agent_with_subagent_costs, capsys):
    """Test that subagent costs are properly aggregated."""
    
    agent, parent_stats, child_stats = mock_agent_with_subagent_costs
    
    # Mock the TinyCodeAgent
    mock_tiny_code_agent = Mock()
    mock_tiny_code_agent.agent = agent
    mock_chat_interface.tiny_code_agent = mock_tiny_code_agent
    
    # Execute the cost command
    await mock_chat_interface._handle_tiny_cost_command()
    
    # Capture output
    captured = capsys.readouterr()
    
    # Verify that child trackers were detected
    assert "Found 2 child trackers" in captured.out
    
    # Calculate expected aggregated values
    expected_total_tokens = parent_stats.total_tokens + sum(cs.total_tokens for cs in child_stats)
    expected_total_cost = parent_stats.cost + sum(cs.cost for cs in child_stats)
    expected_total_calls = parent_stats.call_count + sum(cs.call_count for cs in child_stats)
    
    # Verify aggregated costs are displayed
    assert f"Total Tokens**: {expected_total_tokens:,}" in captured.out
    assert f"Total Cost**: ${expected_total_cost:.4f}" in captured.out
    assert f"API Calls**: {expected_total_calls}" in captured.out
    
    # Verify subagent tracking indication
    assert "Includes Subagent Costs**: ✅ Yes (2 subagents tracked)" in captured.out


@pytest.mark.asyncio
async def test_cost_aggregation_no_subagents(mock_chat_interface, capsys):
    """Test cost display when no subagents are used."""
    
    # Mock parent tracker stats (no children)
    parent_stats = SimpleNamespace(
        prompt_tokens=1000,
        completion_tokens=200,
        total_tokens=1200,
        cost=0.05,
        call_count=2,
        thinking_tokens=0,
        reasoning_tokens=0,
        cache_creation_input_tokens=0,
        cache_read_input_tokens=0
    )
    
    # Mock parent tracker without child trackers
    parent_tracker = Mock()
    parent_tracker.get_total_usage.return_value = parent_stats
    parent_tracker.child_trackers = []
    
    # Mock agent
    agent = Mock()
    agent.callbacks = [Mock(), parent_tracker]
    
    # Mock the TinyCodeAgent
    mock_tiny_code_agent = Mock()
    mock_tiny_code_agent.agent = agent
    mock_chat_interface.tiny_code_agent = mock_tiny_code_agent
    
    # Execute the cost command
    await mock_chat_interface._handle_tiny_cost_command()
    
    # Capture output
    captured = capsys.readouterr()
    
    # Verify no child trackers message
    assert "No child trackers found - showing parent tracker only" in captured.out
    
    # Verify costs match parent stats exactly
    assert f"Total Tokens**: {parent_stats.total_tokens:,}" in captured.out
    assert f"Total Cost**: ${parent_stats.cost:.4f}" in captured.out
    assert f"API Calls**: {parent_stats.call_count}" in captured.out
    
    # Verify no subagent tracking indication
    assert "Includes Subagent Costs**: ❌ No subagent usage detected" in captured.out


@pytest.mark.asyncio
async def test_cost_command_with_no_agent(mock_chat_interface, capsys):
    """Test cost command when no agent is available."""
    
    # No agent set
    mock_chat_interface.tiny_code_agent = None
    
    # Execute the cost command
    await mock_chat_interface._handle_tiny_cost_command()
    
    # Capture output
    captured = capsys.readouterr()
    
    # Verify appropriate message is shown
    assert "No active TinyAgent session" in captured.out


@pytest.mark.parametrize("child_count", [1, 3, 5])
@pytest.mark.asyncio
async def test_cost_aggregation_multiple_children(mock_chat_interface, child_count, capsys):
    """Test cost aggregation with varying numbers of child trackers."""
    
    # Create multiple child trackers
    child_trackers = []
    child_stats_list = []
    
    for i in range(child_count):
        child_stats = SimpleNamespace(
            prompt_tokens=500 + i * 100,
            completion_tokens=100 + i * 20,
            total_tokens=600 + i * 120,
            cost=0.02 + i * 0.01,
            call_count=1 + i,
            thinking_tokens=0,
            reasoning_tokens=0,
            cache_creation_input_tokens=0,
            cache_read_input_tokens=0
        )
        
        child_tracker = Mock()
        child_tracker.get_total_usage.return_value = child_stats
        
        child_trackers.append(child_tracker)
        child_stats_list.append(child_stats)
    
    # Mock parent tracker stats
    parent_stats = SimpleNamespace(
        prompt_tokens=1000,
        completion_tokens=200,
        total_tokens=1200,
        cost=0.05,
        call_count=2,
        thinking_tokens=0,
        reasoning_tokens=0,
        cache_creation_input_tokens=0,
        cache_read_input_tokens=0
    )
    
    # Mock parent tracker with multiple children
    parent_tracker = Mock()
    parent_tracker.get_total_usage.return_value = parent_stats
    parent_tracker.child_trackers = child_trackers
    
    # Mock agent
    agent = Mock()
    agent.callbacks = [Mock(), parent_tracker]
    
    # Mock the TinyCodeAgent
    mock_tiny_code_agent = Mock()
    mock_tiny_code_agent.agent = agent
    mock_chat_interface.tiny_code_agent = mock_tiny_code_agent
    
    # Execute the cost command
    await mock_chat_interface._handle_tiny_cost_command()
    
    # Capture output
    captured = capsys.readouterr()
    
    # Verify correct number of child trackers detected
    assert f"Found {child_count} child trackers" in captured.out
    assert f"Includes Subagent Costs**: ✅ Yes ({child_count} subagents tracked)" in captured.out
    
    # Calculate expected aggregated values
    expected_total_tokens = parent_stats.total_tokens + sum(cs.total_tokens for cs in child_stats_list)
    expected_total_cost = parent_stats.cost + sum(cs.cost for cs in child_stats_list)
    expected_total_calls = parent_stats.call_count + sum(cs.call_count for cs in child_stats_list)
    
    # Verify aggregated costs
    assert f"Total Tokens**: {expected_total_tokens:,}" in captured.out
    assert f"Total Cost**: ${expected_total_cost:.4f}" in captured.out
    assert f"API Calls**: {expected_total_calls}" in captured.out